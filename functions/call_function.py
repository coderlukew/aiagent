from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file
from google.genai import types

def call_function(function_call_part, verbose=False):
    # Step 1: Prepare function lookup dictionary
    function_map = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "run_python_file": run_python_file,
        "write_file": write_file,
    }

    function_name = function_call_part.name
    args = dict(function_call_part.args)  # ensure it's a dict

    # Step 2: Add working_directory to args
    args["working_directory"] = "./calculator"

    # Step 3: Print function call info
    if verbose:
        print(f"Calling function: {function_name}({args})")
    else:
        print(f" - Calling function: {function_name}")

    # Step 4: Call the function if valid, else return error Content
    func = function_map.get(function_name)
    if func is None:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    # Step 5: Actually call the function and capture result
    try:
        function_result = func(**args)
    except Exception as e:
        function_result = f"Error during function execution: {e}"

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )
