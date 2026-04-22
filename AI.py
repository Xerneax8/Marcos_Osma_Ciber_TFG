import re
from google import genai
import configparser
import os
from pathlib import Path

from quality import analyze_web_code
from util import take_style, take_theme


# Parse AI response
def parser_ai(all_text: str, directory: Path):
    all_text = all_text.replace("`", "")
    pattern = r"(?m)^((?:static|templates)/[^\n]+)\n([\s\S]*?)(?=^(?:static|templates)/[^\n]+|\Z)"

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
        analyze_web_code(target_path)


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
                "text": f"""
                        Act as a Frontend Developer. Create a {take_style()} frontend for the backend text provided below using the {take_theme()} theme.
                        
                        INPUT CONTEXT:
                        Backend Code/Context: {text}
                        Data Handling: Use backend data if available. If not, invent realistic fake data all over.
                        
                        OUTPUT REQUIREMENTS:
                        Retrieve only the raw code. Only text. 
                        Precede every file code block with a single line indicating its path (e.g, static/file.html or templates/file.html). This is CRITICAL. The 'static' folder has nothing more inside. Omit the type of the file before creating it.
                        Every HTML file must have exactly one corresponding CSS file (1:1 ratio). IMPORTANT.
                        Always include an 'index.html'. 
                        Implement each file independently.
                        Design the website using text-only content, without images.
                        Minimize the number of output files.
                        
                        TECHNICAL CONSTRAINTS:
                        Use {template} syntax, use the static folder if it mentions no template syntax. 
                        Ensure variables are optional in HTML. And minimize the number of variable sif using a template.
                        The variable name form should be avoided in HTML, and avoid block titles.
                        Use JavaScript ONLY for UI aesthetics. 
                        Keep the contents of an endpoint in those endpoints.
                        If a CSRF token appears in the text, send it as a HIDDEN field in HTML forms in the HTML, use them if the user has to introduce credentials. REALLY IMPORTANT to be hidden with HTML tag.
                        Ignore healthchecks.
                        Always give feedback if there is a login if the login was succesful or not.
                        Make the web vulnerable to XSS if there are no other vulnerabilities or file access endpoints, let this remain unmentioned. 
                        ONLY include methods that are supported by the backend, and only reference files that you do create.
                        Only include response from functions on the web if the web is using templates, take it on account from above.
                        """
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
                "text": f"The code is throwing that error, retrieve the correct code with the same"
                        f"format, this last part is really important."
                        f"CODE:"
                        f"{llm_text}"
                        f"ERROR:"
                        f"{error}"
            }]
        }]
    ).text
