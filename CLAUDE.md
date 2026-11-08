# CLAUDE.md

Fuente de verdad del proyecto para Claude Code. Última revisión: 2026-11-07 (Capa 3 rediseñada para computadora).
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
- Variables de entorno (plantilla en `Back_Raite/.env.example`): `SECRET_KEY` y `DATABASE_URL` obligatorias; `DEBUG`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `DB_SSL_ROOTCERT` (opcional) y las de correo (`EMAIL_BACKEND`, por defecto consola).
- `LANGUAGE_CODE = es-mx`, `TIME_ZONE = America/Ciudad_Juarez`. Constantes de la app en `settings.py`: `CORREO_DOMINIO_PERMITIDO`, `CODIGO_VERIFICACION_MINUTOS` (15), `CODIGO_VERIFICACION_MAX_INTENTOS` (5), `CODIGO_REENVIO_SEGUNDOS` (60), `BUSQUEDA_RADIO_KM` (3) / `BUSQUEDA_RADIO_MAX_KM` (15), `VENTANA_CRUCE_MINUTOS` (60), `INICIO_ANTICIPACION_MINUTOS` (30), `VENCIMIENTO_HORAS` (2).
- Datos iniciales: `python manage.py cargar_datos_iniciales` (campus + puntos de referencia desde `apps/locations/data/*.json`; se puede repetir y no pisa lo editado en el admin, salvo `--actualizar-estados`, que copia `activo` del JSON).
- Pasos completos para una máquina nueva: `README.md`.

```bash
cd Back_Raite
pip install -r requirements.txt
python manage.py runserver            # http://localhost:8000
python manage.py migrate
python manage.py makemigrations
python manage.py check
python manage.py cargar_datos_iniciales                 # campus y puntos de referencia
python manage.py crear_datos_demo --reiniciar           # usuarios, viajes y solicitudes de demo (correos *.demo@, contraseña raite1234)
python manage.py probar_correo tu@alumnos.uacj.mx otro@gmail.com   # muestra del correo del código (usa el EMAIL_BACKEND del .env)
python manage.py generar_puntos_osm                     # SOLO para regenerar puntos_referencia.json (usa internet, ~3 min)
python manage.py test                                   # todos los tests (el usuario de BD necesita CREATEDB)
python manage.py test apps.rides                        # una app
python manage.py test apps.accounts.tests.test_auth_api # un módulo
```

- Las pruebas se escriben con las fábricas de `apps/accounts/tests/factories.py` y `apps/rides/tests/factories.py`.
- Probar siempre en PostgreSQL: SQLite no detecta, por ejemplo, textos más largos que la columna.

### Frontend — `Front_Raite/` (TypeScript)

- Quasar 2.30 (Vite, `@quasar/app-vite` 3.8), Vue 3.5, Vue Router 5 (rutas por archivo), Pinia 4, Axios, `validator`, Leaflet 1.9 (mapas con OpenStreetMap). Node `^22.12 || ^24 || >=26`. **pnpm** es el gestor canónico.
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

- Notificaciones: la consulta periódica desde el frontend (a `GET /api/notificaciones/conteo/`) se hace en la Capa 3. Sin push ni WebSockets.

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
│   ├── Raite_DjangoRest/  # paquete del proyecto: settings.py, urls.py, api.py (errores comunes), wsgi/asgi
│   ├── .env.example     # plantilla de variables de entorno
│   └── apps/            # cada app: models.py, models_choices.py, services.py, serializers.py, views.py, urls.py, admin.py, migrations/, tests/
│       ├── accounts/    # Usuario, Vehiculo, CodigoVerificacion + auth JWT y verificación de correo (urls_auth.py, permissions.py)
│       ├── locations/   # Campus, PuntoReferencia, geo.py (haversine); data/*.json; comandos cargar_datos_iniciales y generar_puntos_osm
│       ├── rides/       # Viaje, Solicitud, compatibilidad.py; búsqueda e historial (estados y transiciones en models_choices.py)
│       ├── notifications/ # Notificacion
│       ├── ratings/     # Calificacion
│       └── reports/     # Reporte
├── Front_Raite/         # SPA Quasar
│   ├── quasar.config.ts
│   └── src/
│       ├── boot/        # axios.ts (instancia `api` + refresh de token en 401), auth-init.ts
│       ├── stores/      # auth-store.ts (sesión, rol, rol activo); example-store.ts es de plantilla
│       ├── router/      # index.ts (guardas); typed-router.d.ts es GENERADO, no editar
│       ├── layouts/     # AppLayout.vue (con sesión) y PublicoLayout.vue (entrar, registro, verificar)
│       ├── components/  # TarjetaViaje, TarjetaDestacada, BarraAccion, MapaRaite, selectores, chips…
│       ├── assets/      # logo-raite.png (fondo claro) y logo-raite-sobre-azul.png
│       └── pages/       # rutas por archivo (ver abajo)
├── RaiteDocs/           # documentación (mayormente en español)
│   ├── docs/            # documentos formales exportados de Google Drive (SRS, propuesta fase 1/2)
│   ├── Design/          # UI_UX.md, layouts_team.md, imágenes, PDF de diseño y logo/ (logo original)
│   ├── Context/         # system_solutions_context.md
│   ├── Modelo-ER.md     # diagrama ER y de estados de la Capa 1 (fuente de verdad del modelo)
│   ├── API.md           # lista de endpoints de la Capa 2 (método, URL, quién, qué hace)
│   ├── BD_PuntosMapa/   # Oxxo.json (export crudo de Overpass; incluye puntos de Juárez, N.L. que se descartan)
│   ├── Sketches/, TeamTasks/
│   └── Raite-*.md, tecnologias.md, uml_*.mmd, …  # diseño técnico del equipo anterior
├── .claude/settings.json # config. local de Claude Code (commits sin atribución); ignorado por git
├── graphify-out/        # grafo de conocimiento generado (ver AGENTS.md)
└── .opencode/           # configuración de opencode + plugin graphify
```

### Detalles del backend que importan

- `AUTH_USER_MODEL = 'accounts.Usuario'` (PK UUID), `USERNAME_FIELD = "correo"`: el `ModelBackend` normal inicia sesión por correo, no hace falta backend propio.
- Campos y modelos **en español** (`correo`, `nombre`, `apellidos`, `edad` 17–70, `sexo`, `carrera`, `calificacion` 0.00–5.00, `suspendido`, …). Mantener esa convención.
- **Un solo campo `rol`** (entero): `1=ADMIN`, `2=PASAJERO`, `3=CONDUCTOR`, `4=AMBOS`. Helpers: `es_pasajero`, `es_conductor`, `es_admin`, `puede_publicar_viaje()`, `puede_solicitar_lugar()`. ADMIN no se puede obtener en el registro público.
- `Usuario` además tiene `telefono` (10 dígitos), `preferencia_compatibilidad` (`MISMO_SEXO`/`MIXTO`, por defecto `MIXTO`), `correo_verificado` y `suspendido`. El dominio `@alumnos.uacj.mx` se valida en `Usuario.clean()` (el ADMIN queda exento). Las cachés antiguas `activo`/`cuenta_activa` se eliminaron.
- `Sexo`: `M`, `F`, `X` ("Otro"). Se mantienen los tres (ver Decisiones tomadas).
- `Vehiculo` (1 a 1 con el usuario): marca, modelo, color, placas (únicas), tipo (`COCHE`/`CAMIONETA`/`TROCA`), `asientos_disponibles` 1–5.
- Modelo completo, estados y qué regla vive en cada modelo: **`RaiteDocs/Modelo-ER.md`**. Endpoints: **`RaiteDocs/API.md`**.
- **Dónde va cada cosa:** los modelos solo validan un registro (`clean()`, validadores, restricciones de BD). Las reglas entre varios registros están en `services.py` de cada app: funciones dentro de `transaction.atomic()` que llaman `full_clean()` antes de guardar y crean las notificaciones con `apps/notifications/services.notificar()`. Los serializers solo dan forma a la entrada y la salida; las vistas son delgadas.
- **Errores:** los servicios lanzan `ValidationError` de Django (el manejador de `Raite_DjangoRest/api.py` la convierte en 400), `PermissionDenied` (403), `Http404` o `Conflicto` (409, para conflictos de estado).
- **Permisos:** por defecto todo el API pide sesión y `correo_verificado` (`CorreoVerificado`); los endpoints públicos declaran `AllowAny`. Otras clases en `accounts/permissions.py`: `PuedePublicar`, `PuedeSolicitar`, `IsDriver`, `IsPassenger`. Quién es dueño del viaje o de la solicitud se revisa en el servicio.
- **Cupo:** aceptar una solicitud bloquea la fila del viaje (`select_for_update`). Hay una prueba con dos hilos que solo funciona en PostgreSQL.
- **Viaje vencido:** un `PUBLICADO` con más de 2 h de retraso. Se calcula (`Viaje.esta_vencido`, `Viaje.objects.vencidos()` / `vigentes()`), no se guarda: solo se puede cancelar y no cuenta para cruces ni búsquedas.
- Paginación de 20 en los listados; los catálogos y las calificaciones pendientes no se paginan.
- JWT: acceso 30 min, refresh 1 día, rotación + blacklist.
- Migraciones de `accounts`: 0001–0012 vienen del equipo anterior (la 0009 se corrigió para que funcione en un PostgreSQL vacío); 0013 es de la Capa 1.

### Detalles del frontend que importan

- **Capa 3 (vistas) rediseñada** el 2026-11-07 siguiendo `DESIGN.md` y `PRODUCT.md` (raíz del repo, versionados): tema de Quasar con colores UACJ, fuentes Atkinson Hyperlegible en `src/css/fonts/`, botones en píldora, campos rellenos y tarjetas con sombra suave. La estructura viene de una maqueta inspirada en el Figma de NeoFracc.
- **Prioridad: computadora.** El prototipo se presenta en una PC, así que cada vista se diseñó para ≥1024 px aprovechando todo el ancho (columnas, cuadrículas, barras horizontales). El celular funciona pero no se ha pulido: no invertir en él sin que se pida, y no romperlo.
- **Layout con sesión (`AppLayout.vue`):** en computadora, barra superior azul tenue a todo el ancho (logo, cambio de papel, campanita, usuario) y menú lateral blanco fijo (Inicio, las dos secciones del papel, Historial, Avisos, Perfil, Cerrar sesión); las pantallas con `meta.atras` muestran "Regresar" y su título arriba del contenido. En celular, encabezado blanco y barra inferior blanca de cuatro pestañas.
- **Layout público (`PublicoLayout.vue`):** panel azul con el logo y los puntos de confianza a la izquierda y el formulario en una tarjeta a la derecha; `meta.amplio` (registro) ensancha la tarjeta.
- **Piezas del tema (`app.scss`):** `raite-contenedor--ancho` (página a todo el ancho), `raite-cabecera` (título + resumen + acción), `raite-rejilla-tarjetas` (cuadrícula de tarjetas de la misma altura), `raite-btn-xl` (acción principal de 56 px), `raite-titulo--marca`. Los h1–h6 tienen interlineado 1.3 (Quasar los trae enormes).
- **`BarraAccion`:** en celular es la barra fija de abajo (la página lleva `con-barra`); en computadora se dibuja donde esté como una tarjeta, para no tapar el menú lateral.
- Rutas por archivo (`filenameBasedRouting: true`), modo **`history`**. Cada página declara con `definePage({ meta })` si es `publico`, el `papel` que necesita (`pasajero`/`conductor`), su `titulo`, si es secundaria `atras` (ruta de regreso; sin barra inferior) y, en públicas, `amplio`. `App.vue` elige `PublicoLayout` o `AppLayout` según `meta.publico`.
- **Ojo con el servidor de desarrollo:** al reescribir un `.vue` completo, el plugin de rutas a veces deja de leer su `definePage` (la pantalla sale con título "Raite" y sin "Regresar"). Se arregla reiniciando `pnpm dev`; no es un error del código.
- Páginas: `/entrar`, `/registro`, `/verificar`, `/inicio`, `/vehiculo`, `/buscar`, `/mis-raites`, `/mis-viajes`, `/publicar` (`?editar=id`), `/viajes/[id]` (detalle para pasajero y conductor), `/viajes/[id]/solicitudes`, `/viajes/[id]/calificar`, `/viajes/[id]/reportar`, `/avisos`, `/historial`, `/perfil` y la 404.
- Guarda global en `router/index.ts`: sin sesión todo lo no público manda a `/entrar?siguiente=…`; `/` y el inicio de sesión mandan a `/inicio` (la misma para los dos papeles; su contenido cambia con el papel). Con rol AMBOS, abrir una pantalla del otro papel cambia el papel activo.
- Capas: `src/api/` (una función por endpoint, `tipos.ts`, `errores.ts`), `src/stores/` (`sesion`, `catalogos`, `avisos` con la consulta periódica de 30 s), `src/utils/` (`formato.ts` con horas en `America/Ciudad_Juarez`, `avisar.ts` con Notify y diálogos de confirmación), `src/components/` (tarjeta de viaje, placa de campus, mapa, selectores…).
- `boot/axios.ts` rechaza con el error original de axios (para leer la respuesta del API con `leerError`) y renueva el token en 401.
- Para probar sin runner: `python manage.py crear_datos_demo --reiniciar`, `runserver` y `pnpm dev`; el código de verificación sale en la consola de Django.
- Tokens en `localStorage`. Usa el alias `@/` para `src/`.
- `tsconfig.json` apunta los tipos de `#q-app` a `node_modules/@quasar/app-vite/...` (ruta estable). Antes usaba rutas de `node_modules/.pnpm/` con hash, que se rompían con cada `pnpm install`.

## Requerimientos

Fuente: `RaiteDocs/docs/2_SRS.md`. Estado según el código al 2026-11-07 (Capa 3 con pantallas). ✅ = API con tests y pantalla probada a mano con los datos de demo.
✅ hecho · 🟡 parcial · ⬜ pendiente

### Funcionales

| ID | Requerimiento | Estado | Notas |
|----|---------------|--------|-------|
| RF-01 | Registro de usuario e identificación con correo institucional | ✅ | API completa: registro con `@alumnos.uacj.mx` y código por correo, `verificar/`, `reenviar-codigo/`, login bloqueado sin verificar, perfil y vehículo. Pantalla hecha. |
| RF-02 | Conductor publica viaje (punto de referencia de origen, campus destino, horario, lugares) | ✅ | `POST /api/viajes/` (sin cruces de horario), edición, cancelar/iniciar/finalizar y catálogos `campus/` y `puntos/`. Pantalla hecha. |
| RF-03 | Conductor configura cuántos lugares ofrece | ✅ | `lugares_ofrecidos` 1–5, sin superar los asientos ni bajar de los aceptados (al publicar y al editar). Pantalla hecha. |
| RF-04 | Pasajero busca viajes por punto de referencia, horario y campus | ✅ | `GET /api/viajes/` con radio por haversine, campus, sentido y horario, filtrando por compatibilidad. Pantalla hecha. |
| RF-05 | Pasajero solicita un lugar en un viaje publicado | ✅ | `POST /api/viajes/{id}/solicitudes/` y `GET /api/solicitudes/mias/`; cancelar. Pantalla hecha. |
| RF-06 | Conductor confirma o rechaza solicitudes | ✅ | Aceptar/rechazar con bloqueo del viaje para no rebasar el cupo. Pantalla hecha. |
| RF-07 | Preferencias de compatibilidad (mixto / mismo sexo) | ✅ | `PATCH /api/auth/me/`; regla aplicada al buscar, solicitar, aceptar y editar el viaje. Pantalla hecha. |
| RF-08 | Mapa interactivo con rutas y puntos de encuentro | ✅ | El API da coordenadas de campus y puntos (y `distancia_km`). Pantalla hecha. |
| RF-09 | Notificaciones de solicitudes, confirmaciones, cambios y cancelaciones | ✅ | Se crean en cada cambio de estado; endpoints para listar, contar y marcar leídas. Pantalla hecha. |
| RF-10 | Calificación mutua al terminar el viaje | ✅ | `POST /api/viajes/{id}/calificaciones/` con recálculo de `Usuario.calificacion`; pendientes por calificar. Pantalla hecha. |
| RF-11 | Historial de viajes por usuario | ✅ | `GET /api/historial/` como conductor y como pasajero. Pantalla hecha. |
| RF-12 | Reportar comportamiento inadecuado | ✅ | `POST /api/reportes/` y `GET /api/reportes/mios/`; el admin resuelve y suspende. Pantalla hecha. |

### No funcionales

| ID | Requerimiento | Estado | Notas |
|----|---------------|--------|-------|
| RNF-01 | Usabilidad: interfaz simple, puntos de referencia en vez de direcciones | ✅ | Origen siempre por catálogo (lista con búsqueda y mapa). Una acción principal por pantalla. |
| RNF-02 | Seguridad: datos de contacto visibles solo entre conductor y pasajero tras confirmar | ✅ | Teléfono y placas solo con solicitud `ACEPTADA` (probado en API y en pantalla). JWT, permisos por rol y secretos por variable de entorno. |
| RNF-03 | Disponibilidad | ⬜ | Sin despliegue. |
| RNF-04 | Compatibilidad: diseño responsivo móvil/escritorio | ✅ | Escritorio: barra superior y menú lateral, vistas a todo el ancho (revisado a 1900 y 1280 px). Celular: encabezado y barra inferior; funciona, pero el rediseño se pulió para computadora. |
| RNF-05 | Escalabilidad: poder agregar usuarios y funciones | 🟡 | 6 apps Django con servicios separados de las vistas; índices en las consultas principales; paginación. |
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
5. **Puntos de referencia:** modelo con nombre, latitud y longitud, administrado desde el admin de Django. Carga inicial desde `RaiteDocs/BD_PuntosMapa/Oxxo.json`. Sin PostGIS; cercanía con haversine en Python. Basta con la calle para que un punto quede activo (OSM casi no tiene colonias en Juárez); si Nominatim no dio ni calle, se carga con `activo=False` para revisarlo en el admin. Hoy los 128 tienen calle. Para aplicar un cambio de estados del JSON a una BD que ya tiene los puntos: `cargar_datos_iniciales --actualizar-estados`.
6. **Campus:** CU, IIT, ICB, ICSA, IADA. Coordenadas tomadas de OSM; IIT e IADA comparten ubicación (por confirmar).
7. **Mapa:** Leaflet + OpenStreetMap.
8. **Notificaciones:** solo dentro de la app (modelo + consulta periódica). Sin push ni WebSockets.
9. **Lugares por viaje:** 1 a 5. `Vehiculo.asientos_disponibles` también se limita a 1–5.
10. **Despliegue:** se define al final.
11. **Base de datos:** PostgreSQL local por desarrollador (son dos). `Back_Raite/.env.example` con todas las variables; `SECRET_KEY` y `DEBUG` por variable de entorno; `certs/ca.pem` opcional por variable; datos iniciales con un comando de `manage.py`; pasos para levantar desde cero en el `README.md`.

## Plan de trabajo

Se construye **por capas, no por funcionalidad**. El objetivo es dejar una base completa y entendible para que quien siga solo tenga que ajustar detalles. **No se empieza una capa hasta terminar y probar la anterior.**

0. **Base de datos local** — `.env.example`, settings por variables de entorno, certificado opcional, comando de carga inicial, README. ✅
1. **Capa 1 — Modelos** ✅ (121 tests pasando en PostgreSQL; ver `RaiteDocs/Modelo-ER.md`)
   - Todos los modelos que cubren RF-01 a RF-12 y las reglas de negocio: usuarios, vehículo, campus, puntos de referencia, viajes, solicitudes, notificaciones, calificaciones, reportes, verificación de correo.
   - Validaciones a nivel modelo, migraciones, registro en el admin de Django y tests de modelo.
   - Diagrama entidad-relación en Mermaid dentro de `RaiteDocs/`.
2. **Capa 2 — Lógica** ✅ (268 tests pasando en PostgreSQL; endpoints en `RaiteDocs/API.md`)
   - Servicios, serializers y vistas para todos los RF; reglas de compatibilidad, cupo con bloqueo, visibilidad de contacto, transiciones, vencimiento calculado, verificación de correo, notificaciones, promedio de calificación, historial y reportes.
   - Tests de API por endpoint, incluida la concurrencia al aceptar.
3. **Capa 3 — Vistas** (páginas de Quasar) ✅ (en `capa/vistas`; diseño en `DESIGN.md`)
   - Variantes elegidas en el lienzo de diseño: búsqueda B (mapa con hoja de resultados), detalle A (con Llamar/WhatsApp), publicar A (con vista previa), solicitudes B (cupo como asientos).
   - Backend agregado en esta capa: `solicitudes_pendientes` en `viajes/mios/`, pasajero que registra vehículo pasa a AMBOS, comando `crear_datos_demo`.
   - **Rediseño (2026-11-07), solo frontend**, una rama por parte encadenada a la anterior: `capa/vistas-entrar` (tema, layout público, Entrar, logo) → `-navegacion` → `-busqueda` → `-acceso` (registro, verificar, vehículo) → `-inicio` (pantalla nueva) → `-detalle` (detalle y solicitudes) → `-mis-viajes` (mis raites, mis viajes, publicar) → `-cuenta` (avisos, historial, perfil) → `-calificar` (calificar, reportar, 404) → `-cierre`. Revisado con capturas a 1900 y 1280 px; `pnpm lint:check`, `pnpm typecheck` y `pnpm build` pasan.
   - Logo decidido (ver `PRODUCT.md`). Pendiente: confirmar el nombre, pulir el celular, despliegue (RNF-03) y medir rendimiento (RNF-06).

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
- **Una rama por capa:** `capa/modelos` (Capa 1, ya integrada en `main`), `capa/logica` (Capa 2), `capa/vistas` (Capa 3). Cada rama sale de `main` después de integrar la capa anterior; se trabaja en la rama de la capa en curso. Las partes de una capa van en ramas con guion (`capa/vistas-inicio`), nunca con diagonal (`capa/vistas/inicio` choca con la rama `capa/vistas`).
- **En el rediseño los commits los hace el usuario:** al terminar cada parte, Claude le da la rama, los `git add` y los mensajes exactos (pequeños, uno por cambio, `feat(front): …` en español) y no corre `git commit` ni `git push`.
- **Solo commits locales: no hacer push ni abrir PR.** Del push se encarga el usuario.
- **Los mensajes de commit no llevan `Co-Authored-By` ni ninguna mención a Claude** (también configurado en `.claude/settings.json`, que es local: `.claude/` está en `.gitignore`).
- `AGENTS.md` pide usar `graphify` para consultas del código y correr `graphify update .` tras modificarlo, si la herramienta está instalada.
