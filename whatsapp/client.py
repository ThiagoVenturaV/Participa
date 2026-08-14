import httpx
try:
    from config import settings
except ImportError:
    from AgenteParticipa.config import settings

async def send_whatsapp_message(to_phone: str, message_text: str) -> bool:
    """
    Envia uma mensagem de texto de resposta para o usuário no WhatsApp via Meta Cloud API.
    """
    if not settings.whatsapp_token or not settings.whatsapp_phone_number_id:
        print("[AVISO] Credenciais do WhatsApp não configuradas; envio recusado.")
        return False

    url = f"https://graph.facebook.com/{settings.whatsapp_api_version}/{settings.whatsapp_phone_number_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message_text
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=10.0)
            
            if response.status_code == 200:
                print("[OK] Mensagem enviada com sucesso.")
                return True
            else:
                print(f"[ERRO] WhatsApp recusou o envio com status {response.status_code}.")
                return False
    except httpx.HTTPError:
        print("[ERRO] Falha de rede ao enviar mensagem ao WhatsApp.")
        return False
