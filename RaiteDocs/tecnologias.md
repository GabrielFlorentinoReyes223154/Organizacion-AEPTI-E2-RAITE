# Tecnologías Propuestas para Raite

---

## 1. BACKEND

### 1.1 Framework y Núcleo
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Django | 5.x | Framework principal: routing, ORM, middleware, admin, security |
| Python | 3.11+ | Lenguaje base |
| asgiref | 3.x | Interfaz ASGI para soporte async y WebSockets futuros |

### 1.2 Configuración y Entorno
| Tecnología | Propósito |
|------------|-----------|
| python-dotenv | Carga variables desde `.env` (secrets, DEBUG, URLs) |
| dj-database-url | Parse `DATABASE_URL` a dict de configuración Django |
| django-environ | (Alternativa) Configuración 12-factor más robusta |

### 1.3 Autenticación y Autorización
| Tecnología | Propósito |
|------------|-----------|
| Django Auth System | User model, login/logout, password reset, permissions, groups |
| django-allauth | Social login (Google, Microsoft/Outlook UACJ), email verification, 2FA (TOTP) |
| django-axes | Bloqueo por fuerza bruta en login (IP/user) |
| django-csp | Content Security Policy headers |
| django-cors-headers | CORS para API/SPA futura |

### 1.4 Lógica de Negocio / Dominio
| Componente | Propósito |
|------------|-----------|
| Modelos Django | Usuario, Perfil, Vehículo, Raite, Solicitud, Calificación, Notificación, Campus, PuntoReferencia |
| Managers/Querysets | Filtros reutilizables (viajes activos, por campus, por horario) |
| Services layer | Lógica de matching (puntos ref, horario, preferencias), reglas de capacidad, validaciones |
| Signals | Side effects: crear notificación al solicitar, actualizar rating al calificar |
| Validators | Validación de dominio (horarios, capacidad, puntos UACJ) |

### 1.5 Enrutamiento y APIs
| Tecnología | Propósito |
|------------|-----------|
| Django URLs | `path()`/`re_path()` para vistas servidor (SSR) |
| Django REST Framework (opcional) | API REST si se expone a móvil/terceros (serializers, viewsets, routers) |
| drf-spectacular | OpenAPI 3 schema auto-generado para docs API |

### 1.6 Geolocalización y Mapas (Backend)
| Tecnología | Propósito |
|------------|-----------|
| GeoDjango | Campos `PointField`, `PolygonField`, lookups espaciales (`distance_lte`, `intersects`) |
| PostGIS | Índices GiST/GiN, funciones ST_Distance, ST_MakeLine, ST_Buffer |
| geopy / Nominatim | Geocodificación direcciones → coordenadas (server-side) |
| OSRM / Valhalla | Cálculo de rutas y tiempos (self-hosted o API) |

### 1.7 Procesamiento Asíncrono y Tiempo Real
| Tecnología | Propósito |
|------------|-----------|
| Django Channels | WebSockets para notificaciones push, chat conductor-pasajero |
| Redis | Channel layer (pub/sub), cache, rate limiting, session store |
| Celery + Redis | Tareas background: email, push notifications, limpieza, reportes |
| django-notifications-hq | Sistema notificaciones in-app (modelo, API, temps) |
| Celery Beat | Tareas periódicas: expirar viajes pasados, recordatorios, stats |

### 1.8 Archivos y Media
| Tecnología | Propósito |
|------------|-----------|
| Pillow | Resize, crop, optimización, conversión formatos (perfil, vehículo) |
| django-imagekit | Specs automáticos: thumbnails, webp, responsive variants |
| python-magic | Validación MIME real (no confiar en extension) |
| django-storages + S3/R2 | Storage remoto en producción (media/static) |

### 1.9 Email y Comunicación
| Tecnología | Propósito |
|------------|-----------|
| django-anymail | Backend unificado (SendGrid, Brevo, Mailgun, Postmark) |
| Templates HTML/TXT | Emails transaccionales responsivos (verificación, solicitud, recordatorio) |

### 1.10 Seguridad y Hardening
| Tecnología | Propósito |
|------------|-----------|
| django-ratelimit | Rate limit en vistas/APIs (búsqueda, registro, login) |
| django-secure / django-csp | HSTS, CSP, X-Frame, Referrer-Policy, Permissions-Policy |
| bleach | Sanitización HTML en inputs usuario (bio, comentarios) |
| cryptography | Tokens firmados (email verification, password reset, invites) |

### 1.11 Internacionalización y Localización
| Tecnología | Propósito |
|------------|-----------|
| Django i18n | `gettext`, `.po` files, `LANGUAGE_CODE = 'es-mx'` |
| Babel / django-countries | Localización de países, monedas, formatos fecha/hora |
| tzdata | Zona horaria `America/Ciudad_Juarez` |

### 1.12 Utilidades de Desarrollo
| Tecnología | Propósito |
|------------|-----------|
| django-extensions | `shell_plus`, `runserver_plus`, `graph_models`, `dumpdata` |
| django-debug-toolbar | Profiling queries, templates, cache, signals (solo DEBUG) |
| Werkzeug debugger | Better tracebacks en `runserver_plus` |

---

## 2. FRONTEND (SSR + Progressive Enhancement)

### 2.1 Plantillas y Renderizado
| Tecnología | Propósito |
|------------|-----------|
| Django Templates | SSR nativo: `{% include %}`, `{% extends %}`, template tags/filters custom |
| Template fragments / partials | Reutilización: `_trip_card.html`, `_notification_bell.html`, `_map_modal.html` |
| django-widget-tweaks | Render forms Bootstrap sin escribir HTML manual |

### 2.2 Framework CSS y Componentes
| Tecnología | Propósito |
|------------|-----------|
| Bootstrap 5.3+ | Grid, utilities, components (modal, dropdown, toast, accordion, forms) |
| Bootstrap Icons | Iconografía SVG consistente (200+ icons) |
| SCSS/Sass (opcional) | Variables, mixins, nesting para theme custom (colores UACJ) |

### 2.3 Mapas e Interacción Geo
| Tecnología | Propósito |
|------------|-----------|
| Leaflet 1.9+ / MapLibre GL JS | Mapa base vectorial/raster, marcadores, popups, clustering |
| Leaflet Routing Machine / MapLibre Navigation | Visualización ruta origen-destino con waypoints |
| Leaflet.Control.Geocoder | Buscador de lugares en mapa (Nominatim/Mapbox) |
| Leaflet.MarkerCluster | Agrupar puntos de referencia cercanos |

### 2.4 UI/UX Libraries
| Tecnología | Propósito |
|------------|-----------|
| AOS (Animate On Scroll) | Animaciones entrada scroll (landing, stats) |
| GLightbox | Lightbox accesible para galerías (foto perfil, vehículo, campus) |
| Swiper | Carrusel: testimonios, viajes recientes, campus destacados |
| PureCounter | Contadores animados (viajes, usuarios, CO₂ ahorrado, rating) |
| Flatpickr / Tom Select | Date/time picker, selects buscables (campus, puntos ref) |
| Toastr / Bootstrap Toasts | Notificaciones toast no intrusivas |

### 2.5 JavaScript - Arquitectura
| Patrón | Propósito |
|--------|-----------|
| ES Modules (`type="module"`) | Imports/exports, tree-shaking, scope isolation |
| Component pattern (vanilla) | `MapComponent`, `TripSearch`, `NotificationBell`, `RatingWidget` |
| Event-driven (Pub/Sub) | Desacoplar UI: `eventBus.emit('trip:created', data)` |
| Progressive Enhancement | Funciona sin JS (forms, links), JS añade UX (autocomplete, map preview) |

### 2.6 JavaScript - Funcionalidades Clave
| Módulo | Propósito |
|--------|-----------|
| `map.js` | Inicializa Leaflet, maneja marcadores origen/destino, ruta, geocoder |
| `search.js` | Autocomplete puntos ref, filtros horario/campus, debounce fetch |
| `trip-form.js` | Validación client-side, photo preview, capacity selector, pref checkboxes |
| `notifications.js` | WebSocket connection, render badge, mark read, push permission |
| `rating.js` | Star rating input, envío AJAX, update UI optimista |
| `pwa.js` | Service Worker registration, install prompt, offline fallback |

### 2.7 PWA y Offline
| Tecnología | Propósito |
|------------|-----------|
| Workbox / sw-precache | Service Worker: cache static assets, network-first para API GET |
| Web App Manifest | `manifest.json`: nombre, icons, theme_color, display: standalone |
| Push API + VAPID | Notificaciones push navegador (solicitud, confirmación, cancelación) |
| Background Sync | Cola acciones offline (calificar, confirmar) y reintenta online |

### 2.8 Accesibilidad (a11y)
| Práctica/Herramienta | Propósito |
|---------------------|-----------|
| Semantic HTML5 | `nav`, `main`, `section`, `article`, `aside`, landmarks ARIA |
| Bootstrap a11y | Focus visible, skip links, ARIA attributes en componentes |
| axe-core / Lighthouse | Auditar a11y en CI |
| prefers-reduced-motion | Respetar animaciones reducidas (AOS, transiciones) |

### 2.9 Tipografía y Assets
| Tecnología | Propósito |
|------------|-----------|
| Google Fonts (Inter, Poppins, DM Sans) | `preconnect`, `font-display: swap`, subset latino |
| Favicon / PWA icons | Generados via `pwa-asset-generator` (todas las densidades) |
| Imágenes responsive | `<picture>` + `srcset` + WebP/AVIF via template tags |

---

## 3. BASE DE DATOS

### 3.1 Motor Principal
| Tecnología | Propósito |
|------------|-----------|
| PostgreSQL 16+ | ACID, JSONB, índices parciales, partitioning, extensiones |
| PostGIS 3.4+ | Tipos geometry/geography, índices GiST, funciones espaciales (ST_DWithin, ST_MakeLine) |

### 3.2 Esquema - Tablas Core
| Tabla | Descripción |
|-------|-------------|
| `users_user` | Custom User (AbstractUser): email, matricula, telefono, verificado, rol |
| `users_perfil` | Foto, bio, genero, preferencias (sexo_grupo, notificaciones), rating_promedio |
| `trips_vehiculo` | Marca, modelo, color, placa, foto, capacidad_total, usuario_fk |
| `trips_puntoreferencia` | Nombre, geom (Point), campus_fk, direccion_formateada, activo |
| `trips_campus` | Nombre, clave (CU-IIT, ICSA, etc.), geom (Polygon), centroide |
| `trips_raite` | Conductor_fk, vehiculo_fk, origen_fk, destino_fk, fecha, hora_salida, hora_llegada_est, plazas_total, plazas_disponibles, estado, preferencia_grupo |
| `trips_solicitud` | Pasajero_fk, raite_fk, estado (pendiente/aceptada/rechazada/cancelada), punto_acordado, creada, respondida |
| `trips_calificacion` | De_user_fk, para_user_fk, raite_fk, puntuacion (1-5), comentario, tipo (conductor/pasajero), creada |
| `notifications_notification` | (django-notifications-hq) recipient, actor, verb, target, timestamp, unread, data_json |

### 3.3 Índices y Performance
| Índice | Propósito |
|--------|-----------|
| `GIST (geom)` en PuntoReferencia | Búsqueda radial `ST_DWithin(geom, user_point, 2000m)` |
| `GIST (geom)` en Campus | `ST_Contains(campus.geom, punto)` |
| `BRIN (fecha, hora_salida)` en Raite | Particionado temporal implícito, range queries |
| `Partial UNIQUE (usuario, raite) WHERE estado IN (...)` | Evitar solicitudes duplicadas |
| `Composite (destino_fk, fecha, estado)` | Listar viajes por campus+fecha |
| `JSONB GIN` en Notificaciones.data | Filtrar por claves dinámicas |

### 3.4 Migraciones y Versionado
| Herramienta | Propósito |
|-------------|-----------|
| Django Migrations | Versionado esquema, `RunSQL` para funciones PostGIS, `RunPython` para data migrations |
| pg_dump / pg_restore | Backup/restore producción |
| pgAdmin / DBeaver / DataGrip | GUI admin y debugging queries |

### 3.5 Conexión y Pooling
| Configuración | Valor/Propósito |
|---------------|-----------------|
| `CONN_MAX_AGE = 60` | Persistent connections (gunicorn workers) |
| PgBouncer (producción) | Connection pooling transaction mode, reduce overhead |
| `ATOMIC_REQUESTS = True` | Transacción por request (rollback en error) |

### 3.6 Desarrollo Local
| Tecnología | Propósito |
|------------|-----------|
| SQLite + SpatiaLite | GeoDjango funcional en dev sin Docker (limitado) |
| Docker Compose (PostgreSQL+PostGIS) | Paridad 1:1 con producción (recomendado) |

---

## 4. EXTERNO A CODIFICACIÓN (INFRA, OPS, PROCESOS)

### 4.1 CI/CD Pipeline
| Etapa | Herramienta | Detalle |
|-------|-------------|---------|
| Source Control | GitHub | Repo privado, branch protection, required reviews |
| CI | GitHub Actions | Matrix: lint → typecheck → test (unit+integration) → build Docker |
| CD Staging | GitHub Actions + Render/Railway | Deploy auto en push a `main` (staging env) |
| CD Production | GitHub Actions + Render/Railway | Deploy manual (workflow_dispatch) o tag `v*` |
| Docker | Multi-stage build | Builder → runtime slim (python:3.11-slim), non-root user |
| Dependency Cache | GitHub Actions cache | `~/.cache/pip`, `node_modules`, `.venv` |
| Security Scan | Trivy / Snyk / GitHub CodeQL | Scan imagen Docker + dependencias en PR |

### 4.2 Control de Versiones y Flujo
| Convención | Propósito |
|------------|-----------|
| Conventional Commits | `feat:`, `fix:`, `refactor:`, `chore:`, `docs:` → changelog auto |
| GitHub Flow | `main` siempre deployable, feature branches cortas, PR + squash merge |
| GitHub Projects (Kanban) | Sprint board: Backlog → Ready → In Progress → Review → Done |
| Semantic Versioning | `MAJOR.MINOR.PATCH` tags para releases |
| Release Drafter | Genera release notes automático desde PRs merged |

### 4.3 Testing y Calidad
| Tipo | Herramientas | Cobertura Objetivo |
|------|--------------|-------------------|
| Unit | pytest, pytest-django, factory_boy | >80% models/services |
| Integration | pytest + test Client | Vistas, forms, auth, API |
| E2E | Playwright (Chromium/Firefox/WebKit) | Flujos críticos: registro→publicar→solicitar→calificar |
| Contract | schemathesis (si API) | Validar OpenAPI spec vs implementación |
| Static Analysis | ruff (lint), mypy + django-stubs (types), bandit (sec) | 0 errors en CI |
| Format | black + isort | Pre-commit hook + CI check |
| Performance | locust / k6 (opcional) | Load test endpoints críticos |

### 4.4 Hosting e Infraestructura (Producción)
| Componente | Opción Recomendada | Alternativas |
|------------|-------------------|--------------|
| App Hosting | Render (Web Service) | Railway, Fly.io, Koyeb, AWS ECS/Fargate |
| Database | Aiven PostgreSQL + PostGIS | Neon, Supabase, Render PG, AWS RDS |
| Redis | Upstash / Redis Cloud | Aiven Redis, Render Redis |
| Static/Media CDN | Cloudflare R2 + Cloudflare CDN | AWS S3+CloudFront, Cloudinary |
| Domain/DNS | PorkBun / Cloudflare | Namecheap, GoDaddy |
| TLS/SSL | Automático (Let's Encrypt via hosting) | Cloudflare Universal SSL |

### 4.5 Observabilidad y Monitoreo
| Área | Herramienta | Qué Mide |
|------|-------------|----------|
| Error Tracking | Sentry (self-hosted o cloud) | Exceptions, traces, release health, user feedback |
| APM / Performance | Sentry / Datadog / Elastic APM | Latencia p95, DB queries lentas, throughput |
| Logs Estructurados | Logtail / Better Stack / Papertrail | JSON logs: request_id, user_id, trip_id, level |
| Uptime | Uptime Robot / Better Stack | HTTPS checks /health/, alertas Telegram/Email/Slack |
| Métricas Negocio | Custom (Prometheus + Grafana opcional) | Viajes activos, solicitudes/min, tasa conversión, rating promedio |
| Health Checks | Django `/health/` endpoint | DB connectivity, Redis, disk space, migrations applied |

### 4.6 Seguridad Operacional
| Práctica | Herramienta/Config |
|----------|-------------------|
| Secrets Management | GitHub Environments + Encrypted Secrets / 1Password CLI / Doppler |
| Dependency Scanning | Dependabot alerts + auto-PR updates / Snyk / Trivy |
| SAST/DAST | GitHub CodeQL (PR), OWASP ZAP (staging) |
| Backup Strategy | Point-in-time recovery (Aiven/Neon), daily pg_dump a R2/S3, test restore mensual |
| Incident Response | Runbook en docs/, escalation: PagerDuty / Opsgenie (opcional) |

### 4.7 Documentación
| Tipo | Herramienta | Ubicación |
|------|-------------|-----------|
| Técnica (devs) | MkDocs + Material theme | `docs/` → GitHub Pages / ReadTheDocs |
| API (si REST) | drf-spectacular → Redoc/Swagger UI | `/api/docs/`, `/api/redoc/` |
| Arquitectura (ADR) | Markdown en `docs/adr/` | `001-use-django-channels.md`, etc. |
| Onboarding | `CONTRIBUTING.md`, `DEVELOPMENT.md`, `DEPLOYMENT.md` | Root repo |
| Changelog | Release Drafter / conventional-changelog | `CHANGELOG.md` auto |

### 4.8 Legal y Cumplimiento (México)
| Requisito | Implementación |
|-----------|----------------|
| LFPDPPP (Ley Federal Protección Datos) | Aviso privacidad, consentimiento explícito, derechos ARCO, DPO designado |
| Términos y Condiciones | Markdown renderizado en `/terminos/`, versionado |
| Cookies / Consentimiento | Banner GDPR-style (aunque LFPDPPP), categorizar: necesarias, analytics, marketing |
| Verificación Identidad | Email @uacj.mx + matrícula (validación regex + lista blanca futura) |
| Reporte Incidentes | Formulario `/reportar/`, canal confidencial, SLA respuesta 48h |

---

## 5. RESUMEN POR CATEGORÍA (QUICK REFERENCE)

| Categoría | Tecnologías Clave |
|-----------|-------------------|
| **Backend Core** | Django 5, Python 3.11, ASGI |
| **Auth/Seguridad** | django-allauth, django-axes, CSP, rate-limit, 2FA |
| **Geo/Mapas** | GeoDjango, PostGIS, Leaflet/MapLibre, OSRM |
| **Tiempo Real** | Django Channels, Redis, Celery, Web Push/PWA |
| **Async/Tasks** | Celery + Redis, Celery Beat |
| **Frontend SSR** | Django Templates, Bootstrap 5, Bootstrap Icons |
| **Frontend JS** | Vanilla ES Modules, Leaflet, Swiper, AOS, GLightbox |
| **PWA** | Service Worker, Manifest, Push API, Background Sync |
| **Database** | PostgreSQL 16 + PostGIS 3.4, GIST/BRIN indexes |
| **Testing** | pytest, Playwright, ruff, mypy, black |
| **CI/CD** | GitHub Actions, Docker, Render/Railway |
| **Observability** | Sentry, Logtail, Uptime Robot, Health checks |
| **Docs** | MkDocs, drf-spectacular, ADRs |
| **Infra** | Cloudflare R2/CDN, Aiven/Neon PG, Upstash Redis |

---

## 6. ARQUITECTURA DE SOFTWARE

### 6.1 Estilo Arquitectónico: Capas + Repository Pattern

Raite adopta una **arquitectura por capas (Layered Architecture)** combinada con **Repository Pattern** para separar responsabilidades, aislar el dominio del framework y facilitar testing y evolución.

**Principios rectores:**
- **Domain-Driven Design (DDD) ligero**: El dominio (entidades, value objects, services, eventos) no depende de Django ni infraestructura
- **Dependency Rule**: Capas internas no conocen capas externas; dependencias apuntan hacia adentro
- **Repository Pattern**: Interfaces en `domain/repositories/`, implementaciones en `infrastructure/django_repositories/`
- **Dependency Injection**: Wireado manual en `apps.py` / `ready()` o con `django-dependency-injector`

### 6.2 Estructura de Carpetas (Tree)

```
raite/                          # Raíz del proyecto Django
├── config/                     # Configuración Django (settings, wsgi, asgi, urls root)
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── testing.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── urls.py
│
├── domain/                     # CAPA DE DOMINIO (Pure Python, sin Django)
│   ├── __init__.py
│   ├── entities/               # Entidades de negocio (identidad + ciclo de vida)
│   │   ├── __init__.py
│   │   ├── user.py             # User, StudentProfile, DriverProfile
│   │   ├── trip.py             # Trip (Raite), TripStatus, Seat
│   │   ├── vehicle.py          # Vehicle, Capacity
│   │   ├── campus.py           # Campus, ReferencePoint
│   │   └── rating.py           # Rating, Review
│   ├── value_objects/          # Objetos de valor (inmutables, sin identidad)
│   │   ├── __init__.py
│   │   ├── coordinate.py       # LatLng, SRID 4326
│   │   ├── time_window.py      # DepartureTime, ArrivalWindow
│   │   ├── capacity.py         # SeatsTotal, SeatsAvailable
│   │   ├── preference.py       # GenderPreference, GroupType
│   │   └── reputation.py       # Score, Badge
│   ├── services/               # Servicios de dominio (lógica de negocio pura)
│   │   ├── __init__.py
│   │   ├── matching_service.py     # Algoritmo matching: puntos ref, horario, prefs
│   │   ├── reputation_service.py   # Cálculo rating, badges, trust score
│   │   ├── validation_service.py   # Reglas: capacidad, horarios, campus válidos
│   │   └── notification_service.py # Orquestación notificaciones (domain events)
│   ├── repositories/           # INTERFACES (Protocol/ABC) - Contratos
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   ├── trip_repository.py
│   │   ├── vehicle_repository.py
│   │   ├── campus_repository.py
│   │   ├── reference_point_repository.py
│   │   └── rating_repository.py
│   ├── events/                 # Eventos de dominio (para desacoplar side effects)
│   │   ├── __init__.py
│   │   ├── trip_created.py
│   │   ├── seat_requested.py
│   │   ├── seat_accepted.py
│   │   ├── seat_rejected.py
│   │   ├── trip_cancelled.py
│   │   ├── rating_submitted.py
│   │   └── event_bus.py        # Pub/Sub simple in-memory
│   └── exceptions/             # Excepciones de dominio
│       ├── __init__.py
│       ├── trip_full.py
│       ├── invalid_preference.py
│       ├── user_not_verified.py
│       └── matching_failed.py
│
├── infrastructure/             # CAPA DE INFRAESTRUCTURA (Implementaciones concretas)
│   ├── __init__.py
│   ├── django_repositories/    # Implementaciones Repository con Django ORM
│   │   ├── __init__.py
│   │   ├── django_user_repository.py
│   │   ├── django_trip_repository.py
│   │   ├── django_vehicle_repository.py
│   │   ├── django_campus_repository.py
│   │   ├── django_reference_point_repository.py
│   │   └── django_rating_repository.py
│   ├── geo/                    # Adaptadores geoespaciales
│   │   ├── __init__.py
│   │   ├── postgis_adapter.py      # Queries ST_DWithin, ST_MakeLine, ST_Buffer
│   │   ├── osrm_client.py          # Cliente OSRM/Valhalla (rutas, ETA)
│   │   ├── nominatim_client.py     # Geocodificación direcciones → coords
│   │   └── map_tiles.py            # Proveedores tiles: OSM, Mapbox, Stadia
│   ├── notifications/          # Canales de notificación
│   │   ├── __init__.py
│   │   ├── email_sender.py         # Anymail (SendGrid/Brevo)
│   │   ├── push_notifier.py        # Web Push (VAPID), FCM
│   │   ├── websocket_publisher.py  # Django Channels group_send
│   │   └── in_app_notifier.py      # django-notifications-hq
│   ├── storage/                # Almacenamiento archivos
│   │   ├── __init__.py
│   │   ├── media_storage.py        # S3/R2/Cloudflare (django-storages)
│   │   └── static_storage.py       # Whitenoise / CDN
│   ├── security/               # Seguridad transversal
│   │   ├── __init__.py
│   │   ├── rate_limiter.py         # django-ratelimit wrapper
│   │   ├── csrf_protection.py
│   │   └── content_sanitizer.py    # bleach wrapper
│   └── tasks/                  # Tareas asíncronas (Celery)
│       ├── __init__.py
│       ├── email_tasks.py
│       ├── notification_tasks.py
│       ├── cleanup_tasks.py
│       └── stats_tasks.py
│
├── presentation/               # CAPA DE PRESENTACIÓN (Django Apps - SSR + HTMX/JS)
│   ├── __init__.py
│   ├── trips/                  # App: viajes (Raite)
│   │   ├── __init__.py
│   │   ├── views.py              # Vistas CBV/FBV (list, detail, create, match)
│   │   ├── forms.py              # TripForm, SearchForm, RequestForm
│   │   ├── urls.py
│   │   ├── templates/trips/      # Templates: list, detail, map, partials
│   │   ├── templatetags/         # Tags custom: trip_status_badge, seats_left
│   │   └── consumers.py          # WebSocket consumers (chat, live updates)
│   ├── users/                  # App: usuarios, auth, perfiles
│   │   ├── __init__.py
│   │   ├── views.py              # Register, Profile, Settings, Verification
│   │   ├── forms.py              # UserForm, ProfileForm, VehicleForm
│   │   ├── urls.py
│   │   ├── templates/users/
│   │   └── adapters.py           # allauth adapters custom
│   ├── api/                    # App: API REST (opcional, DRF)
│   │   ├── __init__.py
│   │   ├── serializers.py
│   │   ├── views.py              # ViewSets: TripViewSet, UserViewSet
│   │   ├── urls.py
│   │   ├── permissions.py        # IsDriver, IsPassenger, IsOwner
│   │   └── pagination.py
│   ├── websocket/              # App: Channels routing
│   │   ├── __init__.py
│   │   ├── routing.py            # WebSocket URL patterns
│   │   └── middleware.py         # AuthMiddlewareStack custom
│   ├── core/                   # App: shared, landing, health
│   │   ├── __init__.py
│   │   ├── views.py              # Home, HealthCheck, Robots.txt
│   │   ├── urls.py
│   │   └── templates/core/
│   └── static/                 # Assets compilados (collectstatic)
│       ├── css/
│       ├── js/
│       └── images/
│
├── tests/                      # Tests organizados por capa
│   ├── __init__.py
│   ├── domain/                 # Unit tests puros (sin BD, mocks)
│   │   ├── test_matching_service.py
│   │   ├── test_reputation_service.py
│   │   └── test_validation_service.py
│   ├── infrastructure/         # Integration tests (con BD real)
│   │   ├── test_django_trip_repository.py
│   │   └── test_postgis_adapter.py
│   ├── presentation/           # View/Template/Forms tests
│   │   ├── test_trip_views.py
│   │   └── test_user_forms.py
│   ├── e2e/                    # Playwright tests
│   │   ├── test_register_flow.py
│   │   ├── test_publish_trip_flow.py
│   │   └── test_request_seat_flow.py
│   └── fixtures/               # Factory Boy factories
│       ├── __init__.py
│       ├── user_factory.py
│       ├── trip_factory.py
│       └── campus_factory.py
│
├── docs/                       # Documentación (MkDocs)
│   ├── adr/                    # Architecture Decision Records
│   │   ├── 001-layered-architecture.md
│   │   ├── 002-repository-pattern.md
│   │   ├── 003-use-django-channels.md
│   │   └── 004-postgis-for-geo.md
│   ├── development.md
│   ├── deployment.md
│   ├── contributing.md
│   └── api.md
│
├── scripts/                    # Scripts utilitarios
│   ├── __init__.py
│   ├── seed_campuses.py
│   ├── seed_reference_points.py
│   └── generate_test_data.py
│
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── pyproject.toml              # Config: black, ruff, mypy, pytest, coverage
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
├── Makefile                    # Comandos comunes: make test, make lint, make migrate
└── README.md
```

### 6.3 Flujo de Dependencias (Dependency Rule)

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION (Django Apps)               │
│  trips, users, api, websocket, core                         │
│                    │                                        │
│                    ▼ (usa interfaces)                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    DOMAIN (Pure Python)             │   │
│  │  entities, value_objects, services, repositories    │   │
│  │  (interfaces), events, exceptions                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                    ▲                                        │
│                    │ (implementa interfaces)                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 INFRASTRUCTURE                       │   │
│  │  django_repositories, geo, notifications, storage,  │   │
│  │  security, tasks                                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Regla**: `domain` **nunca** importa de `infrastructure` ni `presentation`.  
`presentation` importa de `domain` (services + repository interfaces).  
`infrastructure` implementa interfaces de `domain.repositories`.

### 6.4 Ejemplo: Wireado en `apps.py`

```python
# presentation/trips/apps.py
from django.apps import AppConfig

class TripsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'presentation.trips'
    verbose_name = 'Viajes Compartidos'

    def ready(self):
        # Dependency Injection manual
        from domain.services.matching_service import MatchingService
        from domain.services.reputation_service import ReputationService
        from domain.repositories.trip_repository import TripRepository
        from domain.repositories.reference_point_repository import ReferencePointRepository
        from infrastructure.django_repositories.django_trip_repository import DjangoTripRepository
        from infrastructure.django_repositories.django_reference_point_repository import DjangoReferencePointRepository

        # Singletons por request (o usar django-dependency-injector)
        trip_repo: TripRepository = DjangoTripRepository()
        ref_point_repo: ReferencePointRepository = DjangoReferencePointRepository()

        # Inyectar en servicios (patrón Service Locator simple)
        MatchingService.set_repositories(trip_repo, ref_point_repo)
        ReputationService.set_trip_repository(trip_repo)

        # Signals → Domain Events
        from django.db.models.signals import post_save
        from presentation.trips.models import Trip, TripRequest, Rating
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

### 6.5 Ventajas para Raite

| Beneficio | Cómo se logra |
|-----------|---------------|
| **Testabilidad** | `MatchingService` se prueba con `FakeTripRepository` en memoria (sin BD, sin Django) |
| **Intercambiabilidad** | Cambiar `DjangoTripRepository` → `SQLAlchemyTripRepository` o añadir `CachedTripRepository` (Redis) sin tocar dominio |
| **Geo aislado** | `PostGISAdapter` encapsula SQL espacial; dominio usa `Coordinate` + `Distance` value objects |
| **Eventos desacoplados** | `TripCreated` → notifica email, push, websocket, stats sin acoplar emisor a receptores |
| **Onboarding** | Nuevo dev entiende dominio leyendo `domain/` sin saber Django |
| **Migración futura** | Extraer `domain/` a librería compartida si hay app móvil nativa (React Native, Flutter) |

### 6.6 Cuándo NO usar (y mantener simple)

- MVP < 3 sprints: Django "fat models" + views + forms es suficiente
- Equipo < 3 devs: Overhead de DI y capas puede ralentizar
- Sin lógica de matching compleja: CRUD simple → Repository Pattern añade indireccion innecesaria

**Recomendación**: Inicia con `services/` + `repositories/` dentro de apps Django. Extrae `domain/` paquete separado en Sprint 3-4 cuando matching y reputación crezcan.