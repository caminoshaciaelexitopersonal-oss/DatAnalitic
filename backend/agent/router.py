# backend/agent/router.py
from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from backend.agent.manager import agent_manager
from backend.core.state_store import StateStore, get_state_store

router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
)

class ChatRequest(BaseModel):
    session_id: str
    message: str

@router.post("/chat")
async def chat_with_agent(
    request: ChatRequest = Body(...),
    state_store: StateStore = Depends(get_state_store)
) -> Dict[str, Any]:
    """
    Handles a chat message by invoking the agent manager.
    """
    try:
        # La lógica de contexto se puede refinar aquí o mover al manager.
        # Por ahora, mantenemos una construcción de prompt simple.
        df = state_store.load_dataframe(session_id=request.session_id)
        if df is None:
            df_context = "No dataset loaded."
        else:
            df_context = df.head().to_markdown()

        full_prompt = f"""
        Context:
        {df_context}

        Question: {request.message}
        """

        response = agent_manager.handle_request(full_prompt.strip())

        if response["status"] == "error":
            raise HTTPException(status_code=500, detail=response["output"])

        return {"output": response["output"]}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred in the agent router: {e}")
