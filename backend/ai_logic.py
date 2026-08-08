from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

try:
    from .quote_logic import PRODUCT_CATEGORIES, clean_text, slug_text
except ImportError:
    from quote_logic import PRODUCT_CATEGORIES, clean_text, slug_text


# Estas palabras ayudan a entender que quiere el cliente sin usar IA externa todavia.
INTENT_KEYWORDS = {
    "quote": {"cotizar", "cotizacion", "precio", "valor", "cuanto", "comprar", "pedido"},
    "product_question": {"venden", "tienen", "manejan", "hay", "existe", "producto"},
    "technical_advice": {"instalar", "instalacion", "calibre", "breaker", "carga", "amperios", "conexion"},
    "availability": {"disponible", "stock", "inventario", "entrega", "domicilio", "hoy"},
}


# Guardrails: cosas que la IA no debe prometer ni inventar.
GUARDRAIL_KEYWORDS = {
    "price": {"precio", "valor", "cuanto", "barato", "cotizar", "cotizacion"},
    "stock": {"disponible", "stock", "inventario", "hay"},
    "delivery": {"entrega", "domicilio", "envio", "hoy", "manana", "urgente"},
    "electrical_safety": {"instalar", "instalacion", "calibre", "carga", "amperios", "norma", "conexion"},
}


SAFE_REPLIES = {
    "quote": (
        "Gracias. Recibimos tu solicitud de cotizacion para Electropatios. "
        "Un asesor revisara precio, disponibilidad y tiempo de entrega antes de confirmarte."
    ),
    "product_question": (
        "Gracias por escribir a Electropatios. Podemos ayudarte con lamparas, conectores, cable, "
        "tuberia, breakers y accesorios. Un asesor confirmara disponibilidad exacta."
    ),
    "technical_advice": (
        "Gracias. Para temas de instalacion o seleccion tecnica, un asesor debe revisar el caso "
        "antes de darte una recomendacion segura."
    ),
    "availability": (
        "Gracias. Un asesor de Electropatios confirmara disponibilidad y entrega antes de darte "
        "una respuesta final."
    ),
    "unknown": (
        "Gracias por contactar a Electropatios. Voy a dejar tu mensaje para que un asesor lo revise "
        "y te responda con informacion confirmada."
    ),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


# Saco el lead del JSON cuando n8n ya lo creo antes.
def extract_lead(payload: dict[str, Any]) -> dict[str, Any]:
    lead = payload.get("lead")
    if isinstance(lead, dict):
        return lead
    return {}


# Saco la cotizacion del JSON cuando quiero clasificar desde el pedido original.
def extract_quote(payload: dict[str, Any]) -> dict[str, Any]:
    quote = payload.get("quote")
    if isinstance(quote, dict):
        return quote
    return {}


# Junto todos los textos posibles para que la clasificacion tenga contexto.
def text_from_payload(payload: dict[str, Any]) -> str:
    lead = extract_lead(payload)
    quote = extract_quote(payload)
    parts = [
        clean_text(payload.get("message")),
        clean_text(payload.get("question")),
        clean_text(payload.get("notes")),
        clean_text(lead.get("notes")),
        clean_text(lead.get("products_summary")),
        clean_text(quote.get("notes")),
        clean_text(quote.get("product_category")),
    ]
    return " ".join(part for part in parts if part).lower()


# Busca palabras simples dentro del texto. Esta fase usa reglas, no modelo externo.
def words_found(text: str, words: set[str]) -> list[str]:
    return sorted(word for word in words if word in text)


# Decide si el cliente quiere cotizar, preguntar producto, disponibilidad o asesoria tecnica.
def detect_intent(text: str, quote: dict[str, Any], lead: dict[str, Any]) -> tuple[str, list[str]]:
    request_type = slug_text(quote.get("request_type") or "")
    if request_type == "quote" or lead.get("id"):
        return "quote", ["request_type_or_lead"]

    matches = {
        intent: words_found(text, words)
        for intent, words in INTENT_KEYWORDS.items()
    }
    detected = [(intent, found) for intent, found in matches.items() if found]
    if not detected:
        return "unknown", []

    # Si varias intenciones aparecen, priorizo la mas importante para negocio y seguridad.
    for intent in ["technical_advice", "quote", "availability", "product_question"]:
        for detected_intent, found in detected:
            if detected_intent == intent:
                return intent, found

    return detected[0]


# Intenta reconocer la categoria del producto usando catalogo y texto del cliente.
def detect_category(text: str, quote: dict[str, Any], lead: dict[str, Any]) -> tuple[str, list[str]]:
    known_category = slug_text(lead.get("product_category") or quote.get("product_category") or "")
    if known_category in PRODUCT_CATEGORIES and known_category != "otros":
        return known_category, ["product_category_field"]

    matches: dict[str, list[str]] = {}
    for category, labels in PRODUCT_CATEGORIES.items():
        search_words = {category, *[label.lower() for label in labels]}
        found = words_found(text, search_words)
        if found:
            matches[category] = found

    if not matches:
        return "otros", []

    category = max(matches, key=lambda item: len(matches[item]))
    return category, matches[category]


# Marca las cosas que el sistema no debe prometer sin revision humana.
def detect_guardrails(text: str, intent: str) -> list[str]:
    guardrails = []
    for guardrail, words in GUARDRAIL_KEYWORDS.items():
        if words_found(text, words):
            guardrails.append(f"no_confirmar_{guardrail}")

    if intent == "technical_advice" and "pasar_a_asesor_tecnico" not in guardrails:
        guardrails.append("pasar_a_asesor_tecnico")
    if not guardrails:
        guardrails.append("no_inventar_informacion")

    return guardrails


# La confianza me ayuda a decidir si puedo responder o si debo pasar a asesor.
def confidence_for(intent: str, category: str, intent_matches: list[str], category_matches: list[str]) -> str:
    if intent != "unknown" and category != "otros":
        return "high"
    if intent_matches or category_matches:
        return "medium"
    return "low"


# Decide cuando un humano debe revisar antes de responder al cliente.
def handoff_decision(intent: str, confidence: str, guardrails: list[str], lead: dict[str, Any]) -> tuple[bool, str]:
    if lead.get("priority") == "high":
        return True, "lead_prioritario"
    if confidence == "low":
        return True, "baja_confianza"
    if intent in {"quote", "technical_advice", "availability"}:
        return True, f"requiere_confirmacion_{intent}"
    if any(rule != "no_inventar_informacion" for rule in guardrails):
        return True, "guardrail_activo"
    return False, "respuesta_segura"


# Etiquetas que despues pueden viajar a CRM o usarse para reportes.
def suggested_tags(intent: str, category: str, handoff_required: bool) -> list[str]:
    tags = ["ai_safe_mode", f"ai_intent_{intent}", f"ai_category_{category}"]
    if handoff_required:
        tags.append("human_handoff")
    return tags


# Dejo preparado el prompt para cuando conecte una IA real.
def prompt_pack(text: str, category: str) -> dict[str, Any]:
    return {
        "system_prompt": (
            "Eres un asistente de Electropatios. Ayudas con productos electricos, "
            "pero no inventas precios, stock, entregas ni instrucciones peligrosas."
        ),
        "user_context": text[:500],
        "allowed_topics": [
            "lamparas",
            "conectores",
            "cable",
            "tuberia",
            "breakers",
            "tomacorrientes",
            "accesorios electricos",
        ],
        "detected_category": category,
        "rules": [
            "No inventar precios.",
            "No inventar disponibilidad.",
            "No prometer tiempos de entrega.",
            "No dar instrucciones electricas peligrosas.",
            "Pasar a asesor cuando falte informacion confirmada.",
        ],
    }


# Funcion principal: clasifica y prepara respuesta segura.
def build_ai_analysis(payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    lead = extract_lead(payload)
    quote = extract_quote(payload)
    text = text_from_payload(payload)
    errors: list[str] = []

    if not text:
        errors.append("message_required")

    intent, intent_matches = detect_intent(text, quote, lead)
    category, category_matches = detect_category(text, quote, lead)
    guardrails = detect_guardrails(text, intent)
    confidence = confidence_for(intent, category, intent_matches, category_matches)
    handoff_required, handoff_reason = handoff_decision(intent, confidence, guardrails, lead)
    safe_reply = SAFE_REPLIES.get(intent, SAFE_REPLIES["unknown"])

    analysis = {
        "id": str(uuid.uuid4()),
        "mode": "safe_mode",
        "status": "safe_reply_prepared",
        "will_call_ai_model": False,
        "lead_id": clean_text(lead.get("id")),
        "quote_id": clean_text(lead.get("quote_id") or quote.get("id")),
        "intent": intent,
        "intent_matches": intent_matches,
        "category": category,
        "category_matches": category_matches,
        "confidence": confidence,
        "guardrails": guardrails,
        "handoff_required": handoff_required,
        "handoff_reason": handoff_reason,
        "safe_reply": safe_reply,
        "suggested_tags": suggested_tags(intent, category, handoff_required),
        "prompt_pack": prompt_pack(text, category),
        "created_at": utc_now(),
    }

    return analysis, errors
