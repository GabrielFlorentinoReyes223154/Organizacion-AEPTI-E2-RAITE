// Campus, carreras y puntos de referencia: se piden una vez y se reusan en búsqueda, publicar, mapa,
// registro y perfil. Campus y carreras son públicos; los puntos piden sesión.

import { defineStore } from 'pinia';
import { catalogos } from '@/api';
import type { Campus, Carrera, PuntoReferencia } from '@/api/tipos';

export const useCatalogosStore = defineStore('catalogos', {
  state: () => ({
    campus: [] as Campus[],
    puntos: [] as PuntoReferencia[],
    carreras: [] as Carrera[],
    cargando: null as Promise<void> | null,
    cargandoCarreras: null as Promise<void> | null,
  }),

  getters: {
    campusPorId: (s) => (id: number | null | undefined) =>
      s.campus.find((c) => c.id === id) ?? null,
    puntoPorId: (s) => (id: number | null | undefined) => s.puntos.find((p) => p.id === id) ?? null,
    carreraPorId: (s) => (id: number | null | undefined) =>
      s.carreras.find((c) => c.id === id) ?? null,
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

    /** Campus y carreras, sin sesión (registro y perfil). */
    cargarCarreras(): Promise<void> {
      if (this.campus.length && this.carreras.length) return Promise.resolve();
      this.cargandoCarreras ??= Promise.all([catalogos.campus(), catalogos.carreras()])
        .then(([campus, carreras]) => {
          this.campus = campus;
          this.carreras = [...carreras].sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'));
        })
        .finally(() => {
          this.cargandoCarreras = null;
        });
      return this.cargandoCarreras;
    },

    /** Puntos ordenados por cercanía a una ubicación (el API agrega `distancia_km`). */
    cercanos(lat: number, lon: number) {
      return catalogos.puntos({ lat, lon });
    },
  },
});
