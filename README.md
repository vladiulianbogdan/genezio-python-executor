# Genezio LLM Python Evaluator

Python-Eval is a Flask-based web service designed to enable remote execution of Python code, making it especially valuable for LLM tooling. It provides an API endpoint to execute Python code snippets and return their output, offering a seamless way for LLMs to interact with the external world. By deploying Python-Eval to Genezio, you can achieve a scalable and secure runtime evaluator, ensuring efficient and controlled execution of dynamically generated code.

## Features

- Remote Python code execution
- Dynamic dependency installation
- Secure execution environment
- JSON-based API

# Deploy
:rocket: You can deploy your own version of the template to Genezio with one click:

[![Deploy to Genezio](https://raw.githubusercontent.com/Genez-io/graphics/main/svg/deploy-button.svg)](https://app.genez.io/start/deploy?repository=https://github.com/vladiulianbogdan/python-eval)

## How It Works

The service exposes a single endpoint `/execute` that accepts POST requests. The Python code to be executed is sent in the request body, and any required dependencies can be specified as query parameters.

1. The service parses the incoming request, extracting the code and dependencies.
2. If dependencies are specified, they are installed in a temporary directory.
3. The code is written to a temporary file.
4. The code is executed in a controlled environment with access to the installed dependencies.
5. The output (or any errors) from the execution is captured and returned as a JSON response.

## API Usage

### Endpoint

```
POST /execute
```

### Request

- Body: Raw Python code to be executed
- Query Parameter: `dependencies` (optional) - Comma-separated list of Python packages to install before execution

### Response

The API returns a JSON response with the following structure:

- Success (200 OK):
  ```json
  {
    "output": "Output from the executed code"
  }
  ```

- Error (400 Bad Request or 500 Internal Server Error):
  ```json
  {
    "error": "Error message describing what went wrong"
  }
  ```

This README provides an overview of the Python-Eval project, explains its main features, how it works, API usage, security considerations, deployment notes, limitations, and a disclaimer. It should give users a clear understanding of what the project does and how to use it.
