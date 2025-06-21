import os

def get_file_content(working_directory, file_path):
    try:
        working_directory_abs = os.path.abspath(working_directory)
        if os.path.isabs(file_path):
            file_abs = os.path.abspath(file_path)
        else:
            file_abs = os.path.abspath(os.path.join(working_directory_abs, file_path))

        # Guardrail: file must be inside working_directory
        if not file_abs.startswith(working_directory_abs):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        # Check if it is a regular file
        if not os.path.isfile(file_abs):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        # Read file content
        with open(file_abs, "r", encoding="utf-8") as f:
            content = f.read()

        # Truncate if needed
        if len(content) > 10000:
            content = content[:10000] + f'\n[...File "{file_path}" truncated at 10000 characters]'
        return content

    except Exception as e:
        return f"Error: {str(e)}"
