# Paraitus

Paraitus is a simple, instant access interface for interacting with LLMs. It supports all of the major LLM cloud provider APIs,
as well as local model frameworks with APIs that follow the OpenAI specification.

Paraitus is designed to give instant access to an simple interface for interacting with the LLM of your choice. The default launch keyboard shortcut (`control+alt+p`) launches the interface with everthing needed for a quick LLM interaction, and `escape` closes it. No separate programs, browser tabs, or complex interfaces to manage. Keyboard shortcuts enable efficient usage and seamless interaction with the OS clipboard to move data back and forth between Paraitus and other applications.

Paraitus is written in pure Python (using the built-in `tkinter` UI framework), and has minimal other dependencies.

## Installation

You can install this library by cloning the repo and using pip for a local install:

```bash
git clone https://github.com/dscripka/paraitus
pip install -e ./paraitus
```

You can configure different APIs in the `paraitus.yml` YAML configuration file, by default stored in the ~/.paraitus cache directory for the active user. Note that all credentials/keys are saved in plain text in this file, and users with with more strict or complex security requirements should follow the instructions in the [custom authentication](#custom-authentication) to extend Paraitus.

The default structure of the YAML configuration file is shown below, with an example entry for an LLM API:

```yaml
- name: Anthropic Claude 3 Haiku  # the name of the LLM API to display in Paraitus
  model_id: claude-3-haiku-20240307 # the specific model name/id offered by the API provider (e.g., gpt-35-turbo, mistral-medium, etc.)
  api_key: abc123  # the key for the API
  api_url: https://api.anthropic.com/v1/messages  # the URL for the API
  default: False  # whether this model and API should be the default
  api_type: Anthropic  # the type of the API, corresponding to either the built-in or custom API classes for the LLM provider
  authentication_class: MyCustomAuth  # a custom authentication class for the API (if not using standard API keys)
  streaming: True  # whether to stream the responses from the LLM provider API
```

Paraitus has built-in support for many different LLM providers, and can be easily extended to others. Supported values for the `api_type` parameter in the config file are `Anthropic, OpenAI, Mistral, Cohere`.

## Usage

### Launching Paraitus

Once installed and the config file created, you can launch Paraitus by simply issuing the `paraitus` command in your terminal or command prompt. Then, open an interface with `control+alt+p`.

Note! You may have to see where your current Python environment installs user-level binaries if `paraitus` isn't in your default system path.

There are a few other command-line launch options to configure Paraitus:

`paraitus --cache-dir /path/to/my/directory`: Sets the location of the Paraitus cache directory, instead of the default ~/.paraitus location.

### Using Paraitus

Once a window is launched, interact with Paraitus using the interface and keyboard shortcuts listed in the lower left corner of the window.

Type your prompts into the system prompt/user input text boxes, or use the system clipboard to copy/paste text. Pasting the path to a text file will automatically load and paste the contents of that file.

Estimates of tokens used (assuming 4 characters per token) is shown for each text input box.

Multiple Paraitus windows can be opened with the `control+alt+p` keyboard shortcut, and multiple results from separate prompts can stream to them all simultaneous. Pressing `escape` will close the selected window.

### Adding New APIs

You can easily add new LLM API providers to Paraitus by inheriting from the `Provider` base class:

```python
# Generic LLM provider base class (in paraitus/providers/provider.py)
from abc import ABC, abstractmethod

class Provider(ABC):
    def __init__(self, **kwargs):
        self.url = kwargs.get("url", "")
        self.key = kwargs.get("key", "")
        self.model = kwargs.get("model", "")

    @abstractmethod
    def generate_stream(self, **kwargs) -> Generator[str, None, None]:
        "A function that returns a generator, yielding text from the model"
        pass

    @abstractmethod
    def generate(self, **kwargs) -> str:
        "A function that returns text produced from the model all at once"
        pass
```

Your new class should be added to the `custom_providers.py` file in the cache directory, and it can be referenced by name in a new model entry inside the `paraitus.yml` config file using the `api_type` parameter. Your new model will then be loaded and authenticated when Paraitus launches.

## Custom Authentication

Sometimes certain Cloud provider APIs or internal enterprise APIs may require more complex authentication than a simple API key. In these cases, you can extend Paraitus to support these APIs by creating a custom authentication class that is called when initializing the API. For example, if you wanted to add support for an API that uses a dynamically produced bearer token to authenticate, you could create a custom authentication class definition like this:

```python
from pairaitus.authentication import BaseAuth

class MyCustomAuth(BaseAuth):
    def __init__(self, *args, **kwargs):
        # Do any setup here
        pass

    def get_access_token(self):
        # Get the auth token with your custom code here
        return "Bearer token"
```

This class should be added to the `custom_auth.py` file in the cache directory.

Then, in the `paraitus.yml` file, you can specify your custom authentication class for a given model API using the `authentication_class` parameter:

Now when this API is initialized, the `MyCustomAuth.get_access_token` method will be called to get the required access token.

## FAQ

#### Why don't you just use LM Studio, Big-AI, text-generation-webui, or any other existing LLM interfaces?

Paraitus isn't intended to replace much larger, more feature-rich interfaces. In fact, it only (currently) implements the day-to-day requirements that I observed in my usage of LLMs, leaving more expansive features sets to future development.

At a high-level, I wrote Paraitus to meet 3 specific goals:

1) Support both local model APIs *and* Cloud provider APIs, with easy extension to others.

2) Trivially easy to install and setup anywhere, on any platform.

3) Go from thinking about a way to use LLM for a given task to typing a prompt in <1 second. To use LLMs effectively in your day-to-day work you have to, well, [use them](https://twitter.com/emollick/status/1766303368211767601). I wanted to essentially eliminate any barriers and friction to using an LLM when the thought occurs to do so.

#### Why the name?

Paraitus is an (admittedly bad) portmanteau of the latin word "paratus" meaning "ready" or "prepared", and AI.

## Acknowledgements

Many thanks to @rdbende for the amazing [Sun Valley ttk theme](https://github.com/rdbende/Sun-Valley-ttk-theme) which significantly improves the visual quality of the `tkinter` interface.

## Generative AI Disclosure

This library was written with the assistance of Generative AI models.

## License

This code in this repository is licensed under the [MIT](https://choosealicense.com/licenses/mit/) license.