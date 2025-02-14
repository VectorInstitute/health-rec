#!/bin/bash

# Set the base directory for the datasets (adjust if needed)
DATA_DIR="."

# Define the categories and detail levels
CATEGORIES=("regular" "emergency" "out_of_scope")
DETAIL_LEVELS=("low" "medium" "high")

# Endpoint for the RAG system (adjust if needed)
ENDPOINT="http://localhost:8005/recommend"

# Batch size for processing queries (adjust if needed)
BATCH_SIZE=5

# Output directory for all evaluations
MAIN_OUTPUT_DIR="evaluation_results"
mkdir -p "$MAIN_OUTPUT_DIR"

# Create a temporary directory to store intermediate RAG outputs
TEMP_RAG_OUTPUT_DIR="$MAIN_OUTPUT_DIR/temp_rag_outputs"
mkdir -p "$TEMP_RAG_OUTPUT_DIR"

# Initialize an empty associative array (dictionary) to store results
declare -A results_table

# Function to add results to the table
add_to_results_table() {
  local category="$1"
  local detail_level="$2"
  local metric_name="$3"
  local metric_value="$4"
  results_table["${category}_${detail_level}_${metric_name}"]="$metric_value"
}

# Loop through categories and detail levels
for category in "${CATEGORIES[@]}"; do
  for detail_level in "${DETAIL_LEVELS[@]}"; do
    echo "Processing: $category - $detail_level"

    # Construct the input file path
    input_file="$DATA_DIR/connex_dataset_${category}_${detail_level}_connex_v1.json"

    # Check if the input file exists
    if [ ! -f "$input_file" ]; then
      echo "Error: Input file not found: $input_file"
      continue  # Skip to the next iteration
    fi
    
    # Temporary output path
    temp_output_file="${TEMP_RAG_OUTPUT_DIR}/rag_output_${category}_${detail_level}.json"


    # Run collect_rag_outputs.py
    echo "Running collect_rag_outputs.py..."
    python collect_rag_outputs.py --input "$input_file" --output "$temp_output_file" --batch-size "$BATCH_SIZE" --endpoint "$ENDPOINT"

    # Create a subdirectory for each evaluation
    output_dir="${MAIN_OUTPUT_DIR}/${category}_${detail_level}"
    mkdir -p "$output_dir"


    # Run evaluate.py
    echo "Running evaluate.py..."
    python evaluate.py --input "$temp_output_file" --output-dir "$output_dir"

    # Load the evaluation results from the generated dataset.json
    eval_results_file="$output_dir/dataset.json"
    if [ ! -f "$eval_results_file" ]; then
        echo "Error: Evaluation file does not exists."
        exit 1
    fi
    answer_relevancy_score=$(jq '.answer_relevancy' "$eval_results_file")
    faithfulness_score=$(jq '.faithfulness' "$eval_results_file")
    context_recall_score=$(jq '.context_recall' "$eval_results_file")
    context_precision_score=$(jq '.context_precision' "$eval_results_file")


    # Add results to the table
    add_to_results_table "$category" "$detail_level" "answer_relevancy" "$answer_relevancy_score"
    add_to_results_table "$category" "$detail_level" "faithfulness" "$faithfulness_score"
    add_to_results_table "$category" "$detail_level" "context_recall" "$context_recall_score"
    add_to_results_table "$category" "$detail_level" "context_precision" "$context_precision_score"

    echo "Evaluation completed for $category - $detail_level. Results saved to $output_dir"
  done
done

# Print the results table
echo ""
echo "------------------------------------"
echo "           Evaluation Results         "
echo "------------------------------------"
echo ""

# Print header row
printf "%-20s %-10s %-20s %-15s %-15s %-15s\n" "Category" "Detail" "Metric" "Score1" "Score2" "Score3"

# Loop through detail levels for consistent column order within each category
for category in "${CATEGORIES[@]}"; do
    for detail_level in "${DETAIL_LEVELS[@]}"; do
        printf "%-20s %-10s %-20s %-15s %-15s %-15s\n" \
               "$category" \
               "$detail_level" \
               "answer_relevancy" \
               "${results_table[${category}_${detail_level}_answer_relevancy]}" \
               "" \
               ""
    done
    for detail_level in "${DETAIL_LEVELS[@]}"; do
        printf "%-20s %-10s %-20s %-15s %-15s %-15s\n" \
               "$category" \
               "$detail_level" \
               "faithfulness" \
                "" \
               "${results_table[${category}_${detail_level}_faithfulness]}" \
               ""
    done
        for detail_level in "${DETAIL_LEVELS[@]}"; do
        printf "%-20s %-10s %-20s %-15s %-15s %-15s\n" \
               "$category" \
               "$detail_level" \
               "context_recall" \
               "" \
               "" \
               "${results_table[${category}_${detail_level}_context_recall]}"
    done
    for detail_level in "${DETAIL_LEVELS[@]}"; do
        printf "%-20s %-10s %-20s %-15s %-15s %-15s\n" \
               "$category" \
               "$detail_level" \
               "context_precision" \
               "${results_table[${category}_${detail_level}_context_precision]}" \
               "" \
               ""
    done

done
echo "------------------------------------"

# Clean up the temporary directory
rm -rf "$TEMP_RAG_OUTPUT_DIR"

echo "All evaluations completed. Combined results printed above."