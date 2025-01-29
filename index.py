from flask import Flask, request, jsonify
import json
import subprocess
import os
import sys
import base64
import urllib.parse
import sys


app = Flask(__name__)

def parse_event_body(request):
    """
    Parse the request body to extract code and dependencies.

    Args:
        request (Request): The Flask request object.

    Returns:
        tuple: Decoded code (str) and dependencies (list).
    """
    try:
        code = request.data.decode("utf-8")
        decoded_string = urllib.parse.unquote(request.args.get("dependencies", ""))
        if len(decoded_string) == 0:
            return code, []
        
        deps = decoded_string.split(",")
        print(f"Dependencies to install: {deps}")
        return code, deps
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in request body")
    except Exception as e:
        raise ValueError(f"Error parsing request body: {str(e)}")

def install_dependencies(dependencies):
    """
    Install the given dependencies to /tmp/deps.

    Args:
        dependencies (list): List of dependencies to install.
    """
    for dep in dependencies:
        print(f"Installing dependency: {dep} using {sys.executable}")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", dep, "--target", "/tmp/deps"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Error occurred while installing {dep}: {result.stderr}")
        else:
            print(f"Successfully installed {dep}.")

def write_temp_file(code, file_path):
    """
    Write the given code to a temporary file.

    Args:
        code (str): The code to write.
        file_path (str): The path of the temporary file.
    """
    with open(file_path, "w") as temp_file:
        temp_file.write(code)

def read_temp_file(file_path):
    """
    Read the contents of a temporary file.

    Args:
        file_path (str): The path of the temporary file.

    Returns:
        str: The contents of the file.
    """
    with open(file_path, "r") as temp_file:
        return temp_file.read()

def execute_code(file_path):
    """
    Execute the code in the temporary file and capture the output.

    Args:
        file_path (str): The path of the temporary file.

    Returns:
        tuple: Standard output, error output, and return code from the execution.
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = "/tmp/deps" + ":" + ":".join(sys.path)

    result = subprocess.run(
        [sys.executable, file_path],
        capture_output=True,
        text=True,
        env=env
    )
    print("Status code", result.returncode, "Stdout", result.stdout, "Stderr", result.stderr)
    return result.stdout, result.stderr, result.returncode

@app.route("/execute", methods=["POST"])
def execute():
    """
    Endpoint to execute Python code and return the output.

    Returns:
        Response: JSON response with execution results.
    """
    temp_file_path = "/tmp/temp_script.py"

    try:
        # Parse the request body
        decoded_code, dependencies = parse_event_body(request)

        print("Running:\n", decoded_code)
        if not decoded_code:
            return jsonify({"error": "No code provided in request body"}), 400

        # Install dependencies
        install_dependencies(dependencies)

        # Write the code to a temporary file
        write_temp_file(decoded_code, temp_file_path)

        # Execute the code and capture the output
        output, error, return_code = execute_code(temp_file_path)

        # Construct the response based on execution results
        if return_code != 0:
            return jsonify({"error": error or "Unknown error"}), 400

        return jsonify({"output": output}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Error executing code: {str(e)}"}), 500
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
