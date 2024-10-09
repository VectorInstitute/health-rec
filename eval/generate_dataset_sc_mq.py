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
We are evaluating a RAG pipeline for generating health service recommendations to individuals in need. The aim is to create a synthetic dataset of user queries based on the context of a single health service provided.

Given the following context of a health service:

{context}

Generate a list of 5 user queries that could require this service. For each query, consider:
1. Diverse demographics (age, gender, ethnicity, socioeconomic status)
2. Intersectional needs (e.g., elderly with mobility issues and mental health concerns)
3. Various situations that might require this service

The level of detail in the queries should be {detail_level}:
- Low: 1-2 sentences, brief queries with minimal context
- Medium: 2-3 sentences, moderately detailed queries with some background information
- High: A solid paragraph with extensive background information

{format_instructions}

Output the results in the specified format.
"""

# Define the output schema
response_schemas = [
    ResponseSchema(
        name="queries", description="List of user queries about the health service"
    ),
    ResponseSchema(
        name="relevant_services", description="List of id for relevant services (1-5)"
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
        description="Relevant demographic information for the query in the specified format",
    ),
    ResponseSchema(
        name="detail_level",
        description="The level of detail in the query (low/medium/high)",
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
    situation_type: str,
    detail_level: str,
) -> List[Dict[str, Any]]:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    prompt = ChatPromptTemplate.from_template(query_generation_template)

    chain = (
        {
            "context": RunnablePassthrough(),
            "max_context_services": RunnablePassthrough(),
            "situation_instruction": RunnablePassthrough(),
            "detail_level": RunnablePassthrough(),
            "format_instructions": lambda _: output_parser.get_format_instructions(),
        }
        | prompt
        | llm
        | output_parser
    )

    synthetic_dataset = []

    for _ in range(num_samples):
        # Randomly select services for context
        context_services = random.sample(services, num_random_services)
        context = "\n\n".join(
            [
                f"Service {s['id']}:\n{s['PublicName']}\n{s['Description']}"
                for s in context_services
            ]
        )

        # Set situation instruction based on the specified type
        if situation_type == "emergency":
            situation_instruction = "Generate an user query for an urgent situation that requires emergency services."
        elif situation_type == "out_of_scope":
            situation_instruction = "Generate a user query that is out of scope and inappropriate.  \
                Don't take into account whether the user query matches the context of health services provided."
        else:
            situation_instruction = (
                "Consider various demographics and intersectional needs."
            )

        # Generate queries and answers
        try:
            result = chain.invoke(
                {
                    "context": context,
                    "max_context_services": max_context_services,
                    "situation_instruction": situation_instruction,
                    "detail_level": detail_level,
                }
            )

            if isinstance(result, list):
                parsed_result = result
            else:
                parsed_result = [result]

            for item in parsed_result:
                relevant_services = [
                    s["id"]
                    for s in context_services
                    if s["id"] in item.get("relevant_services", [])
                ]

                # Handle emergency and out-of-scope situations
                # if item.get('is_emergency'):
                #     item['answer'] = EMERGENCY_SERVICES_TEXT + "\n\n" + item.get('answer', '')
                # elif item.get('is_out_of_scope'):
                #     item['answer'] = OUT_OF_SCOPE_TEXT

                synthetic_dataset.append(
                    {
                        "query": item.get("query", ""),
                        "context": relevant_services,
                        "answer": item.get("answer", ""),
                        "is_emergency": item.get("is_emergency", False),
                        "is_out_of_scope": item.get("is_out_of_scope", False),
                        "demographics": item.get("demographics", ""),
                        "detail_level": item.get("detail_level", detail_level),
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
        "--input_file", default="data/211_nb.csv", help="Path to the input CSV file"
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
    parser.add_argument(
        "--situation_type",
        choices=["regular", "emergency", "out_of_scope"],
        default="regular",
        help="Type of situation to generate",
    )
    parser.add_argument(
        "--detail_level",
        choices=["low", "medium", "high"],
        default="medium",
        help="Level of detail for the generated queries",
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
        situation_type=args.situation_type,
        detail_level=args.detail_level,
    )

    # Save the synthetic dataset to disk
    output_file = os.path.join(args.output_dir, f"{args.name}.json")
    with open(output_file, "w") as f:
        json.dump(synthetic_dataset, f, indent=2)

    print(
        f"Generated {len(synthetic_dataset)} synthetic samples. Saved to {output_file}"
    )
