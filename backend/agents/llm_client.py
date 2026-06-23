import requests
import json
from typing import Optional

class OllamaClient:
    """Client for interacting with local Ollama models on the College GPU."""
    
    def __init__(self, model_name: str = "llama3.1", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Sends a prompt to the local LLM and returns the text response."""
        url = f"{self.base_url}/api/generate"
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
            
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.exceptions.RequestException as e:
            # Enforce real execution by raising the error if the AI isn't running
            print(f"[ERROR] Ollama connection failed. The AI Engine MUST be running.")
            raise e
