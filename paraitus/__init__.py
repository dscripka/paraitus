# Initialize the configuration file, and load model information

import sys
import os
from pathlib import Path
import yaml
from paraitus.providers.anthropic import AnthropicProvider

# Set library attributes
MODELS = []

# Get the user's home directory
home_dir = os.path.expanduser("~")

# Define the path to the configuration file
config_dir = os.path.join(home_dir, ".paraitus")
config_file = os.path.join(config_dir, "paraitus.yml")

# Check if the configuration directory exists
if not os.path.exists(config_dir):
    # Create the configuration directory
    os.makedirs(config_dir)

# Check if the configuration file exists
if not os.path.exists(config_file):
    # Create a new configuration YAML file
    with open(config_file, "w") as file:
        default_config = [{
                "name": "Anthropic Claude 3 Haiku",
                "api_key": "",
                "api_url": "",
                "custom_authentication_class": "AnthropicAuth"
            }
        ]
        yaml.dump(default_config, file)

# Check if the custom authentication class file exists
custom_auth_file = os.path.join(config_dir, "custom_auth.py")
if not os.path.exists(custom_auth_file):
    # Create a new custom authentication class file
    with open(custom_auth_file, "w") as file:
        file.write("# Define custom authentication classes for Paraitus here\n")

# Load custom authentication classes from the configuration file
def load_auth_classes(config_dir):
    if os.path.exists(os.path.join(config_dir, "custom_auth.py")):
        sys.path.append(config_dir)
        import custom_auth
    else:
        raise ValueError(f"Custom authentication class file not found in {config_dir}!")

def get_auth_class(model_config):
    # Get the class name from the YAML file
    class_name = model_config['authentication_class']

    # Dynamically import the module containing the class
    module = __import__("custom_auth", fromlist=[class_name])
    class_ref = getattr(module, class_name)

    return class_ref

# Load models and provider types from the configuration file
def load_config(config_dir):
    # Load config
    if os.path.exists(os.path.join(config_dir, "paraitus.yml")):
        with open(os.path.join(config_dir, "paraitus.yml"), "r") as file:
            config = yaml.safe_load(file)
    else:
        raise ValueError(f"Configuration file for Paraitus not found in {config_dir}!"
                         " If you are using the --cache-dir argument, make sure the directory provided is correct.")

    # Load any custom authentication classes
    load_auth_classes(config_dir)

    # Load models
    global MODELS
    for model in config:
        if model.get("authentication_class", None) is not None:
            auth_class = get_auth_class(model)()
            model["api_key"] = auth_class.get_access_token()

        if model["api_type"] == "Anthropic":
            model["provider"] = AnthropicProvider(
                url=model["api_url"],
                key=model["api_key"],
                model_id=model["model_id"]
            )
        MODELS.append(model)
