# Ruta de aprendizaje

El objetivo no es aprender veinte herramientas al tiempo. La idea es construir un solo proyecto realista de Electropatios y que cada fase deje una evidencia clara para portafolio.

## Estado actual

| Fase | Estado | Evidencia |
| --- | --- | --- |
| Fase 1 - Git/GitHub | Lista | Repositorio privado, commits, README y `.gitignore`. |
| Fase 2 - Webhook + API | Lista | API Flask con `GET /health`, `GET /api/catalog` y `POST /api/quotes`. |
| Fase 3 - n8n | Lista | Workflow activo para recibir pedidos, validar datos y llamar la API. |
| Fase 4 - Lead Automation | Lista | Formulario -> n8n -> lead -> fila para Sheets -> notificacion interna. |
| Fase 5 - CRM / GoHighLevel | Lista en modo seguro | Contacto, oportunidad, tags, pipeline y validacion sin enviar datos reales. |
| Fase 6 - IA | Lista en modo seguro | Clasificacion, prompts, guardrails y paso a asesor humano sin modelo externo. |
| Fase 7 - Voice AI | Lista en modo seguro | Agente telefonico simulado con transcripcion, clasificacion, respuesta segura y handoff. |
| Fase 8 - WordPress + hosting | Lista version local | Pagina local completa; pendiente WordPress real, dominio, DNS y SSL. |
| Fase 9 - Tracking | Lista en modo local | Eventos, conversiones y UTM sin conectar herramientas externas. |
| Fase 10 - Email infrastructure | Pendiente | SPF, DKIM, DMARC y entregabilidad. |
| Fase 11 - Deploy | Pendiente | API y pagina publicadas online. |
| Fase 12 - Portfolio | Pendiente | README final, diagramas, capturas y demo. |

## Fase 1 - Git/GitHub

Aprendi a tener el proyecto ordenado, hacer commits, conectar con GitHub y subir una version que se pueda mostrar.

Herramientas: Git, GitHub, Markdown.

## Fase 2 - Webhook + API

Aprendi HTTP y JSON usando una API real: la pagina arma un pedido, lo manda por `POST` y la API responde si todo esta bien.

Herramientas: HTML, CSS, JavaScript, Python, Flask, HTTP, JSON.

## Fase 3 - n8n

Aprendi a usar n8n como orquestador. n8n recibe el pedido por webhook, valida campos, llama la API y deja el camino listo para notificaciones o Google Sheets.

Herramientas: n8n, webhooks, nodo HTTP, nodo IF, manejo basico de errores.

## Fase 4 - Lead Automation

Aprendi a convertir una cotizacion en un lead comercial. El sistema prepara datos para seguimiento, una fila para Google Sheets, una estructura para GoHighLevel y una notificacion interna cuando la prioridad es alta.

Herramientas: Python, Flask, n8n, MySQL, JSON, reglas comerciales, pruebas automatizadas.

## Fase 5 - CRM / GoHighLevel

Aprendi a preparar una integracion CRM sin tocar una cuenta real. El sistema arma el contacto, prepara la oportunidad, asigna etapa segun prioridad y guarda un intento de sincronizacion para revisar que se enviaria.

Herramientas: GoHighLevel, CRM, pipelines, oportunidades, tags, variables de entorno, modo seguro.

## Fase 6 - IA

Aprendi a usar IA de forma responsable dentro de una automatizacion. El sistema clasifica la intencion del cliente, detecta categoria de producto, aplica guardrails y prepara una respuesta segura con paso a asesor humano cuando hace falta.

Herramientas: IA, prompts, clasificacion, guardrails, human handoff, n8n, pruebas automatizadas.

## Fase 7 - Voice AI

Aprendi la base de un agente telefonico sin conectar llamadas reales todavia. El sistema recibe una transcripcion, detecta intencion, producto, cantidad y urgencia, prepara una respuesta para telefono y deja un resumen para que un asesor continue.

Herramientas: Voice AI, transcripciones, n8n, API REST, guardrails, human handoff, pruebas automatizadas.

## Fase 8 - WordPress + hosting

Aprendi primero la parte local de una pagina tipo negocio real. La pagina tiene inicio, catalogo, filtros, carrito de cotizacion, formulario, servicios, preguntas frecuentes y contacto. Todavia no pagamos hosting ni dominio; primero dejamos clara la experiencia antes de migrarla a WordPress real.

Herramientas: HTML, CSS, JavaScript, estructura de landing, formulario comercial, n8n, conceptos de WordPress, hosting, dominio, DNS y SSL.

## Fase 9 - Tracking

Aprendi a medir eventos importantes de la pagina sin conectar Google Analytics, Tag Manager o Meta Pixel todavia. La pagina lee parametros UTM, crea una sesion local, guarda eventos de comportamiento y marca la conversion principal cuando una cotizacion se envia bien.

Herramientas: eventos, conversiones, UTM, tracking local, JavaScript, API REST, conceptos de Google Analytics, Tag Manager y Pixel.
