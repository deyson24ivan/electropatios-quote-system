from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any

try:
    from .ai_logic import build_ai_analysis
    from .quote_logic import PRODUCT_CATEGORIES, clean_text, normalize_phone, parse_positive_int, slug_text
except ImportError:
    from ai_logic import build_ai_analysis
    from quote_logic import PRODUCT_CATEGORIES, clean_text, normalize_phone, parse_positive_int, slug_text


# Estas palabras me ayudan a saber si la llamada es venta, pregunta o tema tecnico.
VOICE_QUOTE_TERMS = {
    "cotizar",
    "cotizacion",
    "precio",
    "comprar",
    "pedido",
    "necesito",
    "quiero",
    "me vende",
    "me cotiza",
    "material",
}

VOICE_TECHNICAL_TERMS = {
    "instalar",
    "instalacion",
    "calibre",
    "carga",
    "amperios",
    "conexion",
    "norma",
    "breaker para",
}

VOICE_URGENCY_TERMS = {
    "hoy",
    "urgente",
    "ya",
    "24h",
    "lo antes",
    "esta manana",
    "manana",
    "rapido",
}

VOICE_AVAILABILITY_TERMS = {
    "disponible",
    "stock",
    "inventario",
    "entrega",
    "domicilio",
}

UNIT_ALIASES = {
    "m": "metro",
    "metro": "metro",
    "metros": "metro",
    "unidad": "unidad",
    "unidades": "unidad",
    "und": "unidad",
    "rollo": "rollo",
    "rollos": "rollo",
    "caja": "caja",
    "cajas": "caja",
    "tubo": "tubo",
    "tubos": "tubo",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


# Junto transcripcion y datos sueltos para analizar la llamada como un solo texto.
def text_from_payload(payload: dict[str, Any]) -> str:
    parts = [
        clean_text(payload.get("transcript")),
        clean_text(payload.get("message")),
        clean_text(payload.get("notes")),
        clean_text(payload.get("product_name")),
        clean_text(payload.get("product_category")),
    ]
    return " ".join(part for part in parts if part).lower()


# Reviso si alguna palabra clave aparece en la llamada.
def has_any_term(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


# Uso solo el primer nombre para que la respuesta telefonica suene natural.
def first_name(full_name: str) -> str:
    parts = clean_text(full_name).split()
    return parts[0] if parts else ""


# Convierte la categoria interna en una palabra entendible para el cliente.
def category_label(category: str) -> str:
    labels = PRODUCT_CATEGORIES.get(category) or PRODUCT_CATEGORIES["otros"]
    return labels[0].lower()


# Intenta leer cantidades como "120 metros" desde la transcripcion.
def extract_quantity_and_unit(payload: dict[str, Any], text: str) -> tuple[int, str]:
    quantity = parse_positive_int(payload.get("quantity"))
    unit = slug_text(payload.get("unit") or "")

    if quantity > 0:
        return quantity, unit or "unidad"

    match = re.search(
        r"\b(\d{1,5})\s*(metros?|m|unidades?|und|rollos?|cajas?|tubos?)\b",
        text,
    )
    if not match:
        return 0, unit or "unidad"

    raw_unit = match.group(2).lower()
    return int(match.group(1)), UNIT_ALIASES.get(raw_unit, raw_unit)


# Detecta urgencia usando el campo directo o palabras dichas por el cliente.
def detect_urgency(payload: dict[str, Any], text: str) -> str:
    payload_urgency = slug_text(payload.get("urgency") or "")
    if payload_urgency:
        return payload_urgency
    if "hoy" in text or "24h" in text or "urgente" in text or "ya" in text:
        return "hoy"
    if "manana" in text:
        return "manana"
    if has_any_term(text, VOICE_URGENCY_TERMS):
        return "pronto"
    return "esta_semana"


# Decide que tipo de llamada es: cotizacion, disponibilidad o consulta tecnica.
def detect_call_intent(text: str, ai_intent: str, category: str, quantity: int) -> str:
    if has_any_term(text, VOICE_TECHNICAL_TERMS):
        return "technical_advice"
    if has_any_term(text, VOICE_QUOTE_TERMS) or (category != "otros" and quantity > 0):
        return "quote"
    if has_any_term(text, VOICE_AVAILABILITY_TERMS):
        return "availability"
    if ai_intent and ai_intent != "unknown":
        return ai_intent
    return "unknown"


# La prioridad ayuda a decidir si el asesor debe llamar de una vez.
def priority_for_call(intent: str, urgency: str, quantity: int, text: str) -> str:
    if intent == "technical_advice":
        return "high"
    if urgency in {"hoy", "24h", "urgente", "pronto"}:
        return "high"
    if quantity >= 100 or "empresa" in text or "obra" in text or "constructor" in text:
        return "high"
    if intent in {"quote", "availability", "product_question"}:
        return "medium"
    return "low"


# La confianza sube cuando tengo producto, cantidad, nombre y telefono.
def confidence_for_call(intent: str, category: str, quantity: int, caller_name: str, phone: str) -> str:
    if intent != "unknown" and category != "otros" and quantity > 0 and caller_name and phone:
        return "high"
    if intent != "unknown" and (category != "otros" or quantity > 0):
        return "medium"
    return "low"


# Preguntas que el agente deberia hacer si faltan datos importantes.
def missing_questions(call: dict[str, Any]) -> list[str]:
    questions = []
    if not call["caller_name"]:
        questions.append("nombre completo")
    if not call["phone"]:
        questions.append("telefono de contacto")
    if call["product_category"] == "otros":
        questions.append("producto exacto")
    if call["intent"] == "quote" and call["quantity"] <= 0:
        questions.append("cantidad que necesita")
    if not call["delivery_city"]:
        questions.append("ciudad de entrega")
    return questions


# Convierte una lista de preguntas en texto corto para una llamada.
def format_questions(questions: list[str]) -> str:
    if not questions:
        return ""
    if len(questions) == 1:
        return questions[0]
    return ", ".join(questions[:-1]) + " y " + questions[-1]


# Respuesta segura: no confirma precio, stock ni instrucciones tecnicas.
def safe_voice_reply(call: dict[str, Any]) -> str:
    name = first_name(call["caller_name"])
    greeting = f"Claro, {name}." if name else "Claro."
    product = category_label(call["product_category"])
    questions = call["next_questions"]

    if call["intent"] == "technical_advice":
        return (
            f"{greeting} Para hacerlo bien y seguro, voy a pasar tu consulta a un asesor "
            "de Electropatios. El asesor revisa los datos antes de confirmar instalacion, "
            "calibre o conexion."
        )

    if call["intent"] == "quote":
        if questions:
            return (
                f"{greeting} Te ayudo a dejar la cotizacion de {product} registrada. "
                f"Para completarla necesito confirmar {format_questions(questions)}."
            )
        return (
            f"{greeting} Dejo registrada tu solicitud de {product}. Un asesor de "
            "Electropatios confirma precio, disponibilidad y entrega antes de cerrar la cotizacion."
        )

    if call["intent"] == "availability":
        return (
            f"{greeting} Un asesor de Electropatios confirma disponibilidad y tiempo de entrega "
            "antes de darte una respuesta final."
        )

    if call["intent"] == "product_question":
        return (
            f"{greeting} En Electropatios te podemos ayudar con productos electricos. "
            "Voy a dejar la consulta registrada para que un asesor confirme el producto exacto."
        )

    return (
        f"{greeting} Voy a dejar tu llamada registrada para que un asesor de Electropatios "
        "revise el caso y te responda con informacion confirmada."
    )


# Decide si la llamada debe pasar a asesor humano.
def handoff_for_call(call: dict[str, Any], ai_handoff: bool) -> tuple[bool, str]:
    if call["intent"] == "technical_advice":
        return True, "consulta_tecnica"
    if call["priority"] == "high":
        return True, "llamada_prioritaria"
    if call["intent"] in {"quote", "availability"}:
        return True, "requiere_confirmacion_comercial"
    if call["confidence"] == "low":
        return True, "faltan_datos"
    if ai_handoff:
        return True, "guardrail_ia"
    return False, "respuesta_segura"


# Resumen para que el asesor entienda la llamada sin leer todo.
def build_advisor_brief(call: dict[str, Any]) -> str:
    return (
        f"Llamada {call['priority']} de Electropatios: {call['caller_name'] or 'cliente por confirmar'} "
        f"({call['phone'] or 'telefono por confirmar'}). Intencion: {call['intent']}. "
        f"Producto: {call['product_category']}. Cantidad: {call['quantity']} {call['unit']}. "
        f"Urgencia: {call['urgency']}. Resumen: {call['transcript'][:240]}"
    )


# Borrador de lead si despues quiero convertir la llamada en seguimiento comercial.
def build_voice_lead_draft(call: dict[str, Any]) -> dict[str, Any]:
    return {
        "full_name": call["caller_name"],
        "phone": call["phone"],
        "email": call["email"],
        "product_category": call["product_category"],
        "quantity": call["quantity"],
        "unit": call["unit"],
        "urgency": call["urgency"],
        "delivery_city": call["delivery_city"],
        "priority": call["priority"],
        "source": "voice_ai_safe_mode",
        "notes": call["transcript"],
        "next_questions": call["next_questions"],
    }


# Funcion principal: recibe una transcripcion y prepara respuesta telefonica segura.
def build_voice_call_record(payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    text = text_from_payload(payload)
    errors: list[str] = []

    if not text:
        errors.append("transcript_required")

    ai_analysis, _ = build_ai_analysis({"message": text})
    category = slug_text(payload.get("product_category") or ai_analysis.get("category") or "otros")
    if category not in PRODUCT_CATEGORIES:
        category = "otros"

    quantity, unit = extract_quantity_and_unit(payload, text)
    caller_name = clean_text(payload.get("caller_name") or payload.get("full_name") or payload.get("name"))
    phone = normalize_phone(payload.get("phone") or payload.get("caller_phone"))
    delivery_city = clean_text(payload.get("delivery_city") or payload.get("city"))
    intent = detect_call_intent(text, ai_analysis.get("intent", "unknown"), category, quantity)
    urgency = detect_urgency(payload, text)
    priority = priority_for_call(intent, urgency, quantity, text)
    confidence = confidence_for_call(intent, category, quantity, caller_name, phone)

    call = {
        "id": str(uuid.uuid4()),
        "mode": "safe_mode",
        "status": "voice_reply_prepared",
        "provider": "local_simulator",
        "will_call_voice_provider": False,
        "will_call_ai_model": False,
        "caller_name": caller_name,
        "phone": phone,
        "email": clean_text(payload.get("email")).lower(),
        "delivery_city": delivery_city,
        "transcript": clean_text(payload.get("transcript") or payload.get("message") or payload.get("notes")),
        "intent": intent,
        "product_category": category,
        "quantity": quantity,
        "unit": unit,
        "urgency": urgency,
        "priority": priority,
        "confidence": confidence,
        "guardrails": ai_analysis.get("guardrails", ["no_inventar_informacion"]),
        "created_at": utc_now(),
    }
    call["next_questions"] = missing_questions(call)
    call["safe_voice_reply"] = safe_voice_reply(call)
    handoff_required, handoff_reason = handoff_for_call(call, bool(ai_analysis.get("handoff_required")))
    call["handoff_required"] = handoff_required
    call["handoff_reason"] = handoff_reason
    call["voice_lead_draft"] = build_voice_lead_draft(call)
    call["advisor_brief"] = build_advisor_brief(call)

    return call, errors
