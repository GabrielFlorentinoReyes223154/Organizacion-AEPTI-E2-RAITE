import type { Sentido } from '@/api/tipos';

/** Filtros de la búsqueda tal como los edita la persona (FormBusqueda). */
export interface Busqueda {
  punto: number | null;
  /** Ubicación del dispositivo, si la compartió. */
  ubicacion: [number, number] | null;
  sentido: Sentido;
  campus: number | null;
  /** "2026-11-09" o null para cualquier día. */
  dia: string | null;
  /** "07:30" o null para cualquier hora. */
  hora: string | null;
  radio: number;
}
