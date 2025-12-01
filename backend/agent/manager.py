# backend/agent/manager.py
from typing import Dict, Any, List
from backend.agent.providers import openai_provider, gemini_provider, ollama_provider
from backend.agent import policy

class AgentManager:
    """
    The brain of the AI agent. It orchestrates the entire process from
    receiving a prompt to returning a final response.
    """
    def __init__(self, config: Dict[str, Any] = None):
        # La configuración podría definir el proveedor por defecto, fallbacks, etc.
        self.config = config or {"default_provider": "openai"}

    def handle_request(self, prompt: str) -> Dict[str, Any]:
        """
        Handles an incoming user request.

        1. Validates the prompt using the policy engine.
        2. Selects a provider based on configuration.
        3. Calls the provider to get a response.
        4. Handles fallbacks if the primary provider fails.
        5. Returns the final response.

        Args:
            prompt (str): The user's prompt.

        Returns:
            Dict[str, Any]: The agent's response.
        """
        # 1. Validar el prompt
        validation = policy.validate_prompt(prompt)
        if validation["status"] == "error":
            return validation

        # 2. Seleccionar el proveedor
        provider_name = self.config.get("default_provider", "openai")

        response = None
        if provider_name == "openai":
            # Adapt prompt format for OpenAI (list of dicts)
            openai_prompt = [{"role": "user", "content": prompt}]
            response = openai_provider.get_response(openai_prompt)
        elif provider_name == "gemini":
            response = gemini_provider.get_response(prompt)
        elif provider_name == "ollama":
            response = ollama_provider.get_response(prompt)

        # 3. Manejar fallback
        if response and response["status"] == "error":
            print(f"Primary provider '{provider_name}' failed. Error: {response['output']}. Attempting fallback...")
            # Simple fallback a Gemini si OpenAI falla
            if provider_name == "openai":
                response = gemini_provider.get_response(prompt)

        return response or {"status": "error", "output": "All providers failed to generate a response."}

# Singleton instance of the manager
agent_manager = AgentManager()
