# Generic LLM provider abstract base class
from abc import ABC, abstractmethod
from typing import Generator

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