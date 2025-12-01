# backend/agent/providers/gemini_provider.py
import os
import google.generativeai as genai
from typing import List, Dict, Any

def get_response(prompt: str) -> Dict[str, Any]:
    """
    Gets a response from the Google Gemini API.

    Args:
        prompt (str): The user's prompt as a single string.

    Returns:
        Dict[str, Any]: A dictionary containing the status and the output.
    """
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {"status": "error", "output": "GOOGLE_API_KEY not set."}

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)

        return {"status": "success", "output": response.text}

    except Exception as e:
        return {"status": "error", "output": f"An error occurred with Gemini provider: {e}"}
