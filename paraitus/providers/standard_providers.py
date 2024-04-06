# Support for the Anthropic API
# from paraitus.providers import Provider
import json
import requests
from paraitus.providers.provider import Provider
from typing import Generator

class Anthropic(Provider):
    def __init__(
        self,
        url: str,
        key: str,
        model_id: str,
        **kwargs
        ):
        super().__init__(**kwargs)

        # set attributes
        self.url = url
        self.key = key
        self.model = model_id
        self.headers = {
            "anthropic-version": "2023-06-01",
            "anthropic-beta": "messages-2023-12-15",
            "content-type": "application/json",
            "x-api-key": key
        }

    def generate(self, prompt: str, system_prompt: str="", **kwargs) -> Generator[str, None, None]:
        data = {
            "model": self.model,
            "system": system_prompt,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", 2048),
            "temperature": kwargs.get("temperature", 0.0),
            "stream": False
        }

        response = requests.post(self.url, headers=self.headers, json=data)
        return json.loads(response.text)["messages"][0]["content"]

    def generate_stream(self, prompt: str, system_prompt: str="", **kwargs) -> str:
        messages = []

        data = {
            "model": self.model,
            "system": system_prompt,
            "messages": messages + [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", 2048),
            "temperature": kwargs.get("temperature", 0.0),
            "stream": True
        }

        response = requests.post(self.url, headers=self.headers, json=data, stream=True)
        response_generator = self.get_response_text(response)
        for i in response_generator:
            yield i
    
    def get_response_text(self, stream: requests.models.Response) -> Generator[str, None, None]:
        for chunk in stream.iter_lines():
            data = chunk.decode("utf-8")
            if "data:" in data:
                chunk_json = json.loads(data[6:])
                event_type = chunk_json.get("type")
                if event_type == "content_block_delta":
                    delta = chunk_json["delta"]
                    yield delta["text"]
            else:
                yield ""
