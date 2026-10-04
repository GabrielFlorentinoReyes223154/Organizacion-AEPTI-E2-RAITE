### **MAPAS, GEOCODIFICACIÓN Y RASTREO EN VIVO**

Esta sección recoge la implementación técnica de los mapas, la geocodificación del catálogo de puntos y el seguimiento GPS en tiempo real durante los viajes activos.

> Negocios permitidos: (walmart, s-mart, sams, soriana, oxxo, aurrerá, superette, del río, extra, circle k)

#### **Poblado de la Base de Datos (Catálogo de Puntos)**

De acuerdo a la arquitectura, los puntos de Raite son estáticos y provienen de un catálogo cerrado. Se utilizará **Overpass Turbo** para la extracción inicial y un script *seed* para llenar la tabla `PuntoMapeado`.

##### **Consulta en Overpass Turbo**
Ve a [overpass-turbo.eu](https://overpass-turbo.eu/) y ejecuta la siguiente consulta. Este ejemplo extrae todos los "Oxxo" en Ciudad Juárez. (Deberás repetir o agrupar la consulta para Walmart, S-Mart, etc.).

```text
[out:json][timeout:25];

// 1. Definir el estado de Chihuahua para acotar la búsqueda
area["name"="Chihuahua"]["admin_level"="4"]->.estado;

// 2. Definir el municipio de Juárez dentro de ese estado
area["name"="Juárez"]["admin_level"="6"](area.estado)->.searchArea;

(
  // Buscar por marca (etiqueta oficial)
  node["brand"~"OXXO", i](area.searchArea);
  way["brand"~"OXXO", i](area.searchArea);
  
  // Buscar por nombre (como respaldo)
  node["name"~"OXXO", i](area.searchArea);
  way["name"~"OXXO", i](area.searchArea);
);

out center;
```

##### **Procesamiento y Seed (Migración)**
Exporta el resultado como **JSON**. El JSON resultante tendrá una estructura con elementos (`elements`). Debes iterar sobre ellos en tu script de backend (ej. Django/Node) para llenar la base de datos.

**Lógica del Seed:**
1. Iterar sobre `elements` del JSON.
2. Si es tipo `node`, usar `lat` y `lon`. Si es tipo `way`, usar `center.lat` y `center.lon`.
3. **Resolución de colisiones:** Como `nombre_punto` debe ser único, debes concatenar la calle o colonia (que a menudo viene en el objeto `tags` de Overpass) para diferenciar sucursales. Ej: `tags.name + " - " + tags['addr:street']` -> *"Oxxo - Avenida Tecnológico"*.
4. Insertar en `PuntoMapeado` con `activo = true`.

---