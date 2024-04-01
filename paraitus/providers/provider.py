# Generic LLM provider parent class

class Provider():
    def __init__(self, url, key, authentication_method = "api_key"):
        self.url = url
        self.key = key
        self.authentication_method = authentication_method

    def generate():
        pass