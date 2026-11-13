# Guía de contribución

Este documento explica cómo se prepara el entorno para trabajar en Raite, qué reglas de código se siguen y cómo se suben los cambios al repositorio. El hecho de que el proyecto lo desarrollen varias personas obliga a mantener un orden común, ello permite que cualquier integrante entienda el trabajo de los demás sin dificultad.

## Contenido

1. [Entorno de desarrollo](#1-entorno-de-desarrollo)
2. [Comandos de uso frecuente](#2-comandos-de-uso-frecuente)
3. [Reglas de código](#3-reglas-de-código)
4. [Trabajo con Git](#4-trabajo-con-git)
5. [Revisión antes de entregar](#5-revisión-antes-de-entregar)

## 1. Entorno de desarrollo

Para trabajar en el proyecto, se requiere tener instalado lo siguiente:

- Python 3.12 o superior.
- PostgreSQL 15 o superior.
- Node.js 22.12 o superior (también sirven la 24 y la 26) y [pnpm](https://pnpm.io/installation).
- Git.

### Clonar el repositorio

```bash
git clone https://github.com/Organizacion-AEPTI-E2/Raite.git
cd Raite
```

### Crear la base de datos local

Primero se instala PostgreSQL. En Fedora se hace con los comandos siguientes:

```bash
sudo dnf install postgresql-server postgresql
sudo postgresql-setup --initdb
sudo systemctl enable --now postgresql
```

En Ubuntu basta con este comando:

```bash
sudo apt install postgresql
```

Después se crean el usuario y la base de datos del proyecto:

```bash
sudo -u postgres psql -c "CREATE USER raite WITH PASSWORD 'raite' CREATEDB;"
sudo -u postgres psql -c "CREATE DATABASE raite OWNER raite;"
```

El permiso `CREATEDB` es necesario para que `python manage.py test` pueda crear la base de datos de pruebas. Si PostgreSQL rechaza la contraseña al conectarse por `localhost`, se revisa que el archivo `pg_hba.conf` use `scram-sha-256` (o `md5`) en las conexiones `host` y se reinicia el servicio.

### Preparar el backend

```bash
cd Back_Raite
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # y se editan los valores
```

En el archivo `.env` se necesitan, como mínimo, estas dos variables:

- `SECRET_KEY`: se genera con `python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"`.
- `DATABASE_URL`: `postgres://raite:raite@localhost:5432/raite` (se ajustan usuario, contraseña y nombre si se cambiaron).

Para lo cual, a continuación se ejecutan los comandos que crean las tablas y cargan la información inicial:

```bash
python manage.py migrate                  # crea las tablas
python manage.py cargar_datos_iniciales   # campus y puntos de referencia (se puede repetir)
python manage.py crear_datos_demo         # opcional: usuarios y viajes de ejemplo (contraseña raite1234)
python manage.py createsuperuser          # usuario para el administrador de Django
python manage.py runserver                # http://localhost:8000  (administrador en /admin/)
```

Con la configuración por defecto, los correos (como los códigos de verificación) no se envían, sino que se muestran en la terminal donde corre `runserver`.

### Preparar el frontend

En otra terminal se ejecutan estos comandos:

```bash
cd Front_Raite
pnpm install
pnpm dev                                  # http://localhost:9000
```

El frontend usa `http://localhost:8000` como dirección de la API. Si se necesita cambiar, se define la variable `VITE_API_URL`.

### Comprobar que todo funciona

```bash
cd Back_Raite
python manage.py check
python manage.py test
```

## 2. Comandos de uso frecuente

### Backend (`Back_Raite/`)

| Comando | Para qué sirve |
|---------|----------------|
| `python manage.py makemigrations` | Genera las migraciones después de cambiar los modelos |
| `python manage.py crear_datos_demo --reiniciar` | Rehace los datos de ejemplo |
| `python manage.py cargar_datos_iniciales --actualizar-estados` | Copia el campo `activo` del JSON a una base que ya tiene los puntos |
| `python manage.py probar_correo tu@alumnos.uacj.mx` | Envía un correo de prueba |
| `python manage.py generar_puntos_osm` | Regenera `puntos_referencia.json` (usa internet y tarda unos 3 minutos) |
| `python manage.py test apps.rides` | Corre las pruebas de una sola app |
| `python manage.py test apps.accounts.tests.test_auth_api` | Corre las pruebas de un módulo |

### Frontend (`Front_Raite/`)

| Comando | Para qué sirve |
|---------|----------------|
| `pnpm build` | Compila la aplicación en `dist/spa` |
| `pnpm lint` | Da formato al código y corrige errores de estilo |
| `pnpm lint:check` | Revisa formato y estilo sin modificar archivos |
| `pnpm typecheck` | Verifica los tipos de TypeScript |

## 3. Reglas de código

### Idioma

La interfaz (textos, mensajes de error y etiquetas) está en español. Asimismo, el código del dominio se escribe en español, como ya se hace en el proyecto (`correo`, `nombre`, `Vehiculo`, `Solicitud`), por lo que dicha costumbre se mantiene en los modelos, campos y funciones nuevas.

### Backend

Cada app del backend se organiza de la misma manera, a causa de ello es que resulta fácil ubicar dónde va cada cosa. Las reglas principales son las siguientes:

- Cada app contiene `models.py`, `models_choices.py`, `services.py`, `serializers.py`, `views.py`, `urls.py`, `admin.py`, `migrations/` y `tests/`.
- Los modelos solo validan un registro por separado (con `clean()`, validadores y restricciones de la base de datos).
- Las reglas que involucran varios registros se escriben en `services.py`, dentro de `transaction.atomic()`, llamando a `full_clean()` antes de guardar y creando los avisos con `apps/notifications/services.notificar()`.
- Los serializers solo dan forma a lo que entra y sale, y las vistas se mantienen cortas porque dejan el trabajo a los servicios.
- Los errores se lanzan como `ValidationError` (400), `PermissionDenied` (403), `Http404` (404) o `Conflicto` (409), y un manejador central los convierte en la respuesta correspondiente.
- Todo el API pide sesión y correo verificado de forma predeterminada, así que los endpoints públicos deben declarar `AllowAny` de manera explícita.
- Las pruebas se escriben con las fábricas de `apps/accounts/tests/factories.py` y `apps/rides/tests/factories.py`, y siempre se corren sobre PostgreSQL, ya que SQLite no detecta, por ejemplo, textos más largos que la columna.
- Los secretos y la configuración que cambia según el entorno se leen de variables de entorno y nunca se escriben en el repositorio.

### Frontend

- Se usa TypeScript con Vue 3, Pinia y Quasar, y el gestor de paquetes es pnpm.
- El código sigue la organización existente: `src/api/` (una función por endpoint), `src/stores/`, `src/utils/`, `src/components/`, `src/layouts/` y `src/pages/`.
- Cada página declara con `definePage({ meta })` si es pública, qué papel necesita (`pasajero` o `conductor`), su título y su ruta de regreso.
- Para importar desde `src/` se usa el alias `@/`.
- El archivo `Front_Raite/src/router/typed-router.d.ts` se genera solo, por lo que no se edita a mano.
- El diseño visual se apega a [`DESIGN.md`](DESIGN.md). Se da prioridad a la computadora, aunque el celular debe seguir funcionando.

### Documentación

Los archivos de `RaiteDocs/docs/` provienen de Google Docs, por ello no se editan directamente en el repositorio (ver `RaiteDocs/docs/README.md`). Cuando un cambio modifica el comportamiento del sistema, se actualiza también el documento que lo describe, como lo son `RaiteDocs/API.md`, `RaiteDocs/Modelo-ER.md` o `CLAUDE.md`.

### Alcance del proyecto

No se agregan requerimientos que no estén en el SRS, en la carta del proyecto o en las reglas de negocio de [`CLAUDE.md`](CLAUDE.md). Tampoco se implementan, salvo que se pidan de forma explícita, los pagos dentro de la aplicación, el seguimiento GPS permanente, los conductores externos a la comunidad universitaria, la cobertura fuera de Ciudad Juárez ni la integración con sistemas internos de la UACJ. Antes de cambiar la tecnología o instalar dependencias grandes (PostGIS, Channels, Celery, Redis, entre otras), se consulta con el equipo.

## 4. Trabajo con Git

### Ramas

El trabajo se organiza por capas, con una rama para cada una: `capa/modelos`, `capa/logica` y `capa/vistas`. Cada rama se crea a partir de `main` una vez integrada la capa anterior, y no se comienza una capa hasta terminar y probar la previa. Las partes de una capa llevan guion (`capa/vistas-inicio`) y nunca otra diagonal, esto porque `capa/vistas/inicio` chocaría con la rama `capa/vistas`.

### Commits

Los commits son pequeños, uno por cada funcionalidad o cambio, y sus mensajes se redactan en español con el formato `tipo(ámbito): descripción`, citando el requerimiento cuando aplique:

```
feat(accounts): valida correo institucional (RF-01)
fix(rides): corrige el cruce de horarios al editar un viaje
feat(front): agrega la pantalla de historial
```

Los tipos que se utilizan son los siguientes:

- `feat`: una funcionalidad nueva.
- `fix`: la corrección de un error.
- `refactor`: un cambio interno que no altera el comportamiento.
- `test`: pruebas nuevas o modificadas.
- `docs`: cambios en la documentación.
- `chore`: mantenimiento, dependencias y configuración.

### Integración

Los cambios llegan a `main` mediante una solicitud de integración (*pull request*). El hecho de que cada integración a `main` despliegue de forma automática (ver [`DEPLOYMENT.md`](DEPLOYMENT.md)) obliga a que esa rama se encuentre siempre funcionando.

## 5. Revisión antes de entregar

Antes de dar por terminado un cambio, se ejecutan las comprobaciones que correspondan a lo que se modificó.

Para el backend:

```bash
cd Back_Raite
python manage.py test
```

Para el frontend:

```bash
cd Front_Raite
pnpm lint:check && pnpm typecheck
```

Si el cambio afecta el despliegue, se revisa además lo siguiente:

```bash
cd Back_Raite
DEBUG=False SECRET_KEY=<una-clave-larga> ALLOWED_HOSTS=x python manage.py check --deploy   # debe salir sin avisos

cd ../Front_Raite
pnpm build
```
