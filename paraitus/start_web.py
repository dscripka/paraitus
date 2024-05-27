from flask import Flask, render_template, request, Response, jsonify
import json
import paraitus
from paraitus import utils
import argparse
import os
from pynput import mouse, keyboard

# Setup Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

def value_generator(data):
    for key, value in data.items():
        yield f"Key: {key}, Value: {value}\n"

# Main route to receive payload for LLM APIs
@app.route('/payload', methods=['POST'])
def payload():
    if request.is_json:
        data = request.get_json()

        # Select the model based on the model name
        model = paraitus.get_model(data["model"])

        # Create the stream generator
        stream = model.generate_stream(**data)

        return Response(stream, mimetype='text/plain')
    else:
        return jsonify({"error": "Request must be JSON"}), 400

# Route to get information on available models
@app.route('/models')
def models():
    # Get model information from the MODELS global variable
    return jsonify([i["name"] for i in paraitus.MODELS])

# Set up the OS-wide keyboard listener to open the window
def launch_window():
    os.system("firefox http://localhost:5000")

if __name__ == '__main__':
    # Parse command-line arguments for cache directory location (default is ~/.paraitus)
    parser = argparse.ArgumentParser(description="Paraitus: A simple LLM API interface.")
    parser.add_argument("--cache-dir", type=str, default=os.path.join(os.path.expanduser("~"), ".paraitus"),
                        help="Directory to store config files and custom authentication classes")

    parser = parser.parse_args()

    # Initialize paraitus configuration
    paraitus.load_config(parser.cache_dir)

    listener = keyboard.GlobalHotKeys({'<ctrl>+<alt>+p': launch_window})
    listener.start()

    # Start the webserver (debug mode breaks the pnyput listener)
    app.run(debug=False)