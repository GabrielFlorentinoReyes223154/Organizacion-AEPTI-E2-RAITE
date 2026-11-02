# Organización del frontend Quasar/Vue y plan de trabajo

## Contexto

Este documento consolida la propuesta derivada de `RaiteDocs/Design/UI_UX.md` para organizar el frontend de Raite con Quasar 2.x, Vue 3, Vite, Pinia, Vue Router, Leaflet/OpenStreetMap, Geolocation API y PWA/Workbox planificado.

La aplicación contempla los roles `PASAJERO` y `CONDUCTOR`. Un usuario puede tener ambos roles. El panel administrativo está protegido para `ADMIN`.

## Conteo propuesto de archivos `.vue`

- **24 páginas o componentes únicos de pantalla** para la beta.
- **17 componentes reutilizables base** sugeridos explícitamente.
- **5 componentes compartidos de interacción** agregados para completar los flujos: `Toast`, `ConfirmModal`, `TripDecisionModal`, `RatingModal` y `VehicleForm`.
- **46 archivos `.vue` propuestos en total:** 24 únicos + 22 reutilizables.
- El documento original menciona además 4 pantallas excluidas de beta: `VerifyEmailPage.vue`, `ForgotPasswordPage.vue`, `SettingsPage.vue` y `ErrorNotFound.vue`. Si se incluyen, el total sería **50 archivos**.

Los nombres son una propuesta descriptiva; deben ajustarse a las convenciones definitivas del proyecto antes de implementar rutas.

## Componentes únicos de pantalla

### Autenticación

1. `LoginPage.vue` — Permite iniciar sesión con correo y contraseña mediante JWT.
2. `RegisterPage.vue` — Registra al usuario y permite seleccionar el rol de pasajero, conductor o ambos.
3. `RegisterVehiclePage.vue` — Captura marca, modelo, color, placas, tipo y asientos del vehículo del conductor.

### Inicio y viajes

4. `HomePage.vue` — Muestra el estado actual del raite y permite cambiar el rol activo.
5. `CreateTripPage.vue` — Permite al pasajero seleccionar un punto, hora, tipo de viaje, preferencias y pasajeros requeridos para crear un raite.
6. `DriverTripsPage.vue` — Muestra en el mapa los raites activos disponibles para que un conductor tome uno.
7. `TripProposalPage.vue` — Muestra la propuesta del conductor para que el pasajero la acepte o rechace.
8. `LiveTripPage.vue` — Muestra el seguimiento GPS del viaje confirmado y en curso.

### Notificaciones y calificaciones

9. `NotificationsPage.vue` — Muestra la bandeja paginada, contador de no leídas y preferencias de notificación.
10. `GiveRatingPage.vue` — Permite calificar al otro usuario después de finalizar un viaje.
11. `ReceivedRatingsPage.vue` — Muestra el historial de calificaciones recibidas.

### Perfil del usuario

12. `ProfilePage.vue` — Presenta los datos principales, roles, estado y permisos del usuario.
13. `EditProfilePage.vue` — Permite editar nombre, carrera, sexo y edad.
14. `VehicleProfilePage.vue` — Consulta y edita los datos del vehículo propio.
15. `MyTripsPage.vue` — Muestra el historial de raites realizados como pasajero o conductor.
16. `TripRequestsPage.vue` — Muestra el historial de solicitudes enviadas y recibidas.

### Administración

17. `AdminDashboardPage.vue` — Presenta un resumen general de la operación administrativa.
18. `AdminUsersPage.vue` — Lista, busca, suspende y reactiva usuarios.
19. `AdminPickupPointsPage.vue` — Administra el catálogo de puntos y sucursales.
20. `AdminTripsPage.vue` — Consulta raites pedidos, programados y rechazados con filtros.
21. `AdminTicketsPage.vue` — Administra tickets vencidos y su SLA.
22. `AdminDriverAttemptsPage.vue` — Muestra los intentos de conductores y sus resultados.
23. `AdminReviewsPage.vue` — Revisa, resuelve, reabre o archiva reportes.
24. `AdminVehiclesPage.vue` — Administra vehículos y su activación o desactivación.

## Componentes reutilizables base

1. `MapView.vue` — Mapa base de Leaflet/OpenStreetMap con centro, zoom y eventos.
2. `MarkerCluster.vue` — Agrupa marcadores cercanos para mejorar la lectura del mapa.
3. `MapMarker.vue` — Representa un punto de catálogo, raite activo o posición del conductor.
4. `RoutePolyline.vue` — Dibuja la referencia visual desde el inicio del viaje.
5. `Geocoder.vue` — Busca puntos o ubicaciones dentro del mapa.
6. `TripCard.vue` — Presenta el estado, participantes, horario y acciones de un raite.
7. `TripForm.vue` — Formulario para crear o editar un raite.
8. `TripFilters.vue` — Filtros reutilizables por tipo, estado, hora, usuario y punto.
9. `UserAvatar.vue` — Muestra el avatar o identificación visual de un usuario.
10. `RatingStars.vue` — Visualiza o permite seleccionar una calificación de una a cinco estrellas.
11. `VerificationBadge.vue` — Muestra indicadores de rol, suspensión o verificación.
12. `AppHeader.vue` — Encabezado global de la aplicación.
13. `AppFooter.vue` — Pie de página global.
14. `AppDrawer.vue` — Menú lateral global y navegación del perfil o administración.
15. `PageContainer.vue` — Estructura y espaciado común de las páginas.
16. `BottomSheet.vue` — Panel inferior para detalles en dispositivos móviles.
17. `SkeletonLoader.vue` — Indicadores de carga para mapas, tarjetas y paneles.

## Componentes reutilizables de interacción

18. `Toast.vue` — Mensajes breves de éxito, advertencia o error; puede delegar en `Notify` de Quasar.
19. `ConfirmModal.vue` — Confirma acciones como cambiar de rol, cancelar o realizar operaciones sensibles.
20. `TripDecisionModal.vue` — Permite aceptar o rechazar una propuesta de raite.
21. `RatingModal.vue` — Captura estrellas y comentario para una calificación.
22. `VehicleForm.vue` — Formulario reutilizable para registrar o editar un vehículo.

## Pantallas excluidas de la beta 1

Estas pantallas aparecen en la documentación como excluidas por falta de alcance funcional o por decisiones del producto:

- `VerifyEmailPage.vue` — No hay verificación de correo en beta 1.
- `ForgotPasswordPage.vue` — No está documentada funcionalmente.
- `SettingsPage.vue` — No tiene especificación funcional de layout.
- `ErrorNotFound.vue` — No está documentada funcionalmente.

## Distribución para cinco personas

La distribución evita mezclar páginas únicas con componentes reutilizables dentro de una misma persona y reduce la cantidad de archivos compartidos que pueden generar bloqueos.

### Persona 1 — Autenticación y perfil

**Tipo de trabajo:** solo archivos únicos.

- `LoginPage.vue`
- `RegisterPage.vue`
- `RegisterVehiclePage.vue`
- `ProfilePage.vue`
- `EditProfilePage.vue`
- `VehicleProfilePage.vue`
- `MyTripsPage.vue`
- `TripRequestsPage.vue`
- `ReceivedRatingsPage.vue`

### Persona 2 — Flujo principal de viajes

**Tipo de trabajo:** solo archivos únicos.

- `HomePage.vue`
- `CreateTripPage.vue`
- `DriverTripsPage.vue`
- `TripProposalPage.vue`
- `LiveTripPage.vue`
- `NotificationsPage.vue`
- `GiveRatingPage.vue`

### Persona 3 — Administración

**Tipo de trabajo:** solo archivos únicos.

- `AdminDashboardPage.vue`
- `AdminUsersPage.vue`
- `AdminPickupPointsPage.vue`
- `AdminTripsPage.vue`
- `AdminTicketsPage.vue`
- `AdminDriverAttemptsPage.vue`
- `AdminReviewsPage.vue`
- `AdminVehiclesPage.vue`

### Persona 4 — Layout y componentes visuales

**Tipo de trabajo:** solo archivos reutilizables.

- `AppHeader.vue`
- `AppFooter.vue`
- `AppDrawer.vue`
- `PageContainer.vue`
- `BottomSheet.vue`
- `SkeletonLoader.vue`
- `UserAvatar.vue`
- `RatingStars.vue`
- `VerificationBadge.vue`
- `Toast.vue`
- `ConfirmModal.vue`

Debe implementar primero `PageContainer.vue`, `AppHeader.vue`, `AppDrawer.vue` y `ConfirmModal.vue`.

### Persona 5 — Mapas, formularios y viajes

**Tipo de trabajo:** solo archivos reutilizables.

- `MapView.vue`
- `MarkerCluster.vue`
- `MapMarker.vue`
- `RoutePolyline.vue`
- `Geocoder.vue`
- `TripCard.vue`
- `TripForm.vue`
- `TripFilters.vue`
- `TripDecisionModal.vue`
- `RatingModal.vue`
- `VehicleForm.vue`

Debe implementar primero `MapView.vue`, `TripCard.vue`, `TripForm.vue` y `VehicleForm.vue`.

## Reglas para minimizar bloqueos

1. Al inicio, definir conjuntamente nombres de rutas, interfaces TypeScript, props, eventos, estados de carga y contratos de datos mock.
2. Los componentes reutilizables deben aceptar datos por props y emitir eventos claros; no deben depender directamente de páginas concretas.
3. Las personas que trabajan en páginas únicas deben poder utilizar datos mock y no esperar al backend, stores o componentes finales.
4. Las personas 4 y 5 deben publicar primero los componentes base y sus contratos, pero no necesitan terminar todo para que las personas 1, 2 y 3 comiencen.
5. Evitar que dos personas modifiquen el mismo archivo. Las páginas consumen componentes reutilizables sin cambiar su implementación.
6. Centralizar rutas, tipos y datos mock en archivos acordados por el equipo para que no se creen implementaciones incompatibles.
7. Integrar al final los layouts, el router, stores, permisos por rol, responsive y estados completos de los viajes.

## Secuencia de trabajo

1. **Arranque conjunto:** acordar interfaces, rutas, props, eventos y datos mock.
2. **Trabajo paralelo:** personas 4 y 5 construyen reutilizables; personas 1, 2 y 3 desarrollan páginas con mocks.
3. **Integración:** conectar páginas con layouts, router y stores.
4. **Validación:** probar navegación, responsive, permisos por rol, estados de viaje, notificaciones, GPS y administración.
5. **Alcance beta:** mantener fuera las cuatro pantallas excluidas salvo que el equipo decida incorporarlas.
