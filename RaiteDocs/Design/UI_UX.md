# Raite — Pantallas del Frontend (UI/UX)

> Descripción de las pantallas que debe tener el frontend (Quasar SPA/PWA) para ser pasada a una IA de diseño.
> Extraído exclusivamente de la documentación en `RaiteDocs/`, corregido según decisiones del producto.
> Los ítems marcados **[PENDIENTE - confirmar]** requieren respuesta antes de que la IA los plasme en el diseño.

---

## 1. Resumen del sistema

Raite es una plataforma web de viajes compartidos para estudiantes de la UACJ.
- **Stack frontend:** Quasar 2.x (Vue 3 + Vite), Pinia, Vue Router, Leaflet/OpenStreetMap, HTML5 Geolocation API, PWA/Workbox (planificado).
- **Roles:** `PASAJERO`, `CONDUCTOR`. Un usuario puede tener **ambos roles** (selección múltiple en el registro). No existe `ADMIN` en el registro público.
- **Catálogo cerrado de puntos:** Walmart, S-Mart, Sam's, Soriana, Oxxo, Aurrerá, Superette, Del Río, Extra, Circle K. El CU es punto fijo del sistema, no seleccionable.
- **Tipos de viaje:** `Entrada` (hacia CU) y `Salida` (desde CU).
- **hora_objetivo:** horas enteras 07:00–22:00.
- **Beta 1:** sin verificación de correo electrónico.

---

## 2. Pantallas de Autenticación

### 2.1 Login
**Ruta:** `/login` (layout `AuthLayout`)
**Documentación:** `Raite_layout_disposition_002.md` §Autenticación; `Raite_layout_disposition.md` §LOG IN / REGISTER

| Ítem | Descripción |
|------|-------------|
| Campo Correo | Campo de texto obligatorio (login por correo, `USERNAME_FIELD = 'correo'`) |
| Campo Contraseña | Campo de contraseña obligatorio |
| Botón Iniciar sesión | Envía `POST /api/auth/token/` (JWT access/refresh) |
| Navegación a Registro | Enlace a Registro - Paso 1 |

**Nota:** No hay pantalla de recuperación de contraseña ni verificación de email en la beta 1.

---

### 2.2 Registro - Paso 1
**Ruta:** `/register` (layout `AuthLayout`)
**Formato:** ventana modal/emergente con `q-options` (selección múltiple)
**Documentación:** `Raite_layout_disposition_002.md` §Autenticación; `first_correction_phase2.md` §C10; decisiones del usuario

| Ítem | Descripción |
|------|-------------|
| Campo Nombre completo | Nombre y apellidos (obligatorios) |
| Campo Correo | Correo electrónico obligatorio (@uacj.mx implícito por identidad UACJ) |
| Campo Contraseña | Mínimo 8 caracteres (obligatorio) |
| `q-options` roles | Opciones: `Pasajero`, `Conductor`. **Selección múltiple permitida:** el usuario puede marcar ambos. Si marca `Conductor` (o ambos), se activa el Paso 2. |
| Botón Continuar / Crear cuenta | Envía `POST /api/auth/register/` con `roles: ListField` (máx. 2, sin duplicados, sin `ADMIN`) |
| Respuesta esperada | `201` con `id`, `rol`, `suspendido`, `requiere_vehiculo: true` si se seleccionó `CONDUCTOR` |

**[PENDIENTE - confirmar]:** ¿El `q-options` permite seleccionar ambos roles simultáneamente y el backend crea dos filas en `UsuarioRol` (una por rol), o se envía un solo rol y el segundo se asigna después?

---

### 2.3 Registro - Paso 2 (Condicional: Datos del Vehículo)
**Ruta:** `/register/vehicle` (layout `AuthLayout`)
**Solo si el usuario seleccionó rol `Conductor`** (directo o vía ambos roles)
**Documentación:** `Raite_layout_disposition_002.md` §Autenticación; `Raite_layout_disposition.md`; `first_correction_phase2.md` §C6, §C10

| Ítem | Descripción |
|------|-------------|
| Campo Marca | Texto obligatorio |
| Campo Modelo | Texto obligatorio |
| Campo Color | Texto obligatorio |
| Campo Placas | Texto obligatorio, único, normalizado a mayúsculas sin guiones |
| Selector Tipo de vehículo | `Camioneta`, `Coche`, `Troca` |
| Campo Número de asientos disponibles | Entero 1–8 (pasajeros, excluye al conductor) |
| Checkbox `activo` | Booleano, default `true`. `activo=false` → `es_valido_para_conducir()=false` y modo "Dar Raite" bloqueado (controlado por Admin) |
| Botón Registrar vehículo | Envía `POST /api/auth/vehicle/` (403 si no tiene rol conductor) |
| Respuesta esperada | `201` con `id`, `placas`, `vehiculo_valido: true` |

---

## 3. Pantalla Home (Dashboard)

**Ruta:** `/` (layout `MainLayout`)
**Documentación:** `Raite_layout_disposition_002.md` §PANTALLA HOME

La Home se divide en dos paneles. El contenido de Panel 2 depende del estado del raite del usuario y de su rol.

### 3.1 Panel 1 - Selección de Viaje y Rol Activo

| Ítem | Tipo | Opciones | Notas |
|------|------|----------|-------|
| Tipo de viaje | Radio / Select | `Entrada` (a la escuela), `Salida` (de la escuela) | Requerido |
| **Rol activo** | `q-toggle` | `Pasajero`, `Conductor` | **Solo si el usuario tiene ambos roles**; si solo tiene uno, se oculta y se usa ese rol. Al cambiarlo aparece una ventana de confirmación; al confirmar, se recargan las páginas y aparece el índice de conductor o de pasajero, pero no ambos a la vez. |

### 3.2 Panel 2 - Tarjetas de Estado Dinámico

Según `002.md` (5 estados), las tarjetas son distintas por rol. El pasajero nunca ve "Esperando respuesta" y el conductor nunca ve "te ofrecen el raite". Cada estado se deriva de los bools del raite, no de un enum.

| Estado | Disparador | Datos mostrados | Botones / Acciones |
|--------|------------|-----------------|--------------------|
| 🟢 "¡Hola! Solicita un raite" | Pasajero sin solicitud activa | Estado vacío | CTA a "Pedir Raite" |
| 🔵 "¡X te ofrece el raite!" | Conductor tomó el raite (`PROPUESTO`, `aceptado=true, confirmado=false`) — el pasajero decide | Datos del Conductor (sin placas) + Datos del Viaje + temporizador de respuesta | **Aceptar** / **Rechazar** |
| 🟡 "Esperando respuesta del pasajero" | Solo conductor que tomó el raite y aún no hay respuesta (`PROPUESTO`) | Datos del Viaje + temporizador hasta `hora_objetivo` | (solo espera) |
| 🟣 "¡El pasajero aceptó tu raite!" | Pasajero aceptó (`confirmado=true`) — se muestra al conductor | Datos del Pasajero + Datos del Viaje + **placas desbloqueadas** | — |
| 🔴 "Raite rechazado" | Conductor cuya propuesta fue rechazada: raite en `CREADO` con `rechazado=true` | Motivo opcional | CTA "Buscar otro raite"; `cuenta_activa` vuelve a 0 |
| ⚫ "¡Tienes un raite programado!" | Acuerdo cerrado (`confirmado=true`) | Datos del Contraparte + Datos del Viaje + placas incluidas + hora de encuentro | — |

---

## 4. Pedir Raite (Pasajero) — Crea un RAITE

**Ruta:** `/trips/create` o integrado en Home con panel derecho (mapa) + panel izquierdo (detalle)
**Documentación:** `Raite_layout_disposition_002.md` §PEDIR RAITE

| Paso | Componente | Ítems |
|------|------------|-------|
| 1 | Vista de Mapa (panel derecho) | Mapa con **puntos del catálogo** (Walmart, S-Mart, Sam's, Soriana, Oxxo, Aurrerá, Superette, Del Río, Extra, Circle K) como marcadores seleccionables. Solo `activo=true`. <br>**Entrada:** punto elegido = recogida <br>**Salida:** punto elegido = destino (recogida fija en CU) |
| 2 | Botón "Crear Raite" | Invoca `Raite.crear()` con: `rol_actual` (si tiene ambos roles), `hora_objetivo` (07:00–22:00, horas enteras), `tipo`, `punto_origen`, `punto_destino`, `pasajeros_requeridos`, `configuracion` |
| 3 | Panel de Detalle del Punto (panel izquierdo) | Nombre del comercio y sucursal, coordenadas, conductores cercanos, ETA |

**Configuración de viaje (`configuracion`, JSON):**
- Mismo sexo
- Usar cajuela
- Mascotas

**Validaciones:**
- `validar_puntos()`: CU fijo según `tipo` + ambos extremos en el catálogo. No se admiten coordenadas libres.
- `validar_hora_objetivo()`: 07:00–22:00, horas enteras.
- `no_tiene_raite_en_curso()`: `cuenta_activa == 0` (bloqueo, 409 si ya tiene raite activo).

**Ciclo de vida tras crear:**
- `activo=true` al crearse
- Si nadie toma antes de `hora_objetivo` → `activo=false` (expira)
- Conductor toma → `aceptado=true`, `PROPUESTO`, notifica al pasajero

---

## 5. Dar Raite (Conductor) — Toma un Raite y Propone

**Ruta:** `/trips/driver` o `/dar-raite` (mapa con puntos con raites activos)
**Documentación:** `Raite_layout_disposition_002.md` §DAR RAITE

| Paso | Componente | Ítems |
|------|------------|-------|
| 1 | Vista de Mapa (panel derecho) | **Solo los puntos con raites activos.** El conductor nunca ve el catálogo completo. <br>**Entrada:** marcadores en puntos de recogida con raites activos <br>**Salida:** marcadores en puntos de destino con raites activos (recogida en CU) <br>Cada marcador: nombre del comercio, nº de raites esperando, `hora_objetivo` más próxima |
| 2 | Botón "Tomar Raite" | Invoca `Raite.aceptar(conductor_id)`: valida vehículo, comprueba no haya intento `RECHAZADO` previo, setea `aceptado=true`, abre `RaiteIntento` (`PENDIENTE`), notifica al pasajero (`raite_propuesto`), sincroniza `cuenta_activa` |
| 3 | Pantalla "Esperando respuesta" | Conductor bloqueado (`cuenta_activa=1`) con temporizador hasta `hora_objetivo`. Recibe push: pasajero aceptó o rechazó |

**Validación previa (`puede_aceptar_raite()`):**
- `no_tiene_raite_en_curso()` → `cuenta_activa == 0`
- Posee rol `CONDUCTOR`
- `Vehiculo.es_valido_para_conducir()` (existe, completo y activo)
- `Vehiculo.tiene_capacidad(Raite.pasajeros_requeridos)`
- No existe `RaiteIntento` previo de ese conductor con `resultado = RECHAZADO` para ese raite
- `cantidad_rechazos < MAX_RECHAZOS_POR_RAITE` (3)

**Nota:** El conductor no ve las placas del pasajero ni contacto al tomar. Las placas se desbloquean tras `confirmado=true`.

---

## 6. Responder al Raite (Pasajero) — Aceptar o Rechazar al Conductor

**Ruta:** integrado en Home (tarjeta 🔵) o `/trips/{id}/propuesta`
**Documentación:** `Raite_layout_disposition_002.md` §RESPONDER AL RAITE

| Paso | Componente | Ítems |
|------|------------|-------|
| 1 | Notificación push / in-app | `Notificacion(tipo='raite_propuesto')`. Texto ejemplo: "Un conductor te ofrece el raite de las 07:00" |
| 2 | Pantalla de decisión | Datos del conductor para decidir: nombre, calificación (★), tipo de vehículo, modelo/color, ETA, `hora_objetivo`, punto de recogida, requisitos del viaje. **Las placas siguen ocultas** hasta aceptar |
| 3 | Botón "Aceptar conductor" | Invoca `Raite.responder(acepta=True)` → `confirmado=true`, notifica al conductor, desbloquea placas/datos de contacto, raite queda programado |
| 4 | Botón "Rechazar" | Invoca `Raite.responder(acepta=False)` → `rechazado=true`, `aceptado=false`, `conductor_id=null`, notifica al conductor, libera su `cuenta_activa`, devuelve raite al mapa |

**Reglas:**
- Ventana de decisión: hasta `hora_objetivo`. Temporizador visible en ambas pantallas ("faltan X min para responder").
- `responder()` solo válido en `PROPUESTO` (`aceptado=true ∧ confirmado=false ∧ rechazado=false ∧ finalizado=false`). Solo el `pasajero_id` puede responder.
- Doble toque o respuesta tardía → `409 Conflict` / `422`.
- Límite de rechazos: `MAX_RECHAZOS_POR_RAITE = 3` (configurable, derivado del historial `RaiteIntento`).

---

## 7. Seguimiento GPS en Vivo (viaje EN_CURSO)

**Ruta:** mismo mapa de pedir viaje / detalle del raite activo
**Documentación:** `Raite_layout_disposition_002.md` §MAPAS, GEOCODIFICACIÓN Y RASTREO EN VIVO; `integracion_de_mapas_y_geolocalizacion.md`; decisión del usuario

El rastreo GPS **NO comienza con `aceptado=true`**. Comienza cuando el raite está `CONFIRMADO` y pasa a `EN_CURSO` (`en_curso=true`).

| Ítem | Descripción |
|------|-------------|
| Mapa Leaflet | El **mismo mapa** usado para pedir el viaje. Centrado en CU / Ciudad Juárez, tiles OpenStreetMap |
| Punto de inicio | Se muestra el punto real donde se encuentra el viaje (punto de recogida según `tipo`) |
| Punto final | Se muestra el punto de destino (CU para Entrada; punto del catálogo para Salida) |
| Recorrido respecto al inicio | Se muestra referencia visual desde el punto de inicio. **No se muestra un recorrido completo sugerido de inicio a fin** (no hay servicio de sugerencia de rutas) |
| Visibilidad simultánea | Pasajero y conductor ven el mismo mapa simultáneamente con la posición real del conductor |
| Marcador conductor | Posición en tiempo real (conductor emite por HTML5 Geolocation + WebSocket) |
| Botón "Iniciar viaje" | Conductor pulsa para pasar `CONFIRMADO → EN_CURSO`. Exige verificación GPS (conductor a ≤ 300 m del punto de recogida) o solo el pulso si no hay GPS (`sin_gps=true`) |
| Respaldo temporal | Si pasan 15 min (`GRACIA_INICIO_VIAJE`) desde la hora de encuentro sin activación, el sistema activa `en_curso=true` y notifica a ambos |

---

## 8. Notificaciones (Bandeja In-App)

**Ruta:** `/notifications`
**Documentación:** `Raite-Django-API.md` §notifications

| Ítem | Descripción |
|------|-------------|
| Listado paginado | `GET /api/notificaciones/` con `?leida=false` |
| Contador no leídas | Badge `unread` |
| Cada notificación | `tipo`, `titulo`, `mensaje`, `leida`, `raite_id`, `created_at` |
| Tipos | `raite_creado`, `raite_propuesto`, `raite_confirmado`, `raite_rechazado`, `raite_reasignado`, `raite_expirado`, `raite_finalizado`, `raite_en_revision`, `ticket_resuelto`, `ticket_vencido`, `cuenta_suspendida` |
| Marcar leída | `POST /api/notificaciones/{id}/leer/` |
| Marcar todas leídas | `POST /api/notificaciones/leer-todas/` |
| Preferencias de canales | `GET/PATCH /api/notificaciones/preferencias/` (push, in_app, email) |

**WebSocket:** `ws(s)://<host>/ws/notificaciones/?token=<access_token>` para entrega inmediata (no reemplaza a la API REST).

---

## 9. Calificaciones

**Ruta:** dentro de la sección Perfil (menú lateral) y `/ratings/give`
**Documentación:** `Raite-Django-API.md` §ratings; `Raite-Django-Models.md` §Calificacion

| Ítem | Descripción |
|------|-------------|
| Calificaciones recibidas | `GET /api/calificaciones/recibidas/` — historial de quién califica al usuario |
| Dar calificación | `POST /api/raites/{id}/calificar/` con `estrellas` (1–5) y `comentario` opcional |
| Disponibilidad | Solo si `finalizado=true` |
| Restricciones | No autocalificación; una calificación por usuario por raite |

---

## 10. Perfil de Usuario (Menú Lateral Izquierdo)

**Ruta:** `/profile` (layout `MainLayout` con menú lateral fijo)
**Documentación:** `Raite-Django-API.md` §Perfil; `Raite-Django-Models.md` §Usuario; decisión del usuario

**Estructura de la pantalla:**
- **Panel lateral izquierdo (siempre visible):** menú con páginas de perfil. El ítem activo "Perfil" se mantiene resaltado y muestra el título de la sección en la que está el usuario.
- **Contenido central (cambiante):** al seleccionar otra página del menú, solo se reemplaza el contenido central; el panel lateral y el título de sección permanecen visibles.

| Página del menú | Ítem | Descripción |
|-----------------|------|-------------|
| Perfil (vista principal) | Perfil propio | `GET /api/me/` — nombre, apellidos, correo, edad, sexo, carrera, rol, calificación, activo, suspendido, `es_pasajero`, `es_conductor`, `vehiculo_valido`, `puede_solicitar_raite` |
| Editar perfil | Editar perfil | `PATCH /api/me/` — actualiza nombre, carrera, sexo, edad |
| Vehículo | Vehículo propio | `GET /api/me/vehiculo/` y `PATCH /api/me/vehiculo/` (solo conductor) — marca, modelo, color, placas, tipo, asientos disponibles, activo |
| Mis viajes | Historial de raites | `GET /api/raites/` con filtros `pasajero` / `conductor`. Historial de raites pasados (no solicitudes del raite activo actual). |
| Solicitudes recibidas/enviadas | Historial de solicitudes | Historial de solicitudes de raite enviadas y recibidas (no solicitudes del raite activo actual). |
| Calificaciones recibidas | Historial | `GET /api/calificaciones/recibidas/` |
| Dar calificación | Enviar calificación | `POST /api/raites/{id}/calificar/` (solo si `finalizado=true`) |

**Suspensión:** `suspendido=true` bloquea crear y tomar raites; login permitido; solo Admin lo levanta.

Se eliminó el [PENDIENTE] sobre páginas adicionales de perfil.

---

## 11. Panel de Administración (solo ADMIN)

**Ruta:** `/admin/*` (protegido por rol `ADMIN`)
**Documentación:** `Raite_layout_disposition_002.md` §PANEL DE ADMINISTRACIÓN; `Raite-Django-API.md` §Endpoints del panel de administración

| Sección | Funcionalidades / Ítems |
|---------|-------------------------|
| **Usuarios** | Listar todos / filtrar por rol, búsqueda, paginación. Acciones: **Suspender** (`suspendido=true`) y **Levantar suspensión**. Columna `tickets_en_contra` (derivado). |
| **Puntos de Raite** | CRUD del catálogo + filtrar por cadena, zona, `activo`. Alta por sucursal. |
| **Raites Pedidos** | Filtrar por fecha, estado, usuario, punto. |
| **Raites Programados** | Filtrar + `confirmado=true`. |
| **Raites Rechazados** | Filtrar por `rechazado=true` (raites en `CREADO` cuya última propuesta fue rechazada). Ver `RaiteIntento` para quién lo tomó y cuándo. |
| **Tickets vencidos** | `TicketRevision` con SLA de 24 h agotado (`VENCIDO`). |
| **Intentos de Conductor** | Historial `RaiteIntento`: qué conductor tomó cada raite, fechas, `resultado` (`PENDIENTE`/`ACEPTADO`/`RECHAZADO`/`EXPIRADO`). Filtros por conductor, resultado, raite. Cálculo de `cantidad_rechazos`. |
| **Raites en Revisión** | Bandeja de `TicketRevision` (`en_revision=true`). Ver reporte, implicado, motivo. **Resolver** (marcar `RESUELTO` con notas), **Reabrir encuesta**, **Archivar**. Solo ADMIN accede. |
| **Vehículos** | CRUD + filtrar por tipo, capacidad, conductor. Activar/desactivar (`Vehiculo.activo`). |

**Nota:** Los endpoints admin (`/api/admin/...`) exigen `IsAdmin`. Sirven de backing para el panel; no reemplazan al Django Admin.

---

## 12. Pantallas excluidas de la beta 1

Las siguientes no se incluyen porque no están funcionalmente documentadas o el equipo decidió no incluirlas aún:

| Página | Motivo de exclusión |
|--------|---------------------|
| `VerifyEmailPage.vue` | Beta 1 sin verificación de correo (`first_correction_phase2.md` C4) |
| `ForgotPasswordPage.vue` | No documentado funcionalmente |
| `SettingsPage.vue` | No tiene especificación funcional en documentos de layout |
| `ErrorNotFound.vue` (404) | No documentado funcionalmente |

---

## 13. Componentes reutilizables sugeridos (derivados de las pantallas)

- `MapView` (Leaflet, marcadores, popups, clustering)
- `MarkerCluster` (puntos del catálogo / raites activos)
- `RoutePolyline` (referencia visual desde punto de inicio, no ruta sugerida completa)
- `Geocoder` (buscador de puntos en mapa)
- `TripCard` (tarjeta de estado del raite en Home)
- `TripForm` (crear raite: tipo, punto, hora, preferencias, pasajeros)
- `UserAvatar`, `RatingStars` (calificación ★ 1–5)
- `VerificationBadge` (rol, suspendido)
- `AppHeader`, `AppFooter`, `AppDrawer`, `PageContainer` (layout)
- `BottomSheet` (detalle de viaje en móvil, sugerido en Mejoras UI/UX)
- `SkeletonLoader` (mapa y paneles de datos, sugerido)
- `Toast` / `Notify` (actualizaciones de viaje)
- `Modal` (calificación post-viaje, encuesta de finalización, decisión aceptar/rechazar, registro)

---

> Fin del documento. Todos los ítems arriba provienen de `RaiteDocs/` y las decisiones del usuario incorporadas: registro con `q-options` múltiple (Pasajero/Conductor, ambos permitidos), 5 tarjetas del Home con exclusivas de conductor, perfil como menú lateral izquierdo con "Mis viajes" y "Solicitudes recibidas/enviadas" como historial, `q-toggle` de rol activo con ventana de confirmación que recarga el índice de conductor o pasajero (no ambos a la vez), sin verificación de correo en beta 1, GPS en el mismo mapa con punto inicio/final y sin ruta sugerida completa, y exclusión de pantallas no documentadas.
