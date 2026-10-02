# Arquitectura del Sistema Raite

## Visión General

Raite adopta una **arquitectura desacoplada API-First** con **Quasar (Vue 3)** como frontend SPA/PWA, **Django REST Framework** como backend API, y **PostgreSQL + PostGIS** como base de datos espacial.

---

## Stack Tecnológico

### Frontend (Quasar SPA/PWA)
| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| Framework | Quasar 2.x (Vue 3 + Vite) | SPA, PWA, SSR opcional, Capacitor para móvil nativo |
| UI Components | Quasar Components | Grid, Layout, Forms, Data Table, Dialogs, Notifications |
| State Management | Pinia | Stores reactivos, TypeScript support, devtools |
| Routing | Vue Router 4 | File-based routing, navigation guards, lazy loading |
| HTTP Client | Axios | Interceptors, auth JWT, retry, cancel tokens |
| Mapas | Leaflet 1.9+ / MapLibre GL JS | Mapa base, marcadores, routing, clustering |
| PWA | Workbox (@quasar/pwa) | Cache assets, network-first API, Push API, Background Sync |
| i18n | Vue I18n 9 | Composables, lazy loading locales, es-MX |
| Testing | Vitest + Playwright | Unit/integration + E2E cross-browser |

### Backend API (Django REST Framework)
| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| Framework | Django 5.x + DRF 3.14+ | Serializers, ViewSets, Routers, Permissions, Throttling |
| Auth | djangorestframework-simplejwt | JWT Access/Refresh tokens, rotation, blacklist |
| Schema | drf-spectacular | OpenAPI 3 auto-generado, Swagger UI, Redoc |
| Filters | django-filter | FilterSet, SearchFilter, OrderingFilter |
| Tiempo Real | Django Channels + Redis | WebSockets para notificaciones, chat |
| Tasks | Celery + Redis | Background: email, push, limpieza, reportes |
| Geo | GeoDjango + PostGIS | PointField, PolygonField, ST_DWithin, ST_MakeLine |

### Base de Datos
| Componente | Tecnología | Configuración clave |
|------------|------------|---------------------|
| Motor | PostgreSQL 16+ | ACID, JSONB, partitioning |
| Extensión | PostGIS 3.4+ | Geometry/geography, GiST indexes |
| Índices críticos | GIST (geom), BRIN (fecha), Partial UNIQUE, Composite, JSONB GIN | Búsqueda radial, particionado temporal, anti-duplicados |
| Pooling | PgBouncer (prod) | Transaction mode |
| Conexiones | CONN_MAX_AGE=60, ATOMIC_REQUESTS=True | Persistent + transacción por request |
| Dev local | Docker Compose (PostgreSQL+PostGIS) | Paridad 1:1 con producción |

---

## Arquitectura por Capas (Backend)

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION (Quasar SPA)                │
│  pages, components, stores (Pinia), composables             │
│                    │                                        │
│                    ▼ (HTTP/WS API)                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              BACKEND API (Django REST Framework)    │   │
│  │  api app: serializers, viewsets, permissions, urls  │   │
│  │                    │                                │   │
│  │                    ▼ (usa interfaces)               │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │              DOMAIN (Pure Python)           │   │   │
│  │  │  entities, value_objects, services,         │   │   │
│  │  │  repositories (interfaces), events, exceptions│   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  │                    ▲                                │   │
│  │                    │ (implementa interfaces)        │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │              INFRASTRUCTURE                 │   │   │
│  │  │  django_repositories, geo, notifications,   │   │   │
│  │  │  storage, security, tasks                   │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Regla de Dependencias**:
- `domain` **nunca** importa de `infrastructure` ni `presentation`
- `presentation` (Quasar) consume API REST/GraphQL del backend
- `api` (DRF) importa de `domain` (services + repository interfaces)
- `infrastructure` implementa interfaces de `domain.repositories`

---

## Estructura de Carpetas

### Backend (raite-backend/)
```
raite-backend/
├── config/                     # Configuración Django
│   ├── settings/               # base, development, production, testing
│   ├── wsgi.py, asgi.py, urls.py
├── domain/                     # CAPA DE DOMINIO (Pure Python)
│   ├── entities/               # User, Trip, Vehicle, Campus, Rating
│   ├── value_objects/          # Coordinate, TimeWindow, Capacity, Preference
│   ├── services/               # MatchingService, ReputationService, etc.
│   ├── repositories/           # Interfaces (Protocol/ABC)
│   ├── events/                 # Domain events + event_bus
│   └── exceptions/             # Excepciones de dominio
├── infrastructure/             # CAPA DE INFRAESTRUCTURA
│   ├── django_repositories/    # Implementaciones con Django ORM
│   ├── geo/                    # PostGISAdapter, OSRM, Nominatim, MapTiles
│   ├── notifications/          # Email, Push, WebSocket, In-app
│   ├── storage/                # S3/R2/Cloudflare, Whitenoise
│   ├── security/               # RateLimit, CSP, CSRF, Sanitizer
│   └── tasks/                  # Celery tasks
├── presentation/               # CAPA DE PRESENTACIÓN - API REST
│   ├── api/                    # DRF: serializers, viewsets, urls, permissions
│   ├── websocket/              # Channels: consumers, routing, middleware
│   └── core/                   # Health checks, API root
├── tests/                      # Tests por capa (domain, infrastructure, presentation, e2e)
├── docs/                       # MkDocs + ADRs
├── scripts/                    # Seed data, test data generation
├── Dockerfile, docker-compose.yml, pyproject.toml, requirements/, Makefile
```

### Frontend (raite-frontend/)
```
raite-frontend/
├── src/
│   ├── assets/                 # Imágenes, fuentes, estilos globales
│   ├── components/             # Componentes Vue reutilizables
│   │   ├── common/             # Button, Input, Card, Modal, Toast
│   │   ├── map/                # MapView, MarkerCluster, RoutePolyline
│   │   ├── trip/               # TripCard, TripForm, TripSearch, TripDetail
│   │   ├── user/               # UserAvatar, UserProfile, RatingStars
│   │   └── layout/             # AppHeader, AppFooter, AppDrawer
│   ├── composables/            # useApi, useAuth, useTrips, useMap, useNotifications
│   ├── layouts/                # MainLayout, AuthLayout, EmptyLayout
│   ├── pages/                  # File-based routing (auth, trips, profile, notifications)
│   ├── router/                 # Vue Router + guards (auth, verified, role)
│   ├── stores/                 # Pinia: auth, trips, map, notifications, ui
│   ├── services/               # apiClient, authApi, tripsApi, usersApi, ratingsApi
│   ├── utils/                  # date, validation, geo, constants, helpers
│   ├── plugins/                # axios, pinia, leaflet, maplibre, i18n, pwa
│   ├── styles/                 # SCSS: variables, globals, components, quasar overrides
│   ├── App.vue, main.js
├── public/                     # manifest.json, icons, raite
├── tests/                      # Vitest (unit) + Playwright (e2e)
├── quasar.config.js, package.json, .eslintrc.cjs, .prettierrc
```

---

## Flujo de Datos Principal

1. **Usuario abre la app** → Quasar SPA carga (PWA instalable)
2. **Login/Register** → Quasar llama `/api/v1/auth/login/` → DRF valida + devuelve JWT
3. **Buscar viajes** → Quasar `useTrips.search()` → GET `/api/v1/trips/?origin=...&dest=...&date=...`
4. **Backend matching** → DRF ViewSet → MatchingService (domain) → DjangoTripRepository (infra) → PostGIS ST_DWithin
5. **Resultados** → Serializer → JSON → Quasar store → Reactividad UI
6. **Solicitar plaza** → POST `/api/v1/trips/{id}/request/` → Domain Event `SeatRequested` → Notificaciones (email, push, WS)
7. **Tiempo real** → WebSocket `/ws/notifications/` → Django Channels → Quasar `useNotifications` → Toast/badge reactivo

---

## Despliegue e Infraestructura

| Componente | Opción Recomendada | Alternativas |
|------------|-------------------|--------------|
| Backend Hosting | Render (Web Service) | Railway, Fly.io, Koyeb, AWS ECS/Fargate |
| Frontend Hosting | Vercel / Netlify / Cloudflare Pages | Render Static, AWS S3+CloudFront |
| Database | Aiven PostgreSQL + PostGIS | Neon, Supabase, Render PG, AWS RDS |
| Redis | Upstash / Redis Cloud | Aiven Redis, Render Redis |
| Static/Media CDN | Cloudflare R2 + Cloudflare CDN | AWS S3+CloudFront, Cloudinary |
| Domain/DNS | PorkBun / Cloudflare | Namecheap, GoDaddy |
| TLS/SSL | Automático (Let's Encrypt) | Cloudflare Universal SSL |

---

## CI/CD Pipeline

| Etapa | Herramienta | Detalle |
|-------|-------------|---------|
| Source Control | GitHub | Repo privado, branch protection, required reviews |
| CI Backend | GitHub Actions | Matrix: lint (ruff) → typecheck (mypy) → test (pytest) → build Docker |
| CI Frontend | GitHub Actions | lint (ESLint) → typecheck → unit (Vitest) → build (Vite) → E2E (Playwright) |
| CD Staging | GitHub Actions | Deploy auto en push a `main` (backend + frontend) |
| CD Production | GitHub Actions | Deploy manual (workflow_dispatch) o tag `v*` |
| Docker | Multi-stage build | Builder → runtime slim (python:3.11-slim / node:20-alpine), non-root user |
| Security | Trivy / Snyk / CodeQL | Scan imagen + dependencias en PR |

---

## Observabilidad

| Área | Herramienta | Qué Mide |
|------|-------------|----------|
| Error Tracking | Sentry | Exceptions, traces, release health, user feedback (backend + frontend) |
| APM | Sentry / Datadog | Latencia p95, DB queries lentas, throughput |
| Logs | Logtail / Better Stack | JSON logs: request_id, user_id, trip_id, level |
| Uptime | Uptime Robot / Better Stack | HTTPS checks /health/, /api/health/ |
| Métricas Negocio | Custom (Prometheus + Grafana) | Viajes activos, solicitudes/min, conversión, rating |
| Health Checks | Django `/health/` + Quasar `/health` | DB, Redis, disk space, migrations |

---

## Architecture Decision Records (ADRs)

| ADR | Título | Estado |
|-----|--------|--------|
| 001 | Layered Architecture + Repository Pattern | Accepted |
| 002 | Domain-Driven Design ligero para dominio | Accepted |
| 003 | Django Channels para WebSockets tiempo real | Accepted |
| 004 | PostGIS para geolocalización y matching espacial | Accepted |
| 005 | Celery + Redis para tareas asíncronas y periódicas | Accepted |
| 006 | PWA con Service Worker + Web Push (VAPID) | Accepted |
| 007 | Quasar (Vue 3) para Frontend SPA/PWA | Accepted |
| 008 | GitHub Actions + Render para CI/CD | Accepted |
| 009 | Sentry + Logtail para observabilidad | Accepted |
| 010 | LFPDPPP compliance by design | Accepted |

---

## Legal y Cumplimiento (México)

| Requisito | Implementación |
|-----------|----------------|
| LFPDPPP | Aviso privacidad, consentimiento explícito, derechos ARCO, DPO designado |
| Términos y Condiciones | Markdown en `/terminos/`, versionado |
| Cookies / Consentimiento | Banner GDPR-style, categorizar: necesarias, analytics, marketing |
| Verificación Identidad | Email @uacj.mx + matrícula (validación regex + lista blanca futura) |
| Reporte Incidentes | Formulario `/reportar/`, canal confidencial, SLA respuesta 48h |