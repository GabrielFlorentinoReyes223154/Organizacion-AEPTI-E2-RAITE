import uuid
from decimal import Decimal

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from .models_choices import Rol, Sexo, TipoVehiculo


class UsuarioManager(BaseUserManager):
    def create_user(self, correo, password=None, rol=None, **extra_fields):
        if not correo:
            raise ValueError("El correo es obligatorio")
        correo = self.normalize_email(correo)
        if extra_fields.get("roles"):
            raise ValueError(
                "El parámetro 'roles' ya no se usa. Usa rol=Rol.PASAJERO, rol=Rol.CONDUCTOR o rol=Rol.AMBOS."
            )
        if rol is None:
            rol = Rol.PASAJERO
        if rol == Rol.ADMIN:
            raise ValueError("El rol ADMIN no se otorga en el registro público.")
        user = self.model(correo=correo, rol=rol, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        user = self.model(correo=self.normalize_email(correo), rol=Rol.ADMIN, **extra_fields)
        user.is_staff = False
        user.is_superuser = False
        user.set_password(password)
        user.save(using=self._db)
        user.is_staff = True
        user.is_superuser = True
        user.save(update_fields=["is_staff", "is_superuser"])
        return user


class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    nombre = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=80)
    correo = models.EmailField(unique=True)
    edad = models.PositiveSmallIntegerField(
        default=18,
        validators=[MinValueValidator(17), MaxValueValidator(70)],
    )
    sexo = models.CharField(
        max_length=20, choices=Sexo.choices
    )
    carrera = models.CharField(max_length=120, default="")
    calificacion = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("5.00"))],
    )
    rol = models.PositiveSmallIntegerField(choices=Rol.choices, default=Rol.PASAJERO)
    activo = models.BooleanField(default=False)
    """CACHÉ: True = el usuario está OCUPADO en un Raite activo.
    NO significa "cuenta habilitada" (eso es `is_active`). Lo escribe exclusivamente
    Raite.sincronizar_cuenta_activa() en la fase 3."""

    cuenta_activa = models.PositiveSmallIntegerField(default=0)
    """CACHÉ: nº de Raites activos del usuario. Invariante 0..1. Integer, no Boolean."""

    suspendido = models.BooleanField(default=False)
    """SANCIÓN, no caché: no se refresca desde Raite ni se borra al liberar raites.
    Lo activa el Admin o la regla MAX_TICKETS_SUSPENSION=3 tickets RESUELTOS en contra
    (derivada por COUNT sobre TicketRevision; sin contador almacenado).
    Bloquea crear() y aceptar() por igual; el login sigue permitido.
    Solo el Admin puede levantarlo."""

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    # Habilitación de la cuenta (login permitido aunque esté suspendido).
    is_superuser = models.BooleanField(default=False)

    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "correo"
    REQUIRED_FIELDS = ["nombre", "apellidos", "edad", "sexo", "carrera"]

    objects = UsuarioManager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(edad__gte=17) & Q(edad__lte=70),
                name="edad_en_rango",
            ),
        ]

    def __str__(self):
        return f"{self.nombre_completo} <{self.correo}>"

    def save(self, *args, **kwargs):
        if self.is_staff or self.is_superuser:
            if self.rol != Rol.ADMIN:
                raise ValidationError(
                    "is_staff/is_superuser son exclusivos del rol ADMIN: "
                    "el usuario debe tener rol=1 (ADMIN)."
                )
        super().save(*args, **kwargs)

    def tiene_rol(self, rol: int) -> bool:
        return self.rol == rol

    @property
    def es_pasajero(self) -> bool:
        return self.rol in (Rol.PASAJERO, Rol.AMBOS)

    @property
    def es_conductor(self) -> bool:
        return self.rol in (Rol.CONDUCTOR, Rol.AMBOS)

    @property
    def es_admin(self) -> bool:
        return self.rol == Rol.ADMIN

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellidos}".strip()

    @property
    def vehiculo_valido(self) -> bool:
        return hasattr(self, "vehiculo") and self.vehiculo.es_valido_para_conducir()

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