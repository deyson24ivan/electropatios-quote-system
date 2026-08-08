# Mapa del codigo

Este archivo lo uso para repasar el proyecto sin perderme. La idea es saber que hace cada carpeta y poder explicarlo en una entrevista sin abrir todos los archivos al tiempo.

## Vista rapida

El proyecto tiene cuatro partes principales:

- `frontend/`: la pagina que ve el cliente.
- `backend/`: la API en Python que valida, clasifica y guarda datos.
- `n8n/`: workflows que conectan formularios, API y automatizaciones.
- `docs/`: mis notas para explicar arquitectura, fases y decisiones.

## Raiz del proyecto

| Archivo | Que hace |
| --- | --- |
| `index.html` | Entrada para GitHub Pages. Abre automaticamente `frontend/`. |
| `.nojekyll` | Evita que GitHub Pages procese el sitio como Jekyll. |
| `.env.example` | Muestra variables de entorno sin guardar secretos reales. |
| `.gitignore` | Evita subir `.env`, entorno virtual, datos locales y cache. |
| `requirements.txt` | Dependencias de Python: Flask y MySQL connector. |
| `README.md` | Resumen principal del proyecto para portafolio. |

## Frontend

| Archivo | Que hace |
| --- | --- |
| `frontend/index.html` | Estructura de la pagina: inicio, catalogo, carrito, formulario, servicios, FAQ y contacto. |
| `frontend/style.css` | Diseno visual, colores, grillas, tarjetas, responsive y panel del carrito. |
| `frontend/script.js` | Logica de la tienda: productos, filtros, carrito, formulario, envio local y modo demo online. |
| `frontend/tracking.js` | Tracking local: page view, busquedas, productos agregados, intentos y conversiones. |

Lo mas importante del frontend:

- El catalogo vive en `script.js` como una lista de productos.
- El carrito se guarda en `localStorage` para no perderlo al recargar.
- En mi PC el formulario usa n8n/API.
- En GitHub Pages usa modo demo para que la pagina online funcione sin backend publico.

## Backend

| Archivo | Que hace |
| --- | --- |
| `backend/app.py` | Servidor Flask. Define rutas, CORS, guardado local, guardado MySQL y endpoints. |
| `backend/quote_logic.py` | Limpia datos del formulario, valida campos, calcula prioridad y detecta duplicados. |
| `backend/lead_logic.py` | Convierte una cotizacion en lead, fila para Sheets, payload CRM y mensaje al asesor. |
| `backend/ghl_logic.py` | Prepara contacto y oportunidad para GoHighLevel en modo seguro. |
| `backend/ai_logic.py` | Clasifica intencion, categoria, guardrails y respuesta segura sin IA externa. |
| `backend/voice_logic.py` | Simula Voice AI usando transcripciones, preguntas faltantes y handoff humano. |
| `backend/tracking_logic.py` | Valida eventos de tracking y limpia datos UTM. |
| `backend/email_logic.py` | Prepara plan SPF, DKIM y DMARC sin tocar DNS reales. |

La idea que segui en el backend fue separar responsabilidades:

- Flask recibe HTTP y responde JSON.
- Las reglas de negocio viven en archivos aparte.
- Las pruebas llaman esas reglas directamente.
- Si MySQL falla, se guarda respaldo local en `backend/data`.

## Tests

| Archivo | Que revisa |
| --- | --- |
| `backend/tests/test_quote_logic.py` | Validacion, prioridad y duplicados de cotizaciones. |
| `backend/tests/test_lead_logic.py` | Creacion de lead, fila para Sheets y mensaje al asesor. |
| `backend/tests/test_ghl_logic.py` | Que GoHighLevel quede en modo seguro y sin envio real. |
| `backend/tests/test_ai_logic.py` | Clasificacion, guardrails y human handoff. |
| `backend/tests/test_voice_logic.py` | Transcripciones, respuesta telefonica y paso a asesor. |
| `backend/tests/test_tracking_logic.py` | Eventos permitidos y limpieza de UTM. |
| `backend/tests/test_email_logic.py` | Dominio, SPF, DKIM, DMARC y volumen alto. |

Comando que uso para correr todo:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s backend\tests -p "test_*.py"
```

## Base de datos

| Archivo | Que hace |
| --- | --- |
| `database/schema.sql` | Define las tablas MySQL para cotizaciones, leads, CRM, IA, llamadas, tracking, email y errores. |

En esta version MySQL es opcional. Si no esta configurado, la API guarda en archivos `.jsonl` locales. Eso me permite practicar sin depender de una base prendida todo el tiempo.

## n8n

| Archivo | Que hace |
| --- | --- |
| `n8n/electropatios-order-workflow.json` | Workflow del pedido web: webhook, validacion, API, lead, IA, CRM y notificacion. |
| `n8n/electropatios-voice-workflow.json` | Workflow para probar una llamada simulada desde transcripcion. |
| `n8n/README.md` | Como importar, probar y entender los workflows. |

n8n es el orquestador. No reemplaza la API; la conecta con pasos de automatizacion.

## Examples

| Carpeta | Que hace |
| --- | --- |
| `examples/requests/` | JSONs de prueba para mandar pedidos, tracking, voz y email desde PowerShell o n8n. |

Estos ejemplos me sirven para probar sin llenar formularios cada vez.

## Docs

| Archivo | Que hace |
| --- | --- |
| `docs/architecture.md` | Diagrama y reglas principales del sistema. |
| `docs/api-guide.md` | Endpoints, ejemplos JSON y pruebas desde PowerShell. |
| `docs/learning-roadmap.md` | Estado de las 12 fases. |
| `docs/portfolio-guide.md` | Como presento el proyecto y que digo en entrevista. |
| `docs/code-walkthrough.md` | Este mapa de codigo para repasar archivo por archivo. |

## Flujo completo en una frase

La pagina recibe un pedido de materiales electricos, n8n lo manda a Flask, Flask valida y guarda la cotizacion, despues crea un lead, clasifica el caso, prepara CRM, tracking, voz y email en modo seguro, y la version visible queda publicada en GitHub Pages.
