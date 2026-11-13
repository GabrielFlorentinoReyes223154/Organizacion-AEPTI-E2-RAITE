import secrets
import uuid
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

from .models_choices import PreferenciaCompatibilidad, Rol, Sexo, TipoVehiculo

ASIENTOS_MIN = 1
ASIENTOS_MAX = 5

validar_telefono = RegexValidator(
    regex=r"^\d{10}$",
    message="El teléfono debe tener exactamente 10 dígitos, sin espacios ni guiones.",
)


def ruta_foto(usuario, _nombre_original: str) -> str:
    """Nombre nuevo en cada subida (siempre WebP, ver fotos.py): una URL vieja no muestra la foto nueva."""
    return f"fotos/{usuario.pk}/{uuid.uuid4().hex}.webp"


def correo_es_institucional(correo: str) -> bool:
    dominio = settings.CORREO_DOMINIO_PERMITIDO.lower()
    return (correo or "").strip().lower().endswith("@" + dominio)


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

        extra_fields.setdefault("correo_verificado", True)
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
    carrera = models.ForeignKey(
        "locations.Carrera",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="alumnos",
        help_text="Del catálogo de la UACJ; el campus del alumno sale de aquí. Vacía solo en administradores.",
    )
    telefono = models.CharField(
        "teléfono / WhatsApp",
        max_length=10,
        validators=[validar_telefono],
        help_text="10 dígitos. Solo se muestra al conductor/pasajero de un raite confirmado.",
    )
    preferencia_compatibilidad = models.CharField(
        max_length=12,
        choices=PreferenciaCompatibilidad.choices,
        default=PreferenciaCompatibilidad.MIXTO,
        help_text="Preferencia por defecto; se copia a cada viaje o solicitud.",
    )
    foto = models.ImageField(
        "foto de perfil",
        upload_to=ruta_foto,
        max_length=150,
        blank=True,
        help_text="Opcional. Se guarda como WebP de 512 px como máximo; solo la ven usuarios con sesión.",
    )
    correo_verificado = models.BooleanField(
        default=False,
        help_text="Se activa al confirmar el código enviado al correo institucional.",
    )
    calificacion = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("5.00"))],
    )
    rol = models.PositiveSmallIntegerField(choices=Rol.choices, default=Rol.PASAJERO)
    suspendido = models.BooleanField(default=False)
    """Sanción que pone el admin (por ejemplo, tras un reporte). Impide publicar viajes
    y solicitar lugares; el login sigue permitido. Solo el admin puede quitarla."""

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    # Habilitación de la cuenta (login permitido aunque esté suspendido).
    is_superuser = models.BooleanField(default=False)

    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "correo"
    REQUIRED_FIELDS = ["nombre", "apellidos", "edad", "sexo", "telefono"]

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

    def clean(self):
        super().clean()
        if self.correo and not self.es_admin and not correo_es_institucional(self.correo):
            raise ValidationError(
                {"correo": f"Usa tu correo institucional @{settings.CORREO_DOMINIO_PERMITIDO}."}
            )
        if not self.es_admin and self.carrera_id is None:
            raise ValidationError({"carrera": "Elige tu campus y tu carrera."})

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
    def campus(self):
        """Campus de la carrera del alumno (None en administradores)."""
        return self.carrera.campus if self.carrera_id else None

    @property
    def vehiculo_valido(self) -> bool:
        return hasattr(self, "vehiculo") and self.vehiculo.es_valido_para_conducir()

    def puede_solicitar_lugar(self) -> bool:
        """Requisitos de cuenta para pedir lugar en un viaje (los cruces de horario se revisan en servicios)."""
        return self.es_pasajero and self.correo_verificado and not self.suspendido

    def puede_publicar_viaje(self) -> bool:
        """Requisitos de cuenta para publicar un viaje."""
        return (
            self.es_conductor
            and self.correo_verificado
            and not self.suspendido
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
    asientos_disponibles = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(ASIENTOS_MIN), MaxValueValidator(ASIENTOS_MAX)],
        help_text="Lugares para pasajeros (1 a 5).",
    )
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(asientos_disponibles__gte=ASIENTOS_MIN)
                & Q(asientos_disponibles__lte=ASIENTOS_MAX),
                name="vehiculo_asientos_1_a_5",
            ),
        ]

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.placas})"

    def es_valido_para_conducir(self) -> bool:
        return bool(self.activo)

    def tiene_capacidad(self, requeridos: int) -> bool:
        return self.asientos_disponibles >= requeridos


class CodigoVerificacion(models.Model):
    """Código de 6 dígitos enviado al correo institucional para activar la cuenta.

    El código se guarda con hash; en claro solo existe al generarlo (para enviarlo).
    """

    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="codigos_verificacion"
    )
    codigo_hash = models.CharField(max_length=128)
    creado_en = models.DateTimeField(auto_now_add=True)
    expira_en = models.DateTimeField()
    intentos = models.PositiveSmallIntegerField(default=0)
    usado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "código de verificación"
        verbose_name_plural = "códigos de verificación"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"Código de {self.usuario.correo} ({self.creado_en:%Y-%m-%d %H:%M})"

    @classmethod
    def generar(cls, usuario) -> tuple["CodigoVerificacion", str]:
        """Crea un código nuevo y devuelve (registro, código en claro)."""
        codigo = f"{secrets.randbelow(10**6):06d}"
        registro = cls.objects.create(
            usuario=usuario,
            codigo_hash=make_password(codigo),
            expira_en=timezone.now() + timedelta(minutes=settings.CODIGO_VERIFICACION_MINUTOS),
        )
        return registro, codigo

    def intentos_agotados(self) -> bool:
        return self.intentos >= settings.CODIGO_VERIFICACION_MAX_INTENTOS

    def esta_vigente(self) -> bool:
        return not self.usado and not self.intentos_agotados() and timezone.now() < self.expira_en

    def comprobar(self, codigo: str) -> bool:
        """Cuenta un intento y dice si el código es correcto y sigue vigente.

        No marca el código como usado ni verifica al usuario: eso lo hace el servicio de la Capa 2.
        """
        if not self.esta_vigente():
            return False
        self.intentos += 1
        self.save(update_fields=["intentos"])
        return check_password(codigo or "", self.codigo_hash)
