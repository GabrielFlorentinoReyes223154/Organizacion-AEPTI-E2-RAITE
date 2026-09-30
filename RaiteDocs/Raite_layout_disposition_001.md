# **Raite - Documento de Layout y Disposición (Mejorado)**

---

## **FLUJOS DE USUARIO**

### **Autenticación**
| Pantalla | Campos | Notas |
|----------|--------|-------|
| **Login** | Correo, Contraseña | Autenticación estándar |
| **Registro - Paso 1** | Nombre completo, Correo, Contraseña, **Rol(es)** | Usuario elige: **Pasajero**, **Conductor**, o **Ambos** |
| **Registro - Paso 2 (Condicional)** | **Datos del Vehículo** | **Solo si elige "Conductor" o "Ambos"** |

> **Campos del Vehículo (Paso 2):**
> - Marca
> - Modelo
> - Color
> - Placas
> - Tipo de vehículo: `Camioneta` / `Coche` / `Troca`
> - Número de asientos disponibles para pasajeros

> **Reglas de negocio:**
> - Los pasajeros solo ven la placa del conductor **después de aceptar** el viaje
> - **Entrada**: Recogida = Punto del sistema (seleccionable), Destino = **CU** (fijo)
> - **Salida**: Recogida = **CU** (fijo), Destino = Punto del sistema (seleccionable)
> - Usuario con ambos roles ve ambas interfaces (Home cambia según rol activo)
> - Perfil de conductor **requiere vehículo válido** para activar modo "Dar Raite"

---

### **PANTALLA HOME**

#### **Panel 1 - Selección de Viaje y Rol Activo**
| Elemento | Tipo | Opciones | Notas |
|----------|------|----------|-------|
| Tipo de viaje | Radio/Select | `Entrada` (a la escuela) / `Salida` (de la escuela) | Requerido |
| **Rol activo** | Toggle / Segmented Control | `Pasajero` / `Conductor` | **Solo si usuario tiene ambos roles**; si solo tiene uno, se oculta y usa ese rol |

---

#### **Panel 2 - Tarjetas de Estado Dinámico**

| Estado | Disparador | Datos mostrados |
|--------|------------|-----------------|
| **🟢 "¡Hola! Solicita un raite"** | Pasajero sin solicitud activa | Estado vacío con CTA a "Pedir Raite" |
| **🔵 "¡Han solicitado ser tu raite!"** | Conductor recibe solicitud | **Datos del Conductor** + **Datos del Viaje** (ver abajo) |
| **🟡 "¡Han aceptado tu raite!"** | Solicitud del pasajero aceptada | **Datos del Pasajero** + **Datos del Viaje** |
| **🟣 "¡Tienes un raite programado!"** | Viaje confirmado (ambas partes) | **Datos del Contraparte** + **Datos del Viaje** |

---

#### **Estructuras de Datos**

**Perfil de Conductor:**
- Nombre, Edad, Sexo, Carrera
- Calificación (★ 1-5)
- **Vehículo:**
  - Marca, Modelo, Color, Placas
  - Tipo: `Camioneta` / `Coche` / `Troca`
  - Asientos disponibles para pasajeros
- Preferencias de viaje
- **`activo` (bool):** `true` si tiene un Raite en curso (aceptado y no finalizado)

**Perfil de Pasajero:**
- Nombre, Edad, Sexo, Carrera
- Calificación (★ 1-5)
- Preferencias de viaje
- **`activo` (bool):** `true` si tiene un Raite en curso (creado/aceptado y no finalizado)

**Raite:**
- `pasajero_id` (FK)
- `conductor_id` (FK, nullable hasta aceptación)
- `tipo`: `Entrada` / `Salida`
- **Entrada**: `punto_recogida` (sistema) → `punto_destino` = **CU** (fijo)
- **Salida**: `punto_recogida` = **CU** (fijo) → `punto_destino` (sistema)
- `hora_objetivo` (time, solo horas enteras: 07:00–22:00)
  - **Entrada**: hora de **llegada a CU** (deadline)
  - **Salida**: hora de **salida de CU** (cuándo parten)
- `configuracion`: mismo sexo, usar cajuela, mascotas, etc.
- **Estados (bool):**
  - `activo`: `true` al crear, `false` si expira por hora o se finaliza
  - `aceptado`: `false` inicial, `true` cuando conductor acepta
  - `finalizado`: `false` inicial, `true` tras encuesta **ambos**
- `created_at`, `updated_at`

> **Regla de expiración (Entrada):** Si `hora_objetivo` (llegada a CU) pasa y `aceptado=false` → `activo=false`
> 
> **Regla de expiración (Salida):** Si `hora_objetivo` (salida de CU) pasa y `aceptado=false` → `activo=false`
>
> **Finalización obligatoria:** Encuesta persistente (reintenta si offline). Ambos deben responder `sí` → `finalizado=true`, `activo=false`, libera `activo` en ambos perfiles.
>
> *Placas visibles solo tras `aceptado=true`*

---

### **PEDIR RAITE (Pasajero) — Crea un RAITE**

| Paso | Componente | Descripción |
|------|------------|-------------|
| 1 | **Vista de Mapa** (panel derecho) | **Entrada**: Seleccionar punto de **recogida** del sistema<br>**Salida**: Seleccionar punto de **destino** del sistema (recogida fija en CU) |
| 2 | **Botón "Dar Raite"** | Crea el **Raite** con: `hora_objetivo` (time, horas enteras), `tipo`, `punto_origen`, `punto_destino`, `configuracion`<br>**Atributos del Raite:** `aceptado` (bool), `finalizado` (bool), `activo` (bool) |
| 3 | **Panel de Detalle del Punto** (panel izquierdo) | Muestra info del punto, conductores cercanos, ETA |

> **Ciclo de vida del Raite:**
> - `activo=true` al crearse
> - **Entrada**: Si nadie acepta antes de `hora_objetivo` (llegada a CU) → `activo=false`
> - **Salida**: Si nadie acepta antes de `hora_objetivo` (salida de CU) → `activo=false`
> - Si conductor acepta → `aceptado=true`, se notifica a pasajero
> - **Finalización:** Ambos (pasajero + conductor) responden encuesta obligatoria y persistente → `finalizado=true`
> - **Bloqueo:** Usuario con `activo=true` en cualquier Raite **no puede** crear/aceptar otro (maneja desconexiones)

---

### **DAR RAITE (Conductor)**

| Paso | Componente | Descripción |
|------|------------|-------------|
| 1 | **Vista de Mapa** (panel derecho) | **Entrada**: Puntos con raites de **recogida** activos<br>**Salida**: Puntos con raites de **destino** activos (recogida en CU) |
| 2 | **Botón Aceptar** | Setea `aceptado=true` en el Raite, notifica al pasajero, vincula conductor al Raite |

> **Validación previa:** Conductor debe tener `activo=false` (no tener raite en curso) y vehículo válido

---

## **PANEL DE ADMINISTRACIÓN**

| Sección | Funcionalidades |
|---------|-----------------|
| **Usuarios** | Listar todos / filtrar por rol (Pasajero/Conductor/Admin), búsqueda, paginación |
| **Puntos de Raite** | CRUD + filtrar por zona, demanda, estado |
| **Raites Pedidos** | Filtrar por fecha, estado, usuario, punto |
| **Raites Programados** | Igual que anterior + distinción por atributo `status=confirmado` |
| **Vehículos** | CRUD + filtrar por tipo, capacidad, conductor |

---

## **NOTAS TÉCNICAS / PENDIENTES**

- [ ] **Integración Leaflet**: ¿Cómo se almacenan los Puntos? ¿POIs pre-mapeados (centros comerciales, tiendas)?
- [ ] **Guardias de Autenticación**: Protección de rutas por rol (Pasajero vs Conductor vs Admin)
- [ ] **Django Admin**: Personalizar admin por defecto para modelos de Raite
- [ ] **Diagrama UML**: Generar desde esta especificación (Clases, Secuencia, Estados)
- [ ] **Tiempo Real**: Estrategia WebSocket para solicitudes/actualizaciones de viajes
- [ ] **Notificaciones**: Push + in-app para cambios de estado de viaje

---

## **MEJORAS UI/UX (Sugeridas)**

1. **Skeleton Loaders** para mapa y paneles de datos
2. **Estados Vacíos** con ilustraciones para cada estado del panel
3. **Notificaciones Toast** para actualizaciones de viaje (solicitado, aceptado, cancelado)
4. **Bottom Sheet** para detalles de viaje en móvil (en lugar de panel lateral)
5. **Seguimiento ETA Conductor** en vivo en pantalla "Tienes un raite programado"
6. **Modal de Calificación** post-viaje (ambas partes)

---

*Generado desde `Raite_layout_disposition.md` — Original conservado*

---

## **DIAGRAMAS UML**

### **1. Diagrama de Clases**

```plantuml
@startuml
skinparam classAttributeIconSize 0

enum Rol {
  PASAJERO
  CONDUCTOR
  AMBOS
  ADMIN
}

enum TipoViaje {
  ENTRADA
  SALIDA
}

enum TipoVehiculo {
  CAMIONETA
  COCHE
  TROCA
}

class Usuario {
  + id: UUID
  + nombre: String
  + apellidos: String
  + correo: String (unique)
  + password_hash: String
  + rol: Rol
  + edad: Integer
  + sexo: String
  + carrera: String
  + calificacion: Float (1-5)
  + activo: Boolean
  + created_at: DateTime
  + updated_at: DateTime
  + puede_crear_raite(): Boolean
  + puede_aceptar_raite(): Boolean
}

class Vehiculo {
  + id: UUID
  + usuario_id: UUID (FK)
  + marca: String
  + modelo: String
  + color: String
  + placas: String (unique)
  + tipo: TipoVehiculo
  + asientos_disponibles: Integer
  + created_at: DateTime
}

class PuntoMapeado {
  + id: UUID
  + nombre_punto: String
  + latitud: Float
  + longitud: Float
  + activo: Boolean
}

class Raite {
  + id: UUID
  + pasajero_id: UUID (FK)
  + conductor_id: UUID (FK, nullable)
  + tipo: TipoViaje
  + punto_origen_id: UUID (FK)
  + punto_destino_id: UUID (FK)
  + hora_objetivo: Time  -- solo horas enteras (07:00–22:00)
  + configuracion: JSON
  + activo: Boolean
  + aceptado: Boolean
  + finalizado: Boolean
  + created_at: DateTime
  + updated_at: DateTime
  + expirar_si_pasado_hora(): void
  + aceptar(conductor_id): void
  + finalizar(encuesta_pasajero, encuesta_conductor): void
}

class EncuestaFinalizacion {
  + id: UUID
  + raite_id: UUID (FK)
  + usuario_id: UUID (FK)
  + respondio: Boolean?  -- null=pendiente, true=sí, false=no
  + respondio_en: DateTime?
  + reintentos: Integer
}

class Notificacion {
  + id: UUID
  + usuario_id: UUID (FK)
  + tipo: String (raite_creado, raite_aceptado, raite_finalizado, etc.)
  + titulo: String
  + mensaje: String
  + leida: Boolean
  + created_at: DateTime
}

Usuario "1" -- "0..1" Vehiculo : tiene >
Usuario "1" -- "*" Raite : como_pasajero >
Usuario "1" -- "*" Raite : como_conductor >
Usuario "1" -- "*" Notificacion : recibe >
Raite "1" -- "1" PuntoMapeado : origen >
Raite "1" -- "1" PuntoMapeado : destino >
Raite "1" -- "*" EncuestaFinalizacion : genera >
EncuestaFinalizacion "2" -- "1" Raite : requiere_ambos >

note right of Usuario::activo
  true = tiene Raite en curso
  (activo=true Y finalizado=false)
  Bloquea crear/aceptar nuevo
end note

note right of Raite::activo
  true al crear
  false si expira hora_objetivo sin aceptar
  false al finalizar (encuesta ambos)
end note

@enduml
```

---

### **2. Diagrama de Estados del Raite**

```plantuml
@startuml
[*] --> CREADO : Pasajero crea Raite
CREADO : activo=true\naceptado=false\nfinalizado=false

CREADO --> EXPIRADO : hora_objetivo pasa\nY aceptado=false
CREADO --> ACEPTADO : Conductor acepta\n(setea conductor_id, aceptado=true)

EXPIRADO : activo=false\n(terminal)

ACEPTADO : activo=true\naceptado=true\nfinalizado=false
ACEPTADO --> EN_CURSO : Notificación a pasajero

EN_CURSO : Viaje en progreso
EN_CURSO --> ENCUESTA_PENDIENTE : Llegada a destino\ndetectada (GPS/hora)

ENCUESTA_PENDIENTE : Encuesta enviada a ambos\n(reintentos si offline)
ENCUESTA_PENDIENTE --> FINALIZADO : Ambos responden SÍ
ENCUESTA_PENDIENTE --> ENCUESTA_PENDIENTE : Reintento\n(persistente hasta ambos SÍ)

FINALIZADO : activo=false\nfinalizado=true\nLibera Usuario.activo=false
FINALIZADO --> [*]

note right of CREADO
  Expira por hora_objetivo (time, horas enteras)
  Entrada = llegada a CU | Salida = salida de CU
  NO por 24 horas fijas
end note

note right of ENCUESTA_PENDIENTE
  Persistente y obligatoria
  Maneja desconexiones
  Bloquea nuevos raites hasta completar
end note

@enduml
```

---

### **3. Diagrama de Secuencia: Crear y Aceptar Raite**

```plantuml
@startuml
actor Pasajero
actor Conductor
participant "App Móvil" as App
participant "Backend API" as API
participant "DB" as DB
participant "WebSocket" as WS

== Crear Raite (Pasajero) ==
Pasajero -> App: Selecciona tipo (Entrada/Salida)
Pasajero -> App: Selecciona punto (origen/destino según tipo)
Pasajero -> App: Configura preferencias
Pasajero -> App: Pulsa "Crear Raite"
App -> API: POST /raites {tipo, punto_origen, punto_destino, hora_objetivo, config}
API -> DB: INSERT Raite (activo=true, aceptado=false, finalizado=false)
API -> DB: UPDATE Usuario SET activo=true WHERE id=pasajero_id
API --> App: 201 Created {raite_id}
App --> Pasajero: Muestra "Raite creado, esperando conductor"

== Buscar/Aceptar Raite (Conductor) ==
Conductor -> App: Abre "Dar Raite" (valida Usuario.activo=false y Vehiculo existe)
App -> API: GET /raites?activo=true&tipo=...&punto=...
API -> DB: SELECT * FROM Raite WHERE activo=true AND aceptado=false
API --> App: Lista raites disponibles
App --> Conductor: Mapa con puntos con raites pendientes
Conductor -> App: Selecciona punto -> Pulsa "Aceptar"
App -> API: POST /raites/{id}/aceptar {conductor_id}
API -> DB: UPDATE Raite SET conductor_id=?, aceptado=true WHERE id=? AND activo=true
API -> DB: UPDATE Usuario SET activo=true WHERE id=conductor_id
API -> WS: Push notificación a pasajero ("Tu raite fue aceptado")
WS --> Pasajero: Notificación en tiempo real
API --> App: 200 OK {raite_actualizado}
App --> Conductor: Muestra datos del pasajero y viaje

== Finalización (Ambos) ==
Note over Pasajero, Conductor: Llegada a destino (GPS/hora estimada)
API -> WS: Push a ambos "Encuesta de finalización"
WS --> Pasajero: Modal encuesta "¿Llegaste bien?"
WS --> Conductor: Modal encuesta "¿Pasajero llegó bien?"
Pasajero -> App: Responde SÍ
Conductor -> App: Responde SÍ
App -> API: POST /raites/{id}/encuesta {usuario_id, respondio=true}
API -> DB: INSERT EncuestaFinalizacion
API -> DB: CHECK ambos_respondieron
API -> DB: UPDATE Raite SET finalizado=true, activo=false
API -> DB: UPDATE Usuario SET activo=false WHERE id IN (pasajero_id, conductor_id)
API -> WS: Push "Raite finalizado" a ambos
@enduml
```

---

### **4. Diagrama de Secuencia: Expiración por Tiempo**

```plantuml
@startuml
actor "Scheduler/Cron" as Cron
participant "Backend API" as API
participant "DB" as DB
participant "WebSocket" as WS
actor Pasajero

Cron -> API: Cada 5 min: GET /raites/expirados
API -> DB: SELECT * FROM Raite WHERE activo=true AND aceptado=false AND hora_objetivo < CURRENT_TIME
DB --> API: Lista raites expirados
loop Para cada raite expirado
  API -> DB: UPDATE Raite SET activo=false WHERE id=?
  API -> DB: UPDATE Usuario SET activo=false WHERE id=pasajero_id
  API -> WS: Push "Raite expirado" a pasajero
  WS --> Pasajero: Notificación "Ningún conductor aceptó a tiempo"
end
@enduml
```

---

*Documento completo con UML generado. Original en `Raite_layout_disposition.md` conservado.*