from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from app.core.chat_store import (
    create_conversation,
    delete_conversation,
    get_messages,
    list_conversations,
    save_message,
)
from app.core.config import settings
from app.core.database import conversation_exists
from app.llm.ollama_provider import OllamaProvider, OllamaProviderError


router = APIRouter(prefix="/api", tags=["chat"])
provider = OllamaProvider(
    base_url=settings.ollama_base_url,
    model=settings.ollama_model,
)


class ContextData(BaseModel):
    application: str | None = None
    window_title: str | None = None
    editor: str | None = None
    filename: str | None = None
    language: str | None = None
    selected_text: str | None = None
    file_path: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(..., description="Mensagem do usuário")
    conversation_id: str | None = None
    context: ContextData | None = None

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("A mensagem não pode ficar vazia.")
        return value


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    context_used: dict | None = None


def build_context_prompt(context: ContextData | None) -> str:
    """Monta um prompt com informações do contexto do usuário."""
    if not context:
        return ""
    
    parts = []
    
    if context.editor and context.editor != "Desconhecido":
        parts.append(f"Editor/IDE: {context.editor}")
    
    if context.filename and context.filename != "Sem arquivo":
        parts.append(f"Arquivo: {context.filename}")
    
    if context.language and context.language != "unknown":
        parts.append(f"Linguagem: {context.language}")
    
    if context.window_title:
        parts.append(f"Contexto: {context.window_title}")
    
    if context.selected_text:
        parts.append(f"Texto selecionado:\n```\n{context.selected_text}\n```")
    
    if parts:
        return "Contexto do usuário:\n" + "\n".join(parts) + "\n"
    
    return ""


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "agent-mentor"}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    conversation_id = request.conversation_id
    if conversation_id and not conversation_exists(conversation_id):
        raise HTTPException(status_code=404, detail="Conversa não encontrada.")

    if not conversation_id:
        conversation_id = create_conversation()

    save_message(conversation_id, "user", request.message)

    history = get_messages(conversation_id, limit=12)
    history_text = "\n".join(
        f"{item['role']}: {item['content']}" for item in history
    )

    context_text = build_context_prompt(request.context)

    prompt = (
        "Você é o Agent Mentor, um assistente útil para programação. "
        "Responda em português do Brasil, salvo se o usuário pedir outro idioma. "
        "Seja preciso, conciso e útil.\n\n"
        f"{context_text}"
        f"Histórico:\n{history_text}\n\nAssistente:"
    )

    try:
        response = await provider.generate(prompt)
    except OllamaProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    save_message(conversation_id, "assistant", response)
    
    return ChatResponse(
        response=response,
        conversation_id=conversation_id,
        context_used=request.context.model_dump() if request.context else None,
    )


@router.get("/conversations")
async def conversations() -> list[dict]:
    return list_conversations()


@router.get("/conversations/{conversation_id}/messages")
async def conversation_messages(
    conversation_id: str,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> list[dict]:
    if not conversation_exists(conversation_id):
        raise HTTPException(status_code=404, detail="Conversa não encontrada.")
    return get_messages(conversation_id, limit=limit)


@router.delete("/conversations/{conversation_id}")
async def remove_conversation(conversation_id: str) -> dict:
    if not delete_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversa não encontrada.")
    return {"deleted": True, "conversation_id": conversation_id}
