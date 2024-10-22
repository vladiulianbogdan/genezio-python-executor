from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/name')
def name_route():
    name = request.args.get('name', 'Unknown')
    return f'Hello, {name}!'