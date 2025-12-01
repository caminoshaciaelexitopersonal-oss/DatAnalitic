# backend/agent/providers/openai_provider.py
import os
from openai import OpenAI
from typing import List, Dict, Any

def get_response(prompt: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Gets a response from the OpenAI API.

    Args:
        prompt (List[Dict[str, str]]): A list of messages in the format
                                       expected by the OpenAI API,
                                       e.g., [{"role": "user", "content": "Hello"}].

    Returns:
        Dict[str, Any]: A dictionary containing the status and the output.
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {"status": "error", "output": "OPENAI_API_KEY not set."}

        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4",  # O el modelo que se desee configurar
            messages=prompt
        )

        output = response.choices[0].message.content
        return {"status": "success", "output": output}

    except Exception as e:
        return {"status": "error", "output": f"An error occurred with OpenAI provider: {e}"}
