from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    from .quote_logic import clean_text, parse_positive_int, slug_text
except ImportError:
    from quote_logic import clean_text, parse_positive_int, slug_text


# Estados sencillos para explicar el lead como proceso comercial.
PIPELINE_BY_PRIORITY = {
    "high": "contactar_hoy",
    "medium": "revisar_y_cotizar",
    "low": "nutrir_o_asesorar",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


# Separo nombre y apellido porque GoHighLevel normalmente los pide por separado.
def split_name(full_name: str) -> tuple[str, str]:
    parts = clean_text(full_name).split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


# Resume el carrito en una sola linea para Sheets, CRM y mensajes al asesor.
def product_summary(items: list[dict[str, Any]]) -> str:
    if not items:
        return "Producto por confirmar"

    return "; ".join(
        f"{item.get('quantity', 0)} {item.get('unit', 'unidad')} - {item.get('name') or item.get('sku')}"
        for item in items
    )


# Calcula cuando deberia revisarse el lead segun la prioridad.
def follow_up_due_at(priority: str) -> str:
    now = utc_now()
    if priority == "high":
        return now.isoformat()
    if priority == "medium":
        return (now + timedelta(days=1)).isoformat()
    return (now + timedelta(days=3)).isoformat()


# Crea etiquetas utiles para filtrar leads despues en Sheets o CRM.
def lead_tags(quote: dict[str, Any]) -> list[str]:
    tags = [
        "electropatios",
        "cotizacion",
        f"prioridad_{quote.get('priority', 'low')}",
        f"categoria_{quote.get('product_category', 'otros')}",
    ]

    if quote.get("customer_type") != "persona":
        tags.append("cliente_negocio")
    if quote.get("urgency") in {"hoy", "24h", "same_day", "urgente"}:
        tags.append("urgente")

    return tags


# Esta huella evita duplicar el mismo lead si n8n repite una ejecucion.
def lead_duplicate_key(quote: dict[str, Any]) -> str:
    raw_key = quote.get("id") or "|".join(
        [
            quote.get("email", ""),
            quote.get("phone", ""),
            quote.get("product_category", ""),
            quote.get("created_at", ""),
        ]
    )
    return "lead:" + hashlib.sha1(str(raw_key).encode("utf-8")).hexdigest()


# Arma la fila como me gustaria verla en Google Sheets.
def build_sheet_row(lead: dict[str, Any]) -> dict[str, Any]:
    return {
        "fecha": lead["created_at"],
        "lead_id": lead["id"],
        "quote_id": lead["quote_id"],
        "nombre": lead["full_name"],
        "telefono": lead["phone"],
        "email": lead["email"],
        "ciudad": lead["delivery_city"],
        "productos": lead["products_summary"],
        "prioridad": lead["priority"],
        "etapa": lead["pipeline_stage"],
        "seguimiento": lead["follow_up_status"],
        "vencimiento": lead["task_due_at"],
        "notas": lead["notes"],
    }


# Prepara los datos con forma de CRM, aunque todavia no los envie reales.
def build_ghl_payloads(lead: dict[str, Any]) -> dict[str, Any]:
    return {
        "contact": {
            "firstName": lead["first_name"],
            "lastName": lead["last_name"],
            "name": lead["full_name"],
            "email": lead["email"],
            "phone": lead["phone"],
            "city": lead["delivery_city"],
            "source": lead["source"],
            "tags": lead["tags"],
        },
        "opportunity": {
            "name": f"Cotizacion Electropatios - {lead['full_name']}",
            "status": "open",
            "pipelineStage": lead["pipeline_stage"],
            "monetaryValue": lead["estimated_value_cop"],
            "source": lead["source"],
        },
    }


# Mensaje corto para que un asesor entienda rapido que debe hacer.
def build_advisor_message(lead: dict[str, Any]) -> str:
    return (
        f"Nuevo lead {lead['priority']} de Electropatios: {lead['full_name']} "
        f"({lead['phone']}). Productos: {lead['products_summary']}. "
        f"Ciudad: {lead['delivery_city']}. Etapa: {lead['pipeline_stage']}."
    )


# Acepto payload con {"quote": ...} o una cotizacion directa para facilitar pruebas.
def extract_quote(payload: dict[str, Any]) -> dict[str, Any]:
    quote = payload.get("quote")
    if isinstance(quote, dict):
        return quote
    if isinstance(payload, dict):
        return payload
    return {}


# Funcion principal de esta cajita: convierte cotizacion en lead.
def build_lead_record(payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    quote = extract_quote(payload)
    errors: list[str] = []

    if not quote.get("id"):
        errors.append("quote_id_required")
    if not quote.get("full_name"):
        errors.append("full_name_required")
    if not quote.get("email"):
        errors.append("email_required")
    if not quote.get("phone"):
        errors.append("phone_required")

    if errors:
        return {"quote": quote}, errors

    first_name, last_name = split_name(quote.get("full_name", ""))
    priority = slug_text(quote.get("priority") or "low")
    items = quote.get("items") if isinstance(quote.get("items"), list) else []
    created_at = utc_now().isoformat()

    lead = {
        "id": str(uuid.uuid4()),
        "duplicate_key": lead_duplicate_key(quote),
        "quote_id": quote["id"],
        "full_name": clean_text(quote.get("full_name")),
        "first_name": first_name,
        "last_name": last_name,
        "email": clean_text(quote.get("email")).lower(),
        "phone": clean_text(quote.get("phone")),
        "company_name": clean_text(quote.get("company_name")),
        "customer_type": slug_text(quote.get("customer_type") or "persona"),
        "delivery_city": clean_text(quote.get("delivery_city") or "Cucuta"),
        "product_category": slug_text(quote.get("product_category") or "otros"),
        "products_summary": product_summary(items),
        "quantity": parse_positive_int(quote.get("quantity")),
        "urgency": slug_text(quote.get("urgency") or "this_week"),
        "priority": priority,
        "lead_score": parse_positive_int(quote.get("score")),
        "pipeline_stage": PIPELINE_BY_PRIORITY.get(priority, "nutrir_o_asesorar"),
        "follow_up_status": "pendiente",
        "task_due_at": follow_up_due_at(priority),
        "estimated_value_cop": parse_positive_int(quote.get("budget_cop")),
        "source": clean_text(quote.get("source") or "electropatios_web"),
        "notes": clean_text(quote.get("notes")),
        "tags": lead_tags(quote),
        "created_at": created_at,
        "updated_at": created_at,
    }

    lead["sheet_row"] = build_sheet_row(lead)
    lead["ghl_payloads"] = build_ghl_payloads(lead)
    lead["advisor_message"] = build_advisor_message(lead)
    return lead, []


# Prepara una notificacion interna sin conectar WhatsApp ni email real.
def build_notification(payload: dict[str, Any]) -> dict[str, Any]:
    lead = payload.get("lead") if isinstance(payload.get("lead"), dict) else {}
    message = clean_text(payload.get("advisor_message") or lead.get("advisor_message"))

    return {
        "id": str(uuid.uuid4()),
        "lead_id": lead.get("id", ""),
        "quote_id": lead.get("quote_id", ""),
        "channel": clean_text(payload.get("channel") or "advisor_inbox"),
        "priority": slug_text(lead.get("priority") or payload.get("priority") or "medium"),
        "message": message,
        "status": "prepared",
        "created_at": utc_now().isoformat(),
    }
