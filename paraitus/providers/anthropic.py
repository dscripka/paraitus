# Support for the Anthropic API
# from paraitus.providers import Provider
import json
import requests

class AnthropicProvider():
    def __init__(
        self,
        url = "https://api.anthropic.com/v1/messages",
        key = "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",
        model_id = "claude-3-haiku-20240307",
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

    def generate(self, prompt, system_prompt="", stream=True, **kwargs):
        messages = []

        data = {
            "model": self.model,
            "system": system_prompt,
            "messages": messages + [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", 2048),
            "temperature": kwargs.get("temperature", 0.0),
            "stream": stream
        }

        response = requests.post(self.url, headers=self.headers, json=data, stream=True)
        response_generator = self.get_response_text(response)
        for i in response_generator:
            yield i
    
    def get_response_text(self, stream):
        response_text = ""
        content_block = None
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
