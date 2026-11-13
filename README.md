# Raite

Plataforma web de viajes compartidos ("raites") para estudiantes de la Universidad Autónoma de Ciudad Juárez (UACJ).

- `Back_Raite/` — API en Django + Django REST Framework (PostgreSQL).
- `Front_Raite/` — SPA en Quasar (Vue 3 + TypeScript).
- `RaiteDocs/` — documentación del proyecto (SRS, diseño, diagramas).

## Levantar el proyecto desde cero

### Requisitos

- Python 3.12 o superior
- PostgreSQL 15 o superior (local)
- Node.js 22.12+ (o 24 / 26) y [pnpm](https://pnpm.io/installation)
- Git

### 1. Clonar el repositorio

```bash
git clone https://github.com/Organizacion-AEPTI-E2/Raite.git
cd Raite
```

### 2. Crear la base de datos local

Instala PostgreSQL (en Fedora: `sudo dnf install postgresql-server postgresql` y luego
`sudo postgresql-setup --initdb && sudo systemctl enable --now postgresql`; en Ubuntu:
`sudo apt install postgresql`).

Crea un usuario y una base de datos para el proyecto:

```bash
sudo -u postgres psql -c "CREATE USER raite WITH PASSWORD 'raite' CREATEDB;"
sudo -u postgres psql -c "CREATE DATABASE raite OWNER raite;"
```

> El permiso `CREATEDB` es necesario para que `python manage.py test` pueda crear la base de datos de pruebas.

Si PostgreSQL rechaza la contraseña al conectarte por `localhost`, revisa que `pg_hba.conf` use
`scram-sha-256` (o `md5`) para las conexiones `host` y reinicia el servicio.

### 3. Backend

```bash
cd Back_Raite
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # y edita los valores
```

En `.env`, como mínimo:

- `SECRET_KEY`: genera una con
  `python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"`
- `DATABASE_URL`: `postgres://raite:raite@localhost:5432/raite` (ajusta usuario, contraseña y nombre si los cambiaste).

Después:

```bash
python manage.py migrate                  # crea las tablas
python manage.py cargar_datos_iniciales   # campus y puntos de referencia (se puede repetir)
python manage.py crear_datos_demo         # opcional: usuarios y viajes de demo (contraseña raite1234); --reiniciar para rehacerlos
python manage.py createsuperuser          # usuario para el admin de Django
python manage.py runserver                # http://localhost:8000  (admin en /admin/)
```

Comprobación rápida:

```bash
python manage.py check
python manage.py test
```

Con la configuración por defecto, los correos (por ejemplo, los códigos de verificación) se imprimen en la terminal de `runserver` en lugar de enviarse.

#### Fotos de perfil

- **Sin R2** (lo normal en desarrollo): deja vacías las variables `R2_*`. Las fotos se guardan en `Back_Raite/media/` (ignorada por git) y `runserver` las sirve en `/media/`.
- **Con R2:** pon en `.env` las cuatro variables `R2_BUCKET`, `R2_ENDPOINT_URL`, `R2_ACCESS_KEY_ID` y `R2_SECRET_ACCESS_KEY` (los valores los da quien administra la cuenta de Cloudflare; nunca se suben al repo) y reinicia `runserver`. Las fotos van al bucket privado y el API entrega URLs firmadas que vencen en una hora.
- `python manage.py test` nunca usa R2, aunque el `.env` tenga las variables: guarda las fotos en memoria.

### 4. Frontend

En otra terminal:

```bash
cd Front_Raite
pnpm install
pnpm dev                                  # http://localhost:9000
```

El frontend usa `http://localhost:8000` como API. Para cambiarlo, define `VITE_API_URL`.

## Despliegue (Render + Neon)

- **API:** Web Service de pago en Render (instancia `0.5c-512mb`, región Oregon) con gunicorn; whitenoise sirve los estáticos del admin. Se usa de pago porque el plan gratis bloquea el SMTP de Gmail.
- **Frontend:** Static Site gratis en Render con el build de Quasar (`Front_Raite/dist/spa`) y la regla `/*` → `/index.html` (el router usa modo history).
- **Base de datos:** PostgreSQL en Neon (plan gratis, región Oregon / AWS us-west-2).
- **Correo:** SMTP de Gmail (`smtp.gmail.com`, 587, TLS) desde `raite.uacj@gmail.com` con contraseña de aplicación.

Todo está en `render.yaml` (Blueprint). Los secretos y las URLs **solo** se escriben en el panel de Render, nunca en el repo.

### 1. Neon

1. Proyecto `raite` → **Connect** → rama `main`, base `neondb`, con **Connection pooling desactivado** (conexión directa).
2. Copia la cadena. Es la `DATABASE_URL`:
   `postgresql://usuario:clave@ep-xxx.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require`
3. Las tablas las crea el `migrate` que corre Render antes de cada versión; no hay que hacer nada más en Neon.

> Si la conexión falla por `channel_binding`, quita `&channel_binding=require` de `DATABASE_URL` (deja `sslmode=require`).

### 2. Render

1. Junta la rama `despliegue` en `main` y haz push.
2. **New → Blueprint** → elige el repo y la rama **`main`**. Render lee `render.yaml` y crea `raite-api` y `raite-web`. Desde entonces, cada merge a `main` despliega solo (y solo el servicio cuya carpeta cambió).
3. Render pide las variables marcadas con `sync: false`:

   | Servicio | Variable | Valor |
   |---|---|---|
   | raite-api | `SECRET_KEY` | clave nueva (secreto) |
   | raite-api | `DATABASE_URL` | cadena de Neon (secreto) |
   | raite-api | `EMAIL_HOST_PASSWORD` | contraseña de aplicación de Gmail, sin espacios (secreto) |
   | raite-api | `ALLOWED_HOSTS` | `raite-api.onrender.com` |
   | raite-api | `CORS_ALLOWED_ORIGINS` | `https://raite-web.onrender.com` |
   | raite-api | `CSRF_TRUSTED_ORIGINS` | `https://raite-web.onrender.com` |
   | raite-api | `R2_BUCKET` | `raite-fotos` |
   | raite-api | `R2_ENDPOINT_URL` | `https://<id-de-cuenta>.r2.cloudflarestorage.com` |
   | raite-api | `R2_ACCESS_KEY_ID` | clave de acceso de R2 (secreto) |
   | raite-api | `R2_SECRET_ACCESS_KEY` | secreto de R2 (secreto) |
   | raite-web | `VITE_API_URL` | `https://raite-api.onrender.com` (sin `/` al final) |

   El resto (`DEBUG=False`, `EMAIL_*`, `DEFAULT_FROM_EMAIL`, `PYTHON_VERSION`, `NODE_VERSION`) ya viene en `render.yaml`. Sin las cuatro `R2_*` las fotos se guardarían en el disco de Render, que se borra en cada despliegue.
4. Al terminar, revisa las URLs que asignó Render: si el nombre estaba ocupado, le agrega un sufijo (ej. `raite-api-x1y2.onrender.com`). Si cambiaron, corrige las cuatro variables de URL:
   - `raite-api` se reinicia solo al guardar.
   - `raite-web` necesita **Manual Deploy → Clear build cache & deploy**, porque `VITE_API_URL` se mete al compilar.
5. En **Settings** de `raite-api`, confirma la instancia `0.5c-512mb` y la región Oregon.

En cada versión, Render corre `migrate` y `cargar_datos_iniciales` (preDeploy). **No** se carga `crear_datos_demo` en producción.

### 3. Superusuario

En `raite-api` → pestaña **Shell** (`cd Back_Raite` si no estás ahí):

```bash
python manage.py createsuperuser
```

Pide correo, contraseña, nombre, apellidos, edad, sexo, carrera y teléfono. El admin no necesita correo `@alumnos.uacj.mx` y queda verificado. Entra en `https://raite-api.onrender.com/admin/`.

### 4. Comprobar que funciona

1. Logs de `raite-api`: el preDeploy muestra las migraciones y `Campus: … Puntos de referencia: …` sin errores.
2. `https://raite-api.onrender.com/api/campus/` responde **401** (pide sesión: el API está en línea y el dominio es válido). `/admin/` muestra el login con estilos.
3. `https://raite-web.onrender.com/inicio`, y recargar con F5 en `/buscar`: no debe dar 404.
4. **Correo**, desde la Shell: `python manage.py probar_correo tu@alumnos.uacj.mx` debe llegar a la bandeja.
   Si falla o no llega, revisa la bandeja de `raite.uacj@gmail.com` por una alerta de seguridad de Google por el inicio de sesión desde Render, confirma que fuiste tú y vuelve a probar.
   Después, haz un registro real desde el frontend con un correo `@alumnos.uacj.mx`: llega el código, se verifica y se inicia sesión.
5. Flujo completo con dos cuentas reales: registrar vehículo, publicar, buscar, solicitar, aceptar (se ven teléfono y placas), iniciar, finalizar y calificar.
6. Consola del navegador sin errores de CORS, y el mapa carga.
7. En el admin hay 5 campus y 128 puntos de referencia.

Antes de cada despliegue, en local: `python manage.py test`,
`DEBUG=False SECRET_KEY=<una larga> ALLOWED_HOSTS=x python manage.py check --deploy` (sin avisos) y
`pnpm lint:check && pnpm typecheck && pnpm build`.

### Teselas del mapa

El mapa usa las teselas públicas de OpenStreetMap (`tile.openstreetmap.org`). Para una piloto chica está permitido: hay atribución visible y el navegador manda `Referer`. No tiene garantía de servicio; si el tráfico crece, se cambia la URL en `Front_Raite/src/components/MapaRaite.vue` por un proveedor con plan gratis (MapTiler o Stadia Maps, ambos con registro).

## Datos de mapas

Los puntos de referencia provienen de [OpenStreetMap](https://www.openstreetmap.org/copyright)
(© colaboradores de OpenStreetMap, licencia ODbL) y sus nombres de calle y colonia se obtuvieron con
Nominatim. Ver `Back_Raite/apps/locations/data/`.

## Documentación

- `CLAUDE.md` — estado del proyecto, decisiones, reglas de negocio y convenciones.
- `RaiteDocs/docs/2_SRS.md` — requerimientos (RF-xx, RNF-xx).

