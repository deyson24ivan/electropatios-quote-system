# Guia pagina web local y WordPress

Esta fase deja una pagina local completa de Electropatios antes de pagar hosting o montar WordPress real.

## Que hicimos localmente

La pagina vive en:

```text
frontend/index.html
frontend/style.css
frontend/script.js
```

Ahora tiene:

- Inicio con mensaje comercial.
- Categorias principales.
- Catalogo con buscador y filtros.
- Productos con referencias, usos y cantidades.
- Carrito de cotizacion.
- Formulario conectado al flujo actual.
- Seccion de servicios.
- Paso a paso de compra.
- Preguntas frecuentes.
- Contacto.

## Como funciona

El cliente no paga en linea. Primero arma un pedido y deja sus datos.

JavaScript convierte ese pedido en JSON y lo envia al webhook de n8n:

```text
http://127.0.0.1:5678/webhook/electropatios-order
```

n8n recibe el pedido y sigue el flujo que ya tenemos:

```text
Pagina local -> n8n -> API Flask -> lead -> IA segura -> CRM seguro -> notificacion
```

## Que seria WordPress real

WordPress seria la herramienta para administrar la pagina sin tocar tanto codigo.

En WordPress podriamos crear:

- Pagina de inicio.
- Catalogo o secciones de productos.
- Formulario de cotizacion.
- Pagina de contacto.
- Blog o articulos si la empresa los necesita.

## Que seria hosting

Hosting es el lugar donde vive la pagina para que otras personas la puedan abrir desde internet.

En local solo la vemos en este computador. Con hosting, la pagina queda publicada.

## Que seria dominio

Dominio es el nombre publico de la pagina, por ejemplo:

```text
electropatios.com
```

## Que seria DNS

DNS conecta el dominio con el hosting.

En palabras simples: cuando alguien escribe el dominio, DNS le dice al navegador donde esta guardada la pagina.

## Que seria SSL

SSL es el candado del navegador:

```text
https://
```

Sirve para que la conexion sea segura.

## Que falta para WordPress real

Todavia falta decidir si vale la pena pagar:

- Dominio.
- Hosting.
- Tema de WordPress.
- Plugins para formularios.
- Conexion real del formulario con n8n.
- SSL.

Por ahora no necesitamos pagar. La version local sirve para aprender estructura, diseno, formulario y automatizacion antes de montarlo online.

## Como lo explicaria en entrevista

Primero construi la pagina completa en local para validar la experiencia del cliente: catalogo, carrito de cotizacion, formulario y flujo hacia n8n. Despues esa estructura se puede migrar a WordPress real, conectando dominio, hosting, DNS, SSL y el formulario hacia las mismas automatizaciones.
