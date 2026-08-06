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

## Como lo explicaria en entrevista

El formulario de Electropatios no guarda los datos directamente. Primero convierte los campos en JSON y los envia por HTTP. n8n recibe el pedido, llama a mi API en Python, la API valida la solicitud, calcula prioridad comercial, detecta duplicados y crea un lead listo para Sheets o CRM.
