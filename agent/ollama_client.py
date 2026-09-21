from ollama import Client

from config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)


class OllamaClient:
    def __init__(self):
        self.model = OLLAMA_MODEL

        self.client = Client(
            host=OLLAMA_BASE_URL
        )

    def health_check(self):
        """
        Verify that Ollama is reachable.
        """

        try:
            models = self.client.list()

            return {
                "healthy": True,
                "models": models,
            }

        except Exception as exc:
            return {
                "healthy": False,
                "error": str(exc),
            }

    def chat(self, messages):
        """
        Send messages to the configured Ollama model.
        """

        response = self.client.chat(
            model=self.model,
            messages=messages,
        )

        return response["message"]["content"]