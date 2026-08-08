from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any

try:
    from .quote_logic import EMAIL_PATTERN, clean_text, parse_positive_int, slug_text
except ImportError:
    from quote_logic import EMAIL_PATTERN, clean_text, parse_positive_int, slug_text


# Aqui dejo los proveedores que podria usar Electropatios para mandar correos.
# Los valores reales de DKIM siempre salen del panel de cada proveedor.
PROVIDER_PRESETS = {
    "google_workspace": {
        "label": "Google Workspace",
        "spf_include": "include:_spf.google.com",
        "dkim_selector": "google",
    },
    "sendgrid": {
        "label": "SendGrid",
        "spf_include": "include:sendgrid.net",
        "dkim_selector": "s1",
    },
    "mailgun": {
        "label": "Mailgun",
        "spf_include": "include:mailgun.org",
        "dkim_selector": "smtp",
    },
    "gohighlevel": {
        "label": "GoHighLevel",
        "spf_include": "",
        "dkim_selector": "provider",
    },
    "custom_smtp": {
        "label": "Proveedor SMTP por confirmar",
        "spf_include": "",
        "dkim_selector": "provider",
    },
}

DOMAIN_PATTERN = re.compile(r"^(?!-)([a-z0-9-]{1,63}\.)+[a-z]{2,63}$")
DEFAULT_PROVIDERS = ["google_workspace", "gohighlevel"]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


# Limpio el dominio para comparar siempre en minusculas y sin punto final.
def clean_domain(value: Any) -> str:
    return clean_text(value).lower().strip(".")


# Valido formato basico de dominio antes de preparar registros DNS.
def valid_domain(value: str) -> bool:
    if not value:
        return False
    if "://" in value or "/" in value or "@" in value or "_" in value:
        return False
    return bool(DOMAIN_PATTERN.match(value))


# Acepto proveedores como lista o texto separado por comas.
def normalize_providers(value: Any) -> list[str]:
    if isinstance(value, str):
        raw_providers = [item for item in value.split(",")]
    elif isinstance(value, list):
        raw_providers = value
    else:
        raw_providers = DEFAULT_PROVIDERS

    providers: list[str] = []
    for item in raw_providers:
        provider = slug_text(item)
        if provider and provider not in providers:
            providers.append(provider)

    return providers or DEFAULT_PROVIDERS


# Nombre bonito del proveedor para advertencias y explicaciones.
def provider_label(provider: str) -> str:
    preset = PROVIDER_PRESETS.get(provider)
    if preset:
        return preset["label"]
    return clean_text(provider).replace("_", " ").title()


# Arma el SPF con los includes que conozco y marca lo que debo revisar manualmente.
def build_spf_value(providers: list[str]) -> tuple[str, list[str]]:
    includes = []
    missing = []

    for provider in providers:
        preset = PROVIDER_PRESETS.get(provider, {})
        include_value = clean_text(preset.get("spf_include"))
        if include_value:
            includes.append(include_value)
        else:
            missing.append(provider)

    if includes:
        return f"v=spf1 {' '.join(includes)} ~all", missing

    return "pendiente: copiar el SPF exacto del proveedor", missing


# DMARC empieza suave con p=none para mirar reportes antes de bloquear.
def dmarc_value(report_email: str) -> str:
    return f"v=DMARC1; p=none; rua=mailto:{report_email}; fo=1"


# Registro SPF: quien puede enviar correo por el dominio.
def build_spf_record(domain: str, providers: list[str]) -> tuple[dict[str, Any], list[str]]:
    value, missing = build_spf_value(providers)
    status = "provider_required" if value.startswith("pendiente") else "review_before_publish"

    return (
        {
            "type": "TXT",
            "host": "@",
            "name": domain,
            "purpose": "spf",
            "value": value,
            "status": status,
            "explanation": "Autoriza que proveedores pueden enviar correos usando el dominio de Electropatios.",
        },
        missing,
    )


# Registros DKIM: siempre dependen de la clave que entregue cada proveedor real.
def build_dkim_records(domain: str, providers: list[str]) -> list[dict[str, Any]]:
    records = []

    for provider in providers:
        preset = PROVIDER_PRESETS.get(provider, {})
        selector = clean_text(preset.get("dkim_selector") or "provider")
        host = f"{selector}._domainkey" if selector != "provider" else "<selector>._domainkey"

        records.append(
            {
                "type": "TXT",
                "host": host,
                "name": f"{host}.{domain}",
                "purpose": "dkim",
                "provider": provider,
                "value": f"copiar_valor_dkim_de_{provider}",
                "status": "provider_required",
                "explanation": "Firma los correos para demostrar que no fueron cambiados en el camino.",
            }
        )

    return records


# Registro DMARC: como se revisan SPF/DKIM y a donde llegan reportes.
def build_dmarc_record(domain: str, report_email: str) -> dict[str, Any]:
    return {
        "type": "TXT",
        "host": "_dmarc",
        "name": f"_dmarc.{domain}",
        "purpose": "dmarc",
        "value": dmarc_value(report_email),
        "status": "safe_start",
        "explanation": "Empieza en p=none para mirar reportes antes de bloquear correos.",
    }


# Advertencias para no publicar DNS mal durante una prueba.
def build_warnings(providers: list[str], spf_missing: list[str]) -> list[str]:
    warnings = [
        "No publicar dos registros SPF separados; si hay varios proveedores, se unen en un solo TXT.",
        "El valor DKIM no se inventa; se copia desde el panel real del proveedor de correo.",
        "DMARC empieza en p=none para monitorear antes de pasar a quarantine o reject.",
    ]

    for provider in spf_missing:
        warnings.append(
            f"Confirmar en {provider_label(provider)} si necesita agregar algo mas al SPF antes de publicar."
        )

    if "gohighlevel" in providers:
        warnings.append(
            "Para GoHighLevel hay que copiar los registros exactos desde la subcuenta real antes de activar envios."
        )

    return warnings


# Pasos que seguiria cuando tenga dominio y proveedor reales.
def build_next_steps(domain: str) -> list[str]:
    return [
        f"Entrar al panel DNS del dominio {domain}.",
        "Crear o actualizar un solo registro SPF TXT.",
        "Copiar los registros DKIM exactos desde el proveedor de correo o CRM.",
        "Publicar DMARC con p=none y revisar reportes antes de hacerlo mas estricto.",
        "Enviar un correo de prueba y revisar que SPF, DKIM y DMARC pasen.",
        "Mantener listas limpias, bajas quejas de spam y enlace de baja en correos promocionales.",
    ]


# Funcion principal: prepara el plan sin tocar DNS reales.
def build_email_dns_plan(payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    domain = clean_domain(payload.get("domain") or payload.get("sending_domain"))
    mail_from_domain = clean_domain(payload.get("mail_from_domain"))
    if not mail_from_domain and domain:
        mail_from_domain = f"mail.{domain}"
    report_email = clean_text(payload.get("report_email") or f"dmarc@{domain}").lower()
    providers = normalize_providers(payload.get("providers"))
    daily_volume = parse_positive_int(payload.get("daily_volume") or payload.get("volume_per_day"))

    errors: list[str] = []
    if not valid_domain(domain):
        errors.append("valid_domain_required")
    if mail_from_domain and not valid_domain(mail_from_domain):
        errors.append("valid_mail_from_domain_required")
    if report_email and not EMAIL_PATTERN.match(report_email):
        errors.append("valid_report_email_required")

    if errors:
        return {
            "domain": domain,
            "mail_from_domain": mail_from_domain,
            "providers": providers,
        }, errors

    spf_record, spf_missing = build_spf_record(domain, providers)
    records = [
        spf_record,
        *build_dkim_records(domain, providers),
        build_dmarc_record(domain, report_email),
    ]
    bulk_sender = daily_volume >= 5000

    plan = {
        "id": str(uuid.uuid4()),
        "mode": "safe_mode",
        "status": "dns_plan_prepared",
        "will_change_dns": False,
        "domain": domain,
        "mail_from_domain": mail_from_domain,
        "report_email": report_email,
        "providers": providers,
        "daily_volume": daily_volume,
        "records": records,
        "checks": {
            "spf_record_count_expected": 1,
            "dkim_needs_provider_key": True,
            "dmarc_policy": "none",
            "bulk_sender": bulk_sender,
            "one_click_unsubscribe_required": bulk_sender,
            "spam_rate_goal": "mantener debajo de 0.3%",
            "will_change_dns": False,
        },
        "warnings": build_warnings(providers, spf_missing),
        "next_steps": build_next_steps(domain),
        "created_at": utc_now(),
    }

    return plan, []
