import os
import subprocess
import time
from pathlib import Path
import requests
import yaml

from AI import check_ai, parser_ai
from util import find_resources_folder


def check_deployment_and_health(directory, directory_arg, timeout=60):
    """
    Deploys a Docker container using a shell script and checks its health endpoint.
    Automatically reads the healthcheck URL and correct port (host-side) from docker-compose.yml.
    """
    parent_directory = os.getcwd()
    if not parent_directory:
        print("Error: PWD environment variable not set.")
        return False

    compose_path = os.path.join(Path(directory_arg) / Path(directory), "docker-compose.yml")
    if not os.path.exists(compose_path):
        print(f"Error: docker-compose.yml not found in {directory}")
        return False

    try:
        # Parse docker-compose.yml
        with open(compose_path, "r") as f:
            compose_data = yaml.safe_load(f)

        services = compose_data.get("services", {})
        if not services:
            print("Error: No services defined in docker-compose.yml.")
            return False

        # Get the first service
        service_name, service_data = next(iter(services.items()))
        ports = service_data.get("ports", [])
        healthcheck = service_data.get("healthcheck", {}).get("test", [])

        if not ports:
            print("Error: No ports defined in service.")
            return False

        # Extract host port (the part AFTER ":")
        port_mapping = ports[0]
        parts = port_mapping.split(":")
        if len(parts) != 2:
            print(f"Invalid port mapping format: {port_mapping}")
            return False

        host_port, container_port = parts  # "12104:8080"
        host_port = host_port.strip().strip('"').strip("'")

        # Extract healthcheck URL if defined, else default
        health_url = None
        for part in healthcheck:
            if part.startswith("http"):
                health_url = part.replace(container_port, host_port)
                break

        if not health_url:
            # Fallback default
            health_url = f"http://localhost:{host_port}/health"

        print(f"Using healthcheck URL: {health_url}")

        os.chdir(Path(directory_arg) / Path(directory))
        print(f"Changed to directory: {os.getcwd()}")

        # --- Run deployment script ---
        print("Running deploy-challenge.sh...")
        subprocess.run(["sh", "deploy-challenge.sh"], check=True, capture_output=True, text=True)
        print("Deployment script executed successfully.")

        # --- Poll health endpoint ---
        print(f"Checking health at {health_url} (timeout: {timeout}s)")
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                resp = requests.get(health_url, timeout=5)
                if resp.ok:
                    print(f"Health check PASSED with status {resp.status_code}")
                    return "OK"
                print(f"Health check returned status {resp.status_code}, retrying...")
            except requests.RequestException:
                print("Container not ready yet, retrying...")
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
            Path(dir_versions_name) / Path(str(directory) + f"-{num + 1}"), directory_args)
        num_retries += 1

    if ret_str != "OK":
        print(f"Max number of retries reached, problem not solved: {ret_str}")
    else:
        print("Exercise " + str(directory) + " crafted")