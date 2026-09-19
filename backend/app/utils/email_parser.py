"""
Parser robusto de emails no padrão RFC822 / MIME (.eml / IMAP payloads) (#23).
Extrai remetente, destinatário, assunto, corpo em texto limpo e metadados de anexos.
"""
import email
from email import policy
import re
from typing import Dict, Any, List, Optional


def _strip_html_tags(html: str) -> str:
    """Remove tags HTML mantendo quebras de linha essenciais."""
    if not html:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_eml(eml_bytes_or_str: Any) -> Dict[str, Any]:
    """
    Decodifica um arquivo ou payload de email RFC822 (.eml).
    
    Args:
        eml_bytes_or_str: Bytes ou string com conteúdo MIME/RFC822.
        
    Returns:
        Dicionário estruturado com metadados e corpo do email.
    """
    if isinstance(eml_bytes_or_str, str):
        msg = email.message_from_string(eml_bytes_or_str, policy=policy.default)
    else:
        msg = email.message_from_bytes(eml_bytes_or_str, policy=policy.default)

    subject = msg.get("Subject", "(Sem Assunto)")
    from_addr = msg.get("From", "")
    to_addr = msg.get("To", "")
    date_str = msg.get("Date", "")
    message_id = msg.get("Message-ID", "")

    body_plain = ""
    body_html = ""
    attachments: List[Dict[str, Any]] = []

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))

            if "attachment" in disposition:
                filename = part.get_filename() or "anexo"
                payload = part.get_payload(decode=True) or b""
                attachments.append({
                    "filename": filename,
                    "content_type": content_type,
                    "size_bytes": len(payload),
                })
            elif content_type == "text/plain" and not body_plain:
                try:
                    body_plain = part.get_content()
                except Exception:
                    body_plain = str(part.get_payload(decode=True) or "")
            elif content_type == "text/html" and not body_html:
                try:
                    body_html = part.get_content()
                except Exception:
                    body_html = str(part.get_payload(decode=True) or "")
    else:
        content_type = msg.get_content_type()
        if content_type == "text/plain":
            body_plain = msg.get_content()
        elif content_type == "text/html":
            body_html = msg.get_content()

    # Consolidar texto final
    main_text = body_plain.strip()
    if not main_text and body_html:
        main_text = _strip_html_tags(body_html)

    # Formatar corpo contextual consolidado para a IA
    full_email_text = f"De: {from_addr}\nPara: {to_addr}\nAssunto: {subject}\nData: {date_str}\n\n{main_text}"

    return {
        "subject": subject,
        "from": from_addr,
        "to": to_addr,
        "date": date_str,
        "message_id": message_id,
        "body_plain": body_plain,
        "body_html": body_html,
        "attachments": attachments,
        "full_text": full_email_text,
    }
