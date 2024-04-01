# Initialize the configuration file, and load model information

import sys
import os
from pathlib import Path
import yaml
from paraitus.providers.anthropic import AnthropicProvider

if sys.platform == "win32":
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

if sys.platform == "darwin":
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
                    "custom_authentication_class": "AnthropicAuth"
                }
            ]
            yaml.dump(default_config, file)

if sys.platform == "linux":
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
                    "custom_authentication_class": "AnthropicAuth"
                }
            ]
            yaml.dump(default_config, file)

# Load models and provider types from the configuration file
MODELS = []
with open(config_file, "r") as file:
    models = yaml.safe_load(file)
    for model in models:
        if model["api_type"] == "Anthropic":
            model["provider"] = AnthropicProvider(
                url=model["api_url"],
                key=model["api_key"],
                model_id=model["model_id"]
            )
        MODELS.append(model)
