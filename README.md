<div align="center">

<img src="Front_Raite/src/assets/logo-raite.png" alt="Raite" width="260">

### Viajes compartidos para la comunidad UACJ

Conecta a estudiantes que manejan al campus con quienes van para el mismo lado.<br>
Menos gasto, menos tráfico y más seguridad, solo entre alumnos verificados.

<br>

![Django](https://img.shields.io/badge/Django_6-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-A30000?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Vue](https://img.shields.io/badge/Vue_3-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white)
![Quasar](https://img.shields.io/badge/Quasar-1976D2?style=for-the-badge&logo=quasar&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=for-the-badge&logo=leaflet&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=black)

[Características](#-características) ·
[Tecnologías](#️-tecnologías) ·
[Inicio rápido](#-inicio-rápido) ·
[Despliegue](#️-despliegue) ·
[Documentación](#-documentación)

</div>

---

## 🚗 ¿Qué es Raite?

**Raite** es una plataforma web de viajes compartidos ("raites") pensada para los estudiantes de la
**Universidad Autónoma de Ciudad Juárez**. Los conductores publican sus trayectos hacia o desde
algún campus y los pasajeros buscan, solicitan un lugar y califican la experiencia al terminar.

Solo pueden entrar cuentas con correo `@alumnos.uacj.mx`, verificadas con un código.

## ✨ Características

| | |
|---|---|
| 🎓 **Acceso institucional** | Registro solo con correo `@alumnos.uacj.mx` y verificación por código. |
| 🗺️ **Mapa de puntos de referencia** | El origen se elige de un catálogo de 128 puntos en 5 campus; nunca se expone una dirección. |
| 🔍 **Búsqueda por cercanía** | Encuentra viajes cerca de ti, calculados con la fórmula de haversine. |
| 🪑 **Cupo controlado** | De 1 a 5 lugares por viaje, con bloqueo de fila para que nunca se sobrevenda. |
| 🚺 **Compatibilidad** | Cada usuario elige viajar con personas de su mismo sexo o en modo mixto. |
| 🔒 **Contacto protegido** | Teléfono y placas visibles solo después de aceptar la solicitud. |
| 🔔 **Avisos** | Notificaciones dentro de la aplicación en cada cambio de estado del viaje. |
| ⭐ **Calificaciones y reportes** | Conductor y pasajero se califican; los malos comportamientos se pueden reportar. |
| 🔄 **Doble rol** | Una misma cuenta puede ser pasajero y conductor; el papel cambia según la pantalla. |

### Ciclo de un raite

```mermaid
flowchart LR
    A[Publicar] --> B[Buscar]
    B --> C[Solicitar]
    C --> D[Aceptar]
    D --> E[Iniciar]
    E --> F[Finalizar]
    F --> G[Calificar]
```

## 🛠️ Tecnologías

<table>
<tr>
<td valign="top" width="33%">

**Backend** · `Back_Raite/`

- Python 3.12
- Django 6 + Django REST Framework
- JWT (SimpleJWT) con lista negra
- PostgreSQL 15+
- gunicorn + WhiteNoise

</td>
<td valign="top" width="33%">

**Frontend** · `Front_Raite/`

- Vue 3 + TypeScript
- Quasar 2
- Pinia
- Axios con renovación de token
- Leaflet + OpenStreetMap

</td>
<td valign="top" width="33%">

**Infraestructura**

- Render (API y sitio estático)
- Neon (PostgreSQL)
- Gmail SMTP (códigos)
- Blueprint en `render.yaml`

</td>
</tr>
</table>

### Arquitectura

```mermaid
flowchart LR
    U[Usuario<br/>navegador] --> F[Frontend<br/>Quasar + Vue 3]
    F -->|HTTPS + JWT| A[API<br/>Django + DRF]
    A --> D[(PostgreSQL<br/>Neon)]
    A -->|SMTP| G[Gmail]
    F -->|teselas| O[OpenStreetMap]
```

### Estructura

```text
Raite/
├── Back_Raite/          API en Django
│   └── apps/
│       ├── accounts/       usuarios, vehículos y verificación
│       ├── locations/      campus y puntos de referencia
│       ├── rides/          viajes, solicitudes y búsqueda
│       ├── notifications/  avisos
│       ├── ratings/        calificaciones
│       └── reports/        reportes
├── Front_Raite/         SPA en Quasar
└── render.yaml          configuración de despliegue
```

## 🚀 Inicio rápido

> **Requisitos:** Python 3.12+, PostgreSQL 15+, Node.js 22.12+ y [pnpm](https://pnpm.io/installation).

**1. Clona el repositorio**

```bash
git clone https://github.com/GabrielFlorentinoReyes223154/Organizacion-AEPTI-E2-RAITE.git
cd Organizacion-AEPTI-E2-RAITE
```

**2. Crea la base de datos**

```bash
sudo -u postgres psql -c "CREATE USER raite WITH PASSWORD 'raite' CREATEDB;"
sudo -u postgres psql -c "CREATE DATABASE raite OWNER raite;"
```

> `CREATEDB` es necesario para que las pruebas puedan crear su propia base de datos.

**3. Levanta el backend**

```bash
cd Back_Raite
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                   # define SECRET_KEY y DATABASE_URL
```

```bash
python manage.py migrate
python manage.py cargar_datos_iniciales   # campus y puntos de referencia
python manage.py crear_datos_demo         # opcional: usuarios y viajes de prueba
python manage.py createsuperuser
python manage.py runserver                # → http://localhost:8000
```

<details>
<summary>Valores de <code>.env</code></summary>

- `SECRET_KEY`: genera una con
  `python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"`
- `DATABASE_URL`: `postgres://raite:raite@localhost:5432/raite`

Los usuarios de demo usan la contraseña `raite1234` (usa `--reiniciar` para rehacerlos).
En desarrollo, los correos con códigos de verificación se imprimen en la terminal de `runserver`.

</details>

**4. Levanta el frontend** (en otra terminal)

```bash
cd Front_Raite
pnpm install
pnpm dev                                  # → http://localhost:9000
```

El frontend apunta a `http://localhost:8000`; para cambiarlo, define `VITE_API_URL`.

### ✅ Pruebas y revisión

```bash
# Backend
python manage.py check
python manage.py test

# Frontend
pnpm lint:check && pnpm typecheck && pnpm build
```

## ☁️ Despliegue

| Pieza | Servicio |
|---|---|
| API | Render · Web Service (gunicorn) |
| Frontend | Render · Static Site |
| Base de datos | Neon · PostgreSQL |
| Correo | Gmail SMTP |

Todo está declarado en [`render.yaml`](render.yaml) y cada merge a `main` despliega solo.
Los secretos se configuran únicamente en el panel de Render. La guía paso a paso está en
[`DEPLOYMENT.md`](DEPLOYMENT.md).

## 📚 Documentación

| Documento | Contenido |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Cómo está armado el sistema y por qué. |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Publicación en Render y Neon, y verificación. |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Entorno, reglas de código y flujo con Git. |

## 🗺️ Datos de mapas

Los puntos de referencia provienen de [OpenStreetMap](https://www.openstreetmap.org/copyright)
(© colaboradores de OpenStreetMap, licencia ODbL); los nombres de calle y colonia se obtuvieron con
Nominatim. Ver `Back_Raite/apps/locations/data/`.

---

<div align="center">

Hecho en Ciudad Juárez por estudiantes de la **UACJ** 💙💛

</div>
