from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request

try:
    from .ai_logic import build_ai_analysis
    from .ghl_logic import build_crm_sync_record
    from .lead_logic import build_lead_record, build_notification
    from .quote_logic import ERROR_MESSAGES, PRODUCT_CATEGORIES, build_quote_record
    from .tracking_logic import build_tracking_event
    from .voice_logic import build_voice_call_record
except ImportError:
    from ai_logic import build_ai_analysis
    from ghl_logic import build_crm_sync_record
    from lead_logic import build_lead_record, build_notification
    from quote_logic import ERROR_MESSAGES, PRODUCT_CATEGORIES, build_quote_record
    from tracking_logic import build_tracking_event
    from voice_logic import build_voice_call_record


# Rutas principales del proyecto. Todo lo que se guarda localmente queda en backend/data.
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
QUOTES_FILE = DATA_DIR / "quotes.jsonl"
LEADS_FILE = DATA_DIR / "leads.jsonl"
NOTIFICATIONS_FILE = DATA_DIR / "notifications.jsonl"
CRM_SYNCS_FILE = DATA_DIR / "crm_syncs.jsonl"
AI_ANALYSES_FILE = DATA_DIR / "ai_analyses.jsonl"
VOICE_CALLS_FILE = DATA_DIR / "voice_calls.jsonl"
TRACKING_EVENTS_FILE = DATA_DIR / "tracking_events.jsonl"
ERRORS_FILE = DATA_DIR / "automation_errors.jsonl"

app = Flask(__name__)


# Permite que la pagina HTML local pueda llamar a la API sin bloquearse por CORS.
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response


# Revisa si hay datos suficientes para intentar guardar en MySQL.
def mysql_configured() -> bool:
    return all(
        os.getenv(name)
        for name in [
            "MYSQL_HOST",
            "MYSQL_USER",
            "MYSQL_DATABASE",
        ]
    )


# Abre conexion con MySQL solo cuando haga falta.
def mysql_connection():
    import mysql.connector

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "electropatios_automation"),
    )


# Guarda una linea JSON en un archivo local. Esto sirve como respaldo simple.
def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=True) + "\n")


# Lee archivos JSONL locales. Lo uso para cotizaciones, leads y notificaciones.
def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))
    return records


# Lee las cotizaciones guardadas localmente cuando no usamos MySQL.
def read_local_quotes() -> list[dict[str, Any]]:
    return read_jsonl(QUOTES_FILE)


# Lee los leads guardados localmente cuando no usamos MySQL.
def read_local_leads() -> list[dict[str, Any]]:
    return read_jsonl(LEADS_FILE)


# Lee las notificaciones guardadas localmente para revisar que el flujo aviso algo.
def read_local_notifications() -> list[dict[str, Any]]:
    return read_jsonl(NOTIFICATIONS_FILE)


# Lee los intentos CRM preparados en modo seguro.
def read_local_crm_syncs() -> list[dict[str, Any]]:
    return read_jsonl(CRM_SYNCS_FILE)


# Lee las respuestas y clasificaciones de IA guardadas en modo seguro.
def read_local_ai_analyses() -> list[dict[str, Any]]:
    return read_jsonl(AI_ANALYSES_FILE)


# Lee las llamadas simuladas del agente telefonico en modo seguro.
def read_local_voice_calls() -> list[dict[str, Any]]:
    return read_jsonl(VOICE_CALLS_FILE)


# Lee eventos de tracking guardados localmente.
def read_local_tracking_events() -> list[dict[str, Any]]:
    return read_jsonl(TRACKING_EVENTS_FILE)


# Busca si ya existe una solicitud exactamente igual en el respaldo local.
def find_local_duplicate(duplicate_key: str) -> dict[str, Any] | None:
    for quote in read_local_quotes():
        if quote.get("duplicate_key") == duplicate_key:
            return quote
    return None


def find_local_lead_duplicate(duplicate_key: str) -> dict[str, Any] | None:
    for lead in read_local_leads():
        if lead.get("duplicate_key") == duplicate_key:
            return lead
    return None


# Convierte fechas de Python a texto, para que el JSON de respuesta sea facil de leer.
def clean_mysql_value(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


# MySQL entiende mejor fechas con espacio en vez de la T de ISO.
def mysql_datetime(value: Any) -> Any:
    if not value:
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return value
    return parsed.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")


# Convierte columnas JSON de MySQL al mismo formato que usa el respaldo local.
def normalize_mysql_lead(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not row:
        return None

    lead = {key: clean_mysql_value(value) for key, value in row.items()}
    for mysql_key, lead_key, default in [
        ("tags_json", "tags", []),
        ("sheet_row_json", "sheet_row", {}),
        ("ghl_payloads_json", "ghl_payloads", {}),
    ]:
        raw_value = lead.pop(mysql_key, default)
        if isinstance(raw_value, str):
            lead[lead_key] = json.loads(raw_value)
        else:
            lead[lead_key] = raw_value or default
    return lead


# Busca duplicados en MySQL cuando la base de datos ya este configurada.
def find_mysql_duplicate(duplicate_key: str) -> dict[str, Any] | None:
    with mysql_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
              id, full_name, email, phone, request_type, product_category,
              quantity, unit, status, priority, created_at
            FROM quote_requests
            WHERE duplicate_key = %s
            LIMIT 1
            """,
            (duplicate_key,),
        )
        return cursor.fetchone()


# Busca si este lead ya existe en MySQL. Asi evitamos crear dos leads del mismo pedido.
def find_mysql_lead_duplicate(duplicate_key: str) -> dict[str, Any] | None:
    with mysql_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
              id, duplicate_key, quote_id, full_name, first_name, last_name, email,
              phone, company_name, customer_type, delivery_city, product_category,
              products_summary, quantity, urgency, priority, lead_score,
              pipeline_stage, follow_up_status, task_due_at, estimated_value_cop,
              source, notes, tags_json, sheet_row_json, ghl_payloads_json,
              advisor_message, created_at, updated_at
            FROM lead_records
            WHERE duplicate_key = %s
            LIMIT 1
            """,
            (duplicate_key,),
        )
        return normalize_mysql_lead(cursor.fetchone())


# Guarda una cotizacion nueva en MySQL y tambien registra un evento.
def save_mysql_quote(quote: dict[str, Any]) -> None:
    quote_for_mysql = {
        **quote,
        "items_json": json.dumps(quote.get("items", []), ensure_ascii=True),
        "created_at": mysql_datetime(quote.get("created_at")),
    }
    with mysql_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO quote_requests (
                id, duplicate_key, full_name, email, phone, customer_type,
                company_name, request_type, product_category, quantity, unit,
                budget_cop, urgency, delivery_city, source, notes, items_json, priority,
                score, status, priority_reason, created_at
            )
            VALUES (
                %(id)s, %(duplicate_key)s, %(full_name)s, %(email)s, %(phone)s,
                %(customer_type)s, %(company_name)s, %(request_type)s,
                %(product_category)s, %(quantity)s, %(unit)s, %(budget_cop)s,
                %(urgency)s, %(delivery_city)s, %(source)s, %(notes)s, %(items_json)s,
                %(priority)s, %(score)s, %(status)s, %(priority_reason)s,
                %(created_at)s
            )
            """,
            quote_for_mysql,
        )
        cursor.execute(
            """
            INSERT INTO quote_events (quote_id, event_type, event_payload)
            VALUES (%s, %s, %s)
            """,
            (quote["id"], "quote_request_created", json.dumps(quote, ensure_ascii=True)),
        )
        connection.commit()


# Guarda el lead en MySQL cuando ya tengamos una base de datos configurada.
def save_mysql_lead(lead: dict[str, Any]) -> None:
    lead_for_mysql = {
        **lead,
        "tags_json": json.dumps(lead.get("tags", []), ensure_ascii=True),
        "sheet_row_json": json.dumps(lead.get("sheet_row", {}), ensure_ascii=True),
        "ghl_payloads_json": json.dumps(lead.get("ghl_payloads", {}), ensure_ascii=True),
        "task_due_at": mysql_datetime(lead.get("task_due_at")),
        "created_at": mysql_datetime(lead.get("created_at")),
        "updated_at": mysql_datetime(lead.get("updated_at")),
    }
    with mysql_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO lead_records (
                id, duplicate_key, quote_id, full_name, first_name, last_name,
                email, phone, company_name, customer_type, delivery_city,
                product_category, products_summary, quantity, urgency, priority,
                lead_score, pipeline_stage, follow_up_status, task_due_at,
                estimated_value_cop, source, notes, tags_json, sheet_row_json,
                ghl_payloads_json, advisor_message, created_at, updated_at
            )
            VALUES (
                %(id)s, %(duplicate_key)s, %(quote_id)s, %(full_name)s,
                %(first_name)s, %(last_name)s, %(email)s, %(phone)s,
                %(company_name)s, %(customer_type)s, %(delivery_city)s,
                %(product_category)s, %(products_summary)s, %(quantity)s,
                %(urgency)s, %(priority)s, %(lead_score)s, %(pipeline_stage)s,
                %(follow_up_status)s, %(task_due_at)s, %(estimated_value_cop)s,
                %(source)s, %(notes)s, %(tags_json)s, %(sheet_row_json)s,
                %(ghl_payloads_json)s, %(advisor_message)s, %(created_at)s,
                %(updated_at)s
            )
            """,
            lead_for_mysql,
        )
        cursor.execute(
            """
            INSERT INTO quote_events (quote_id, event_type, event_payload)
            VALUES (%s, %s, %s)
            """,
            (lead["quote_id"], "lead_record_created", json.dumps(lead, ensure_ascii=True)),
        )
        connection.commit()


# Guarda una notificacion preparada. Despues esto puede ser email, WhatsApp o tarea en GoHighLevel.
def save_mysql_notification(notification: dict[str, Any]) -> None:
    notification_for_mysql = {
        **notification,
        "created_at": mysql_datetime(notification.get("created_at")),
    }
    with mysql_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO advisor_notifications (
                id, lead_id, quote_id, channel, priority, message, status, created_at
            )
            VALUES (
                %(id)s, %(lead_id)s, %(quote_id)s, %(channel)s, %(priority)s,
                %(message)s, %(status)s, %(created_at)s
            )
            """,
            notification_for_mysql,
        )
        connection.commit()


# Guarda el intento de sincronizacion CRM. En esta fase todavia no manda datos reales.
def save_mysql_crm_sync(sync: dict[str, Any]) -> None:
    sync_for_mysql = {
        **sync,
        "will_send_to_crm": bool(sync.get("will_send_to_crm")),
        "contact_request_json": json.dumps(sync.get("requests", {}).get("contact_upsert", {}), ensure_ascii=True),
        "opportunity_request_json": json.dumps(
            sync.get("requests", {}).get("opportunity_create", {}),
            ensure_ascii=True,
        ),
        "missing_config_json": json.dumps(sync.get("missing_config", []), ensure_ascii=True),
        "created_at": mysql_datetime(sync.get("created_at")),
    }
    with mysql_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO crm_sync_attempts (
                id, lead_id, quote_id, provider, mode, status, will_send_to_crm,
                contact_request_json, opportunity_request_json, missing_config_json,
                created_at
            )
            VALUES (
                %(id)s, %(lead_id)s, %(quote_id)s, %(provider)s, %(mode)s,
                %(status)s, %(will_send_to_crm)s, %(contact_request_json)s,
                %(opportunity_request_json)s, %(missing_config_json)s, %(created_at)s
            )
            """,
            sync_for_mysql,
        )
        connection.commit()


# Guarda una clasificacion IA. En esta fase no hay llamada a un modelo externo.
def save_mysql_ai_analysis(analysis: dict[str, Any]) -> None:
    analysis_for_mysql = {
        **analysis,
        "handoff_required": bool(analysis.get("handoff_required")),
        "will_call_ai_model": bool(analysis.get("will_call_ai_model")),
        "guardrails_json": json.dumps(analysis.get("guardrails", []), ensure_ascii=True),
        "suggested_tags_json": json.dumps(analysis.get("suggested_tags", []), ensure_ascii=True),
        "prompt_pack_json": json.dumps(analysis.get("prompt_pack", {}), ensure_ascii=True),
        "created_at": mysql_datetime(analysis.get("created_at")),
    }
    with mysql_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO ai_safe_analyses (
                id, lead_id, quote_id, mode, status, will_call_ai_model,
                intent, category, confidence, handoff_required, handoff_reason,
                safe_reply, guardrails_json, suggested_tags_json, prompt_pack_json,
                created_at
            )
            VALUES (
                %(id)s, %(lead_id)s, %(quote_id)s, %(mode)s, %(status)s,
                %(will_call_ai_model)s, %(intent)s, %(category)s, %(confidence)s,
                %(handoff_required)s, %(handoff_reason)s, %(safe_reply)s,
                %(guardrails_json)s, %(suggested_tags_json)s, %(prompt_pack_json)s,
                %(created_at)s
            )
            """,
            analysis_for_mysql,
        )
        connection.commit()


# Guarda una llamada del agente telefonico. En esta fase solo es simulacion segura.
def save_mysql_voice_call(call: dict[str, Any]) -> None:
    call_for_mysql = {
        **call,
        "will_call_voice_provider": bool(call.get("will_call_voice_provider")),
        "will_call_ai_model": bool(call.get("will_call_ai_model")),
        "handoff_required": bool(call.get("handoff_required")),
        "guardrails_json": json.dumps(call.get("guardrails", []), ensure_ascii=True),
        "next_questions_json": json.dumps(call.get("next_questions", []), ensure_ascii=True),
        "voice_lead_draft_json": json.dumps(call.get("voice_lead_draft", {}), ensure_ascii=True),
        "created_at": mysql_datetime(call.get("created_at")),
    }
    with mysql_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO voice_call_intakes (
                id, mode, status, provider, will_call_voice_provider,
                will_call_ai_model, caller_name, phone, email, delivery_city,
                transcript, intent, product_category, quantity, unit, urgency,
                priority, confidence, handoff_required, handoff_reason,
                safe_voice_reply, guardrails_json, next_questions_json,
                voice_lead_draft_json, advisor_brief, created_at
            )
            VALUES (
                %(id)s, %(mode)s, %(status)s, %(provider)s,
                %(will_call_voice_provider)s, %(will_call_ai_model)s,
                %(caller_name)s, %(phone)s, %(email)s, %(delivery_city)s,
                %(transcript)s, %(intent)s, %(product_category)s, %(quantity)s,
                %(unit)s, %(urgency)s, %(priority)s, %(confidence)s,
                %(handoff_required)s, %(handoff_reason)s, %(safe_voice_reply)s,
                %(guardrails_json)s, %(next_questions_json)s,
                %(voice_lead_draft_json)s, %(advisor_brief)s, %(created_at)s
            )
            """,
            call_for_mysql,
        )
        connection.commit()


# Guarda eventos de tracking para analizar de donde vienen los pedidos.
def save_mysql_tracking_event(event: dict[str, Any]) -> None:
    event_for_mysql = {
        **event,
        "metadata_json": json.dumps(event.get("metadata", {}), ensure_ascii=True),
        "created_at": mysql_datetime(event.get("created_at")),
    }
    with mysql_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO tracking_events (
                id, mode, event_name, session_id, page_path, page_title,
                utm_source, utm_medium, utm_campaign, utm_term, utm_content,
                referrer, user_agent, metadata_json, created_at
            )
            VALUES (
                %(id)s, %(mode)s, %(event_name)s, %(session_id)s, %(page_path)s,
                %(page_title)s, %(utm_source)s, %(utm_medium)s, %(utm_campaign)s,
                %(utm_term)s, %(utm_content)s, %(referrer)s, %(user_agent)s,
                %(metadata_json)s, %(created_at)s
            )
            """,
            event_for_mysql,
        )
        connection.commit()


# Decide donde guardar: primero intenta MySQL; si falla, usa archivo local.
def save_quote(quote: dict[str, Any]) -> dict[str, Any]:
    if mysql_configured():
        try:
            duplicate = find_mysql_duplicate(quote["duplicate_key"])
            if duplicate:
                return {"duplicate": True, "storage": "mysql", "quote": duplicate}

            save_mysql_quote(quote)
            return {"duplicate": False, "storage": "mysql", "quote": quote}
        except Exception as exc:
            append_jsonl(
                ERRORS_FILE,
                {
                    "error": str(exc),
                    "fallback": "local_jsonl",
                    "quote": quote,
                },
            )

    duplicate = find_local_duplicate(quote["duplicate_key"])
    if duplicate:
        return {"duplicate": True, "storage": "local_jsonl", "quote": duplicate}

    append_jsonl(QUOTES_FILE, quote)
    return {"duplicate": False, "storage": "local_jsonl", "quote": quote}


# Guarda el lead comercial. Primero intenta MySQL y si algo falla usa archivo local.
def save_lead(lead: dict[str, Any]) -> dict[str, Any]:
    if mysql_configured():
        try:
            duplicate = find_mysql_lead_duplicate(lead["duplicate_key"])
            if duplicate:
                return {"duplicate": True, "storage": "mysql", "lead": duplicate}

            save_mysql_lead(lead)
            return {"duplicate": False, "storage": "mysql", "lead": lead}
        except Exception as exc:
            append_jsonl(
                ERRORS_FILE,
                {
                    "error": str(exc),
                    "fallback": "local_jsonl",
                    "lead": lead,
                },
            )

    duplicate = find_local_lead_duplicate(lead["duplicate_key"])
    if duplicate:
        return {"duplicate": True, "storage": "local_jsonl", "lead": duplicate}

    append_jsonl(LEADS_FILE, lead)
    return {"duplicate": False, "storage": "local_jsonl", "lead": lead}


# Guarda la notificacion preparada sin perderla si MySQL no responde.
def save_notification(notification: dict[str, Any]) -> str:
    if mysql_configured():
        try:
            save_mysql_notification(notification)
            return "mysql"
        except Exception as exc:
            append_jsonl(
                ERRORS_FILE,
                {
                    "error": str(exc),
                    "fallback": "local_jsonl",
                    "notification": notification,
                },
            )

    append_jsonl(NOTIFICATIONS_FILE, notification)
    return "local_jsonl"


# Guarda el resultado del modo seguro de CRM para poder revisarlo despues.
def save_crm_sync(sync: dict[str, Any]) -> str:
    if mysql_configured():
        try:
            save_mysql_crm_sync(sync)
            return "mysql"
        except Exception as exc:
            append_jsonl(
                ERRORS_FILE,
                {
                    "error": str(exc),
                    "fallback": "local_jsonl",
                    "crm_sync": sync,
                },
            )

    append_jsonl(CRM_SYNCS_FILE, sync)
    return "local_jsonl"


# Guarda el resultado de la IA segura para poder revisar intencion, guardrails y handoff.
def save_ai_analysis(analysis: dict[str, Any]) -> str:
    if mysql_configured():
        try:
            save_mysql_ai_analysis(analysis)
            return "mysql"
        except Exception as exc:
            append_jsonl(
                ERRORS_FILE,
                {
                    "error": str(exc),
                    "fallback": "local_jsonl",
                    "ai_analysis": analysis,
                },
            )

    append_jsonl(AI_ANALYSES_FILE, analysis)
    return "local_jsonl"


# Guarda la llamada segura para revisarla despues o convertirla en tarea comercial.
def save_voice_call(call: dict[str, Any]) -> str:
    if mysql_configured():
        try:
            save_mysql_voice_call(call)
            return "mysql"
        except Exception as exc:
            append_jsonl(
                ERRORS_FILE,
                {
                    "error": str(exc),
                    "fallback": "local_jsonl",
                    "voice_call": call,
                },
            )

    append_jsonl(VOICE_CALLS_FILE, call)
    return "local_jsonl"


# Guarda el evento de tracking sin perderlo si MySQL no esta listo.
def save_tracking_event(event: dict[str, Any]) -> str:
    if mysql_configured():
        try:
            save_mysql_tracking_event(event)
            return "mysql"
        except Exception as exc:
            append_jsonl(
                ERRORS_FILE,
                {
                    "error": str(exc),
                    "fallback": "local_jsonl",
                    "tracking_event": event,
                },
            )

    append_jsonl(TRACKING_EVENTS_FILE, event)
    return "local_jsonl"


# Flujo completo del formulario: recibe, valida, guarda y responde.
def handle_quote_request():
    payload = request.get_json(silent=True) or {}
    quote, errors = build_quote_record(payload)

    if errors:
        return jsonify(
            {
                "ok": False,
                "errors": errors,
                "messages": [ERROR_MESSAGES.get(error, error) for error in errors],
                "quote": quote,
            }
        ), 400

    result = save_quote(quote)
    return jsonify({"ok": True, **result}), 200 if result["duplicate"] else 201


# Recibe el resultado de la cotizacion y lo convierte en lead comercial.
def handle_lead_request():
    payload = request.get_json(silent=True) or {}
    quote = payload.get("quote") if isinstance(payload.get("quote"), dict) else {}
    lead, errors = build_lead_record(payload)

    if errors:
        return jsonify({"ok": False, "errors": errors, "lead": lead}), 400

    result = save_lead(lead)
    saved_lead = result["lead"]
    quote_duplicate = bool(payload.get("duplicate"))
    lead_duplicate = bool(result["duplicate"])

    return jsonify(
        {
            "ok": True,
            "duplicate": quote_duplicate or lead_duplicate,
            "quote_duplicate": quote_duplicate,
            "lead_duplicate": lead_duplicate,
            "storage": result["storage"],
            "quote": quote,
            "lead": saved_lead,
            "sheet_row": saved_lead.get("sheet_row", {}),
            "ghl_payloads": saved_lead.get("ghl_payloads", {}),
            "advisor_message": saved_lead.get("advisor_message", ""),
        }
    ), 200 if lead_duplicate else 201


# Recibe un lead y prepara lo que se mandaria a GoHighLevel en modo seguro.
def handle_crm_sync_request():
    payload = request.get_json(silent=True) or {}
    sync, errors = build_crm_sync_record(payload)

    if errors:
        return jsonify({"ok": False, "errors": errors, "crm_sync": sync}), 400

    storage = save_crm_sync(sync)
    return jsonify({"ok": True, **payload, "crm_sync_storage": storage, "crm_sync": sync}), 201


# Prepara una clasificacion y una respuesta segura sin llamar a IA externa.
def handle_ai_request():
    payload = request.get_json(silent=True) or {}
    analysis, errors = build_ai_analysis(payload)

    if errors:
        return jsonify({"ok": False, "errors": errors, "ai_analysis": analysis}), 400

    storage = save_ai_analysis(analysis)
    return jsonify({"ok": True, **payload, "ai_analysis_storage": storage, "ai_analysis": analysis}), 201


# Recibe una transcripcion de llamada y prepara respuesta telefonica segura.
def handle_voice_call_request():
    payload = request.get_json(silent=True) or {}
    call, errors = build_voice_call_record(payload)

    if errors:
        return jsonify({"ok": False, "errors": errors, "voice_call": call}), 400

    storage = save_voice_call(call)
    return jsonify({"ok": True, **payload, "voice_call_storage": storage, "voice_call": call}), 201


# Recibe eventos de tracking local para entender el comportamiento de la pagina.
def handle_tracking_event_request():
    payload = request.get_json(silent=True) or {}
    event, errors = build_tracking_event(payload)

    if errors:
        return jsonify({"ok": False, "errors": errors, "tracking_event": event}), 400

    storage = save_tracking_event(event)
    return jsonify({"ok": True, "tracking_event_storage": storage, "tracking_event": event}), 201


# Endpoint sencillo para revisar si la API esta viva.
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "electropatios-quote-api"})


# Catalogo inicial que despues puede conectarse con inventario real.
@app.route("/api/catalog", methods=["GET"])
def catalog():
    return jsonify({"ok": True, "company": "Electropatios", "categories": PRODUCT_CATEGORIES})


@app.route("/api/quotes", methods=["OPTIONS"])
def quote_options():
    return "", 204


@app.route("/api/quotes", methods=["POST"])
def create_quote():
    return handle_quote_request()


@app.route("/api/quotes", methods=["GET"])
def list_quotes():
    expected_token = os.getenv("ADMIN_TOKEN")
    if expected_token and request.args.get("token") != expected_token:
        return jsonify({"ok": False, "error": "invalid admin token"}), 401

    return jsonify({"ok": True, "quotes": read_local_quotes()})


@app.route("/api/leads", methods=["OPTIONS"])
def lead_options():
    return "", 204


@app.route("/api/leads", methods=["POST"])
def create_lead():
    return handle_lead_request()


@app.route("/api/leads", methods=["GET"])
def list_leads():
    expected_token = os.getenv("ADMIN_TOKEN")
    if expected_token and request.args.get("token") != expected_token:
        return jsonify({"ok": False, "error": "invalid admin token"}), 401

    return jsonify({"ok": True, "leads": read_local_leads()})


@app.route("/api/notifications", methods=["OPTIONS"])
def notification_options():
    return "", 204


@app.route("/api/notifications", methods=["POST"])
def create_notification():
    payload = request.get_json(silent=True) or {}
    notification = build_notification(payload)
    storage = save_notification(notification)
    return jsonify({"ok": True, **payload, "notification_storage": storage, "notification": notification}), 201


@app.route("/api/notifications", methods=["GET"])
def list_notifications():
    expected_token = os.getenv("ADMIN_TOKEN")
    if expected_token and request.args.get("token") != expected_token:
        return jsonify({"ok": False, "error": "invalid admin token"}), 401

    return jsonify({"ok": True, "notifications": read_local_notifications()})


@app.route("/api/crm/sync", methods=["OPTIONS"])
def crm_sync_options():
    return "", 204


@app.route("/api/crm/sync", methods=["POST"])
def create_crm_sync():
    return handle_crm_sync_request()


@app.route("/api/crm/syncs", methods=["GET"])
def list_crm_syncs():
    expected_token = os.getenv("ADMIN_TOKEN")
    if expected_token and request.args.get("token") != expected_token:
        return jsonify({"ok": False, "error": "invalid admin token"}), 401

    return jsonify({"ok": True, "crm_syncs": read_local_crm_syncs()})


@app.route("/api/ai/classify", methods=["OPTIONS"])
def ai_classify_options():
    return "", 204


@app.route("/api/ai/classify", methods=["POST"])
def create_ai_classification():
    return handle_ai_request()


@app.route("/api/ai/assist", methods=["OPTIONS"])
def ai_assist_options():
    return "", 204


@app.route("/api/ai/assist", methods=["POST"])
def create_ai_assist():
    return handle_ai_request()


@app.route("/api/ai/analyses", methods=["GET"])
def list_ai_analyses():
    expected_token = os.getenv("ADMIN_TOKEN")
    if expected_token and request.args.get("token") != expected_token:
        return jsonify({"ok": False, "error": "invalid admin token"}), 401

    return jsonify({"ok": True, "ai_analyses": read_local_ai_analyses()})


@app.route("/api/voice/intake", methods=["OPTIONS"])
def voice_intake_options():
    return "", 204


@app.route("/api/voice/intake", methods=["POST"])
def create_voice_call():
    return handle_voice_call_request()


@app.route("/api/voice/calls", methods=["GET"])
def list_voice_calls():
    expected_token = os.getenv("ADMIN_TOKEN")
    if expected_token and request.args.get("token") != expected_token:
        return jsonify({"ok": False, "error": "invalid admin token"}), 401

    return jsonify({"ok": True, "voice_calls": read_local_voice_calls()})


@app.route("/api/tracking/events", methods=["OPTIONS"])
def tracking_events_options():
    return "", 204


@app.route("/api/tracking/events", methods=["POST"])
def create_tracking_event():
    return handle_tracking_event_request()


@app.route("/api/tracking/events", methods=["GET"])
def list_tracking_events():
    expected_token = os.getenv("ADMIN_TOKEN")
    if expected_token and request.args.get("token") != expected_token:
        return jsonify({"ok": False, "error": "invalid admin token"}), 401

    return jsonify({"ok": True, "tracking_events": read_local_tracking_events()})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_ENV") == "development")
