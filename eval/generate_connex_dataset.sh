#!/bin/bash

# Set the total number of samples
TOTAL_SAMPLES=200

# Set the distribution percentages (keeping the same proportions as original)
REGULAR_PERCENT=80
EMERGENCY_PERCENT=10
OUT_OF_SCOPE_PERCENT=10
SUFFIX="connex"
INPUT_DIR="health_rec/data/connex"
INCLUDE_DEMOGRAPHICS=0

# Calculate the number of samples for each situation type
REGULAR_SAMPLES=$((TOTAL_SAMPLES * REGULAR_PERCENT / 100))
EMERGENCY_SAMPLES=$((TOTAL_SAMPLES * EMERGENCY_PERCENT / 100))
OUT_OF_SCOPE_SAMPLES=$((TOTAL_SAMPLES * OUT_OF_SCOPE_PERCENT / 100))

# Ensure we have exactly 200 samples by adjusting regular samples
REGULAR_SAMPLES=$((REGULAR_SAMPLES + TOTAL_SAMPLES - REGULAR_SAMPLES - EMERGENCY_SAMPLES - OUT_OF_SCOPE_SAMPLES))

echo "Generating Connex evaluation dataset with:"
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
    if [ $INCLUDE_DEMOGRAPHICS -eq 1 ]; then
        python3 eval/generate_dataset_demo.py --input_dir  $INPUT_DIR --situation_type $SITUATION --detail_level $DETAIL --num_samples $COUNT --name $OUTPUT_FILE
    else
        python3 eval/generate_dataset.py --input_dir  $INPUT_DIR --situation_type $SITUATION --detail_level $DETAIL --num_samples $COUNT --name $OUTPUT_FILE
    fi
}

# Generate regular samples with varying detail levels
generate_samples regular low $((REGULAR_SAMPLES / 3)) $SUFFIX
generate_samples regular medium $((REGULAR_SAMPLES / 3)) $SUFFIX
generate_samples regular high $((REGULAR_SAMPLES - 2*(REGULAR_SAMPLES / 3))) $SUFFIX

# Generate emergency samples
generate_samples emergency medium $EMERGENCY_SAMPLES $SUFFIX

# Generate out of scope samples
generate_samples out_of_scope medium $OUT_OF_SCOPE_SAMPLES $SUFFIX

# Combine the generated JSON files
echo "Combining generated JSON files..."
python3 eval/combine_json_datasets.py "eval/dataset_*_${SUFFIX}.json" "eval/dataset_${SUFFIX}.json"

# Delete the individual JSON files
echo "Deleting individual JSON files..."
rm eval/dataset_*_${SUFFIX}.json
