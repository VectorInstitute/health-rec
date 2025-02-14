"""
Script for evaluating RAG system outputs using RAGAS metrics.

This module provides functionality to evaluate RAG system outputs using RAGAS metrics,
including category-based analysis and aggregation.
"""

import os
import argparse
import json
import logging
from typing import Any, Dict, List

import pandas as pd
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_recall,
    context_precision,
)
from datasets import Dataset


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_dataset(file_path: str) -> Any:
    """Load evaluation samples from a JSON file."""
    with open(file_path, "r") as f:
        return json.load(f)


def prepare_dataset(
    samples: List[Dict[str, Any]], query_dataset: List[Dict[str, Any]]
) -> Dataset:
    """Prepare the dataset for RAGAS evaluation with category information."""
    processed_data: Dict[str, List[Any]] = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [],
        "is_emergency": [],
        "is_out_of_scope": [],
        "detail_level": [],
    }

    for i, sample in enumerate(samples):
        query = sample["query"]
        query_data = query_dataset[i]

        processed_data["question"].append(query)
        processed_data["answer"].append(sample["answer"])
        processed_data["contexts"].append(sample["context"])
        processed_data["ground_truth"].append(sample.get("ground_truth", [""])[0])
        processed_data["is_emergency"].append(query_data.get("is_emergency", False))
        processed_data["is_out_of_scope"].append(
            query_data.get("is_out_of_scope", False)
        )
        processed_data["detail_level"].append(query_data.get("detail_level", "medium"))

    return Dataset.from_dict(processed_data)


def run_evaluation(dataset: Dataset) -> pd.DataFrame:
    """Run the RAGAS evaluation."""
    results = evaluate(
        dataset=dataset,
        metrics=[
            answer_relevancy,
            faithfulness,
            context_recall,
            context_precision,
        ],
    )
    return results.to_pandas()


def aggregate_by_category(
    results: pd.DataFrame, dataset: Dataset
) -> Dict[str, Dict[str, Dict[str, float]]]:
    """
    Aggregate evaluation results by category.

    Returns a nested dictionary with category-based metrics.
    """
    # Convert dataset to pandas for easier manipulation
    dataset_df = pd.DataFrame(
        {
            "is_emergency": dataset["is_emergency"],
            "is_out_of_scope": dataset["is_out_of_scope"],
            "detail_level": dataset["detail_level"],
        }
    )

    # Combine with results
    combined_df = pd.concat([results, dataset_df], axis=1)

    metrics = [
        "answer_relevancy",
        "faithfulness",
        "context_recall",
        "context_precision",
    ]
    categories: Dict[str, List[Any]] = {
        "is_emergency": [True, False],
        "is_out_of_scope": [True, False],
        "detail_level": ["low", "medium", "high"],
    }

    aggregated_results: Dict[str, Dict[str, Dict[str, float]]] = {}

    for category, values in categories.items():
        aggregated_results[category] = {}
        for value in values:
            metric_results = {}
            mask = combined_df[category] == value
            if mask.any():
                for metric in metrics:
                    if metric in combined_df.columns:
                        metric_results[metric] = float(combined_df[mask][metric].mean())
            aggregated_results[category][str(value)] = metric_results

    return aggregated_results


def main() -> None:
    """Main function for RAGAS evaluation."""
    parser = argparse.ArgumentParser(
        description="Evaluate RAG system outputs using RAGAS metrics."
    )
    parser.add_argument(
        "--input", required=True, help="Path to the processed results JSON file"
    )
    parser.add_argument(
        "--query-dataset", required=True, help="Path to the original dataset JSON file"
    )
    parser.add_argument(
        "--output-dir", default="./evaluation_results", help="Directory to save results"
    )

    args = parser.parse_args()

    try:
        # Load data
        samples = load_dataset(args.input)
        query_dataset = load_dataset(args.query_dataset)

        # Prepare dataset with categories
        dataset = prepare_dataset(samples, query_dataset)

        # Run evaluation
        results = run_evaluation(dataset)

        # Aggregate results by category
        aggregated_results = aggregate_by_category(results, dataset)

        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)

        # Save results
        results.to_csv(f"{args.output_dir}/evaluation_results.csv", index=False)

        with open(f"{args.output_dir}/aggregated_results.json", "w") as f:
            json.dump(aggregated_results, f, indent=2)

        logger.info(f"Evaluation results saved to {args.output_dir}")
        logger.info("Category-based results:")
        logger.info(json.dumps(aggregated_results, indent=2))

    except Exception as e:
        logger.error(f"Error in evaluation: {e}")
        raise


if __name__ == "__main__":
    main()
