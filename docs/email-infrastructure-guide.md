# Guia de infraestructura email

Esta guia es la Fase 10 del proyecto. La idea es entender que necesita un dominio para mandar correos de forma mas confiable, sin tocar DNS reales todavia.

## Que hicimos

Agregue un modo seguro para preparar un plan de DNS/email.

El endpoint recibe un dominio como:

```text
electropatios.com
```

Y devuelve una lista de registros que habria que revisar:

- SPF
- DKIM
- DMARC

Importante: esta fase no cambia el DNS real, no compra dominio y no manda correos. Solo deja el plan armado para revisarlo con calma.

## Que es SPF

SPF es un registro TXT que dice que servidores pueden mandar correos usando tu dominio.

Ejemplo:

```text
v=spf1 include:_spf.google.com ~all
```

En palabras simples: "si el correo viene desde este proveedor autorizado, confia mas en el".

Regla importante: normalmente debe existir un solo registro SPF por dominio. Si tienes varios proveedores, se unen en el mismo registro.

## Que es DKIM

DKIM es una firma digital del correo.

Sirve para demostrar que el correo salio de un proveedor autorizado y que el contenido no fue cambiado en el camino.

El valor DKIM no se inventa en el codigo. Se copia desde el proveedor real, por ejemplo Google Workspace, GoHighLevel, SendGrid o Mailgun.

## Que es DMARC

DMARC usa SPF y DKIM para decidir que hacer cuando un correo no pasa autenticacion.

Para empezar de forma segura usamos:

```text
v=DMARC1; p=none; rua=mailto:dmarc@electropatios.com; fo=1
```

`p=none` significa: "no bloquees todavia, solo manda reportes".

Cuando ya se revisan reportes y todo pasa bien, mas adelante se puede subir a:

- `p=quarantine`
- `p=reject`

## Entregabilidad

Entregabilidad significa que los correos lleguen a la bandeja de entrada y no a spam.

Buenas practicas:

- Usar SPF o DKIM como minimo.
- Usar SPF y DKIM si se mandan muchos correos.
- Tener DMARC publicado.
- Mantener quejas de spam por debajo de 0.3%.
- Usar TLS para mandar correos.
- Tener DNS directo y reverso correcto si se usa IP propia.
- En correos promocionales, tener enlace de baja y one-click unsubscribe cuando aplique.

## Endpoint nuevo

```text
POST /api/email/dns-plan
```

Ejemplo:

```json
{
  "domain": "electropatios.com",
  "mail_from_domain": "mail.electropatios.com",
  "providers": ["google_workspace", "gohighlevel"],
  "report_email": "dmarc@electropatios.com",
  "daily_volume": 300
}
```

La API responde con:

- Registros que habria que revisar.
- Advertencias para no publicar algo mal.
- Pasos siguientes.
- Confirmacion de que `will_change_dns` es `false`.

## Como probar

```powershell
$body = Get-Content -Raw "examples/requests/email-dns-plan.json"
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/email/dns-plan" -Method Post -ContentType "application/json" -Body $body
```

## Como lo explicaria en entrevista

Prepare una fase de infraestructura email en modo seguro. El sistema genera un plan para SPF, DKIM y DMARC, valida el dominio, marca que registros dependen del proveedor real y guarda el resultado sin tocar DNS. Esto demuestra que entiendo autenticacion de correo y entregabilidad antes de activar envios reales.

## Fuentes oficiales para revisar

- Gmail sender guidelines: https://support.google.com/mail/answer/81126
- Gmail sender requirements FAQ: https://support.google.com/mail/answer/14229414
- Yahoo sender best practices: https://senders.yahooinc.com/best-practices/
