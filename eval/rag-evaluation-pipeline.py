import csv
import random
import json
import argparse
import os
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.runnables import RunnablePassthrough


# Load the services data
def load_services(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        return list(reader)


# Create a prompt template for generating synthetic queries and answers
query_generation_template = """
Given the following context of health services:

{context}

Generate a user query that correspond to 1-{max_context_services} services in the context.
Consider various demographics, intersectional needs, potential emergency situations, and out-of-scope queries.
For each query, provide an expected answer based on the relevant services.


{format_instructions}

Remember to consider:
1. Diverse demographics (age, gender, ethnicity, socioeconomic status)
2. Intersectional needs (e.g., elderly with mobility issues and mental health concerns)
3. Out-of-scope situations (queries that are inappropriate or don't match the available services)
4. Potential emergency services
5. Primary and secondary service recommendations

Output the results in the specified format.
"""

# Define the output schema
response_schemas = [
    ResponseSchema(name="query", description="The user's query about health services"),
    ResponseSchema(
        name="relevant_services",
        description="List of ResourceAgencyNum for relevant services (1-5)",
    ),
    ResponseSchema(
        name="answer",
        description="Expected answer based on the query and relevant services",
    ),
    ResponseSchema(
        name="is_emergency",
        description="Boolean indicating if this is an emergency situation",
    ),
    ResponseSchema(
        name="is_out_of_scope",
        description="Boolean indicating if the query is out of scope for available services",
    ),
    ResponseSchema(
        name="demographics",
        description="Relevant demographic information for the query",
    ),
]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

EMERGENCY_SERVICES_TEXT = """
**In an emergency, call 9‑1‑1.**

* At home, you can dial 9‑1‑1 directly. At a business or other location, you may need to dial an outside line before dialing 9‑1‑1.
* At a pay phone, dial 9‑1‑1; the call is free. When using a cellular phone, be prepared to give the exact location of the emergency; the call is free.
* For TTY access (Telephone Device for the Deaf), press the space bar announcer key repeatedly until a response is received. Deaf, deafened, Hard of Hearing, or Speech Impaired persons may register for Text with 9-1-1 Service.

**If you do not speak English,** stay on the line while the call taker contacts the telephone translations service.

When you call, remain calm and speak clearly. Identify which emergency service you require (police, fire, or ambulance) and be prepared to provide the following information: a description of what is happening, the location, and your name, address, and telephone number.

Please remain on the line to provide additional information if requested by the call taker. Do not hang up until the call taker tells you to.
"""

OUT_OF_SCOPE_TEXT = "I apologize, but I couldn't find any relevant services that match your query. The services available may not cover this specific need. If you have a different health-related question or need, please feel free to ask, and I'll do my best to help you find appropriate resources."


# Create the Langchain pipeline
def create_synthetic_dataset(
    services: List[Dict[str, Any]],
    num_samples: int,
    num_random_services: int,
    max_context_services: int,
) -> List[Dict[str, Any]]:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    prompt = ChatPromptTemplate.from_template(query_generation_template)

    chain = (
        {  # type: ignore
            "context": RunnablePassthrough(),
            "max_context_services": RunnablePassthrough(),
            "format_instructions": lambda _: output_parser.get_format_instructions(),
        }
        | prompt
        | llm
        | output_parser
    )

    synthetic_dataset = []

    for _ in range(num_samples):
        # Randomly select 10 services for context
        context_services = random.sample(services, num_random_services)
        context = "\n\n".join(
            [
                f"Service {s['ResourceAgencyNum']}:\n{s['PublicName']}\n{s['AgencyDescription']}"
                for s in context_services
            ]
        )

        # Generate queries and answers
        try:
            result = chain.invoke(
                {"context": context, "max_context_services": max_context_services}
            )

            if isinstance(result, list):
                parsed_result = result
            else:
                parsed_result = [result]

            for item in parsed_result:
                relevant_services = [
                    s
                    for s in context_services
                    if s["ResourceAgencyNum"] in item.get("relevant_services", [])
                ]

                # Handle emergency and out-of-scope situations

                synthetic_dataset.append(
                    {
                        "query": item.get("query", ""),
                        "context": relevant_services,
                        "answer": item.get("answer", ""),
                        "is_emergency": item.get("is_emergency", ""),
                        "is_out_of_scope": item.get("is_out_of_scope", ""),
                        "demographics": item.get("demographics", ""),
                    }
                )
        except Exception as e:
            print(f"Error generating sample: {e}")

    return synthetic_dataset


# Main execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate synthetic dataset for RAG evaluation"
    )
    parser.add_argument(
        "--input_file",
        default="data/211_central.csv",
        help="Path to the input CSV file",
    )
    parser.add_argument(
        "--output_dir", default="./eval", help="Directory to save the output JSON file"
    )
    parser.add_argument(
        "--name", default="synthetic_dataset", help="Name of the output JSON file"
    )
    parser.add_argument(
        "--num_random_services",
        type=int,
        default=10,
        help="Number of services to randomly select for each sample",
    )
    parser.add_argument(
        "--max_context_services",
        type=int,
        default=5,
        help="Maximum number of services to include in the context",
    )
    parser.add_argument(
        "--num_samples", type=int, default=20, help="Number of samples to generate"
    )
    args = parser.parse_args()

    # Ensure the output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Read OpenAI API key from environment variable
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    # Set the API key for the ChatOpenAI model
    os.environ["OPENAI_API_KEY"] = openai_api_key

    services = load_services(args.input_file)
    synthetic_dataset = create_synthetic_dataset(
        services,
        num_samples=args.num_samples,
        num_random_services=args.num_random_services,
        max_context_services=args.max_context_services,
    )

    # Save the synthetic dataset to disk
    output_file = os.path.join(args.output_dir, f"{args.name}.json")
    with open(output_file, "w") as f:
        json.dump(synthetic_dataset, f, indent=2)

    print(
        f"Generated {len(synthetic_dataset)} synthetic samples. Saved to {output_file}"
    )
