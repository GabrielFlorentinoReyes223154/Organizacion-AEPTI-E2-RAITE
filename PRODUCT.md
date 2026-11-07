# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Estudiantes de la Universidad Autónoma de Ciudad Juárez (UACJ) con correo `@alumnos.uacj.mx`. Un mismo perfil hace dos papeles según el día:

- **Pasajero:** no tiene auto o no lo trae hoy. Desde el celular, a menudo minutos antes de salir o ya en la calle, busca un raite cerca de su punto de referencia hacia o desde su campus, pide lugar y espera la confirmación.
- **Conductor:** ya hace el recorrido y le sobran lugares. Publica el viaje (punto de referencia, campus, horario, lugares) y acepta o rechaza solicitudes desde el teléfono.
- **Administrador:** revisa reportes y suspende cuentas desde el admin de Django; no es usuario de la interfaz de Quasar.

## Product Purpose

Ordenar y dar confianza a los raites que hoy los alumnos organizan de manera informal. Baja el gasto y el tiempo de traslado de quien depende del transporte público o privado, y aprovecha los lugares libres en autos de compañeros que ya van al mismo campus a la misma hora.

Éxito para esta etapa: que funcione completo en la demo ante el profesor de la materia (Innovación Tecnológica, UACJ, 2026) y en una prueba piloto con estudiantes reales.

## Positioning

Solo entre alumnos de la UACJ, verificados con correo institucional. No es un servicio profesional tipo Uber o DiDi: son compañeros que comparten un trayecto que ya iban a hacer. El origen se elige de un catálogo de lugares conocidos de Juárez ("Oxxo Dunas", "Del Río"), nunca con direcciones; el punto exacto se acuerda después de confirmar. La preferencia "mismo sexo" se respeta para todo el viaje.

## Operating Context

- Uso principal en el celular, sobre la marcha y muchas veces en exteriores: el texto y los controles deben leerse a pleno sol.
- La demo se hace en escritorio, así que el escritorio también debe verse bien y no puede ser un celular estirado.
- Flujo: registro con correo institucional y código de verificación → perfil (y vehículo si conduce) → publicar o buscar → solicitar → aceptar o rechazar → iniciar y finalizar → calificar; además historial, notificaciones dentro de la app y reportes.
- Campus: CU, IIT, ICB, ICSA, IADA. Puntos de referencia: 128 lugares de Ciudad Juárez tomados de OpenStreetMap.

## Capabilities and Constraints

- Frontend en Quasar 2 (Vue 3, Pinia, Vue Router). El diseño se aplica **personalizando el tema de Quasar** (variables, marca, estilos), no reemplazando sus componentes.
- Mapas con Leaflet + OpenStreetMap (aún sin instalar).
- Backend Django REST ya terminado (Capa 2); los endpoints están en `RaiteDocs/API.md`.
- Toda la interfaz en español de México.
- Notificaciones solo dentro de la app, por consulta periódica; sin push ni WebSockets.
- El teléfono y las placas solo se muestran entre conductor y pasajero con un raite confirmado.
- 1 a 5 lugares por viaje. Un viaje `PUBLICADO` con más de 2 h de retraso se da por vencido.
- Fuera de alcance: pagos, GPS permanente, conductores ajenos a la UACJ, cobertura fuera de Ciudad Juárez, integración con sistemas de la UACJ.
- Reglas de negocio completas y su prioridad: `CLAUDE.md`.

## Brand Commitments

- **Nombre:** por confirmar. En el código y en la interfaz se usa "Raite" hasta que se decida otra cosa ("UniGo-UACJ" y "RutaClara" aparecen en documentos viejos).
- **Colores institucionales de la UACJ** (Manual básico de Identidad Gráfica Institucional): azul Pantone 293 C `#003CA6`, amarillo Pantone Yellow 012 C `#FFD600`, gris Pantone Cool Gray 11 C `#555559` y negro `#231F20`. Son los colores de marca; se pueden derivar tonos más claros u oscuros para fondos, bordes y estados. El amarillo nunca va como texto sobre fondo claro. Detalle y reglas de contraste en `DESIGN.md`.
- **Sin escudo ni logotipo oficial de la UACJ.** Los textos sí pueden mencionar a la universidad ("solo alumnos de la UACJ"), porque el acceso es con correo institucional.
- **Voz:** de tú. Estudiantil, juarense, cercana y confiable; no corporativa. "Raite" es la palabra del producto.
- **Logo:** sin decidir. Existe `Front_Raite/src/assets/raite.svg`, pero no se ha confirmado que sea el definitivo.

## Evidence on Hand

- Requerimientos: `RaiteDocs/docs/2_SRS.md`; carta y fase 1: `RaiteDocs/docs/1_Raite - Fase 1 - Proyecto Innovacion tecnologica.md`.
- Catálogo real de campus y puntos: `Back_Raite/apps/locations/data/*.json`.
- Bocetos del equipo anterior generados con IA (`RaiteDocs/Design/Raite_PageImages/`) y `RaiteDocs/Design/UI_UX.md`: solo referencia. Describen otro flujo (sin verificación de correo, catálogo cerrado de marcas) y no son obligatorios.
- No hay usuarios, testimonios, cifras de uso ni resultados del piloto. No inventarlos.

## Product Principles

1. **Confianza antes que velocidad.** Cada pantalla debe dejar claro que todos son alumnos verificados, que la calificación de cada uno se ve y que el contacto solo se muestra al confirmar.
2. **Lugares conocidos, no direcciones.** El origen siempre es un punto de referencia del catálogo; el punto exacto se acuerda entre las dos personas.
3. **Usable en la banqueta.** Pensado para una mano, a pleno sol y con prisa: lo principal se hace en pocos toques y el estado del raite se entiende de un vistazo.
4. **Dos papeles, una persona.** Cambiar entre pasajero y conductor debe ser natural y sin pantallas extra.
5. **Lista para la demo.** Que cada flujo se pueda mostrar completo en escritorio sin huecos ni pantallas de plantilla.

## Accessibility & Inclusion

- Cumplir WCAG 2.1 AA: contraste, navegación con teclado, foco visible y etiquetas para lectores de pantalla.
- El contraste y el tamaño del texto deben aguantar el uso en exteriores, más allá del mínimo AA.
- El campo `sexo` tiene tres valores (`M`, `F`, `X` "Otro"). Los textos sobre la preferencia "mismo sexo" deben ser neutros y no dar nada por supuesto.
