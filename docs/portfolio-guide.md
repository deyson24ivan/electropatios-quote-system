# Guia de portafolio

Este documento es para cerrar el proyecto y tener una forma clara de explicarlo. No es un libreto para memorizar. Es una guia para repasar que hice, por que lo hice y que podria mejorar despues.

## Resumen corto

Construi un sistema de automatizacion comercial para Electropatios. La pagina permite armar un pedido de materiales electricos, enviarlo como cotizacion, convertirlo en lead, clasificar prioridad, preparar seguimiento en CRM, simular IA/voz en modo seguro, medir eventos y publicar una demo online con GitHub Pages.

## Demo

Pagina online:

```text
https://deyson24ivan.github.io/electropatios-quote-system/
```

La demo online funciona sin backend publico. Cuando la pagina esta en internet, el formulario guarda una respuesta de prueba en el navegador para que no falle por `localhost`.

En local, el flujo completo usa:

```text
frontend -> n8n -> Flask API -> JSONL/MySQL opcional
```

## Que problema resuelve

Un negocio que recibe pedidos por WhatsApp, llamadas o formularios puede perder informacion facil. Este proyecto organiza ese flujo:

- El cliente arma un pedido.
- El sistema valida datos.
- Se calcula prioridad.
- Se crea un lead.
- Se prepara seguimiento comercial.
- Se deja listo para CRM, Sheets, tracking, email y voz.

## Que aprendi por fase

| Fase | Que aprendi |
| --- | --- |
| 1. Git/GitHub | Repositorio, commits, push, README, `.gitignore` y Git Graph. |
| 2. Webhook + API | HTTP, JSON, Flask, endpoints y respuestas con errores claros. |
| 3. n8n | Webhooks, nodos, condiciones, errores y llamadas HTTP. |
| 4. Lead Automation | Convertir una cotizacion en lead con datos para seguimiento. |
| 5. GoHighLevel | Preparar contacto, oportunidad, tags y pipeline sin enviar datos reales. |
| 6. IA | Clasificar intencion con reglas, usar guardrails y pasar a asesor humano. |
| 7. Voice AI | Simular llamadas desde texto y preparar respuesta telefonica segura. |
| 8. Web local / WordPress | Crear una pagina completa antes de pagar hosting o montar WordPress. |
| 9. Tracking | Medir eventos, conversiones y UTM antes de conectar Analytics real. |
| 10. Email infrastructure | Entender SPF, DKIM, DMARC y entregabilidad en modo seguro. |
| 11. Deploy | Publicar la pagina con GitHub Pages. |
| 12. Portfolio | Ordenar README, docs, mapa de codigo y explicacion para repasar. |

## Como explico la arquitectura

La pagina no guarda todo directamente. Primero arma un JSON con los datos del pedido. n8n recibe ese JSON por webhook y llama mi API. La API valida datos, calcula prioridad, detecta duplicados y guarda la cotizacion. Despues crea un lead y prepara las siguientes partes del flujo: Sheets, CRM, IA segura, voz, tracking y email.

## Que esta terminado

- Pagina web completa de Electropatios.
- Catalogo, filtros, carrito y formulario.
- API Flask con endpoints REST.
- Workflows n8n importables.
- Lead automation.
- GoHighLevel en modo seguro.
- IA en modo seguro.
- Voice AI en modo seguro.
- Tracking local con UTM.
- Plan SPF/DKIM/DMARC.
- Deploy de pagina en GitHub Pages.
- Pruebas automatizadas del backend.

## Que sigue siendo modo seguro

Estas partes estan preparadas, pero no conectadas a servicios reales:

- GoHighLevel real.
- Google Sheets real.
- IA externa.
- Proveedor de telefonia/voz.
- Google Analytics, Tag Manager y Pixel.
- DNS/email real.
- API publica con base de datos cloud.

Lo deje asi a proposito porque primero queria entender el flujo sin gastar dinero ni mandar datos reales.

## Preguntas que me pueden hacer

**Por que separaste la logica en varios archivos?**

Porque `app.py` solo debe recibir HTTP y responder JSON. Las reglas de cotizacion, leads, CRM, IA, voz, tracking y email son cajitas separadas. Asi puedo probarlas mas facil.

**Por que usaste modo seguro?**

Porque antes de conectar cuentas reales queria ver exactamente que datos se enviarian. Eso evita crear contactos falsos, mandar correos de prueba o prometer cosas que no estan confirmadas.

**Que hace n8n aqui?**

n8n orquesta el flujo. Recibe el webhook, valida datos, llama endpoints de la API y conecta pasos como lead, IA, CRM y notificacion.

**Que hace Flask?**

Flask es la API. Recibe JSON, valida, aplica reglas y guarda resultados.

**Que pasa si MySQL no esta prendido?**

La API usa archivos `.jsonl` como respaldo local. Asi no se pierde la solicitud durante pruebas.

**Por que la pagina online usa demo?**

Porque GitHub Pages solo publica archivos estaticos. No ejecuta Flask ni n8n. Por eso online se guarda una respuesta demo en el navegador, y local conserva el flujo completo.

## Como lo mejoraria en un trabajo real

- Subiria la API a Render, Railway o un VPS.
- Usaria una base de datos cloud.
- Conectaria n8n en servidor o n8n Cloud.
- Activaria GoHighLevel con credenciales reales.
- Agregaria Google Sheets o CRM real para seguimiento.
- Conectaria Analytics/Tag Manager.
- Configuraria dominio, DNS, SSL, SPF, DKIM y DMARC reales.
- Agregaria autenticacion para endpoints administrativos.

## Frase final

Este proyecto me sirvio para practicar un flujo completo: pagina, API, automatizacion, CRM, IA segura, voz, tracking, email y deploy. Lo importante no fue solo que funcionara, sino entender que hace cada pieza y como se conectan.
