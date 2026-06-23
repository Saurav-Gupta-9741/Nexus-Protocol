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
            # Fallback for local laptop testing (when Ollama isn't running)
            print(f"[Warning] Could not connect to Ollama at {self.base_url}. Is it running?")
            return self._fallback_mock_response(prompt)
            
    def _fallback_mock_response(self, prompt: str) -> str:
        """Used strictly for testing on your laptop before moving to the College GPU."""
        if "NXP" in prompt or "packet" in prompt:
            return "[NX:MSG|FROM:A|TO:B|ACT:GEN_REPORT|CTX:revenue|VAL:4.2M]"
        return "Based on my analysis, the total revenue is $4.2M. I have generated the financial summary report."
