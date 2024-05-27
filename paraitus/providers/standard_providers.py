# Base API providers for Paraitus

import json
import requests
from paraitus.providers.provider import Provider
from typing import Generator

# Anthropic API provider

class Anthropic(Provider):
    def __init__(
        self,
        url: str,
        key: str,
        model_id: str,
        streaming: bool = False,
        **kwargs
        ):
        super().__init__(**kwargs)

        # set attributes
        self.url = url
        self.key = key
        self.model = model_id
        self.streaming = streaming
        self.headers = {
            "anthropic-version": "2023-06-01",
            "anthropic-beta": "messages-2023-12-15",
            "content-type": "application/json",
            "x-api-key": key
        }

    def generate(self, **kwargs) -> Generator[str, None, None]:
        # Check for a system prompt
        messages = kwargs.get("messages")
        if messages is None:
            raise ValueError("No messages provided for model input! Input arguments must be OpenAI API spec compliant.")
        system_message = [i for i in messages if i["role"] == "system"]
        system_prompt = system_message[0]["content"] if len(system_message) > 0 else ""

        # Build payload
        data = {
            "model": self.model,
            "system": system_prompt,
            "messages": [i for i in messages if i["role"] != "system"],
            "max_tokens": kwargs.get("max_tokens", 2048),
            "temperature": kwargs.get("temperature", 0.0),
            "top_p": kwargs.get("top_p", 1.0),
            "stream": False
        }

        response = requests.post(self.url, headers=self.headers, json=data)
        return response.json()["content"][0]['text']

    def generate_stream(self, **kwargs) -> str:
        # Check for a system prompt
        messages = kwargs.get("messages")
        if messages is None:
            raise ValueError("No messages provided for model input! Input arguments must be OpenAI API spec compliant.")
        system_message = [i for i in messages if i["role"] == "system"]
        system_prompt = system_message[0]["content"] if len(system_message) > 0 else ""

        data = {
            "model": self.model,
            "system": system_prompt,
            "messages": [i for i in messages if i["role"] != "system"],
            "max_tokens": kwargs.get("max_tokens", 2048),
            "temperature": kwargs.get("temperature", 0.0),
            "top_p": kwargs.get("top_p", 1.0),
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


# OpenAI Provider
class OpenAI(Provider):
    def __init__(
        self,
        url: str,
        key: str,
        model_id: str,
        streaming: bool = False,
        **kwargs
        ):
        super().__init__(**kwargs)

        # set attributes
        self.url = url
        self.key = key
        self.model = model_id
        self.streaming = streaming
        self.headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        self.base_url = url

    def generate(self, prompt: str, **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 2048),
            "temperature": kwargs.get("temperature", 0.0),
            "top_p": kwargs.get("top_p", 1.0)
        }

        response = requests.post(self.base_url, headers=self.headers, json=data)
        return response.json()["choices"][0]["message"]["content"]

    def generate_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        messages = [{"role": "user", "content": prompt}]
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 2048),
            "temperature": kwargs.get("temperature", 0.0),
            "top_p": kwargs.get("top_p", 1.0),
            "stream": True
        }

        response = requests.post(self.base_url, headers=self.headers, json=data, stream=True)
        return self.get_response_text(response)

    def get_response_text(self, stream: requests.models.Response) -> Generator[str, None, None]:
        for chunk in stream.iter_lines():
            if chunk:
                raw_chunk = chunk.decode("utf-8")
                if raw_chunk != "data: [DONE]":
                    data = json.loads(raw_chunk[6:])
                    if "choices" in data and len(data["choices"]) > 0:
                        message = data["choices"][0]["delta"]
                        content = message.get("content", None)
                        if message.get("role", None) != "system" and content is not None:
                            yield content
                    else:
                        yield ""
