from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/name')
def name_route():
    name = request.args.get('name', 'Unknown')
    return f'Hello, {name}!'

@app.route('/post-data', methods=['POST'])
def post_data():
    data = request.get_json()
    if not data:
        return {'error': 'No data found in request'}, 400
    print(f"Received data: {data}")
    return data