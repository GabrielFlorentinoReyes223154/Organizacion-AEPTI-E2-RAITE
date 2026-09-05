# Arquitectura del Sistema Raite

## Visión General

Raite adopta una **arquitectura por capas (Layered Architecture)** combinada con **Repository Pattern** y principios de **Domain-Driven Design (DDD) ligero**, diseñada para separar responsabilidades, aislar el dominio del framework y facilitar testing, evolución y futura extracción a librería compartida para apps móviles nativas.

La arquitectura sigue un enfoque **API-First** con **Quasar (Vue.js)** como frontend SPA/PWA desacoplado, **Django REST Framework** como backend API, y **PostgreSQL + PostGIS** como base de datos.

---

## Estilo Arquitectónico: Capas + Repository Pattern

### Principios Rectores

1. **Domain-Driven Design (DDD) ligero**: El dominio (entidades, value objects, services, eventos) no depende de Django ni infraestructura
2. **Dependency Rule**: Capas internas no conocen capas externas; dependencias apuntan hacia adentro
3. **Repository Pattern**: Interfaces en `domain/repositories/`, implementaciones en `infrastructure/django_repositories/`
4. **Dependency Injection**: Wireado manual en `apps.py` / `ready()` o con `django-dependency-injector`

### Flujo de Dependencias

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

**Regla**: `domain` **nunca** importa de `infrastructure` ni `presentation`.  
`presentation` (Quasar) consume API REST/GraphQL del backend.  
`api` (DRF) importa de `domain` (services + repository interfaces).  
`infrastructure` implementa interfaces de `domain.repositories`.

---

## Estructura de Carpetas

```
raite-backend/                    # Raíz del proyecto Django (Backend API)
├── config/                       # Configuración Django (settings, wsgi, asgi, urls root)
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── testing.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── urls.py
│
├── domain/                       # CAPA DE DOMINIO (Pure Python, sin Django)
│   ├── __init__.py
│   ├── entities/                 # Entidades de negocio (identidad + ciclo de vida)
│   │   ├── __init__.py
│   │   ├── user.py               # User, StudentProfile, DriverProfile
│   │   ├── trip.py               # Trip (Raite), TripStatus, Seat
│   │   ├── vehicle.py            # Vehicle, Capacity
│   │   ├── campus.py             # Campus, ReferencePoint
│   │   └── rating.py             # Rating, Review
│   ├── value_objects/            # Objetos de valor (inmutables, sin identidad)
│   │   ├── __init__.py
│   │   ├── coordinate.py         # LatLng, SRID 4326
│   │   ├── time_window.py        # DepartureTime, ArrivalWindow
│   │   ├── capacity.py           # SeatsTotal, SeatsAvailable
│   │   ├── preference.py         # GenderPreference, GroupType
│   │   └── reputation.py         # Score, Badge
│   ├── services/                 # Servicios de dominio (lógica de negocio pura)
│   │   ├── __init__.py
│   │   ├── matching_service.py   # Algoritmo matching: puntos ref, horario, prefs
│   │   ├── reputation_service.py # Cálculo rating, badges, trust score
│   │   ├── validation_service.py # Reglas: capacidad, horarios, campus válidos
│   │   └── notification_service.py # Orquestación notificaciones (domain events)
│   ├── repositories/             # INTERFACES (Protocol/ABC) - Contratos
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   ├── trip_repository.py
│   │   ├── vehicle_repository.py
│   │   ├── campus_repository.py
│   │   ├── reference_point_repository.py
│   │   └── rating_repository.py
│   ├── events/                   # Eventos de dominio (para desacoplar side effects)
│   │   ├── __init__.py
│   │   ├── trip_created.py
│   │   ├── seat_requested.py
│   │   ├── seat_accepted.py
│   │   ├── seat_rejected.py
│   │   ├── trip_cancelled.py
│   │   ├── rating_submitted.py
│   │   └── event_bus.py          # Pub/Sub simple in-memory
│   └── exceptions/               # Excepciones de dominio
│       ├── __init__.py
│       ├── trip_full.py
│       ├── invalid_preference.py
│       ├── user_not_verified.py
│       └── matching_failed.py
│
├── infrastructure/               # CAPA DE INFRAESTRUCTURA (Implementaciones concretas)
│   ├── __init__.py
│   ├── django_repositories/      # Implementaciones Repository con Django ORM
│   │   ├── __init__.py
│   │   ├── django_user_repository.py
│   │   ├── django_trip_repository.py
│   │   ├── django_vehicle_repository.py
│   │   ├── django_campus_repository.py
│   │   ├── django_reference_point_repository.py
│   │   └── django_rating_repository.py
│   ├── geo/                      # Adaptadores geoespaciales
│   │   ├── __init__.py
│   │   ├── postgis_adapter.py    # Queries ST_DWithin, ST_MakeLine, ST_Buffer
│   │   ├── osrm_client.py        # Cliente OSRM/Valhalla (rutas, ETA)
│   │   ├── nominatim_client.py   # Geocodificación direcciones → coords
│   │   └── map_tiles.py          # Proveedores tiles: OSM, Mapbox, Stadia
│   ├── notifications/            # Canales de notificación
│   │   ├── __init__.py
│   │   ├── email_sender.py       # Anymail (SendGrid/Brevo)
│   │   ├── push_notifier.py      # Web Push (VAPID), FCM
│   │   ├── websocket_publisher.py # Django Channels group_send
│   │   └── in_app_notifier.py    # django-notifications-hq
│   ├── storage/                  # Almacenamiento archivos
│   │   ├── __init__.py
│   │   ├── media_storage.py      # S3/R2/Cloudflare (django-storages)
│   │   └── static_storage.py     # Whitenoise / CDN
│   ├── security/                 # Seguridad transversal
│   │   ├── __init__.py
│   │   ├── rate_limiter.py       # django-ratelimit wrapper
│   │   ├── csrf_protection.py
│   │   └── content_sanitizer.py  # bleach wrapper
│   └── tasks/                    # Tareas asíncronas (Celery)
│       ├── __init__.py
│       ├── email_tasks.py
│       ├── notification_tasks.py
│       ├── cleanup_tasks.py
│       └── stats_tasks.py
│
├── presentation/                 # CAPA DE PRESENTACIÓN - API REST (Django REST Framework)
│   ├── __init__.py
│   ├── api/                      # App: API REST (DRF)
│   │   ├── __init__.py
│   │   ├── serializers.py        # Serializers: TripSerializer, UserSerializer, etc.
│   │   ├── views.py              # ViewSets: TripViewSet, UserViewSet, VehicleViewSet
│   │   ├── urls.py               # Router DRF + custom endpoints
│   │   ├── permissions.py        # IsDriver, IsPassenger, IsOwner, IsVerified
│   │   ├── pagination.py         # Cursor/PageNumber pagination
│   │   ├── filters.py            # Django-filter: búsqueda, ordenamiento
│   │   └── schema.py             # drf-spectacular extensions
│   ├── websocket/                # App: Channels routing (tiempo real)
│   │   ├── __init__.py
│   │   ├── routing.py            # WebSocket URL patterns
│   │   ├── consumers.py          # AsyncWebsocketConsumer (chat, live updates)
│   │   └── middleware.py         # AuthMiddlewareStack custom
│   └── core/                     # App: shared, health checks
│       ├── __init__.py
│       ├── views.py              # HealthCheck, API root, version info
│       ├── urls.py
│       └── permissions.py        # ReadOnly, AdminOnly
│
├── tests/                        # Tests organizados por capa
│   ├── __init__.py
│   ├── domain/                   # Unit tests puros (sin BD, mocks)
│   │   ├── test_matching_service.py
│   │   ├── test_reputation_service.py
│   │   └── test_validation_service.py
│   ├── infrastructure/           # Integration tests (con BD real)
│   │   ├── test_django_trip_repository.py
│   │   └── test_postgis_adapter.py
│   ├── presentation/             # API tests (DRF test client)
│   │   ├── test_trip_api.py
│   │   ├── test_user_api.py
│   │   └── test_auth_api.py
│   ├── e2e/                      # Playwright tests (contra API + Quasar)
│   │   ├── test_register_flow.py
│   │   ├── test_publish_trip_flow.py
│   │   └── test_request_seat_flow.py
│   └── fixtures/                 # Factory Boy factories
│       ├── __init__.py
│       ├── user_factory.py
│       ├── trip_factory.py
│       └── campus_factory.py
│
├── docs/                         # Documentación (MkDocs)
│   ├── adr/                      # Architecture Decision Records
│   │   ├── 001-layered-architecture.md
│   │   ├── 002-repository-pattern.md
│   │   ├── 003-use-django-channels.md
│   │   ├── 004-postgis-for-geo.md
│   │   └── 005-quasar-frontend.md
│   ├── development.md
│   ├── deployment.md
│   ├── contributing.md
│   └── api.md
│
├── scripts/                      # Scripts utilitarios
│   ├── __init__.py
│   ├── seed_campuses.py
│   ├── seed_reference_points.py
│   └── generate_test_data.py
│
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── pyproject.toml                # Config: black, ruff, mypy, pytest, coverage
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   ├── production.txt
│   └── testing.txt
├── .env.example
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── cd-staging.yml
│   │   ├── cd-production.yml
│   │   └── security-scan.yml
│   └── dependabot.yml
├── .pre-commit-config.yaml
├── Makefile                      # Comandos comunes: make test, make lint, make migrate
└── README.md
```

```
raite-frontend/                   # Raíz del proyecto Quasar (Frontend SPA/PWA)
├── src/
│   ├── assets/                   # Assets estáticos (imágenes, fuentes, estilos globales)
│   ├── components/               # Componentes Vue reutilizables
│   │   ├── common/               # Button, Input, Card, Modal, Toast, etc.
│   │   ├── map/                  # MapView, MarkerCluster, RoutePolyline, Geocoder
│   │   ├── trip/                 # TripCard, TripForm, TripSearch, TripDetail
│   │   ├── user/                 # UserAvatar, UserProfile, RatingStars, VerificationBadge
│   │   └── layout/               # AppHeader, AppFooter, AppDrawer, PageContainer
│   ├── composables/              # Composables Vue 3 (lógica reactiva reutilizable)
│   │   ├── useApi.js             # Wrapper Axios/Fetch con interceptors, auth
│   │   ├── useAuth.js            # Login, register, logout, token refresh, user state
│   │   ├── useTrips.js           # CRUD viajes, matching, solicitudes
│   │   ├── useMap.js             # Leaflet/MapLibre init, markers, routing
│   │   ├── useNotifications.js   # WebSocket, push, in-app notifications
│   │   └── useGeolocation.js     # Browser Geolocation API wrapper
│   ├── layouts/                  # Layouts Quasar (MainLayout, AuthLayout, EmptyLayout)
│   │   ├── MainLayout.vue
│   │   ├── AuthLayout.vue
│   │   └── EmptyLayout.vue
│   ├── pages/                    # Páginas (rutas) - File-based routing
│   │   ├── IndexPage.vue         # Landing / Dashboard
│   │   ├── auth/
│   │   │   ├── LoginPage.vue
│   │   │   ├── RegisterPage.vue
│   │   │   ├── VerifyEmailPage.vue
│   │   │   └── ForgotPasswordPage.vue
│   │   ├── trips/
│   │   │   ├── ListPage.vue      # Búsqueda y lista de viajes
│   │   │   ├── CreatePage.vue    # Publicar nuevo viaje
│   │   │   ├── DetailPage.vue    # Detalle de viaje + mapa
│   │   │   ├── MyTripsPage.vue   # Mis viajes (conductor/pasajero)
│   │   │   └── RequestsPage.vue  # Solicitudes recibidas/enviadas
│   │   ├── profile/
│   │   │   ├── ProfilePage.vue
│   │   │   ├── EditProfilePage.vue
│   │   │   ├── VehiclePage.vue
│   │   │   └── SettingsPage.vue
│   │   ├── notifications/
│   │   │   └── ListPage.vue
│   │   ├── ratings/
│   │   │   ├── ReceivedPage.vue
│   │   │   └── GivePage.vue
│   │   └── ErrorNotFound.vue     # 404
│   ├── router/                   # Vue Router config
│   │   ├── index.js              # Rutas + guards (auth, verified, role)
│   │   └── routes.js             # Definición de rutas
│   ├── stores/                   # Pinia stores (estado global)
│   │   ├── auth.js               # user, token, permissions
│   │   ├── trips.js              # trips, filters, pagination, matching results
│   │   ├── map.js                # map instance, markers, selected location
│   │   ├── notifications.js      # unread count, list, websocket connection
│   │   └── ui.js                 # loading, toasts, dialogs, drawer state
│   ├── services/                 # Servicios de API (capa de datos)
│   │   ├── apiClient.js          # Instancia Axios configurada (baseURL, interceptors)
│   │   ├── authApi.js            # login, register, refresh, verify, password reset
│   │   ├── tripsApi.js           # CRUD trips, search, match, requests, cancel
│   │   ├── usersApi.js           # profile, vehicle, preferences, verification
│   │   ├── ratingsApi.js         # submit, list, stats
│   │   └── notificationsApi.js   # list, markRead, subscribe
│   ├── utils/                    # Utilidades puras (sin dependencias Vue)
│   │   ├── date.js               # Formateo, timezones, relative time
│   │   ├── validation.js         # Reglas validación (email, matricula, phone)
│   │   ├── geo.js                # Distance, bounds, coordinate formatting
│   │   ├── constants.js          # Enums: TripStatus, UserRole, GenderPreference
│   │   └── helpers.js            # Debounce, throttle, deepClone, formatNumber
│   ├── plugins/                  # Plugins Quasar/Vue (boot files)
│   │   ├── axios.js              # Config global Axios
│   │   ├── pinia.js              # Pinia store registration
│   │   ├── leaflet.js            # Leaflet CSS/JS global setup
│   │   ├── maplibre.js           # MapLibre GL JS setup (opcional)
│   │   ├── i18n.js               # Vue I18n (es-MX)
│   │   └── pwa.js                # Workbox, service worker registration
│   ├── styles/                   # Estilos globales (SCSS)
│   │   ├── variables.scss        # Colores UACJ, spacing, breakpoints, z-index
│   │   ├── globals.scss          # Reset, typography, utility classes
│   │   ├── components.scss       # Estilos componentes comunes
│   │   └── quasar.scss           # Overrides Quasar theme (primary, secondary, etc.)
│   ├── App.vue                   # Componente raíz
│   └── main.js                   # Entry point: createApp, router, pinia, plugins
├── public/                       # Assets públicos (copiados tal cual a dist/)
│   ├── manifest.json             # PWA Manifest
│   ├── icons/                    # PWA icons (generados con pwa-asset-generator)
│   └── favicon.ico
├── tests/                        # Tests frontend
│   ├── unit/                     # Vitest: composables, stores, utils, components
│   │   ├── composables/
│   │   ├── stores/
│   │   └── utils/
│   ├── e2e/                      # Playwright/Cypress: flujos críticos
│   │   ├── auth.spec.js
│   │   ├── trips.spec.js
│   │   └── map.spec.js
│   └── setup.js                  # Config global tests
├── .github/
│   └── workflows/
│       ├── ci.yml                # Lint, typecheck, unit test, build
│       └── e2e.yml               # Playwright E2E contra staging
├── quasar.config.js              # Config Quasar (Vite, PWA, SSR, Cordova, Capacitor)
├── package.json
├── pnpm-lock.yaml / package-lock.json
├── .env.example
├── .eslintrc.cjs
├── .prettierrc
├── tsconfig.json (opcional)      # Si se usa TypeScript
├── vite.config.js (extendido)    # Config Vite adicional
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Stack Tecnológico por Capa

### Backend Core
| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| Framework | Django 5.x | Routing, ORM, middleware, admin, security |
| Lenguaje | Python 3.11+ | Base |
| ASGI | asgiref 3.x | Soporte async y WebSockets |
| Configuración | python-dotenv, dj-database-url | 12-factor env |

### Autenticación y Autorización
| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| Auth base | Django Auth System | User model, login/logout, permissions, groups |
| Social/2FA | django-allauth | Google, Microsoft/Outlook UACJ, email verification, TOTP |
| Brute-force | django-axes | Bloqueo IP/user |
| Headers | django-csp, django-cors-headers | CSP, CORS para API/SPA futura |

### Geolocalización y Mapas (Backend)
| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| ORM espacial | GeoDjango | PointField, PolygonField, lookups espaciales |
| BD espacial | PostGIS 3.4+ | Índices GiST/GiN, ST_Distance, ST_MakeLine, ST_Buffer |
| Geocodificación | geopy / Nominatim | Direcciones → coordenadas (server-side) |
| Rutas | OSRM / Valhalla | Cálculo rutas y tiempos (self-hosted o API) |

### Tiempo Real y Procesamiento Asíncrono
| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| WebSockets | Django Channels | Notificaciones push, chat conductor-pasajero |
| Message broker | Redis | Channel layer, cache, rate limiting, session store |
| Tasks | Celery + Redis | Background: email, push, limpieza, reportes |
| Notifs in-app | django-notifications-hq | Modelo, API, templates |
| Periodic tasks | Celery Beat | Expirar viajes, recordatorios, stats |

### Backend API (Django REST Framework)
| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| Framework | Django REST Framework 3.14+ | Serializers, ViewSets, Routers, Permissions, Throttling |
| Auth | djangorestframework-simplejwt | JWT Access/Refresh tokens, rotation, blacklist |
| Schema | drf-spectacular | OpenAPI 3 auto-generado, Swagger UI, Redoc |
| Filters | django-filter | FilterSet, SearchFilter, OrderingFilter |
| Pagination | DRF built-in | CursorPagination, PageNumberPagination |
| Versioning | DRF URLPathVersioning | /api/v1/, /api/v2/ |

### Frontend (Quasar SPA/PWA)
| Área | Tecnología | Propósito |
|------|------------|-----------|
| Framework | Quasar 2.x (Vue 3 + Vite) | SPA, PWA, SSR opcional, Capacitor/Cordova para móvil |
| UI Components | Quasar Components | Grid, Layout, Forms, Data Table, Dialogs, Notifications |
| CSS | Quasar (SCSS) + Tailwind opcional | Design system, theming, dark mode, responsive |
| State Management | Pinia | Stores reactivos, TypeScript support, devtools |
| Routing | Vue Router 4 | File-based routing, navigation guards, lazy loading |
| HTTP Client | Axios | Interceptors, auth, retry, cancel tokens |
| Mapas | Leaflet 1.9+ / MapLibre GL JS | Mapa base, marcadores, routing, clustering |
| PWA | Workbox (Quasar @quasar/pwa) | Cache assets, network-first API, Push API, Background Sync |
| i18n | Vue I18n 9 | gettext, composables, lazy loading locales |
| Testing | Vitest + Vue Test Utils | Unit/integration components, composables, stores |
| E2E | Playwright | Flujos críticos cross-browser |
| Lint/Format | ESLint + Prettier + @quasar/eslint-config | Code quality, Vue/Quasar rules |

### Base de Datos
| Componente | Tecnología | Configuración clave |
|------------|------------|---------------------|
| Motor | PostgreSQL 16+ | ACID, JSONB, partitioning |
| Extensión | PostGIS 3.4+ | Geometry/geography, GiST indexes |
| Índices críticos | GIST (geom), BRIN (fecha), Partial UNIQUE, Composite, JSONB GIN | Búsqueda radial, particionado temporal, anti-duplicados, filtros compuestos |
| Pooling | PgBouncer (prod) | Transaction mode |
| Conexiones | CONN_MAX_AGE=60, ATOMIC_REQUESTS=True | Persistent + transacción por request |
| Dev local | Docker Compose (PostgreSQL+PostGIS) | Paridad 1:1 con producción |

### Archivos y Media
| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| Procesamiento | Pillow + django-imagekit | Resize, crop, WebP, thumbnails, responsive variants |
| Validación | python-magic | MIME real (no extension) |
| Storage prod | django-storages + Cloudflare R2/S3 | Media/static remoto |

### Email y Comunicación
| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| Backend | django-anymail | SendGrid, Brevo, Mailgun, Postmark unificado |
| Templates | HTML/TXT responsivos | Verificación, solicitud, recordatorio |

### Seguridad y Hardening
| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| Rate limit | django-ratelimit | Búsqueda, registro, login |
| Headers | django-secure / django-csp | HSTS, CSP, X-Frame, Referrer-Policy |
| Sanitización | bleach | HTML en inputs usuario (bio, comentarios) |
| Tokens | cryptography | Firmados (email verification, password reset, invites) |

### Internacionalización
| Componente | Tecnología | Configuración |
|------------|------------|---------------|
| i18n | Django i18n | gettext, .po files, LANGUAGE_CODE='es-mx' |
| Localización | Babel / django-countries | Países, monedas, formatos fecha/hora |
| Timezone | tzdata | America/Ciudad_Juarez |

---

## Infraestructura, CI/CD y Observabilidad

### CI/CD Pipeline
| Etapa | Herramienta | Detalle |
|-------|-------------|---------|
| Source Control | GitHub | Repo privado, branch protection, required reviews |
| CI | GitHub Actions | Matrix: lint → typecheck → test → build Docker |
| CD Staging | GitHub Actions + Render/Railway | Deploy auto en push a `main` |
| CD Production | GitHub Actions + Render/Railway | Deploy manual (workflow_dispatch) o tag `v*` |
| Docker | Multi-stage build | Builder → runtime slim (python:3.11-slim), non-root user |
| Security | Trivy / Snyk / CodeQL | Scan imagen + dependencias en PR |

### Control de Versiones
- **Conventional Commits**: `feat:`, `fix:`, `refactor:`, `chore:`, `docs:` → changelog auto
- **GitHub Flow**: `main` siempre deployable, feature branches cortas, PR + squash merge
- **GitHub Projects (Kanban)**: Sprint board
- **Semantic Versioning**: `MAJOR.MINOR.PATCH` tags
- **Release Drafter**: Release notes automático

### Testing y Calidad
| Tipo | Herramientas | Cobertura Objetivo |
|------|--------------|-------------------|
| Unit (Backend) | pytest, pytest-django, factory_boy | >80% models/services |
| Unit (Frontend) | Vitest, Vue Test Utils, @pinia/testing | >80% composables/stores/utils |
| Integration (Backend) | pytest + DRF test client | API endpoints, auth, permissions |
| Integration (Frontend) | Vitest + MSW (Mock Service Worker) | API integration, stores |
| E2E | Playwright (Chromium/Firefox/WebKit) | Flujos críticos cross-browser |
| Contract | schemathesis / Pact | OpenAPI spec vs implementación |
| Static Analysis (Backend) | ruff, mypy + django-stubs, bandit | 0 errors en CI |
| Static Analysis (Frontend) | ESLint, TypeScript (opcional), Vue TSC | 0 errors en CI |
| Format (Backend) | black + isort | Pre-commit + CI check |
| Format (Frontend) | Prettier + ESLint --fix | Pre-commit + CI check |
| Performance | locust / k6 (opcional) | Load test endpoints críticos |

### Hosting e Infraestructura (Producción)
| Componente | Opción Recomendada | Alternativas |
|------------|-------------------|--------------|
| App Hosting | Render (Web Service) | Railway, Fly.io, Koyeb, AWS ECS/Fargate |
| Database | Aiven PostgreSQL + PostGIS | Neon, Supabase, Render PG, AWS RDS |
| Redis | Upstash / Redis Cloud | Aiven Redis, Render Redis |
| Static/Media CDN | Cloudflare R2 + Cloudflare CDN | AWS S3+CloudFront, Cloudinary |
| Domain/DNS | PorkBun / Cloudflare | Namecheap, GoDaddy |
| TLS/SSL | Automático (Let's Encrypt) | Cloudflare Universal SSL |

### Observabilidad
| Área | Herramienta | Qué Mide |
|------|-------------|----------|
| Error Tracking | Sentry | Exceptions, traces, release health, user feedback |
| APM | Sentry / Datadog / Elastic APM | Latencia p95, DB queries lentas, throughput |
| Logs | Logtail / Better Stack / Papertrail | JSON logs: request_id, user_id, trip_id, level |
| Uptime | Uptime Robot / Better Stack | HTTPS checks /health/, alertas |
| Métricas Negocio | Custom (Prometheus + Grafana opcional) | Viajes activos, solicitudes/min, conversión, rating |
| Health Checks | Django `/health/` endpoint | DB, Redis, disk space, migrations |

### Seguridad Operacional
| Práctica | Herramienta/Config |
|----------|-------------------|
| Secrets | GitHub Environments + Encrypted Secrets / 1Password CLI / Doppler |
| Dependency Scanning | Dependabot + auto-PR / Snyk / Trivy |
| SAST/DAST | GitHub CodeQL (PR), OWASP ZAP (staging) |
| Backup | PITR (Aiven/Neon), daily pg_dump a R2/S3, test restore mensual |
| Incident Response | Runbook en docs/, escalation: PagerDuty / Opsgenie |

### Documentación
| Tipo | Herramienta | Ubicación |
|------|-------------|-----------|
| Técnica | MkDocs + Material theme | `raite-backend/docs/` → GitHub Pages / ReadTheDocs |
| API | drf-spectacular → Redoc/Swagger UI | `/api/docs/`, `/api/redoc/` |
| Arquitectura (ADR) | Markdown en `docs/adr/` | `001-use-django-channels.md`, etc. |
| Onboarding | `CONTRIBUTING.md`, `DEVELOPMENT.md`, `DEPLOYMENT.md` | Root repo (backend + frontend) |
| Changelog | Release Drafter | `CHANGELOG.md` auto |

### Legal y Cumplimiento (México)
| Requisito | Implementación |
|-----------|----------------|
| LFPDPPP | Aviso privacidad, consentimiento explícito, derechos ARCO, DPO designado |
| Términos y Condiciones | Markdown en `/terminos/`, versionado |
| Cookies | Banner GDPR-style, categorizar: necesarias, analytics, marketing |
| Verificación Identidad | Email @uacj.mx + matrícula (regex + lista blanca futura) |
| Reporte Incidentes | Formulario `/reportar/`, canal confidencial, SLA 48h |

---

## Ejemplo: Wireado en `apps.py` (Backend API)

```python
# presentation/api/apps.py
from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'presentation.api'
    verbose_name = 'API REST'

    def ready(self):
        # Dependency Injection manual
        from domain.services.matching_service import MatchingService
        from domain.services.reputation_service import ReputationService
        from domain.repositories.trip_repository import TripRepository
        from domain.repositories.reference_point_repository import ReferencePointRepository
        from infrastructure.django_repositories.django_trip_repository import DjangoTripRepository
        from infrastructure.django_repositories.django_reference_point_repository import DjangoReferencePointRepository

        trip_repo: TripRepository = DjangoTripRepository()
        ref_point_repo: ReferencePointRepository = DjangoReferencePointRepository()

        MatchingService.set_repositories(trip_repo, ref_point_repo)
        ReputationService.set_trip_repository(trip_repo)

        # Signals → Domain Events
        from django.db.models.signals import post_save
        from presentation.api.models import Trip, TripRequest, Rating
        from domain.events import TripCreated, SeatRequested, RatingSubmitted, event_bus

        def emit_trip_created(sender, instance, created, **kwargs):
            if created:
                event_bus.publish(TripCreated(trip_id=instance.id, driver_id=instance.driver_id))

        def emit_seat_requested(sender, instance, created, **kwargs):
            if created:
                event_bus.publish(SeatRequested(request_id=instance.id, trip_id=instance.trip_id))

        def emit_rating_submitted(sender, instance, created, **kwargs):
            if created:
                event_bus.publish(RatingSubmitted(rating_id=instance.id, to_user_id=instance.to_user_id))

        post_save.connect(emit_trip_created, sender=Trip)
        post_save.connect(emit_seat_requested, sender=TripRequest)
        post_save.connect(emit_rating_submitted, sender=Rating)
```

## Ejemplo: Boot File Quasar (Frontend)

```javascript
// raite-frontend/src/boot/axios.js
import { useAuthStore } from 'stores/auth'
import { apiClient } from 'services/apiClient'

export default async ({ app }) => {
  // Interceptor request: adjuntar token
  apiClient.interceptors.request.use((config) => {
    const authStore = useAuthStore()
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    return config
  })

  // Interceptor response: refresh token en 401
  apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true
        const authStore = useAuthStore()
        try {
          await authStore.refreshAccessToken()
          originalRequest.headers.Authorization = `Bearer ${authStore.accessToken}`
          return apiClient(originalRequest)
        } catch (e) {
          authStore.logout()
          return Promise.reject(e)
        }
      }
      return Promise.reject(error)
    }
  )
}
```

---

## Ventajas para Raite

| Beneficio | Cómo se logra |
|-----------|---------------|
| **Testabilidad** | `MatchingService` se prueba con `FakeTripRepository` en memoria (sin BD, sin Django) |
| **Intercambiabilidad** | Cambiar `DjangoTripRepository` → `SQLAlchemyTripRepository` o `CachedTripRepository` (Redis) sin tocar dominio |
| **Geo aislado** | `PostGISAdapter` encapsula SQL espacial; dominio usa `Coordinate` + `Distance` value objects |
| **Eventos desacoplados** | `TripCreated` → notifica email, push, websocket, stats sin acoplar emisor a receptores |
| **Onboarding** | Nuevo dev entiende dominio leyendo `domain/` sin saber Django |
| **Migración futura** | Extraer `domain/` a librería compartida si hay app móvil nativa (React Native, Flutter) |

---

## Cuándo NO usar (y mantener simple)

- MVP < 3 sprints: Django "fat models" + views + forms es suficiente
- Equipo < 3 devs: Overhead de DI y capas puede ralentizar
- Sin lógica de matching compleja: CRUD simple → Repository Pattern añade indireccion innecesaria

**Recomendación**: Inicia con `services/` + `repositories/` dentro de apps Django. Extrae `domain/` paquete separado en Sprint 3-4 cuando matching y reputación crezcan.

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