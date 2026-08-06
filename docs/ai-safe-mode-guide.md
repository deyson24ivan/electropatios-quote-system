# Guia de IA en modo seguro

Esta guia cubre la Fase 6. La idea no es poner una IA a inventar respuestas, sino crear una capa segura que clasifique mensajes, prepare respuestas responsables y sepa cuando pasar a un asesor humano.

## Que hace esta fase

Flujo actual:

```text
Pagina Electropatios
  -> n8n
  -> API /api/quotes
  -> API /api/leads
  -> API /api/ai/classify
  -> API /api/crm/sync
  -> Notificacion si aplica
```

La IA entra despues de crear el lead. Asi ya tiene datos del cliente, productos, prioridad y notas.

## Que significa modo seguro

Modo seguro significa:

- No llama a OpenAI ni a ningun modelo externo.
- Usa reglas locales para aprender el flujo.
- No inventa precios.
- No inventa disponibilidad.
- No promete tiempos de entrega.
- No da instrucciones electricas peligrosas.
- Prepara una respuesta segura.
- Decide si debe pasar a un asesor humano.

## Archivos importantes

| Archivo | Para que sirve |
| --- | --- |
| `backend/ai_logic.py` | Clasifica intencion, categoria, guardrails y handoff. |
| `backend/app.py` | Expone `/api/ai/classify`, `/api/ai/assist` y `/api/ai/analyses`. |
| `backend/tests/test_ai_logic.py` | Prueba que la IA no llame modelos externos ni prometa cosas riesgosas. |
| `database/schema.sql` | Agrega la tabla `ai_safe_analyses`. |
| `n8n/electropatios-order-workflow.json` | Agrega la cajita `AI Classify Safe Mode`. |

## Conceptos que se practican

| Concepto | Significado en este proyecto |
| --- | --- |
| Intencion | Que quiere el cliente: cotizar, preguntar, pedir disponibilidad o asesoria tecnica. |
| Categoria | Producto principal: cable, lamparas, tuberia, conectores, proteccion u otros. |
| Guardrails | Reglas para evitar respuestas peligrosas o inventadas. |
| Handoff humano | Pasar el caso a un asesor cuando no conviene automatizar. |
| Prompt pack | Plantilla de instrucciones que despues puede usarse con IA real. |

## Ejemplo de respuesta

```json
{
  "mode": "safe_mode",
  "status": "safe_reply_prepared",
  "will_call_ai_model": false,
  "intent": "quote",
  "category": "cable",
  "confidence": "high",
  "guardrails": [
    "no_confirmar_price",
    "no_confirmar_delivery"
  ],
  "handoff_required": true,
  "safe_reply": "Gracias. Recibimos tu solicitud de cotizacion para Electropatios. Un asesor revisara precio, disponibilidad y tiempo de entrega antes de confirmarte."
}
```

## Por que casi siempre pasa a asesor

En un negocio real, una IA puede ayudar a ordenar, pero no debe confirmar cosas que cambian todos los dias:

- precios
- stock
- marcas disponibles
- tiempos de entrega
- recomendaciones tecnicas de instalacion

Por eso la IA prepara una respuesta segura y deja claro cuando un asesor debe revisar.

## Endpoints

Clasificar un mensaje:

```text
POST http://localhost:5000/api/ai/classify
```

Preparar una respuesta segura:

```text
POST http://localhost:5000/api/ai/assist
```

Listar analisis guardados:

```text
GET http://localhost:5000/api/ai/analyses
```

## Prompt pack

Aunque no usamos IA externa todavia, el sistema ya prepara una base de prompt:

```json
{
  "system_prompt": "Eres un asistente de Electropatios. Ayudas con productos electricos, pero no inventas precios, stock, entregas ni instrucciones peligrosas.",
  "rules": [
    "No inventar precios.",
    "No inventar disponibilidad.",
    "No prometer tiempos de entrega.",
    "No dar instrucciones electricas peligrosas.",
    "Pasar a asesor cuando falte informacion confirmada."
  ]
}
```

Esto sirve para que despues, cuando conectemos IA real, no empecemos desde cero.

## Como lo explicaria en entrevista

Implemente una capa de IA en modo seguro que clasifica intencion, categoria de producto, nivel de confianza y necesidad de handoff humano. Antes de conectar un modelo externo, defini guardrails para evitar que el sistema invente precios, stock, entregas o recomendaciones electricas peligrosas. n8n usa esta clasificacion dentro del flujo comercial antes del CRM.
