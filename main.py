import os
import argparse

from challenges import process_challenge
from checkers import check_deployment_and_health
from util import parse_arguments


def main():
    # Get all arguments
    parser = argparse.ArgumentParser()
    parse_arguments(parser)
    args = parser.parse_args()
    num_versions = int(args.number[0])
    max_retries = int(args.retries[0])
    directory_args = args.directory[0]

    if num_versions <= 0:
        print("Number of versions should be greater than zero...")
        exit()

    # Getting all the challenge directories of one folder
    files = os.listdir(directory_args)
    list_challenge_directories = sorted([file for file in files if
                                         "web" in file and "versions" not in file])  # All the directories with "web" in their name or "versions"

    # Pipeline to get the backend file, give it to Gemini and write back the answer
    for directory in list_challenge_directories:
        ret_str = check_deployment_and_health(directory, directory_args)
        if ret_str == "OK":
            process_challenge(directory, num_versions, directory_args, max_retries)
        else:
            print(f"Exercise " + directory + f" can't be deployed for checking, check the code...\nError: {ret_str}")


if __name__ == "__main__":
    main()
