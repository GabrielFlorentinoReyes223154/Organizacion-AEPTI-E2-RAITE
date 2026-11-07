// Avisos breves (Notify) y confirmaciones (Dialog) con el estilo de DESIGN.md.

import { Dialog, Notify } from 'quasar';
import { leerError } from '@/api/errores';

export function avisarExito(mensaje: string) {
  Notify.create({ message: mensaje, color: 'positive', textColor: 'white', icon: 'check_circle' });
}

export function avisarError(error: unknown): ReturnType<typeof leerError> {
  const legible = leerError(error);
  Notify.create({ message: legible.mensaje, color: 'negative', textColor: 'white', icon: 'error' });
  return legible;
}

export function avisarAdvertencia(mensaje: string) {
  Notify.create({ message: mensaje, color: 'warning', textColor: 'dark', icon: 'warning' });
}

interface OpcionesConfirmar {
  titulo: string;
  mensaje: string;
  /** Texto del botón que confirma; nombra la acción ("Rechazar", "Cancelar viaje"). */
  confirmar: string;
  /** Texto del botón que regresa. */
  regresar?: string;
  peligro?: boolean;
}

/** Diálogo de confirmación. Resuelve true si la persona confirma. */
export function confirmar(opciones: OpcionesConfirmar): Promise<boolean> {
  return new Promise((resolve) => {
    Dialog.create({
      title: opciones.titulo,
      message: opciones.mensaje,
      persistent: false,
      ok: {
        label: opciones.confirmar,
        color: opciones.peligro ? 'negative' : 'primary',
        unelevated: true,
        noCaps: true,
      },
      cancel: {
        label: opciones.regresar ?? 'Regresar',
        flat: true,
        color: 'primary',
        noCaps: true,
      },
    })
      .onOk(() => resolve(true))
      .onCancel(() => resolve(false))
      .onDismiss(() => resolve(false));
  });
}
