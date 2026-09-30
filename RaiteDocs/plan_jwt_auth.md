# Plan: JWT Auth Completo (Frontend + Backend Gaps)

## Objetivo
Implementar autenticación JWT end-to-end: backend gaps + frontend store/interceptor/guards.

---

## Fase 1: Backend - Completar Gaps (Prioridad Alta)

### 1.1 Token Blacklist (Logout seguro)
- [ ] Agregar `'rest_framework_simplejwt.token_blacklist'` a `INSTALLED_APPS`
- [ ] `python manage.py migrate` (crea tablas `token_blacklist_*`)
- [ ] Agregar endpoint `POST /api/token/blacklist/` en `urls.py`:
  ```python
  from rest_framework_simplejwt.views import TokenBlacklistView
  path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
  ```

### 1.2 Endpoint `/api/me/` (Perfil usuario)
- [ ] Crear `UserSerializer` con campos necesarios
- [ ] Crear vista `MeView` (GET `/api/me/`) que retorne `request.user`
- [ ] Registrar en `urls.py`

### 1.3 (Opcional) Refresh Token Rotation
- [ ] `SIMPLE_JWT.ROTATE_REFRESH_TOKENS = True` en settings
- [ ] `SIMPLE_JWT.BLACKLIST_AFTER_ROTATION = True`

### 1.4 Seguridad
- [ ] Mover `SECRET_KEY` a `.env` únicamente
- [ ] `DEBUG = False` en producción
- [ ] Configurar `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, etc.

---

## Fase 2: Frontend - Implementación Global (Prioridad Alta)

### 2.1 Archivos a CREAR
| Archivo | Descripción |
|---------|-------------|
| `src/stores/auth-store.ts` | Pinia store: tokens, user, login/logout/refresh, `initializeAuth()` |
| `src/boot/axios.ts` | Instancia axios + interceptor 401 → refresh automático + cola de requests |
| `src/boot/auth-init.ts` | Boot file: llama `authStore.initializeAuth()` al arrancar |

### 2.2 Archivos a MODIFICAR
| Archivo | Cambio |
|---------|--------|
| `quasar.config.ts` | Agregar `'axios'`, `'auth-init'` al array `boot:` (orden: axios primero) |
| `src/router/index.ts` | Agregar guard global `Router.beforeEach()` para `meta.requiresAuth` |

### 2.3 Detalles Técnicos Clave
- **Interceptor axios**: Maneja 401 → refresh → retry con cola para evitar race conditions
- **Guard global**: Por convención (todas las rutas menos `/login/*` requieren auth) — migración fácil a `<route>` por página después
- **Inicialización**: Al cargar app, si hay access token en localStorage → setea header + fetch user / refresh si falla

---

## Fase 3: Integración Login Page (Prioridad Media)

- [ ] Conectar `LoginPage.vue` con `authStore.login()`
- [ ] Manejo de errores (credenciales inválidas, red, etc.)
- [ ] Redirección post-login según rol o ruta anterior

---

## Fase 4: Testing & Documentación (Prioridad Baja)

- [ ] Probar flujo completo: login → access protected → refresh → logout → login
- [ ] Probar expiración access (30 min) y refresh (1 día)
- [ ] Documentar endpoints finales en `jwt_auth.md` (actualizar estado)

---

## Dependencias entre fases

```
Fase 1.1 (Blacklist) ──┐
Fase 1.2 (/api/me/) ───┼──► Fase 2 (Frontend store/interceptor/guards)
Fase 1.3 (Rotation) ───┘       │
                                ▼
                       Fase 3 (Login page)
                                │
                                ▼
                       Fase 4 (Testing/Docs)
```

---

## Estimación de Esfuerzo

| Fase | Archivos | Complejidad | Tiempo estimado |
|------|----------|-------------|-----------------|
| 1. Backend Gaps | 3-4 | Baja | 30-60 min |
| 2. Frontend Core | 5 | Media | 1-2 horas |
| 3. Login Page | 1 | Baja | 30 min |
| 4. Testing | - | Baja | 30 min |
| **Total** | **~10** | - | **~3-4 horas** |

---

## Preguntas Abiertas / Decisiones Pendientes

1. **¿Cookies HttpOnly vs localStorage?** → **Decidido: localStorage** (Bearer header, simple, estándar SPA)
2. **¿Registro de usuarios en frontend?** → No requiere auth; página pública `/login/signuppage`
3. **¿Roles/permisos en frontend?** → Modelo: `User.roles = ['admin'] | ['pasajero'] | ['conductor'] | ['pasajero','conductor']` (múltiples roles por usuario). Admin es excluyente por lógica de negocio (no se codifica explícitamente).
4. **¿SSR futuro?** → No. Equipo usa **SPA** (default Quasar). `localStorage` disponible en cliente.