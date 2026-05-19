import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class OpenAIClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-4.1")

        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing in environment variables.")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "developer", "content": "You are Orion, a helpful research assistant."},
                {"role": "user", "content": prompt},
            ],
        )

        return response.choices[0].message.content.strip()