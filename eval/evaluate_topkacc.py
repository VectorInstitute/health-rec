import argparse
import torch
import json
import csv
from tqdm import tqdm
from collections import defaultdict
from typing import List, Dict, Any, DefaultDict


def load_embeddings(path: str) -> torch.Tensor:
    return torch.load(path)


def calculate_similarity_scores(
    query_vec: torch.Tensor, doc_vectors: torch.Tensor, scoring_method: str
) -> torch.Tensor:
    if scoring_method == "max":
        # For models like ColBERT
        scores = torch.matmul(
            query_vec.unsqueeze(0).float(), doc_vectors.transpose(1, 2).float()
        )
        max_scores_per_query_term = scores.max(dim=2).values
        total_scores = max_scores_per_query_term.sum(dim=1)
    elif scoring_method == "mean":
        # For single vector per query/doc models
        total_scores = torch.matmul(query_vec.unsqueeze(0), doc_vectors.t()).squeeze(0)
    else:
        raise ValueError("Invalid scoring method. Choose 'max' or 'mean'.")

    return total_scores


def calculate_topk_accuracy(
    query_vectors: torch.Tensor,
    doc_vectors: torch.Tensor,
    ground_truth: List[Any],
    query_dataset: List[Dict[str, Any]],
    k_values: List[int],
    scoring_method: str,
) -> DefaultDict[str, DefaultDict[str, float]]:
    results: DefaultDict[str, DefaultDict[str, float]] = defaultdict(
        lambda: defaultdict(float)
    )
    splits = ["detail_level", "is_emergency", "is_out_of_scope"]
    split_counts: DefaultDict[str, DefaultDict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )

    for k in k_values:
        for i, query_vec in tqdm(enumerate(query_vectors), desc=f"Calculating acc@{k}"):
            total_scores = calculate_similarity_scores(
                query_vec, doc_vectors, scoring_method
            )
            sorted_indices = total_scores.argsort(descending=True)

            topk_indices = sorted_indices[:k]
            topk_ids = [ground_truth[idx] for idx in topk_indices]
            hit = int(query_dataset[i]["context"] in topk_ids)

            results["all"][f"acc@{k}"] += hit
            for split in splits:
                if split in query_dataset[i]:
                    split_value = query_dataset[i][split]
                    results[split][f"{split_value}_acc@{k}"] += hit
                    split_counts[split][split_value] += 1

    total_queries = len(query_vectors)
    for k in k_values:
        results["all"][f"acc@{k}"] /= total_queries
        for split in splits:
            for split_value, count in split_counts[split].items():
                if count > 0:
                    results[split][f"{split_value}_acc@{k}"] /= count

    return results


def save_results_to_csv(
    results: DefaultDict[str, DefaultDict[str, float]],
    experiment_name: str,
    scoring_method: str,
    output_file: str,
) -> None:
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["experiment", "scoring_method", "metric", "value"])

        for category, metrics in results.items():
            for metric, value in metrics.items():
                writer.writerow(
                    [experiment_name, scoring_method, f"{category}_{metric}", value]
                )


def main(args: argparse.Namespace) -> None:
    # Load embeddings
    query_vectors = load_embeddings(args.query_embeddings)
    doc_vectors = load_embeddings(args.doc_embeddings)

    # Load ground truth and query dataset
    with open(args.ground_truth, "r") as f:
        ground_truth: List[Any] = json.load(f)

    with open(args.query_dataset, "r") as f:
        query_dataset: List[Dict[str, Any]] = json.load(f)

    # Calculate top-k accuracy
    k_values = [int(k) for k in args.topk.split(",")]
    results = calculate_topk_accuracy(
        query_vectors,
        doc_vectors,
        ground_truth,
        query_dataset,
        k_values,
        args.scoring_method,
    )

    # Save results
    output_file = f"{args.experiment_name}_{args.scoring_method}_results.csv"
    save_results_to_csv(results, args.experiment_name, args.scoring_method, output_file)
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate top-k accuracy for embeddings"
    )
    parser.add_argument(
        "--query_embeddings", required=True, help="Path to query embeddings .pt file"
    )
    parser.add_argument(
        "--doc_embeddings", required=True, help="Path to document embeddings .pt file"
    )
    parser.add_argument(
        "--ground_truth", required=True, help="Path to ground truth JSON file"
    )
    parser.add_argument(
        "--query_dataset", required=True, help="Path to query dataset JSON file"
    )
    parser.add_argument(
        "--experiment_name", required=True, help="Name of the experiment"
    )
    parser.add_argument(
        "--topk",
        default="5,10,15,20",
        help="Comma-separated list of k values for top-k accuracy",
    )
    parser.add_argument(
        "--scoring_method",
        choices=["max", "mean"],
        required=True,
        help="Scoring method: 'max' for models like ColBERT, 'mean' for single vector models",
    )

    args = parser.parse_args()
    main(args)
