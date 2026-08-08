# n8n

`electropatios-order-workflow.json` es el workflow principal de pedidos.

`electropatios-voice-workflow.json` es el workflow de llamadas simuladas para Voice AI en modo seguro.

Instalacion local actual:

```text
n8n 2.33.5
Node.js con npx
Datos en C:\Users\deyso\.n8n
Sin Docker, sin servicio de Windows y sin instalacion global
```

Ruta activa probada en local:

```text
POST http://127.0.0.1:5678/webhook/electropatios-order
```

Ruta de Voice AI para probar llamadas simuladas:

```text
POST http://127.0.0.1:5678/webhook/electropatios-voice-call
```

Comandos principales:

```powershell
npx.cmd --yes n8n@2.33.5 start
npx.cmd --yes n8n@2.33.5 import:workflow --input=n8n\electropatios-order-workflow.json
npx.cmd --yes n8n@2.33.5 update:workflow --id=electropatios-order-intake --active=true
npx.cmd --yes n8n@2.33.5 import:workflow --input=n8n\electropatios-voice-workflow.json
npx.cmd --yes n8n@2.33.5 update:workflow --id=electropatios-voice-intake --active=true
```

## Objetivo del workflow

1. Recibir un pedido desde la pagina de Electropatios por webhook.
2. Validar campos minimos.
3. Enviar el payload a la API local.
4. Crear el lead comercial.
5. Clasificar el caso con IA en modo seguro.
6. Preparar una fila para Google Sheets.
7. Preparar datos para GoHighLevel en modo seguro.
8. Guardar una notificacion interna cuando sea prioridad alta.
9. Responder al formulario o prueba manual.

## Objetivo del workflow de voz

1. Recibir una llamada simulada por webhook.
2. Validar que exista transcripcion.
3. Enviar la transcripcion a `POST /api/voice/intake`.
4. Recibir intencion, categoria, prioridad y respuesta telefonica.
5. Si necesita asesor, preparar y guardar una notificacion interna.
6. Responder con el texto que diria el agente.

## Pendiente al importarlo

- Cambiar URLs locales por URLs reales.
- Activar el workflow cuando ya este probado.
- Configurar credenciales de Google Sheets.
- Conectar el nodo real de Google Sheets.
- Conectar GoHighLevel real cuando existan token, location, pipeline y stages.
- Conectar IA real cuando tengamos prompts y guardrails suficientemente probados.
- Conectar proveedor de voz real cuando ya se decida si sera Twilio, GoHighLevel Phone u otra herramienta.
- Configurar credenciales de email, WhatsApp o Slack.
- Agregar manejo de errores por nodo.
- Agregar retry para APIs externas.
- Conectar catalogo e inventario real de Electropatios.
- Conectar Google Sheets o CRM despues de probar el webhook basico.
