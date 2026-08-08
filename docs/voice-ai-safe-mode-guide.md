# Guia Voice AI en modo seguro

Esta fase simula un agente telefonico para Electropatios.

No hace llamadas reales todavia. Recibe una transcripcion escrita y responde como si el sistema hubiera escuchado una llamada.

## Para que sirve

Sirve para practicar la base de Voice AI:

- Entender una llamada como datos.
- Detectar que quiere el cliente.
- Identificar producto, cantidad y urgencia.
- Preparar una respuesta corta para telefono.
- Pasar a asesor humano cuando hace falta confirmar algo.

## Endpoint principal

```text
POST http://localhost:5000/api/voice/intake
```

Ejemplo:

```json
{
  "caller_name": "Carlos Ramirez",
  "phone": "+57 301 222 3344",
  "delivery_city": "Los Patios",
  "transcript": "Necesito 120 metros de cable THHN para hoy."
}
```

## Que hace la API

1. Limpia el texto de la llamada.
2. Detecta si es cotizacion, disponibilidad, pregunta de producto o tema tecnico.
3. Detecta categoria: cable, lamparas, tuberia, conectores, proteccion u otros.
4. Busca cantidad y unidad cuando el cliente las dice.
5. Calcula prioridad.
6. Aplica guardrails.
7. Prepara la respuesta que diria el agente.
8. Guarda el caso en `backend/data/voice_calls.jsonl` si MySQL no esta conectado.

## Guardrails

El agente no debe:

- Inventar precios.
- Confirmar stock.
- Prometer entregas.
- Dar instrucciones electricas peligrosas.
- Reemplazar al asesor cuando el caso necesita revision.

## Que significa handoff

`handoff_required: true` significa que el sistema debe pasar el caso a una persona.

Ejemplos:

- El cliente pide precio o disponibilidad.
- La llamada es urgente.
- El cliente pregunta algo tecnico.
- Faltan datos importantes.

## Workflow de n8n

El archivo es:

```text
n8n/electropatios-voice-workflow.json
```

Ese workflow recibe la llamada por webhook, llama a la API y guarda una notificacion interna si se necesita asesor.

## Como lo explicaria en entrevista

Construí un prototipo seguro de Voice AI para Electropatios. En vez de conectar telefonia real desde el primer dia, primero modele el flujo con transcripciones: recibo la llamada como JSON, clasifico intencion, producto, cantidad y urgencia, preparo una respuesta telefonica segura y paso el caso a un asesor cuando hay precio, disponibilidad o asesoria tecnica por confirmar.
