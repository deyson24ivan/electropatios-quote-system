# Arquitectura

Este proyecto esta disenado como una plataforma de cotizaciones para Electropatios. La primera version funciona con una pagina web y una API local; las siguientes fases conectan n8n, MySQL, Google Sheets, CRM, email e IA.

## Flujo principal

```mermaid
flowchart TD
  A["Cliente entra a la pagina"] --> B["Solicita cotizacion o asesoria"]
  B --> C["POST /api/quotes"]
  C --> D{"Datos validos?"}
  D -- "No" --> E["Respuesta 400 con errores"]
  D -- "Si" --> F{"Solicitud repetida?"}
  F -- "Si" --> G["Retorna solicitud existente"]
  F -- "No" --> H["Guarda en MySQL"]
  H --> I{"MySQL disponible?"}
  I -- "No" --> J["Respaldo local JSONL"]
  I -- "Si" --> K["Evento quote_request_created"]
  J --> L["Prioridad high/medium/low"]
  K --> L
  L --> M["n8n continua el flujo"]
  M --> N["CRM / Sheets / Email / Notificacion"]
```

## Contrato de datos

```json
{
  "full_name": "Ana Perez",
  "email": "ana@example.com",
  "phone": "+573001234567",
  "customer_type": "empresa",
  "company_name": "Proyecto Norte",
  "request_type": "quote",
  "product_category": "cable",
  "quantity": 150,
  "unit": "metro",
  "budget_cop": 2500000,
  "urgency": "hoy",
  "delivery_city": "Cucuta",
  "notes": "Necesito cable #12 y disponibilidad para hoy",
  "consent": true
}
```

## Reglas iniciales

- Validar nombre, email, telefono, categoria de producto, cantidad para cotizaciones y consentimiento.
- Permitir que un mismo cliente haga varias cotizaciones distintas.
- Detectar repetidos por huella de solicitud: cliente, categoria, cantidad, unidad, ciudad y detalle.
- Clasificar como `high` si hay urgencia, volumen alto, presupuesto alto o cliente empresarial.
- Clasificar como `medium` si hay potencial comercial pero falta confirmar precio, disponibilidad o entrega.
- Clasificar como `low` si es una pregunta inicial que requiere asesoria o seguimiento posterior.
- Si MySQL falla, guardar respaldo local y registrar el error.

## Catalogo base

La API expone `GET /api/catalog` con categorias iniciales:

- Lamparas.
- Conectores.
- Cable.
- Tuberia.
- Breakers, tableros, tomacorrientes e interruptores.
- Herramientas y accesorios.

## Guardrails para IA

Cuando agreguemos el agente IA, no debe inventar precios, disponibilidad o marcas. Debe responder solo con informacion disponible en catalogo, inventario o reglas cargadas.

Si el cliente pregunta algo que no esta documentado, la respuesta esperada es:

> No tengo esa informacion confirmada. Puedo registrar la pregunta para que un asesor de Electropatios la revise.

Esta regla es importante para explicar en entrevista como se reducen alucinaciones.

