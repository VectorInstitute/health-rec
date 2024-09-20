import glob
import json


DATA_PATH = "/mnt/data/211"


data_files = glob.glob(f"{DATA_PATH}/**/*.json", recursive=True)

for data_file in data_files:
    with open(data_file, "r") as f:
        data = json.load(f)
    print(len(data["Records"]))
    print(len(data))