# backend/agent/policy.py
from typing import Dict, Any

# Lista de palabras clave o patrones a bloquear.
# Esto debería ser expandido y gestionado en una configuración más robusta.
BLOCKED_KEYWORDS = [
    "ignore your previous instructions",
    "confidential",
    "malicious code",
    "delete files",
    "shutdown",
    "hack",
]

def validate_prompt(prompt: str) -> Dict[str, Any]:
    """
    Validates a user prompt against a set of security policies.

    Args:
        prompt (str): The user's input prompt.

    Returns:
        Dict[str, Any]: A dictionary containing the validation status
                        ("success" or "error") and a message.
    """
    prompt_lower = prompt.lower()

    for keyword in BLOCKED_KEYWORDS:
        if keyword in prompt_lower:
            return {
                "status": "error",
                "message": f"Prompt blocked due to security policy violation (contains: '{keyword}')."
            }

    # Aquí se podrían añadir más validaciones, como análisis de PII, etc.

    return {"status": "success", "message": "Prompt passed validation."}
