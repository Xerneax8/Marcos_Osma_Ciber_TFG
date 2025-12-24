import re
from google import genai
import configparser
import os
from pathlib import Path

from util import take_style, take_theme


# Parse AI response
def parser_ai(all_text: str, directory: Path):
    pattern = r"([\w\-/\.]+)\n```[a-zA-Z]*\n([\s\S]*?)```"

    matches = re.findall(pattern, all_text)
    if not matches:
        raise ValueError("No valid file sections found in the provided text.")

    base_dir = directory.resolve()

    for filepath, content in matches:
        rel_path = Path(filepath)

        # Reject absolute paths
        if rel_path.is_absolute():
            raise ValueError(f"Absolute paths are not allowed: {filepath}")

        # Resolve and enforce sandbox
        target_path = (base_dir / rel_path).resolve()
        if not target_path.is_relative_to(base_dir):
            raise ValueError(f"Path traversal attempt detected: {filepath}")

        # Write file
        with open(target_path, "w") as f:
            f.write(content.strip() + "\n")


def call_ai(text):
    # Configuring OS to get the API Key
    config = configparser.ConfigParser()
    config.read("config.ini")
    os.environ['GEMINI_API_KEY'] = config["API_KEY"]["GEMINI_API_KEY"]

    client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

    # Prompt to retrieve the frontend with all the parts
    return client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[{
            "role": "user",
            "parts": [{
                "text": f"Create a {take_style()} frontend for this backend with theme {take_theme()} (invent fake data if necessary), retrieve all the necessary html, js and css"
                        f" (only use percentages here) retrieve only the code and a line above it indicating static/name"
                        f" or template/name, this last one is important, ignore the healthcheck and if a file misses. {text}"
            }]
        }]
    ).text


def check_ai(llm_text, error):
    # Configuring OS to get the API Key
    config = configparser.ConfigParser()
    config.read("config.ini")
    os.environ['GEMINI_API_KEY'] = config["API_KEY"]["GEMINI_API_KEY"]

    client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

    # Prompt to retrieve the frontend with all the parts
    return client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[{
            "role": "user",
            "parts": [{
                "text": f"You give me this code and it is throwing that error, retrieve the correct code with the same"
                        f"format, this last part is really important.\n{llm_text}\n{error}"
            }]
        }]
    ).text
