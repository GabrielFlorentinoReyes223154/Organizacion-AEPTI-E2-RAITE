# **Raite - Especificación Técnica: Mapas, Geocodificación y Rastreo en Vivo**

Este documento detalla la implementación técnica para la gestión de puntos de encuentro (catálogo estático) y el seguimiento GPS en tiempo real durante los viajes activos en la plataforma Raite.

---

## **1. Poblado de la Base de Datos (Catálogo de Puntos)**

De acuerdo a la arquitectura, los puntos de Raite son estáticos y provienen de un catálogo cerrado. Se utilizará **Overpass Turbo** para la extracción inicial y un script *seed* para llenar la tabla `PuntoMapeado`.

### **1.1. Consulta en Overpass Turbo**
Ve a [overpass-turbo.eu](https://overpass-turbo.eu/) y ejecuta la siguiente consulta. Este ejemplo extrae todos los "Oxxo" en Ciudad Juárez. (Deberás repetir o agrupar la consulta para Walmart, S-Mart, etc.).

```text
[out:json][timeout:25];
// Definir el área de búsqueda (Ciudad Juárez)
area["name"="Ciudad Juárez"]->.searchArea;
(
  // Buscar nodos (puntos simples)
  node["name"~"Oxxo", i](area.searchArea);
  // Buscar vías/polígonos (edificios)
  way["name"~"Oxxo", i](area.searchArea);
);
// 'out center' convierte los polígonos en un solo punto central (lat/lon)
out center;
```

### **1.2. Procesamiento y Seed (Migración)**
Exporta el resultado como **JSON**. El JSON resultante tendrá una estructura con elementos (`elements`). Debes iterar sobre ellos en tu script de backend (ej. Django/Node) para llenar la base de datos.

**Lógica del Seed:**
1. Iterar sobre `elements` del JSON.
2. Si es tipo `node`, usar `lat` y `lon`. Si es tipo `way`, usar `center.lat` y `center.lon`.
3. **Resolución de colisiones:** Como `nombre_punto` debe ser único, debes concatenar la calle o colonia (que a menudo viene en el objeto `tags` de Overpass) para diferenciar sucursales. Ej: `tags.name + " - " + tags['addr:street']` -> *"Oxxo - Avenida Tecnológico"*.
4. Insertar en `PuntoMapeado` con `activo = true`.

---

## **2. Uso de Leaflet y Seguimiento Live (GPS)**

El rastreo en vivo se usa una vez que el Raite pasa a estado `ACEPTADO`. Se requiere la API de Geolocalización de HTML5 en el frontend y WebSockets para compartir la ubicación.

### **2.1. Renderizado Básico con Leaflet**
Para mostrar el catálogo o los viajes pendientes:

```javascript
// Inicializar mapa centrado en CU / Ciudad Juárez
const map = L.map('mapa').setView([31.6904, -106.4245], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Agregar un punto estático de la BD
const marcadorOxxo = L.marker([latBD, lonBD]).addTo(map);
marcadorOxxo.bindPopup("Oxxo - Tecnológico (2 esperando)");
```

### **2.2. Seguimiento Live GPS del Dispositivo**
Lógica exclusiva para el **Conductor** (para emitir) y el **Pasajero** (para recibir).

```javascript
let marcadorConductor;
let watchId;

// INICIAR RASTREO (Se ejecuta en el celular del Conductor)
function iniciarRastreo(raiteId) {
    if (!navigator.geolocation) return alert("GPS no soportado");

    watchId = navigator.geolocation.watchPosition(
        (position) => {
            const { latitude, longitude } = position.coords;
            
            // 1. Actualizar Leaflet localmente
            if (!marcadorConductor) {
                marcadorConductor = L.marker([latitude, longitude]).addTo(map);
            } else {
                marcadorConductor.setLatLng([latitude, longitude]);
            }
            map.setView([latitude, longitude]); // Centrar mapa

            // 2. Enviar por WebSocket al backend
            socket.send(JSON.stringify({
                tipo: 'ubicacion_conductor',
                raite_id: raiteId,
                lat: latitude,
                lon: longitude
            }));
        },
        (error) => console.error("Error GPS:", error),
        { enableHighAccuracy: true, maximumAge: 0 }
    );
}

// DETENER RASTREO (Al llegar al destino o finalizar)
function detenerRastreo() {
    if (watchId) navigator.geolocation.clearWatch(watchId);
}
```

---

## **3. Actualizaciones al Diagrama de Clases UML**

Para soportar el rastreo en vivo sin sobrecargar la base de datos relacional (no debes guardar cada coordenada en SQL por segundo), debes modelar una interfaz de **WebSocket/Caché**. 

**Agrega estas clases y métodos a tu UML existente:**

### **Nuevos Atributos en `Raite`**
*   No agregues `lat/lon` actual a la tabla `Raite` si cambia cada segundo. Usa la base de datos solo para persistir estados.

### **Nueva Clase Transitoria (WebSocket Manager / Redis)**
Añade una clase `GestorUbicacionLive` (representa el canal WebSocket/Caché) con estereotipo `<<Transient>>` o `<<Service>>`.

```plantuml
class GestorUbicacionLive <<Service>> {
  + conectar_cliente(usuario_id, raite_id)
  + actualizar_ubicacion(raite_id, conductor_id, latitud, longitud)
  + notificar_pasajero(raite_id, latitud, longitud)
  + desconectar_cliente(usuario_id)
}
```

### **Nuevos Métodos en el Frontend (App/UI)**
Si tu UML modela la aplicación cliente, agrega:
```plantuml
class AppMovil {
  + watch_id: Integer
  + iniciar_rastreo_gps(raite_id): void
  + detener_rastreo_gps(): void
  + actualizar_mapa_leaflet(latitud, longitud): void
}
```

### **Relaciones a Agregar en el UML:**
*   `GestorUbicacionLive` ---> `Raite` : Lee estado (valida que esté `ACEPTADO` y `EN_CURSO`)
*   `AppMovil` ---> `GestorUbicacionLive` : Emite/Escucha eventos por WebSocket
*   `AppMovil` ---> `PuntoMapeado` : Renderiza marcadores estáticos en Leaflet