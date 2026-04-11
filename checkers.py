import os
import subprocess
import time
from pathlib import Path
import shutil
import yaml
import urllib.request
import urllib.error
from AI import check_ai, parser_ai
from util import find_resources_folder


# Deploys a Docker container using a shell script and checks its health.
def check_deployment_and_health(directory, check_frontend, timeout=60):
    parent_directory = os.getcwd()
    if not parent_directory:
        print("Error: PWD environment variable not set.")
        return False

    compose_path = os.path.join(Path(directory), "docker-compose.yml")
    if not os.path.exists(compose_path):
        print(f"Error: docker-compose.yml not found in {directory}")
        return False

    if shutil.which("docker") is None:
        return "ERROR: Docker is not installed or not in PATH."

    try:
        os.chdir(Path(directory))
        print(f"Changed to directory: {os.getcwd()}")

        # --- Run deployment script ---
        print("Running deploy-challenge.sh...")
        subprocess.run(["sh", "deploy-challenge.sh"], check=True, capture_output=True, text=True)
        print("Deployment script executed successfully.")

        # --- Poll health endpoint ---
        print(f"Checking container health via docker ps (timeout: {timeout}s)")
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                result = subprocess.run(
                    ["docker", "ps", "--format", "{{.Status}}"],
                    capture_output=True,
                    text=True,
                    check=True
                )

                statuses = result.stdout.strip().splitlines()

                for status in statuses:
                    if "unhealthy" in status:
                        print(f"Health check FAILED: {status}")
                        return "UNHEALTHY"

                    elif "healthy" in status:
                        print(f"Health check PASSED: {status}")
                        if check_frontend:
                            frontend_status = check_frontend_health("docker-compose.yml")
                            if frontend_status != "OK":
                                print("Error rendering frontend")
                                return frontend_status
                        return "OK"

                    elif "starting" in status:
                        print(f"Container starting: {status}")

                print("Container not ready yet, retrying...")

            except subprocess.SubprocessError as e:
                print(f"Docker command failed, retrying... ({e})")

            time.sleep(3)

        print(f"Health check FAILED after {timeout} seconds.")
        return "Health check failed"

    except subprocess.CalledProcessError as e:
        error_msg = f"Deployment failed (exit code {e.returncode}):\n{e.stderr}"
        return error_msg

    except Exception as e:
        error_msg = f"Unexpected error during deployment: {str(e)}"
        return error_msg
    finally:
        print("Cleaning up Docker containers (docker compose down)...")
        subprocess.run(["docker", "compose", "down"], capture_output=True)
        os.chdir(parent_directory)
        print(f"Returned to directory: {parent_directory}\n")


def check_frontend_health(filename):
    try:
        # Load the YAML file
        with open(filename, 'r') as file:
            compose_data = yaml.safe_load(file)

        # Grab the service's port, split by ':', and take the host port
        first_service = next(iter(compose_data['services'].values()))
        target_port = first_service['ports'][0].split(':')[0]

        # Fetch the frontend
        url = f"http://localhost:{target_port}"
        with urllib.request.urlopen(url, timeout=5) as response:
            html_content = response.read().decode('utf-8').lower()

        # Check for keywords
        if "error" in html_content or "exception" in html_content:
            return "UNHEALTHY"

        return "OK"

    except Exception as e:
        # Catch file missing, bad YAML, missing keys, etc.
        return f"ERROR: {str(e)}"


# Retrying generating LLM code if errors are found
def generate_retry(num, ret_str, llm_text, directory, dir_versions_complete_path, dir_versions_name, num_retries,
                   directory_args, max_retries):
    # Check for errors and create new code if necessary
    if ret_str != "OK" and num_retries > 0:
        print("Problems were found, retrying...")
    while ret_str != "OK" and num_retries < max_retries:
        print("Checking with AI...")
        llm_checked_text = check_ai(llm_text, ret_str)
        parser_ai(llm_checked_text,
                  dir_versions_complete_path / (
                      Path(str(directory) + f"-{num + 1}")) / Path(find_resources_folder(dir_versions_complete_path /
                                                                                         Path(
                                                                                             str(directory) + f"-{num + 1}"))))

        ret_str = check_deployment_and_health(
            Path(dir_versions_name) / Path(str(directory) + f"-{num + 1}"), check_frontend=True)
        num_retries += 1

    if ret_str != "OK":
        print(f"Max number of retries reached, problem not solved: {ret_str}")
