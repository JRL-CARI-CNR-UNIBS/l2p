import os, json


def load_file(file_path):
    _, ext = os.path.splitext(file_path)
    with open(file_path, "r") as file:
        if ext == ".json":
            return json.load(file)
        else:
            return file.read().strip()
