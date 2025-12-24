import random
from pathlib import Path
import os


# ------------ Random themes ----------
# Get an style for the frontend
def take_style():
    with open("styles.txt", "r+") as f:
        styles = f.read()
    f.close()

    styles_list = styles.split("\n")

    return styles_list[random.randint(0, len(styles_list) - 1)]


def take_theme():
    with open("themes.txt", "r+") as f:
        themes = f.read()
    f.close()

    themes_list = themes.split("\n")

    return themes_list[random.randint(0, len(themes_list) - 1)]

# ---------------------------------------


# ------------ Folders finders ----------
def list_folders_with_file_type(folder_path):
    file_types = ["py", "js", "java"]
    root = Path(folder_path)

    for file_type in file_types:
        extension = f".{file_type.lstrip('.')}"
        for p in root.rglob(f"*{extension}"):
            if p.is_file():
                return Path(str(p.parent.relative_to(root)))

    return None


def find_resources_folder(folder_path):
    root = Path(folder_path).expanduser().resolve()

    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")

    for dirpath, dirnames, _ in os.walk(root):
        for d in dirnames:
            if d == "resources":
                return (Path(dirpath) / d).relative_to(root)

    return None

# ---------------------------------------


def parse_arguments(parser):
    parser.add_argument("-d", "--directory", nargs="*", default=".",
                        help="Directory where the script will take the folders of the challenges. Default value: Current Directory")
    parser.add_argument("-n", "--number", nargs="*", default="1",
                        help="Number of copies of each challenge, it should be at least 1. Default value: 1")
    parser.add_argument("-r", "--retries", nargs="*", default="0",
                        help="Times that the script try to fix the issues of the LLM. Default value: 0")
