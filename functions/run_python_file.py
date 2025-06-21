import os
import subprocess

def run_python_file(working_directory, file_path):
    try:
        working_directory_abs = os.path.abspath(working_directory)
        if os.path.isabs(file_path):
            file_abs = os.path.abspath(file_path)
        else:
            file_abs = os.path.abspath(os.path.join(working_directory_abs, file_path))

        # Guardrail: file must be inside working_directory
        if not file_abs.startswith(working_directory_abs):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        # Check if file exists
        if not os.path.isfile(file_abs):
            return f'Error: File "{file_path}" not found.'

        # Check if file is a Python file
        if not file_abs.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file.'

        # Run the Python file
        result = subprocess.run(
            ["python3", file_abs],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.path.dirname(file_abs)
        )

        output_lines = []
        if result.stdout:
            output_lines.append("STDOUT:")
            output_lines.append(result.stdout.rstrip())
        if result.stderr:
            output_lines.append("STDERR:")
            output_lines.append(result.stderr.rstrip())
        if result.returncode != 0:
            output_lines.append(f"Process exited with code {result.returncode}")

        if not output_lines:
            return "No output produced."
        return "\n".join(output_lines)

    except Exception as e:
        return f"Error: executing Python file: {e}"
