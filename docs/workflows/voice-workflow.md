# Workflow de Voice AI

Este workflow practica la Fase 7 sin conectar telefonia real todavia.

Archivo:

```text
n8n/electropatios-voice-workflow.json
```

Webhook local:

```text
POST http://127.0.0.1:5678/webhook/electropatios-voice-call
```

## Cajas del workflow

| Caja | Que hace |
| --- | --- |
| Webhook Electropatios Voice | Recibe una llamada simulada como JSON. |
| Validate Voice Call | Revisa que exista transcripcion. |
| Is Valid Voice Call? | Decide si sigue o responde error. |
| Send To Voice API | Manda la llamada a `POST /api/voice/intake`. |
| Needs Human Handoff? | Revisa si debe pasar a asesor humano. |
| Prepare Voice Notification | Arma el mensaje interno para el asesor. |
| Save Voice Notification | Guarda la notificacion preparada. |
| Success Voice Response | Devuelve la respuesta del agente telefonico. |

## Ejemplo de prueba

```json
{
  "caller_name": "Carlos Ramirez",
  "phone": "+57 301 222 3344",
  "delivery_city": "Los Patios",
  "transcript": "Necesito 120 metros de cable THHN para hoy."
}
```

## Que aprendi en esta fase

- Una llamada puede convertirse en JSON igual que un formulario.
- La transcripcion es el texto que el sistema usa para entender al cliente.
- Un agente de voz no debe inventar precios, stock, entregas ni consejos tecnicos.
- El handoff humano es importante cuando falta confirmar informacion.
