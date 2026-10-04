# Raite — Arquitectura de Apps Django

> Documento derivado de `Raite_layout_disposition.md` y `Raite_layout_disposition_001.md`.
> Define cómo se descompone el backend en apps Django para mantener el sistema modular.

---

## 1. Principio de descomposición

Cada app Django es una **frontera de negocio**, no una capa técnica. Un criterio de separaciónhealthy combina:

- **Cohesión**: los modelos de una app cambian juntos.
- **Acoplamiento dirigido**: `rides` conoce a `accounts`; `accounts` no conoce a `rides`.
- **Cambio independiente**: el admin de `locations` no debería requerir tocar `rides`.

Consecuencia: los *serializers*, *views* y *urls* viven **dentro** de la app que posee el modelo. No se crea una app `api` monolítica.

---

## 2. Apps de dominio

| App | Modelos | Responsabilidad |
|-----|---------|-----------------|
| `accounts` | `Usuario`, `PerfilConductor` | Autenticación, registro en 2 pasos, roles (pasajero / conductor / ambos), estado `activo` |
| `vehicles` | `Vehiculo` | Datos del vehículo del conductor, validación de "vehículo válido" |
| `locations` | `PuntoMapeado`, `Campus` | Puntos del sistema en Leaflet, destino fijo CU |
| `rides` | `Raite`, `ConfiguracionViaje`, `PreferenciaViaje` | Núcleo: crear y aceptar raite, máquina de estados, expiración |
| `surveys` | `EncuestaFinalizacion` | Finalización obligatoria persistente con reintentos |
| `ratings` | `Calificacion` | Calificación 1–5 bidireccional post-viaje |
| `notifications` | `Notificacion`, `PreferenciaNotificacion` | Bandeja in-app y registro de canales push |

## 3. Apps de soporte

| App | Responsabilidad |
|-----|-----------------|
| `realtime` | Consumers y routing de Channels; publicación de eventos de dominio |
| `core` | Health check, raíz de API, permisos base, mixins, constantes (CU), utilidades |

---

## 4. Grafo de dependencias

```
                    ┌──────────┐
                    │   core   │  (sin dependencias de dominio)
                    └────┬─────┘
                         │ (todos usan core)
   ┌──────────┬──────────┼──────────┬───────────┐
   │          │          │          │           │
┌──┴───┐  ┌───┴────┐  ┌──┴───┐  ┌───┴────┐  ┌───┴────┐
│accounts│ │vehicles │  │locations│  │notifi-  │  │realtime │
└───┬───┘  └───┬────┘  └───┬────┘  │cations  │  └───┬────┘
    │         │            │       └────┬────┘      │
    └─────────┴────────────┴────────────┤           │
                                       │  (señales/│event bus)
                                  ┌────┴───────────┴───┐
                                  │      rides        │
                                  └────┬──────────┬───┘
                                       │          │
                              ┌────────┴───┐  ┌───┴──────┐
                              │  surveys  │  │  ratings │
                              └────────────┘  └──────────┘
```

**Reglas de dependencia:**

1. `rides` depende de `accounts`, `locations`, `vehicles`.
2. `surveys` y `ratings` dependen de `rides`.
3. `notifications` **no** importa de `rides`. Se engancha por señales Django
   (`post_save` de `Raite`) y por un event bus simple. Así `rides` no conoce quién escucha.
4. `realtime` es un *sink*: recibe eventos y hace `group_send`. No escribe en modelos de negocio.
5. `core` no importa de ninguna app de dominio.
6. Prohibido importar modelos entre apps de dominio directamente en `views.py`.
   Usar `select_related` y serializers de la app propietaria.

---

## 5. Estructura interna de una app

Cada app de dominio sigue la misma plantilla, que separa capas sin crear apps extra:

```
apps/rides/
├── models.py              # Solo modelo + managers propios
├── models_choices.py      # Enums: TipoViaje, EstadoRaite
├── selectors.py           # Queries de lectura nombradas (Q_objects)
├── services.py            # Casos de uso: crear_raite(), aceptar_raite(), finalizar()
├── signals.py             # Emisores post_save / post_delete
├── admin.py
├── permissions.py         # IsPassenger, IsDriver, IsRaiteOwner
├── serializers/
│   ├── __init__.py
│   ├── raite.py
│   └── config.py
├── views/
│   ├── __init__.py
│   ├── raite_viewset.py
│   └── acciones.py        # @action: aceptar, cancelar, expirar
├── urls.py
├── migrations/
└── tests/
    ├── test_models.py
    ├── test_services.py
    └── test_api.py
```

- `selectors.py` — el frontend no escribe queries. Un `listar_raites_disponibles(...)` encapsula el filtro.
- `services.py` — toda escritura pasa por aquí, con `transaction.atomic()`. Las vistas son delgadas.
- `permissions.py` por app: cada app define sus propias, `core` solo aporta `IsAdmin`, `IsOwner` genérico.

---

## 6. Comandos de creación

```bash
cd Back_Raite

python manage.py startapp core
python manage.py startapp accounts
python manage.py startapp vehicles
python manage.py startapp locations
python manage.py startapp rides
python manage.py startapp surveys
python manage.py startapp ratings
python manage.py startapp notifications
python manage.py startapp realtime
```

Registro en `settings.py` (nota: `Raite_DjangoRest` **no** es una app):

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',

    'apps.core',
    'apps.accounts',
    'apps.vehicles',
    'apps.locations',
    'apps.rides',
    'apps.surveys',
    'apps.ratings',
    'apps.notifications',
    'apps.realtime',
]

AUTH_USER_MODEL = 'accounts.Usuario'
```

Routing:

```python
# Raite_DjangoRest/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/',       include('apps.accounts.urls_auth')),
    path('api/',            include('apps.accounts.urls')),
    path('api/',            include('apps.vehicles.urls')),
    path('api/',            include('apps.locations.urls')),
    path('api/',            include('apps.rides.urls')),
    path('api/',            include('apps.surveys.urls')),
    path('api/',            include('apps.ratings.urls')),
    path('api/',            include('apps.notifications.urls')),
    path('api/',            include('apps.core.urls')),
]
```

> **Nota de migración:** cambiar `AUTH_USER_MODEL` a un modelo propio requiere una migración
> inicial con `AUTH_USER_MODEL` ya seteado, o exportando antes los usuarios existentes.
> Si el proyecto aún no tiene usuarios reales en producción, es el momento ideal.

---

## 7. Orden de implementación por sprint

| Sprint | Apps | Entregable verificable |
|--------|------|------------------------|
| 0 | `core` | `/api/health/` responde 200, `IsAdmin` disponible |
| 1 | `accounts` | Registro en 2 pasos + login JWT + `GET /api/me/` con rol |
| 2 | `vehicles` + `locations` | CRUD de vehículo, seed de puntos UACJ, `Campus` = CU |
| 3 | `rides` (crear + listar) | Pasajero crea raite; conductor ve puntos con demanda |
| 4 | `rides` (aceptar + expirar) | Aceptar transaccional, cron de expiración por `hora_objetivo` |
| 5 | `surveys` + `ratings` | Finalización con ambos `sí`; calificación liberada |
| 6 | `notifications` + `realtime` | WS: aceptado / expirado / encuesta pendiente |
| 7 | Admin | Panel de administración completo de las 5 secciones |

---

## 8. Criterios para dividir apps en el futuro

No dividing más por ahora. Señales de que una app debe partirse:

| Señal | División propuesta |
|-------|--------------------|
| `locations` supera 5 modelos o entra geospatial serio | `geo` (PostGIS: `ST_DWithin`, `ST_MakeLine`, OSRM/Nominatim) |
| `rides` tiene dos conjuntos de reglas disconnected (match vs. admin) | `rides` + `ride_admin` |
| Se requiere app móvil nativa | extraer `domain/` a librería compartida |
| Multi-institución (varias CU) | `tenants` + `locations` parametrizado |

---

## 9. Documentos relacionados

- `Raite-Django-Models.md` — campos, constraints y estados por modelo
- `Raite-Django-API.md` — endpoints, permisos y eventos WebSocket
- `Raite-System-Architecture.md` — capas, ports/adapters e infraestructura
- `Raite_layout_disposition.md` / `_001.md` — especificación funcional original
