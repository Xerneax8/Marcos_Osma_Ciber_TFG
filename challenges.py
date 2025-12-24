import sys
import os
from pathlib import Path
import shutil

from AI import parser_ai, call_ai
from checkers import check_deployment_and_health, generate_retry
from parsers import parse_code
from files import generate_prompt_code
from util import find_resources_folder, list_folders_with_file_type


# Create the versions for the students
def create_different_versions(result, dir_versions_complete_path, directory, dir_versions_name, directory_args,
                              num_versions, max_retries):
    for num in range(num_versions):
        print(f"Calling AI for version {num + 1}...")
        llm_text = call_ai(result)
        print(f"Writing LLM code for version {num + 1}...")
        parser_ai(llm_text,
                  dir_versions_complete_path / (
                      Path(str(directory) + f"-{num + 1}")) / Path(find_resources_folder(dir_versions_complete_path /
                                                                                         Path(
                                                                                             str(directory) + f"-{num + 1}"))))
        print(f"Checking code for version {num + 1}...")
        ret_str = check_deployment_and_health(
            Path(dir_versions_name) / Path(str(directory) + f"-{num + 1}"), directory_args)
        num_retries = 0
        generate_retry(num, ret_str, llm_text, directory, dir_versions_complete_path, dir_versions_name, num_retries,
                       directory_args, max_retries)


# Process each challenge
def process_challenge(directory, num_versions, directory_args, max_retries):
    dir_versions_name = directory + "-versions"
    dir_versions_complete_path = Path(os.path.dirname(os.path.abspath(sys.argv[0]))) / dir_versions_name

    try:
        os.mkdir(dir_versions_complete_path)
        print("Creating versions folder...")
        for num in range(num_versions):
            shutil.copytree(directory, dir_versions_complete_path / (directory + f"-{num + 1}"))

        directory = Path(directory)

        if list_folders_with_file_type(directory) is None:
            raise FileNotFoundError("No Python, JavaScript or Java files were found...")
        else:
            complete_path_challenge_directories_python = directory / list_folders_with_file_type(directory)

        text = generate_prompt_code(complete_path_challenge_directories_python)

        result = parse_code(text)

        create_different_versions(result, dir_versions_complete_path, directory, dir_versions_name,
                                  directory_args, num_versions, max_retries)
    except FileExistsError:
        print(str(directory) + " DONE")
