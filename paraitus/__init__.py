# Initialize the configuration file, and load model information

import sys
import os
import yaml
import importlib
import inspect

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

# Check if the custom provider class file exists
custom_provider_file = os.path.join(config_dir, "custom_providers.py")
if not os.path.exists(custom_provider_file):
    # Create a new custom provider class file
    with open(custom_provider_file, "w") as file:
        file.write("# Define custom provider classes for Paraitus here\n")

# Load custom authentication classes
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
    module = importlib.import_module("custom_auth")
    class_ref = getattr(module, class_name)

    return class_ref

# Load custom model classes
def load_custom_providers(config_dir):
    if os.path.exists(os.path.join(config_dir, "custom_providers.py")):
        sys.path.append(config_dir)
        import custom_providers
    else:
        raise ValueError(f"Custom authentication class file not found in {config_dir}!")

def get_provider_class(model_config):
    # Get the class name from the YAML file
    class_name = model_config['api_type']

    # Dynamically import the module containing the classes
    custom_module = importlib.import_module("custom_providers")
    custom_classes = [name for name, obj in inspect.getmembers(custom_module) if inspect.isclass(obj)]

    standard_module = importlib.import_module("paraitus.providers.standard_providers")
    standard_classes = [name for name, obj in inspect.getmembers(standard_module) if inspect.isclass(obj)]

    if class_name in custom_classes:
        class_ref = getattr(custom_module, class_name)
    elif class_name in standard_classes:
        class_ref = getattr(standard_module, class_name)

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

    # Load any custom providers
    load_custom_providers(config_dir)

    # Load built-in and custom model providers
    global MODELS
    for model in config:
        if model.get("authentication_class", None) is not None:
            auth_class = get_auth_class(model)()
            model["api_key"] = auth_class.get_access_token()

        model["provider"] = get_provider_class(model)(
            url=model["api_url"],
            key=model["api_key"],
            model_id=model["model_id"],
            streaming=model.get("streaming", False)
        )
        MODELS.append(model)
    
def get_model(model_name):
    for model in MODELS:
        if model["name"] == model_name:
            return model["provider"]
    raise ValueError(f"Model {model_name} not found in the configuration file.")