#!/bin/bash

# Set the total number of samples
TOTAL_SAMPLES=1000

# Set the distribution percentages
REGULAR_PERCENT=80
EMERGENCY_PERCENT=10
OUT_OF_SCOPE_PERCENT=10
SUFFIX="nb_v4_2"

# Calculate the number of samples for each situation type
REGULAR_SAMPLES=$((TOTAL_SAMPLES * REGULAR_PERCENT / 100))
EMERGENCY_SAMPLES=$((TOTAL_SAMPLES * EMERGENCY_PERCENT / 100))
OUT_OF_SCOPE_SAMPLES=$((TOTAL_SAMPLES * OUT_OF_SCOPE_PERCENT / 100))

# Ensure we have exactly 1000 samples by adjusting regular samples
REGULAR_SAMPLES=$((REGULAR_SAMPLES + TOTAL_SAMPLES - REGULAR_SAMPLES - EMERGENCY_SAMPLES - OUT_OF_SCOPE_SAMPLES))

echo "Generating dataset with:"
echo "Regular samples: $REGULAR_SAMPLES"
echo "Emergency samples: $EMERGENCY_SAMPLES"
echo "Out of scope samples: $OUT_OF_SCOPE_SAMPLES"

# Function to generate samples for a given situation type and detail level
generate_samples() {
    SITUATION=$1
    DETAIL=$2
    COUNT=$3
    SUFFIX=$4
    OUTPUT_FILE="dataset_${SITUATION}_${DETAIL}_${SUFFIX}"
    
    echo "Generating $COUNT $SITUATION samples with $DETAIL detail level..."
    python3 eval/generate_dataset.py --situation_type $SITUATION --detail_level $DETAIL --num_samples $COUNT --name $OUTPUT_FILE
}

# Generate regular samples with varying detail levels
generate_samples regular low $((REGULAR_SAMPLES / 3)) $SUFFIX
generate_samples regular medium $((REGULAR_SAMPLES / 3)) $SUFFIX
generate_samples regular high $((REGULAR_SAMPLES - 2*(REGULAR_SAMPLES / 3))) $SUFFIX

# Generate emergency samples
generate_samples emergency medium $EMERGENCY_SAMPLES $SUFFIX

# Generate out of scope samples
generate_samples out_of_scope medium $OUT_OF_SCOPE_SAMPLES $SUFFIX

# echo "All samples generated. Combining into a single file..."

# Combine all generated files into a single dataset
# jq -s 'flatten' dataset_*.json > combined_dataset.json

# Count the total number of samples in the combined dataset
# TOTAL_GENERATED=$(jq length combined_dataset.json)

# echo "Combined dataset created with $TOTAL_GENERATED samples."

# Clean up individual files
# rm dataset_*.json

# echo "Individual dataset files removed. Process complete."