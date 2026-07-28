import datetime
from langchain_core.tools import tool

@tool
def get_current_time() -> str:
    """Retorna o horário e data atual formatados."""
    now = datetime.datetime.now()
    return now.strftime("%d/%m/%Y às %H:%M:%S")

@tool
def search_faq(query: str) -> str:
    """
    Busca informações frequentes na base de conhecimento ou FAQ.
    Use esta ferramenta para responder dúvidas comuns de usuários sobre serviços, horários, preços ou suporte.
    """
    query_lower = query.lower()
    
    faq_database = {
        "horario": "Nosso atendimento automático funciona 24/7. O suporte humano atende de segunda a sexta, das 08:00 às 18:00.",
        "preco": "Oferecemos diferentes planos adaptados para o seu negócio. Entre em contato com nossa equipe comercial para uma cotação personalizada.",
        "suporte": "Para suporte técnico avançado, você pode enviar um e-mail para suporte@empresa.com ou aguardar a transferência para um atendente.",
        "servicos": "Prestamos serviços de desenvolvimento de IA, automações no WhatsApp, integração de sistemas e consultoria tecnológica."
    }
    
    results = []
    for key, val in faq_database.items():
        if key in query_lower:
            results.append(f"- {val}")
            
    if results:
        return "\n".join(results)
    
    return "Não encontrei uma resposta exata no FAQ. Posso verificar com nossa equipe se desejar."

# Lista de todas as ferramentas disponíveis para o Agente
tools = [get_current_time, search_faq]
