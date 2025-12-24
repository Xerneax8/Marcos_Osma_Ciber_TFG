# Marcos Osma TFG

The functionality of this program is generating frontend code through LLM (Gemini) for any backend code, but it is addressed 
to be used in cybersecurity challenges for students.

The program can process three backend languages at the moment: Python, Java and JavaScript and the only thing left to do should be 
the frontend part of the challenge.

## Project Structure
The "challenges" folder should contain one folder per challenge that has to be processed.

Any challenge should include Docker files to check the project on a controlled environment. Docker files that are mandatory:
"docker-challenge.sh", with the docker compose commands, "docker-compose.yml" with the instructions to compose the docker and a "Dockerfile"
where the docker is described. This files should be just under the root of the challenge.

Lastly, it should include a folder named "resources" on any part of the challenge where the code should take the frontend. In that folder, the
LLM code would be written when crafted.

## Usage
Firstly, it is important to get a Gemini API key to use this program (https://aistudio.google.com/api-keys).
That key should be place in a config.ini file with this format:

"[API_KEY]"\
GEMINI_API_KEY= '\<API KEY\>'

Now with the main program, it has three parameters to change a variety of things: 
* -d is for changing the directory where the program is going to take the challenges folders.
* -n is for the numbers of different versions of the frontend code that you want for each challenge.
* -r is for the number of retries that the program is going to make in case a piece of code is malfunctioning.

All of them has default values, and they could be customised. There is more info when using the -h command to get help.

A basic usage of the program would be just calling the program, this would take the current directory of the script as the
one to look for the challenges folder, it would create a single copy of the program with an AI generated frontend and it would not have any retries.

If you want custom parameters, run the program with the arguments mentioned above, for example: ./main.py -d "/home/user/challenges" -n 2 -r 1. This 
would take the challenges from the /home/user/challenges folder and would make 2 versions of the frontend with 1 retry if the AI fails on the first time.
