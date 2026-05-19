import os
from urllib import response
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class GroqClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

        if not api_key:
            raise ValueError("GROQ_API_KEY is missing in environment variables.")

        self.client = Groq(api_key=api_key)

    def generate(self, prompt: str, temperature: float = 0.7, json_mode: bool = False) -> str:
        kwargs = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
    
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content.strip()