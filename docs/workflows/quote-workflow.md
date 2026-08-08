# Workflow de cotizaciones

## Version 1

1. La pagina de Electropatios envia una solicitud por POST.
2. La API valida datos basicos.
3. La API detecta solicitudes repetidas sin bloquear nuevas cotizaciones del mismo cliente.
4. La API guarda en MySQL si esta disponible.
5. Si MySQL falla, guarda respaldo local.
6. La API clasifica la solicitud por prioridad comercial.
7. n8n puede continuar el flujo con hojas, correo, CRM o WhatsApp.

## Version 2 con n8n

1. La pagina puede enviar el pedido al webhook `electropatios-order`.
2. n8n revisa que el pedido tenga nombre, email, telefono, consentimiento y productos.
3. Si faltan datos, n8n responde un error claro.
4. Si el pedido esta completo, n8n llama a `POST /api/quotes`.
5. La API guarda y clasifica la solicitud.
6. n8n revisa si la prioridad es alta.
7. Si es alta, n8n deja preparado el mensaje para el asesor.
8. n8n responde a la pagina con el resultado de la cotizacion.

## Version 3 con lead automation

1. n8n recibe el pedido desde la pagina principal de Electropatios.
2. n8n valida campos minimos y llama a `POST /api/quotes`.
3. La API guarda la cotizacion y calcula prioridad.
4. n8n llama a `POST /api/leads`.
5. La API crea un lead con etapa comercial, tags y resumen de productos.
6. n8n prepara la fila que puede ir a Google Sheets.
7. n8n deja listo el payload que use para GoHighLevel en modo seguro.
8. Si el lead es urgente, n8n guarda una notificacion interna para el asesor.
9. La pagina recibe una respuesta con `quote_id`, `lead_id`, prioridad y estado.

## Version 4 con CRM en modo seguro

1. n8n recibe el lead creado por la API.
2. n8n llama a `POST /api/crm/sync`.
3. La API prepara el contacto de GoHighLevel usando estrategia `upsert`.
4. La API prepara la oportunidad con pipeline, stage, estado `open` y valor estimado.
5. La API guarda el intento CRM en modo seguro.
6. El flujo responde con `crm_sync.mode = safe_mode` y `will_send_to_crm = false`.

## Version 5 con IA en modo seguro

1. n8n recibe el lead creado por la API.
2. n8n llama a `POST /api/ai/classify`.
3. La API detecta intencion, categoria, confianza y guardrails.
4. La API prepara una respuesta segura sin llamar IA externa.
5. La API decide si el caso requiere handoff humano.
6. n8n continua hacia Sheets, CRM seguro y notificacion.

## Casos de error que quiero practicar

- Email invalido.
- Telefono incompleto.
- Categoria de producto vacia.
- Cotizacion sin cantidad.
- Solicitud repetida.
- MySQL desconectado.
- Timeout de API.
- Payload incompleto desde webhook.
- Nodo de IA sin respuesta.
- Error al escribir en Google Sheets.

## Mejoras siguientes

- Agregar precios reales o rangos de precios por producto.
- Sincronizar catalogo e inventario desde una hoja de calculo.
- Conectar el nodo real de Google Sheets.
- Conectar GoHighLevel real cuando tengamos credenciales y IDs confirmados.
- Conectar IA real usando el prompt pack y guardrails ya probados.
- Crear pipeline CRM con estados: nueva, revisada, cotizada, ganada y perdida.
- Agregar agente IA que responda preguntas sin inventar precios ni disponibilidad.
