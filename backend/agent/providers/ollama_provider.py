# backend/agent/providers/ollama_provider.py
import requests
import json
from typing import List, Dict, Any

OLLAMA_HOST = "http://localhost:11434" # Asume que Ollama corre localmente

def get_response(prompt: str, model: str = "llama2") -> Dict[str, Any]:
    """
    Gets a response from a local Ollama server.

    Args:
        prompt (str): The user's prompt.
        model (str): The name of the model to use in Ollama (e.g., 'llama2', 'mistral').

    Returns:
        Dict[str, Any]: A dictionary containing the status and the output.
    """
    try:
        url = f"{OLLAMA_HOST}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(url, data=json.dumps(payload))
        response.raise_for_status()

        response_json = response.json()
        return {"status": "success", "output": response_json.get("response")}

    except requests.exceptions.ConnectionError:
        return {"status": "error", "output": f"Could not connect to Ollama server at {OLLAMA_HOST}. Is it running?"}
    except Exception as e:
        return {"status": "error", "output": f"An error occurred with Ollama provider: {e}"}
