// Foto de perfil: elegir el archivo, revisarlo, recortarlo (RecortarFoto) y subirlo.
// La usan /perfil y el último paso del registro (/foto). El API la revisa otra vez.
import { ref } from 'vue';
import { cuenta } from '@/api';
import { useSesionStore } from '@/stores/sesion';
import { avisarAdvertencia, avisarError, avisarExito, confirmar } from '@/utils/avisar';

const TIPOS_FOTO = ['image/jpeg', 'image/png', 'image/webp'];
const FOTO_MAX_MB = 5;

export function useFotoPerfil() {
  const sesion = useSesionStore();
  const entradaFoto = ref<HTMLInputElement | null>(null);
  const archivoFoto = ref<File | null>(null);
  const subiendoFoto = ref(false);

  function elegirFoto() {
    entradaFoto.value?.click();
  }

  function fotoElegida(evento: Event) {
    const entrada = evento.target as HTMLInputElement;
    const archivo = entrada.files?.[0];
    entrada.value = ''; // para poder elegir el mismo archivo otra vez
    if (!archivo) return;
    if (!TIPOS_FOTO.includes(archivo.type)) {
      avisarAdvertencia('Elige una imagen JPG, PNG o WebP.');
      return;
    }
    if (archivo.size > FOTO_MAX_MB * 1024 * 1024) {
      avisarAdvertencia(`La foto pesa más de ${FOTO_MAX_MB} MB. Elige una más ligera.`);
      return;
    }
    archivoFoto.value = archivo;
  }

  /** Sube la foto recortada. Devuelve true si se guardó. */
  async function subirFoto(foto: Blob, nombre: string) {
    subiendoFoto.value = true;
    try {
      sesion.usuario = await cuenta.subirFoto(foto, nombre);
      archivoFoto.value = null;
      avisarExito('Guardamos tu foto.');
      return true;
    } catch (e) {
      avisarError(e);
      return false;
    } finally {
      subiendoFoto.value = false;
    }
  }

  async function quitarFoto() {
    const ok = await confirmar({
      titulo: '¿Quitar tu foto?',
      mensaje: 'En su lugar se mostrarán tus iniciales.',
      confirmar: 'Quitar foto',
      peligro: true,
    });
    if (!ok) return;
    subiendoFoto.value = true;
    try {
      sesion.usuario = await cuenta.quitarFoto();
      avisarExito('Quitamos tu foto.');
    } catch (e) {
      avisarError(e);
    } finally {
      subiendoFoto.value = false;
    }
  }

  return { entradaFoto, archivoFoto, subiendoFoto, elegirFoto, fotoElegida, subirFoto, quitarFoto };
}
