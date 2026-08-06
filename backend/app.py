from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request

from quote_logic import PRODUCT_CATEGORIES, build_quote_record


# Rutas principales del proyecto. Todo lo que se guarda localmente queda en backend/data.
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
QUOTES_FILE = DATA_DIR / "quotes.jsonl"
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


# Lee las cotizaciones guardadas localmente cuando no usamos MySQL.
def read_local_quotes() -> list[dict[str, Any]]:
    if not QUOTES_FILE.exists():
        return []

    quotes: list[dict[str, Any]] = []
    with QUOTES_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                quotes.append(json.loads(line))
    return quotes


# Busca si ya existe una solicitud exactamente igual en el respaldo local.
def find_local_duplicate(duplicate_key: str) -> dict[str, Any] | None:
    for quote in read_local_quotes():
        if quote.get("duplicate_key") == duplicate_key:
            return quote
    return None


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


# Guarda una cotizacion nueva en MySQL y tambien registra un evento.
def save_mysql_quote(quote: dict[str, Any]) -> None:
    with mysql_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO quote_requests (
                id, duplicate_key, full_name, email, phone, customer_type,
                company_name, request_type, product_category, quantity, unit,
                budget_cop, urgency, delivery_city, source, notes, priority,
                score, status, priority_reason, created_at
            )
            VALUES (
                %(id)s, %(duplicate_key)s, %(full_name)s, %(email)s, %(phone)s,
                %(customer_type)s, %(company_name)s, %(request_type)s,
                %(product_category)s, %(quantity)s, %(unit)s, %(budget_cop)s,
                %(urgency)s, %(delivery_city)s, %(source)s, %(notes)s,
                %(priority)s, %(score)s, %(status)s, %(priority_reason)s,
                %(created_at)s
            )
            """,
            quote,
        )
        cursor.execute(
            """
            INSERT INTO quote_events (quote_id, event_type, event_payload)
            VALUES (%s, %s, %s)
            """,
            (quote["id"], "quote_request_created", json.dumps(quote, ensure_ascii=True)),
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


# Flujo completo del formulario: recibe, valida, guarda y responde.
def handle_quote_request():
    payload = request.get_json(silent=True) or {}
    quote, errors = build_quote_record(payload)

    if errors:
        return jsonify({"ok": False, "errors": errors, "quote": quote}), 400

    result = save_quote(quote)
    return jsonify({"ok": True, **result}), 200 if result["duplicate"] else 201


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


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_ENV") == "development")

