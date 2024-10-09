import json
import glob
from typing import List, Dict, Any
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_recall,
    context_precision,
)
from datasets import Dataset

def load_samples(file_pattern: str) -> List[Dict[str, Any]]:
    samples = []
    for file_path in glob.glob(file_pattern):
        with open(file_path, 'r') as f:
            samples.extend(json.load(f))
    return samples

def prepare_dataset(samples: List[Dict[str, Any]]) -> Dataset:
    return Dataset.from_dict({
        "question": [sample["query"] for sample in samples],
        "answer": [sample["answer"] for sample in samples],
        "contexts": [sample["context"] for sample in samples],
        "ground_truth": [sample["answer"] for sample in samples],
    })

def run_evaluation(dataset: Dataset) -> Dict[str, float]:
    result = evaluate(
        dataset=dataset,
        metrics=[
            answer_relevancy,
            faithfulness,
            context_recall,
            context_precision,
        ]
    )
    return result

def main():
    # Load samples from JSON files
    samples = load_samples("./rag_eval_nb_v4_2.json")
    
    # Prepare the dataset
    dataset = prepare_dataset(samples)
    
    # Run the evaluation
    results = run_evaluation(dataset)
    
    # Print the results
    # print("Evaluation Results:")
    # for metric, score in results.items():
    #     print(f"{metric}: {score:.4f}")

    results.save_to_disk("evaluation_results")

if __name__ == "__main__":
    main()