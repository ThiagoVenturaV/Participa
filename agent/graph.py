import hashlib
import os
from typing import Literal
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

try:
    from config import settings
    from agent.state import AgentState
    from agent.tools import tools
except ImportError:
    from AgenteParticipa.config import settings
    from AgenteParticipa.agent.state import AgentState
    from AgenteParticipa.agent.tools import tools

# 1. Configuração do Modelo LLM
def get_llm():
    provider = settings.llm_provider.lower().strip()
    
    if provider == "groq":
        groq_key = settings.groq_api_key or os.getenv("GROQ_API_KEY") or ""
        model_name = (settings.llm_model or "openai/gpt-oss-120b").strip()
        return ChatOpenAI(
            model=model_name,
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1",
            temperature=0.7
        )
    elif provider == "gemini":
        gemini_key = settings.google_api_key or os.getenv("GOOGLE_API_KEY") or ""
        return ChatGoogleGenerativeAI(
            model=settings.llm_model if "gemini" in settings.llm_model else "gemini-1.5-flash",
            google_api_key=gemini_key,
            temperature=0.7
        )
    else:
        openai_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY") or ""
        return ChatOpenAI(
            model=settings.llm_model if "gpt" in settings.llm_model else "gpt-4o-mini",
            api_key=openai_key,
            temperature=0.7
        )

# Instancia o LLM de forma dinâmica no momento da chamada para refletir alterações no .env
def get_llm_with_tools():
    llm = get_llm()
    return llm.bind_tools(tools)

# 2. Instruções do Sistema para o Agente WhatsApp
SYSTEM_PROMPT = """Você é um assistente virtual atencioso, eficiente e amigável no WhatsApp.

Diretrizes de resposta:
- Mantenha respostas concisas, claras e diretas ao ponto (adequadas para leitura no WhatsApp).
- Utilize marcações de texto do WhatsApp quando apropriado: *negrito* para destaque, _itálico_ para detalhes, e listas com marcadores.
- Use emojis com moderação para manter uma conversa amigável.
- Se precisar consultar informações ou horários, use as ferramentas disponíveis.
- Sempre responda no mesmo idioma do usuário (padrão: Português do Brasil).
"""

# 3. Nó do Modelo (Reasoning Node)
def call_model(state: AgentState):
    messages = state["messages"]
    
    # Se a primeira mensagem não for de sistema, injeta o prompt do sistema
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    
    llm_with_tools = get_llm_with_tools()
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# 4. Construção do Grafo LangGraph
workflow = StateGraph(AgentState)

# Adiciona Nós
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

# Adiciona Arestas (Edges)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

# Memória Persistente em Memória (MemorySaver) por thread_id
checkpointer = MemorySaver()
app_graph = workflow.compile(checkpointer=checkpointer)

# 5. Função Utilitária para Executar o Agente
async def process_whatsapp_message(sender_phone: str, sender_name: str, message_text: str) -> str:
    """
    Executa o grafo do LangGraph para um determinado usuário do WhatsApp.
    O número de telefone é usado como thread_id único para manter a memória.
    """
    thread_id = hashlib.sha256(sender_phone.encode("utf-8")).hexdigest()
    config = {"configurable": {"thread_id": thread_id}}
    
    input_state = {
        "messages": [HumanMessage(content=message_text)],
        "sender_phone": sender_phone,
        "sender_name": sender_name
    }
    
    # Executa o grafo assincronamente
    final_state = await app_graph.ainvoke(input_state, config=config)
    
    # Pega a última mensagem gerada pelo agente
    last_message = final_state["messages"][-1]
    return last_message.content
