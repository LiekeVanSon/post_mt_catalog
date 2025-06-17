import json
import numpy as np


def read_json_file(file_path):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


def main():
    file_path = "../data/dummy.json"
    data = read_json_file(file_path)
    if data:
        print(f"Number of entries: {len(data)}")
        if data:
            print("Sample entry:")
            print(json.dumps(data[0], indent=2))

    # Make arrays of the data
    system_name = [entry["System Name"] for entry in data]
    m1 = np.array([entry["M1"] for entry in data])

    print(system_name)
    print(m1)
    print(m1[:, 0])


if __name__ == "__main__":
    main()
