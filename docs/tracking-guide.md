# Guia de tracking

Esta fase mide que hace el cliente en la pagina de Electropatios sin conectar herramientas externas todavia.

## Que es tracking

Tracking es guardar eventos importantes de la pagina para entender que esta pasando.

Ejemplos:

- El cliente entro a la pagina.
- Busco un producto.
- Filtro una categoria.
- Agrego un producto al pedido.
- Abrio el carrito.
- Envio una cotizacion.
- El envio salio bien o fallo.

## Que hicimos en local

Agregamos:

```text
frontend/tracking.js
POST /api/tracking/events
GET /api/tracking/events
backend/data/tracking_events.jsonl
```

La pagina manda eventos a la API. Si la API esta apagada, los guarda en el navegador y los intenta enviar despues.

## Que es UTM

UTM son parametros que se agregan al link para saber de donde viene un cliente.

Ejemplo:

```text
frontend/index.html?utm_source=facebook&utm_medium=paid_social&utm_campaign=cables_agosto
```

Significa:

- `utm_source`: de donde vino, por ejemplo Facebook, Google o WhatsApp.
- `utm_medium`: tipo de canal, por ejemplo pago, organico o referido.
- `utm_campaign`: nombre de la campana.
- `utm_term`: palabra clave si aplica.
- `utm_content`: variante del anuncio o boton.

## Que es Analytics

Analytics es una herramienta para ver reportes: visitas, fuentes, paginas, eventos y conversiones.

Ejemplo real futuro: Google Analytics 4.

## Que es Tag Manager

Tag Manager sirve para manejar codigos de medicion sin editar tanto la pagina.

Ejemplo real futuro: Google Tag Manager.

## Que es Pixel

Un pixel es un codigo de seguimiento de una plataforma de anuncios.

Ejemplo real futuro: Meta Pixel para Facebook e Instagram Ads.

## Que es conversion

Una conversion es una accion valiosa para el negocio.

En Electropatios, la conversion principal es:

```text
quote_submit_success
```

Eso significa que una cotizacion fue enviada correctamente.

## Eventos que mide la pagina

| Evento | Que significa |
| --- | --- |
| `page_view` | El cliente entro a la pagina. |
| `catalog_search` | Busco algo en el catalogo. |
| `category_filter` | Filtro o eligio una categoria. |
| `product_add` | Agrego un producto al pedido. |
| `cart_open` | Abrio el resumen del pedido. |
| `cart_clear` | Vacio el pedido. |
| `quote_submit_attempt` | Intento enviar cotizacion. |
| `quote_submit_success` | La cotizacion se envio bien. |
| `quote_submit_error` | La cotizacion fallo o faltaron datos. |

## Como probar

Con la API corriendo:

```powershell
$body = Get-Content -Raw "examples/requests/tracking-product-add.json"
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/tracking/events" -Method Post -ContentType "application/json" -Body $body
```

Para ver eventos guardados:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/tracking/events"
```

## Como lo explicaria en entrevista

Implemente tracking local antes de conectar herramientas externas. La pagina captura eventos de comportamiento, lee parametros UTM, envia los eventos a mi API y guarda conversiones como `quote_submit_success`. Esto deja listo el camino para conectar despues Google Analytics 4, Google Tag Manager y Meta Pixel con una estructura ya probada.
