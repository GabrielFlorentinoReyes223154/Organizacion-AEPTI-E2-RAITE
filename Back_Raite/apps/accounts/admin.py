from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User as AuthUser

from .models import CodigoVerificacion, Usuario, Vehiculo

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
        fields = ("correo", "nombre", "apellidos", "edad", "sexo", "carrera", "telefono", "rol")

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


class VehiculoInline(admin.StackedInline):
    model = Vehiculo
    extra = 0
    can_delete = False


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    inlines = [VehiculoInline]
    form = UsuarioChangeForm
    add_form = UsuarioCreationForm
    add_form_template = "admin/auth/user/add_form.html"

    fieldsets = (
        (None, {"fields": ("correo", "password")}),
        (
            "Datos personales",
            {
                "fields": (
                    "nombre",
                    "apellidos",
                    "edad",
                    "sexo",
                    "carrera",
                    "telefono",
                    "preferencia_compatibilidad",
                    "rol",
                )
            },
        ),
        (
            "Estado en Raite",
            {"fields": ("correo_verificado", "suspendido", "calificacion")},
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
                    "edad",
                    "sexo",
                    "carrera",
                    "telefono",
                    "rol",
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
        "correo_verificado",
        "suspendido",
        "is_staff",
    )
    list_filter = (
        "rol",
        "sexo",
        "correo_verificado",
        "suspendido",
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


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("placas", "marca", "modelo", "color", "tipo", "asientos_disponibles", "usuario", "activo")
    list_filter = ("tipo", "activo")
    search_fields = ("placas", "marca", "modelo", "usuario__correo")
    autocomplete_fields = ("usuario",)


@admin.register(CodigoVerificacion)
class CodigoVerificacionAdmin(admin.ModelAdmin):
    """Solo lectura: los códigos se generan desde el API."""

    list_display = ("usuario", "creado_en", "expira_en", "intentos", "usado")
    list_filter = ("usado",)
    search_fields = ("usuario__correo",)
    readonly_fields = ("usuario", "codigo_hash", "creado_en", "expira_en", "intentos", "usado")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
