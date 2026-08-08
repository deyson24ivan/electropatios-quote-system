# Guia de Lead Automation

Esta guia cubre la Fase 4 del proyecto. La idea es que un pedido de la pagina no quede solo como una cotizacion, sino como un lead comercial que se pueda seguir en una hoja, en un CRM o con un asesor.

## Que hace esta fase

Flujo actual:

```text
Pagina Electropatios
  -> Webhook n8n
  -> API /api/quotes
  -> API /api/leads
  -> Fila preparada para Google Sheets
  -> Payload preparado para GoHighLevel
  -> Notificacion interna si el lead es urgente
```

En palabras simples: el cliente arma un pedido, el sistema lo guarda, calcula la prioridad y prepara la informacion para que alguien de Electropatios pueda hacer seguimiento.

## Archivos importantes

| Archivo | Para que sirve |
| --- | --- |
| `backend/lead_logic.py` | Convierte una cotizacion en lead comercial. |
| `backend/app.py` | Expone los endpoints `/api/leads` y `/api/notifications`. |
| `database/schema.sql` | Tiene las tablas `lead_records` y `advisor_notifications`. |
| `n8n/electropatios-order-workflow.json` | Workflow que conecta cotizacion, lead y notificacion. |
| `backend/tests/test_lead_logic.py` | Pruebas para confirmar que el lead se arma bien. |

## Que es un lead en este proyecto

Un lead es una persona o empresa que mostro interes real en comprar. En Electropatios seria alguien que pidio cable, lamparas, conectores, tuberia u otro producto y dejo datos de contacto.

Ejemplo de datos importantes del lead:

```json
{
  "full_name": "Ana Perez",
  "phone": "+573001234567",
  "email": "ana@example.com",
  "products_summary": "150 metro - Cable THHN #12",
  "priority": "high",
  "pipeline_stage": "contactar_hoy",
  "follow_up_status": "pendiente"
}
```

## Reglas comerciales

El lead queda en una etapa segun su prioridad:

| Prioridad | Etapa | Significado |
| --- | --- | --- |
| `high` | `contactar_hoy` | Hay que llamarlo rapido. |
| `medium` | `revisar_y_cotizar` | Conviene revisar disponibilidad y precio. |
| `low` | `nutrir_o_asesorar` | Puede necesitar asesoria antes de comprar. |

## Salida para Google Sheets

Todavia no conectamos una hoja real. Lo que hicimos fue dejar lista la fila que despues se manda a Google Sheets desde n8n.

Ejemplo:

```json
{
  "fecha": "2026-08-06T02:46:16+00:00",
  "lead_id": "...",
  "quote_id": "...",
  "nombre": "Ana Perez",
  "telefono": "+573001234567",
  "productos": "150 metro - Cable THHN #12",
  "prioridad": "high",
  "etapa": "contactar_hoy"
}
```

## Salida para GoHighLevel

En esta fase tambien deje preparado el formato que despues conecte con GoHighLevel en modo seguro:

- `contact`: datos de la persona.
- `opportunity`: oportunidad comercial dentro de un pipeline.
- `tags`: etiquetas para filtrar o disparar automatizaciones.

Ejemplo de tags:

```json
[
  "electropatios",
  "cotizacion",
  "prioridad_high",
  "categoria_cable",
  "cliente_negocio",
  "urgente"
]
```

## Notificacion al asesor

Si el lead es prioridad alta, n8n prepara una notificacion y la guarda en:

```text
POST /api/notifications
```

En esta fase no enviamos WhatsApp real ni email real. Primero dejamos el mensaje preparado y probado para no depender de herramientas externas.

## Como lo explicaria en entrevista

Construi una automatizacion donde una solicitud web se convierte en una cotizacion validada y despues en un lead comercial. El sistema prepara una fila para Google Sheets, una estructura compatible con CRM y una notificacion interna cuando la prioridad es alta. Use n8n para orquestar el flujo y Python para mantener reglas claras y probadas con pruebas automatizadas.
