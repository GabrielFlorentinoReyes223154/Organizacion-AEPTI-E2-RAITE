# Raite — API REST y Tiempo Real

> Contrato HTTP de `Back_Raite` (Django 6.1 + DRF 3.18 + SimpleJWT 5.5).
> Derivado de `Raite_layout_disposition_001.md` (Diagrama de Secuencia) y `Raite-Django-Models.md`.
> Prefijo global: `/api`. Autenticación: `Bearer <access_token>`.

---

## 1. Convenciones

| Aspecto | Decisión |
|---------|----------|
| Autenticación | JWT (SimpleJWT). `POST /api/auth/token/` y `POST /api/auth/token/refresh/` |
| Refresh rotation | `ROTATE_REFRESH_TOKENS = True` + `BLACKLIST_AFTER_ROTATION = True` |
| Login | Correo (`EmailBackend` + `CustomTokenObtainPairSerializer`) |
| Errores | `{"detail": "...", "code": "RAITE_CONFLICT"}` cuando aplica |
| Filtros | `django-filter` en listados con estado y tipo |
| Paginación | `PageNumberPagination`, `page_size=20`, `max_page_size=100` |
| Fechas | ISO 8601 UTC, `2026-09-30T14:00:00Z` |
| Códigos usados | 200, 201, 204, 400, 401, 403, 404, **409** (conflicto de estado), 422 |

> **409 es la respuesta clave del dominio.** Casi todos los conflictos de negocio
> (usuario ya tiene raite en curso, raite ya aceptado, vehículo inválido) son 409, no 400.
> El frontend lo usa para distinguir "reintentar" de "mostrar error al usuario".

---

## 2. `core` — Salud y raíz

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| `GET` | `/api/health/` | No | Liveness probe. `200 {"status": "ok", "version": "0.1.0"}` |
| `GET` | `/api/` | Sí | Índice de recursos disponibles |

```json
// GET /api/health/  →  200
{ "status": "ok", "version": "0.1.0", "time": "2026-09-30T14:00:00Z" }
```

---

## 3. `accounts` — Autenticación y perfil

### 3.1 Registro en 2 pasos

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| `POST` | `/api/auth/register/` | No | Paso 1: crea usuario y rol |
| `POST` | `/api/auth/vehicle/` | Sí | Paso 2 (condicional): crea vehículo |
| `POST` | `/api/auth/token/` | No | Login por correo |
| `POST` | `/api/auth/token/refresh/` | No | Renueva access token |
| `POST` | `/api/auth/token/blacklist/` | Sí | Logout (revoca el refresh) |

```json
// POST /api/auth/register/
{
  "nombre": "Ana",
  "apellidos": "López",
  "correo": "ana@uacj.mx",
  "password": "••••••••",
  "edad": 20,
  "sexo": "F",
  "carrera": "Ingeniería en Sistemas",
  "rol": "AMBOS"
}

// 201 Created
{ "id": "…", "rol": "AMBOS", "verificado": false, "requiere_vehiculo": true }
```

Reglas: si `rol ∈ {CONDUCTOR, AMBOS}` la respuesta incluye `requiere_vehiculo: true` y el
frontend encadena `POST /api/auth/vehicle/` antes de habilitar "Dar Raite".

```json
// POST /api/auth/vehicle/   (solo si es conductor)
{
  "marca": "Nissan",
  "modelo": "Tsuru",
  "color": "Blanco",
  "placas": "ABC123D",
  "tipo": "COCHE",
  "asientos_disponibles": 3
}

// 201 Created
{ "id": "…", "placas": "ABC123D", "vehiculo_valido": true }
```

> `POST /api/auth/vehicle/` responde **403** si el usuario no tiene rol de conductor.

### 3.2 Perfil

| Método | Ruta | Auth | Permiso | Descripción |
|--------|------|------|---------|-------------|
| `GET` | `/api/me/` | Sí | `IsAuthenticated` | Perfil propio + flags de UI |
| `PATCH` | `/api/me/` | Sí | `IsAuthenticated` | Actualiza nombre, carrera, sexo, edad |
| `GET` | `/api/me/vehiculo/` | Sí | `IsDriver` | Vehículo propio (placas visibles aquí) |
| `PATCH` | `/api/me/vehiculo/` | Sí | `IsDriver` | Actualiza vehículo |
| `GET` | `/api/me/raite-activo/` | Sí | `IsAuthenticated` | Raite en curso, o `null` |

```json
// GET /api/me/
{
  "id": "…",
  "nombre": "Ana",
  "apellidos": "López",
  "nombre_completo": "Ana López",
  "correo": "ana@uacj.mx",
  "edad": 20,
  "sexo": "F",
  "carrera": "Ingeniería en Sistemas",
  "rol": "AMBOS",
  "calificacion": 4.6,
  "activo": true,
  "verificado": false,
  "es_pasajero": true,
  "es_conductor": true,
  "vehiculo_valido": true,
  "puede_solicitar_raite": false
}
```

`GET /api/me/raite-activo/` es el endpoint que el Home consulta para decidir cuál de los
cuatro estados mostrar: `null`, `solicitado`, `aceptado_por_otro`, `programado`.

---

## 4. `vehicles`

| Método | Ruta | Auth | Permiso | Descripción |
|--------|------|------|---------|-------------|
| `GET` | `/api/vehicles/` | Sí | `IsAdmin` | Listado con filtros `?tipo=COCHE&capacidad_min=4` |
| `POST` | `/api/vehicles/` | Sí | `IsAdmin` | Alta administrativa |
| `GET` | `/api/vehicles/{id}/` | Sí | `IsAdmin` o dueño | Detalle |
| `PATCH` | `/api/vehicles/{id}/` | Sí | `IsAdmin` o dueño | Actualizar |
| `DELETE` | `/api/vehicles/{id}/` | Sí | `IsAdmin` | Baja lógica (`activo=False`) |

**Visibilidad de placas.** El campo `placas` solo se serializa cuando se cumple una de:

1. El solicitante es el conductor dueño del vehículo.
2. El solicitante es el pasajero de un raite con `aceptado=True` de ese conductor.
3. El solicitante es admin.

En cualquier otro caso DRF omite el campo del payload (no lo manda en `null`).
Implementación: un `VehiculoSerializer` con `SerializerMethodField` sobre
`self.context["request"].user` y un selector `vehiculo_visible_para(conductor,(user)`.

---

## 5. `locations`

| Método | Ruta | Auth | Permiso | Descripción |
|--------|------|------|---------|-------------|
| `GET` | `/api/puntos/` | Sí | `IsAuthenticated` | Puntos activos del campus, opcional `?zona=` |
| `GET` | `/api/puntos/{id}/` | Sí | `IsAuthenticated` | Detalle + conductores cercanos |
| `GET` | `/api/campus/` | Sí | `IsAuthenticated` | Lista campus; incluye el `predeterminado` (CU) |
| `GET` | `/api/puntos/{id}/demanda/` | Sí | `IsAuthenticated` | Raites activos en ese punto |
| `POST` `PATCH` `DELETE` | `/api/puntos/…` | Sí | `IsAdmin` | CRUD de puntos |

```json
// GET /api/puntos/
{
  "count": 24,
  "results": [
    { "id": "…", "nombre_punto": "Plaza Benito Juárez",
      "latitud": 31.690142, "longitud": -106.084520, "zona": "Centro" }
  ]
}
```

```json
// GET /api/puntos/{id}/demanda/   →  raites activos por tipo de viaje
{
  "punto_id": "…",
  "entrada": 3,
  "salida": 1,
  "conductores_cercanos": 5,
  "eta_minutos": 6
}
```

> El mapa de "Dar Raite" consume `demanda/`; el de "Pedir Raite" consume `puntos/`.
> El frontend no calcula ciencia de datos: el backend ya devuelve conteos.

---

## 6. `rides` — Endpoints

| Método | Ruta | Auth | Permiso | Descripción |
|--------|------|------|---------|-------------|
| `GET` | `/api/raites/` | Sí | `IsAuthenticated` | Filtros: `?activo&aceptado&tipo&conductor&pasajero` |
| `POST` | `/api/raites/` | Sí | `IsPassenger` | Crear raite |
| `GET` | `/api/raites/{id}/` | Sí | `IsRaiteParticipant` | Detalle |
| `DELETE` | `/api/raites/{id}/` | Sí | `IsRaiteParticipant` + es pasajero | Cancelar |
| `GET` | `/api/raites/disponibles/` | Sí | `IsDriver` | Raites activos sin aceptar |
| `POST` | `/api/raites/{id}/aceptar/` | Sí | `IsDriver` | Aceptar (transaccional) |
| `POST` | `/api/raites/{id}/rechazar/` | Sí | `IsDriver` | Ocultar de la lista del conductor |
| `POST` | `/api/raites/{id}/finalizar/` | Sí | `IsRaiteParticipant` | Ambos `sí` → finalizado |

### 6.1 Crear raite

```json
// POST /api/raites/
{
  "tipo": "ENTRADA",
  "punto_origen": "uuid-del-punto",
  "hora_objetivo": "07:00",
  "configuracion": {
    "mismo_sexo": true,
    "usar_cajuela": false,
    "mascotas": false
  }
}

// 201 Created
{
  "id": "…",
  "tipo": "ENTRADA",
  "punto_origen": { "id": "…", "nombre_punto": "Plaza Benito Juárez",
                    "latitud": 31.690142, "longitud": -106.084520 },
  "punto_destino": { "id": "…", "nombre_punto": "CU" },
  "hora_objetivo": "07:00",
  "configuracion": { … },
  "activo": true, "aceptado": false, "finalizado": false,
  "created_at": "2026-09-30T05:00:00Z"
}
```

El cliente **no** envía `punto_destino` en `ENTRADA` ni `punto_origen` en `SALIDA`.
El backend lo fuerza al `Campus` predeterminado y descarta el campo si viene.

Respuestas de error:

| Código | Situación |
|--------|-----------|
| `409` | El pasajero ya tiene `activo=true` |
| `400` | `hora_objetivo` fuera de 07:00–22:00, o no es hora entera |
| `400` | `punto_origen` inactivo |
| `400` | En `ENTRADA`, `punto_destino` enviado y distinto de CU |

### 6.2 Aceptar raite

```json
// POST /api/raites/{id}/aceptar/  (body vacío; el conductor es el del token)
{}

// 200 OK
{ "id": "…", "conductor": { "id": "…", "nombre_completo": "Luis Pérez",
                           "edad": 22, "sexo": "M",
                           "carrera": "Ingeniería Eléctrica", "calificacion": 4.8 },
  "vehiculo": { "tipo": "COCHE", "color": "Blanco",
                "placas": "ABC123D", "asientos_disponibles": 3 },
  "activo": true, "aceptado": true, "finalizado": false }
```

Aquí sí aparecen las placas: la aceptación es lo que habilita esa visibilidad.

| Código | Situación |
|--------|-----------|
| `409` | Raite ya aceptado por otro conductor |
| `409` | Raite expirado (`hora_objetivo` ya pasó) |
| `409` | Conductor ya tiene `activo=true` |
| `409` | Conductor sin `vehiculo_valido` |
| `403` | Usuario sin rol de conductor |

### 6.3 Consultar raites disponibles (mapa de "Dar Raite")

```
GET /api/raites/disponibles/?tipo=ENTRADA&punto=<id>&radio_km=3
```

```json
{
  "count": 1,
  "results": [
    { "id": "…", "tipo": "ENTRADA",
      "punto_origen": { "id": "…", "nombre_punto": "Plaza Benito Juárez" },
      "punto_destino": { "id": "…", "nombre_punto": "CU" },
      "hora_objetivo": "07:00",
      "pasajero": { "nombre": "Ana", "edad": 20, "sexo": "F",
                    "carrera": "Ingeniería en Sistemas", "calificacion": 4.6 },
      "distancia_km": 1.8 }
  ]
}
```

El serializer de este listado **omite placas y correo** del conductor (el conductor aún no
fue aceptado, así que no puede ver al pasajero completo). Solo ve lo necesario para decidir.

### 6.4 Detalle del raite (datos de las tarjetas del Home)

`GET /api/raites/{id}/` devuelve según el rol del solicitante:

**Conductor viendo un raite aceptado** — ve al pasajero, incluido su vehículo de referencia
si aplica, y la configuración del viaje.

**Pasajero viendo un raite aceptado** — ve al conductor con placas.

El serializer decide con `instance.pasajero_id == request.user.id`.

---

## 7. `surveys`

| Método | Ruta | Auth | Permiso | Descripción |
|--------|------|------|---------|-------------|
| `GET` | `/api/encuestas/pendientes/` | Sí | `IsAuthenticated` | Encuesta abierta del usuario |
| `POST` | `/api/encuestas/{id}/responder/` | Sí | `IsRaiteParticipant` | Responde `true` / `false` |
| `GET` | `/api/raites/{id}/encuestas/` | Sí | `IsRaiteParticipant` | Estado de ambas encuestas |

```json
// GET /api/encuestas/pendientes/
{
  "id": "…",
  "raite_id": "…",
  "pregunta": "¿Llegaste bien a tu destino?",
  "reintentos": 0,
  "respondio": false
}

// POST /api/encuestas/{id}/responder/
{ "respondio": true, "offline_retry": false }

// 200 OK  —  todavía falta la contraparte
{ "raite_finalizado": false, "respondidas": 1, "requeridas": 2 }

// 200 OK  —  completada
{ "raite_finalizado": true, "respondidas": 2, "requeridas": 2 }
```

`respondio: false` no cancela el viaje: la encuesta es persistente e insiste. El raite
permanece bloqueado hasta que ambos respondan `true`. El frontend guarda el `id` de la
encuesta en localStorage y reintenta al reconectar (`offline_retry: true`).

---

## 8. `ratings`

| Método | Ruta | Auth | Permiso | Descripción |
|--------|------|------|---------|-------------|
| `GET` | `/api/calificaciones/recibidas/` | Sí | `IsAuthenticated` | Historial de quien califica al usuario |
| `POST` | `/api/raites/{id}/calificar/` | Sí | `IsRaiteParticipant` | Enviar `1–5` |

```json
// POST /api/raites/{id}/calificar/
{ "estrellas": 5, "comentario": "Muy puntual" }

// 201 Created
{ "id": "…", "estrellas": 5, "comentario": "Muy puntual",
  "para_usuario": "…", "created_at": "2026-09-30T14:05:00Z" }
```

| Código | Situación |
|--------|-----------|
| `409` | El raite no está `finalizado` |
| `409` | El usuario ya calificación este raite |
| `400` | `estrellas` fuera de 1–5 |

---

## 9. `notifications`

| Método | Ruta | Auth | Permiso | Descripción |
|--------|------|------|---------|-------------|
| `GET` | `/api/notificaciones/` | Sí | `IsAuthenticated` | Bandeja, paginada, `?leida=false` |
| `POST` | `/api/notificaciones/{id}/leer/` | Sí | dueño | Marcar una leída |
| `POST` | `/api/notificaciones/leer-todas/` | Sí | `IsAuthenticated` | Marcar todas |
| `GET` `PATCH` | `/api/notificaciones/preferencias/` | Sí | `IsAuthenticated` | Canales: push, in_app, email |

```json
// GET /api/notificaciones/
{
  "count": 3,
  "unread": 2,
  "results": [
    { "id": "…", "tipo": "raite_aceptado", "titulo": "¡Han aceptado tu raite!",
      "mensaje": "Luis Pérez te llevará a CU.", "leida": false,
      "raite_id": "…", "created_at": "2026-09-30T05:12:00Z" }
  ]
}
```

Tipos: `raite_creado`, `raite_aceptado`, `raite_expirado`, `raite_finalizado`,
`encuesta_pendiente`, `calificacion_recibida`.

---

## 10. `realtime` — WebSocket

### 10.1 Canal

```
ws(s)://<host>/ws/notificaciones/?token=<access_token>
```

Autenticación por `token` en query string porque el navegador no puede mandar headers
en el handshake de WebSocket. Un middleware de `AuthMiddlewareStack` valida el JWT.

### 10.2 Group por usuario

Cada conexión entra al grupo `user_{usuario_id}`. Los eventos se publican con
`channel_layer.group_send()`.

### 10.3 Eventos

| Evento | `type` | Destinatario | Payload |
|--------|--------|--------------|---------|
| Raite creado | `raite_creado` | Conductores con `vehiculo_valido` en radio | `{raite_id, tipo, punto, hora_objetivo, distancia_km}` |
| Raite aceptado | `raite_aceptado` | Pasajero | `{raite_id, conductor: {nombre_completo, calificacion}, vehiculo: {tipo, color, placas}}` |
| Raite expirado | `raite_expirado` | Pasajero | `{raite_id, motivo: "hora_objetivo"}` |
| Raite cancelado | `raite_cancelado` | Conductor | `{raite_id}` |
| Encuesta abierta | `encuesta_pendiente` | Ambos | `{raite_id, encuesta_id, pregunta}` |
| Raite finalizado | `raite_finalizado` | Ambos | `{raite_id, habilita_calificacion: true}` |

Ejemplo de mensaje al cliente:

```json
{
  "type": "raite_aceptado",
  "data": {
    "raite_id": "9f2c…",
    "conductor": { "id": "…", "nombre_completo": "Luis Pérez", "calificacion": 4.8 },
    "vehiculo": { "tipo": "COCHE", "color": "Blanco", "placas": "ABC123D" }
  }
}
```

> Los eventos WS **no reemplazan** a la API REST. Ambos caminos crean la
> `Notificacion` en BD. El WS es la entrega inmediata; el REST es la fuente de verdad
> para recargar. Si el WS cae, el usuario sigue viendo todo en `/api/notificaciones/`.

---

## 11. Permisos

Todos en `apps/*/permissions.py`, salvo los genéricos en `core`.

| Clase | Ubicación | Regla |
|-------|-----------|-------|
| `IsAdmin` | `core` | `request.user.is_staff` |
| `IsPassenger` | `accounts` | `usuario.es_pasajero` |
| `IsDriver` | `accounts` | `usuario.es_conductor` |
| `IsOwner` | `core` | `obj.usuario_id == request.user.id` |
| `IsRaiteParticipant` | `rides` | `user.id in {raite.pasajero_id, raite.conductor_id}` |
| `IsRaitePassenger` | `rides` | `raite.pasajero_id == user.id` |
| `IsRaiteDriver` | `rides` | `raite.conductor_id == user.id` |
| `ReadOnly` | `core` | `SAFE_METHODS` |

**Rutas protegidas por rol.** Un usuario con rol `PASAJERO` que llame a un endpoint de
conductor recibe `403`, no `404`. La pantalla de Login/Registro deriva la navegación
inicial de `GET /api/me/` → `es_pasajero`, `es_conductor`, `activo`.

---

## 12. Endpoints del panel de administración

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/admin/usuarios/` | Listar / filtrar por rol, búsqueda, paginación |
| `GET` | `/api/admin/raites-pedidos/` | Filtros: fecha, estado, usuario, punto |
| `GET` | `/api/admin/raites-programados/` | Igual + solo `confirmados` |
| `GET` | `/api/admin/puntos/` | CRUD de puntos, filtros por zona y demanda |
| `GET` | `/api/admin/vehiculos/` | CRUD, filtros por tipo y capacidad |
| `GET` | `/api/admin/estadisticas/` | Raites por día, tasa de aceptación, cancelaciones |

Todos exigen `IsAdmin`. Sirven de backing para el Django Admin, no lo reemplazan.

---

## 13. Superficie de eventos y tareas periódicas

| Disparador | Acción | Responsable |
|------------|--------|-------------|
| `Raite` creado | Notificación a conductores cercanos + WS | Señal `post_save` en `rides` |
| `Raite` aceptado | Notificación al pasajero + WS | Señal `post_save` en `rides` |
| Cron cada 5 min | Expirar raites `activo & !aceptado` con `hora_objetivo` pasada | `core.tasks` → `rides.services.expirar_vencidos()` |
| Cron cada 15 min | Reenviar `encuesta_pendiente` a pendientes | `surveys.tasks` |
| Cron diario | Reconciliar `Usuario.activo` contra raites abiertos | `core.tasks` |
| `Calificacion` insertada | Recalcular `Usuario.calificacion` | Señal `post_save` en `ratings` |
| Raite finalizado | Habilitar calificación | Señal `post_save` en `rides` |

> **Reconciliación de `activo`.** `Usuario.activo` es un bool desnormalizado. El cron
> diario pone `activo=True` solo si el usuario tiene un raite con
> `(activo=True, finalizado=False)`. Sin esto, un crash a mitad de una transacción deja
> usuarios bloqueados permanentemente.

---

## 14. Pendientes técnicos

- [ ] **Rate limiting** en `POST /api/auth/token/` y `POST /api/raites/` (evitar abuso).
- [ ] **Idempotencia** en `aceptar/` con clave `Idempotency-Key` para reintentos del móvil.
- [ ] **Paginación por cursor** en `notificaciones/` cuando el volumen crezca.
- [ ] **OpenAPI** con `drf-spectacular` para generar el cliente del frontend.
- [ ] **Versionado** `/api/v1/` antes de que el móvil 1.0 quede en stores.
