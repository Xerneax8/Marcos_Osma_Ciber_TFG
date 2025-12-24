import os


# Get the names of the file that we are going to send to the LLM
def get_source_files(path):
    print("Getting source code files...")
    files_list = []
    if os.path.isdir(path / "controller"):
        list_per_directory = os.listdir(path / "controller")
        files_list.append([file for file in list_per_directory if "Web" in file])
    else:
        list_per_directory = os.listdir(path)
        files_list.append([file for file in list_per_directory if "Web" in file])
    return files_list


# Read the code and return string
def read_code(complete_path, source_files):
    print("Reading code...")
    with open(complete_path / source_files[0][0], "r+") as f:
        text = f.read()
    f.close()

    return text


# Get all files and return the string
def generate_prompt_code(complete_path):
    source_files = get_source_files(complete_path)

    return read_code(complete_path, source_files)
