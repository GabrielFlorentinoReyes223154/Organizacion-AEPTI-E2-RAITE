# Graph Report - Raite  (2026-10-01)

## Corpus Check
- 75 files · ~51,456 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: .ico 7, (none) 4, .scss 2)

## Summary
- 651 nodes · 766 edges · 54 communities (32 shown, 22 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 88 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b1568043`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- LoginPage.vue
- views.py
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
- models.py
- Plan: User Model Propio (`accounts.Usuario`) + Adaptación del JWT
- **3. Actualizaciones al Diagrama de Clases UML**
- UsuarioModelTests
- JWT Authentication - Backend (Estado Actual)
- Roles del Equipo Raite - Asignación por Afinidad (v2)
- Usuario
- Vehiculo
- AuthAPITests
- Install the dependencies
- Roles del Equipo Raite
- .prettierrc.json
- opencode.json
- AGENTS.md
- env.d.ts
- README.md
- **Raite - Documento de Layout y Disposición (Mejorado)**
- **Usuario**
- **Raite - Documento de Layout y Disposición (Mejorado)**
- **MAPAS, GEOCODIFICACIÓN Y RASTREO EN VIVO**
- **FLUJOS DE USUARIO**
- **FLUJOS DE USUARIO**
- PerfilConductor
- **Poblado de la Base de Datos (Catálogo de Puntos)**
- UsuarioAdmin

## God Nodes (most connected - your core abstractions)
1. `Usuario` - 35 edges
2. `Plan: User Model Propio (`accounts.Usuario`) + Adaptación del JWT` - 17 edges
3. `PerfilConductor` - 16 edges
4. `UsuarioModelTests` - 15 edges
5. `paths` - 15 edges
6. `Raite — API REST y Tiempo Real` - 15 edges
7. `1. BACKEND` - 13 edges
8. `Vehiculo` - 12 edges
9. `Stack Tecnológico por Capa` - 12 edges
10. `Raite — Modelos de Dominio` - 11 edges

## Surprising Connections (you probably didn't know these)
- `10. Decisiones de diseño pendientes` --references--> `Usuario`  [INFERRED]
  RaiteDocs/Raite-Django-Models.md → Back_Raite/apps/accounts/models.py
- `**PEDIR RAITE (Pasajero) — Crea un RAITE**` --references--> `Usuario`  [INFERRED]
  RaiteDocs/Raite_layout_disposition_002.md → Back_Raite/apps/accounts/models.py
- `2. Decisiones tomadas` --references--> `Usuario`  [INFERRED]
  RaiteDocs/Sketches/plan_custom_user_model.md → Back_Raite/apps/accounts/models.py
- `Objetivo` --references--> `Usuario`  [INFERRED]
  RaiteDocs/Sketches/plan_custom_user_model.md → Back_Raite/apps/accounts/models.py
- `**PEDIR RAITE (Pasajero) — Crea un RAITE**` --references--> `Usuario`  [INFERRED]
  RaiteDocs/Sketches/Raite_layout_disposition_001.md → Back_Raite/apps/accounts/models.py

## Import Cycles
- None detected.

## Communities (54 total, 22 thin omitted)

### Community 0 - "LoginPage.vue"
Cohesion: 0.05
Nodes (25): api, failedQueue, RetryableRequestConfig, authStore, correo, loading, password, rememberMeCheckbox (+17 more)

### Community 1 - "views.py"
Cohesion: 0.09
Nodes (12): Meta, RegistroResponseSerializer, RegistroSerializer, UsuarioSerializer, VehiculoRegistroResponseSerializer, VehiculoRegistroSerializer, VehiculoSerializer, MeView (+4 more)

### Community 2 - "package.json"
Cohesion: 0.05
Nodes (41): dependencies, axios, pinia, quasar, @quasar/extras, validator, vue, vue-router (+33 more)

### Community 3 - "1. BACKEND"
Cohesion: 0.06
Nodes (31): 1.10 Seguridad y Hardening, 1.11 Internacionalización y Localización, 1.12 Utilidades de Desarrollo, 1.1 Framework y Núcleo, 1.2 Configuración y Entorno, 1.3 Autenticación y Autorización, 1.4 Lógica de Negocio / Dominio, 1.5 Enrutamiento y APIs (+23 more)

### Community 4 - "Raite — API REST y Tiempo Real"
Cohesion: 0.05
Nodes (41): IsAdmin, IsDriver, IsPassenger, 10.1 Canal, 10.2 Group por usuario, 10.3 Eventos, 10. `realtime` — WebSocket, 12. Endpoints del panel de administración (+33 more)

### Community 5 - "Stack Tecnológico por Capa"
Cohesion: 0.06
Nodes (31): AccountsConfig, Architecture Decision Records (ADRs), Archivos y Media, Arquitectura del Sistema Raite, Autenticación y Autorización, Backend API (Django REST Framework), Backend Core, Base de Datos (+23 more)

### Community 6 - "Infraestructura, CI/CD y Observabilidad"
Cohesion: 0.10
Nodes (21): main(), CI/CD Pipeline, Control de Versiones, Documentación, Hosting e Infraestructura (Producción), Infraestructura, CI/CD y Observabilidad, Legal y Cumplimiento (México), Observabilidad (+13 more)

### Community 7 - "paths"
Cohesion: 0.10
Nodes (19): compilerOptions, ignoreDeprecations, paths, extends, boot/*, components/*, pages/*, #q-app (+11 more)

### Community 8 - "SignUpPage.vue"
Cohesion: 0.11
Nodes (14): EssentialLinkProps, leftDrawerOpen, linksList, confirmPassword, email, hasLowercase, hasMinLength, hasNumber (+6 more)

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
Cohesion: 0.15
Nodes (12): 10. Decisiones de diseño pendientes, 1. Diagrama de entidades, 3. `vehicles.Vehiculo`, 4. `locations`, 5. `rides.Raite`, 6. `surveys.EncuestaFinalizacion`, 7. `ratings.Calificacion`, 8. `notifications.Notificacion` (+4 more)

### Community 15 - "models.py"
Cohesion: 0.08
Nodes (9): Meta, UsuarioChangeForm, UsuarioCreationForm, Migration, Migration, Migration, Migration, Sexo (+1 more)

### Community 16 - "Plan: User Model Propio (`accounts.Usuario`) + Adaptación del JWT"
Cohesion: 0.14
Nodes (13): 11. Riesgos y desviaciones, 12. Rollback, 1. Contexto verificado, 2. Decisiones tomadas, 3. Orden de operaciones (crítico), 5.1 Por qué el `UserAdmin` por defecto es peligroso, 5.2 `apps/accounts/admin.py`, 5.3 Qué sobrevive del admin actual (+5 more)

### Community 17 - "**3. Actualizaciones al Diagrama de Clases UML**"
Cohesion: 0.15
Nodes (12): **1.1. Consulta en Overpass Turbo**, **1.2. Procesamiento y Seed (Migración)**, **1. Poblado de la Base de Datos (Catálogo de Puntos)**, **2.1. Renderizado Básico con Leaflet**, **2.2. Seguimiento Live GPS del Dispositivo**, **2. Uso de Leaflet y Seguimiento Live (GPS)**, **3. Actualizaciones al Diagrama de Clases UML**, **Nueva Clase Transitoria (WebSocket Manager / Redis)** (+4 more)

### Community 19 - "JWT Authentication - Backend (Estado Actual)"
Cohesion: 0.17
Nodes (11): 1. Configuración Actual, 2. Endpoints Disponibles, 3. Flujo de Autenticación Actual, 4. Protección de Vistas, 5. Limitaciones Actuales (Gaps), 6. Variables de Entorno Relevantes, 7. Seguridad Actual, Dependencias instaladas (`requirements.txt`) (+3 more)

### Community 20 - "Roles del Equipo Raite - Asignación por Afinidad (v2)"
Cohesion: 0.20
Nodes (9): Angel, Cambios Respecto a v1, Gabriel, Notas de Implementación, Rafa, Raúl, Resumen de Cobertura de Roles Críticos, Rogelio (+1 more)

### Community 21 - "Usuario"
Cohesion: 0.14
Nodes (10): Rol, Meta, Usuario, 11. Permisos, **DAR RAITE (Conductor)**, 14. Referencias, 4.2 Mapa campo por campo (UML → implementación), 4.4 `apps/accounts/models_choices.py` (+2 more)

### Community 22 - "Vehiculo"
Cohesion: 0.22
Nodes (8): Vehiculo, 2. `accounts.Usuario`, 9. Resumen de dependencias entre modelos, 4.1 Archivos a crear, 4.3 `apps/accounts/apps.py`, 4.5 `apps/accounts/models.py`, 4.6 `apps/accounts/signals.py`, 4. Fase 1 — Modelos

### Community 24 - "Install the dependencies"
Cohesion: 0.29
Nodes (6): Build the app for production, Customize the configuration, Format & Lint the files, Install the dependencies, Raite App (front-raite), Start the app in development mode (HMR, error reporting, etc.)

### Community 25 - "Roles del Equipo Raite"
Cohesion: 0.29
Nodes (6): Angel, Gabriel, Rafa, Raúl, Rogelio, Roles del Equipo Raite

### Community 27 - ".prettierrc.json"
Cohesion: 0.50
Nodes (3): printWidth, $schema, singleQuote

### Community 45 - "**Raite - Documento de Layout y Disposición (Mejorado)**"
Cohesion: 0.20
Nodes (9): **1. Diagrama de Clases**, **2. Diagrama de Estados del Raite**, **3. Diagrama de Secuencia: Crear y Aceptar Raite**, **4. Diagrama de Secuencia: Expiración por Tiempo**, **DIAGRAMAS UML**, **MEJORAS UI/UX (Sugeridas)**, **NOTAS TÉCNICAS / PENDIENTES**, **PANEL DE ADMINISTRACIÓN** (+1 more)

### Community 46 - "**Usuario**"
Cohesion: 0.20
Nodes (9): **Admin**, | DAR RAITE |, | HOME |, | LOG IN / REGISTER |, Panel 1, Panel 2, | PEDIR RAITE |, **Pendientes** (+1 more)

### Community 47 - "**Raite - Documento de Layout y Disposición (Mejorado)**"
Cohesion: 0.20
Nodes (9): **1. Diagrama de Clases**, **2. Diagrama de Estados del Raite**, **3. Diagrama de Secuencia: Crear y Aceptar Raite**, **4. Diagrama de Secuencia: Expiración por Tiempo**, **DIAGRAMAS UML**, **MEJORAS UI/UX (Sugeridas)**, **NOTAS TÉCNICAS / PENDIENTES**, **PANEL DE ADMINISTRACIÓN** (+1 more)

### Community 48 - "**MAPAS, GEOCODIFICACIÓN Y RASTREO EN VIVO**"
Cohesion: 0.25
Nodes (8): **Actualizaciones al Diagrama de Clases UML**, **Consulta en Overpass Turbo**, **MAPAS, GEOCODIFICACIÓN Y RASTREO EN VIVO**, **Poblado de la Base de Datos (Catálogo de Puntos)**, **Procesamiento y Seed (Migración)**, **Renderizado Básico con Leaflet**, **Seguimiento Live GPS del Dispositivo**, **Uso de Leaflet y Seguimiento Live (GPS)**

### Community 49 - "**FLUJOS DE USUARIO**"
Cohesion: 0.25
Nodes (8): **Autenticación**, **CATÁLOGO DE PUNTOS DE RAITE**, **Estructuras de Datos**, **FLUJOS DE USUARIO**, **Panel 1 - Selección de Viaje y Rol Activo**, **Panel 2 - Tarjetas de Estado Dinámico**, **PANTALLA HOME**, **PEDIR RAITE (Pasajero) — Crea un RAITE**

### Community 50 - "**FLUJOS DE USUARIO**"
Cohesion: 0.25
Nodes (8): **Autenticación**, **CATÁLOGO DE PUNTOS DE RAITE**, **Estructuras de Datos**, **FLUJOS DE USUARIO**, **Panel 1 - Selección de Viaje y Rol Activo**, **Panel 2 - Tarjetas de Estado Dinámico**, **PANTALLA HOME**, **PEDIR RAITE (Pasajero) — Crea un RAITE**

### Community 51 - "PerfilConductor"
Cohesion: 0.43
Nodes (3): PerfilConductor, actualizar_vehiculo_valido(), crear_perfil_conductor()

### Community 52 - "**Poblado de la Base de Datos (Catálogo de Puntos)**"
Cohesion: 0.40
Nodes (4): **Consulta en Overpass Turbo**, **MAPAS, GEOCODIFICACIÓN Y RASTREO EN VIVO**, **Poblado de la Base de Datos (Catálogo de Puntos)**, **Procesamiento y Seed (Migración)**

## Knowledge Gaps
- **316 isolated node(s):** `$schema`, `plugin`, `Migration`, `Migration`, `Migration` (+311 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 432 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Usuario` connect `Usuario` to `views.py`, `Raite — API REST y Tiempo Real`, `Raite — Modelos de Dominio`, `models.py`, `Plan: User Model Propio (`accounts.Usuario`) + Adaptación del JWT`, `**FLUJOS DE USUARIO**`, `**FLUJOS DE USUARIO**`, `PerfilConductor`, `UsuarioAdmin`, `Vehiculo`?**
  _High betweenness centrality (0.172) - this node is a cross-community bridge._
- **Why does `Tecnologías Propuestas para Raite` connect `1. BACKEND` to `Stack Tecnológico por Capa`, `Infraestructura, CI/CD y Observabilidad`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `Usuario` (e.g. with `UsuarioChangeForm` and `UsuarioCreationForm`) actually correct?**
  _`Usuario` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `PerfilConductor` (e.g. with `VehiculoRegistroSerializer` and `VehiculoSerializer`) actually correct?**
  _`PerfilConductor` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `plugin`, `Migration` to the rest of the system?**
  _316 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `LoginPage.vue` be split into smaller, more focused modules?**
  _Cohesion score 0.052854122621564484 - nodes in this community are weakly interconnected._
- **Should `views.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09269162210338681 - nodes in this community are weakly interconnected._