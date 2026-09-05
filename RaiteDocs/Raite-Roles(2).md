# Roles del Equipo Raite - Asignación por Afinidad (v2)

## Angel
- Programador FullStack (Backend-heavy: Django, DRF, GeoDjango, PostGIS, Channels, Celery, Services Layer, Repository Pattern)
- Análisis de requisitos
- Casos de uso
- **Product Owner / Analista Funcional** (afinidad: análisis de requisitos, visión de producto, definición de reglas de matching)
- **Security Engineer** (afinidad: backend expone superficie de ataque, define hardening, CSP, rate-limit, 2FA, LFPDPPP compliance)

---

## Rogelio
- Arquitecto de BD
- Programador FullStack (Backend-heavy: Django, DRF, modelos, migraciones, queries espaciales, optimización)
- Modelo E-R de la BD
- Script de PostgreSQL + PostGIS
- **DBA / Database Performance Engineer** (afinidad: índices GIST/BRIN/Partial/Composite, particionado temporal, PgBouncer, PITR backup)
- **GIS / Geo Engineer** (afinidad: PostGIS avanzado, ST_DWithin, ST_MakeLine, ST_Buffer, OSRM/Valhalla, tile servers, clustering)
- **DevOps / Platform Engineer** (afinidad: hosting PostgreSQL+PostGIS, Redis, pooling, backups, Docker, CI/CD database jobs)

---

## Raúl
- Programador FullStack (Backend-heavy: Django, DRF, matching service, reputation service, validation service, domain events, WebSocket consumers)
- Diagramas de casos de uso
- Diagramas UML
- **QA / Test Engineer** (afinidad: UML/casos de uso → diseño de pruebas, pytest unit/integration, Playwright E2E, contract testing, quality gates CI)

---

## Rafa
- Project Manager
- Programador FullStack (Frontend-heavy: Quasar, Vue 3, Pinia, Vue Router, Leaflet/MapLibre, JS vanilla ES Modules, PWA)
- Arquitecto de Software
- **Scrum Master** (afinidad: PM, GitHub Projects Kanban, sprint planning, retro, definición de done)
- **UI/UX Designer** (afinidad: arquitecto define design system, flujos registro→publicar→solicitar→calificar, mapas usables, PWA install flow)

---

## Gabriel
- Programador FullStack (Frontend-heavy: Quasar, Vue 3, Pinia, Leaflet, MapLibre, Swiper, AOS, GLightbox, Service Worker, Push API, Background Sync, a11y)
- Diseñador UI
- Wireframes
- Mockups
- **UI/UX Designer** (afinidad: wireframes, mockups, design system, accesibilidad, responsive design)

---

## Resumen de Cobertura de Roles Críticos

| Rol Crítico Raite | Asignado a | Justificación de Afinidad |
|-------------------|------------|---------------------------|
| Software Architect | Rafa | Ahora lo es en el original |
| DB Architect / DBA | Rogelio | Ya lo era |
| GIS / Geo Engineer | Rogelio | Extensión natural de BD espacial |
| DevOps / Platform Engineer | Rogelio | Extensión natural de infra BD |
| Fullstack Backend (Django/DRF/Geo/Async) | Angel, Rogelio, Raúl | Todos FullStack, Raúl enfocado en lógica dominio |
| Fullstack Frontend (Quasar/Vue/PWA) | Rafa, Gabriel | Perfil UI/UX + arquitecto define design system |
| QA / Test Engineer | Raúl | Diagramas UML/casos de uso → test design |
| Security Engineer | Angel | Backend owner define posture seguridad |
| UI/UX Designer | Rafa, Gabriel | Ya lo eran en el original |
| Product Owner / Analista Funcional | Angel | Análisis requisitos + visión |
| Scrum Master | Rafa | Ya era PM |

---

## Cambios Respecto a v1

| Integrante | Cambio en Original | Impacto en Asignación v2 |
|------------|-------------------|--------------------------|
| **Angel** | Perdió "Arquitecto de Software" | Gana PO + Security (backend owner) |
| **Rafa** | Ganó "Arquitecto de Software" | Asume Architect + Scrum Master + UI/UX |
| **Gabriel** | Ganó "Diseñador UI" | Refuerza UI/UX Designer (ya tenía wireframes/mockups) |
| **Rogelio** | Sin cambios | Mantiene BD + gana GIS/Geo/DevOps |
| **Raúl** | Sin cambios | Mantiene FullStack + gana QA/Test |

---

## Notas de Implementación

1. **Todos los roles originales se reciclan** - ninguno se elimina, solo se expanden
2. **Cada integrante tiene 1-3 roles nuevos** asignados por afinidad natural con su perfil actual
3. **Backend pesado** (3 personas): Angel, Rogelio, Raúl cubren Django, DRF, GeoDjango, PostGIS, Channels, Celery, domain services, matching
4. **Frontend/PWA** (2 personas): Rafa (Architect + UI/UX), Gabriel (UI Designer) cubren Quasar, Vue 3, Pinia, Vue Router, Leaflet, MapLibre, JS modules, Service Worker, Push, a11y
5. **Calidad/Proceso** (2 personas): Raúl (QA técnico), Rafa (Scrum/Proceso + Architect)
6. **Seguridad/Compliance**: Angel (backend owner) + Rogelio (DBA/DevOps) cubren hardening, secrets, LFPDPPP
7. **Geoespacial**: Rogelio centraliza PostGIS/OSRM/tiles por ser DB Architect
8. **Product Ownership**: Angel por visión técnica + requisitos; Rafa (Architect) apoya en decisiones técnicas de producto
9. **Arquitectura**: Rafa define ADRs, dependency rule, wireado DI; Angel y Rogelio implementan en sus capas