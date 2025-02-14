import json
import glob


def combine_json_files(input_pattern: str, output_file: str) -> None:
    """
    Combines multiple JSON files matching a pattern into a single JSON file.

    Args:
        input_pattern:  A glob pattern (e.g., "data/*.json") specifying the input JSON files.
        output_file:   The path to the output JSON file.
    """

    all_data = []
    file_list = glob.glob(input_pattern)

    if not file_list:
        print(f"Error: No files found matching the pattern '{input_pattern}'.")
        return

    for filename in file_list:
        try:
            with open(filename, "r", encoding="utf-8") as f:  # Specify UTF-8 encoding
                data = json.load(f)
                # Ensure the loaded data is a list
                if isinstance(data, list):
                    all_data.extend(data)
                elif isinstance(data, dict):
                    all_data.append(data)  # add dict as single element in list
                else:
                    print(
                        f"Warning: Skipping {filename} -  content is not a JSON list or dict."
                    )

        except json.JSONDecodeError as e:
            print(f"Error: Could not decode JSON in {filename}: {e}")
            #   Consider adding 'continue' here if you want to skip to the next file on error
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            #   Consider 'continue' here as well.

    if not all_data:
        print("Error: No valid JSON data found to combine.")
        return

    try:
        with open(output_file, "w", encoding="utf-8") as outfile:
            json.dump(
                all_data, outfile, indent=2, ensure_ascii=False
            )  # Use indent for readability, ensure_ascii for Unicode
        print(f"Successfully combined {len(file_list)} files into {output_file}")
    except Exception as e:
        print(f"Error writing to output file: {e}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Combine multiple JSON files into one."
    )
    parser.add_argument(
        "input_pattern", help="Glob pattern for input JSON files (e.g., 'data/*.json')"
    )
    parser.add_argument(
        "output_file", help="Path to the output JSON file (e.g., 'combined.json')"
    )
    args = parser.parse_args()

    combine_json_files(args.input_pattern, args.output_file)


if __name__ == "__main__":
    main()
