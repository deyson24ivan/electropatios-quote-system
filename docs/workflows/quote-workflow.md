# Workflow de cotizaciones

## Version 1

1. La pagina de Electropatios envia una solicitud por POST.
2. La API valida datos basicos.
3. La API detecta solicitudes repetidas sin bloquear nuevas cotizaciones del mismo cliente.
4. La API guarda en MySQL si esta disponible.
5. Si MySQL falla, guarda respaldo local.
6. La API clasifica la solicitud por prioridad comercial.
7. n8n puede continuar el flujo con hojas, correo, CRM o WhatsApp.

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
- Enviar notificacion para solicitudes prioritarias.
- Sincronizar solicitudes con Google Sheets.
- Crear pipeline CRM con estados: nueva, revisada, cotizada, ganada y perdida.
- Agregar agente IA que responda preguntas sin inventar precios ni disponibilidad.

