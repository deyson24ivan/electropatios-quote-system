# Guia de n8n

Esta guia cubre la Fase 3 del proyecto: usar n8n para recibir pedidos y conectarlos con la API de Electropatios.

## Que es n8n en este proyecto

n8n es la herramienta que va en medio del negocio. En vez de que la pagina hable solo con Python, n8n puede recibir el pedido, decidir que hacer y conectarlo con otras herramientas.

Flujo actual de pedidos:

```text
Pagina Electropatios
  -> Webhook n8n
  -> Validacion en n8n
  -> API Python /api/quotes
  -> API Python /api/leads
  -> IA segura /api/ai/classify
  -> Preparacion para Sheets
  -> CRM GoHighLevel en modo seguro
  -> Respuesta al cliente
```

Flujo actual de llamadas:

```text
Llamada simulada
  -> Webhook n8n
  -> Validacion en n8n
  -> API Python /api/voice/intake
  -> Respuesta telefonica segura
  -> Notificacion interna si necesita asesor
```

Mas adelante ese mismo flujo puede seguir hacia:

```text
Google Sheets
CRM
Email
WhatsApp
IA
```

## Archivo del workflow

Los workflows importables estan en:

```text
n8n/electropatios-order-workflow.json
n8n/electropatios-voice-workflow.json
```

## Nodos del workflow

| Nodo | Que hace |
| --- | --- |
| Webhook Electropatios Order | Recibe el pedido por HTTP POST. |
| Validate Order | Revisa que venga nombre, email, telefono, consentimiento y productos. |
| Is Valid Order? | Decide si el pedido sigue o responde error. |
| Send To Quote API | Envia el pedido a `http://127.0.0.1:5000/api/quotes`. |
| Create Lead Record | Convierte la cotizacion en lead usando `http://127.0.0.1:5000/api/leads`. |
| AI Classify Safe Mode | Clasifica intencion, categoria, guardrails y handoff sin IA externa. |
| Prepare Sheets Row | Deja lista la fila que despues ira a Google Sheets. |
| Sync CRM Safe Mode | Prepara contacto y oportunidad para GoHighLevel sin enviar datos reales. |
| Is High Priority? | Revisa si el lead debe atenderse hoy. |
| Prepare Advisor Notification | Prepara el texto para el asesor. |
| Save Advisor Notification | Guarda la notificacion preparada en `http://127.0.0.1:5000/api/notifications`. |
| Success Response | Devuelve una respuesta JSON cuando todo salio bien. |
| Invalid Order Response | Devuelve una respuesta JSON cuando faltan datos. |

## Como correr n8n localmente

En este equipo usamos Node.js con `npx`. No hay Docker, servicio de Windows ni instalacion global de n8n.

La instalacion activa probada es:

```text
n8n 2.33.5
http://localhost:5678
C:\Users\deyso\.n8n
```

Para arrancar n8n:

```powershell
npx.cmd --yes n8n@2.33.5 start
```

El editor queda en:

```text
http://localhost:5678
```

## Como importar y activar el workflow

```powershell
npx.cmd --yes n8n@2.33.5 import:workflow --input=n8n\electropatios-order-workflow.json
npx.cmd --yes n8n@2.33.5 update:workflow --id=electropatios-order-intake --active=true
npx.cmd --yes n8n@2.33.5 import:workflow --input=n8n\electropatios-voice-workflow.json
npx.cmd --yes n8n@2.33.5 update:workflow --id=electropatios-voice-intake --active=true
```

Si n8n ya estaba abierto, se reinicia para que registre el webhook activo. No uses `N8N_USER_FOLDER` para este proyecto; la carpeta normal es `C:\Users\deyso\.n8n`.

## Como probar el webhook activo

Con la API de Python corriendo en `http://127.0.0.1:5000`, envia un ejemplo:

```powershell
$body = Get-Content -Raw "examples/requests/storefront-cart-order.json"
Invoke-RestMethod `
  -Uri "http://127.0.0.1:5678/webhook/electropatios-order" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

Para probar el webhook de Voice AI:

```powershell
$body = Get-Content -Raw "examples/requests/voice-call-cable-urgent.json"
Invoke-RestMethod `
  -Uri "http://127.0.0.1:5678/webhook/electropatios-voice-call" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

## Que deberia pasar

Si todo esta bien:

1. n8n recibe el pedido.
2. n8n valida los datos.
3. n8n envia el pedido a la API de Python.
4. La API guarda la solicitud y calcula prioridad.
5. n8n crea un lead comercial.
6. n8n clasifica el caso con IA en modo seguro.
7. n8n prepara una fila para Sheets.
8. n8n prepara el contacto y la oportunidad de GoHighLevel en modo seguro.
9. Si es urgente, n8n guarda una notificacion interna.
10. n8n responde algo como:

```json
{
  "ok": true,
  "duplicate": false,
  "priority": "high",
  "status": "contactar_hoy",
  "quote_id": "...",
  "lead_id": "...",
  "ai_analysis": {
    "intent": "quote",
    "handoff_required": true
  },
  "crm_sync": {
    "mode": "safe_mode",
    "status": "dry_run_prepared"
  }
}
```

Si pruebas el workflow de voz, n8n deberia responder con `safe_voice_reply`, `intent`, `priority` y `handoff_required`.

## Como conectar la pagina con n8n

La pagina ya quedo preparada para esto. En `frontend/script.js` hay una opcion llamada:

```javascript
const USE_N8N_WEBHOOK = true;
```

Con ese valor, el pedido va primero al webhook de n8n. Si n8n esta apagado y quieres probar solo la API de Python, se puede cambiar temporalmente a:

```javascript
const USE_N8N_WEBHOOK = false;
```

Los pedidos enviados por la URL normal `/webhook/electropatios-order` se ven en la seccion **Executions** de n8n. Si quieres ver las cajitas iluminandose en el canvas, se usa `Listen for test event`.

## Resultado probado

El webhook activo respondio correctamente con un pedido de carrito en la instalacion nueva de n8n:

```json
{
  "ok": true,
  "priority": "high",
  "status": "contactar_hoy",
  "ai_analysis": {
    "mode": "safe_mode"
  },
  "crm_sync": {
    "mode": "safe_mode"
  }
}
```

El webhook de Voice AI tambien respondio correctamente:

```json
{
  "ok": true,
  "intent": "quote",
  "priority": "high",
  "handoff_required": true,
  "safe_voice_reply": "Claro, Carlos. Dejo registrada tu solicitud de cable thhn. Un asesor de Electropatios confirma precio, disponibilidad y entrega antes de cerrar la cotizacion."
}
```

## Como lo explicaria en entrevista

Use n8n como orquestador entre el formulario, las llamadas simuladas y la API. El formulario envia un pedido por webhook, n8n valida campos minimos, llama a una API REST propia, convierte la cotizacion en lead, clasifica el caso con IA segura, prepara la fila para Google Sheets, llama el modo seguro de GoHighLevel y guarda una notificacion interna si el pedido es urgente. Para Voice AI, n8n recibe una transcripcion de llamada, llama a `/api/voice/intake` y devuelve una respuesta telefonica segura sin conectar telefonia real todavia.
