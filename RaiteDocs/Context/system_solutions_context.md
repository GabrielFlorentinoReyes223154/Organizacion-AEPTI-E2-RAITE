# Contexto de soluciones del sistema — Raite

Documento de referencia del stack tecnológico de Raite: frontend, backend, base de datos, mapas, servicios y herramientas.

> **Fecha de verificación:** 2026-10-30.
> Se separa lo **implementado actualmente en el repositorio** de lo **planificado en la documentación** y que todavía no está instalado o configurado.

## 1. Resumen

Raite se construye con una arquitectura **API-First**:

- **Frontend:** SPA con Quasar Framework (Vue 3 + Vite + TypeScript).
- **Backend:** API REST con Django + Django REST Framework + JWT.
- **Base de datos:** PostgreSQL administrado en Neon.
- **Mapas:** Leaflet + OpenStreetMap, con extracción de puntos de interés mediante Overpass Turbo.

## 2. Frontend

### 2.1 Stack actual

| Tecnología | Versión | Uso |
| --- | --- | --- |
| Quasar Framework | `^2.30.0` | Framework de UI, layout, componentes y CLI. |
| Vue.js | `^3.5.22` | Framework reactivo (Composition API + SFC). |
| TypeScript | `^6.0.0` | Tipado estricto del frontend. |
| Vite | `@quasar/app-vite ^3.8.1` | Bundler y servidor de desarrollo. |
| Vue Router | `^5.0.6` | Rutas, auto-routes y guards de autenticación. |
| Pinia | `^4.0.2` | Estado global (por ejemplo, `auth-store`). |
| Axios | `^1.20.0` | Cliente HTTP e interceptores para JWT/refresh. |
| validator.js | `^13.15.35` | Validaciones de formularios. |
| Quasar Notify | Incluido en Quasar | Notificaciones tipo toast. |
| Quasar Extras | `^2.0.4` | Material Icons y fuente Roboto. |
| SCSS/Sass | Incluido en Quasar | Variables y estilos del tema. |
| PostCSS + Autoprefixer | `^8.5.8` / `^10.4.27` | Procesamiento de CSS. |
| ESLint | `^10.8.0` | Linting de TS/Vue. |
| Prettier | `^3.8.1` | Formato de código. |
| vue-tsc | `^3.3.3` | Chequeo de tipos en Vue. |
| vite-plugin-checker | `^0.14.5` | Chequeo de tipos/lint durante el desarrollo. |
| Node.js | `>= 26 \|\| ^24 \|\| ^22.12` | Runtime para Quasar/Vite. |
| pnpm | `pnpm-lock.yaml` | Gestor de paquetes del frontend. |

**Configuración relevante:** `Front_Raite/quasar.config.ts` y `Front_Raite/package.json`.

- Boot files: `axios`, `auth-init`.
- Modo de router: `history`.
- Puerto de desarrollo: `9000`.
- Ruteo por nombre de archivo: habilitado.

### 2.2 Frontend planificado

| Tecnología | Uso previsto |
| --- | --- |
| Leaflet 1.9+ | Renderizado del mapa, marcadores y rutas. **Aún no está en `package.json`.** |
| OpenStreetMap | Proveedor de tiles del mapa base. |
| HTML5 Geolocation API | Obtención de la ubicación del dispositivo para seguimiento GPS. |
| PWA / Workbox | Cache offline, instalación y notificaciones push. Documentado, no configurado. |
| Vitest + Vue Test Utils | Pruebas unitarias de componentes, stores y composables. Documentado, no instalado. |

## 3. Backend

### 3.1 Stack actual

| Tecnología | Versión | Uso |
| --- | --- | --- |
| Python | 3.14.7 | Runtime del backend (venv del proyecto). |
| Django | 6.1.1 | Framework principal: ORM, admin, middleware, seguridad. |
| Django REST Framework | 3.18.1 | Serializers, vistas API y permisos. |
| djangorestframework-simplejwt | 5.5.1 | Access/refresh tokens, rotación y blacklist. |
| PyJWT | 2.15.1 | Codificación/decodificación de JWT. |
| django-cors-headers | 4.9.0 | CORS para el frontend. |
| python-dotenv | 1.2.3 | Carga de variables desde `.env`. |
| dj-database-url | 3.1.2 | Parseo de `DATABASE_URL` para Django. |
| psycopg2-binary | 2.9.13 | Driver PostgreSQL. |
| asgiref | 3.12.1 | Interfaz ASGI. |
| sqlparse | 0.6.0 | Formateo/parseo SQL. |
| tzdata | 2026.4 | Datos de zonas horarias. |
| Django Admin | Incluido en Django | Panel administrativo. |
| Django ORM + migraciones | Incluido en Django | Modelos, consultas y versionado del esquema. |
| Modelo `Usuario` | Código del proyecto | Usuario personalizado con login por correo y roles. |

**Configuración relevante:** `Back_Raite/requirements.txt`, `Back_Raite/Raite_DjangoRest/settings.py` y `Back_Raite/.env`.

### 3.2 Backend planificado

| Tecnología | Uso previsto |
| --- | --- |
| Django Channels | WebSockets para notificaciones y ubicación en tiempo real. |
| Redis | Channel layer, caché y rate limiting. |
| Celery + Celery Beat | Tareas asíncronas y periódicas. |
| GeoDjango + PostGIS | Campos y consultas espaciales en el backend. |
| geopy / Nominatim | Geocodificación de direcciones a coordenadas. |
| OSRM / Valhalla | Cálculo de rutas y tiempos estimados. |
| drf-spectacular | Documentación OpenAPI de la API. |
| pytest + pytest-django + factory_boy | Pruebas del backend. |
| Ruff + mypy + black | Lint, tipado y formato. |
| Docker / Docker Compose | Entorno reproducible de desarrollo y despliegue. |

## 4. Base de datos

### 4.1 Actual

| Componente | Detalle |
| --- | --- |
| Motor | PostgreSQL 18.6 |
| Servicio | Neon (PostgreSQL administrado, endpoint con pooler) |
| Driver | `psycopg2-binary` |
| Configuración | `DATABASE_URL` cargada desde `.env` con `dj-database-url` |
| Seguridad de conexión | `sslmode=require` y `channel_binding=require` |
| Migraciones | Django Migrations |
| Extensiones instaladas | Solo `plpgsql` |

> **Nota:** la base actual **no tiene PostGIS instalado**. Las funciones espaciales descritas en la documentación todavía no están disponibles en Neon.

### 4.2 Planificado

| Componente | Uso previsto |
| --- | --- |
| PostGIS 3.4+ | Tipos `geometry`/`geography` y funciones espaciales. |
| Índices GIST/BRIN | Búsquedas por distancia y consultas temporales. |
| pg_dump / pg_restore | Respaldos y restauración. |
| pgAdmin / DBeaver / DataGrip | Administración y depuración de la base. |
| PgBouncer | Pooling de conexiones (Neon ya ofrece pooling). |

## 5. Mapas y geolocalización

Flujo previsto:

1. **Overpass Turbo / Overpass API** extrae puntos de interés de OpenStreetMap (por ejemplo, Oxxo, Walmart, S-Mart) y se guardan en la base mediante un seed.
2. **Leaflet** renderiza el mapa usando tiles de **OpenStreetMap** y muestra los puntos guardados.
3. La **HTML5 Geolocation API** obtiene la ubicación del conductor; el backend la distribuye a los pasajeros por WebSockets.
4. **Nominatim** convierte direcciones en coordenadas y **OSRM/Valhalla** calcula rutas y tiempos.

| Tecnología | Tipo | Estado |
| --- | --- | --- |
| Leaflet | Librería de mapas | Planificado (no instalado). |
| OpenStreetMap | Servicio de tiles/datos | Planificado. |
| Overpass Turbo / Overpass API | Herramienta/servicio de extracción de POI | Planificado; documentado en `RaiteDocs/integracion_de_mapas_y_geolocalizacion.md`. |
| HTML5 Geolocation API | API del navegador | Planificado. |
| Nominatim | Servicio de geocodificación | Planificado. |
| OSRM / Valhalla | Servicio de ruteo | Planificado. |
| Leaflet MarkerCluster | Plugin de agrupación de marcadores | Opcional/planificado. |
| Leaflet Routing Machine | Plugin de rutas | Opcional/planificado. |
| MapLibre GL JS | Alternativa a Leaflet | Alternativa considerada. |

## 6. Servicios, herramientas e infraestructura

| Herramienta/Servicio | Uso | Estado |
| --- | --- | --- |
| Git + GitHub | Control de versiones y repositorio remoto. | Actual. |
| Neon | Base de datos PostgreSQL administrada. | Actual. |
| pnpm | Gestor de paquetes del frontend. | Actual. |
| Node.js | Runtime del frontend. | Actual. |
| Python + venv | Runtime y entorno aislado del backend. | Actual. |
| VS Code | Editor recomendado (ESLint, Prettier, EditorConfig, Vue Volar). | Actual. |
| ESLint + Prettier | Calidad y formato de código. | Actual. |
| GitHub Actions | CI/CD. | Planificado. |
| Render / Railway | Hosting del backend. | Planificado. |
| Sentry | Monitoreo de errores. | Planificado. |
| UptimeRobot | Monitoreo de disponibilidad. | Planificado. |

## 7. Resumen por capa

| Capa | Stack actual | Stack planificado |
| --- | --- | --- |
| Frontend | Quasar 2.30, Vue 3.5, TypeScript 6, Vite, Vue Router 5, Pinia 4, Axios, pnpm | Leaflet, OpenStreetMap, PWA/Workbox, Vitest |
| Backend | Django 6.1, DRF 3.18, SimpleJWT 5.5, CORS, dotenv, psycopg2 | Channels, Redis, Celery, GeoDjango, PostGIS, OSRM |
| Base de datos | PostgreSQL 18.6 en Neon (sin PostGIS) | PostGIS, índices espaciales, respaldos |
| Mapas | — | Leaflet + OSM + Overpass Turbo + Geolocation API |
| Infraestructura | Git/GitHub, Neon, pnpm, venv | GitHub Actions, Render/Railway, Sentry |

## 8. Referencias en el repositorio

- `Front_Raite/package.json` — dependencias y versiones del frontend.
- `Front_Raite/quasar.config.ts` — configuración de Quasar, boot files y plugins.
- `Back_Raite/requirements.txt` — dependencias y versiones del backend.
- `Back_Raite/Raite_DjangoRest/settings.py` — apps, middleware, JWT, CORS y base de datos.
- `Back_Raite/.env` — variables de entorno, incluida `DATABASE_URL`.
- `RaiteDocs/tecnologias.md` — propuesta tecnológica amplia.
- `RaiteDocs/Raite-System-Architecture.md` — arquitectura y stack por capa.
- `RaiteDocs/integracion_de_mapas_y_geolocalizacion.md` — detalle de Overpass Turbo, Leaflet y GPS.
