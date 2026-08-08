# Guia de deploy

Esta guia es la Fase 11 del proyecto. En esta version no estamos subiendo toda la automatizacion a produccion. Primero dejamos online la pagina principal como demo de portafolio usando GitHub Pages.

## Que queda online

La carpeta que se publica es:

```text
main / root
```

En la raiz hay un `index.html` pequeno que abre la pagina real en:

```text
frontend/
```

La pagina real tiene:

- `index.html`: estructura de la pagina.
- `style.css`: diseno visual.
- `script.js`: catalogo, carrito, formulario y modo demo online.
- `tracking.js`: eventos y UTM en local o demo online.

## Que sigue local

Estas partes siguen en tu computador:

- API Flask en `http://localhost:5000`.
- n8n en `http://localhost:5678`.
- MySQL local si lo activas.
- Archivos JSONL en `backend/data`.

Esto esta bien para una primera version de aprendizaje. Asi mostramos la pagina sin pagar hosting ni exponer automatizaciones reales.

## Como funciona el modo online

Cuando abres la pagina desde GitHub Pages, el navegador no puede llamar a:

```text
http://localhost:5000
http://127.0.0.1:5678
```

Eso solo existe en tu PC.

Por eso `frontend/script.js` detecta si esta en local o en internet:

- En local usa n8n/API.
- En internet guarda el pedido en el navegador como demo segura.

Asi la pagina no queda rota y se puede mostrar en portafolio.

## Configuracion de GitHub Pages

En GitHub hay que entrar al repositorio y elegir:

```text
Settings -> Pages -> Build and deployment
```

Selecciona:

- Source: `Deploy from a branch`.
- Branch: `main`.
- Folder: `/ (root)`.

Despues de guardar, GitHub publica la pagina cada vez que haya cambios en `main`.

## Archivos de deploy

- `index.html`: redirige a `frontend/`.
- `.nojekyll`: le dice a GitHub Pages que publique archivos estaticos sin procesarlos con Jekyll.
- `frontend/`: contiene la pagina completa.

## URL esperada

La pagina publicada queda en:

```text
https://deyson24ivan.github.io/electropatios-quote-system/
```

Si el repositorio es privado y tu plan de GitHub no permite Pages privado, GitHub puede pedir hacerlo publico o cambiar de plan.

## Como lo explicaria en entrevista

Publique la pagina estatica en GitHub Pages desde la rama `main`. Como el backend y n8n siguen locales, agregue un modo demo online para que el formulario no falle cuando se abre desde internet. La version local conserva el flujo completo con n8n, API, tracking y automatizaciones.
