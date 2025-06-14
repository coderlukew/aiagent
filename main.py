import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# Check for prompt argument
if len(sys.argv) < 2:
    print("Error: No prompt provided.")
    sys.exit(1)

# Handle --verbose flag
verbose = False
args = sys.argv[1:]  # All arguments after script name
if "--verbose" in args:
    verbose = True
    args.remove("--verbose")

# Join all arguments after the script name to allow multi-word prompts
prompt = " ".join(args)

messages = [
    types.Content(role="user", parts=[types.Part(text=prompt)]),
]

response = client.models.generate_content(
    model='gemini-2.0-flash-001', contents=messages
)
print(response.text)

if verbose:
    print(f'User prompt: {prompt}')
    print(f'Prompt tokens: {response.usage_metadata.prompt_token_count}')
    print(f'Response tokens: {response.usage_metadata.candidates_token_count}')