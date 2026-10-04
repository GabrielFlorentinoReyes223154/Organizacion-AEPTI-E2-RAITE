# Primera Corrección — Fase 2: Alineación de `apps/accounts` con `Raite_layout_disposition_002.md`

> **Documento de instrucciones ejecutable.** Cada corrección indica la referencia exacta en
> `RaiteDocs/Raite_layout_disposition_002.md`, el estado actual en código (archivo:línea) y el estado
> objetivo. Un agente de IA debe seguir el orden de la §4 y no eliminar pasos.

---

## 0. Objetivo y alcance

`002.md` describe el sistema completo. El código actual solo tiene `apps/accounts` con
`Usuario`, `PerfilConductor` y `Vehiculo`, y **5 divergencias de fondo** que invalidan el modelo de
dominio sobre el que se construiría todo lo demás (roles, sexo, ocupación, sanción, admin).

**Alcance de esta fase:** corregir esas 5 divergencias bloqueantes (C1–C5) más las 5 secundarias
(C6–C10) que las sostienen. **Fuera de alcance:** crear `Raite`, `RaiteIntento`, `PuntoMapeado`,
`EncuestaFinalizacion`, `TicketRevision`, `Notificacion`, `GestorUbicacionLive`, los endpoints de
raite, el Panel de Administración, Leaflet/GPS y el WebSocket (fase 3 en adelante).

**Resultado esperado:** al terminar, `apps/accounts` es *compatible* con el modelo documentado y
`Raite.sincronizar_cuenta_activa()` puede escribirse en la fase 3 sin pelearse con el esquema.

---

## 1. Reglas de ejecución (obligatorias para el agente)

1. **Una corrección por commit.** Nunca mezcles C3 y C4 en el mismo commit: cada una genera su
   migración y su `makemigrations` debe producir exactamente los campos esperados.
2. **Migración manual, no automática ciega.** Tras cada cambio de modelos ejecuta
   `python3 manage.py makemigrations accounts` y **lee el archivo generado**. Si aparecen operaciones
   no esperadas (`AlterField` sobre campos que no tocaste, `DeleteModel` de algo que no quitaste),
   revierte antes de aplicar.
3. **Datos existentes.** Cada migración que rompa filas existentes debe incluir un `RunPython` con
   `reverse_code`. Los datos de `Back_Raite/db.sqlite3` y de Postgres son de desarrollo: si una
   migración es irrecuperable, dilo en el resumen del commit en lugar de inventar un backup.
4. **Verificación obligatoria antes de pasar a la siguiente corrección:**
   ```bash
   cd Back_Raite
   DATABASE_URL="sqlite:///tmp_test.sqlite3" python3 manage.py test apps --noinput
   ```
   Debe terminar en `OK`. (El `DATABASE_URL` con SQLite es necesario: el `DATABASE_URL` del `.env`
   apunta a Postgres y la base de datos de pruebas está ocupada.)
5. **No inventes functionality.** Si un campo del doc depende de `Raite` (todos los de `Raite.*`),
   no lo implementes aquí: créalo como campo inerte o.properties que leen la caché, y déjalo
   anotado en §6 de este documento.
6. **No toques `Front_Raite` salvo en C10.** El frontend se alinea cuando el contrato de API cambie.
7. **Actualiza `002.md` solo si detecta que el doc es contradictorio internamente.** Si el código y
   el doc discrepan, **el doc gana** (salvo indicación explícita en contrario). Si el doc se
   contradice a sí mismo, no lo resuelvas por tu cuenta: anótalo en §7.
8. **`graphify update .`** al cerrar la fase.

---

## 2. Resumen de correcciones

| ID | Corrección | Prioridad | Doc | Archivo principal |
|----|-----------|-----------|-----|-------------------|
| **C1** | Roles → tabla `UsuarioRol`; `AMBOS` deja de ser valor almacenado | 🔴 Bloqueante | L11, L53, L270-274, L507-511, L559-563, L712-720 | `models.py`, `models_choices.py` |
| **C2** | `sexo` sin `PREFIERE_NO_DECIR`, obligatorio | 🔴 Bloqueante | L57 | `models_choices.py`, `models.py` |
| **C3** | `activo` (bool) + `cuenta_activa` (Integer) = caché de ocupación | 🔴 Bloqueante | L61, L284-285, L292, L306, L549-550, L996-1003 | `models.py` |
| **C4** | `suspendido` (sanción) reemplaza a `verificado` | 🔴 Bloqueante | L58, L263-268, L551, L926-940 | `models.py`, `admin.py` |
| **C5** | `ADMIN` como rol real, independiente y exclusivo de `is_staff`/`is_superuser` | 🔴 Bloqueante | L54-56, L59, L450 | `models.py`, `permissions.py`, `serializers.py` |
| C6 | `Vehiculo`: `es_valido_para_conducir()` / `tiene_capacidad()`; eliminar `PerfilConductor` | 🟡 Alta | L60, L565-578, L1005-1012 | `models.py`, `signals.py` |
| C7 | `no_tiene_raite_en_curso()` y reescritura de `puede_*_raite()` | 🟡 Alta | L554-556, L380, L806-819 | `models.py` |
| C8 | Limpieza de código muerto (`urls.py`, serializers, `if…pass`, `notas_admin`) | 🟢 Media | — | varios |
| C9 | `calificacion` acotada a 0–5 | 🟢 Media | L278, L548 | `models.py` |
| C10 | Contrato de registro alineado al doc (`roles` sin `ADMIN`) | 🟡 Alta | L11-12 | `serializers.py`, `views.py` |

---

## 3. Correcciones en detalle

---

### 🔴 C1 — Roles: tabla `UsuarioRol`, sin `AMBOS` almacenado

**Doc (referencia exacta)**
- L11: *"Usuario elige: Pasajero, Conductor, o Ambos (marca ambos = 2 filas en `UsuarioRol`)"*
- L270-274: un usuario tiene **N** filas; **Único** por `(usuario_id, rol)`; **"Ambos" no es un valor
  almacenado**; un `ADMIN` no requiere `Vehiculo`.
- L507-511: `enum Rol { PASAJERO, CONDUCTOR, ADMIN }` — **no existe `AMBOS`**.
- L712-716: *"Un usuario con PASAJERO y CONDUCTOR (dos filas en UsuarioRol) es 'AMBOS' en la interfaz.
  No es un valor del enum."*

**Estado actual**
- `models_choices.py:4-7` — `Rol` = `PASAJERO | CONDUCTOR | **AMBOS**`. Sin `ADMIN`.
- `models.py:50` — `rol = models.CharField(max_length=12, choices=Rol.choices, default=Rol.PASAJERO)`
  (un solo valor).
- `models.py:82-88` — `es_pasajero` / `es_conductor` derivan de ese único campo.
- No existe la tabla `UsuarioRol`.

**Objetivo**

`models_choices.py`:
```python
class Rol(models.TextChoices):
    PASAJERO = "PASAJERO", "Pasajero"
    CONDUCTOR = "CONDUCTOR", "Conductor"
    ADMIN = "ADMIN", "Admin"


class TipoVehiculo(models.TextChoices):
    CAMIONETA = "CAMIONETA", "Camioneta"
    COCHE = "COCHE", "Coche"
    TROCA = "TROCA", "Troca"
```

`models.py` — **eliminar** el campo `Usuario.rol` y añadir:
```python
class UsuarioRol(models.Model):
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="usuario_roles"
    )
    rol = models.CharField(max_length=12, choices=Rol.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["usuario", "rol"], name="unico_usuario_rol"),
        ]

    def __str__(self):
        return f"{self.usuario_id} · {self.rol}"
```
> Sin `id` propio explícito: el `id` implícito de Django (BigAutoField) es equivalente al `UUID` del
> UML. **No añadas `creado_en`**: el doc (L559-563) no lo define.

Propiedades en `Usuario` (reemplazan a las actuales):
```python
    def tiene_rol(self, rol: str) -> bool:
        return self.usuario_roles.filter(rol=rol).exists()

    @property
    def es_pasajero(self) -> bool:
        return self.tiene_rol(Rol.PASAJERO)

    @property
    def es_conductor(self) -> bool:
        return self.tiene_rol(Rol.CONDUCTOR)

    @property
    def es_admin(self) -> bool:
        return self.tiene_rol(Rol.ADMIN)
```

`UsuarioManager.create_user` acepta `roles` y crea las filas (L270-271):
```python
    def create_user(self, correo, password=None, roles=None, **extra_fields):
        if not correo:
            raise ValueError("El correo es obligatorio")
        correo = self.normalize_email(correo)
        if extra_fields.get("rol"):
            raise ValueError(
                "El rol ya no es un campo de Usuario. Usa roles=['PASAJERO', 'CONDUCTOR']."
            )
        user = self.model(correo=correo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        for rol in roles if roles is not None else [Rol.PASAJERO]:
            UsuarioRol.objects.create(usuario=user, rol=rol)
        return user
```
> Default `[Rol.PASAJERO]` para mantener la ergonomic de `create_user` en tests y consola. Doc L12:
> el registro público nunca ofrece `ADMIN`.

`REQUIRED_FIELDS` (L67) queda `["nombre", "apellidos", "edad", "sexo", "carrera"]` (sin cambios).

**Migraciones** (una sola, `_usuarios_a_tabla_roles`):
1. `CreateModel` `UsuarioRol`.
2. `RemoveField` `Usuario.rol`.
3. `RunPython` que crea una fila por usuario: `AMBOS` → `[PASAJERO, CONDUCTOR]`; `CONDUCTOR` →
   `[CONDUCTOR]`; `PASAJERO` → `[PASAJERO]`. `reverse_code` elimina las filas y **no** puede
   recuperar el valor de `rol` (avísalo en el mensaje del commit).
4. `AddConstraint` `unico_usuario_rol`.

**Criterios de aceptación**
- [ ] `Rol` no contiene `AMBOS`; `Usuario` no tiene campo `rol`.
- [ ] Un usuario con filas `PASAJERO`+`CONDUCTOR` tiene `es_pasajero is True` y `es_conductor is True`,
      sin ningún valor "AMBOS" almacenado.
- [ ] `create_user(correo, password, rol=Rol.PASAJERO)` lanza `ValueError` con mensaje explícito.
- [ ] Intentar `(mismo_usuario, mismo_rol)` dos veces → `IntegrityError`.

---

### 🔴 C2 — `sexo` obligatorio, sin `PREFIERE_NO_DECIR`

**Doc (L57)**
> *"`sexo` es obligatorio y sin opción 'prefiere no decir'. Por seguridad de los estudiantes no se
> permite la opción de no verificar el sexo biológico. El catálogo de `Sexo` no debe incluir
> `PREFIERE_NO_DECIR` ni valores vacíos"*

**Estado actual**
- `models_choices.py:14` — existe `PREFIERE_NO_DECIR = "PREFIERE_NO_DECIR", "Prefiere no decir"`.
- `models.py:46-48` — `default=Sexo.PREFIERE_NO_DECIR` (es decir, **opcional de hecho**).

**Objetivo**
```python
class Sexo(models.TextChoices):
    M = "M", "Masculino"
    F = "F", "Femenino"
    X = "X", "Otro"
```
```python
    sexo = models.CharField(max_length=20, choices=Sexo.choices)
```
> **Sin `default`** → Django exige el valor. `X = "Otro"` se conserva: es una respuesta real, no una
> evasión. `blank=False` implícito.

**Migración** (`_sexo_sin_prefiere_no_decir`): `AlterField` en `Usuario.sexo` + `RunPython` que
convierte las filas `PREFIERE_NO_DECIR` a `Sexo.X`. Deja un `print()` con el número de filas
afectadas y menciónalo en el commit: es una decisión de negocio, no un refactor silencioso.

**Criterios de aceptación**
- [ ] `Sexo.PREFIERE_NO_DECIR` no existe.
- [ ] `Usuario.objects.create_user(...)` sin `sexo` → `IntegrityError`/`ValidationError`.
- [ ] No queda ninguna fila con el valor antiguo.

---

### 🔴 C3 — `activo` (bool) y `cuenta_activa` (Integer) como caché de ocupación

**Doc (referencia exacta)**
- L61: *"`Usuario.activo` y `Usuario.cuenta_activa` **son caché, no fuente de verdad**. `Usuario.activo`
  significa **"el usuario está ocupado en un Raite activo"**, NO "la cuenta está habilitada"… **única**
  estrategia de sincronización: `Raite.sincronizar_cuenta_activa()`"*.
- L284-285 / L292: `activo: Boolean` (ocupado) y `cuenta_activa: **Integer**` (nº de raites activos;
  "se mantiene `Integer` —y no `Boolean`— por compatibilidad"; "No es un `Boolean`").
- L328: *"Usuario no expone ninguna operación que escriba su propio estado de ocupación por
  iniciativa propia"*.
- L380 / L813-819: `no_tiene_raite_en_curso()` lee `cuenta_activa == 0`; exige índice único parcial o
  lock pesimista para evitar carrera.

**Estado actual (inversión de semántica)**
- La migración `0003_remove_usuario_activo_usuario_cuenta_activa.py` **borró `activo`** y creó
  `cuenta_activa = BooleanField(default=True)` con el comentario
  `# True = cuenta habilitada (no penalizada)` (`models.py:54`).
- Consecuencia: `cuenta_activa=True` significa lo **opuesto** a lo documentado, y `activo` desapareció.

**Objetivo**
```python
    activo = models.BooleanField(default=False)
    """CACHÉ: True = el usuario está OCUPADO en un Raite activo.
    NO significa "cuenta habilitada" (eso es `is_active`). Lo escribe exclusivamente
    Raite.sincronizar_cuenta_activa() en la fase 3."""

    cuenta_activa = models.PositiveSmallIntegerField(default=0)
    """CACHÉ: nº de Raites activos del usuario. Invariante 0..1. Integer, no Boolean."""
```
Y **eliminar** `is_active` como concepto de ocupación. `is_active` se conserva (lo usa
`AbstractBaseUser` y el login) con su significado real: *cuenta habilitada por el Admin*. Deja un
comentario junto a `is_active`:# Habilitación de la cuenta (login permitido aunque esté suspendido).

**Invariantes a codificar ahora (fase 3 las completará)**
- No expongas `activo` ni `cuenta_activa` como escribibles en ningún serializer ni en el admin:
  `read_only_fields` en `UsuarioSerializer`, `readonly_fields` en `UsuarioAdmin`.
- No añadas `Usuario.set_activo()`, `Usuario.marcar_ocupado()` ni nada equivalente (L328). La
  escritura llega con `Raite`.
- Invariante `cuenta_activa <= 1` documentada en el docstring del campo.

**Migración** (`_ocupacion_como_cache`):
1. `AddField` `activo = BooleanField(default=False)`.
2. `AlterField` `cuenta_activa` → `PositiveSmallIntegerField(default=0)`.
   La conversión de `True → 1` / `False → 0` la hace Django en el `ALTER` (SQLite rescribe la tabla).
   Verifica el resultado con `SELECT DISTINCT cuenta_activa FROM accounts_usuario;` antes de seguir:
   solo deben existir `0` y `1`.

**Criterios de aceptación**
- [ ] `Usuario.activo` existe y es `False` por defecto.
- [ ] `Usuario.cuenta_activa` es `IntegerField` con default `0` (no `BooleanField`).
- [ ] `type(user.cuenta_activa) is int`.
- [ ] `activo`/`cuenta_activa` no aparecen editables en `/api/auth/me/` ni en el Django admin.
- [ ] Ningún método de `Usuario` escribe `activo`/`cuenta_activa`.

---

### 🔴 C4 — `suspendido` (sanción) en lugar de `verificado`

**Doc (referencia exacta)**
- L58: *"`Usuario.suspendido=true` cuando el usuario acumula **`MAX_TICKETS_SUSPENSION = 3`** tickets
  resueltos en su contra. Mientras está suspendido **no puede crear ni tomar raites**; **el login sigue
  permitido**… La regla es **simétrica** para pasajero y conductor."*
- L263-268: es **independiente** del estado de ocupación; **no se borra al liberar raites**; solo el
  Admin lo levanta; conteo **derivado** (`COUNT(TicketRevision) WHERE implicado=X AND estado=RESUELTO`),
  sin contador almacenado.
- L926-940: *"SANCION, no caché: NO se refresca desde Raite ni se borra al liberar raites."*

**Estado actual**
- No existe `suspendido`.
- Existe `verificado = BooleanField(default=False)` (`models.py:55`), que **no aparece en el doc**.
  Solo se pone en `True` a mano desde el admin, y `puede_crear_raite()` lo exige
  (`models.py:114`) → **ningún usuario registrado puede crear un raite jamás** (deadlock, sec. 5.1
  de la auditoría).

**Objetivo**
```python
    suspendido = models.BooleanField(default=False)
    """SANCIÓN, no caché: no se refresca desde Raite ni se borra al liberar raites.
    Lo activa el Admin o la regla MAX_TICKETS_SUSPENSION=3 tickets RESUELTOS en contra
    (derivada por COUNT sobre TicketRevision; sin contador almacenado).
    Bloquea crear() y aceptar() por igual; el login sigue permitido.
    Solo el Admin puede levantarlo."""
```
**Eliminar** el campo `verificado` y todas sus referencias (`models.py:114`, `admin.py:59`,
`admin.py:114`, `serializers.py:23`, `serializers.py:28`, `serializers.py:71`, `views.py:35`).

**Matiz importante (no lo saltes):** el doc **no** contempla verificación de correo. Si el equipo la
quiere, debe **añadirse a `002.md` primero**. No la reimplementes por intuición.

`RegistroResponseSerializer` (`serializers.py:68-72`) y la respuesta de `RegistroView`
(`views.py:32-37`) exponen `verificado`: **cambiar ese campo por `suspendido`** y actualizar el
consumidor (`Front_Raite/src/stores/auth-store.ts` no lo lee; `UsuarioSerializer` sí lo expone →
reemplazar en `fields`).

**Migración** (`_verificado_a_suspendido`): `AddField` `suspendido` + `RemoveField` `verificado`.
> `RemoveField` **destruye** la columna y su contenido. Antes de aplicar, ejecuta
> `SELECT COUNT(*) FROM accounts_usuario WHERE verificado = true;` y reporta el número. Si es `> 0`,
> **detente y pregunta** en lugar de perder el dato.

**Criterios de aceptación**
- [ ] `Usuario.suspendido` existe, default `False`, y no hay campo `verificado`.
- [ ] `suspendido` es editable **solo** en el Django admin; `read_only` en la API.
- [ ] `puede_crear_raite()` y `puede_aceptar_raite()` devuelven `False` con `suspendido=True`.
- [ ] El login (`/api/auth/token/`) sigue funcionando con `suspendido=True`.

---

### 🔴 C5 — `ADMIN` como rol real e independiente

**Doc (referencia exacta)**
- L54: *"El rol `ADMIN` **no está disponible en el registro público**. Solo un Admin existente lo otorga."*
- L55: *"El rol `ADMIN` es **independiente y NO implica `PASAJERO` ni `CONDUCTOR`**. Asignar `ADMIN` no
  crea filas adicionales en `UsuarioRol`… **está exento de poseer `Vehiculo`**."*
- L56: *"Si un administrador quiere operar en la plataforma… debe **adquirir ese rol por separado**…
  `ADMIN + PASAJERO` y `ADMIN + CONDUCTOR` son combinaciones válidas, pero **opt-in**, nunca automáticas."*
- L59: *"`is_superuser` / `is_staff` son **exclusivos del rol `ADMIN`**. Ninguna cuenta que sea solo
  `PASAJERO`, solo `CONDUCTOR` o `Ambos` puede tenerlos en `true`… quien las tenga `true` debe poseer
  la fila `ADMIN` en `UsuarioRol`."*
- L457: *"Solo `ADMIN` accede"* al bandeja de revisión.

**Estado actual**
- No existe el rol `ADMIN` en el enum.
- `permissions.py:4-6` — `IsAdmin` valida **solo** `request.user.is_staff`.
- `serializers.py:30-38` — `get_roles()` **deriva** `"admin"` de `is_staff`/`is_superuser` (circular:
  el permiso deriva del flag en vez de al revés).
- `Rol` no incluye `ADMIN`, así que el registro público tampoco puede filtrarlo: hoy nadie puede ser
  Admin en el modelo.

**Objetivo — 1. Guardia de exclusividad en `Usuario.save()`**
```python
    def save(self, *args, **kwargs):
        if self.is_staff or self.is_superuser:
            if not UsuarioRol.objects.filter(usuario=self, rol=Rol.ADMIN).exists():
                raise ValidationError(
                    "is_staff/is_superuser son exclusivos del rol ADMIN: "
                    "el usuario debe tener la fila ADMIN en UsuarioRol."
                )
        super().save(*args, **kwargs)
```
> Esto implementa directamente L59. Requiere `from django.core.exceptions import ValidationError`.
> Consecuencia: **hay que crear primero la fila `ADMIN` y después activar los flags** (ver abajo).

**Objetivo — 2. `create_superuser` debe respetar la guarda**
```python
    def create_superuser(self, correo, password, **extra_fields):
        extra_fields.setdefault("is_active", True)
        user = self.model(correo=self.normalize_email(correo), **extra_fields)
        user.is_staff = False
        user.is_superuser = False
        user.set_password(password)
        user.save(using=self._db)                     # pasa la guarda
        UsuarioRol.objects.create(usuario=user, rol=Rol.ADMIN)
        user.is_staff = True
        user.is_superuser = True
        user.save(update_fields=["is_staff", "is_superuser"])   # ahora sí pasa
        return user
```
> Verifica que `create_superuser` siga exigiendo `is_staff=True` e `is_superuser=True` en
> `extra_fields` (prueba que hoy existe, `models.py:28-31`). **Muévela antes** del `setdefault`.

**Objetivo — 3. `IsAdmin` derivado del rol, no del flag**
```python
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.es_admin)
```

**Objetivo — 4. `get_roles()` lee `UsuarioRol`**
```python
    def get_roles(self, obj):
        return [r.rol.lower() for r in obj.usuario_roles.all()]
```
> L273: un usuario con `PASAJERO`+`CONDUCTOR` produce `["pasajero", "conductor"]` → "ambos" en la UI.
> Un `ADMIN` puro produce `["admin"]` y **no** `["pasajero"]`. Esto elimina el
> `return roles or ["pasajero"]` actual, que mentía sobre los roles de un admin.
> `IsPassenger`/`IsDriver` (`permissions.py:9-16`) ya leen `es_pasajero`/`es_conductor`, que tras C1
> consultan `UsuarioRol`: no requieren cambios.

**Objetivo — 5. Exención de vehículo y no-derivación de roles**
`Rol.ADMIN` no debe crear `UsuarioRol` de `PASAJERO`/`CONDUCTOR` (L55) — no añadas ninguna lógica que
lo haga. El `Paso 2` (vehículo) ya se salta al Admin por `VehiculoRegistroView`, que exige
`user.es_conductor` (`views.py:49-53`): es el comportamiento correcto según L55/L56, **déjalo así**.

**Criterios de aceptación**
- [ ] Un usuario con `PASAJERO`+`CONDUCTOR` y `is_staff=True` → `ValidationError` en `save()`.
- [ ] `create_superuser(...)` funciona y deja `is_staff=True`, `is_superuser=True` **y** una fila
      `ADMIN` en `UsuarioRol`.
- [ ] `POST /api/auth/register/` con `roles=["ADMIN"]` → `400`.
- [ ] `/api/auth/me/` de un admin puro devuelve `roles: ["admin"]` (no `["admin","pasajero"]`).
- [ ] `POST /api/auth/vehicle/` de un admin puro → `403` (no posee `CONDUCTOR`).

---

### 🟡 C6 — `Vehiculo`: métodos del doc y fin de `PerfilConductor`

**Doc (referencia exacta)**
- L565-578: `Vehiculo` con `es_valido_para_conducir(): Boolean` y
  `tiene_capacidad(requeridos: Integer): Boolean`.
- L60: *"Perfil de conductor **requiere vehículo válido** (`Vehiculo.es_valido_para_conducir()`) para
  activar modo 'Dar Raite'."*
- L403: *"`Vehiculo.es_valido_para_conducir()` → existe, completo y activo"*;
  L404: *"`Vehiculo.tiene_capacidad(Raite.pasajeros_requeridos)` → hay asientos libres"*.
- L1005-1012: `activo=false` = inválido → no puede dar raite.
- L21: *"`activo=false` → `es_valido_para_conducir()` = `false` y el modo 'Dar Raite' queda bloqueado"*.

**Estado actual**
- `Vehiculo` **no tiene ninguno** de los dos métodos.
- `PerfilConductor` (`models.py:120-125`) **no existe en el doc**: duplica `vehiculo_valido` como bool
  desnormalizada, escrita por un `post_save` (`signals.py:13-18`) y de nuevo a mano en
  `views.py:79-81`. Es una segunda fuente de verdad que además se desincroniza: borrar o desactivar
  el vehículo **no** pone `PerfilConductor.vehiculo_valido=False`.
- `Usuario.vehiculo_valido` (`models.py:94-99`) consulta el perfil duplicado.

**Objetivo**
```python
class Vehiculo(models.Model):
    """Modelo temporal en accounts; se moverá a app vehicles en sprint posterior."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name="vehiculo"
    )
    marca = models.CharField(max_length=60)
    modelo = models.CharField(max_length=60)
    color = models.CharField(max_length=40)
    placas = models.CharField(max_length=12, unique=True)
    tipo = models.CharField(max_length=12, choices=TipoVehiculo.choices)
    asientos_disponibles = models.PositiveSmallIntegerField()
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.placas})"

    def es_valido_para_conducir(self) -> bool:
        return bool(self.activo)

    def tiene_capacidad(self, requeridos: int) -> bool:
        return self.asientos_disponibles >= requeridos
```
> L403 pide "existe, completo y activo". Como la vista exige que los 6 campos venga completos en el
> serializer (`serializers.py:83-88`), "completo" está garantizado por la creación; implementa solo
> `activo` y anótalo en §6.

En `Usuario`, reemplazar la property `vehiculo_valido`:
```python
    @property
    def vehiculo_valido(self) -> bool:
        return hasattr(self, "vehiculo") and self.vehiculo.es_valido_para_conducir()
```
**Eliminar** `PerfilConductor` por completo: modelo (`models.py:120-125`), signal
`crear_perfil_conductor` (`signals.py:7-10`), `actualizar_vehiculo_valido` (`signals.py:13-18`) y las
escrituras de `views.py:78-81`. Si tras C6 **ambos** signals quedan sin función, borra
`signals.py` y el `def ready()` de `apps.py:9-10`; si queda alguno útil, conserva solo ese.

En `VehiculoRegistroView` (`views.py:83-89`), la respuesta ya no debe depender del perfil:
```python
        return Response(
            {"id": vehiculo.id, "placas": vehiculo.placas, "vehiculo_valido": True},
            status=status.HTTP_201_CREATED,
        )
```

**Migración** (`_vehiculo_es_metodos_y_fin_perfil_conductor`): `AlterField` en `Vehiculo.tipo` (a
`TipoVehiculo`), `DeleteModel PerfilConductor`.
> `DeleteModel` **destruye** `notas_admin`. Ejecuta antes
> `SELECT COUNT(*) FROM accounts_perfilconductor;` y reporta. `notas_admin` no está en el doc
> (`PerfilConductor` no existe en el UML); si el equipo la quiere, debe documentarla primero.

**Criterios de aceptación**
- [ ] `PerfilConductor` no existe en el código ni en `INSTALLED_APPS`.
- [ ] `user.vehiculo_valido` es `False` tras crear un vehículo con `activo=False`.
- [ ] `vehiculo.tiene_capacidad(4)` sobre un vehículo de 3 asientos → `False`.
- [ ] `test_senal_crea_perfil_conductor` y `test_senal_no_crea_perfil_si_no_conductor` se **eliminan**
      (prueban comportamiento ya retirado); `test_puede_aceptar_raite` se reescribe con vehículo real.

---

### 🟡 C7 — `no_tiene_raite_en_curso()` y reescritura de `puede_*_raite()`

**Doc (referencia exacta)**
- L554-556 — `Usuario` expone `puede_crear_raite()`, `puede_aceptar_raite()`,
  `no_tiene_raite_en_curso()`.
- L806-811 (`puede_crear_raite`): *"true solo si: `no_tiene_raite_en_curso()`, posee el rol
  correspondiente"*.
- L813-819 (`no_tiene_raite_en_curso`): *"Invariante: `cuenta_activa <= 1`. Exige índice único parcial o
  lock pesimista sobre `Usuario`: dos peticiones concurrentes pueden pasar el 'if' a la vez."*
- L401: *"`no_tiene_raite_en_curso()` → `cuenta_activa == 0` (y lock para evitar carrera)"*.

**Estado actual**
- `no_tiene_raite_en_curso()` **no existe**. Lo sustituye la property `en_viaje`
  (`models.py:101-111`), que consulta `self.raites_solicitados` / `self.raites_aceptados` de la app
  `rides`, **inexistente**, y captura `AttributeError` para devolver `False` (`models.py:109-111`).
  Es código muerto que además devolvería "libre" siempre.
- `puede_crear_raite()` (`models.py:113-114`) exige `self.verificado` (retirado en C4) y
  `self.cuenta_activa` (que tras C3 es un contador, no un bool → siempre truthy salvo `0`).
- `puede_aceptar_raite()` (`models.py:116-117`) **no** comprueba `suspendido` ni capacidad
  (`tiene_capacidad`), exigidas por L58/L404.

**Objetivo**
```python
    def no_tiene_raite_en_curso(self) -> bool:
        """Invariante: cuenta_activa <= 1. Lee la caché, no consulta Raite.
        La exclusión de carrera (índice único parcial o lock pesimista) se implementa en
        Raite.crear()/Raite.aceptar() en la fase 3; un `if` aquí NO es suficiente por sí solo."""
        return self.cuenta_activa == 0

    def puede_crear_raite(self) -> bool:
        return (
            self.es_pasajero
            and not self.suspendido
            and self.no_tiene_raite_en_curso()
        )

    def puede_aceptar_raite(self) -> bool:
        return (
            self.es_conductor
            and not self.suspendido
            and self.no_tiene_raite_en_curso()
            and self.vehiculo_valido
        )
```
**Eliminar** la property `en_viaje` completa (`models.py:101-111`), incluido su `try/except
AttributeError`. Tras esto, `accounts` **no debe contener ninguna referencia a `rides`, `raites_*` ni
a apps futuras**: se comprueba con
`grep -rniE "rides|raites_|notifications|surveys|ratings" Back_Raite/apps/accounts --include=*.py`
(esperado: 0 coincidencias).

> Nota de capacidad: `tiene_capacidad(raite.pasajeros_requeridos)` (L404) necesita el `Raite` para
> tener el argumento. En esta fase `puede_aceptar_raite()` valida lo validable sin `Raite`; la
> capacidad se comprueba en `Raite.validar_vehiculo()` (L612) en la fase 3. **Anótalo en §6.**

**Criterios de aceptación**
- [ ] `no_tiene_raite_en_curso()` devuelve `self.cuenta_activa == 0`.
- [ ] `en_viaje` ya no existe; `grep` de referencias a `rides` = 0.
- [ ] `suspendido=True` bloquea ambos `puede_*_raite()`.
- [ ] Un admin puro (`roles=["admin"]`) → ambos `False` (no posee PASAJERO ni CONDUCTOR).

---

### 🟢 C8 — Limpieza de código muerto

Sin referencia en el doc; es deuda que estorba a la fase 3.

| # | Ubicación | Acción |
|---|-----------|--------|
| 8.1 | `apps/accounts/urls.py` (5 líneas) | **Borrar el archivo.** `Raite_DjangoRest/urls.py:22` incluye `apps.accounts.urls_auth` directamente; `accounts/urls.py` no está en ninguna ruta y duplica el `include`. |
| 8.2 | `serializers.py:93-95` | `VehiculoRegistroSerializer.validate_placas` tiene un `if …: pass` muerto. **Borrar el bloque entero**; la unicidad ya se comprueba en `views.py:62-66` sobre `Vehiculo`. Deja un comentario de una línea explicando que la unicidad se valida en la vista. |
| 8.3 | `serializers.py:68-72`, `99-102` | `RegistroResponseSerializer` y `VehiculoRegistroResponseSerializer` no se usan (las vistas construyen dicts a mano). **Borrar** y decidir una sola vía: o se usan en las vistas, o se borran. Prefiere: **usarlas** en `RegistroView` y `VehiculoRegistroView` (evita que el contrato de respuesta se desincronice del modelo). |
| 8.4 | `serializers.py:75-79` | `VehiculoSerializer` usa `model = PerfilConductor` y no se usa. Con C6 desaparece `PerfilConductor`: **borrar la clase**. |
| 8.5 | `settings.py` | No hay `AUTHENTICATION_BACKENDS`, y el commit `907f0c5` afirma haber añadido un "EmailBackend" que no existe. **No crees `backends.py`**: `USERNAME_FIELD = "correo"` (models.py:66) ya hace que `ModelBackend` autentique por correo (`test_authenticate_por_correo` lo prueba). Deja un comentario en `settings.py` aclarándolo y corrige el mensaje del commit si puedes. |
| 8.6 | `settings.py:87-93` | `DATABASES` usa `dj_database_url.config(default=os.getenv('DATABASE_URL'))`. El bloque comentado de SQLite (líneas 89-92) es el que permite correr tests sin tocar Postgres. **No lo borres**; es la vía del §1.4. |
| 8.7 | `admin.py:121-127` | `readonly_fields` incluye `calificacion` (bien, L548), pero `cuenta_activa` está editable en `fieldsets` (línea 59) contradiciendo L61/L328. **Mover `cuenta_activa` y `activo` a `readonly_fields`** tras C3. `verificado` desaparece con C4; añadir `suspendido` como editable (único que debe serlo). |
| 8.8 | `Front_Raite/src/pages/login/SignUpPage.vue:109` | Atributo mal escrito: `:disble="!isPasswordValid"` (typo de `disable`), y el `<q-form>` no tiene `@submit`. El frontend se alinea en C10; **deja constancia aquí** y no lo arregles en este commit. |

**Criterios de aceptación**
- [ ] `accounts/urls.py` no existe.
- [ ] `grep -n "pass" Back_Raite/apps/accounts/serializers.py` → 0 coincidencias.
- [ ] Ningún serializer queda importado sin usarse: `python3 -W error -c "import apps.accounts.serializers"`.

---

### 🟢 C9 — `calificacion` acotada a 0–5

**Doc (L278, L548):** *"Calificación (★ 1-5)"*, tipo `Float (1-5)`.

**Estado actual:** `calificacion = models.DecimalField(max_digits=2, decimal_places=1,
default=Decimal("0.0"))` (`models.py:51-53`) → admite cualquier valor de `0.0` a `9.9`, sin
validación. (Además `max_digits=2` es demasiado estrecho para cualquier esquema futuro de "1-5 con
decimales"; no cambies el tipo sin actualizar el doc.)

**Objetivo**
```python
    calificacion = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("5.00"))],
    )
```
> **Desviación deliberada y documentada:** el rango es `0.00–5.00`, no `1–5`, porque un usuario sin
  calificar debe poder existir. El doc no especifica el valor de "sin calificar"; se elige `0.00`
> para no romper `test_crear_usuario_con_datos_validos`. **Anota esta desviación en §6.**

**Migración** (`_calificacion_acotada`): `AlterField` + `RunPython` que normaliza filas fuera de
rango (`UPDATE ... SET calificacion = 5.00 WHERE calificacion > 5`) antes del `ALTER`. Reporta el
número de filas tocadas.

**Criterios de aceptación**
- [ ] `calificacion=5.5` lanza `ValidationError` en `full_clean()`.
- [ ] `calificacion=4.75` se guarda correctamente.

---

### 🟡 C10 — Contrato de registro alineado al doc

**Doc (L11-12)**
- *"`Registro - Paso 1`: Nombre completo, Correo, Contraseña, **Rol(es)**."*
- *"`Registro - Paso 2 (Condicional)`: Datos del Vehículo. **Solo si posee el rol `CONDUCTOR`**
  (directo o vía 'Ambos')."*
- L54: *"`ADMIN` no está disponible en el registro público."*

**Estado actual**
- `RegistroSerializer` (`serializers.py:44-55`) recibe `rol` **como valor único** (que tras C1 ya no
  existe) y **no** `roles`.
- `views.py:31` calcula `requiere_vehiculo = user.es_conductor`, correcto según L12: consérvalo.
- `RegistroView` no tiene `permission_classes` → es público: correcto, consérvalo.

**Objetivo**
```python
class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    roles = serializers.ListField(
        child=serializers.ChoiceField(choices=[Rol.PASAJERO, Rol.CONDUCTOR]),
        allow_empty=False,
        max_length=2,
    )

    class Meta:
        model = Usuario
        fields = [
            "nombre", "apellidos", "correo", "password",
            "edad", "sexo", "carrera", "roles",
        ]
        extra_kwargs = {
            "edad": {"required": True},
            "sexo": {"required": True},
            "carrera": {"required": True},
        }

    def validate_correo(self, value):
        if Usuario.objects.filter(correo__iexact=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value.lower()

    def validate_roles(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("No repitas roles.")
        if Rol.ADMIN in value:
            raise serializers.ValidationError("El rol ADMIN no se otorga en el registro público.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        roles = validated_data.pop("roles")
        return Usuario.objects.create_user(password=password, roles=roles, **validated_data)
```
> `max_length=2` + `validate_roles` sin duplicados materializa "AMBOS = PASAJERO + CONDUCTOR" sin
> permitir triples. `ADMIN` queda excluido **explícitamente**, no por descarte de choices: el LLM
> debe ver la intención (L54).

`RegistroView` (`views.py:23-38`): la respuesta pasa a usar `RegistroResponseSerializer` (8.3) con
`requiere_vehiculo = user.es_conductor`. **Sin cambios de contrato** salvo el campo `verificado` →
`suspendido` (C4).

`UsuarioSerializer` (`serializers.py:6-38`): `read_only_fields` pasa a
`["id", "calificacion", "activo", "cuenta_activa", "suspendido"]` y `fields` incluye `"activo"` y
`"suspendido"` (nunca `cuenta_activa` como escribible). `rol` desaparece de `fields` porque ya no es
campo del modelo; `roles` se mantiene.

**Criterios de aceptación**
- [ ] `POST /api/auth/register/` con `{"roles": ["PASAJERO", "CONDUCTOR"]}` → `201` y **dos** filas
      en `UsuarioRol`.
- [ ] `{"roles": ["ADMIN"]}` → `400`.
- [ ] `{"roles": ["PASAJERO", "PASAJERO"]}` → `400`.
- [ ] La respuesta de registro incluye `requiere_vehiculo: true` si hay `CONDUCTOR`.
- [ ] `rol` ya no aparece en ningún serializer.

---

## 4. Orden de ejecución

```
C1 (Roles: UsuarioRol) ──┬─► C5 (ADMIN usa la tabla de C1)
                         │
C2 (sexo) ───────────────┼─► C10 (roles[] en el contrato)
                         │
C3 (activo/cuenta_activa) ┼─► C7 (no_tiene_raite_en_curso lee la caché)
                         │
C4 (suspendido, -verificado) ┼─► C7 (puede_*_raite comprueba suspendido)
                         │
C6 (Vehiculo, -PerfilConductor) ─► C7 (vehiculo_valido)
                         │
C8 (limpieza) ───────────┴─► C10 (serializers sin Imports muertos)
C9 (calificacion)  ──── independiente
```

**Secuencia de commits recomendada**

1. `C2` — aislada, sin dependencias.
2. `C9` — aislada, sin dependencias.
3. `C1` — la más delicada (migración de datos). Requiere leer la migración generada línea por línea.
4. `C5` — depende de C1.
5. `C4` — depende de C3 (semántica de `cuenta_activa` que usa `puede_crear_raite`).
6. `C3` — antes de C7.
7. `C6` — antes de C7.
8. `C7** — último de modelos: consolida todo.
9. `C8` — limpieza final (los serializers ya no tienen imports muertos tras C1/C6).
10. `C10` — último: cierra el contrato de API.

> C8 puede ir antes que C10 solo; **nunca** muevas 8.3/8.4 antes de C6, porque `PerfilConductor`
> debe existir mientras se reference en las importaciones.

---

## 5. Verificación

### 5.1 Después de cada corrección (§1.4)
```bash
cd Back_Raite
DATABASE_URL="sqlite:///tmp_test.sqlite3" python3 manage.py test apps --noinput
```
Estado inicial: **17 tests OK**. Al terminar la fase deben pasar **más** tests, nunca menos.

### 5.2 Checks finales
```bash
cd Back_Raite

# Sin referencias a apps futuras
grep -rniE "rides|raites_|notifications|surveys|ratings|locations" apps/accounts --include=*.py
# esperado: 0 coincidencias

# Sin AMBOS almacenado ni PREFIERE_NO_DECIR
grep -rn "AMBOS\|PREFIERE_NO_DECIR" apps/ --include=*.py
# esperado: 0 coincidencias

# Sin código muerto de C8
grep -n "pass" apps/accounts/serializers.py          # esperado: 0
ls apps/accounts/urls.py                              # esperado: No such file

# Sin 'verificado'
grep -rn "verificado" apps/ --include=*.py            # esperado: 0

# Migraciones pendientes
python3 manage.py makemigrations --check --dry-run    # esperado: No changes detected
```

### 5.3 Tests nuevos obligatorios

Añadir en `apps/accounts/tests/test_models.py`:

| Test | Qué prueba |
|------|-----------|
| `test_ambos_es_dos_filas` | `roles=[PASAJERO, CONDUCTOR]` → 2 filas, ambas properties `True` |
| `test_usuario_rol_es_unico` | `(usuario, rol)` duplicado → `IntegrityError` |
| `test_rol_admin_no_esta_en_el_enum_ambos` | `Rol.AMBOS` no existe |
| `test_sexo_es_obligatorio` | `create_user` sin `sexo` → `IntegrityError` |
| `test_sexo_no_tiene_prefiere_no_decir` | `Sexo.PREFIERE_NO_DECIR` no existe |
| `test_cuenta_activa_es_entero` | `type(user.cuenta_activa) is int` y vale `0` |
| `test_activo_significa_ocupado` | `activo=False` con `is_active=True` (libre ≠ deshabilitado) |
| `test_is_staff_requiere_rol_admin` | `is_staff=True` sin fila ADMIN → `ValidationError` |
| `test_create_superuser_crea_rol_admin` | `create_superuser` deja flags `True` **y** fila `ADMIN` |
| `test_admin_no_deriva_pasajero` | admin puro: `roles == ["admin"]` |
| `test_vehiculo_inactivo_no_es_valido` | `activo=False` → `vehiculo_valido is False` |
| `test_tiene_capacidad` | 3 asientos, `tiene_capacidad(4) is False`, `(3) is True` |
| `test_suspendido_bloquea_crear_y_aceptar` | ambos `puede_*_raite()` en `False` |
| `test_suspendido_permite_login` | `authenticate()` sigue devolviendo usuario |
| `test_no_tiene_raite_en_curso` | `cuenta_activa=0 → True`, `=1 → False` |

Añadir en `apps/accounts/tests/test_auth_api.py`:

| Test | Qué prueba |
|------|-----------|
| `test_registro_crea_dos_filas_para_ambos` | `roles=[PASAJERO, CONDUCTOR]` → `201` |
| `test_registro_rechaza_admin` | `roles=[ADMIN]` → `400` |
| `test_registro_rechaza_roles_duplicados` | → `400` |
| `test_registro_devuelve_requiere_vehiculo` | `requiere_vehiculo` correcto por rol |
| `test_me_devuelve_suspendido` | `/api/auth/me/` incluye `suspendido` |
| `test_me_no_expone_cuenta_activa_como_booleano` | `cuenta_activa` es número |

**Tests a eliminar** (prueban comportamiento retirado):
- `test_senal_crea_perfil_conductor` — `PerfilConductor` ya no existe (C6).
- `test_senal_no_crea_perfil_si_no_conductor` — ídem.

**Tests a reescribir**:
- `test_crear_usuario_con_datos_validos` — quitar `rol=Rol.AMBOS`, añadir `roles=`, cambiar
  `assertTrue(user.cuenta_activa)` por `assertEqual(user.cuenta_activa, 0)` y
  `assertFalse(user.activo)`, quitar `verificado`, `calificacion` → `Decimal("0.00")`.
- `test_es_pasajero_es_conductor` — los tres usuarios se crean con `roles=[...]`.
- `test_puede_crear_raite` / `test_puede_aceptar_raite` — `rol=` → `roles=`; eliminar las líneas que
  manipulan `cuenta_activa` como bool (`user.cuenta_activa = False`) y usar `= 1`; `test_puede_aceptar_raite`
  crea un `Vehiculo` real en vez de tocar `perfil_conductor`.
- `test_crear_usuario_con_datos_validos` y `test_edad_*` — deben pasar `sexo` siempre (ya lo hacen).

---

## 6. Decisiones tomadas aquí que el agente NO debe cambiar

| # | Decisión | Motivo |
|---|----------|--------|
| 6.1 | `UsuarioRol` y `Vehiculo` viven en `accounts`, no en apps nuevas | `Vehiculo` ya está marcado como temporal (`models.py:129`); crear `vehicles` es fase 3 |
| 6.2 | `UsuarioRol` usa `id` implícito (BigAutoField), no `UUID` | El UML pide `UUID` pero el doc no lo exige; cambiar el PK de la tabla de roles no aporta nada |
| 6.3 | `es_valido_para_conducir()` solo comprueba `activo` | "Completo" lo garantiza el serializer al crear; no hay campos opcionales que validar |
| 6.4 | `tiene_capacidad()` se invocará desde `Raite.validar_vehiculo()`, no desde `puede_aceptar_raite()` | Necesita `raite.pasajeros_requeridos`, que no existe aún |
| 6.5 | `calificacion` es `0.00–5.00`, no `1–5` | Necesita un valor para "sin calificar"; el doc no lo especifica |
| 6.6 | Se elimina `verificado` | No aparece en `002.md`. Si el equipo quiere verificación de correo, **primero se documenta** |
| 6.7 | La sincronización del rol se hace con `roles: ListField(max_length=2)` + dedupe | Sin fila `AMBOS` ni campo `rol`; "AMBOS" es un concepto de interfaz, no de persistencia |
| 6.8 | Se elimina `PerfilConductor` y su columna `notas_admin` | `PerfilConductor` no está en el UML. Si `notas_admin` es necesaria, **primero se documenta** |
| 6.9 | `create_user(roles=None)` → `[PASAJERO]` | Mantiene la ergonomía de tests y `createsuperuser` |
| 6.10 | `IsAdmin` pasa a `es_admin` (rol), no `is_staff` (flag) | L59: el flag es consecuencia del rol, no su fuente |

---

## 7. Abiertas para el usuario (no resolverlas por cuenta propia)

1. **`verificado` (C4)** — ¿el equipo quiere verificación de correo? Si sí, hay que **añadirla a
   `002.md`** antes de implementarla; si no, se elimina y punto.
2. **`notas_admin` de `PerfilConductor` (C6)** — se pierde al borrar el modelo. ¿Se traslada a
   `TicketRevision.notas_admin` (que sí está en el UML, L660) o se descarta?
3. **`calificacion` sin calificar (C9)** — se eligió `0.00`. La alternativa es `null=True`, que
   obligaría a cambiar `default` y los tests de serializers.
4. **`Rol.ADMIN` y `is_staff` en el mismo guardado (C5)** — la guarda de `save()` exige dos
   escrituras (fila `ADMIN`, luego flags). Es correcto pero no atómico. Alternativa: `transaction.atomic`
   en `create_superuser`. **Recomendado**: implementa `transaction.atomic` en `create_superuser` para
   que no queden superusuarios sin rol si el proceso muere entre ambas escrituras.
5. **`backend` de correo** — el commit `907f0c5` menciona un `EmailBackend` inexistente. ¿Se
   documenta `AUTHENTICATION_BACKENDS` explícito o se deja `ModelBackend` con `USERNAME_FIELD="correo"`?

---

*Documento generado a partir de la auditoría `002.md` ↔ código (2026-10-03). Al cerrar la fase:
`graphify update .` y marcar en `002.md` §NOTAS TÉCNICAS los ítems que esta fase cubrió.*