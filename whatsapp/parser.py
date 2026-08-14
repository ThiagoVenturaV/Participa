from typing import Optional, Dict, Any, Tuple

def parse_whatsapp_payload(payload: Dict[str, Any]) -> Optional[Tuple[str, str, str, str]]:
    """
    Parse o payload recebido via webhook do WhatsApp (Meta Cloud API).
    
    Retorna uma tupla: (sender_phone, sender_name, message_text)
    Retorna None se o evento não for uma mensagem de texto recebida.
    """
    try:
        entry = payload.get("entry", [])
        if not entry:
            return None

        changes = entry[0].get("changes", [])
        if not changes:
            return None

        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        if not messages:
            # Podem ser notificações de status de envio/leitura
            return None

        message = messages[0]
        message_id = message.get("id", "")
        # Suporta apenas mensagens do tipo 'text' nesta versão simples
        msg_type = message.get("type")
        if msg_type != "text":
            # Caso o usuário envie áudio, imagem ou sticker
            sender_phone = message.get("from")
            contacts = value.get("contacts", [])
            sender_name = contacts[0].get("profile", {}).get("name", "Usuário") if contacts else "Usuário"
            if sender_phone and message_id:
                return sender_phone, sender_name, "[O usuário enviou uma mídia ou tipo de mensagem não suportado ainda]", message_id
            return None

        sender_phone = message.get("from")
        message_text = message.get("text", {}).get("body", "")

        contacts = value.get("contacts", [])
        sender_name = contacts[0].get("profile", {}).get("name", "Usuário") if contacts else "Usuário"

        if sender_phone and message_text and message_id:
            return sender_phone, sender_name, message_text[:4000], message_id

        return None
    except (AttributeError, IndexError, TypeError):
        return None
