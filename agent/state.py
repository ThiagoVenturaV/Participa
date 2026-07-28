from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    Estado do Agente LangGraph.
    
    'messages': Lista de mensagens no histórico da conversa (com suporte a add_messages reducer).
    'sender_phone': Número do telefone do usuário do WhatsApp.
    'sender_name': Nome do usuário no WhatsApp (se disponível).
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    sender_phone: str
    sender_name: str
