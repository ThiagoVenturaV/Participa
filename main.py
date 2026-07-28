import uvicorn
from fastapi import FastAPI, Request, Response, BackgroundTasks, Query, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse

try:
    from config import settings
    from whatsapp.parser import parse_whatsapp_payload
    from whatsapp.client import send_whatsapp_message
    from agent.graph import process_whatsapp_message
    app_module = "main:app"
except ImportError:
    from AgenteParticipa.config import settings
    from AgenteParticipa.whatsapp.parser import parse_whatsapp_payload
    from AgenteParticipa.whatsapp.client import send_whatsapp_message
    from AgenteParticipa.agent.graph import process_whatsapp_message
    app_module = "AgenteParticipa.main:app"

app = FastAPI(
    title="WhatsApp LangGraph Agent API",
    description="API de Webhook para Agente Inteligente de WhatsApp usando LangGraph e FastAPI",
    version="1.0.0"
)

async def handle_agent_response_task(sender_phone: str, sender_name: str, message_text: str):
    """
    Background Task: Processa a mensagem com o agente LangGraph e envia a resposta de volta ao WhatsApp.
    """
    try:
        print(f"[MSG] Processando mensagem de [{sender_name} - {sender_phone}]: {message_text}")
        
        # Executa o agente LangGraph
        agent_reply = await process_whatsapp_message(sender_phone, sender_name, message_text)
        
        print(f"[AGENT] Resposta do Agente: {agent_reply}")
        
        # Envia a resposta via API do WhatsApp
        await send_whatsapp_message(sender_phone, agent_reply)
    except Exception as e:
        print(f"[ERRO] Erro ao processar task do agente: {e}")

@app.get("/")
def root():
    return {"status": "online", "message": "WhatsApp LangGraph Agent is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/webhook")
async def verify_webhook(
    request: Request,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """
    Endpoint de verificação de Webhook exigido pela Meta Cloud API.
    """
    try:
        mode = hub_mode or request.query_params.get("hub.mode")
        token = hub_verify_token or request.query_params.get("hub.verify_token")
        challenge = hub_challenge or request.query_params.get("hub.challenge")
        
        print(f"[WEBHOOK GET] Verificacao recebida: mode={mode}, token={token}, challenge={challenge}")
        
        if mode == "subscribe" and token == settings.webhook_verify_token:
            print("[OK] Webhook verificado com sucesso pelo Meta Cloud API!")
            return Response(content=str(challenge or ""), media_type="text/plain", status_code=200)
        
        print(f"[ERRO] Falha na verificacao do Webhook. Token recebido: '{token}', Esperado: '{settings.webhook_verify_token}'")
        return Response(content="Verification token mismatch", media_type="text/plain", status_code=403)
    except Exception as e:
        print(f"[ERRO EXCECAO] Erro na verificacao do webhook: {e}")
        return Response(content=str(e), media_type="text/plain", status_code=500)

@app.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint POST onde a Meta envia os eventos/mensagens do WhatsApp.
    """
    try:
        payload = await request.json()
        
        # Faz o parse da mensagem
        parsed_data = parse_whatsapp_payload(payload)
        
        if parsed_data:
            sender_phone, sender_name, message_text = parsed_data
            
            # Adiciona o processamento do LangGraph como tarefa em segundo plano
            background_tasks.add_task(
                handle_agent_response_task,
                sender_phone=sender_phone,
                sender_name=sender_name,
                message_text=message_text
            )
        
        # Retorna 200 OK imediatamente para a Meta não reenviar a requisição
        return JSONResponse(content={"status": "received"}, status_code=200)
    except Exception as e:
        print(f"[ERRO] Erro ao receber webhook: {e}")
        # Mesmo com erro de parse interno, responde 200 OK para evitar retentativas infinitas do WhatsApp
        return JSONResponse(content={"status": "error", "detail": str(e)}, status_code=200)

if __name__ == "__main__":
    uvicorn.run(app_module, host=settings.host, port=settings.port, reload=True)
