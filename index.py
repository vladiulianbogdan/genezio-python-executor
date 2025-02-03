from flask import Flask, request, jsonify
import os
import sys
import subprocess
import shutil
import urllib.parse

app = Flask(__name__)

UPLOAD_DIR = "/tmp/code_exec"

def parse_dependencies(request):
    """
    Parse dependencies from the request.
    """
    try:
        decoded_string = urllib.parse.unquote(request.args.get("dependencies", ""))
        if len(decoded_string) == 0:
            return []
        deps = decoded_string.split(",")
        print(f"Dependencies to install: {deps}")
        return deps
    except Exception as e:
        raise ValueError(f"Error parsing dependencies: {str(e)}")

def install_dependencies(dependencies):
    """
    Install dependencies to a temporary directory.
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

def execute_main():
    """
    Execute the main.py script inside the upload directory.
    """
    main_script_path = os.path.join(UPLOAD_DIR, "main.py")

    if not os.path.exists(main_script_path):
        return {"error": "main.py not found. Please upload a valid main.py file."}, 400

    env = os.environ.copy()
    env["PYTHONPATH"] = "/tmp/deps" + ":" + ":".join(sys.path)
    
    result = subprocess.run(
        [sys.executable, main_script_path],
        capture_output=True,
        text=True,
        env=env,
        cwd=UPLOAD_DIR  # Ensure scripts run inside the upload directory
    )
    
    print("Execution result:", result.stdout, result.stderr)
    
    if result.returncode != 0:
        return {"error": result.stderr or "Unknown execution error"}, 400

    return {"output": result.stdout}, 200

@app.route("/execute", methods=["POST"])
def execute():
    """
    Endpoint to execute main.py from uploaded files.
    """
    try:
        # Ensure the upload directory exists
        if os.path.exists(UPLOAD_DIR):
            shutil.rmtree(UPLOAD_DIR)  # Clean previous files
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Parse dependencies
        dependencies = parse_dependencies(request)
        install_dependencies(dependencies)

        # Save uploaded files
        if "files" not in request.files:
            return jsonify({"error": "No files provided"}), 400

        for file in request.files.getlist("files"):
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            file.save(file_path)

        # Execute main.py
        response, status_code = execute_main()
        return jsonify(response), status_code

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Error executing code: {str(e)}"}), 500
    finally:
        shutil.rmtree(UPLOAD_DIR, ignore_errors=True)  # Cleanup after execution

