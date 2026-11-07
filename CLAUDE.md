# CLAUDE.md

Fuente de verdad del proyecto para Claude Code. Última revisión: 2026-11-06.
Si algo de aquí contradice al código, revisa el código y actualiza este archivo.

> **Nombre del proyecto:** [NOMBRE] — pendiente de confirmar (aparece como "Raite" en el SRS y en el código, "UniGo-UACJ" en la carta y "RutaClara" en el encabezado del PDF de la carta). En el código se mantiene "Raite": no renombrar nada hasta que se pida.

## Resumen del proyecto

[NOMBRE] es un sitio web de viajes compartidos ("raites") exclusivo para estudiantes de la Universidad Autónoma de Ciudad Juárez (UACJ). Los estudiantes con auto publican viajes hacia o desde un campus indicando un punto de referencia de origen, el campus destino, el horario y los lugares que ofrecen; los estudiantes que necesitan transporte buscan esos viajes y piden un lugar.

Resuelve dos problemas: el gasto y el tiempo de traslado de los alumnos que dependen del transporte público o privado, y el desaprovechamiento de lugares libres en autos de compañeros que ya hacen el mismo recorrido a la misma hora. Hoy eso se organiza de forma informal; la plataforma lo ordena y le agrega confianza (acceso solo con correo institucional, perfiles identificados, preferencias de compatibilidad, calificaciones, historial y reportes).

Es un proyecto escolar (materia Innovación Tecnológica, UACJ, 2026, metodología Scrum). El equipo original ya no participa; el proyecto lo termina Gabriel Florentino Reyes con Claude.

## Stack y comandos

Lo que **realmente** hay en el repo (los docs de diseño mencionan más cosas: PostGIS, Channels, Celery, Redis, Leaflet, PWA… nada de eso está instalado todavía).

### Backend — `Back_Raite/` (Python)

- Django 6.1.1, Django REST Framework 3.18, `djangorestframework-simplejwt` 5.5 (con `token_blacklist`), `django-cors-headers`, `dj-database-url`, `python-dotenv`, `psycopg2-binary`.
- Base de datos: **PostgreSQL local** de cada desarrollador (sin PostGIS). Ya no se usa el Postgres remoto. Se configura con `DATABASE_URL` en `Back_Raite/.env` (gitignored); no hay respaldo SQLite. El certificado `certs/ca.pem` solo se usa si se configura por variable de entorno. Hay un virtualenv local en `Back_Raite/.venv/`.
- Variables de entorno: `DATABASE_URL`, `SECRET_KEY`, `DEBUG` (y las de correo/certificado que se agreguen). Plantilla en `Back_Raite/.env.example`.
- Datos iniciales (campus y puntos de referencia): se cargan con un comando de `manage.py` para que todos tengan los mismos datos.
- **Estado:** el cambio a BD local, `.env.example`, las variables de entorno y el comando de carga están **planeados, aún no implementados** (hoy `settings.py` todavía tiene `SECRET_KEY`/`DEBUG` fijos). Al implementarlos, quitar esta línea y documentar el comando exacto aquí y en el `README.md`.

```bash
cd Back_Raite
pip install -r requirements.txt
python manage.py runserver            # http://localhost:8000
python manage.py migrate
python manage.py makemigrations
python manage.py check
python manage.py test                                   # todos los tests (crea BD de prueba en el Postgres de DATABASE_URL)
python manage.py test apps.accounts.tests.test_auth_api # un módulo
```

### Frontend — `Front_Raite/` (TypeScript)

- Quasar 2.30 (Vite, `@quasar/app-vite` 3.8), Vue 3.5, Vue Router 5 (rutas por archivo), Pinia 4, Axios, `validator`. Node `^22.12 || ^24 || >=26`. **pnpm** es el gestor canónico.
- Sin runner de tests (no hay Vitest/Playwright).

```bash
cd Front_Raite
pnpm install
pnpm dev          # quasar dev → http://localhost:9000
pnpm build
pnpm lint         # prettier --write + eslint --fix
pnpm lint:check
pnpm typecheck    # vue-tsc --noEmit
```

- `VITE_API_URL` define la URL del API (por defecto `http://localhost:8000`). El CORS del backend solo permite `http://localhost:9000` y `http://localhost:9002`.

### Decidido, aún no instalado

- Mapas: Leaflet + OpenStreetMap (se instala en la Capa 3).
- Notificaciones: solo dentro de la app (modelo + consulta periódica desde el frontend). Sin push ni WebSockets.
- Cercanía geográfica: fórmula de haversine en Python. Sin PostGIS.

### Por definir

- Hospedaje / despliegue: **POR DEFINIR** (se decide al final).

## Estructura del repo

```
Raite/
├── CLAUDE.md            # este archivo (versionado)
├── AGENTS.md            # instrucciones para agentes (graphify)
├── README.md
├── Back_Raite/          # API Django
│   ├── manage.py
│   ├── requirements.txt
│   ├── certs/ca.pem     # CA del antiguo Postgres remoto (opcional, por variable)
│   ├── Raite_DjangoRest/  # paquete del proyecto: settings.py, urls.py, wsgi/asgi
│   └── apps/
│       └── accounts/    # única app: usuarios, roles, vehículo, auth JWT
│           ├── models.py, models_choices.py
│           ├── serializers.py, views.py, urls_auth.py, permissions.py
│           ├── admin.py, signals.py (vacío)
│           ├── migrations/ (0001–0012)
│           └── tests/ (test_models.py, test_auth_api.py)
├── Front_Raite/         # SPA Quasar
│   ├── quasar.config.ts
│   └── src/
│       ├── boot/        # axios.ts (instancia `api` + refresh de token en 401), auth-init.ts
│       ├── stores/      # auth-store.ts (sesión, rol, rol activo); example-store.ts es de plantilla
│       ├── router/      # index.ts (guardas); typed-router.d.ts es GENERADO, no editar
│       ├── layouts/     # MainLayout.vue
│       ├── components/  # RoleSelectionModal.vue, EssentialLink.vue (plantilla)
│       └── pages/       # rutas por archivo (ver abajo)
├── RaiteDocs/           # documentación (mayormente en español)
│   ├── docs/            # documentos formales exportados de Google Drive (SRS, propuesta fase 1/2)
│   ├── Design/          # UI_UX.md, layouts_team.md, imágenes y PDF de diseño
│   ├── Context/         # system_solutions_context.md
│   ├── BD_PuntosMapa/   # Oxxo.json (export de Overpass/OSM con los OXXO de Juárez)
│   ├── Sketches/, TeamTasks/
│   └── Raite-*.md, tecnologias.md, uml_*.mmd, …  # diseño técnico del equipo anterior
├── graphify-out/        # grafo de conocimiento generado (ver AGENTS.md)
└── .opencode/           # configuración de opencode + plugin graphify
```

### Detalles del backend que importan

- `AUTH_USER_MODEL = 'accounts.Usuario'` (PK UUID), `USERNAME_FIELD = "correo"`: el `ModelBackend` normal inicia sesión por correo, no hace falta backend propio.
- Campos y modelos **en español** (`correo`, `nombre`, `apellidos`, `edad` 17–70, `sexo`, `carrera`, `calificacion` 0.00–5.00, `suspendido`, …). Mantener esa convención.
- **Un solo campo `rol`** (entero): `1=ADMIN`, `2=PASAJERO`, `3=CONDUCTOR`, `4=AMBOS`. La tabla `UsuarioRol` ya no existe (migraciones 0011–0012). Helpers: `es_pasajero`, `es_conductor`, `es_admin`, `puede_crear_raite()`, `puede_aceptar_raite()`. ADMIN no se puede obtener en el registro público.
- `Sexo`: `M`, `F`, `X` ("Otro"). Se mantienen los tres (ver Decisiones tomadas).
- `activo` / `cuenta_activa` son cachés de "tiene un raite en curso" (pensadas para la futura app de viajes), **no** el estado de la cuenta (eso es `is_active`).
- `Vehiculo` (1 a 1 con el usuario): marca, modelo, color, placas (únicas, normalizadas), tipo (`COCHE`/`CAMIONETA`/`TROCA`), `asientos_disponibles` (el serializer acepta 1–8).
- Endpoints (`/api/auth/`): `token/`, `token/refresh/`, `token/blacklist/`, `me/` (GET), `register/` (POST, paso 1; responde `requiere_vehiculo`), `vehicle/` (POST, paso 2, solo conductores). Además `admin/` de Django.
- JWT: acceso 30 min, refresh 1 día, rotación + blacklist.
- `settings.py` aún tiene `SECRET_KEY` fija y `DEBUG = True`; no apto para producción.

### Detalles del frontend que importan

- Rutas por archivo (`filenameBasedRouting: true`), modo **`history`**. Páginas: `/login/LoginPage`, `/login/SignUpPage`, `/home` (elige vista según rol; con rol AMBOS abre `RoleSelectionModal` para elegir rol activo), `/home-pasajero` y `/home-conductor` (solo un título y botón de cerrar sesión), y restos de plantilla (`index.vue`, `index/(index).vue`, `index/second.vue`, `login/MainPage.vue`, `login/ErrorNotFound.vue`, `[...path].vue`).
- Guarda global en `router/index.ts`: todo fuera de `/login*` requiere sesión; con sesión, `/login*` y `/` redirigen a `/home`.
- Tokens en `localStorage`. Usa el alias `@/` para `src/`.
- `tsconfig.json` referencia archivos de tipos dentro de `node_modules/.pnpm/...` con rutas con hash: si `pnpm install` cambia versiones, el typecheck puede romperse hasta actualizar esas rutas.

## Requerimientos

Fuente: `RaiteDocs/docs/2_SRS.md`. Estado según el código al 2026-11-06.
✅ hecho · 🟡 parcial · ⬜ pendiente

### Funcionales

| ID | Requerimiento | Estado | Notas |
|----|---------------|--------|-------|
| RF-01 | Registro de usuario e identificación con correo institucional | 🟡 | Registro, login, logout y `/me` funcionan (backend + pantallas). **No se valida el dominio institucional**: se acepta cualquier correo. El paso 2 (vehículo) existe en el API pero no hay pantalla. |
| RF-02 | Conductor publica viaje (punto de referencia de origen, campus destino, horario, lugares) | ⬜ | No existe modelo ni endpoint de viajes. |
| RF-03 | Conductor configura cuántos lugares ofrece | ⬜ | Solo existe `Vehiculo.asientos_disponibles` (1–8), no lugares por viaje. |
| RF-04 | Pasajero busca viajes por punto de referencia, horario y campus | ⬜ | |
| RF-05 | Pasajero solicita un lugar en un viaje publicado | ⬜ | |
| RF-06 | Conductor confirma o rechaza solicitudes | ⬜ | |
| RF-07 | Preferencias de compatibilidad (mixto / mismo sexo) | ⬜ | Solo se guarda `sexo` del usuario. |
| RF-08 | Mapa interactivo con rutas y puntos de encuentro | ⬜ | Solo hay `RaiteDocs/BD_PuntosMapa/Oxxo.json` (datos crudos de OSM). |
| RF-09 | Notificaciones de solicitudes, confirmaciones, cambios y cancelaciones | ⬜ | |
| RF-10 | Calificación mutua al terminar el viaje | ⬜ | Solo el campo `Usuario.calificacion` (0.00 por defecto). |
| RF-11 | Historial de viajes por usuario | ⬜ | |
| RF-12 | Reportar comportamiento inadecuado | ⬜ | Solo el campo `Usuario.suspendido` y el admin de Django. |

### No funcionales

| ID | Requerimiento | Estado | Notas |
|----|---------------|--------|-------|
| RNF-01 | Usabilidad: interfaz simple, puntos de referencia en vez de direcciones | ⬜ | No hay pantallas de viajes todavía. |
| RNF-02 | Seguridad: datos de contacto visibles solo entre conductor y pasajero tras confirmar | 🟡 | Hay auth JWT con refresh/blacklist. No hay datos de contacto (no existe teléfono) ni reglas de visibilidad. `SECRET_KEY` fija y `DEBUG=True`. |
| RNF-03 | Disponibilidad | ⬜ | Sin despliegue. |
| RNF-04 | Compatibilidad: diseño responsivo móvil/escritorio | 🟡 | Quasar es responsivo; solo existen login y registro. |
| RNF-05 | Escalabilidad: poder agregar usuarios y funciones | 🟡 | Backend organizado en apps Django; solo existe `accounts`. |
| RNF-06 | Rendimiento en búsqueda y mapa | ⬜ | No aplica aún. |

## Reglas de negocio

Vienen de la nota de voz del equipo. **Tienen prioridad sobre cualquier documento** si hay conflicto (en particular sobre `Raite_layout_disposition_002.md`, `UI_UX.md` y `Raite-Django-Models.md`, que describen otro flujo).

1. **Origen por catálogo de puntos de referencia.** El origen se elige de un catálogo de lugares conocidos (ej. "Oxxo Dunas", "Del Río"), nunca por calles ni direcciones exactas. El punto exacto de recogida lo acuerdan conductor y pasajero **después** de que se acepta el raite.
2. **Lugares los define el conductor**: de 1 a 5, según su vehículo.
3. **Preferencia de compatibilidad**: cada usuario (conductor o pasajero) solo puede elegir **"mismo sexo"** o **"mixto"**. Nadie puede pedir exclusivamente el sexo opuesto. Si el conductor o **cualquier** pasajero eligió "mismo sexo", **todos** los integrantes del viaje deben tener el mismo valor en el campo `sexo` (un usuario `X` con "mismo sexo" solo empata con otros `X`).
4. **Datos de contacto** (y placas del vehículo) solo se muestran entre conductor y pasajero una vez confirmado el raite.
5. **Acceso solo con correo institucional de la UACJ** (`@alumnos.uacj.mx`), activado con código de verificación.

## Fuera de alcance

De la carta del proyecto. No implementar sin que se pida explícitamente:

- Pagos dentro de la app.
- Seguimiento GPS permanente de los usuarios.
- Conductores externos a la comunidad universitaria.
- Cobertura fuera de Ciudad Juárez.
- Integración con sistemas internos de la UACJ.

(La carta también excluye: servicio profesional tipo Uber/DiDi y transporte propiedad de la universidad.)

## Decisiones tomadas

Decididas el 2026-11-06. Tienen la misma prioridad que las reglas de negocio.

1. **Nombre:** [NOMBRE] (por confirmar). Si no es "Raite", no renombrar nada en el código todavía.
2. **Sexo:** se mantienen `M`, `F` y `X`. "Mismo sexo" = mismo valor del campo `sexo`. Un usuario `X` con "mismo sexo" solo empata con otros `X`.
3. **Correo institucional:** solo `@alumnos.uacj.mx`. La cuenta se activa con un código de verificación enviado por correo.
4. **Contacto:** campo de teléfono/WhatsApp en el usuario, visible solo entre conductor y pasajero con raite confirmado.
5. **Puntos de referencia:** modelo con nombre, latitud y longitud, administrado desde el admin de Django. Carga inicial desde `RaiteDocs/BD_PuntosMapa/Oxxo.json`. Sin PostGIS; cercanía con haversine en Python.
6. **Campus:** CU, IIT, ICB, ICSA, IADA.
7. **Mapa:** Leaflet + OpenStreetMap.
8. **Notificaciones:** solo dentro de la app (modelo + consulta periódica). Sin push ni WebSockets.
9. **Lugares por viaje:** 1 a 5. `Vehiculo.asientos_disponibles` también se limita a 1–5.
10. **Despliegue:** se define al final.
11. **Base de datos:** PostgreSQL local por desarrollador (son dos). `Back_Raite/.env.example` con todas las variables; `SECRET_KEY` y `DEBUG` por variable de entorno; `certs/ca.pem` opcional por variable; datos iniciales con un comando de `manage.py`; pasos para levantar desde cero en el `README.md`.

## Plan de trabajo

Se construye **por capas, no por funcionalidad**. El objetivo es dejar una base completa y entendible para que quien siga solo tenga que ajustar detalles. **No se empieza una capa hasta terminar y probar la anterior.**

0. **Base de datos local** — `.env.example`, settings por variables de entorno, certificado opcional, comando de carga inicial, README. ⬜
1. **Capa 1 — Modelos** ⬜
   - Todos los modelos que cubren RF-01 a RF-12 y las reglas de negocio: usuarios, vehículo, campus, puntos de referencia, viajes, solicitudes, notificaciones, calificaciones, reportes, verificación de correo.
   - Validaciones a nivel modelo, migraciones, registro en el admin de Django y tests de modelo.
   - Diagrama entidad-relación en Mermaid dentro de `RaiteDocs/`.
2. **Capa 2 — Lógica** (serializers, views del API y servicios) ⬜
   - Endpoints y reglas de negocio: compatibilidad por sexo, cupo de lugares, visibilidad de contacto, estados del viaje y de la solicitud, verificación de correo.
   - Tests de API.
3. **Capa 3 — Vistas** (páginas de Quasar) ⬜
   - Pantallas que consumen el API. Sin bocetos: diseño simple y funcional con componentes de Quasar.

Al terminar cada capa, actualizar aquí su estado y la tabla de requerimientos.

## Convenciones

- **Interfaz en español** (textos, mensajes de error, etiquetas). Código del dominio también en español, como ya está (`correo`, `nombre`, `Vehiculo`…).
- **Commits pequeños, uno por funcionalidad.** Citar el requerimiento cuando aplique (ej. `feat(accounts): valida correo institucional (RF-01)`).
- **No agregar requerimientos que no estén en los docs sin preguntar.** Si algo parece necesario y no está en el SRS, la carta o las reglas de negocio de arriba, preguntar primero.
- **Preguntar antes de cambiar el stack o instalar dependencias grandes** (PostGIS/GeoDjango, Channels, Celery, Redis, librerías de mapas, etc.).
- Los diseños técnicos en `RaiteDocs/` (arquitectura por capas, `Raite-Django-*.md`, `UI_UX.md`, `Raite_layout_disposition_002.md`) son referencia, no obligación: no construir toda la arquitectura DDD de golpe; seguir el patrón simple de `apps/accounts` y crecer cuando haga falta.
- Los archivos de `RaiteDocs/docs/` vienen de Google Docs: no editarlos a mano aquí (ver `RaiteDocs/docs/README.md`).
- `Front_Raite/src/router/typed-router.d.ts` es generado: no editar a mano.
- Antes de dar por terminado un cambio: `python manage.py test` (backend) y `pnpm lint:check && pnpm typecheck` (frontend).
- `AGENTS.md` pide usar `graphify` para consultas del código y correr `graphify update .` tras modificarlo, si la herramienta está instalada.
