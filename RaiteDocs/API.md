# API (Capa 2)

Todo vive bajo `/api/`. Autenticación con JWT: `Authorization: Bearer <access>`.
Fuente de verdad: el código en `Back_Raite/apps/*/urls.py`; actualiza esta página si cambia.

"Verificado" = con sesión y `correo_verificado`. Es el permiso por defecto de todo el API; los endpoints públicos lo dicen.

## Respuestas de error

| Código | Cuándo | Forma |
|--------|--------|-------|
| 400 | Datos inválidos (incluye las validaciones `clean()` de los modelos) | `{"campo": ["mensaje"]}` o `{"non_field_errors": [...]}` |
| 401 | Sin token o token vencido | `{"detail": ...}` |
| 403 | Sin el rol o permiso, o correo sin verificar | `{"detail": ...}` (login: `{"detail", "codigo": "correo_no_verificado"}`) |
| 404 | No existe o no le corresponde verlo | `{"detail": ...}` |
| 409 | Conflicto de estado: transición inválida, viaje lleno, cruce de horario, reenvío antes de tiempo | `{"detail": ...}` |

- Los listados vienen paginados de 20 en 20: `{count, next, previous, results}`. Las excepciones se indican en cada endpoint.
- Las fechas van en ISO 8601. Si no traen zona horaria se interpretan como hora de Ciudad Juárez.

## Cuenta — `/api/auth/`

| Método | URL | Quién | Qué hace |
|--------|-----|-------|----------|
| POST | `auth/register/` | Público | Valida los datos (`@alumnos.uacj.mx`, teléfono de 10 dígitos, `carrera` como id de una carrera activa del catálogo) y envía un código de 6 dígitos **sin guardar nada ni apartar el correo**. Responde `token` (firmado, vence a los 15 min), `requiere_vehiculo` y `requiere_verificacion`. 409 si se pidió un código para ese correo hace menos de 60 s. |
| POST | `auth/verificar/` | Público | `{token, codigo}`. Crea la cuenta ya verificada y devuelve `access`, `refresh` y `usuario`. Máximo 5 intentos. Reemplaza una cuenta antigua que se haya quedado sin verificar. 409 si el correo ya está verificado. |
| POST | `auth/reenviar-codigo/` | Público | `{token}`. Manda un código nuevo y devuelve el `token` que reemplaza al anterior. 409 si no han pasado 60 s o el correo ya está verificado. |
| POST | `auth/token/` | Público | Login con `{correo, password}`. Responde 403 `correo_no_verificado` en cuentas antiguas que no completaron la verificación. |
| POST | `auth/token/refresh/`, `auth/token/blacklist/` | Público (con refresh) | Renovar sesión o cerrarla. |
| GET | `auth/me/` | Verificado | Perfil propio, con teléfono y vehículo (placas incluidas). `carrera` es el nombre, `carrera_id` el id y `campus` `{id, codigo, nombre}` (vacíos en administradores). |
| PATCH | `auth/me/` | Verificado | Edita `telefono`, `carrera` (id de una carrera activa del catálogo) y `preferencia_compatibilidad`. |
| PUT | `auth/me/foto/` | Verificado | Sube o cambia la foto de perfil (`multipart/form-data`, campo `foto`). Solo JPG, PNG o WebP de hasta 5 MB (se revisa el contenido, no la extensión). Se endereza según el EXIF, se le quitan los metadatos, se reduce a 512 px y se guarda como WebP; la anterior se borra. Responde el perfil propio. |
| DELETE | `auth/me/foto/` | Verificado | Quita la foto y borra el archivo. Responde el perfil propio. |
| POST | `auth/vehicle/` | Verificado (no admin) | Registra el vehículo (uno por usuario; 409 si ya tiene). Si el usuario era `PASAJERO`, su rol pasa a `AMBOS`. Responde `rol` y `rol_display`. |
| GET / PATCH | `auth/vehicle/` | Verificado | Ver o editar marca, modelo, color y asientos (1–5; no menos que los lugares de un viaje vigente). 404 si no tiene vehículo. |

**Foto de perfil.** `foto` viene en el perfil propio y en todos los usuarios que aparecen en viajes, solicitudes, calificaciones y reportes (`null` si no hay). Con R2 es una URL firmada que vence en una hora (el bucket es privado); sin R2, una ruta `/media/...` relativa al API. Solo la reciben usuarios con sesión.

## Catálogos

| Método | URL | Quién | Qué hace |
|--------|-----|-------|----------|
| GET | `campus/` | Público | Campus activos (sin paginar). Público porque el registro lo usa para elegir la carrera. |
| GET | `carreras/` | Público | Carreras activas de campus activos (sin paginar): `{id, campus, nombre, area}`. `?campus=<id>` filtra. |
| GET | `puntos/` | Verificado | Puntos de referencia activos (sin paginar). `?q=` busca por nombre. `?lat=&lon=` ordena por cercanía y agrega `distancia_km`. |

## Viajes

| Método | URL | Quién | Qué hace |
|--------|-----|-------|----------|
| GET | `viajes/` | Verificado | **Búsqueda.** Acepta `punto` o `lat`+`lon`, `radio_km` (3 por defecto, máximo 15), `campus`, `sentido`, `desde` y `hasta`. Devuelve viajes `PUBLICADO` a futuro, con lugar libre, que no son propios y son compatibles por sexo. Ordena por distancia y luego por hora. |
| POST | `viajes/` | Conductor con vehículo activo, no suspendido | Publica un viaje: `punto_referencia`, `campus`, `sentido`, `fecha_hora`, `lugares_ofrecidos`, `preferencia_compatibilidad` (opcional) y `notas`. 409 si se cruza de horario con otro viaje o solicitud propios. |
| GET | `viajes/mios/` | Conductor | Sus viajes. Por defecto `PUBLICADO` y `EN_CURSO`, vencidos incluidos (`esta_vencido`). `?estado=` filtra. Cada viaje trae `solicitudes_pendientes`. |
| GET | `viajes/{id}/` | Verificado | Detalle. Si el viaje está publicado lo ve cualquiera; si no, solo el conductor y quien tuvo una solicitud. Incluye `mi_solicitud` y, para el conductor, `pasajeros_confirmados`. |
| PATCH | `viajes/{id}/` | Conductor del viaje | Edita `fecha_hora`, `lugares_ofrecidos`, `notas` y `preferencia_compatibilidad`, solo si está publicado y no vencido. Avisa a las solicitudes activas. |
| POST | `viajes/{id}/cancelar/` | Conductor del viaje | `PUBLICADO → CANCELADO`, también si está vencido. Cancela las solicitudes activas y avisa a sus pasajeros. |
| POST | `viajes/{id}/iniciar/` | Conductor del viaje | `PUBLICADO → EN_CURSO`, desde 30 min antes de la hora y si no está vencido. Las pendientes pasan a rechazadas. |
| POST | `viajes/{id}/finalizar/` | Conductor del viaje | `EN_CURSO → FINALIZADO`. Avisa a los pasajeros aceptados para que califiquen. |

**Viaje vencido:** un viaje `PUBLICADO` cuya hora pasó hace más de 2 h. No es un estado guardado: se calcula con la fecha. Un viaje vencido:
- no aparece en búsquedas ni cuenta para los cruces de horario;
- no se puede iniciar, editar ni recibir solicitudes;
- solo se puede cancelar.

## Solicitudes

| Método | URL | Quién | Qué hace |
|--------|-----|-------|----------|
| POST | `viajes/{id}/solicitudes/` | Pasajero no suspendido | Pide un lugar. Responde 400 si es incompatible por sexo; 409 si el viaje está lleno o cerrado, si ya tiene una solicitud activa o si hay cruce de horario. |
| GET | `viajes/{id}/solicitudes/` | Conductor del viaje | Solicitudes del viaje; el teléfono del pasajero aparece solo en las aceptadas. |
| GET | `solicitudes/mias/` | Pasajero | Sus solicitudes con el resumen del viaje. `?estado=` filtra. |
| POST | `solicitudes/{id}/aceptar/` | Conductor del viaje | `PENDIENTE → ACEPTADA`, con la fila del viaje bloqueada para que dos aceptaciones simultáneas no rebasen el cupo. 409 si ya no hay lugar o si dejó de ser compatible. |
| POST | `solicitudes/{id}/rechazar/` | Conductor del viaje | `PENDIENTE → RECHAZADA`. |
| POST | `solicitudes/{id}/cancelar/` | Pasajero de la solicitud | `PENDIENTE`/`ACEPTADA → CANCELADA`, mientras el viaje no haya salido. |

**Contacto:** el teléfono del conductor y las placas solo aparecen para el pasajero con solicitud `ACEPTADA`. El conductor ve el teléfono de sus pasajeros aceptados.

## Historial, notificaciones, calificaciones y reportes

| Método | URL | Quién | Qué hace |
|--------|-----|-------|----------|
| GET | `historial/` | Verificado | Viajes finalizados o cancelados en los que participó, con `mi_papel`. `?rol=conductor` o `?rol=pasajero` filtra. |
| GET | `notificaciones/` | Verificado | Las propias, de la más nueva a la más vieja. `?no_leidas=1` filtra. |
| GET | `notificaciones/conteo/` | Verificado | `{no_leidas}`, para la consulta periódica del frontend. |
| POST | `notificaciones/{id}/leer/` | Dueño | Marca una como leída. |
| POST | `notificaciones/leer-todas/` | Verificado | Marca todas como leídas. Responde `{marcadas}`. |
| POST | `viajes/{id}/calificaciones/` | Participante | `{calificado, puntuacion (1–5), comentario}`. Solo en viajes finalizados, entre el conductor y un pasajero aceptado, una vez. Recalcula `Usuario.calificacion`. |
| GET | `calificaciones/pendientes/` | Verificado | A quién le falta calificar (sin paginar). |
| POST | `reportes/` | Participante | `{viaje, reportado, motivo}`. 409 si ya tiene un reporte pendiente contra esa persona en ese viaje. |
| GET | `reportes/mios/` | Verificado | Reportes que hizo y su estado. |

Los reportes se resuelven en el admin de Django (`/admin/`): marcar resuelto, descartar o suspender al reportado.

## Notificaciones que se crean

| Evento | Tipo | Destinatario |
|--------|------|--------------|
| Solicitud nueva | `SOLICITUD_NUEVA` | Conductor |
| Aceptada / rechazada | `SOLICITUD_ACEPTADA` / `SOLICITUD_RECHAZADA` | Pasajero |
| Viaje iniciado con solicitudes pendientes | `SOLICITUD_RECHAZADA` | Pasajeros pendientes |
| Pasajero cancela | `SOLICITUD_CANCELADA` | Conductor |
| Viaje editado | `VIAJE_MODIFICADO` | Pasajeros con solicitud activa |
| Viaje cancelado | `VIAJE_CANCELADO` | Pasajeros con solicitud activa |
| Viaje finalizado | `VIAJE_FINALIZADO` | Pasajeros aceptados |
