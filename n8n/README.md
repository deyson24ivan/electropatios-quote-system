# n8n

`electropatios-order-workflow.json` es un workflow inicial para importar y adaptar en n8n.

Ruta activa probada en local:

```text
POST http://127.0.0.1:5678/webhook/electropatios-order
```

## Objetivo del workflow

1. Recibir un pedido desde la pagina de Electropatios por webhook.
2. Validar campos minimos.
3. Enviar el payload a la API local.
4. Separar solicitudes de prioridad alta del resto.
5. Preparar mensaje para el asesor cuando sea prioridad alta.
6. Responder al formulario o prueba manual.

## Pendiente al importarlo

- Cambiar URLs locales por URLs reales.
- Activar el workflow cuando ya este probado.
- Configurar credenciales de Google Sheets.
- Configurar credenciales de email, WhatsApp o Slack.
- Agregar manejo de errores por nodo.
- Agregar retry para APIs externas.
- Conectar catalogo e inventario real de Electropatios.
- Conectar Google Sheets o CRM despues de probar el webhook basico.
