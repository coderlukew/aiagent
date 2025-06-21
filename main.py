import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.call_function import call_function

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

if len(sys.argv) < 2:
    print("Error: No prompt provided.")
    sys.exit(1)

# Handle --verbose flag
verbose = False
args = sys.argv[1:]
if "--verbose" in args:
    verbose = True
    args.remove("--verbose")

prompt = " ".join(args)

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

# Function schemas
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)
schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads and returns the contents of a file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to read, relative to the working directory.",
            ),
        },
    ),
)
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file with optional arguments, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to execute, relative to the working directory.",
            ),
        },
    ),
)
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes or overwrites a file with the provided content, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write into the file.",
            ),
        },
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

messages = [
    types.Content(role="user", parts=[types.Part(text=prompt)]),
]

MAX_ITERATIONS = 20

for i in range(MAX_ITERATIONS):
    if verbose:
        print(f"\n--- Iteration {i+1}/{MAX_ITERATIONS} ---")

    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt
        )
    )

    # Add all candidate responses to message history
    if not response.candidates:
        print("No response candidates found")
        break

    for candidate in response.candidates:
        if candidate.content:
            messages.append(candidate.content)
            if verbose:
                print(f"Added candidate response: {candidate.content}")

    # Handle function calls
    if hasattr(response, "function_calls") and response.function_calls:
        for function_call_part in response.function_calls:
            function_call_result = call_function(function_call_part, verbose=verbose)
            # Check for the required function_response structure
            try:
                function_response = function_call_result.parts[0].function_response.response
            except AttributeError:
                raise RuntimeError("Fatal: function_call_result does not have the expected .parts[0].function_response.response structure!")
            if verbose:
                print(f"-> {function_response}")
            # Add the tool response to the message history so the LLM can see the result
            messages.append(function_call_result)
    else:
        # No function calls - print the final LLM response and break
        if response.text:
            print(f"\nFinal response: {response.text}")
        else:
            print("No text response generated")
        break
else:
    print(f"\nReached maximum iterations ({MAX_ITERATIONS}) without completion")

if verbose:
    print(f'User prompt: {prompt}')
    print(f'Prompt tokens: {response.usage_metadata.prompt_token_count}')
    print(f'Response tokens: {response.usage_metadata.candidates_token_count}')
