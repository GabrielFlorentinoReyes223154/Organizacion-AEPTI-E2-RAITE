from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User as AuthUser

from .models import Usuario, UsuarioRol

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
        fields = ("correo", "nombre", "apellidos", "edad", "sexo", "carrera")

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


class UsuarioRolInline(admin.TabularInline):
    model = UsuarioRol
    extra = 1


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    form = UsuarioChangeForm
    add_form = UsuarioCreationForm
    add_form_template = "admin/auth/user/add_form.html"
    inlines = [UsuarioRolInline]

    fieldsets = (
        (None, {"fields": ("correo", "password")}),
        (
            "Datos personales",
            {"fields": ("nombre", "apellidos", "edad", "sexo", "carrera")},
        ),
        (
            "Estado en Raite",
            {"fields": ("activo", "cuenta_activa", "suspendido", "calificacion")},
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
        "calificacion",
        "activo",
        "cuenta_activa",
        "suspendido",
        "is_staff",
    )
    list_filter = (
        "sexo",
        "activo",
        "cuenta_activa",
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
        "activo",
        "cuenta_activa",
    )


@admin.register(UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ("usuario", "rol")
    list_filter = ("rol",)
    search_fields = ("usuario__correo", "usuario__nombre", "usuario__apellidos")