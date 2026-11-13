# Despliegue

Este documento explica cómo se publica Raite en internet y cómo se comprueba que todo quedó funcionando. El hecho de que el sistema deba estar disponible en todo momento obliga a usar servicios en la nube, los cuales se configuran una sola vez y después se actualizan solos.

## Contenido

1. [Cómo está armado el despliegue](#1-cómo-está-armado-el-despliegue)
2. [Configuración de Neon](#2-configuración-de-neon)
3. [Configuración de Render](#3-configuración-de-render)
4. [Creación del superusuario](#4-creación-del-superusuario)
5. [Verificación del despliegue](#5-verificación-del-despliegue)
6. [Revisión previa a cada despliegue](#6-revisión-previa-a-cada-despliegue)
7. [Mapas de OpenStreetMap](#7-mapas-de-openstreetmap)

## 1. Cómo está armado el despliegue

El sistema se reparte en cuatro servicios, entre los cuales están:

- **API:** se publica en Render como *Web Service* de pago (instancia `0.5c-512mb`, región Oregon) y se ejecuta con gunicorn. WhiteNoise se encarga de los archivos estáticos del administrador. Es de pago porque el plan gratuito de Render bloquea el SMTP de Gmail.
- **Frontend:** se publica en Render como *Static Site* gratuito, con la compilación de Quasar (`Front_Raite/dist/spa`) y la regla `/*` → `/index.html`, ya que el router funciona en modo `history`.
- **Base de datos:** PostgreSQL en Neon (plan gratuito, región Oregon / AWS `us-west-2`).
- **Correo:** SMTP de Gmail (`smtp.gmail.com`, puerto 587, TLS) desde `raite.uacj@gmail.com`, con una contraseña de aplicación.

Toda la configuración está en el archivo [`render.yaml`](render.yaml). Los secretos y las URLs únicamente se escriben en el panel de Render y jamás en el repositorio.

## 2. Configuración de Neon

1. En el proyecto `raite` se abre **Connect**, se elige la rama `main` y la base `neondb`, y se desactiva **Connection pooling** (se usa la conexión directa).
2. Se copia la cadena de conexión, que será el valor de `DATABASE_URL`:

   ```
   postgresql://usuario:clave@ep-xxx.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
   ```

3. Las tablas las crea el comando `migrate` que Render ejecuta antes de cada versión, por lo que no se necesita hacer nada más en Neon.

Si la conexión falla a causa de `channel_binding`, se quita `&channel_binding=require` de `DATABASE_URL` y se deja únicamente `sslmode=require`.

## 3. Configuración de Render

1. Se integra la rama `despliegue` en `main` y se hace *push*.
2. En Render se elige **New → Blueprint**, se selecciona el repositorio y la rama **`main`**. Render lee `render.yaml` y crea los servicios `raite-api` y `raite-web`. Desde ese momento, cada integración a `main` despliega de forma automática, y solo el servicio cuya carpeta cambió.
3. Render pide las variables marcadas con `sync: false`, las cuales se llenan como se muestra a continuación:

   | Servicio | Variable | Valor |
   |----------|----------|-------|
   | `raite-api` | `SECRET_KEY` | Una clave nueva (secreto) |
   | `raite-api` | `DATABASE_URL` | La cadena de Neon (secreto) |
   | `raite-api` | `EMAIL_HOST_PASSWORD` | La contraseña de aplicación de Gmail, sin espacios (secreto) |
   | `raite-api` | `ALLOWED_HOSTS` | `raite-api.onrender.com` |
   | `raite-api` | `CORS_ALLOWED_ORIGINS` | `https://raite-web.onrender.com` |
   | `raite-api` | `CSRF_TRUSTED_ORIGINS` | `https://raite-web.onrender.com` |
   | `raite-web` | `VITE_API_URL` | `https://raite-api.onrender.com` (sin `/` al final) |

   El resto de las variables (`DEBUG=False`, `EMAIL_*`, `DEFAULT_FROM_EMAIL`, `PYTHON_VERSION` y `NODE_VERSION`) ya vienen definidas en `render.yaml`.

4. Al terminar, se revisan las URLs que asignó Render. Cuando el nombre ya estaba ocupado, se le agrega un sufijo (por ejemplo, `raite-api-x1y2.onrender.com`), y si eso ocurre se corrigen las cuatro variables de URL:
   - `raite-api` se reinicia solo al guardar los cambios.
   - `raite-web` necesita **Manual Deploy → Clear build cache & deploy**, esto porque `VITE_API_URL` se incorpora al momento de compilar.
5. En **Settings** de `raite-api` se confirma la instancia `0.5c-512mb` y la región Oregon.

En cada versión, Render ejecuta `migrate` y `cargar_datos_iniciales` antes de publicar. En cambio, `crear_datos_demo` no se ejecuta en producción.

## 4. Creación del superusuario

En el servicio `raite-api` se abre la pestaña **Shell** (con `cd Back_Raite` si no se está en esa carpeta) y se ejecuta:

```bash
python manage.py createsuperuser
```

El comando pide correo, contraseña, nombre, apellidos, edad, sexo, carrera y teléfono. El administrador no necesita correo `@alumnos.uacj.mx` y queda verificado desde el inicio. Para entrar al panel se usa `https://raite-api.onrender.com/admin/`.

## 5. Verificación del despliegue

Una vez publicado el sistema, se recomienda comprobar los puntos que se leen consecuentemente:

1. **Registros de `raite-api`:** el *preDeploy* debe mostrar las migraciones y la línea `Campus: … Puntos de referencia: …` sin errores.
2. **API en línea:** `https://raite-api.onrender.com/api/campus/` debe responder **401**, lo que indica que pide sesión y, por ello, el API está activo. Además, `/admin/` debe mostrar el inicio de sesión con estilos.
3. **Frontend:** se abre `https://raite-web.onrender.com/inicio` y se recarga con F5 en `/buscar`, sin que aparezca un error 404.
4. **Correo:** desde la Shell se ejecuta `python manage.py probar_correo tu@alumnos.uacj.mx`, y el mensaje debe llegar a la bandeja. Si falla o no llega, se revisa la bandeja de `raite.uacj@gmail.com`, ya que Google puede enviar una alerta de seguridad por el inicio de sesión desde Render. Se confirma que fue el equipo y se repite la prueba. Después se hace un registro real desde el frontend con un correo `@alumnos.uacj.mx`: debe llegar el código, verificarse y permitir iniciar sesión.
5. **Flujo completo con dos cuentas reales:** registrar vehículo, publicar, buscar, solicitar, aceptar (deben verse teléfono y placas), iniciar, finalizar y calificar.
6. **Navegador:** la consola no debe mostrar errores de CORS y el mapa debe cargar.
7. **Administrador:** debe haber 5 campus y 128 puntos de referencia.

## 6. Revisión previa a cada despliegue

Antes de integrar cambios a `main`, se ejecutan las siguientes comprobaciones en la computadora local:

```bash
# Backend
cd Back_Raite
python manage.py test
DEBUG=False SECRET_KEY=<una-clave-larga> ALLOWED_HOSTS=x python manage.py check --deploy   # sin avisos

# Frontend
cd ../Front_Raite
pnpm lint:check && pnpm typecheck && pnpm build
```

## 7. Mapas de OpenStreetMap

El mapa utiliza las teselas públicas de OpenStreetMap (`tile.openstreetmap.org`). Para un piloto pequeño, su uso está permitido porque hay atribución visible y el navegador envía el encabezado `Referer`, aunque el servicio no ofrece garantía de disponibilidad. Si el tráfico crece, se cambia la URL en `Front_Raite/src/components/MapaRaite.vue` por la de un proveedor con plan gratuito (MapTiler o Stadia Maps, ambos con registro).
