import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class GroqClient:
    """Client for interacting with the ultra-fast Groq Cloud API."""
    
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.model_name = model_name
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key or self.api_key == "paste_your_key_here":
            raise ValueError("[ERROR] GROQ_API_KEY is missing! Please paste your key into backend/.env")
            
        self.client = Groq(api_key=self.api_key)

    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Sends a prompt to the Groq API and returns the text response."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.1,  # Low temp for deterministic outputs
                max_tokens=1024,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"[ERROR] Groq API connection failed: {e}")
            raise e
