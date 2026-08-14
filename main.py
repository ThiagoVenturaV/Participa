import json
import time
import uvicorn
from fastapi import FastAPI, Request, Response, BackgroundTasks, Query, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse

try:
    from config import settings
    from whatsapp.parser import parse_whatsapp_payload
    from whatsapp.client import send_whatsapp_message
    from agent.graph import process_whatsapp_message
    from webhook_security import MAX_WEBHOOK_BYTES, verify_meta_signature
    app_module = "main:app"
except ImportError:
    from AgenteParticipa.config import settings
    from AgenteParticipa.whatsapp.parser import parse_whatsapp_payload
    from AgenteParticipa.whatsapp.client import send_whatsapp_message
    from AgenteParticipa.agent.graph import process_whatsapp_message
    from AgenteParticipa.webhook_security import MAX_WEBHOOK_BYTES, verify_meta_signature
    app_module = "AgenteParticipa.main:app"

app = FastAPI(
    title="WhatsApp LangGraph Agent API",
    description="API de Webhook para Agente Inteligente de WhatsApp usando LangGraph e FastAPI",
    version="1.0.0"
)

processed_message_ids: dict[str, float] = {}


def is_duplicate_message(message_id: str) -> bool:
    now = time.monotonic()
    cutoff = now - 24 * 60 * 60
    for stored_id, stored_at in list(processed_message_ids.items()):
        if stored_at < cutoff:
            processed_message_ids.pop(stored_id, None)
    if message_id in processed_message_ids:
        return True
    processed_message_ids[message_id] = now
    return False

async def handle_agent_response_task(sender_phone: str, sender_name: str, message_text: str):
    """
    Background Task: Processa a mensagem com o agente LangGraph e envia a resposta de volta ao WhatsApp.
    """
    try:
        print("[MSG] Processando mensagem autenticada do WhatsApp.")
        
        # Executa o agente LangGraph
        agent_reply = await process_whatsapp_message(sender_phone, sender_name, message_text)
        
        # Envia a resposta via API do WhatsApp
        await send_whatsapp_message(sender_phone, agent_reply)
    except Exception:
        print("[ERRO] Falha ao processar mensagem autenticada.")

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
        
        if mode == "subscribe" and token == settings.webhook_verify_token:
            return Response(content=str(challenge or ""), media_type="text/plain", status_code=200)
        return Response(content="Verification token mismatch", media_type="text/plain", status_code=403)
    except Exception:
        return Response(content="Webhook verification failed", media_type="text/plain", status_code=500)

@app.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint POST onde a Meta envia os eventos/mensagens do WhatsApp.
    """
    try:
        raw_body = await request.body()
        if len(raw_body) > MAX_WEBHOOK_BYTES:
            raise HTTPException(status_code=413, detail="Payload too large")
        if not verify_meta_signature(
            raw_body,
            request.headers.get("x-hub-signature-256"),
            settings.whatsapp_app_secret,
        ):
            raise HTTPException(status_code=403, detail="Invalid signature")
        payload = json.loads(raw_body)
        
        # Faz o parse da mensagem
        parsed_data = parse_whatsapp_payload(payload)
        
        if parsed_data:
            sender_phone, sender_name, message_text, message_id = parsed_data
            if is_duplicate_message(message_id):
                return JSONResponse(content={"status": "duplicate"}, status_code=200)
            
            # Adiciona o processamento do LangGraph como tarefa em segundo plano
            background_tasks.add_task(
                handle_agent_response_task,
                sender_phone=sender_phone,
                sender_name=sender_name,
                message_text=message_text
            )
        # Retorna 200 OK imediatamente para a Meta não reenviar a requisição
        return JSONResponse(content={"status": "received"}, status_code=200)
    except HTTPException:
        raise
    except (json.JSONDecodeError, TypeError, ValueError):
        return JSONResponse(content={"status": "invalid_payload"}, status_code=400)
    except Exception:
        return JSONResponse(content={"status": "error"}, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app_module, host=settings.host, port=settings.port, reload=False)
