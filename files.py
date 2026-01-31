from parsers import parse_code

# Get the names of the file that we are going to send to the LLM
def get_source_files(path):
    print("Getting source code files...")
    files_list = [str(p.resolve()) for p in path.rglob("*") if p.suffix in {".py", ".java", ".js"}]
    endpoint_file_list = []
    for file in files_list:
        if detect_endpoint_file(file):
            endpoint_file_list.append(file)

    return endpoint_file_list

def detect_endpoint_file(file_path):
    with open(file_path, "r") as f:
        endpoint_code = f.read()
    f.close()
    result = parse_code(endpoint_code)

    return result


# Read the code and return string
def read_code(source_files):
    print("Reading code...")

    text = ""
    for file in source_files:
        with open(file, "r+") as f:
            text += f.read() + "\n"
        f.close()

    return text


# Get all files and return the string
def generate_prompt_code(complete_path):
    source_files = get_source_files(complete_path)

    return read_code(source_files)
