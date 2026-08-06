from __future__ import annotations

import hashlib
import re
import uuid
from datetime import datetime, timezone
from typing import Any


# Aqui guardo las categorias principales que vende Electropatios.
# Mas adelante esto puede salir de MySQL, Google Sheets o un inventario real.
PRODUCT_CATEGORIES = {
    "lamparas": [
        "Lamparas LED",
        "paneles LED",
        "reflectores",
        "bombillos",
        "apliques",
    ],
    "conectores": [
        "conectores electricos",
        "terminales",
        "regletas",
        "cajas de paso",
    ],
    "cable": [
        "cable THHN",
        "cable duplex",
        "cable encauchetado",
        "alambre de cobre",
    ],
    "tuberia": [
        "tuberia PVC",
        "tuberia EMT",
        "conduit",
        "accesorios para tuberia",
    ],
    "proteccion": [
        "breakers",
        "tableros",
        "tomacorrientes",
        "interruptores",
    ],
    "herramientas": [
        "cintas aislantes",
        "multimetros",
        "herramientas electricas",
    ],
    "otros": [
        "producto por confirmar",
    ],
}

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Mensajes amigables para mostrar en la pagina cuando algo falta.
ERROR_MESSAGES = {
    "full_name_required": "Escribe tu nombre completo.",
    "valid_email_required": "Escribe un email valido.",
    "valid_phone_required": "Escribe un telefono valido.",
    "product_category_required": "Selecciona una categoria de producto.",
    "quantity_required_for_quotes": "Escribe la cantidad que necesitas cotizar.",
    "consent_required": "Acepta ser contactado para poder responder la solicitud.",
}


# Limpia textos que llegan del formulario para guardar datos mas ordenados.
def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


# Convierte textos de formularios a valores faciles de comparar.
def slug_text(value: Any) -> str:
    return clean_text(value).lower().replace(" ", "_")


# Saca solo los numeros para cantidades y presupuestos.
def parse_positive_int(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return max(0, int(value))

    digits = re.sub(r"\D", "", str(value))
    if not digits:
        return 0
    return int(digits)


# Dejo esta funcion separada porque despues el presupuesto puede tener mas reglas.
def parse_budget(value: Any) -> int:
    return parse_positive_int(value)


# Normaliza el telefono para comparar y guardar siempre de forma parecida.
def normalize_phone(value: Any) -> str:
    raw = clean_text(value)
    if raw.startswith("+"):
        return "+" + re.sub(r"\D", "", raw[1:])
    return re.sub(r"\D", "", raw)


# Esta funcion arma una cotizacion limpia con los datos que llegan del formulario.
def normalize_quote(payload: dict[str, Any]) -> dict[str, Any]:
    product_category = slug_text(payload.get("product_category"))
    if product_category not in PRODUCT_CATEGORIES:
        product_category = "otros" if product_category else ""

    request_type = slug_text(payload.get("request_type") or "quote")
    urgency = slug_text(payload.get("urgency") or "this_week")

    return {
        "full_name": clean_text(payload.get("full_name") or payload.get("name")),
        "email": clean_text(payload.get("email")).lower(),
        "phone": normalize_phone(payload.get("phone")),
        "customer_type": slug_text(payload.get("customer_type") or "persona"),
        "company_name": clean_text(payload.get("company_name")),
        "request_type": request_type,
        "product_category": product_category,
        "quantity": parse_positive_int(payload.get("quantity")),
        "unit": slug_text(payload.get("unit") or "unidad"),
        "budget_cop": parse_budget(payload.get("budget_cop") or payload.get("budget")),
        "urgency": urgency,
        "delivery_city": clean_text(payload.get("delivery_city") or "Cucuta"),
        "source": clean_text(payload.get("source") or "electropatios_web"),
        "notes": clean_text(payload.get("notes") or payload.get("question")),
        "consent": bool(payload.get("consent")),
    }


# Valida lo minimo que necesito antes de guardar o automatizar la solicitud.
def validate_quote(quote: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not quote.get("full_name"):
        errors.append("full_name_required")
    if not EMAIL_PATTERN.match(quote.get("email", "")):
        errors.append("valid_email_required")
    if len(quote.get("phone", "")) < 7:
        errors.append("valid_phone_required")
    if not quote.get("product_category"):
        errors.append("product_category_required")
    if quote.get("request_type") == "quote" and quote.get("quantity", 0) <= 0:
        errors.append("quantity_required_for_quotes")
    if not quote.get("consent"):
        errors.append("consent_required")

    return errors


# Clasifica la solicitud para saber si debe atenderse rapido.
# Esto no reemplaza al asesor; solo ayuda a ordenar prioridades.
def classify_quote(quote: dict[str, Any]) -> dict[str, Any]:
    budget = int(quote.get("budget_cop") or 0)
    quantity = int(quote.get("quantity") or 0)
    urgency = quote.get("urgency", "")
    notes = quote.get("notes", "").lower()
    request_type = quote.get("request_type", "")
    customer_type = quote.get("customer_type", "")

    urgent_terms = {"hoy", "24h", "same_day", "urgente"}
    business_customer = customer_type in {
        "empresa",
        "ferreteria",
        "constructor",
        "constructora",
        "tecnico",
        "tecnico_electricista",
    }
    wants_fast_contact = urgency in urgent_terms or "urgente" in notes or "hoy" in notes
    is_quote = request_type == "quote"
    high_value = budget >= 2_000_000 or quantity >= 100
    medium_value = budget >= 500_000 or quantity >= 10

    if (is_quote and wants_fast_contact) or high_value or (business_customer and medium_value):
        return {
            "priority": "high",
            "score": 92,
            "status": "qualified",
            "reason": "Solicitud prioritaria por urgencia, volumen o tipo de cliente.",
        }

    if is_quote or medium_value or business_customer:
        return {
            "priority": "medium",
            "score": 68,
            "status": "pending_review",
            "reason": "Solicitud con potencial de venta; falta confirmar precio y disponibilidad.",
        }

    return {
        "priority": "low",
        "score": 40,
        "status": "new",
        "reason": "Consulta inicial que necesita asesoria o seguimiento.",
    }


# Crea una huella de la solicitud para detectar repetidos.
# Asi un cliente puede cotizar varias cosas sin que todo parezca duplicado.
def duplicate_key(quote: dict[str, Any]) -> str:
    raw_key = "|".join(
        [
            quote.get("email") or quote.get("phone", ""),
            quote.get("request_type", ""),
            quote.get("product_category", ""),
            str(quote.get("quantity", "")),
            quote.get("unit", ""),
            quote.get("delivery_city", "").lower(),
            quote.get("notes", "").lower()[:80],
        ]
    )
    return "quote:" + hashlib.sha1(raw_key.encode("utf-8")).hexdigest()


# Esta es la funcion principal: recibe datos crudos y devuelve una cotizacion lista.
def build_quote_record(payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    quote = normalize_quote(payload)
    errors = validate_quote(quote)
    if errors:
        return quote, errors

    classification = classify_quote(quote)
    quote.update(
        {
            "id": str(uuid.uuid4()),
            "duplicate_key": duplicate_key(quote),
            "priority": classification["priority"],
            "score": classification["score"],
            "status": classification["status"],
            "priority_reason": classification["reason"],
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        }
    )
    return quote, []
