"""Foto de perfil: subir, cambiar, quitar, validaciones y dónde se muestra (RF-01)."""

from io import BytesIO

from django.conf import settings
from django.core.files.storage import InMemoryStorage, default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework import status

from apps.accounts.tests.factories import cliente_para, crear_conductor, crear_usuario
from apps.rides.tests.factories import crear_solicitud, crear_viaje

URL = "/api/auth/me/foto/"


def imagen(formato="JPEG", tam=(1200, 800), nombre=None, modo="RGB"):
    datos = BytesIO()
    Image.new(modo, tam, (200, 40, 40) if modo == "RGB" else (200, 40, 40, 128)).save(datos, format=formato)
    extension = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp", "GIF": "gif"}[formato]
    return SimpleUploadedFile(nombre or f"foto.{extension}", datos.getvalue(), content_type=f"image/{extension}")


def abrir_guardada(nombre):
    with default_storage.open(nombre) as archivo:
        foto = Image.open(archivo)
        foto.load()
        return foto


class FotoBase(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()
        self.cliente = cliente_para(self.usuario)

    def subir(self, archivo, cliente=None):
        with self.captureOnCommitCallbacks(execute=True):
            return (cliente or self.cliente).put(URL, {"foto": archivo}, format="multipart")

    def quitar(self):
        with self.captureOnCommitCallbacks(execute=True):
            return self.cliente.delete(URL)


class SubirFotoTests(FotoBase):
    def test_los_tests_nunca_usan_r2(self):
        self.assertFalse(settings.USA_R2)
        self.assertIsInstance(default_storage, InMemoryStorage)

    def test_jpg_png_y_webp_quedan_en_webp_reducido(self):
        for formato in ("JPEG", "PNG", "WEBP"):
            with self.subTest(formato):
                respuesta = self.subir(imagen(formato))
                self.assertEqual(respuesta.status_code, status.HTTP_200_OK, respuesta.data)
                self.usuario.refresh_from_db()
                self.assertTrue(self.usuario.foto.name.startswith(f"fotos/{self.usuario.pk}/"))
                self.assertTrue(self.usuario.foto.name.endswith(".webp"))
                guardada = abrir_guardada(self.usuario.foto.name)
                self.assertEqual(guardada.format, "WEBP")
                self.assertEqual(max(guardada.size), settings.FOTO_MAX_PX)
                self.assertEqual(guardada.size, (512, 341))  # conserva la proporción
                self.assertTrue(respuesta.data["foto"])

    def test_imagen_chica_no_se_agranda(self):
        self.subir(imagen(tam=(200, 300)))
        self.usuario.refresh_from_db()
        self.assertEqual(abrir_guardada(self.usuario.foto.name).size, (200, 300))

    def test_png_con_transparencia(self):
        respuesta = self.subir(imagen("PNG", modo="RGBA"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK, respuesta.data)

    def test_rechaza_archivos_que_no_son_jpg_png_ni_webp(self):
        casos = {
            "texto con extensión .jpg": SimpleUploadedFile("foto.jpg", b"no soy una imagen", content_type="image/jpeg"),
            "gif": imagen("GIF"),
            "svg": SimpleUploadedFile("foto.svg", b"<svg xmlns='http://www.w3.org/2000/svg'/>", content_type="image/svg+xml"),
        }
        for nombre, archivo in casos.items():
            with self.subTest(nombre):
                respuesta = self.subir(archivo)
                self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("foto", respuesta.data)
        self.usuario.refresh_from_db()
        self.assertFalse(self.usuario.foto)

    def test_rechaza_mas_de_5_mb(self):
        grande = SimpleUploadedFile("foto.jpg", b"0" * (settings.FOTO_MAX_MB * 1024 * 1024 + 1))
        respuesta = self.subir(grande)
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("5 MB", str(respuesta.data["foto"]))

    def test_sin_archivo(self):
        respuesta = self.cliente.put(URL, {}, format="multipart")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("foto", respuesta.data)

    def test_pide_sesion_y_correo_verificado(self):
        self.assertEqual(self.subir(imagen(), cliente=cliente_para()).status_code, status.HTTP_401_UNAUTHORIZED)
        sin_verificar = crear_usuario(correo_verificado=False)
        self.assertEqual(
            self.subir(imagen(), cliente=cliente_para(sin_verificar)).status_code, status.HTTP_403_FORBIDDEN
        )


class CambiarYQuitarFotoTests(FotoBase):
    def test_cambiar_la_foto_borra_la_anterior(self):
        self.subir(imagen())
        self.usuario.refresh_from_db()
        anterior = self.usuario.foto.name

        self.subir(imagen("PNG"))
        self.usuario.refresh_from_db()
        self.assertNotEqual(self.usuario.foto.name, anterior)
        self.assertTrue(default_storage.exists(self.usuario.foto.name))
        self.assertFalse(default_storage.exists(anterior))

    def test_una_foto_invalida_conserva_la_anterior(self):
        self.subir(imagen())
        self.usuario.refresh_from_db()
        actual = self.usuario.foto.name
        self.subir(SimpleUploadedFile("foto.jpg", b"basura"))
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.foto.name, actual)
        self.assertTrue(default_storage.exists(actual))

    def test_quitar_la_foto_borra_el_archivo(self):
        self.subir(imagen())
        self.usuario.refresh_from_db()
        nombre = self.usuario.foto.name

        respuesta = self.quitar()
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIsNone(respuesta.data["foto"])
        self.usuario.refresh_from_db()
        self.assertFalse(self.usuario.foto)
        self.assertFalse(default_storage.exists(nombre))

    def test_quitar_sin_foto_no_falla(self):
        respuesta = self.quitar()
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIsNone(respuesta.data["foto"])

    def test_eliminar_la_cuenta_borra_la_foto(self):
        self.subir(imagen())
        self.usuario.refresh_from_db()
        nombre = self.usuario.foto.name
        with self.captureOnCommitCallbacks(execute=True):
            self.usuario.delete()
        self.assertFalse(default_storage.exists(nombre))


class FotoVisibleTests(FotoBase):
    def test_sin_foto_llega_null(self):
        self.assertIsNone(self.cliente.get("/api/auth/me/").data["foto"])

    def test_la_foto_llega_en_el_perfil_el_detalle_y_las_solicitudes(self):
        conductor = crear_conductor()
        viaje = crear_viaje(conductor)
        crear_solicitud(viaje, self.usuario)
        self.subir(imagen())
        self.subir(imagen(), cliente=cliente_para(conductor))
        self.usuario.refresh_from_db()
        conductor.refresh_from_db()

        self.assertEqual(self.cliente.get("/api/auth/me/").data["foto"], self.usuario.foto.url)

        detalle = self.cliente.get(f"/api/viajes/{viaje.pk}/")
        self.assertEqual(detalle.status_code, status.HTTP_200_OK, detalle.data)
        self.assertEqual(detalle.data["conductor"]["foto"], conductor.foto.url)

        solicitudes = cliente_para(conductor).get(f"/api/viajes/{viaje.pk}/solicitudes/").data
        if isinstance(solicitudes, dict):
            solicitudes = solicitudes["results"]
        self.assertEqual(solicitudes[0]["pasajero"]["foto"], self.usuario.foto.url)
