from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

try:
    from .quote_logic import clean_text, slug_text
except ImportError:
    from quote_logic import clean_text, slug_text


# Eventos que me interesa medir en la pagina de Electropatios.
ALLOWED_EVENTS = {
    "page_view",
    "catalog_search",
    "category_filter",
    "product_add",
    "cart_open",
    "cart_clear",
    "quote_submit_attempt",
    "quote_submit_success",
    "quote_submit_error",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def clean_utm(value: Any) -> str:
    return slug_text(value).replace("-", "_")[:120]


def clean_metadata(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}

    metadata: dict[str, Any] = {}
    for key, item in value.items():
        clean_key = clean_text(key)[:80]
        if not clean_key:
            continue
        if isinstance(item, (str, int, float, bool)) or item is None:
            metadata[clean_key] = item
        else:
            metadata[clean_key] = clean_text(item)[:240]
    return metadata


def build_tracking_event(payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    event_name = slug_text(payload.get("event_name") or payload.get("event"))

    if not event_name:
        errors.append("event_name_required")
    elif event_name not in ALLOWED_EVENTS:
        errors.append("event_name_not_allowed")

    event = {
        "id": str(uuid.uuid4()),
        "mode": "local_tracking",
        "event_name": event_name or "unknown",
        "session_id": clean_text(payload.get("session_id"))[:120],
        "page_path": clean_text(payload.get("page_path") or payload.get("path"))[:240],
        "page_title": clean_text(payload.get("page_title") or payload.get("title"))[:180],
        "utm_source": clean_utm(payload.get("utm_source")),
        "utm_medium": clean_utm(payload.get("utm_medium")),
        "utm_campaign": clean_utm(payload.get("utm_campaign")),
        "utm_term": clean_utm(payload.get("utm_term")),
        "utm_content": clean_utm(payload.get("utm_content")),
        "referrer": clean_text(payload.get("referrer"))[:300],
        "user_agent": clean_text(payload.get("user_agent"))[:300],
        "metadata": clean_metadata(payload.get("metadata")),
        "created_at": utc_now(),
    }

    return event, errors
