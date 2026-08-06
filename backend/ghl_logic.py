from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any, Mapping

try:
    from .quote_logic import clean_text, parse_positive_int, slug_text
except ImportError:
    from quote_logic import clean_text, parse_positive_int, slug_text


# Relaciono nuestra prioridad interna con la variable de entorno que tendra el stage real.
STAGE_ENV_BY_PRIORITY = {
    "high": "GHL_STAGE_HIGH",
    "medium": "GHL_STAGE_MEDIUM",
    "low": "GHL_STAGE_LOW",
}


# Estos nombres ayudan a entender el pipeline aunque todavia no tengamos IDs reales.
STAGE_NAME_BY_PRIORITY = {
    "high": "Contactar hoy",
    "medium": "Revisar y cotizar",
    "low": "Nutrir o asesorar",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def env_enabled(value: str | None) -> bool:
    return clean_text(value).lower() in {"1", "true", "yes", "si", "on"}


def mask_secret(value: str) -> str:
    value = clean_text(value)
    if not value:
        return ""
    if len(value) <= 6:
        return "***"
    return "***" + value[-4:]


def get_env(env: Mapping[str, str] | None = None) -> Mapping[str, str]:
    return env or os.environ


def crm_settings(env: Mapping[str, str] | None = None) -> dict[str, Any]:
    values = get_env(env)
    api_base = clean_text(values.get("GHL_API_BASE") or "https://services.leadconnectorhq.com").rstrip("/")
    enabled = env_enabled(values.get("GHL_ENABLED"))

    return {
        "enabled": enabled,
        "api_base": api_base,
        "location_id": clean_text(values.get("GHL_LOCATION_ID")),
        "private_token": clean_text(values.get("GHL_PRIVATE_TOKEN")),
        "pipeline_id": clean_text(values.get("GHL_PIPELINE_ID")),
        "assigned_user_id": clean_text(values.get("GHL_ASSIGNED_USER_ID")),
        "stage_ids": {
            "high": clean_text(values.get("GHL_STAGE_HIGH")),
            "medium": clean_text(values.get("GHL_STAGE_MEDIUM")),
            "low": clean_text(values.get("GHL_STAGE_LOW")),
        },
    }


def extract_lead(payload: dict[str, Any]) -> dict[str, Any]:
    lead = payload.get("lead")
    if isinstance(lead, dict):
        return lead
    if isinstance(payload, dict) and payload.get("id") and payload.get("quote_id"):
        return payload
    return {}


def validate_lead_for_crm(lead: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not lead.get("id"):
        errors.append("lead_id_required")
    if not lead.get("quote_id"):
        errors.append("quote_id_required")
    if not lead.get("full_name"):
        errors.append("full_name_required")
    if not lead.get("email") and not lead.get("phone"):
        errors.append("email_or_phone_required")
    return errors


def stage_for_lead(lead: dict[str, Any], settings: dict[str, Any]) -> dict[str, str]:
    priority = slug_text(lead.get("priority") or "low")
    env_name = STAGE_ENV_BY_PRIORITY.get(priority, "GHL_STAGE_LOW")
    stage_id = clean_text(settings["stage_ids"].get(priority))

    return {
        "priority": priority,
        "env_name": env_name,
        "stage_id": stage_id or f"<{env_name}>",
        "stage_name": STAGE_NAME_BY_PRIORITY.get(priority, "Nutrir o asesorar"),
    }


def missing_live_config(settings: dict[str, Any], stage: dict[str, str]) -> list[str]:
    missing = []
    if not settings["private_token"]:
        missing.append("GHL_PRIVATE_TOKEN")
    if not settings["location_id"]:
        missing.append("GHL_LOCATION_ID")
    if not settings["pipeline_id"]:
        missing.append("GHL_PIPELINE_ID")
    if stage["stage_id"].startswith("<"):
        missing.append(stage["env_name"])
    return missing


def request_headers(settings: dict[str, Any]) -> dict[str, str]:
    token = settings["private_token"]
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {mask_secret(token) if token else '<GHL_PRIVATE_TOKEN>'}",
        "Version": "v3",
    }


def build_contact_body(lead: dict[str, Any], settings: dict[str, Any]) -> dict[str, Any]:
    body = {
        "firstName": clean_text(lead.get("first_name")),
        "lastName": clean_text(lead.get("last_name")),
        "name": clean_text(lead.get("full_name")),
        "email": clean_text(lead.get("email")).lower(),
        "phone": clean_text(lead.get("phone")),
        "locationId": settings["location_id"] or "<GHL_LOCATION_ID>",
        "city": clean_text(lead.get("delivery_city")),
        "source": clean_text(lead.get("source") or "electropatios_web"),
        "companyName": clean_text(lead.get("company_name")),
        "tags": lead.get("tags") if isinstance(lead.get("tags"), list) else [],
        "createNewIfDuplicateAllowed": False,
        "customFields": [
            {"key": "electropatios_lead_id", "fieldValue": clean_text(lead.get("id"))},
            {"key": "electropatios_quote_id", "fieldValue": clean_text(lead.get("quote_id"))},
            {"key": "electropatios_productos", "fieldValue": clean_text(lead.get("products_summary"))},
            {"key": "electropatios_prioridad", "fieldValue": clean_text(lead.get("priority"))},
        ],
    }

    if settings["assigned_user_id"]:
        body["assignedTo"] = settings["assigned_user_id"]

    return body


def build_opportunity_body(lead: dict[str, Any], settings: dict[str, Any], stage: dict[str, str]) -> dict[str, Any]:
    return {
        "pipelineId": settings["pipeline_id"] or "<GHL_PIPELINE_ID>",
        "locationId": settings["location_id"] or "<GHL_LOCATION_ID>",
        "name": f"Cotizacion Electropatios - {clean_text(lead.get('full_name'))}",
        "pipelineStageId": stage["stage_id"],
        "status": "open",
        "contactId": "<CONTACT_ID_FROM_UPSERT>",
        "monetaryValue": parse_positive_int(lead.get("estimated_value_cop")),
        "source": clean_text(lead.get("source") or "electropatios_web"),
        "externalObjectId": clean_text(lead.get("id")),
        "customFields": [
            {"key": "electropatios_lead_id", "fieldValue": clean_text(lead.get("id"))},
            {"key": "electropatios_quote_id", "fieldValue": clean_text(lead.get("quote_id"))},
            {"key": "electropatios_productos", "fieldValue": clean_text(lead.get("products_summary"))},
        ],
    }


def build_crm_requests(lead: dict[str, Any], settings: dict[str, Any]) -> dict[str, Any]:
    stage = stage_for_lead(lead, settings)
    headers = request_headers(settings)

    return {
        "stage": stage,
        "contact_upsert": {
            "method": "POST",
            "url": f"{settings['api_base']}/contacts/upsert",
            "headers": headers,
            "body": build_contact_body(lead, settings),
        },
        "opportunity_create": {
            "method": "POST",
            "url": f"{settings['api_base']}/opportunities/",
            "headers": headers,
            "body": build_opportunity_body(lead, settings, stage),
        },
    }


def crm_status(settings: dict[str, Any], missing_config: list[str]) -> tuple[str, str, bool]:
    if not settings["enabled"]:
        return "safe_mode", "dry_run_prepared", False
    if missing_config:
        return "live_check", "blocked_missing_config", False
    return "live_check", "ready_for_live_sync", False


def build_crm_sync_record(
    payload: dict[str, Any],
    env: Mapping[str, str] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    lead = extract_lead(payload)
    errors = validate_lead_for_crm(lead)
    if errors:
        return {"lead": lead}, errors

    settings = crm_settings(env)
    requests = build_crm_requests(lead, settings)
    missing_config = missing_live_config(settings, requests["stage"])
    mode, status, will_send_to_crm = crm_status(settings, missing_config)

    sync = {
        "id": str(uuid.uuid4()),
        "provider": "gohighlevel",
        "mode": mode,
        "status": status,
        "will_send_to_crm": will_send_to_crm,
        "lead_id": clean_text(lead.get("id")),
        "quote_id": clean_text(lead.get("quote_id")),
        "full_name": clean_text(lead.get("full_name")),
        "priority": slug_text(lead.get("priority") or "low"),
        "pipeline_stage": clean_text(lead.get("pipeline_stage")),
        "duplicate_strategy": "contacts/upsert usa email o telefono para evitar duplicados",
        "missing_config": missing_config,
        "requests": requests,
        "next_step": "revisar en modo seguro antes de activar envios reales",
        "created_at": utc_now(),
    }

    return sync, []
