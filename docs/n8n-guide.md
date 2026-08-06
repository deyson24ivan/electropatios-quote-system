# Guia de n8n

Esta guia cubre la Fase 3 del proyecto: usar n8n para recibir pedidos y conectarlos con la API de Electropatios.

## Que es n8n en este proyecto

n8n es la herramienta que va en medio del negocio. En vez de que la pagina hable solo con Python, n8n puede recibir el pedido, decidir que hacer y conectarlo con otras herramientas.

Flujo actual:

```text
Pagina Electropatios
  -> Webhook n8n
  -> Validacion en n8n
  -> API Python /api/quotes
  -> API Python /api/leads
  -> Preparacion para Sheets
  -> CRM GoHighLevel en modo seguro
  -> Respuesta al cliente
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

El workflow importable esta en:

```text
n8n/electropatios-order-workflow.json
```

## Nodos del workflow

| Nodo | Que hace |
| --- | --- |
| Webhook Electropatios Order | Recibe el pedido por HTTP POST. |
| Validate Order | Revisa que venga nombre, email, telefono, consentimiento y productos. |
| Is Valid Order? | Decide si el pedido sigue o responde error. |
| Send To Quote API | Envia el pedido a `http://127.0.0.1:5000/api/quotes`. |
| Create Lead Record | Convierte la cotizacion en lead usando `http://127.0.0.1:5000/api/leads`. |
| Prepare Sheets Row | Deja lista la fila que despues ira a Google Sheets. |
| Sync CRM Safe Mode | Prepara contacto y oportunidad para GoHighLevel sin enviar datos reales. |
| Is High Priority? | Revisa si el lead debe atenderse hoy. |
| Prepare Advisor Notification | Prepara el texto para el asesor. |
| Save Advisor Notification | Guarda la notificacion preparada en `http://127.0.0.1:5000/api/notifications`. |
| Success Response | Devuelve una respuesta JSON cuando todo salio bien. |
| Invalid Order Response | Devuelve una respuesta JSON cuando faltan datos. |

## Como correr n8n localmente

En este equipo usamos Node.js. PowerShell bloquea `npm.ps1`, por eso usamos comandos `.cmd` o `node` directo.

La primera vez se puede instalar n8n dentro de una cache local del proyecto:

```powershell
npm.cmd install --cache .\.npm-cache --prefix .\.npm-cache\_npx\electropatios-n8n n8n@2.33.4 n8n-nodes-base@2.33.1 sqlite3@5.1.7
```

Despues se arranca con:

```powershell
$env:N8N_USER_FOLDER = ".n8n-local"
node .\.npm-cache\_npx\electropatios-n8n\node_modules\n8n\bin\n8n start
```

El editor queda en:

```text
http://localhost:5678
```

## Como importar y activar el workflow

```powershell
$env:N8N_USER_FOLDER = ".n8n-local"
node .\.npm-cache\_npx\electropatios-n8n\node_modules\n8n\bin\n8n import:workflow --input=n8n\electropatios-order-workflow.json
node .\.npm-cache\_npx\electropatios-n8n\node_modules\n8n\bin\n8n update:workflow --id=electropatios-order-intake --active=true
```

Si n8n ya estaba abierto, se reinicia para que registre el webhook activo.

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

## Que deberia pasar

Si todo esta bien:

1. n8n recibe el pedido.
2. n8n valida los datos.
3. n8n envia el pedido a la API de Python.
4. La API guarda la solicitud y calcula prioridad.
5. n8n crea un lead comercial.
6. n8n prepara una fila para Sheets.
7. n8n prepara el contacto y la oportunidad de GoHighLevel en modo seguro.
8. Si es urgente, n8n guarda una notificacion interna.
9. n8n responde algo como:

```json
{
  "ok": true,
  "duplicate": false,
  "priority": "high",
  "status": "contactar_hoy",
  "quote_id": "...",
  "lead_id": "...",
  "crm_sync": {
    "mode": "safe_mode",
    "status": "dry_run_prepared"
  }
}
```

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

El webhook activo respondio correctamente con un pedido de carrito:

```json
{
  "ok": true,
  "priority": "high",
  "status": "contactar_hoy"
}
```

## Como lo explicaria en entrevista

Use n8n como orquestador entre el formulario y la API. El formulario envia un pedido por webhook, n8n valida campos minimos, llama a una API REST propia, convierte la cotizacion en lead, prepara la fila para Google Sheets, llama el modo seguro de GoHighLevel y guarda una notificacion interna si el pedido es urgente.
