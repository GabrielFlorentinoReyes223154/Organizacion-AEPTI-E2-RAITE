# Graph Report - Raite  (2026-10-01)

## Corpus Check
- 71 files · ~33,564 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 14 file(s) not represented in the graph (top: .ico 7, (none) 4, .scss 2)

## Summary
- 605 nodes · 717 edges · 44 communities (23 shown, 21 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 82 edges (avg confidence: 0.95)
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
- 2. FRONTEND (SSR + Progressive Enhancement)
- paths
- SignUpPage.vue
- **Raite - Documento de Layout y Disposición (Mejorado)**
- **Raite - Documento de Layout y Disposición (Mejorado)**
- devDependencies
- Arquitectura del Sistema Raite
- Raite — Modelos de Dominio
- models.py
- JWT Authentication - Backend (Estado Actual)
- Plan: JWT Auth Completo (Frontend + Backend Gaps)
- UsuarioModelTests
- **Usuario**
- Roles del Equipo Raite - Asignación por Afinidad (v2)
- Usuario
- AuthAPITests
- Install the dependencies
- Roles del Equipo Raite
- .prettierrc.json
- opencode.json
- AGENTS.md
- env.d.ts
- README.md

## God Nodes (most connected - your core abstractions)
1. `Usuario` - 33 edges
2. `Plan: User Model Propio (`accounts.Usuario`) + Adaptación del JWT` - 17 edges
3. `PerfilConductor` - 16 edges
4. `UsuarioModelTests` - 15 edges
5. `paths` - 15 edges
6. `Raite — API REST y Tiempo Real` - 15 edges
7. `1. BACKEND` - 13 edges
8. `Stack Tecnológico por Capa` - 12 edges
9. `Raite — Modelos de Dominio` - 11 edges
10. `Arquitectura del Sistema Raite` - 11 edges

## Surprising Connections (you probably didn't know these)
- `10. Decisiones de diseño pendientes` --references--> `Usuario`  [INFERRED]
  RaiteDocs/Raite-Django-Models.md → Back_Raite/apps/accounts/models.py
- `6.1 Qué se borra de `Raite_DjangoRest/views.py`` --references--> `MeView`  [INFERRED]
  RaiteDocs/plan_custom_user_model.md → Back_Raite/apps/accounts/views.py
- `1.2 Endpoint `/api/me/` (Perfil usuario)` --references--> `MeView`  [INFERRED]
  RaiteDocs/plan_jwt_auth.md → Back_Raite/apps/accounts/views.py
- `13. Checklist de ejecución` --references--> `UsuarioAdmin`  [INFERRED]
  RaiteDocs/plan_custom_user_model.md → Back_Raite/apps/accounts/admin.py
- `13. Checklist de ejecución` --references--> `Usuario`  [INFERRED]
  RaiteDocs/plan_custom_user_model.md → Back_Raite/apps/accounts/models.py

## Import Cycles
- None detected.

## Communities (44 total, 21 thin omitted)

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
Cohesion: 0.07
Nodes (28): 1.10 Seguridad y Hardening, 1.11 Internacionalización y Localización, 1.12 Utilidades de Desarrollo, 1.1 Framework y Núcleo, 1.2 Configuración y Entorno, 1.3 Autenticación y Autorización, 1.4 Lógica de Negocio / Dominio, 1.5 Enrutamiento y APIs (+20 more)

### Community 4 - "Raite — API REST y Tiempo Real"
Cohesion: 0.05
Nodes (40): IsAdmin, IsDriver, IsPassenger, 6.1 Qué se borra de `Raite_DjangoRest/views.py`, 6.2 Qué **no** se toca (verificado), 6.3 `Raite_DjangoRest/settings.py`, 6.4 `apps/accounts/serializers.py`, `views.py`, `urls_auth.py`, 6.5 `Raite_DjangoRest/urls.py` (+32 more)

### Community 5 - "Stack Tecnológico por Capa"
Cohesion: 0.07
Nodes (25): AccountsConfig, Architecture Decision Records (ADRs), Archivos y Media, Arquitectura del Sistema Raite, Autenticación y Autorización, Backend API (Django REST Framework), Backend Core, Base de Datos (+17 more)

### Community 6 - "2. FRONTEND (SSR + Progressive Enhancement)"
Cohesion: 0.07
Nodes (30): main(), CI/CD Pipeline, Control de Versiones, Documentación, Hosting e Infraestructura (Producción), Infraestructura, CI/CD y Observabilidad, Legal y Cumplimiento (México), Observabilidad (+22 more)

### Community 7 - "paths"
Cohesion: 0.10
Nodes (19): compilerOptions, ignoreDeprecations, paths, extends, boot/*, components/*, pages/*, #q-app (+11 more)

### Community 8 - "SignUpPage.vue"
Cohesion: 0.11
Nodes (14): EssentialLinkProps, leftDrawerOpen, linksList, confirmPassword, email, hasLowercase, hasMinLength, hasNumber (+6 more)

### Community 9 - "**Raite - Documento de Layout y Disposición (Mejorado)**"
Cohesion: 0.11
Nodes (17): **1. Diagrama de Clases**, **2. Diagrama de Estados del Raite**, **3. Diagrama de Secuencia: Crear y Aceptar Raite**, **4. Diagrama de Secuencia: Expiración por Tiempo**, **Autenticación**, **DAR RAITE (Conductor)**, **DIAGRAMAS UML**, **Estructuras de Datos** (+9 more)

### Community 10 - "**Raite - Documento de Layout y Disposición (Mejorado)**"
Cohesion: 0.11
Nodes (17): **1. Diagrama de Clases**, **2. Diagrama de Estados del Raite**, **3. Diagrama de Secuencia: Crear y Aceptar Raite**, **4. Diagrama de Secuencia: Expiración por Tiempo**, **Autenticación**, **DAR RAITE (Conductor)**, **DIAGRAMAS UML**, **Estructuras de Datos** (+9 more)

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

### Community 16 - "JWT Authentication - Backend (Estado Actual)"
Cohesion: 0.17
Nodes (11): 1. Configuración Actual, 2. Endpoints Disponibles, 3. Flujo de Autenticación Actual, 4. Protección de Vistas, 5. Limitaciones Actuales (Gaps), 6. Variables de Entorno Relevantes, 7. Seguridad Actual, Dependencias instaladas (`requirements.txt`) (+3 more)

### Community 17 - "Plan: JWT Auth Completo (Frontend + Backend Gaps)"
Cohesion: 0.12
Nodes (16): 1.1 Token Blacklist (Logout seguro), 1.2 Endpoint `/api/me/` (Perfil usuario), 1.3 (Opcional) Refresh Token Rotation, 1.4 Seguridad, 2.1 Archivos a CREAR, 2.2 Archivos a MODIFICAR, 2.3 Detalles Técnicos Clave, Dependencias entre fases (+8 more)

### Community 19 - "**Usuario**"
Cohesion: 0.20
Nodes (9): **Admin**, | DAR RAITE |, | HOME |, | LOG IN / REGISTER |, Panel 1, Panel 2, | PEDIR RAITE |, **Pendientes** (+1 more)

### Community 20 - "Roles del Equipo Raite - Asignación por Afinidad (v2)"
Cohesion: 0.20
Nodes (9): Angel, Cambios Respecto a v1, Gabriel, Notas de Implementación, Rafa, Raúl, Resumen de Cobertura de Roles Críticos, Rogelio (+1 more)

### Community 21 - "Usuario"
Cohesion: 0.05
Nodes (35): UsuarioAdmin, Rol, Meta, PerfilConductor, Usuario, Vehiculo, actualizar_vehiculo_valido(), crear_perfil_conductor() (+27 more)

### Community 24 - "Install the dependencies"
Cohesion: 0.29
Nodes (6): Build the app for production, Customize the configuration, Format & Lint the files, Install the dependencies, Raite App (front-raite), Start the app in development mode (HMR, error reporting, etc.)

### Community 25 - "Roles del Equipo Raite"
Cohesion: 0.29
Nodes (6): Angel, Gabriel, Rafa, Raúl, Rogelio, Roles del Equipo Raite

### Community 27 - ".prettierrc.json"
Cohesion: 0.50
Nodes (3): printWidth, $schema, singleQuote

## Knowledge Gaps
- **292 isolated node(s):** `$schema`, `plugin`, `Migration`, `Migration`, `Migration` (+287 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 405 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AccountsConfig` connect `Stack Tecnológico por Capa` to `Usuario`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Why does `Usuario` connect `Usuario` to `views.py`, `Raite — Modelos de Dominio`, `models.py`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Why does `Tecnologías Propuestas para Raite` connect `1. BACKEND` to `2. FRONTEND (SSR + Progressive Enhancement)`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `Usuario` (e.g. with `UsuarioChangeForm` and `UsuarioCreationForm`) actually correct?**
  _`Usuario` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `PerfilConductor` (e.g. with `VehiculoRegistroSerializer` and `VehiculoSerializer`) actually correct?**
  _`PerfilConductor` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `plugin`, `Migration` to the rest of the system?**
  _292 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `LoginPage.vue` be split into smaller, more focused modules?**
  _Cohesion score 0.052854122621564484 - nodes in this community are weakly interconnected._