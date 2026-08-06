# Guia GoHighLevel en modo seguro

Esta guia cubre la Fase 5 en modo seguro. Todavia no enviamos datos reales a GoHighLevel. Primero preparamos y revisamos lo que el sistema mandaria.

## Que problema resuelve

Cuando un cliente pide una cotizacion en Electropatios, no basta con guardar el pedido. En un CRM necesitamos:

- Un contacto con nombre, telefono y email.
- Una oportunidad comercial dentro de un pipeline.
- Tags para filtrar o activar automatizaciones.
- Una etapa clara para saber que hacer despues.

## Flujo actual

```text
Pagina Electropatios
  -> n8n
  -> API /api/quotes
  -> API /api/leads
  -> API /api/crm/sync
  -> CRM preparado en modo seguro
```

## Que significa modo seguro

Modo seguro significa:

- El sistema arma el contacto.
- El sistema arma la oportunidad.
- El sistema muestra los endpoints y datos que usaria.
- El sistema guarda un registro local del intento.
- No envia nada real a GoHighLevel.

Esto evita llenar una cuenta real con pruebas mientras estamos aprendiendo.

## Archivos importantes

| Archivo | Para que sirve |
| --- | --- |
| `backend/ghl_logic.py` | Prepara contacto, oportunidad, tags y etapa CRM. |
| `backend/app.py` | Expone `POST /api/crm/sync`. |
| `backend/tests/test_ghl_logic.py` | Prueba que el modo seguro no envie datos reales. |
| `database/schema.sql` | Agrega la tabla `crm_sync_attempts`. |
| `.env.example` | Muestra las variables que haran falta cuando usemos GoHighLevel real. |
| `n8n/electropatios-order-workflow.json` | Agrega la cajita `Sync CRM Safe Mode`. |

## Variables de entorno

Mientras estamos aprendiendo queda asi:

```text
GHL_ENABLED=false
```

Cuando tengamos una cuenta, token e IDs reales revisados, se llenaran estas variables:

```text
GHL_PRIVATE_TOKEN=
GHL_LOCATION_ID=
GHL_PIPELINE_ID=
GHL_STAGE_HIGH=
GHL_STAGE_MEDIUM=
GHL_STAGE_LOW=
GHL_ASSIGNED_USER_ID=
```

No pongas tokens reales en GitHub. Los tokens van solo en `.env`, no en `.env.example`.

## Contacto preparado

El contacto usa `contacts/upsert`. Eso significa: si el contacto ya existe por email o telefono, GoHighLevel puede actualizarlo en vez de crear otro igual.

Ejemplo:

```json
{
  "firstName": "Carlos",
  "lastName": "Ramirez",
  "name": "Carlos Ramirez",
  "email": "carlos@example.com",
  "phone": "+573012223344",
  "locationId": "<GHL_LOCATION_ID>",
  "tags": [
    "electropatios",
    "cotizacion",
    "prioridad_high",
    "categoria_tuberia"
  ]
}
```

## Oportunidad preparada

La oportunidad representa la venta posible.

Ejemplo:

```json
{
  "pipelineId": "<GHL_PIPELINE_ID>",
  "locationId": "<GHL_LOCATION_ID>",
  "name": "Cotizacion Electropatios - Carlos Ramirez",
  "pipelineStageId": "<GHL_STAGE_HIGH>",
  "status": "open",
  "contactId": "<CONTACT_ID_FROM_UPSERT>",
  "monetaryValue": 1800000
}
```

## Etapas del pipeline

| Prioridad del lead | Etapa CRM preparada |
| --- | --- |
| `high` | `Contactar hoy` |
| `medium` | `Revisar y cotizar` |
| `low` | `Nutrir o asesorar` |

## Como revisar los intentos

El endpoint que prepara CRM es:

```text
POST http://localhost:5000/api/crm/sync
```

Los intentos guardados localmente se revisan con:

```text
GET http://localhost:5000/api/crm/syncs
```

## Como lo explicaria en entrevista

Prepare una integracion segura con GoHighLevel antes de conectar credenciales reales. La API arma el contacto con estrategia de upsert para evitar duplicados, prepara la oportunidad con pipeline y stage segun prioridad, guarda el intento de sincronizacion y deja visibles las variables necesarias para activar el envio real despues.

## Fuentes oficiales revisadas

- HighLevel API Documentation: `https://help.gohighlevel.com/support/solutions/articles/48001060529-highlevel-api`
- Contacts API v3: `https://marketplace.gohighlevel.com/docs/ghl/contacts/contacts-api-v-3/`
- Upsert Contact: `https://marketplace.gohighlevel.com/docs/ghl/contacts/upsert-contact/`
- Opportunities API v3: `https://marketplace.gohighlevel.com/docs/ghl/opportunities/opportunities-api-v-3/`
