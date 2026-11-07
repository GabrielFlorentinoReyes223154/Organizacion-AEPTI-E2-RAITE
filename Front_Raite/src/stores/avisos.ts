// Contador de avisos sin leer para la campanita. Consulta periódica (RF-09): sin push ni WebSockets.

import { defineStore } from 'pinia';
import { avisos } from '@/api';

const CADA_MS = 30_000;

// Al volver a la pestaña se actualiza enseguida, sin esperar la siguiente vuelta.
function alVolver() {
  if (document.visibilityState === 'visible') void useAvisosStore().actualizar();
}

export const useAvisosStore = defineStore('avisos', {
  state: () => ({
    noLeidas: 0,
    temporizador: null as ReturnType<typeof setInterval> | null,
  }),

  actions: {
    async actualizar() {
      if (typeof document !== 'undefined' && document.visibilityState === 'hidden') return;
      try {
        this.noLeidas = (await avisos.conteo()).no_leidas;
      } catch {
        /* sin conexión: se intenta en la siguiente vuelta */
      }
    },

    iniciar() {
      if (this.temporizador) return;
      void this.actualizar();
      this.temporizador = setInterval(() => void this.actualizar(), CADA_MS);
      document.addEventListener('visibilitychange', alVolver);
    },

    detener() {
      if (this.temporizador) clearInterval(this.temporizador);
      this.temporizador = null;
      this.noLeidas = 0;
      document.removeEventListener('visibilitychange', alVolver);
    },
  },
});
