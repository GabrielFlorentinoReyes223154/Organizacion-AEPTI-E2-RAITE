---
name: Raite
description: Raites entre alumnos de la UACJ, con los colores institucionales y legible a pleno sol.
colors:
  azul-uacj: "#003CA6"
  amarillo-uacj: "#FFD600"
  gris-uacj: "#555559"
  negro-uacj: "#231F20"
  azul-hondo: "#002C7A"
  azul-noche: "#001F57"
  azul-niebla: "#DCE5F7"
  azul-tenue: "#E6EDF9"
  amarillo-hondo: "#E8C200"
  amarillo-tenue: "#FFF3B0"
  blanco: "#FFFFFF"
  fondo: "#F3F5F9"
  gris-tenue: "#ECEDF0"
  borde-sutil: "#D5D8DE"
  borde-campo: "#8A8C93"
  gris-placeholder: "#6B6B70"
  gris-deshabilitado: "#6E7076"
  verde: "#1E6B34"
  verde-texto: "#14532D"
  verde-tenue: "#E2F2E6"
  rojo: "#B3261E"
  rojo-texto: "#8C1D18"
  rojo-tenue: "#FCE8E6"
typography:
  headline:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "0em"
  body:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0em"
  label:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "0.01em"
  button:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0em"
  hora:
    fontFamily: "Atkinson Hyperlegible Mono, ui-monospace, monospace"
    fontSize: "1.75rem"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  dato:
    fontFamily: "Atkinson Hyperlegible Mono, ui-monospace, monospace"
    fontSize: "1.25rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.08em"
rounded:
  md: "12px"
  lg: "16px"
  tarjeta: "20px"
  xl: "24px"
  hoja: "28px"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "48px"
components:
  button-primary:
    backgroundColor: "{colors.azul-uacj}"
    textColor: "{colors.blanco}"
    typography: "{typography.button}"
    rounded: "{rounded.pill}"
    padding: "0 24px"
    height: "48px"
  button-primary-xl:
    height: "56px"
    fontSize: "1.125rem"
  button-primary-hover:
    backgroundColor: "{colors.azul-hondo}"
  button-primary-active:
    backgroundColor: "{colors.azul-noche}"
  button-acento:
    backgroundColor: "{colors.amarillo-uacj}"
    textColor: "{colors.negro-uacj}"
    typography: "{typography.button}"
    rounded: "{rounded.pill}"
    padding: "0 24px"
    height: "48px"
  button-acento-hover:
    backgroundColor: "{colors.amarillo-hondo}"
  button-secundario:
    backgroundColor: "{colors.blanco}"
    textColor: "{colors.azul-uacj}"
    typography: "{typography.button}"
    rounded: "{rounded.pill}"
    padding: "0 24px"
    height: "48px"
  button-peligro:
    backgroundColor: "{colors.rojo}"
    textColor: "{colors.blanco}"
    typography: "{typography.button}"
    rounded: "{rounded.pill}"
    height: "48px"
  button-deshabilitado:
    backgroundColor: "{colors.gris-tenue}"
    textColor: "{colors.gris-deshabilitado}"
  card-viaje:
    backgroundColor: "{colors.blanco}"
    textColor: "{colors.negro-uacj}"
    rounded: "{rounded.tarjeta}"
    padding: "16px"
  tarjeta-destacada:
    backgroundColor: "{colors.azul-uacj}"
    textColor: "{colors.blanco}"
    rounded: "{rounded.xl}"
    padding: "20px"
  placa-campus:
    backgroundColor: "{colors.azul-uacj}"
    textColor: "{colors.blanco}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "4px 8px"
  chip-publicado:
    backgroundColor: "{colors.azul-tenue}"
    textColor: "{colors.azul-uacj}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    height: "32px"
  chip-en-curso:
    backgroundColor: "{colors.amarillo-uacj}"
    textColor: "{colors.negro-uacj}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    height: "32px"
  chip-finalizado:
    backgroundColor: "{colors.blanco}"
    textColor: "{colors.negro-uacj}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    height: "32px"
  chip-pendiente:
    backgroundColor: "{colors.amarillo-tenue}"
    textColor: "{colors.negro-uacj}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    height: "32px"
  chip-aceptada:
    backgroundColor: "{colors.verde-tenue}"
    textColor: "{colors.verde-texto}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    height: "32px"
  chip-rechazada:
    backgroundColor: "{colors.rojo-tenue}"
    textColor: "{colors.rojo-texto}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    height: "32px"
  chip-cancelado:
    backgroundColor: "{colors.gris-tenue}"
    textColor: "{colors.gris-uacj}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    height: "32px"
  chip-vencido:
    backgroundColor: "{colors.gris-tenue}"
    textColor: "{colors.negro-uacj}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    height: "32px"
  input:
    backgroundColor: "{colors.gris-tenue}"
    textColor: "{colors.negro-uacj}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    height: "56px"
  header:
    backgroundColor: "{colors.blanco}"
    textColor: "{colors.negro-uacj}"
    typography: "{typography.headline}"
    height: "64px"
  header-escritorio:
    backgroundColor: "{colors.azul-tenue}"
    textColor: "{colors.azul-uacj}"
    height: "72px"
  menu-lateral:
    backgroundColor: "{colors.blanco}"
    textColor: "{colors.negro-uacj}"
    rounded: "{rounded.tarjeta}"
    width: "240px"
  menu-lateral-activo:
    backgroundColor: "{colors.azul-tenue}"
    textColor: "{colors.azul-uacj}"
  nav-inferior:
    backgroundColor: "{colors.blanco}"
    textColor: "{colors.gris-uacj}"
    typography: "{typography.label}"
    height: "72px"
  nav-inferior-activo:
    backgroundColor: "{colors.blanco}"
    textColor: "{colors.azul-uacj}"
---

# Design System: Raite

> Rediseño del 2026-11-07. La estructura viene de una maqueta inspirada en el Figma de NeoFracc (encabezado blanco, barra inferior blanca, tarjeta destacada, accesos rápidos, botones en píldora y campos rellenos), traducida a la paleta UACJ de abajo. Se aplica vista por vista; la primera fue Entrar (con el layout público y el tema base). Si algo no funciona en Quasar o con contenido real, se corrige aquí primero.

## Overview

**Creative North Star: "El letrero de la parada"**

Raite se ve como la señalización de una parada de transporte en Juárez: un azul sólido que ubica, un amarillo que marca lo que importa ahora y texto negro grande sobre blanco, hecho para leerse de lejos, de reojo y a pleno sol. Se usa con prisa y con una mano, así que manda la claridad: cada pantalla tiene una tarea principal, un estado que se entiende de un vistazo y una sola acción destacada.

Los colores son los institucionales de la UACJ (azul 293 C, amarillo 012 C, gris Cool Gray 11 C y negro). El azul es la estructura: encabezado, barra de navegación y acción principal. El amarillo es escaso y siempre va sobre azul o con texto negro encima. El gris y el negro se encargan del texto. No se usa el escudo ni el logotipo de la universidad.

La interfaz es clara a propósito. El uso principal es en exteriores, de día, y un fondo blanco con texto casi negro da el mayor contraste bajo el sol. La densidad es media: las tarjetas de viaje muestran lo indispensable para decidir (hora, punto de referencia, campus, lugares libres y calificación del conductor), y el resto vive en el detalle.

**Key Characteristics:**
- Celular: encabezado blanco con el título grande a la izquierda y barra inferior blanca; la pestaña activa va en azul con un punto.
- Computadora: barra superior azul tenue (marca, cambio de papel, campanita, usuario) y menú lateral blanco con la navegación.
- El azul sólido se reserva para la acción principal, la tarjeta destacada ("Tu próximo raite") y el panel de las pantallas públicas.
- Una sola acción destacada por pantalla.
- Texto de lectura con contraste de 7:1 o más; nada por debajo de 4.5:1.
- Tarjetas blancas con sombra suave sobre la página `fondo`, sin borde.
- Las horas, las placas y el código de verificación usan una fuente monoespaciada para que se lean sin errores.
- Todo se construye con componentes de Quasar y su tema; no hay componentes visuales propios fuera de la tarjeta de viaje.

## Colors

Azul institucional como estructura, amarillo como señal, negro y gris para leer, y tonos derivados solo para fondos, bordes y estados.

### Primary
- **Azul UACJ** (#003CA6): encabezado, barra de navegación inferior, botón principal, enlaces, íconos activos, foco sobre fondo claro y la placa de campus. Contra blanco da 9.56:1, así que sirve como texto en títulos y enlaces.
- **Azul hondo** (#002C7A): hover del botón principal, pestaña activa de la barra inferior y color `info`.
- **Azul noche** (#001F57): botón principal presionado.
- **Azul tenue** (#E6EDF9): fondo de un elemento seleccionado (punto elegido en una lista, filtro activo) y del chip "Publicado".
- **Azul niebla** (#DCE5F7): etiquetas inactivas de la barra inferior y texto secundario sobre azul (7.55:1 sobre el azul UACJ).

### Secondary
- **Amarillo UACJ** (#FFD600): es el acento. Se usa en el botón de acento (solo sobre superficies azules), el indicador de la pestaña activa, la barra de la placa de campus, el foco sobre superficies azules, el chip "En curso" y la selección de texto. Lleva texto negro encima (11.54:1) o va sobre azul (6.77:1).
- **Amarillo hondo** (#E8C200): hover del botón de acento.
- **Amarillo tenue** (#FFF3B0): fondo del chip "Pendiente" y de los avisos de advertencia, siempre con texto negro (14.51:1).

### Neutral
- **Negro UACJ** (#231F20): todo el texto principal. Contra blanco da 16.30:1. No se usa `#000`.
- **Gris UACJ** (#555559): texto secundario (fechas, contadores, ayudas de campo, etiquetas). Contra blanco da 7.42:1 y contra el fondo 6.80:1.
- **Blanco** (#FFFFFF): tarjetas, campos y hojas.
- **Fondo** (#F3F5F9): fondo de página. Es un gris azulado muy claro para que las tarjetas blancas se distingan sin sombra.
- **Gris tenue** (#ECEDF0): fondo de chips cancelados o vencidos y de botones deshabilitados.
- **Hover** (`--raite-blanco-hover` #FAFBFD, `--raite-azul-tenue-hover` #DDE6F6, `--raite-amarillo-tenue-hover` #FFEB85): fondos apenas más oscuros al pasar el puntero sobre tarjetas, avisos y el aviso de solicitudes pendientes. El texto encima no cambia.
- **Borde sutil** (#D5D8DE): borde de tarjetas y separadores. Es decorativo; nunca es lo único que delimita un control.
- **Borde de campo** (#8A8C93): borde de los campos de formulario. Contra blanco da 3.36:1, lo que cumple el mínimo de 3:1 para componentes.
- **Gris de placeholder** (#6B6B70): ya no se usa dentro de los campos rellenos (sobre gris tenue da 4.49:1). El texto de ejemplo va en gris UACJ (6.34:1 sobre gris tenue).
- **Gris deshabilitado** (#6E7076): texto de un control deshabilitado (4.23:1 sobre gris tenue; WCAG no exige contraste aquí, pero se mantiene legible).

### Estados
- **Verde** (#1E6B34): fondo de botones o avisos de éxito con texto blanco (6.55:1). **Verde texto** (#14532D) sobre **verde tenue** (#E2F2E6): chip "Aceptada" (7.84:1).
- **Rojo** (#B3261E): botones de cancelar o rechazar, borde de campo con error y fondo con texto blanco (6.54:1). **Rojo texto** (#8C1D18): mensajes de error y chip "Rechazada" sobre **rojo tenue** (#FCE8E6) (7.74:1).

### Tabla de contraste

Combinaciones permitidas de texto sobre fondo (WCAG 2.1, calculado con la fórmula de luminancia relativa). Si una combinación no está aquí, no se usa.

| Texto | Fondo | Contraste | Uso |
|---|---|---|---|
| Negro #231F20 | Blanco #FFFFFF | 16.30:1 | Texto principal |
| Negro #231F20 | Fondo #F3F5F9 | 14.93:1 | Texto directo sobre la página |
| Negro #231F20 | Amarillo #FFD600 | 11.54:1 | Botón de acento, chip "En curso" |
| Negro #231F20 | Amarillo hondo #E8C200 | 9.43:1 | Hover del botón de acento |
| Negro #231F20 | Amarillo tenue #FFF3B0 | 14.51:1 | Chip "Pendiente", aviso |
| Negro #231F20 | Gris tenue #ECEDF0 | 13.92:1 | Chip "Vencido" |
| Gris #555559 | Blanco #FFFFFF | 7.42:1 | Texto secundario |
| Gris #555559 | Fondo #F3F5F9 | 6.80:1 | Texto secundario sobre la página |
| Gris #555559 | Gris tenue #ECEDF0 | 6.34:1 | Chip "Cancelado", placeholder en campo relleno |
| Azul #003CA6 | Blanco #FFFFFF | 9.56:1 | Enlaces, títulos, botón secundario |
| Azul #003CA6 | Azul tenue #E6EDF9 | 8.12:1 | Chip "Publicado", elemento seleccionado |
| Blanco #FFFFFF | Azul #003CA6 | 9.56:1 | Botón principal, encabezado, placa de campus |
| Blanco #FFFFFF | Azul hondo #002C7A | 12.79:1 | Hover, pestaña activa |
| Amarillo #FFD600 | Azul #003CA6 | 6.77:1 | Acento sobre azul |
| Amarillo #FFD600 | Azul hondo #002C7A | 9.06:1 | Acento sobre azul hondo |
| Azul niebla #DCE5F7 | Azul #003CA6 | 7.55:1 | Pestañas inactivas, subtítulo del encabezado |
| Verde texto #14532D | Verde tenue #E2F2E6 | 7.84:1 | Chip "Aceptada" |
| Blanco #FFFFFF | Verde #1E6B34 | 6.55:1 | Aviso o botón de éxito |
| Rojo texto #8C1D18 | Rojo tenue #FCE8E6 | 7.74:1 | Chip "Rechazada", aviso de error |
| Rojo texto #8C1D18 | Blanco #FFFFFF | 9.11:1 | Mensaje de error de campo |
| Blanco #FFFFFF | Rojo #B3261E | 6.54:1 | Botón de peligro |
| Gris placeholder #6B6B70 | Blanco #FFFFFF | 5.30:1 | Placeholder |

Combinaciones **prohibidas**: amarillo sobre blanco (1.41:1), amarillo sobre fondo (1.29:1) y cualquier texto amarillo sobre una superficie clara.

### Named Rules

**La regla de la señal.** El amarillo nunca es texto ni borde sobre fondo claro. Va sobre azul (indicador, foco, barra de la placa, botón de acento) o como fondo con texto negro encima. Se usa poco: es lo que importa ahora en la pantalla.

**La regla del sol.** El texto de lectura (párrafos, nombres, horas, puntos de referencia) va a 7:1 o más. Las etiquetas y los chips van a 6:1 o más. Nada baja de 4.5:1. El color nunca es la única señal: cada estado lleva además ícono y texto.

**La regla del azul que señala.** El azul sólido marca lo más importante: la acción principal, la tarjeta destacada ("Tu próximo raite", una por pantalla) y el panel de las pantallas públicas. El resto de las tarjetas y secciones van en blanco. Los fondos azul tenue sirven para lo seleccionado, los círculos de los íconos y la barra superior de escritorio.

## Typography

**Fuente de interfaz:** Atkinson Hyperlegible Next (respaldo: `system-ui, sans-serif`)
**Fuente de datos:** Atkinson Hyperlegible Mono (respaldo: `ui-monospace, monospace`)

**Carácter:** Atkinson Hyperlegible la diseñó el Braille Institute para que cada letra se distinga de las demás (l/I/1, O/0, rn/m) aun con poca visión o con reflejo. La versión Mono, de la misma familia, se usa para los datos que se copian o se comparan: horas, placas, teléfono y código de verificación. Las dos tienen acentos y ñ.

Las dos están en Google Fonts con licencia OFL. Se auto-hospedan como `woff2` variables (un archivo cubre todos los pesos) en `Front_Raite/src/css/fonts/`, con `font-display: swap`, para no depender de una petición externa en la calle con mala señal.

### Hierarchy
- **Headline** (700, 1.5rem en celular / 1.75rem desde 1024px, interlineado 1.2): título de la pantalla ("Buscar raite", "Mis viajes"). Uno por pantalla.
- **Title** (700, 1.125rem, 1.3): títulos de sección, nombre del punto de referencia en la tarjeta y encabezados de diálogo.
- **Body** (400, 1rem, 1.5): todo el texto corrido, descripciones y mensajes. Medida máxima de 65ch en textos largos (reportes, ayuda).
- **Label** (600, 0.875rem, 1.3, +0.01em): etiquetas de campo, chips, pestañas y metadatos. Es el tamaño mínimo de toda la interfaz: no hay texto de menos de 14px.
- **Button** (700, 1rem, 1.2): texto de botones, en minúsculas normales (sin MAYÚSCULAS).
- **Hora** (Mono 700, 1.75rem, 1.1, cifras tabulares): la hora de salida en la tarjeta de viaje y en el detalle. Formato de 24 horas, "07:30".
- **Dato** (Mono 600, 1.25rem, +0.08em): placas ("ABC-123-D"), teléfono ("656 123 4567") y el código de verificación de 6 dígitos (este último a 1.75rem).

### Named Rules

**La regla de los 16.** El texto base es de 16px (Quasar trae 14px por defecto: se cambia). Así se lee al sol y evita que iOS haga zoom al enfocar un campo.

**La regla sin gritos.** Nada en MAYÚSCULAS. Quasar pone en mayúsculas los botones y las pestañas por defecto: se desactiva de forma global.

## Layout

**Escala de espaciado:** la de Quasar con base de 16px: `xs` 4, `sm` 8, `md` 16, `lg` 24, `xl` 48. No se usan valores fuera de la escala.

**Celular (menos de 600px):** margen lateral de 16px. Estructura de Quasar `hHh lpR fFf`: encabezado fijo azul de 56px arriba, contenido en una columna y barra de navegación inferior azul de 64px (más el área segura de iOS). Cuando hay una acción principal en una pantalla de detalle ("Solicitar lugar", "Aceptar"), va en una barra fija sobre la navegación inferior y ocupa todo el ancho.

**Tableta (600 a 1023px):** margen de 24px y la misma estructura que en celular. Los listados pueden ir en dos columnas de tarjetas.

**Escritorio (1024px o más):** la barra inferior desaparece y su navegación pasa a un menú lateral blanco de 240px a la izquierda. Arriba va una barra azul tenue de 72px con la marca, el cambio de papel, la campanita y el usuario. La barra y el cuerpo ocupan todo el ancho de la ventana (márgenes de 32px, sin tope): en computadora se aprovecha la pantalla completa, y cada vista acomoda su contenido en columnas o cuadrículas en lugar de una sola columna angosta. La búsqueda lleva los filtros en una barra horizontal arriba y, debajo, la lista (izquierda) y el mapa grande (derecha) al alto de la ventana. Las pantallas públicas (entrar, registro, verificar) se parten a la mitad: panel azul con el mensaje a la izquierda y el formulario en una tarjeta a la derecha (máximo 480px). Registro, que es largo, marca `meta.amplio`: el panel baja al 40% y la tarjeta crece a 820px con los campos en dos columnas y dos secciones numeradas ("Tus datos", "Cómo vas a viajar"). Las pantallas con formulario y sesión (Vehículo) usan dos columnas: el formulario en una tarjeta y, a la derecha, una vista previa que se actualiza mientras se escribe.

**Ritmo:** 8px entre una etiqueta y su campo, 16px entre campos, 24px entre grupos y 48px entre secciones de una pantalla. Hay más espacio arriba de un título que debajo. Las tarjetas de un listado se separan 16px.

**Objetivos táctiles:** todo lo que se toca mide al menos 48×48px, incluidos los íconos sueltos (con relleno si el ícono es más chico).

## Elevation & Depth

La profundidad se marca con capas de color (página `fondo` → tarjeta `blanco`) y con sombras suaves. Bajo el sol las sombras casi no se ven, así que nunca cargan información: la tarjeta blanca sobre el gris azulado ya se distingue sola.

### Shadow Vocabulary
- **Tarjeta** (`--raite-sombra-tarjeta`: `0 2px 10px rgba(35, 31, 32, 0.06)`): tarjetas, accesos rápidos, menú lateral.
- **Destacada** (`--raite-sombra-destacada`: `0 10px 24px rgba(0, 44, 122, 0.22)`): la tarjeta azul "Tu próximo raite".
- **Flotante** (`box-shadow: 0 4px 12px rgba(35, 31, 32, 0.14)`): menús desplegables, opciones de `q-select` y tooltips.
- **Hoja** (`box-shadow: 0 8px 24px rgba(35, 31, 32, 0.18)`): diálogos y hojas inferiores (`q-dialog position="bottom"`).
- **Barra de acción** (`box-shadow: 0 -2px 8px rgba(35, 31, 32, 0.10)`): la barra fija de acción principal en celular, para separarla del contenido que se desplaza debajo.

### Named Rules

**La regla suave.** Las sombras son las del vocabulario de arriba, nunca las `shadow-1` a `shadow-24` de Quasar. `q-card` y `.raite-tarjeta` ya traen la sombra de tarjeta desde `app.scss`.

## Shapes

Esquinas redondeadas y amables: píldora en botones, chips, filtros y contadores; 12px en campos; 8px en la placa de campus; 20px en tarjetas; 24px en la tarjeta destacada; 28px en la parte superior de las hojas y en la tarjeta del formulario público. Los campos llevan solo una línea inferior de 2px (`borde-campo`) y un contorno de 2px azul al enfocarse. No hay bordes laterales de color en tarjetas ni avisos.

**Foco visible:** contorno de 2px con 2px de separación. Es azul UACJ sobre superficies claras y amarillo UACJ sobre superficies azules. Nunca se quita el foco.

## Components

Todos son componentes de Quasar configurados con el tema; ninguno se reemplaza.

### Buttons
- **Forma:** píldora (`$button-border-radius: 999px`), alto de 48px y texto Button sin mayúsculas. La acción principal de un formulario usa la clase `raite-btn-xl` (56px, 1.125rem) y ocupa todo el ancho de su tarjeta. El botón secundario (`outline`) lleva borde de 2px.
- **Principal** (`color="primary"`): fondo azul UACJ con texto blanco. Hover en azul hondo y presionado en azul noche. Hay uno por pantalla: "Buscar", "Publicar viaje", "Solicitar lugar", "Aceptar".
- **Acento** (`color="accent" text-color="dark"`): fondo amarillo con texto negro y hover en amarillo hondo. **Solo sobre superficies azules** (por ejemplo, "Publicar viaje" dentro del encabezado en escritorio). Nunca sobre blanco.
- **Secundario** (`outline color="primary"`): fondo blanco, borde de 1px y texto azul. Para "Editar", "Ver en el mapa" y "Reenviar código".
- **Texto** (`flat color="primary"`): para acciones menores dentro de una tarjeta o un diálogo ("Cancelar" en el sentido de cerrar).
- **Peligro** (`color="negative"`): fondo rojo con texto blanco, para la acción destructiva principal de una pantalla ("Cancelar solicitud", "Cancelar mi lugar"). Siempre pide confirmación en un diálogo.
- **Peligro de texto** (`flat` con clase `text-rojo-texto`): texto rojo #8C1D18 sin fondo (9.11:1 sobre blanco), para acciones destructivas que se repiten en una lista o que no son la principal ("Rechazar" en cada solicitud, "Cancelar viaje" en el detalle). Siempre pide confirmación en un diálogo cuyo botón de confirmar sí es rojo relleno.
- **Deshabilitado:** fondo gris tenue con texto gris deshabilitado. Si hay un motivo, se explica cerca ("No quedan lugares").
- **Cargando:** usa la propiedad `loading` de Quasar, que mantiene el ancho del botón; no se cambia el texto.

### Chips
- **Estilo:** `q-chip` sin borde, en forma de píldora y de 32px de alto, con ícono a la izquierda y texto Label. El color nunca va solo: siempre hay ícono y palabra.
- **Estados de viaje:**
  - Publicado: azul tenue con texto azul, ícono de calendario.
  - En curso: amarillo con texto negro, ícono de auto.
  - Finalizado: blanco con borde `borde-campo` y texto negro, ícono de bandera.
  - Cancelado: gris tenue con texto gris, ícono de prohibido.
  - Vencido (calculado): gris tenue con texto negro, ícono de reloj.
- **Estados de solicitud:**
  - Pendiente: amarillo tenue con texto negro, ícono de reloj de arena.
  - Aceptada: verde tenue con texto verde, ícono de palomita.
  - Rechazada: rojo tenue con texto rojo, ícono de tache.
  - Cancelada: gris tenue con texto gris, ícono de prohibido.
- **Filtros** (campus, sentido): `q-chip clickable` con fondo blanco y borde `borde-campo` cuando no está elegido, y fondo azul tenue con texto azul e ícono de palomita cuando sí.

### Cards / Containers
- **Esquinas:** 16px.
- **Fondo:** blanco sobre la página `fondo`.
- **Sombra:** ninguna (`flat bordered`; ver Elevation & Depth).
- **Borde:** 1px `borde-sutil`.
- **Relleno interno:** 16px; 24px en escritorio para el detalle.
- Una tarjeta nunca va dentro de otra. Las secciones dentro del detalle se separan con espacio o con un `q-separator`.

### Tarjeta de viaje (componente distintivo)
Es la única pieza propia del sistema y aparece en la búsqueda, en "Mis viajes" y en el historial. Toda la tarjeta se puede tocar (`q-card` con `q-item clickable` o `v-ripple`). De arriba abajo:

1. **Fila superior:** la hora en estilo Hora (azul UACJ) a la izquierda y el chip de estado a la derecha. Debajo, la fecha en Label gris ("Hoy", "Mañana", "jue 12 nov").
2. **Ruta:** dos paradas unidas por una línea vertical de 2px en azul tenue.
   - **Origen:** círculo azul de 12px con contorno y el nombre del punto de referencia en Title ("Oxxo Dunas"), con la calle en gris debajo.
   - **Destino:** la **placa de campus**, una etiqueta azul UACJ con el código del campus en blanco ("CU", "ICB") y una barra amarilla de 3px en la orilla inferior, seguida del nombre completo en gris. Es la señal del sistema: se ve igual en la tarjeta, en el detalle y en el mapa. Si el viaje va desde el campus, el orden se invierte.
3. **Fila inferior:** lugares libres ("2 de 4 lugares"), calificación del conductor (ícono de estrella y número con una decimal, en negro) y la distancia en búsqueda ("a 1.2 km"). Todo en Label, separado por espacio y sin puntos medios decorativos.

Cuando la solicitud está aceptada, el detalle muestra un bloque de contacto con teléfono y placas en estilo Dato, sobre azul tenue. Este bloque no existe antes de la confirmación (RNF-02).

### Inputs / Fields
- **Estilo:** `q-input` y `q-select` con `outlined` (el tema lo pinta relleno): fondo gris tenue, línea inferior de 2px `borde-campo`, esquinas de 12px, alto de 56px y texto de 16px. La etiqueta va arriba del campo, en Label negro (no flotante dentro del campo), y la ayuda va debajo en gris.
- **Foco:** borde de 2px azul UACJ.
- **Error:** borde rojo, mensaje en rojo texto debajo del campo con un ícono de alerta, y el mensaje dice qué está mal y cómo corregirlo ("Usa tu correo @alumnos.uacj.mx"). Se valida al salir del campo, no mientras se escribe.
- **Deshabilitado:** fondo gris tenue y texto gris deshabilitado.
- **Casos especiales:**
  - Correo: `type="email"`, con el sufijo `@alumnos.uacj.mx` visible como ayuda.
  - Teléfono: máscara `### ### ####` y `inputmode="tel"`.
  - Código de verificación: un solo `q-input` con máscara `######`, `inputmode="numeric"` y `autocomplete="one-time-code"`, en estilo Dato a 1.75rem y centrado. Debajo, el botón secundario "Reenviar código" con la cuenta regresiva de 60 s.
  - Punto de referencia: `q-select` con `use-input` para filtrar mientras se escribe. Cada opción muestra el nombre en Body y la calle en gris; si hay ubicación, también la distancia.
  - Hora: `q-time` en formato de 24 horas dentro de un `q-popup-proxy`, y el valor se muestra en estilo Dato.
  - Lugares: `q-btn-toggle` del 1 al 5, sin pasar los asientos del vehículo.

### Navigation
Todo vive en `layouts/AppLayout.vue`.

- **Encabezado en celular** (`q-header`): blanco, 64px, con una línea `borde-sutil` abajo. A la izquierda, el título de la pantalla en Headline negro; a la derecha, la campanita (botón redondo azul tenue con ícono azul de 24px y contador `amarillo` con texto negro y un aro blanco). En pantallas secundarias (`meta.atras`) lleva la flecha de regresar a la izquierda y el título centrado en Title azul, sin campanita.
- **Barra superior en computadora:** azul tenue, 72px, contenido centrado a 1280px. Logo (versión para fondo claro, `assets/logo-raite.png`, 48px de alto) que lleva a `/`; a la derecha el cambio de papel, la campanita (botón redondo blanco) y una píldora blanca con las iniciales en un círculo azul y el nombre corto ("Valeria R.") que lleva a Perfil.
- **Menú lateral en computadora:** tarjeta blanca de 240px, fija al desplazarse, con el papel arriba ("Como pasajero" / "Como conductor"), las mismas entradas que la barra inferior más Avisos (con contador amarillo tenue) y, separado, "Cerrar sesión" en rojo texto. La entrada activa lleva fondo azul tenue y texto azul. En pantallas secundarias, arriba del contenido van "Regresar" y el título de la pantalla.
- **Barra inferior en celular** (`q-footer` + `q-tabs` con ícono y texto): blanca, 72px, con una línea `borde-sutil` arriba y cuatro pestañas. Las inactivas van en gris UACJ; la activa en azul con el texto en negritas y un punto azul de 5px debajo.
  - Como pasajero: Inicio · Buscar raite · Mis raites · Perfil.
  - Como conductor: Inicio · Mis viajes · Publicar · Perfil.
  - Historial y Avisos no van en la barra: se abren desde Inicio y con la campanita. En el menú lateral de computadora sí aparecen (Inicio, las dos del papel, Historial, Avisos, Perfil).

### Inicio (`/inicio`)
Es la pantalla a la que llevan `/` y el inicio de sesión, para los dos papeles; su contenido cambia con el papel activo.
- **Cabecera:** la fecha ("Hoy, sábado 7 de noviembre"), "Hola, Nombre" y la acción principal a la derecha ("Buscar raite" o "Publicar viaje", `raite-btn-xl`).
- **Cifras (solo conductor):** cuatro tarjetas con ícono en círculo de color tenue: solicitudes por responder (amarillo), viajes próximos (azul), lugares ocupados (verde) y su calificación (azul).
- **Tarjeta destacada** (`TarjetaDestacada`, 3/5 del ancho): el próximo raite del pasajero (su solicitud aceptada o pendiente más cercana, con conductor, calificación y auto) o el próximo viaje del conductor (lugares ocupados y solicitudes por responder; el botón lleva a las solicitudes si hay). Sin nada próximo, invita a buscar o publicar.
- **Pendientes** (2/5): calificaciones por hacer (fondo amarillo tenue, botón negro "Calificar"), solicitudes en espera (pasajero) o viajes con solicitudes por responder (conductor). Sin nada, "Todo al día" en verde. Abajo, el enlace a los avisos.
- **Accesos rápidos:** seis cuadros blancos de 128px con ícono en círculo azul tenue.
- **Cambio de papel:** con rol AMBOS, un par de píldoras "Pido raite / Doy raite". La elegida va en azul con texto blanco y la otra en azul sobre azul tenue (en la barra de computadora el fondo del control es blanco). En celular ocupa una segunda fila del encabezado a todo el ancho; en computadora va en la barra superior. Se nombra por lo que haces y no por género. El mismo control está en Perfil.
- **Foco:** el encabezado y la barra inferior son claros, así que el foco ahí es azul. El amarillo queda solo para lo marcado con `.raite-sobre-azul`.

### Búsqueda (variante B elegida)
- **Celular:** el mapa ocupa la pantalla. Arriba flota el buscador ("Sales de …") y un botón de filtros que abre los filtros en una hoja inferior. Los resultados van en una hoja inferior con tres alturas (mini, media y completa) que se cambia arrastrando el asa o con el botón "Ver lista / Ver mapa" (`aria-expanded`).
- **Accesibilidad:** en el documento, la lista de resultados va antes que el mapa, así que con teclado o lector se llega primero a las tarjetas. Todo lo que se elige en el mapa también se puede elegir en el buscador.
- **Escritorio:** barra de filtros blanca a todo el ancho (`FormBusqueda horizontal`): punto con botón de ubicación de solo ícono, sentido, campus, día, hora y distancia en menús. Cabe en un renglón desde unos 1700px y en dos a 1280px. Debajo, la lista de resultados (entre 380 y 520px, se desplaza sola) y el mapa en una tarjeta redondeada que llena el resto del alto.

### Detalle del viaje y solicitudes (computadora)
- **Detalle:** dos columnas a todo el ancho. Izquierda (3/5): la fecha, hora, estado y ruta en la `TarjetaDestacada`, con el sentido y los lugares libres abajo; el mapa (360px de alto) y los datos del viaje (vehículo, grupo, lugares, punto, notas). Derecha (2/5): quién maneja (o tus pasajeros, para el conductor), el estado de la solicitud o el bloque de contacto, la tarjeta de acciones y, debajo, las acciones secundarias (editar, cancelar, reportar) como botones de texto.
- **Solicitudes:** izquierda, el cupo como asientos en una tarjeta azul (los ocupados en amarillo con las iniciales) y los confirmados; derecha, "Quieren un lugar" con una tarjeta por solicitud: persona a la izquierda y "Rechazar" (texto rojo) y "Aceptar" (azul) en el mismo renglón.
- **Barra de acción (`BarraAccion`):** en celular es la barra fija de abajo; en computadora se dibuja donde está en la página como una tarjeta blanca con la nota arriba y los botones apilados a todo el ancho. Así nunca tapa el menú lateral.

### Listados y publicar (computadora)
- **Mis raites y Mis viajes:** a todo el ancho (`raite-contenedor--ancho`). Arriba, `raite-cabecera`: el título, un resumen en gris ("3 viajes por hacer, 2 solicitudes por responder") y la acción principal a la derecha. Los viajes van en `raite-rejilla-tarjetas`: tantas columnas de 340px o más como quepan, y las tarjetas de una fila miden lo mismo (el pie amarillo de "solicitudes por responder" queda abajo).
- **Publicar:** dos columnas. Izquierda, el formulario en una tarjeta con secciones numeradas y separadas por una línea (1 Ruta, con el mapa abierto de entrada; 2 Horario; 3 Lugares y grupo; 4 Notas). Derecha, fija al desplazarse: la vista previa "Así te verán los pasajeros" (con un aviso punteado mientras falte el punto o el campus), la tarjeta con "Publicar viaje" y el recordatorio de que el teléfono y las placas solo los ve quien aceptes.

### Avisos, historial y perfil (computadora)
- **Avisos:** ya no es pantalla secundaria (está en el menú lateral). Cabecera con "N sin leer" y "Marcar todo como leído" (secundario). Filtros en píldora "Todos / Sin leer". Los avisos se agrupan por día con una píldora azul tenue ("Hoy", "Ayer", "Mié 4 de nov") y cada grupo es una tarjeta con renglones: ícono en círculo de color según el tipo, título con la etiqueta "Nuevo" si no se ha leído, el mensaje en gris y, a la derecha, la hora y la acción ("Ver solicitudes", "Calificar", "Ver raite"). Los no leídos llevan fondo azul tenue.
- **Historial:** cabecera con el total y, con rol AMBOS, los filtros en píldora (Todos, Como pasajero, Como conductor). "Te falta calificar" va en una franja amarilla tenue con tarjetas blancas y botón negro "Calificar". Los viajes, en `raite-rejilla-tarjetas`.
- **Perfil:** izquierda (fija), el resumen centrado (avatar de 112px con aro, nombre, carrera, correo, "Correo verificado" en verde, calificación y para qué usas Raite), el cambio de papel o la invitación azul a registrar el vehículo, y "Cerrar sesión" (contorno rojo). Derecha: "Tus datos" (teléfono y carrera a dos columnas y "Con quién viajo" como dos tarjetas seleccionables con explicación neutra), el vehículo en una fila con "Editar" y "Mis reportes" desplegable.
- **Encabezados:** `app.scss` fija el interlineado de h1–h6 en 1.3 porque Quasar trae interlineados enormes (h2: 3.75rem).

### Calificar, reportar y 404 (computadora)
- **Calificar:** izquierda (fija), el viaje que se califica (cuándo, desde dónde, campus) con la explicación de para qué sirve calificar; derecha, una tarjeta por persona en cuadrícula (avatar, nombre, carrera, estrellas azules de 44px con el texto "Muy mal… Excelente" debajo, comentario opcional y "Enviar calificación" a todo el ancho). Las estrellas no van en amarillo: sobre blanco no se verían (1.41:1).
- **Reportar:** izquierda, el formulario: la persona se elige en tarjetas con avatar y una marca circular, "¿Qué pasó?" en un campo alto y "Enviar reporte" a la derecha. Derecha (fija): el aviso rojo tenue "¿Estás en peligro ahora? Llama al 911…" y "Qué pasa después" en tres pasos numerados.
- **404:** tarjeta centrada de 560px con el ícono en círculo azul tenue, "404" en letra de datos, el mensaje y dos salidas ("Ir al inicio" y "Ver historial").

### Mapa (Leaflet + OpenStreetMap)
- Teselas estándar de OSM con su atribución visible.
- **Punto de referencia:** círculo azul UACJ de 14px con contorno blanco de 2px. El seleccionado crece a 20px, en amarillo con contorno negro.
- **Campus:** la placa de campus como marcador (`divIcon`), igual que en la tarjeta.
- **Radio de búsqueda:** círculo con contorno azul UACJ de 2px y relleno azul al 8%.
- Los controles de zoom miden 48px y llevan el foco del sistema.

### Avisos y estados vacíos
- **Notificaciones** (`q-notify`): éxito en verde con texto blanco, error en rojo con texto blanco y advertencia en amarillo con texto negro. Siempre con ícono y en la parte inferior, por encima de la barra de navegación.
- **Estado vacío:** un ícono de 48px en gris, una frase en Body que dice qué pasa ("No hay raites cerca de Oxxo Dunas a esa hora") y la acción para salir de ahí ("Ampliar a 5 km"). Nunca una pantalla en blanco.
- **Carga:** `q-skeleton` con la forma de la tarjeta de viaje, no spinners de página completa.

### Superficies del navegador
- Selección de texto: fondo amarillo UACJ con texto negro.
- Cursor de texto (`caret-color`): azul UACJ.
- Barra de desplazamiento: delgada, en gris UACJ sobre fondo.
- Números: `font-variant-numeric: tabular-nums` en horas, contadores y calificaciones.

### Movimiento
Se usan las transiciones de Quasar con 200ms y salida suave. El único momento propio es cuando una solicitud pasa a Aceptada: el chip cambia de amarillo tenue a verde y el bloque de contacto se despliega hacia abajo en 240ms. Con `prefers-reduced-motion` se quitan las transiciones y los desplazamientos; solo los indicadores de carga siguen girando, para que no parezca que la app se trabó.

## Do's and Don'ts

### Do:
- **Do** usar el azul UACJ para el encabezado, la barra inferior y la única acción principal de cada pantalla.
- **Do** poner el amarillo sobre azul o con texto negro encima (11.54:1).
- **Do** revisar cada combinación nueva de texto y fondo contra la tabla de contraste; si no está, calcularla y agregarla aquí antes de usarla.
- **Do** acompañar cada estado con ícono y palabra, además del color.
- **Do** usar Atkinson Hyperlegible Mono para horas, placas, teléfono y código.
- **Do** mantener texto de 16px como base y 14px como mínimo absoluto.
- **Do** usar `q-card` o `.raite-tarjeta` (blancas con sombra suave) y los componentes estándar de Quasar.
- **Do** probar cada pantalla a 375px de ancho y a 1280px, que es como se hará la demo.

### Don't:
- **Don't** poner texto amarillo, bordes amarillos ni íconos amarillos sobre blanco o sobre la página (1.41:1).
- **Don't** usar el escudo, el logotipo ni la tipografía oficial de la UACJ.
- **Don't** usar `#000` ni grises fuera de la paleta para el texto.
- **Don't** escribir en MAYÚSCULAS botones, pestañas ni títulos.
- **Don't** usar sombras fuera del vocabulario de Elevation, ni tarjetas dentro de tarjetas.
- **Don't** usar bordes laterales de color en tarjetas o avisos.
- **Don't** usar el botón de acento amarillo sobre fondo blanco.
- **Don't** mostrar teléfono ni placas antes de que la solicitud esté aceptada.
- **Don't** usar emojis como íconos; los íconos son de Material Icons, que ya viene con Quasar, con un solo estilo.
- **Don't** activar el modo oscuro de Quasar: no está diseñado todavía.

## Aplicación como tema de Quasar

Aplicado en `Front_Raite/src/css/quasar.variables.scss` y `Front_Raite/src/css/app.scss`. Los nombres de las variables se comprobaron contra Quasar 2.30.

**Colores de marca** (`src/css/quasar.variables.scss`):

| Variable de Quasar | Valor | Nota |
|---|---|---|
| `$primary` | #003CA6 | Azul UACJ |
| `$secondary` | #555559 | Gris UACJ, para botones neutros |
| `$accent` | #FFD600 | Amarillo UACJ; siempre con `text-color="dark"` |
| `$dark` | #231F20 | Negro UACJ; también lo usan `text-dark` y `bg-dark` |
| `$dark-page` | #231F20 | Sin uso mientras no haya modo oscuro |
| `$positive` | #1E6B34 | Verde |
| `$negative` | #B3261E | Rojo |
| `$info` | #002C7A | Azul hondo |
| `$warning` | #FFD600 | Amarillo; siempre con texto negro |

**Tonos derivados:** variables CSS en `src/css/app.scss` (`--raite-azul-hondo`, `--raite-azul-tenue`, `--raite-fondo`, etc.) con sus clases `.bg-*` y `.text-*` (por ejemplo `bg-azul-tenue text-primary`).

**Tipografía y forma:**
- `$typography-font-family`: Atkinson Hyperlegible Next.
- `$body-font-size: 16px`. Mapas `$h4` (Headline en escritorio), `$h5` (Headline), `$h6` (Title), `$subtitle1`, `$subtitle2`, `$body1` (Body), `$body2` y `$caption` (Label). Ninguno baja de 14px.
- `$generic-border-radius: 12px` y `$button-border-radius: 12px`.
- `$button-font-weight: 700`, `$button-font-size: 16px`, `$button-padding: 0 24px` y `$button-shadow: none`. Quasar no tiene variable para quitar las mayúsculas: lo hace una regla de `app.scss` sobre `.q-btn` y `.q-tab`.
- `$space-base: 16px` (es el valor por defecto; se deja así).
- Los puntos de corte de Quasar (`sm` 600, `md` 1024, `lg` 1440) coinciden con los de Layout; no se cambian.

**Valores por defecto de componentes:** `q-card` con `flat bordered`, `q-input` y `q-select` con `outlined` y la etiqueta fuera del campo, y `q-tabs` con `indicator-color="accent"` y `no-caps`. Donde Quasar no tenga una variable, se agrega una regla en `app.scss`; nunca se sustituye el componente.

**Idioma:** `framework.lang: 'es'` en `quasar.config.ts` para que fechas, `q-date` y `q-time` salgan en español.
