"""Crea usuarios, viajes, solicitudes y calificaciones de demostración.

Sirve para probar las pantallas y para la demo ante el profesor. Todo se crea con los
servicios de la app (mismas reglas de cupo, compatibilidad y notificaciones). Las fechas son
relativas al momento en que se corre, así que conviene volver a correrlo antes de una demo:

    python manage.py crear_datos_demo --reiniciar
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Vehiculo
from apps.accounts.models_choices import PreferenciaCompatibilidad, Rol, Sexo, TipoVehiculo
from apps.locations.geo import haversine_km
from apps.locations.models import Campus, PuntoReferencia
from apps.ratings.models import Calificacion
from apps.ratings.services import calificar
from apps.reports.models import Reporte
from apps.rides import services
from apps.rides.models import Solicitud, Viaje
from apps.rides.models_choices import SentidoViaje

PASSWORD = "raite1234"
MARCA_DEMO = ".demo@"  # todos los correos de demo la llevan; así se pueden borrar sin tocar nada más
DOMINIO = "alumnos.uacj.mx"
PUNTO_ANCLA = "Triunfo de la República"  # punto donde se juntan varios viajes para la búsqueda

MIXTO, MISMO = PreferenciaCompatibilidad.MIXTO, PreferenciaCompatibilidad.MISMO_SEXO

USUARIOS = {
    # clave: (nombre, apellidos, sexo, edad, carrera, rol, preferencia, vehículo o None)
    "mariana": ("Mariana", "López Villa", Sexo.F, 22, "Ingeniería en Sistemas Computacionales", Rol.CONDUCTOR, MIXTO,
                ("Nissan", "Versa", "Gris", "EFH4821", TipoVehiculo.COCHE, 4)),
    "diego": ("Diego", "Hernández Soto", Sexo.M, 23, "Ingeniería Industrial", Rol.CONDUCTOR, MIXTO,
              ("Chevrolet", "Aveo", "Blanco", "EKL1093", TipoVehiculo.COCHE, 4)),
    "valeria": ("Valeria", "Ruiz Campos", Sexo.F, 21, "Médico Cirujano", Rol.AMBOS, MISMO,
                ("Kia", "Rio", "Rojo", "ESD7754", TipoVehiculo.COCHE, 3)),
    "andrea": ("Andrea", "Martínez Olivas", Sexo.F, 20, "Psicología", Rol.PASAJERO, MIXTO, None),
    "luis": ("Luis", "Ortega Ramos", Sexo.M, 19, "Arquitectura", Rol.PASAJERO, MIXTO, None),
    "sofia": ("Sofía", "Chávez Durán", Sexo.F, 20, "Enfermería", Rol.PASAJERO, MISMO, None),
    "alex": ("Alex", "Ramírez Luna", Sexo.X, 21, "Diseño Gráfico", Rol.PASAJERO, MIXTO, None),
}


def correo_demo(clave):
    nombre, apellidos = USUARIOS[clave][0], USUARIOS[clave][1]
    base = f"{nombre}.{apellidos.split()[0]}".lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")):
        base = base.replace(a, b)
    return f"{base}{MARCA_DEMO}{DOMINIO}"


class Command(BaseCommand):
    help = "Crea datos de demostración (usuarios, viajes, solicitudes y calificaciones)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reiniciar",
            action="store_true",
            help="Borra los datos de demo anteriores (solo los de correos con '.demo@') y los crea de nuevo.",
        )

    def handle(self, *args, **opciones):
        Usuario = get_user_model()
        existentes = Usuario.objects.filter(correo__contains=MARCA_DEMO)
        if existentes.exists():
            if not opciones["reiniciar"]:
                raise CommandError("Ya hay datos de demo. Usa --reiniciar para borrarlos y crearlos de nuevo.")
            self._borrar(existentes)

        if not Campus.objects.exists() or not PuntoReferencia.objects.exists():
            call_command("cargar_datos_iniciales", verbosity=0)

        with transaction.atomic():
            self.u = {clave: self._crear_usuario(clave) for clave in USUARIOS}
            self._crear_viajes()

        self._resumen()

    # --- Borrado ---

    def _borrar(self, usuarios):
        viajes = Viaje.objects.filter(conductor__in=usuarios)
        with transaction.atomic():
            Reporte.objects.filter(viaje__in=viajes).delete()
            Calificacion.objects.filter(viaje__in=viajes).delete()
            Solicitud.objects.filter(pasajero__in=usuarios).delete()
            viajes.delete()
            usuarios.delete()  # borra en cascada vehículos, notificaciones y códigos

    # --- Usuarios ---

    def _crear_usuario(self, clave):
        nombre, apellidos, sexo, edad, carrera, rol, preferencia, vehiculo = USUARIOS[clave]
        n = list(USUARIOS).index(clave)
        usuario = get_user_model().objects.create_user(
            correo=correo_demo(clave),
            password=PASSWORD,
            nombre=nombre,
            apellidos=apellidos,
            sexo=sexo,
            edad=edad,
            carrera=carrera,
            rol=rol,
            preferencia_compatibilidad=preferencia,
            telefono=f"65611{n:05d}",
            correo_verificado=True,
        )
        if vehiculo:
            marca, modelo, color, placas, tipo, asientos = vehiculo
            v = Vehiculo(usuario=usuario, marca=marca, modelo=modelo, color=color, placas=placas, tipo=tipo,
                         asientos_disponibles=asientos)
            v.full_clean()
            v.save()
        return usuario

    # --- Viajes ---

    def _puntos(self):
        """El punto ancla y los dos más cercanos (a menos de 3 km), para que una búsqueda los encuentre juntos."""
        activos = list(PuntoReferencia.objects.filter(activo=True).order_by("nombre"))
        if not activos:
            raise CommandError("No hay puntos de referencia activos.")
        ancla = next((p for p in activos if PUNTO_ANCLA in p.nombre), activos[0])
        cercanos = sorted(
            (p for p in activos if p.pk != ancla.pk),
            key=lambda p: haversine_km(ancla.latitud, ancla.longitud, p.latitud, p.longitud),
        )
        cerca = [p for p in cercanos if haversine_km(ancla.latitud, ancla.longitud, p.latitud, p.longitud) <= 3][:2]
        while len(cerca) < 2:
            cerca.append(ancla)
        lejos = cercanos[-1] if cercanos else ancla
        return ancla, cerca[0], cerca[1], lejos

    def _publicar(self, conductor, punto, campus, cuando, lugares, sentido=SentidoViaje.HACIA_CAMPUS, notas=""):
        return services.publicar_viaje(
            self.u[conductor],
            {
                "punto_referencia": punto,
                "campus": Campus.objects.get(codigo=campus),
                "sentido": sentido,
                "fecha_hora": cuando,
                "lugares_ofrecidos": lugares,
                "notas": notas,
            },
        )

    def _pedir(self, viaje, pasajero):
        return services.solicitar_lugar(viaje.pk, self.u[pasajero])

    def _aceptar(self, viaje, pasajero):
        solicitud = self._pedir(viaje, pasajero)
        return services.aceptar_solicitud(solicitud.pk, viaje.conductor)

    @staticmethod
    def _mover(viaje, cuando):
        """Pasa el viaje a otra fecha sin validar (para dejarlo en el pasado)."""
        Viaje.objects.filter(pk=viaje.pk).update(fecha_hora=cuando)

    def _crear_viajes(self):
        ancla, cerca1, cerca2, lejos = self._puntos()
        ahora = timezone.localtime()

        def dia(dias, hora, minuto=0):
            return (ahora + timedelta(days=dias)).replace(hour=hora, minute=minuto, second=0, microsecond=0)

        # Viajes ya terminados: se publican en el futuro cercano, se inician y finalizan con los
        # servicios (que crean las notificaciones) y al final se mueven al pasado.
        pronto = ahora + timedelta(minutes=10)

        p1 = self._publicar("diego", ancla, "CU", pronto, 4)
        self._aceptar(p1, "andrea")
        self._aceptar(p1, "luis")
        services.iniciar_viaje(p1.pk, self.u["diego"])
        services.finalizar_viaje(p1.pk, self.u["diego"])
        calificar(p1.pk, self.u["luis"], {"calificado": self.u["diego"], "puntuacion": 5, "comentario": "Muy puntual."})
        calificar(p1.pk, self.u["diego"], {"calificado": self.u["luis"], "puntuacion": 5, "comentario": ""})
        self._mover(p1, dia(-3, 7))  # Andrea aún no califica: sirve para mostrar "Calificar"

        p2 = self._publicar("mariana", cerca1, "IIT", pronto, 3)
        self._aceptar(p2, "alex")
        services.iniciar_viaje(p2.pk, self.u["mariana"])
        services.finalizar_viaje(p2.pk, self.u["mariana"])
        calificar(p2.pk, self.u["alex"], {"calificado": self.u["mariana"], "puntuacion": 4, "comentario": "Todo bien."})
        calificar(p2.pk, self.u["mariana"], {"calificado": self.u["alex"], "puntuacion": 5, "comentario": ""})
        self._mover(p2, dia(-5, 8))

        p3 = self._publicar("valeria", cerca2, "ICB", pronto, 3)
        self._aceptar(p3, "sofia")
        services.cancelar_viaje(p3.pk, self.u["valeria"])
        self._mover(p3, dia(-2, 9))

        vencido = self._publicar("diego", lejos, "ICSA", pronto, 2)
        self._mover(vencido, ahora - timedelta(hours=3))  # vencido: solo se puede cancelar

        # Viajes por venir.
        v1 = self._publicar("mariana", ancla, "CU", dia(1, 7), 3, notas="Salgo puntual; espero 5 minutos.")
        self._pedir(v1, "andrea")
        self._pedir(v1, "luis")
        self._aceptar(v1, "alex")

        self._publicar("diego", cerca1, "CU", dia(1, 7, 30), 4)

        v3 = self._publicar("valeria", cerca2, "ICB", dia(1, 8), 2, notas="Solo mujeres.")
        self._pedir(v3, "sofia")

        v4 = self._publicar("diego", ancla, "CU", dia(1, 14), 4, sentido=SentidoViaje.DESDE_CAMPUS)
        self._aceptar(v4, "luis")
        rechazada = self._pedir(v4, "andrea")
        services.rechazar_solicitud(rechazada.pk, self.u["diego"])

        self._publicar("mariana", cerca1, "IIT", dia(2, 9), 3)
        self._publicar("diego", ancla, "ICSA", dia(2, 18), 2, sentido=SentidoViaje.DESDE_CAMPUS)

        # Sale en 25 minutos: el conductor ya lo puede iniciar durante la demo.
        v7 = self._publicar("mariana", ancla, "CU", ahora + timedelta(minutes=25), 2)
        self._aceptar(v7, "andrea")

        self.punto_ancla = ancla

    # --- Resumen ---

    def _resumen(self):
        self.stdout.write(self.style.SUCCESS("Datos de demo creados."))
        self.stdout.write(f"Contraseña de todas las cuentas: {PASSWORD}")
        self.stdout.write(f"Para buscar, usa el punto: {self.punto_ancla.nombre}\n")
        for clave, usuario in self.u.items():
            self.stdout.write(f"  {usuario.get_rol_display():<9} {usuario.get_sexo_display():<10} {usuario.correo}")
