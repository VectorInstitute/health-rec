import json
import requests
from typing import List, Dict
from urllib.parse import urljoin
import argparse


def calculate_topk_accuracy(
    retrieved_ids: List[str], relevant_id: str, k: int
) -> float:
    """
    Calculates the top-k accuracy for a single relevant ID.

    Parameters
    ----------
    retrieved_ids : List[str]
        List of IDs retrieved by the system.
    relevant_id : str
        The single ground truth relevant ID.
    k : int
        The 'k' in top-k accuracy.

    Returns
    -------
    float
        The top-k accuracy. Returns 0 if retrieved_ids is empty or no match is found.
    """
    if not retrieved_ids or not relevant_id:
        return 0.0

    top_k_retrieved = retrieved_ids[:k]
    return 1.0 if str(relevant_id) in top_k_retrieved else 0.0


def evaluate_retrieval_accuracy(
    dataset_path: str, endpoint: str, top_k_values: List[int]
) -> Dict[str, Dict[str, Dict[int, float]]]:
    """
    Evaluates the top-k accuracy of the retrieval API, split by categories.

    Parameters
    ----------
    dataset_path : str
        Path to the JSON dataset file.
    endpoint : str
        The retrieval API endpoint URL.
    top_k_values : List[int]
        A list of 'k' values for which to calculate top-k accuracy.

    Returns
    -------
    Dict[str, Dict[int, float]]
        A dictionary of dictionaries. The outer keys are categories
        (e.g., "is_emergency", "is_out_of_scope", "detail_level").
        The inner dictionaries map top-k values to average accuracies
        for that category and k.
    """

    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    # Initialize results dictionary
    results: Dict[str, Dict[str, Dict[int, List[float]]]] = {
        "is_emergency": {},
        "is_out_of_scope": {},
        "detail_level": {},
    }
    for category in results:
        if category in ("is_emergency", "is_out_of_scope"):
            results[category] = {
                "true": {k: [] for k in top_k_values},
                "false": {k: [] for k in top_k_values},
            }
        elif category == "detail_level":
            results[category] = {
                "low": {k: [] for k in top_k_values},
                "medium": {k: [] for k in top_k_values},
                "high": {k: [] for k in top_k_values},
            }

    for item in dataset:
        query = item["query"]
        relevant_id = item["context"]  # Now expects a single ID instead of a list

        # Skip items with empty context (no relevant service ID)
        if not relevant_id:
            continue

        # Build the request payload
        payload = {
            "query": query,
            "latitude": None,
            "longitude": None,
            "radius": None,
            "detail_level": "low",  # This doesn't affect retrieval, but is part of the schema
        }

        try:
            response = requests.post(
                urljoin(endpoint, "retrieve"),
                json=payload,
                params={"top_k": max(top_k_values)},
            )
            response.raise_for_status()
            retrieved_services = response.json()
            retrieved_ids = [service["id"] for service in retrieved_services]

            for k in top_k_values:
                accuracy = calculate_topk_accuracy(retrieved_ids, relevant_id, k)

                # Store results based on categories
                for category in ["is_emergency", "is_out_of_scope", "detail_level"]:
                    if category in ("is_emergency", "is_out_of_scope"):
                        category_value = str(item.get(category, "false")).lower()
                    else:  # detail_level
                        category_value = item.get(category, "low").lower()

                    if category_value in list(results[category].keys()):
                        results[category][category_value][k].append(accuracy)
                    else:
                        print(
                            f"Warning: Unknown value '{category_value}' for category '{category}'. Skipping."
                        )

        except requests.exceptions.RequestException as e:
            print(f"Error during API request for query '{query}': {e}")
            continue
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response for query '{query}': {e}")
            continue
        except KeyError as e:
            print(f"KeyError for query '{query}', likely missing 'id' in service: {e}")
            continue

    # Calculate average accuracies
    average_accuracies: Dict[str, Dict[str, Dict[int, float]]] = {}
    for category, sub_categories in results.items():
        average_accuracies[category] = {}
        for sub_category, k_values in sub_categories.items():
            average_accuracies[category][sub_category] = {}
            for k, accuracies in k_values.items():
                average_accuracies[category][sub_category][k] = (
                    sum(accuracies) / len(accuracies) if accuracies else 0.0
                )

    return average_accuracies


def main() -> None:
    """
    Main function to run the evaluation using command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Evaluate retrieval accuracy of an API."
    )
    parser.add_argument("dataset_path", type=str, help="Path to the JSON dataset file.")
    parser.add_argument(
        "--endpoint",
        type=str,
        default="http://localhost:8005/",
        help="The retrieval API endpoint URL (default: http://localhost:8005/).",
    )
    parser.add_argument(
        "--top_k",
        type=str,
        default="5,10,15,20",
        help="Comma-separated list of top-k values (default: 5,10,15,20).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="eval_results.json",
        help="Output file name for JSON results (default: eval_results.json).",
    )

    args = parser.parse_args()

    # Parse top_k values
    try:
        top_k_values = [int(k) for k in args.top_k.split(",")]
    except ValueError:
        print(
            "Error: Invalid top_k values. Provide a comma-separated list of integers."
        )
        return

    accuracies = evaluate_retrieval_accuracy(
        args.dataset_path, args.endpoint, top_k_values
    )

    # Output to JSON file
    with open(args.output, "w") as outfile:
        json.dump(accuracies, outfile, indent=4)

    print(f"Evaluation results saved to {args.output}")


if __name__ == "__main__":
    main()
