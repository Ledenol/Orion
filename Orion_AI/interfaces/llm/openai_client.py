from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
class OpenAI_Client:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "nemotron-3-ultra-550b-a55b")

        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing in environment variables.")

        self.client = OpenAI(api_key=api_key, base_url="https://integrate.api.nvidia.com/v1")

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        json_mode: bool = False,
    ) -> str:

        kwargs = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "detailed thinking off"},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_completion_tokens": max_tokens,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)
        print("[FINISH REASON]", response.choices[0].finish_reason, "| USAGE:", response.usage)  # TEMP DEBUG
        return response.choices[0].message.content.strip()