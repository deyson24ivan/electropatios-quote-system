# Guia de API

Esta guia es para entender la Fase 2 del proyecto: como una pagina web le manda informacion a una API usando HTTP y JSON.

## Que es la API en este proyecto

La API es la parte de Python que recibe solicitudes de cotizacion. En este proyecto vive en:

```text
backend/app.py
```

Cuando el cliente llena el formulario, JavaScript envia los datos a:

```text
POST http://localhost:5000/api/quotes
```

Ese `POST` significa: "quiero enviar informacion nueva".

## Endpoints actuales

| Metodo | Ruta | Para que sirve |
| --- | --- | --- |
| GET | `/health` | Revisa si la API esta viva. |
| GET | `/api/catalog` | Devuelve categorias de productos. |
| POST | `/api/quotes` | Recibe una cotizacion nueva. |
| GET | `/api/quotes` | Lista cotizaciones guardadas localmente. |
| POST | `/api/leads` | Convierte una cotizacion guardada en lead comercial. |
| GET | `/api/leads` | Lista leads guardados localmente. |
| POST | `/api/notifications` | Guarda una notificacion preparada para el asesor. |
| GET | `/api/notifications` | Lista notificaciones guardadas localmente. |
| POST | `/api/crm/sync` | Prepara sincronizacion segura con GoHighLevel. |
| GET | `/api/crm/syncs` | Lista intentos CRM guardados localmente. |
| POST | `/api/ai/classify` | Clasifica intencion, categoria y handoff en modo seguro. |
| POST | `/api/ai/assist` | Prepara una respuesta segura para el cliente. |
| GET | `/api/ai/analyses` | Lista analisis de IA guardados localmente. |
| POST | `/api/voice/intake` | Recibe una transcripcion de llamada y prepara respuesta telefonica segura. |
| GET | `/api/voice/calls` | Lista llamadas simuladas guardadas localmente. |
| POST | `/api/tracking/events` | Guarda un evento de tracking local. |
| GET | `/api/tracking/events` | Lista eventos de tracking guardados localmente. |

## Ejemplo de JSON que recibe la API

```json
{
  "full_name": "Ana Perez",
  "email": "ana@example.com",
  "phone": "+573001234567",
  "customer_type": "tecnico_electricista",
  "company_name": "",
  "request_type": "quote",
  "product_category": "cable",
  "quantity": "120",
  "unit": "metro",
  "budget": "2500000",
  "urgency": "hoy",
  "delivery_city": "Los Patios",
  "notes": "Cable #12 para entregar hoy",
  "items": [
    {
      "sku": "CAB-THHN-12",
      "name": "Cable THHN #12",
      "category": "cable",
      "quantity": 120,
      "unit": "metro"
    }
  ],
  "source": "manual_test",
  "consent": true
}
```

## Que hace la API cuando recibe una solicitud

1. Recibe el JSON.
2. Limpia datos como telefono, cantidad y presupuesto.
3. Valida que no falte lo importante.
4. Calcula prioridad: `high`, `medium` o `low`.
5. Revisa si la misma solicitud ya fue enviada.
6. Guarda la solicitud.
7. Responde con otro JSON.

## Como funciona el carrito de la pagina

La pagina tiene un catalogo en `frontend/script.js`. Cuando el cliente presiona
`Agregar`, JavaScript guarda ese producto en un carrito temporal. Al enviar el
pedido, el carrito viaja a la API dentro de la propiedad `items`.

Ejemplo:

```json
"items": [
  {
    "sku": "CAB-THHN-12",
    "name": "Cable THHN #12",
    "category": "cable",
    "quantity": 30,
    "unit": "metro"
  }
]
```

Todavia no hay pago online. La idea realista para esta version es que el cliente
arme un pedido y Electropatios confirme precio, disponibilidad y entrega.

## Respuesta cuando todo sale bien

```json
{
  "ok": true,
  "duplicate": false,
  "storage": "local_jsonl",
  "quote": {
    "full_name": "Ana Perez",
    "product_category": "cable",
    "quantity": 120,
    "priority": "high",
    "status": "qualified"
  }
}
```

## Respuesta de lead automation

Despues de guardar la cotizacion, n8n llama a:

```text
POST http://localhost:5000/api/leads
```

Ese endpoint responde con datos listos para seguimiento:

```json
{
  "ok": true,
  "lead": {
    "full_name": "Ana Perez",
    "priority": "high",
    "pipeline_stage": "contactar_hoy"
  },
  "sheet_row": {
    "nombre": "Ana Perez",
    "telefono": "+573001234567",
    "prioridad": "high"
  },
  "ghl_payloads": {
    "contact": {
      "firstName": "Ana",
      "email": "ana@example.com"
    }
  }
}
```

En la Fase 5 usaremos esa parte de `ghl_payloads` para hablar con GoHighLevel.

## Respuesta CRM en modo seguro

n8n llama a:

```text
POST http://localhost:5000/api/crm/sync
```

La API responde algo como:

```json
{
  "ok": true,
  "crm_sync": {
    "provider": "gohighlevel",
    "mode": "safe_mode",
    "status": "dry_run_prepared",
    "will_send_to_crm": false,
    "missing_config": [
      "GHL_PRIVATE_TOKEN",
      "GHL_LOCATION_ID",
      "GHL_PIPELINE_ID",
      "GHL_STAGE_HIGH"
    ]
  }
}
```

Eso quiere decir: el sistema ya sabe que mandaria, pero todavia no envio nada real.

## Respuesta IA en modo seguro

n8n llama a:

```text
POST http://localhost:5000/api/ai/classify
```

La API responde algo como:

```json
{
  "ok": true,
  "ai_analysis": {
    "mode": "safe_mode",
    "intent": "quote",
    "category": "cable",
    "confidence": "high",
    "handoff_required": true,
    "will_call_ai_model": false
  }
}
```

Eso significa que la IA clasifico el caso, pero no llamo ningun modelo externo.

## Respuesta Voice AI en modo seguro

Para simular una llamada telefonica, n8n o PowerShell manda:

```text
POST http://localhost:5000/api/voice/intake
```

Ejemplo:

```json
{
  "caller_name": "Carlos Ramirez",
  "phone": "+57 301 222 3344",
  "delivery_city": "Los Patios",
  "transcript": "Necesito 120 metros de cable THHN para hoy."
}
```

La API responde algo como:

```json
{
  "ok": true,
  "voice_call": {
    "mode": "safe_mode",
    "provider": "local_simulator",
    "intent": "quote",
    "product_category": "cable",
    "priority": "high",
    "handoff_required": true,
    "safe_voice_reply": "Claro, Carlos. Dejo registrada tu solicitud de cable thhn. Un asesor de Electropatios confirma precio, disponibilidad y entrega antes de cerrar la cotizacion."
  }
}
```

Esto significa que el sistema actua como agente telefonico, pero todavia no llama a Twilio, GoHighLevel Phone, ElevenLabs ni a un modelo externo.

## Respuesta tracking en modo local

La pagina manda eventos a:

```text
POST http://localhost:5000/api/tracking/events
```

Ejemplo:

```json
{
  "event_name": "product_add",
  "session_id": "manual-session-001",
  "utm_source": "facebook",
  "utm_medium": "paid_social",
  "utm_campaign": "cables_agosto",
  "metadata": {
    "sku": "CAB-THHN-12",
    "quantity": 2
  }
}
```

La API responde algo como:

```json
{
  "ok": true,
  "tracking_event": {
    "event_name": "product_add",
    "mode": "local_tracking",
    "utm_source": "facebook",
    "utm_campaign": "cables_agosto"
  }
}
```

Eso significa que el evento quedo guardado localmente, sin llamar Google Analytics, Tag Manager ni Meta Pixel.

## Respuesta cuando faltan datos

```json
{
  "ok": false,
  "errors": [
    "valid_email_required",
    "quantity_required_for_quotes"
  ],
  "messages": [
    "Escribe un email valido.",
    "Escribe la cantidad que necesitas cotizar."
  ]
}
```

## Pruebas desde PowerShell

Primero confirma que la API esta viva:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/health"
```

Luego puedes enviar un archivo JSON de ejemplo:

```powershell
$body = Get-Content -Raw "examples/requests/quote-cable-urgent.json"
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/quotes" -Method Post -ContentType "application/json" -Body $body
```

Para probar la llamada simulada:

```powershell
$body = Get-Content -Raw "examples/requests/voice-call-cable-urgent.json"
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/voice/intake" -Method Post -ContentType "application/json" -Body $body
```

Para probar tracking local:

```powershell
$body = Get-Content -Raw "examples/requests/tracking-product-add.json"
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/tracking/events" -Method Post -ContentType "application/json" -Body $body
```

## Como lo explicaria en entrevista

El formulario de Electropatios no guarda los datos directamente. Primero convierte los campos en JSON y los envia por HTTP. n8n recibe el pedido, llama a mi API en Python, la API valida la solicitud, calcula prioridad comercial, detecta duplicados y crea un lead listo para Sheets o CRM. Tambien tengo tracking local para medir eventos y UTM, y un endpoint de Voice AI en modo seguro que toma una transcripcion de llamada, detecta intencion, categoria, urgencia y prepara una respuesta telefonica sin inventar precios ni disponibilidad.
