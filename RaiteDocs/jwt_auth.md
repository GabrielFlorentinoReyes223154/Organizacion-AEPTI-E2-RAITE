# JWT Authentication - Backend (Estado Actual)

## 1. Configuración Actual

### Settings (`Raite_DjangoRest/settings.py`)

| Configuración | Valor |
|---------------|-------|
| `REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES` | `['rest_framework_simplejwt.authentication.JWTAuthentication']` |
| `SIMPLE_JWT.ACCESS_TOKEN_LIFETIME` | 30 minutos (`timedelta(minutes=30)`) |
| `SIMPLE_JWT.REFRESH_TOKEN_LIFETIME` | 1 día (`timedelta(days=1)`) |
| Algoritmo de firma | HS256 (usa `SECRET_KEY` de Django) |
| `CORS_ALLOWED_ORIGINS` | `['http://localhost:9000']` |

### Dependencias instaladas (`requirements.txt`)

| Paquete | Versión |
|---------|---------|
| `djangorestframework` | 3.18.1 |
| `djangorestframework-simplejwt` | 5.5.1 |
| `PyJWT` | 2.15.1 |

---

## 2. Endpoints Disponibles

Definidos en `Raite_DjangoRest/urls.py` usando vistas built-in de SimpleJWT:

| Método | Endpoint | Vista | Descripción |
|--------|----------|-------|-------------|
| POST | `/api/token/` | `TokenObtainPairView` | Login - devuelve access + refresh token |
| POST | `/api/token/refresh/` | `TokenRefreshView` | Renueva access token usando refresh token |

### Formato de Request/Response

**POST `/api/token/`**
```json
// Request
{
  "email": "user@example.com",
  "password": "password123"
}

// Response (200)
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**POST `/api/token/refresh/`**
```json
// Request
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

// Response (200)
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 3. Flujo de Autenticación Actual

1. **Login**: Cliente envía `email` + `password` a `POST /api/token/`
2. **Respuesta**: Servidor valida credenciales y devuelve `access` (30 min) + `refresh` (1 día)
3. **Almacenamiento**: Cliente guarda ambos tokens (localStorage, memory, cookies)
4. **Requests autenticados**: Cliente envía header `Authorization: Bearer <access_token>`
5. **Validación**: `JWTAuthentication` valida firma, expiración y usuario existe
6. **Acceso a vistas**: Cualquier vista con `permission_classes = [IsAuthenticated]` permite acceso y expone `request.user`
7. **Expiración access**: Cuando access expira (401), cliente usa `refresh` en `POST /api/token/refresh/`
8. **Nuevo access**: Servidor valida refresh (firma, expiración, usuario existe) y emite nuevo access

---

## 4. Protección de Vistas

- **Autenticación global**: Configurada en `REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES`
- **Permisos por vista**: Agregar `permission_classes = [IsAuthenticated]` en cada View/ViewSet
- **Usuario disponible**: `request.user` contiene la instancia de User autenticado

Ejemplo:
```python
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class MiVistaProtegida(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({"usuario": request.user.email})
```

---

## 5. Limitaciones Actuales (Gaps)

| Funcionalidad | Estado | Comentario |
|---------------|--------|------------|
| **Logout / Revocación de tokens** | ❌ No implementado | No hay endpoint `/api/token/blacklist/`. Refresh tokens válidos hasta expiración (1 día) |
| **Endpoint perfil usuario (`/api/me/`)** | ❌ No existe | No hay vista que retorne datos del usuario autenticado |
| **Rotación de refresh tokens** | ❌ Deshabilitado | `ROTATE_REFRESH_TOKENS = False` (default) |
| **Blacklist app** | ❌ No instalada | `rest_framework_simplejwt.token_blacklist` no está en `INSTALLED_APPS` |

---

## 6. Variables de Entorno Relevantes

| Variable | Archivo | Uso |
|----------|---------|-----|
| `SECRET_KEY` | `.env` / `settings.py` | Firma y verificación de tokens JWT |
| `DATABASE_URL` | `.env` | Conexión a BD (necesaria para tabla blacklist futuro) |

---

## 7. Seguridad Actual

- **Tokens en header Authorization** (Bearer token)
- **CORS** restringido a `http://localhost:9000`
- **DEBUG = True** (desarrollo únicamente)
- **SECRET_KEY** hardcodeada en settings (debería estar solo en `.env`)
- **Sin HTTPS** en desarrollo local