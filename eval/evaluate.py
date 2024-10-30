import argparse
import json
import logging
from typing import List, Dict, Any

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


def load_samples(file_path: str) -> Any:
    """Load evaluation samples from a JSON file."""
    with open(file_path, "r") as f:
        return json.load(f)


def prepare_dataset(samples: List[Dict[str, Any]]) -> Dataset:
    """Prepare the dataset for RAGAS evaluation."""
    return Dataset.from_dict(
        {
            "question": [sample["query"] for sample in samples],
            "answer": [sample["answer"] for sample in samples],
            "contexts": [sample["context"] for sample in samples],
            "ground_truth": [sample.get("ground_truth", []) for sample in samples],
        }
    )


def run_evaluation(dataset: Dataset) -> Any:
    """Run the RAGAS evaluation."""
    return evaluate(
        dataset=dataset,
        metrics=[
            answer_relevancy,
            faithfulness,
            context_recall,
            context_precision,
        ],
    )


def main() -> None:
    """Main function for RAGAS evaluation."""
    parser = argparse.ArgumentParser(
        description="Evaluate RAG system outputs using RAGAS metrics."
    )
    parser.add_argument(
        "--input", required=True, help="Path to the processed results JSON file"
    )
    parser.add_argument(
        "--output-dir", default="./evaluation_results", help="Directory to save results"
    )

    args = parser.parse_args()

    # Load and prepare samples
    samples = load_samples(args.input)
    dataset = prepare_dataset(samples)

    # Run evaluation
    results = run_evaluation(dataset)

    # Save results
    results.save_to_disk(args.output_dir)
    logger.info(f"Evaluation results saved to {args.output_dir}")


if __name__ == "__main__":
    main()
