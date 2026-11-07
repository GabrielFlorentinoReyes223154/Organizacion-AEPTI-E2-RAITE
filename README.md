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

### 4. Frontend

En otra terminal:

```bash
cd Front_Raite
pnpm install
pnpm dev                                  # http://localhost:9000
```

El frontend usa `http://localhost:8000` como API. Para cambiarlo, define `VITE_API_URL`.

## Datos de mapas

Los puntos de referencia provienen de [OpenStreetMap](https://www.openstreetmap.org/copyright)
(© colaboradores de OpenStreetMap, licencia ODbL) y sus nombres de calle y colonia se obtuvieron con
Nominatim. Ver `Back_Raite/apps/locations/data/`.

## Documentación

- `CLAUDE.md` — estado del proyecto, decisiones, reglas de negocio y convenciones.
- `RaiteDocs/docs/2_SRS.md` — requerimientos (RF-xx, RNF-xx).

