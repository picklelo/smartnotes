def run_python_script(script_content):
    import subprocess
    import tempfile
    import os

    # Create a temporary file to store the script
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
        temp_file.write(script_content)
        temp_file_path = temp_file.name

    try:
        # Run the Python script and capture the output
        result = subprocess.run(
            ["python", temp_file_path], capture_output=True, text=True, timeout=30
        )
        output = result.stdout
        error = result.stderr

        if error:
            return f"Error: {error}"
        else:
            return f"Output: {output}"
    except subprocess.TimeoutExpired:
        return "Error: Script execution timed out after 30 seconds."
    except Exception as e:
        return f"Error: An unexpected error occurred - {str(e)}"
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)
