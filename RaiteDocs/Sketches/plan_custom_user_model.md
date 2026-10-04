# Plan: User Model Propio (`accounts.Usuario`) + Adaptación del JWT

## Objetivo

Reemplazar el user model por defecto de Django (`auth.User`) por `accounts.Usuario`, definido en
`RaiteDocs/Raite_layout_disposition_001.md:189-205` y detallado en
`RaiteDocs/Raite-Django-Models.md:119-172`. Al terminar:

- El login por correo y el JWT siguen funcionando, sin `EmailBackend` propio.
- El admin de Django sigue funcionando (con `Usuario` registrado en vez de `auth.User`).
- `GET /api/me/` devuelve el payload de `RaiteDocs/Raite-Django-API.md:102-121`.

**Alcance:** solo el modelo y la autenticación. No se crean las apps de dominio
(`vehicles`, `locations`, `rides`, `surveys`, `ratings`, `notifications`, `realtime`, `core`).

---

## 1. Contexto verificado

| Dato | Valor |
|------|-------|
| Versiones | Django 6.1.1, DRF 3.18.1, SimpleJWT 5.5.1 (`Back_Raite/requirements.txt`) |
| **Intérprete** | Usar `python3` del sistema. **`Back_Raite/venv/` es de Windows** (tiene `Scripts/`, no `bin/python`) |
| Base de datos | Neon Postgres vía `DATABASE_URL` en `Back_Raite/.env` |
| Contenido actual de `auth_user` | 6 filas: `rafaelorona12@gmail.com` (staff+superuser), `test@test.com`, 4 con correo vacío |
| Migraciones aplicadas | Solo contrib + `token_blacklist`. No hay apps propias |
| Archivos a modificar | `settings.py`, `views.py`, `urls.py`, `Front_Raite/src/stores/auth-store.ts` |

Modelos de dominio que **dependen** de este user model (sprints futuros, no se tocan ahora):
`Vehiculo.usuario`, `Raite.pasajero`/`Raite.conductor`, `EncuestaFinalizacion.usuario`,
`Calificacion.de_usuario`/`para_usuario`, `Notificacion.usuario`.

---

## 2. Decisiones tomadas

| Decisión | Valor | Motivo |
|----------|-------|--------|
| User model | Un solo modelo `Usuario`; el staff se distingue por `is_staff`/`is_superuser` | Un segundo modelo (`SystemUser`) **no puede entrar a `/admin/`**: el admin solo autentica contra `AUTH_USER_MODEL` (`django/contrib/admin/sites.py:209`) |
| Nombres de campos | Español: `nombre`, `apellidos`, `correo` | `Raite-Django-Models.md:123-136` y `Raite-Django-API.md:102-121` |
| Datos existentes | Reinicio limpio (`flush`) antes de migrar | La migración de `token_blacklist` altera su FK de `int` a `uuid` y en Postgres falla si hay filas |
| `verificado` | **Se mantiene** | Lo pide `Raite-Django-Models.md:135` y el payload de `/api/me/`; el UML se quedó corto |
| `created_at` / `updated_at` | **Se agregan** | El UML los pide; `AbstractUser` solo da `last_login` y `date_joined` |
| Admin | `UserAdmin` completo con fieldsets y formularios propios | Un `UserAdmin` heredado a medias produce `admin.E108` y **tumba `runserver`** |

---

## 3. Orden de operaciones (crítico)

Dos reglas. Invertir cualquiera rompe el backend:

1. **`AUTH_USER_MODEL` en `settings.py` ANTES de `makemigrations`.** Con el setting puesto y la app
   sin registrar, Django lanza `LookupError: No installed app with label 'accounts'`.
2. **`flush` ANTES de `migrate`.** `token_blacklist/models.py:8-9` declara
   `user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True)`. Al cambiar el
   user model, `migrate` ejecuta `ALTER COLUMN user_id int → uuid`, que falla en Postgres si la
   tabla tiene filas.

---

## 4. Fase 1 — Modelos

### 4.1 Archivos a crear

```
Back_Raite/apps/__init__.py
Back_Raite/apps/accounts/__init__.py
Back_Raite/apps/accounts/apps.py
Back_Raite/apps/accounts/models_choices.py
Back_Raite/apps/accounts/models.py
Back_Raite/apps/accounts/signals.py
Back_Raite/apps/accounts/migrations/__init__.py
```

### 4.2 Mapa campo por campo (UML → implementación)

| Campo del UML (`_001.md:189-205`) | ¿Viene de `AbstractUser`? | Implementación |
|-----------------------------------|---------------------------|----------------|
| `id: UUID` | no | `UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` |
| `nombre: String` | no (`first_name`) | `CharField(80)`, `first_name = None` |
| `apellidos: String` | no (`last_name`) | `CharField(80)`, `last_name = None` |
| `correo: String (unique)` | `email` existe pero **no es unique** | `EmailField(unique=True)`, `USERNAME_FIELD = "correo"`, `email = None` |
| `password_hash` | sí (`password`) | nada; no exponer en serializers |
| `rol: Rol` | no | `CharField(choices=Rol.choices, default=Rol.PASAJERO)` |
| `edad: Integer` | no | `PositiveSmallIntegerField(default=18, validators=[Min/MaxValueValidator(17/70)])` |
| `sexo: String` | no | `CharField(choices=Sexo.choices, default=Sexo.PREFIERE_NO_DECIR)` |
| `carrera: String` | no | `CharField(120, default="")` |
| `calificacion: Float (1-5)` | no | `DecimalField(2, 1, default=Decimal("0.0"))` |
| `activo: Boolean` | no | `BooleanField(default=False)` — `True` = tiene raite en curso |
| `created_at` / `updated_at` | **no** | `DateTimeField(auto_now_add=True)` / `auto_now=True` |
| `verificado` | no | `BooleanField(default=False)` |
| — | sí | `username = None` (eliminado) |
| `is_staff`, `is_superuser`, `is_active`, `groups`, `user_permissions`, `last_login`, `date_joined` | sí | heredados, no tocar |
| `puede_crear_raite()` | — | método |
| `puede_aceptar_raite()` | — | método |

### 4.3 `apps/accounts/apps.py`

```python
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"

    def ready(self):
        from . import signals  # noqa: F401
```

`INSTALLED_APPS` debe llevar `'apps.accounts'` (ruta con prefijo `apps.`, no `accounts`).

### 4.4 `apps/accounts/models_choices.py`

```python
from django.db import models


class Rol(models.TextChoices):
    PASAJERO = "PASAJERO", "Pasajero"
    CONDUCTOR = "CONDUCTOR", "Conductor"
    AMBOS = "AMBOS", "Ambos"


class Sexo(models.TextChoices):
    M = "M", "Masculino"
    F = "F", "Femenino"
    X = "X", "Otro"
    PREFIERE_NO_DECIR = "PREFIERE_NO_DECIR", "Prefiere no decir"
```

`Rol` **no** incluye `ADMIN` aunque el UML (`_001.md:171`) lo liste: el admin se representa con
`is_staff`/`is_superuser` (`Raite-Django-Models.md:136`).

### 4.5 `apps/accounts/models.py`

```python
import uuid
from decimal import Decimal

from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from .models_choices import Rol, Sexo


class Usuario(AbstractUser):
    # Heredado de AbstractUser y descartado a favor de los campos en español
    username = None
    first_name = None
    last_name = None
    email = None

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    nombre = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=80)
    correo = models.EmailField(unique=True)
    edad = models.PositiveSmallIntegerField(
        default=18,
        validators=[MinValueValidator(17), MaxValueValidator(70)],
    )
    sexo = models.CharField(
        max_length=16, choices=Sexo.choices, default=Sexo.PREFIERE_NO_DECIR
    )
    carrera = models.CharField(max_length=120, default="")
    rol = models.CharField(max_length=12, choices=Rol.choices, default=Rol.PASAJERO)
    calificacion = models.DecimalField(
        max_digits=2, decimal_places=1, default=Decimal("0.0")
    )
    activo = models.BooleanField(default=False)
    verificado = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "correo"
    REQUIRED_FIELDS = ["nombre", "apellidos", "edad", "sexo", "carrera"]

    objects = UserManager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(edad__gte=17) & Q(edad__lte=70),
                name="edad_en_rango",
            ),
        ]

    def __str__(self):
        return f"{self.nombre_completo} <{self.correo}>"

    @property
    def es_pasajero(self) -> bool:
        return self.rol in {Rol.PASAJERO, Rol.AMBOS}

    @property
    def es_conductor(self) -> bool:
        return self.rol in {Rol.CONDUCTOR, Rol.AMBOS}

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellidos}".strip()

    @property
    def vehiculo_valido(self) -> bool:
        return (
            hasattr(self, "perfil_conductor")
            and self.perfil_conductor.vehiculo_valido
        )

    def puede_crear_raite(self) -> bool:
        return self.es_pasajero and not self.activo and self.verificado

    def puede_aceptar_raite(self) -> bool:
        return self.es_conductor and not self.activo and self.vehiculo_valido


class PerfilConductor(models.Model):
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name="perfil_conductor"
    )
    vehiculo_valido = models.BooleanField(default=False)
    notas_admin = models.TextField(blank=True)
```

**Sobre los `default`:** `edad`, `sexo` y `carrera` llevan default solo para que
`createsuperuser --noinput` funcione (sin ellos, un campo `null=False` sin default hace fallar el
alta por consola). Los defaults no violan el `CheckConstraint` 17–70.

**Sobre `vehiculo_valido`:** se resuelve contra `PerfilConductor`, no contra `Vehiculo`, porque
`vehicles` es un sprint posterior. Cuando exista, `vehicles/services.py` lo mantiene sincronizado.

### 4.6 `apps/accounts/signals.py`

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PerfilConductor, Usuario


@receiver(post_save, sender=Usuario)
def crear_perfil_conductor(sender, instance, created, **kwargs):
    if instance.es_conductor:
        PerfilConductor.objects.get_or_create(usuario=instance)
```

Si el usuario deja de ser conductor, el perfil **no se borra** (conserva `notas_admin`); solo
`vehicles` se encargará de apagar `vehiculo_valido`.

---

## 5. Fase 2 — Admin

### 5.1 Por qué el `UserAdmin` por defecto es peligroso

| Trampa | Comportamiento verificado |
|--------|---------------------------|
| `list_display` heredado (`username`, `email`, `first_name`, `last_name`) | `admin/checks.py:951` (`_check_list_display_item`) valida contra el modelo y devuelve **`admin.E108`**. `runserver` ejecuta los system checks y aborta con `SystemCheckError`: **no levanta ni el admin ni la API** |
| `fieldsets` heredados | **No los validan los checks**: `admin/checks.py:461-466` (`_check_field_spec_item`) hace `except FieldDoesNotExist: return []`. El fallo aparece en runtime como 500 al abrir `/admin/accounts/usuario/add/`: `FieldError: Unknown field(s) (username, email, first_name, last_name) specified for accounts.Usuario` |
| `form` / `add_form` heredados | `django/contrib/auth/forms.py:285` → `UserChangeForm.Meta.model = User` (el modelo **swapped out**). `AdminUserCreationForm` hereda de `UserCreationForm`, cuyo `Meta.fields = ("username",)`. Hay que redeclarar ambas |
| `auth.User` sigue registrado | `django/contrib/auth/admin.py:40` → `@admin.register(User)`. Sin `unregister`, `/admin/auth/user/` sigue "funcionando" sobre la tabla `auth_user` huérfana |

### 5.2 `apps/accounts/admin.py`

```python
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User as AuthUser

from .models import Usuario

try:
    admin.site.unregister(AuthUser)
except admin.sites.NotRegistered:
    pass


class UsuarioCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Repite la contraseña", widget=forms.PasswordInput
    )

    class Meta:
        model = Usuario
        fields = ("correo", "nombre", "apellidos", "edad", "sexo", "carrera", "rol")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UsuarioChangeForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = "__all__"


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    form = UsuarioChangeForm
    add_form = UsuarioCreationForm
    add_form_template = "admin/auth/user/add_form.html"

    fieldsets = (
        (None, {"fields": ("correo", "password")}),
        (
            "Datos personales",
            {"fields": ("nombre", "apellidos", "edad", "sexo", "carrera", "rol")},
        ),
        (
            "Estado en Raite",
            {"fields": ("activo", "verificado", "calificacion")},
        ),
        (
            "Permisos",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Fechas",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "correo",
                    "nombre",
                    "apellidos",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    list_display = (
        "correo",
        "nombre",
        "apellidos",
        "rol",
        "calificacion",
        "activo",
        "is_staff",
    )
    list_filter = (
        "rol",
        "sexo",
        "activo",
        "verificado",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    search_fields = ("correo", "nombre", "apellidos", "carrera")
    ordering = ("correo",)
    readonly_fields = (
        "last_login",
        "date_joined",
        "created_at",
        "updated_at",
        "calificacion",
    )
```

`list_display`, `list_filter`, `search_fields` y `ordering` **propios** son los que evitan el
`admin.E108` que tumba el arranque del servidor.

### 5.3 Qué sobrevive del admin actual

- El site, las URLs `/admin/`, el índice, `AdminSite.login`, la sesión de staff.
- `Group` y `Permission` (los m2m se heredan de `AbstractUser`).
- `django_admin_log`: su FK se remapea sola en la migración.
- El login del admin **pide correo** en vez de "Username", porque `AdminAuthenticationForm` se
  construye sobre `AUTH_USER_MODEL.USERNAME_FIELD`.

Cambios visibles: la URL del listado pasa de `/admin/auth/user/` a `/admin/accounts/usuario/`, y
los usuarios con `is_staff=False` reciben 403 en `/admin/` (igual que hoy).

---

## 6. Fase 3 — Auth y JWT

### 6.1 Qué se borra de `Raite_DjangoRest/views.py`

| Elemento actual | Líneas | Por qué se borra |
|-----------------|--------|-------------------|
| `EmailBackend` | 13-22 | Con `USERNAME_FIELD='correo'` el backend por defecto ya autentica por correo: `django/contrib/auth/backends.py:65-78` hace `username = kwargs.get(UserModel.USERNAME_FIELD)` y luego `get_by_natural_key(username)`. Además usa `check_password_with_timing_attack_mitigation` (línea 75), que el backend manual no aplicaba |
| `CustomTokenObtainPairSerializer` | 25-30 | El de stock ya hace login por correo. `rest_framework_simplejwt/serializers.py:31` → `username_field = get_user_model().USERNAME_FIELD`; línea 41 arma `self.fields[self.username_field]`; línea 46 llama `authenticate(**{self.username_field: ..., "password": ...})`. El hack `username_field = 'email'` depende de un campo que desaparece |
| `CustomTokenObtainPairView` | 33-34 | Se usa `TokenObtainPairView` de stock |
| `UserSerializer`, `MeView` | 37-62 | Se migran a `apps/accounts` con los nombres de campo nuevos |

> El `EmailBackend` actual tenía además `User().set_password(password)` (línea 18) para igualar
> tiempos: es correcto en intención, pero innecesario porque `ModelBackend` ya lo hace mejor.

### 6.2 Qué **no** se toca (verificado)

- **`JWTAuthentication`**: ya es agnóstico al modelo. `rest_framework_simplejwt/authentication.py:36`
  hace `self.user_model = get_user_model()` y la línea 132 hace
  `objects.get(id=user_id)`. Que el `id` pase de `int` a `UUID` no le afecta: el claim viaja como
  string dentro del JWT.
- **`token_blacklist`**: cero líneas de código. Solo su migración altera la FK `int → uuid`.

### 6.3 `Raite_DjangoRest/settings.py`

```python
INSTALLED_APPS = [
    # ... lo actual ...
    'apps.accounts',          # + al final
]

AUTH_USER_MODEL = "accounts.Usuario"   # +
```

- **Borrar** el bloque `AUTHENTICATION_BACKENDS` (líneas 141-144). Deja de hacer falta.
- Opcional del mismo bloque de auth, según `Raite-Django-API.md:14`:
  ```python
  SIMPLE_JWT = {
      'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
      'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
      'ROTATE_REFRESH_TOKENS': True,
      'BLACKLIST_AFTER_ROTATION': True,
  }
  ```
- Corrección aparte: `MAILERS` (línea 135) está mal escrito, debe ser `EMAIL_BACKEND`. No bloquea
  este sprint, pero `verificado` por correo lo necesitará después.

### 6.4 `apps/accounts/serializers.py`, `views.py`, `urls_auth.py`

```python
# serializers.py
from rest_framework import serializers

from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    es_pasajero = serializers.BooleanField(read_only=True)
    es_conductor = serializers.BooleanField(read_only=True)
    roles = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            "id",
            "correo",
            "nombre",
            "apellidos",
            "nombre_completo",
            "rol",
            "calificacion",
            "activo",
            "verificado",
            "es_pasajero",
            "es_conductor",
            "roles",
        ]
        read_only_fields = ["id", "calificacion", "activo", "verificado", "rol"]

    def get_roles(self, obj):
        if obj.is_superuser or obj.is_staff:
            return ["admin"]
        roles = []
        if obj.es_conductor:
            roles.append("conductor")
        if obj.es_pasajero:
            roles.append("pasajero")
        return roles or ["pasajero"]
```

```python
# views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UsuarioSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)
```

```python
# urls_auth.py
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import MeView

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("me/", MeView.as_view(), name="me"),
]
```

`password` nunca aparece en el serializer. La búsqueda en el admin es el único filtro de permisos
del `UserAdmin`; para las rutas protegidas por rol del API (`IsAdmin`, `IsPassenger`, `IsDriver`)
ver `RaiteDocs/Raite-Django-API.md:436-447` — se implementan en el sprint de permisos.

### 6.5 `Raite_DjangoRest/urls.py`

Borrar el import `from .views import MeView, CustomTokenObtainPairView` (línea 23) y las cuatro rutas
de token/me (líneas 27-30), y dejar:

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls_auth')),
]
```

Adopta la ruta de la spec (`Raite-Django-API.md:13`). Si se prefiere no tocar el front, se puede
dejar `api/token/`; la diferencia es el prefijo.

---

## 7. Fase 4 — Frontend

`Front_Raite/src/stores/auth-store.ts`:

```ts
// línea 5-10
interface User {
  id: string;       // era number; ahora es UUID
  correo: string;   // era email
  nombre: string;
  apellidos: string;
  roles: string[];
}
```

- Línea 29 (`login`): el body pasa de `{ email, password }` a `{ correo, password }`.
- Líneas 38, 50, 54: URLs → `/api/auth/token/blacklist/`, `/api/auth/token/refresh/`, `/api/auth/me/`.

**No cambia nada más:** `roles` sigue siendo `['admin'] | ['conductor'] | ['pasajero']`, así que los
getters `isAdmin`/`isConductor`/`isPasajero`, `router/index.ts` y `LoginPage.vue` quedan intactos.
`SignUpPage.vue` todavía no llama a la API (el registro llega en el sprint de `accounts`).

---

## 8. Fase 5 — Migraciones y datos

```bash
cd Back_Raite

# 1) settings.py ya tiene AUTH_USER_MODEL + 'apps.accounts'  ← antes de makemigrations
# 2) ya existen los archivos de apps/accounts/

python3 manage.py flush --noinput    # borra las 6 filas de auth_user,
                                     # django_admin_log y token_blacklist_*

python3 manage.py makemigrations accounts
python3 manage.py migrate
python3 manage.py createsuperuser   # pide: correo, nombre, apellidos, edad, sexo, carrera
python3 manage.py check
```

El `flush` va **antes** de `makemigrations`: `flush` emite la señal `post_migrate` (para recrear
content types y permisos), y así corre con la base ya vacía y sin migraciones propias pendientes.

`flush` es destructivo sobre la BD de desarrollo: borra también el historial del admin y los tokens
emitidos. Es aceptable porque el usuario admin se recrea en el paso siguiente con el mismo correo y
contraseña.

---

## 9. Fase 6 — Tests

`apps/accounts/tests/test_models.py`:
- `edad` 16 y 71 lanzan `IntegrityError`; 17 y 70 se guardan.
- `nombre_completo` con nombres vacíos no produce espacios sueltos.
- `es_pasajero` / `es_conductor` para los tres valores de `Rol`.
- `puede_crear_raite()` es `False` si `verificado=False` o `activo=True`.
- `puede_aceptar_raite()` es `False` sin `perfil_conductor.vehiculo_valido`.
- La señal crea `PerfilConductor` solo cuando `rol` es `CONDUCTOR` o `AMBOS`.
- `correo` duplicado lanza `IntegrityError`.
- `authenticate(correo=..., password=...)` devuelve el usuario; contraseña incorrecta devuelve `None`.

`apps/accounts/tests/test_auth_api.py`:
- `POST /api/auth/token/` con `{correo, password}` → `200` con `access` y `refresh`.
- Mismo endpoint con contraseña incorrecta → `401`.
- `POST /api/auth/token/` con `{email, ...}` → `400` (el campo ya no existe).
- `GET /api/auth/me/` con token → `200`, incluye `correo`, `nombre_completo`, `roles`, y **no**
  incluye `password` ni `is_superuser`.
- `GET /api/auth/me/` sin token → `401`.
- `GET /api/auth/token/blacklist/` con refresh → revoca y el refresh posterior → `401`.

Ejecutar con `python3 manage.py test apps.accounts` (el proyecto no usa pytest).

---

## 10. Fase 7 — Verificación manual

```bash
python3 manage.py makemigrations --check --dry-run   # sin cambios pendientes
python3 manage.py check                              # sin admin.E108
python3 manage.py test apps.accounts
python3 manage.py runserver
```

- [ ] Entrar a `http://localhost:8000/admin/` — el campo de login dice **correo**, y `/admin/accounts/usuario/`
      lista usuarios, permite dar de alta y cambiar contraseña.
- [ ] `curl -X POST http://localhost:8000/api/auth/token/ -H 'Content-Type: application/json' \
      -d '{"correo":"<superuser>","password":"<password>"}'` → `200` con `access`/`refresh`.
- [ ] `curl http://localhost:8000/api/auth/me/ -H 'Authorization: Bearer <access>'` → el payload de
      `RaiteDocs/Raite-Django-API.md:102-121`.
- [ ] `pnpm dev` en `Front_Raite` → login correcto con ese superuser.

Si `manage.py check` reporta `admin.E108`, el problema está en `list_display` de `UsuarioAdmin`
(se reference un campo que `Usuario` ya no tiene).

---

## 11. Riesgos y desviaciones

| Riesgo | Mitigación |
|--------|------------|
| `edad`/`sexo`/`carrera` con `default` (la spec dice `null=no` sin default) | Desviación consciente: sin ella `createsuperuser --noinput` falla. Los defaults no violan el `CheckConstraint` 17–70 |
| Se pierden los 6 usuarios de `auth_user` | 4 con correo vacío (basura), 1 de prueba, 1 superuser que se recrea |
| URL del listado: `/admin/auth/user/` → `/admin/accounts/usuario/` | Solo marcadores |
| `token_blacklist` con `user_id` NULL en filas previas | El `flush` las elimina; las nuevas se guardan bien |
| `MAILERS` mal escrito en `settings.py:135` | Sin impacto ahora; se corrige a `EMAIL_BACKEND` |
| JWT emitidos antes del cambio | Quedan inválidos (el `id` cambia de `int` a `UUID`) |
| `verificado` no está en el UML | Mantenido por Models.md y por el contrato de `/api/me/` |
| `Usuario.activo` no tiene tarea que lo reconcilie | Pendiente del cron diario (`Raite-Django-API.md:477-485`) |

---

## 12. Rollback

`flush` es destructivo, así que conviene tener esto claro antes de ejecutar:

1. `git checkout -- Back_Raite/Raite_DjangoRest/settings.py Back_Raite/Raite_DjangoRest/views.py Back_Raite/Raite_DjangoRest/urls.py`
2. Borrar `Back_Raite/apps/`.
3. La tabla `auth_user` **no se reconstruye sola** (con `AUTH_USER_MODEL` en un modelo propio,
   `auth/migrations/0001_initial.py:196` la marca `swappable` y Django no la crea). Para volver
   atrás hay que ejecutar el SQL a mano sobre Postgres:
   ```sql
   DROP TABLE IF EXISTS accounts_usuario CASCADE;
   -- y recrear auth_user con el esquema de Django 6.1 antes de migrate
   ```
4. `python3 manage.py makemigrations && python3 manage.py migrate`

Por eso el orden es: modelar y verificar en local primero, y tratar el `flush` como el punto sin
retorno de la migración de datos.

---

## 13. Checklist de ejecución

- [ ] `settings.py`: `+AUTH_USER_MODEL`, `+'apps.accounts'`, `-AUTHENTICATION_BACKENDS`
- [ ] `apps/__init__.py`, `apps/accounts/__init__.py`, `apps.py`, `models_choices.py`
- [ ] `models.py` con `Usuario` + `PerfilConductor`
- [ ] `signals.py` con la señal `post_save`
- [ ] `admin.py` con `UsuarioAdmin` completo + `unregister(auth.User)`
- [ ] `serializers.py` con `UsuarioSerializer`
- [ ] `views.py` con `MeView`, `urls_auth.py` con las 4 rutas
- [ ] `Raite_DjangoRest/views.py` eliminado
- [ ] `urls.py` con `path('api/auth/', include('apps.accounts.urls_auth'))`
- [ ] `auth-store.ts`: `interface User`, body del login, 4 URLs
- [ ] `flush --noinput`
- [ ] `makemigrations accounts`
- [ ] `migrate`
- [ ] `createsuperuser`
- [ ] `tests/test_models.py` y `tests/test_auth_api.py` en verde
- [ ] Verificación manual de la Fase 7 completa
- [ ] `graphify update .`
- [ ] **No hacer `git commit`** — dejar los cambios para revisión

---

## 14. Referencias

**Specs del proyecto**
- `RaiteDocs/Raite_layout_disposition_001.md:189-205` — clase `Usuario` del UML
- `RaiteDocs/Raite_layout_disposition_001.md:171-176` — enum `Rol` (incluye `ADMIN`, descartado)
- `RaiteDocs/Raite-Django-Models.md:119-172` — campos, constraints y properties
- `RaiteDocs/Raite-Django-Apps.md:22-24, 156` — ubicación de la app y `AUTH_USER_MODEL`
- `RaiteDocs/Raite-Django-API.md:13, 42-121` — endpoints de auth y payload de `/api/me/`
- `RaiteDocs/Raite_layout_disposition.md:8-11` — campos del formulario de registro

**Código de Django 6.1 instalado (para verificar decisiones)**
- `django/contrib/auth/backends.py:65-78` — `ModelBackend` con `USERNAME_FIELD`
- `django/contrib/auth/forms.py:285` — `UserChangeForm.Meta.model = User`
- `django/contrib/auth/admin.py:40` — `@admin.register(User)` (hay que desenregistrar)
- `django/contrib/admin/sites.py:209` — `has_permission` exige `is_staff`
- `django/contrib/admin/checks.py:951` — `admin.E108` en `list_display`
- `django/contrib/admin/checks.py:461-466` — los `fieldsets` con campos desconocidos **no** se validan
- `django/contrib/auth/migrations/0001_initial.py:196` — `auth.User` es `swappable`

**SimpleJWT 5.5**
- `serializers.py:31, 41, 46` — el serializer usa `USERNAME_FIELD`
- `authentication.py:36, 132` — `get_user_model()`, agnóstico al modelo
- `token_blacklist/models.py:8-9` — FK a `AUTH_USER_MODEL`
