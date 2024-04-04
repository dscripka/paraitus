# Paraitus

Paraitus is a simple, instant access interface for interacting with LLMs. It supports all of the major LLM cloud provider APIs,
as well as local model frameworks with APIs that follow the OpenAI specification.

Paraitus is designed to give instant access to an simple interface for interacting with the LLM of your choice. The default launch keyboard shortcut (`control+alt+p`) launches the interface with everthing needed for a quick LLM interaction, and `escape` closes it. No separate programs, browser tabs, or complex interfaces to manage. Keyboard shortcuts enable efficient usage and seamless interaction with the OS clipboard to move data back and forth between Paraitus and other applications.

Paraitus is written in pure Python (using the built-in `tkinter` UI framework), and has minimal other dependencies.

## Installation

You can install this library using pip:

```bash
pip install paraitus
```

You can configure different APIs in the paraitus.config YAML file, by default created in the ~/.paraitus cache directory for the active user.
Note that all credentials/keys are saved in plain text in this file, and users with with more strict or complex security requirements should follow the instructions in the [custom authentication](#custom-authentication) to extend Paraitus.

## Usage

Once installed, you can launch Paraitus by simply issuing the `paraitus` command in your terminal or command prompt. Then, open an interface with `control+alt+p`.

There are a few other command-line options to configure Paraitus:

`paraitus --cache-dir /path/to/my/directory`: Sets the location of the Paraitus cache directory, instead of the default ~/.paraitus location.

## Custom Authentication

Sometimes certain Cloud provider APIs or internal Enterprise APIs may require more complex authentication than a simple API key. In these cases, you can extend Paraitus to support these APIs by creating a custom authentication class that is called when initializing the API. For example, if you wanted to add support for an API that uses a dynamically produced bearer token to authenticate, you could create a custom authentication class definition like this:

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

This class should be added to `custom_auth.py` file in the cache directory.

Then, in the paraitus.config file, you can specify your custom authentication class for a given model API:

```yaml
- name: my_custom_llm_api
  api_key: None
  authentication_class: MyCustomAuth
```

Now when this API is intialized, the `MyCustomAuth.get_access_token` method will be called to get the required access token.

## FAQ

#### Why don't you just use LM Studio, Big-AI, text-generation-webui, or any other existing LLM interfaces?

Paraitus isn't intended to replace much larger, more feature-rich interfaces.

I wrote Paraitus to meet 3 specific goals:

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