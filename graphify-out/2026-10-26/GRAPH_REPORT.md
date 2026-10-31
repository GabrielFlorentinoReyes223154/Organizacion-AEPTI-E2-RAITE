# Graph Report - Raite  (2026-10-26)

## Corpus Check
- 87 files · ~66,658 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 16 file(s) not represented in the graph (top: .ico 7, (none) 4, .scss 2)

## Summary
- 745 nodes · 969 edges · 63 communities (40 shown, 23 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 176 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6d6de68c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- LoginPage.vue
- Vehiculo
- package.json
- 1. BACKEND
- Raite — API REST y Tiempo Real
- Stack Tecnológico por Capa
- Infraestructura, CI/CD y Observabilidad
- paths
- SignUpPage.vue
- **Raite - Documento de Layout y Disposición (Mejorado)**
- Plan: JWT Auth Completo (Frontend + Backend Gaps)
- devDependencies
- Arquitectura del Sistema Raite
- Raite — Modelos de Dominio
- 0001_initial.py
- Usuario
- **3. Actualizaciones al Diagrama de Clases UML**
- UsuarioModelTests
- JWT Authentication - Backend (Estado Actual)
- Roles del Equipo Raite - Asignación por Afinidad (v2)
- 3. BASE DE DATOS
- 2. FRONTEND (SSR + Progressive Enhancement)
- main
- Install the dependencies
- Roles del Equipo Raite
- .prettierrc.json
- opencode.json
- AGENTS.md
- env.d.ts
- README.md
- MainLayout.vue
- 4. EXTERNO A CODIFICACIÓN (INFRA, OPS, PROCESOS)
- **Usuario**
- .no_tiene_raite_en_curso
- **MAPAS, GEOCODIFICACIÓN Y RASTREO EN VIVO**
- django_db
- **Poblado de la Base de Datos (Catálogo de Puntos)**
- admin.py
- auth-store.ts
- models.py
- stores/index.ts
- typed-router.d.ts
- axios.ts
- RoleSelectionModal.vue
- 0006_alter_usuario_calificacion.py
- 0005_alter_usuario_sexo.py
- 0008_remove_usuario_verificado_usuario_suspendido.py

## God Nodes (most connected - your core abstractions)
1. `Usuario` - 44 edges
2. `Vehiculo` - 27 edges
3. `UsuarioModelTests` - 23 edges
4. `Plan: User Model Propio (`accounts.Usuario`) + Adaptación del JWT` - 17 edges
5. `5.3 Tests nuevos obligatorios` - 16 edges
6. `paths` - 15 edges
7. `Raite — API REST y Tiempo Real` - 15 edges
8. `AuthAPITests` - 14 edges
9. `1. BACKEND` - 13 edges
10. `Stack Tecnológico por Capa` - 12 edges

## Surprising Connections (you probably didn't know these)
- `10. Decisiones de diseño pendientes` --references--> `Usuario`  [INFERRED]
  RaiteDocs/Raite-Django-Models.md → Back_Raite/apps/accounts/models.py
- `**Estructuras de Datos**` --references--> `Vehiculo`  [INFERRED]
  RaiteDocs/Sketches/Raite_layout_disposition_001.md → Back_Raite/apps/accounts/models.py
- `6.1 Qué se borra de `Raite_DjangoRest/views.py`` --references--> `MeView`  [INFERRED]
  RaiteDocs/Sketches/plan_custom_user_model.md → Back_Raite/apps/accounts/views.py
- `1.2 Endpoint `/api/me/` (Perfil usuario)` --references--> `MeView`  [INFERRED]
  RaiteDocs/Sketches/plan_jwt_auth.md → Back_Raite/apps/accounts/views.py
- `Control de Versiones` --references--> `main()`  [INFERRED]
  RaiteDocs/Raite-System-Architecture.md → Back_Raite/manage.py

## Import Cycles
- None detected.

## Communities (63 total, 23 thin omitted)

### Community 0 - "LoginPage.vue"
Cohesion: 0.15
Nodes (8): authStore, correo, loading, password, rememberMeCheckbox, showPassword, quasar, validator

### Community 1 - "Vehiculo"
Cohesion: 0.12
Nodes (18): TipoVehiculo, Vehiculo, Meta, RegistroResponseSerializer, RegistroSerializer, UsuarioSerializer, VehiculoRegistroResponseSerializer, VehiculoRegistroSerializer (+10 more)

### Community 2 - "package.json"
Cohesion: 0.05
Nodes (41): dependencies, axios, pinia, quasar, @quasar/extras, validator, vue, vue-router (+33 more)

### Community 3 - "1. BACKEND"
Cohesion: 0.15
Nodes (13): 1.10 Seguridad y Hardening, 1.11 Internacionalización y Localización, 1.12 Utilidades de Desarrollo, 1.1 Framework y Núcleo, 1.2 Configuración y Entorno, 1.3 Autenticación y Autorización, 1.4 Lógica de Negocio / Dominio, 1.5 Enrutamiento y APIs (+5 more)

### Community 4 - "Raite — API REST y Tiempo Real"
Cohesion: 0.05
Nodes (38): IsAdmin, IsDriver, IsPassenger, 12. Endpoints del panel de administración, 13. Superficie de eventos y tareas periódicas, 14. Pendientes técnicos, 1. Convenciones, 2. `core` — Salud y raíz (+30 more)

### Community 5 - "Stack Tecnológico por Capa"
Cohesion: 0.05
Nodes (31): AccountsConfig, Architecture Decision Records (ADRs), Archivos y Media, Arquitectura del Sistema Raite, Autenticación y Autorización, Backend API (Django REST Framework), Backend Core, Base de Datos (+23 more)

### Community 6 - "Infraestructura, CI/CD y Observabilidad"
Cohesion: 0.25
Nodes (8): Control de Versiones, Documentación, Hosting e Infraestructura (Producción), Infraestructura, CI/CD y Observabilidad, Legal y Cumplimiento (México), Observabilidad, Seguridad Operacional, Testing y Calidad

### Community 7 - "paths"
Cohesion: 0.10
Nodes (19): compilerOptions, ignoreDeprecations, paths, extends, boot/*, components/*, pages/*, #q-app (+11 more)

### Community 8 - "SignUpPage.vue"
Cohesion: 0.08
Nodes (19): apellidos, authStore, carrera, confirmPassword, edad, email, formRef, hasLowercase (+11 more)

### Community 9 - "**Raite - Documento de Layout y Disposición (Mejorado)**"
Cohesion: 0.11
Nodes (17): **1. Diagrama de Clases**, **2. Diagrama de Estados del Raite**, **3. Diagrama de Secuencia: Crear y Aceptar Raite**, **4. Diagrama de Secuencia: Expiración por Tiempo**, **Autenticación**, **DAR RAITE (Conductor)**, **DIAGRAMAS UML**, **Estructuras de Datos** (+9 more)

### Community 10 - "Plan: JWT Auth Completo (Frontend + Backend Gaps)"
Cohesion: 0.12
Nodes (16): 1.1 Token Blacklist (Logout seguro), 1.2 Endpoint `/api/me/` (Perfil usuario), 1.3 (Opcional) Refresh Token Rotation, 1.4 Seguridad, 2.1 Archivos a CREAR, 2.2 Archivos a MODIFICAR, 2.3 Detalles Técnicos Clave, Dependencias entre fases (+8 more)

### Community 11 - "devDependencies"
Cohesion: 0.12
Nodes (17): devDependencies, autoprefixer, eslint, @eslint/js, eslint-plugin-vue, globals, postcss, prettier (+9 more)

### Community 13 - "Arquitectura del Sistema Raite"
Cohesion: 0.12
Nodes (15): Architecture Decision Records (ADRs), Arquitectura del Sistema Raite, Arquitectura por Capas (Backend), Backend API (Django REST Framework), Backend (raite-backend/), Base de Datos, Despliegue e Infraestructura, Estructura de Carpetas (+7 more)

### Community 14 - "Raite — Modelos de Dominio"
Cohesion: 0.14
Nodes (13): 10. Decisiones de diseño pendientes, 1. Diagrama de entidades, 3. `vehicles.Vehiculo`, 4. `locations`, 5. `rides.Raite`, 6. `surveys.EncuestaFinalizacion`, 7. `ratings.Calificacion`, 8. `notifications.Notificacion` (+5 more)

### Community 15 - "0001_initial.py"
Cohesion: 0.19
Nodes (3): Migration, Migration, Migration

### Community 16 - "Usuario"
Cohesion: 0.05
Nodes (39): UsuarioAdmin, Rol, Meta, Usuario, UsuarioManager, 🔴 C1 — Roles: tabla `UsuarioRol`, sin `AMBOS` almacenado, 🔴 C3 — `activo` (bool) y `cuenta_activa` (Integer) como caché de ocupación, 10.1 Canal (+31 more)

### Community 17 - "**3. Actualizaciones al Diagrama de Clases UML**"
Cohesion: 0.15
Nodes (12): **1.1. Consulta en Overpass Turbo**, **1.2. Procesamiento y Seed (Migración)**, **1. Poblado de la Base de Datos (Catálogo de Puntos)**, **2.1. Renderizado Básico con Leaflet**, **2.2. Seguimiento Live GPS del Dispositivo**, **2. Uso de Leaflet y Seguimiento Live (GPS)**, **3. Actualizaciones al Diagrama de Clases UML**, **Nueva Clase Transitoria (WebSocket Manager / Redis)** (+4 more)

### Community 18 - "UsuarioModelTests"
Cohesion: 0.06
Nodes (8): AuthAPITests, UsuarioModelTests, 5.1 Después de cada corrección (§1.4), 5.2 Checks finales, 5.3 Tests nuevos obligatorios, 5. Verificación, 7. Abiertas para el usuario (no resolverlas por cuenta propia), 🟢 C9 — `calificacion` acotada a 0–5

### Community 19 - "JWT Authentication - Backend (Estado Actual)"
Cohesion: 0.17
Nodes (11): 1. Configuración Actual, 2. Endpoints Disponibles, 3. Flujo de Autenticación Actual, 4. Protección de Vistas, 5. Limitaciones Actuales (Gaps), 6. Variables de Entorno Relevantes, 7. Seguridad Actual, Dependencias instaladas (`requirements.txt`) (+3 more)

### Community 20 - "Roles del Equipo Raite - Asignación por Afinidad (v2)"
Cohesion: 0.20
Nodes (9): Angel, Cambios Respecto a v1, Gabriel, Notas de Implementación, Rafa, Raúl, Resumen de Cobertura de Roles Críticos, Rogelio (+1 more)

### Community 21 - "3. BASE DE DATOS"
Cohesion: 0.20
Nodes (9): 3.1 Motor Principal, 3.2 Esquema - Tablas Core, 3.3 Índices y Performance, 3.4 Migraciones y Versionado, 3.5 Conexión y Pooling, 3.6 Desarrollo Local, 3. BASE DE DATOS, 5. RESUMEN POR CATEGORÍA (QUICK REFERENCE) (+1 more)

### Community 22 - "2. FRONTEND (SSR + Progressive Enhancement)"
Cohesion: 0.22
Nodes (9): 2.1 Plantillas y Renderizado, 2.2 Framework CSS y Componentes, 2.3 Mapas e Interacción Geo, 2.4 UI/UX Libraries, 2.5 JavaScript - Arquitectura, 2.6 JavaScript - Funcionalidades Clave, 2.7 PWA y Offline, 2.9 Tipografía y Assets (+1 more)

### Community 23 - "main"
Cohesion: 0.29
Nodes (6): main(), CI/CD Pipeline, CI/CD Pipeline, 2.8 Accesibilidad (a11y), 4.1 CI/CD Pipeline, 4.2 Control de Versiones y Flujo

### Community 24 - "Install the dependencies"
Cohesion: 0.29
Nodes (6): Build the app for production, Customize the configuration, Format & Lint the files, Install the dependencies, Raite App (front-raite), Start the app in development mode (HMR, error reporting, etc.)

### Community 25 - "Roles del Equipo Raite"
Cohesion: 0.29
Nodes (6): Angel, Gabriel, Rafa, Raúl, Rogelio, Roles del Equipo Raite

### Community 27 - ".prettierrc.json"
Cohesion: 0.50
Nodes (3): printWidth, $schema, singleQuote

### Community 35 - "MainLayout.vue"
Cohesion: 0.22
Nodes (5): EssentialLinkProps, authStore, leftDrawerOpen, linksList, logout()

### Community 45 - "4. EXTERNO A CODIFICACIÓN (INFRA, OPS, PROCESOS)"
Cohesion: 0.29
Nodes (7): 4.3 Testing y Calidad, 4.4 Hosting e Infraestructura (Producción), 4.5 Observabilidad y Monitoreo, 4.6 Seguridad Operacional, 4.7 Documentación, 4.8 Legal y Cumplimiento (México), 4. EXTERNO A CODIFICACIÓN (INFRA, OPS, PROCESOS)

### Community 46 - "**Usuario**"
Cohesion: 0.20
Nodes (9): **Admin**, | DAR RAITE |, | HOME |, | LOG IN / REGISTER |, Panel 1, Panel 2, | PEDIR RAITE |, **Pendientes** (+1 more)

### Community 47 - ".no_tiene_raite_en_curso"
Cohesion: 0.06
Nodes (40): 0. Objetivo y alcance, 1. Reglas de ejecución (obligatorias para el agente), 2. Resumen de correcciones, 4. Orden de ejecución, 6. Decisiones tomadas aquí que el agente NO debe cambiar, 🟡 C7 — `no_tiene_raite_en_curso()` y reescritura de `puede_*_raite()`, Primera Corrección — Fase 2: Alineación de `apps/accounts` con `Raite_layout_disposition_002.md`, **1. Diagrama de Clases** (+32 more)

### Community 48 - "**MAPAS, GEOCODIFICACIÓN Y RASTREO EN VIVO**"
Cohesion: 0.25
Nodes (8): **Actualizaciones al Diagrama de Clases UML**, **Consulta en Overpass Turbo**, **MAPAS, GEOCODIFICACIÓN Y RASTREO EN VIVO**, **Poblado de la Base de Datos (Catálogo de Puntos)**, **Procesamiento y Seed (Migración)**, **Renderizado Básico con Leaflet**, **Seguimiento Live GPS del Dispositivo**, **Uso de Leaflet y Seguimiento Live (GPS)**

### Community 50 - "django_db"
Cohesion: 0.13
Nodes (6): Migration, Migration, Migration, Migration, Migration, Migration

### Community 52 - "**Poblado de la Base de Datos (Catálogo de Puntos)**"
Cohesion: 0.40
Nodes (4): **Consulta en Overpass Turbo**, **MAPAS, GEOCODIFICACIÓN Y RASTREO EN VIVO**, **Poblado de la Base de Datos (Catálogo de Puntos)**, **Procesamiento y Seed (Migración)**

### Community 53 - "admin.py"
Cohesion: 0.17
Nodes (3): Meta, UsuarioChangeForm, UsuarioCreationForm

### Community 54 - "auth-store.ts"
Cohesion: 0.20
Nodes (8): authStore, logout(), authStore, logout(), Router, useAuthStore, User, vue-router

### Community 55 - "models.py"
Cohesion: 0.23
Nodes (3): Sexo, 🔴 C2 — `sexo` obligatorio, sin `PREFIERE_NO_DECIR`, **Autenticación**

### Community 56 - "stores/index.ts"
Cohesion: 0.20
Nodes (4): useCounterStore, pinia, PiniaCustomProperties, pinia

### Community 57 - "typed-router.d.ts"
Cohesion: 0.25
Nodes (6): _RouteFileInfoMap, RouteNamedMap, _RouteNamesForFilePath, TypesConfig, vue-router, vue-router/auto-routes

### Community 58 - "axios.ts"
Cohesion: 0.29
Nodes (5): api, failedQueue, RetryableRequestConfig, axios, vue

### Community 59 - "RoleSelectionModal.vue"
Cohesion: 0.38
Nodes (6): emit, Emits, loading, Props, select(), show

## Knowledge Gaps
- **340 isolated node(s):** `$schema`, `plugin`, `Migration`, `Migration`, `Migration` (+335 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 472 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Usuario` connect `Usuario` to `Vehiculo`, `Raite — API REST y Tiempo Real`, `Raite — Modelos de Dominio`, `.no_tiene_raite_en_curso`, `admin.py`, `models.py`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Why does `Vehiculo` connect `Vehiculo` to `Raite — API REST y Tiempo Real`, `Raite — Modelos de Dominio`, `.no_tiene_raite_en_curso`, `Usuario`, `UsuarioModelTests`, `models.py`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `MeView` connect `Vehiculo` to `Plan: JWT Auth Completo (Frontend + Backend Gaps)`, `Raite — API REST y Tiempo Real`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `Usuario` (e.g. with `UsuarioChangeForm` and `UsuarioCreationForm`) actually correct?**
  _`Usuario` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `Vehiculo` (e.g. with `TipoVehiculo` and `VehiculoRegistroSerializer`) actually correct?**
  _`Vehiculo` has 19 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `plugin`, `Migration` to the rest of the system?**
  _340 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Vehiculo` be split into smaller, more focused modules?**
  _Cohesion score 0.1166429587482219 - nodes in this community are weakly interconnected._