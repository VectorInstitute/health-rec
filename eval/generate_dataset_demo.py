import glob
import json
import logging
import os
import random
from typing import Any, Dict, List, Union


from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.runnables import RunnablePassthrough

# get env variables
from dotenv import load_dotenv

load_dotenv(".env.development")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_services(data_dir: str) -> List[Dict[str, Any]]:
    """
    Load services from multiple JSON files in a directory.

    Parameters
    ----------
    data_dir : str
        Path to directory containing JSON files (data-XX.json)

    Returns
    -------
    List[Dict[str, Any]]
        List of service dictionaries
    """
    services = []
    json_files = sorted(glob.glob(os.path.join(data_dir, "data-*.json")))

    if not json_files:
        raise ValueError(f"No data-XX.json files found in {data_dir}")

    for file_path in json_files:
        logger.info(f"Loading services from {file_path}")
        try:
            with open(file_path, "r") as f:
                file_services = json.load(f)
                if isinstance(file_services, list):
                    services.extend(file_services)
                else:
                    logger.warning(f"Skipping {file_path}: content is not a list")
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {file_path}")
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")

    logger.info(f"Loaded {len(services)} services total")
    return services


def parse_demographics_string(demographics: str) -> Dict[str, str]:
    """Convert a comma-separated demographics string into a structured dictionary."""
    demo_dict = {
        "Age": "N/A",
        "Gender": "N/A",
        "Ethnicity": "N/A",
        "Employment status": "N/A",
        "Housing situation": "N/A",
        "Disability status": "N/A",
        "Immigration status": "N/A"
    }
    
    try:
        # Handle string format
        if isinstance(demographics, str):
            pairs = [pair.strip() for pair in demographics.split(',')]
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key in demo_dict:
                        demo_dict[key] = value.strip()
        # Handle dict format
        elif isinstance(demographics, dict):
            for key in demo_dict:
                if key in demographics:
                    demo_dict[key] = demographics[key]
    except Exception as e:
        logger.error(f"Error parsing demographics: {e}")
    
    return demo_dict


def process_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Process and standardize the result from the LLM."""
    processed = result.copy()
    
    # Ensure demographics is properly formatted
    demographics = result.get("demographics", {})
    if isinstance(demographics, str):
        # Convert string format to dictionary
        processed["demographics"] = parse_demographics_string(demographics)
    elif isinstance(demographics, dict):
        # Ensure all required fields exist
        processed["demographics"] = {
            "Age": demographics.get("Age", "N/A"),
            "Gender": demographics.get("Gender", "N/A"),
            "Ethnicity": demographics.get("Ethnicity", "N/A"),
            "Employment status": demographics.get("Employment status", "N/A"),
            "Housing situation": demographics.get("Housing situation", "N/A"),
            "Disability status": demographics.get("Disability status", "N/A"),
            "Immigration status": demographics.get("Immigration status", "N/A")
        }
    else:
        # Default empty demographics
        processed["demographics"] = parse_demographics_string("")
    
    return processed


# Create prompt template for generating synthetic queries and answers
query_generation_template = """
We are evaluating a RAG pipeline for generating health service recommendations to individuals in need. The aim is to create a synthetic dataset of user queries based on the context of health services provided.

Given the following context of health service:

{context}

Generate a user query that corresponds to the service in the context.
{situation_instruction}

For each query, provide an expected answer based on the relevant services.

{format_instructions}

Remember to consider:
1. Diverse demographics (age, gender, ethnicity, socioeconomic status)
2. Intersectional needs (e.g., elderly with mobility issues and mental health concerns)
3. Primary and secondary service recommendations

If the demographic isn't **explicitly** mentioned in the generated user query, set it to N/A.
Avoid providing services tailored to specific ethnicities or religions unless explicitly mentioned in the query.

For the level of detail:
- Low: Brief, general queries with minimal context
- Medium: Moderately detailed queries with some background information
- High: Highly detailed queries with extensive context and specific needs

The level of detail in the query should be {detail_level}.

Output the results in the specified format.
"""

# Define the output schema
# Update the response schemas to be more specific
response_schemas = [
    ResponseSchema(name="query", description="The user's query about health services"),
    ResponseSchema(
        name="answer",
        description="Expected answer based on the query and relevant services",
    ),
    ResponseSchema(
        name="demographics",
        description="""Demographic information in the following format:
        {
            "Age": "[child/teen/young adult/adult/senior]",
            "Gender": "[male/female/non-binary]",
            "Ethnicity": "[Caucasian/African/Asian/Hispanic/Indigenous/Other]",
            "Employment status": "[employed/unemployed/student/retired/unable to work]",
            "Housing situation": "[own home/renting/homeless/shelter/assisted living]",
            "Disability status": "[no disability/physical disability/cognitive disability]",
            "Immigration status": "[citizen/permanent resident/temporary resident/refugee/undocumented]"
        }""",
    ),
]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)


def create_synthetic_dataset(
    services: List[Dict[str, Any]],
    num_samples: int,
    situation_type: str,
    detail_level: str,
    name: str,
) -> List[Dict[str, Any]]:
    """Create synthetic dataset from services with robust demographics handling."""
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)
    prompt = ChatPromptTemplate.from_template(query_generation_template)

    chain = (
        {
            "context": RunnablePassthrough(),
            "situation_instruction": RunnablePassthrough(),
            "detail_level": RunnablePassthrough(),
            "format_instructions": lambda _: output_parser.get_format_instructions(),
        }
        | prompt
        | llm
        | output_parser
    )

    synthetic_dataset = []
    random_services = random.sample(services, num_samples)

    for context_service in random_services:
        if "gta" in name:
            context = f"Service {str(context_service.get('id', ''))}:\n{context_service.get('name', 'Unnamed Service')}\n{context_service.get('description', 'No description available')}"
        else:
            context = f"Service {str(context_service.get('id', ''))}:\n{context_service.get('PublicName', 'Unnamed Service')}\n{context_service.get('Description', 'No description available')}"

        # Set situation instruction based on the specified type
        if situation_type == "emergency":
            situation_instruction = "Generate a user query for an urgent situation that requires emergency services."
        elif situation_type == "out_of_scope":
            situation_instruction = (
                "Generate a user query that is out of scope and inappropriate. "
                "Don't take into account whether the user query matches the context of health services provided."
            )
        else:
            situation_instruction = (
                "Consider various demographics and intersectional needs."
            )

        try:
            result = chain.invoke(
                {
                    "context": context,
                    "situation_instruction": situation_instruction,
                    "detail_level": detail_level,
                }
            )

            # Process the result to ensure consistent formatting
            processed_result = process_result(result)

            synthetic_dataset.append(
                {
                    "query": processed_result.get("query", ""),
                    "context": context_service["id"],
                    "answer": processed_result.get("answer", ""),
                    "demographics": processed_result.get("demographics", {}),
                    "is_emergency": True if situation_type == "emergency" else False,
                    "is_out_of_scope": True if situation_type == "out_of_scope" else False,
                    "detail_level": detail_level,
                }
            )
        except Exception as e:
            logger.error(f"Error generating sample: {e}")
            logger.error(f"Result was: {result}")

    return synthetic_dataset


def main() -> None:
    """Main function to run the script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate synthetic dataset for RAG evaluation"
    )
    parser.add_argument(
        "--input_dir", required=True, help="Directory containing the JSON files"
    )
    parser.add_argument(
        "--output_dir", default="./eval", help="Directory to save the output JSON file"
    )
    parser.add_argument(
        "--name", default="synthetic_dataset", help="Name of the output JSON file"
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

    # Load services from JSON files
    services = load_services(args.input_dir)

    # Generate synthetic dataset
    synthetic_dataset = create_synthetic_dataset(
        services,
        num_samples=args.num_samples,
        situation_type=args.situation_type,
        detail_level=args.detail_level,
        name=args.name,
    )

    # Save the synthetic dataset to disk
    output_file = os.path.join(args.output_dir, f"{args.name}.json")
    with open(output_file, "w") as f:
        json.dump(synthetic_dataset, f, indent=2)

    logger.info(
        f"Generated {len(synthetic_dataset)} synthetic samples. Saved to {output_file}"
    )


if __name__ == "__main__":
    main()
