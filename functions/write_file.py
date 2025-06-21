import os

def write_file(working_directory, file_path, content):
    try:
        working_directory_abs = os.path.abspath(working_directory)
        if os.path.isabs(file_path):
            file_abs = os.path.abspath(file_path)
        else:
            file_abs = os.path.abspath(os.path.join(working_directory_abs, file_path))

        # Guardrail: file must be inside working_directory
        if not file_abs.startswith(working_directory_abs):
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        # Ensure parent directory exists
        parent_dir = os.path.dirname(file_abs)
        os.makedirs(parent_dir, exist_ok=True)

        # Write content to file (overwrite)
        with open(file_abs, "w", encoding="utf-8") as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except Exception as e:
        return f"Error: {str(e)}"
