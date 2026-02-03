import re
from google import genai
import configparser
import os
from pathlib import Path

from util import take_style, take_theme


# Parse AI response
def parser_ai(all_text: str, directory: Path):
    all_text = all_text.replace("`", "")
    pattern = r"(?:^|\n)((?:static|templates)\/[^\n]+)\n([\s\S]*?)(?=\n(?:static|templates)\/)"

    matches = re.findall(pattern, all_text)
    if not matches:
        raise ValueError("No valid file sections found in the provided text.")

    base_dir = directory.resolve()

    for filepath, content in matches:
        rel_path = Path(filepath)

        lines = content.splitlines()
        content = "\n".join(lines[1:])

        # Reject absolute paths
        if rel_path.is_absolute():
            raise ValueError(f"Absolute paths are not allowed: {filepath}")

        # Resolve and enforce sandbox
        target_path = (base_dir / rel_path).resolve()

        # Remove subfolders in static
        parts = list(target_path.parts)

        filtered = [p for p in parts if p not in ("css", "js")]

        target_path = Path(str(Path(*filtered)))

        if not target_path.is_relative_to(base_dir):
            raise ValueError(f"Path traversal attempt detected: {filepath}")

        # Write file
        with open(target_path, "w") as f:
            f.write(content.strip() + "\n")


def call_ai(text, num):
    # Configuring OS to get the API Key
    config = configparser.ConfigParser()
    config.read("config.ini")
    os.environ['GEMINI_API_KEY'] = config["API_KEY"]["GEMINI_API_KEY"]

    client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))


    template = input("Which template engine should it work for? (Press enter for no template engine)\n")

    print(f"Calling AI for version {num + 1}...")
    if not template:
        template = "Use no templates"
    # Prompt to retrieve the frontend with all the parts
    return client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[{
            "role": "user",
            "parts": [{
                "text": f"Create a {take_style()} frontend for this backend with theme {take_theme()} (invent fake data if necessary, do NOT use the word placeholder, but if the backend has data to include, use it), retrieve all the necessary html, js and css retrieve only the code (one css per html), no images, and a line above it indicating static/name or templates/name, do not include more folders, the line above them is really important, always is important to include a index.html, ignore the healthcheck and if a file misses. Do not include new functionality with JavaScript, just for esthetical purposes. The static folder is at the same level as the template folder, when referrencing css and js files from html mention only the name except if there is an endpoint to access files or using a template (in that case use the tools of the template), the folder static has no more folders inside, drop all the files just there. Every css and js file should have its own html file, so there should be the same number of html and css files, count the files to assure that. Do not include things that have no backend and could fail. If it uses templates, use only one {template} (BE CAREFUL with template syntax, asure it works fine, also when accesing the css and js files from the html) and use the backend outputs (all outputs for the template MUST be optional in the html in case they do not exist), but ONLY use html, css and js files. If in the text below appear a CSRF token, send it HIDDEN in the HTML, use them if the user has to introduce credentials. Make it vulnerable to XSS if backend has no other vulnerabilities, but do NOT mention it.\n{text}"
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
