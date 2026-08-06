# n8n

`quote-workflow.sample.json` es un blueprint inicial para importar y adaptar en n8n.

## Objetivo del workflow

1. Recibir una solicitud de cotizacion por webhook.
2. Validar campos minimos.
3. Enviar el payload a la API local.
4. Separar solicitudes de prioridad alta del resto.
5. Enviar notificacion para solicitudes prioritarias.
6. Guardar respaldo en Google Sheets.

## Pendiente al importarlo

- Cambiar URLs locales por URLs reales.
- Configurar credenciales de Google Sheets.
- Configurar credenciales de email, WhatsApp o Slack.
- Agregar manejo de errores por nodo.
- Agregar retry para APIs externas.
- Conectar catalogo e inventario real de Electropatios.

