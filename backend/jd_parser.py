import os


def extract_jd_text(relative_path):
    base_dir = os.path.dirname(__file__)      
    full_path = os.path.abspath(
        os.path.join(base_dir, relative_path)
    )

    with open(full_path, "r", encoding="utf-8") as file:
        return file.read()
