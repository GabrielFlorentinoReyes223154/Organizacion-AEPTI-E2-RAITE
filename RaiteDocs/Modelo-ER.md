# Modelo entidad-relación (Capa 1)

> Refleja los modelos implementados en `Back_Raite/apps/` (Capa 1, noviembre 2026).
> **Sustituye** a `uml_mermaid_raite.mmd`, `uml_diagram.mmd` y `Raite-Django-Models.md` donde se contradigan:
> esos documentos describen el diseño anterior (el pasajero creaba el raite y el conductor lo "tomaba").
> Aquí el conductor publica el viaje y los pasajeros solicitan lugar, como dicen el SRS y la carta.

## Diagrama

```mermaid
erDiagram
    USUARIO ||--o| VEHICULO : "tiene"
    USUARIO ||--o{ CODIGO_VERIFICACION : "recibe"
    USUARIO ||--o{ VIAJE : "conduce"
    VEHICULO ||--o{ VIAJE : "se usa en"
    PUNTO_REFERENCIA ||--o{ VIAJE : "origen / destino"
    CAMPUS ||--o{ VIAJE : "destino / origen"
    VIAJE ||--o{ SOLICITUD : "recibe"
    USUARIO ||--o{ SOLICITUD : "pide lugar"
    USUARIO ||--o{ NOTIFICACION : "recibe"
    VIAJE |o--o{ NOTIFICACION : "sobre"
    VIAJE ||--o{ CALIFICACION : "se califica en"
    USUARIO ||--o{ CALIFICACION : "autor / calificado"
    VIAJE ||--o{ REPORTE : "ocurre en"
    USUARIO ||--o{ REPORTE : "reportante / reportado / resuelto_por"

    USUARIO {
        uuid id PK
        string correo UK "solo @alumnos.uacj.mx (salvo ADMIN)"
        string nombre
        string apellidos
        int edad "17 a 70"
        string sexo "M, F, X"
        string carrera
        string telefono "10 dígitos; visible solo con raite confirmado"
        string preferencia_compatibilidad "MISMO_SEXO, MIXTO"
        int rol "1 ADMIN, 2 PASAJERO, 3 CONDUCTOR, 4 AMBOS"
        decimal calificacion "promedio 0.00 a 5.00"
        bool correo_verificado
        bool suspendido
        bool is_active
    }
    VEHICULO {
        uuid id PK
        uuid usuario_id FK "1 a 1"
        string marca
        string modelo
        string color
        string placas UK "visibles solo con raite confirmado"
        string tipo "COCHE, CAMIONETA, TROCA"
        int asientos_disponibles "1 a 5"
        bool activo
    }
    CODIGO_VERIFICACION {
        int id PK
        uuid usuario_id FK
        string codigo_hash "6 dígitos con hash"
        datetime expira_en
        int intentos
        bool usado
    }
    CAMPUS {
        int id PK
        string codigo UK "CU, IIT, ICB, ICSA, IADA"
        string nombre
        decimal latitud "dentro de Cd. Juárez"
        decimal longitud
        bool activo
    }
    PUNTO_REFERENCIA {
        int id PK
        string nombre "ej. Oxxo – Av. X, Col. Y"
        decimal latitud "dentro de Cd. Juárez"
        decimal longitud
        string osm_id UK "opcional"
        bool activo
    }
    VIAJE {
        uuid id PK
        uuid conductor_id FK
        uuid vehiculo_id FK
        int punto_referencia_id FK
        int campus_id FK
        string sentido "HACIA_CAMPUS, DESDE_CAMPUS"
        datetime fecha_hora
        int lugares_ofrecidos "1 a 5, sin superar asientos"
        string preferencia_compatibilidad "MISMO_SEXO, MIXTO"
        text notas "máx. 300"
        string estado "ver diagrama de estados"
    }
    SOLICITUD {
        uuid id PK
        uuid viaje_id FK
        uuid pasajero_id FK
        string preferencia_compatibilidad "MISMO_SEXO, MIXTO"
        string estado "ver diagrama de estados"
        datetime respondida_en
    }
    NOTIFICACION {
        uuid id PK
        uuid usuario_id FK
        string tipo
        string mensaje "máx. 255"
        uuid viaje_id FK "opcional"
        bool leida
    }
    CALIFICACION {
        uuid id PK
        uuid viaje_id FK
        uuid autor_id FK
        uuid calificado_id FK
        int puntuacion "1 a 5"
        text comentario "máx. 500"
    }
    REPORTE {
        uuid id PK
        uuid viaje_id FK
        uuid reportante_id FK
        uuid reportado_id FK
        text motivo "máx. 1000"
        string estado "PENDIENTE, RESUELTO, DESCARTADO"
        text notas_admin
        uuid resuelto_por_id FK
    }
```

## Estados del viaje

```mermaid
stateDiagram-v2
    [*] --> PUBLICADO
    PUBLICADO --> EN_CURSO : el conductor inicia
    PUBLICADO --> CANCELADO : el conductor cancela
    EN_CURSO --> FINALIZADO : el conductor finaliza
    FINALIZADO --> [*]
    CANCELADO --> [*]
```

"Lleno" no es un estado: un viaje está lleno cuando sus solicitudes aceptadas igualan `lugares_ofrecidos`.

"Vencido" tampoco es un estado: un viaje `PUBLICADO` cuya hora pasó hace más de 2 h (`VENCIMIENTO_HORAS`) se considera vencido. Solo se puede cancelar, no aparece en búsquedas y no cuenta para cruces de horario. Iniciar solo se permite desde 30 min antes de la hora (`INICIO_ANTICIPACION_MINUTOS`).

## Estados de la solicitud

```mermaid
stateDiagram-v2
    [*] --> PENDIENTE
    PENDIENTE --> ACEPTADA : el conductor acepta
    PENDIENTE --> RECHAZADA : el conductor rechaza
    PENDIENTE --> CANCELADA : el pasajero cancela o se cancela el viaje
    ACEPTADA --> CANCELADA : el pasajero cancela o se cancela el viaje
    RECHAZADA --> [*]
    CANCELADA --> [*]
```

- Si el conductor no responde, la solicitud sigue `PENDIENTE`.
- Un pasajero solo puede tener una solicitud `PENDIENTE` o `ACEPTADA` por viaje; tras un rechazo o cancelación puede volver a solicitar.

## Reglas que viven en el modelo (Capa 1)

| Regla | Dónde |
|-------|-------|
| Correo `@alumnos.uacj.mx` (el ADMIN queda exento) | `Usuario.clean()` |
| Teléfono de 10 dígitos | validador de `Usuario.telefono` |
| Asientos del vehículo y lugares del viaje: 1 a 5 | validadores + `CheckConstraint` |
| Lugares del viaje ≤ asientos del vehículo; vehículo del conductor y activo | `Viaje.clean()` |
| Viaje nuevo: fecha futura, punto y campus activos | `Viaje.clean()` |
| Coordenadas dentro de Ciudad Juárez | validadores de `latitud` / `longitud` |
| El conductor no solicita lugar en su propio viaje | `Solicitud.clean()` |
| Una solicitud activa por viaje y pasajero | `UniqueConstraint` parcial |
| Calificar solo viajes finalizados, solo conductor ↔ pasajero aceptado, una vez | `Calificacion.clean()` + restricciones |
| Reportar solo entre participantes del viaje | `Reporte.clean()` |

Las reglas de negocio que dependen de varios registros se aplican en la Capa 2 (`services.py` de cada app; ver `RaiteDocs/API.md`):
compatibilidad por sexo, cupo al aceptar, visibilidad de contacto y placas, quién puede cambiar cada estado,
envío del código de verificación y recálculo de `Usuario.calificacion`.
