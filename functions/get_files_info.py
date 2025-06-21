import os

def get_files_info(working_directory, directory=None):
    try:
        working_directory_abs = os.path.abspath(working_directory)
        if directory is None:
            directory_abs = working_directory_abs
        elif os.path.isabs(directory):
            directory_abs = os.path.abspath(directory)
        else:
            # Join directory relative to working_directory
            directory_abs = os.path.abspath(os.path.join(working_directory_abs, directory))

        # Guardrail: directory must be inside working_directory
        if not directory_abs.startswith(working_directory_abs):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        if not os.path.isdir(directory_abs):
            return f'Error: "{directory}" is not a directory'

        entries = []
        for entry_name in os.listdir(directory_abs):
            entry_path = os.path.join(directory_abs, entry_name)
            is_dir = os.path.isdir(entry_path)
            is_file = os.path.isfile(entry_path)
            size = os.path.getsize(entry_path) if is_file else 0
            entries.append(
                f"- {entry_name}: file_size={size} bytes, is_dir={str(is_dir)}"
            )

        return "\n".join(entries)

    except Exception as e:
        return f"Error: {str(e)}"
