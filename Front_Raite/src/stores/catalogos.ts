// Campus y puntos de referencia: se piden una vez y se reusan en búsqueda, publicar y mapa.

import { defineStore } from 'pinia';
import { catalogos } from '@/api';
import type { Campus, PuntoReferencia } from '@/api/tipos';

export const useCatalogosStore = defineStore('catalogos', {
  state: () => ({
    campus: [] as Campus[],
    puntos: [] as PuntoReferencia[],
    cargando: null as Promise<void> | null,
  }),

  getters: {
    campusPorId: (s) => (id: number | null | undefined) =>
      s.campus.find((c) => c.id === id) ?? null,
    puntoPorId: (s) => (id: number | null | undefined) => s.puntos.find((p) => p.id === id) ?? null,
  },

  actions: {
    cargar(): Promise<void> {
      if (this.campus.length && this.puntos.length) return Promise.resolve();
      this.cargando ??= Promise.all([catalogos.campus(), catalogos.puntos()])
        .then(([campus, puntos]) => {
          this.campus = campus;
          this.puntos = [...puntos].sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'));
        })
        .finally(() => {
          this.cargando = null;
        });
      return this.cargando;
    },

    /** Puntos ordenados por cercanía a una ubicación (el API agrega `distancia_km`). */
    cercanos(lat: number, lon: number) {
      return catalogos.puntos({ lat, lon });
    },
  },
});
