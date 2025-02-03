"""Load ON and 211CX data, and filter out the ConnexOntario data."""

import argparse
from typing import List, Set
import json
import os
import glob
from pathlib import Path


def get_unique_ids(files: List[str]) -> Set[str]:
    """Get unique IDs from the given files.

    Parameters
    ----------
    files : list
        List of file paths.

    Returns
    -------
    set
        Set of unique IDs.

    """
    ids = set()
    for file in files:
        with open(file) as f:
            data = json.load(f)
            for entry in data:
                ids.add(str(entry["id"]))
    return ids


def filter_connex_data(data_dir: Path) -> None:
    """Filter out ConnexOntario data from the 211 data.

    Parameters
    ----------
    data_dir : Path
        Directory with saved 211 data.

    """
    ontario_with_connex_files_path = os.path.join(data_dir, "211CX")
    ontario_files_path = os.path.join(data_dir, "on")
    ontario_with_connex_files = list(
        glob.glob(os.path.join(ontario_with_connex_files_path, "*.json"))
    )
    ontario_files = list(glob.glob(os.path.join(ontario_files_path, "*.json")))
    ontario_with_connex_ids = get_unique_ids(ontario_with_connex_files)
    ontario_ids = get_unique_ids(ontario_files)
    connex_ids = ontario_with_connex_ids - ontario_ids
    connex_data = []
    for file in ontario_with_connex_files:
        with open(file) as f:
            data = json.load(f)
            for entry in data:
                if entry["id"] in connex_ids:
                    connex_data.append(entry)
    os.makedirs(os.path.join(data_dir, "connex"), exist_ok=True)
    with open(os.path.join(data_dir, "connex", "data-00.json"), "w") as f:
        json.dump(connex_data, f, indent=2)


def main() -> None:
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description="Filter out connex data.")
    parser.add_argument(
        "--data-dir",
        default="/mnt/data/211",
        help="Directory with saved 211 data",
        type=Path,
    )

    args = parser.parse_args()
    filter_connex_data(args.data_dir)


if __name__ == "__main__":
    main()
