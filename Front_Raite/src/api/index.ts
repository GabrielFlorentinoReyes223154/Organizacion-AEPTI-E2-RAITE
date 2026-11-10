// Una función por endpoint del API (RaiteDocs/API.md). Las pantallas no llaman a axios directo.

import { api } from '@/boot/axios';
import type {
  CalificacionPendiente,
  Campus,
  DatosRegistro,
  DatosVehiculo,
  DatosViaje,
  FiltrosBusqueda,
  MiSolicitud,
  MiViaje,
  Notificacion,
  Pagina,
  Papel,
  Preferencia,
  PuntoReferencia,
  Reporte,
  RolId,
  Solicitud,
  Tokens,
  Usuario,
  Uuid,
  Vehiculo,
  Viaje,
  ViajeDetalle,
  ViajeHistorial,
} from './tipos';

async function get<T>(url: string, params?: object): Promise<T> {
  const { data } = await api.get<T>(url, { params });
  return data;
}

async function post<T>(url: string, body?: object): Promise<T> {
  const { data } = await api.post<T>(url, body ?? {});
  return data;
}

async function patch<T>(url: string, body: object): Promise<T> {
  const { data } = await api.patch<T>(url, body);
  return data;
}

// --- Cuenta ---

export const cuenta = {
  entrar: (correo: string, password: string) =>
    post<Tokens>('/api/auth/token/', { correo, password }),
  renovar: (refresh: string) =>
    post<{ access: string; refresh?: string }>('/api/auth/token/refresh/', { refresh }),
  salir: (refresh: string) => post<unknown>('/api/auth/token/blacklist/', { refresh }),
  registrar: (datos: DatosRegistro) =>
    post<{
      correo: string;
      rol: RolId;
      requiere_vehiculo: boolean;
      requiere_verificacion: boolean;
      token: string;
    }>('/api/auth/register/', datos),
  verificar: (token: string, codigo: string) =>
    post<Tokens & { usuario: Usuario }>('/api/auth/verificar/', { token, codigo }),
  reenviarCodigo: (token: string) =>
    post<{ detail: string; token: string }>('/api/auth/reenviar-codigo/', { token }),
  yo: () => get<Usuario>('/api/auth/me/'),
  editarPerfil: (datos: {
    telefono?: string;
    carrera?: string;
    preferencia_compatibilidad?: Preferencia;
  }) => patch<Usuario>('/api/auth/me/', datos),
  vehiculo: () => get<Vehiculo>('/api/auth/vehicle/'),
  registrarVehiculo: (datos: DatosVehiculo) =>
    post<{ id: Uuid; placas: string; vehiculo_valido: boolean; rol: RolId; rol_display: string }>(
      '/api/auth/vehicle/',
      datos,
    ),
  editarVehiculo: (
    datos: Partial<Pick<DatosVehiculo, 'marca' | 'modelo' | 'color' | 'asientos_disponibles'>>,
  ) => patch<Vehiculo>('/api/auth/vehicle/', datos),
};

// --- Catálogos ---

export const catalogos = {
  campus: () => get<Campus[]>('/api/campus/'),
  puntos: (params?: { q?: string; lat?: number; lon?: number }) =>
    get<PuntoReferencia[]>('/api/puntos/', params),
};

// --- Viajes ---

export const viajes = {
  buscar: (filtros: FiltrosBusqueda) => get<Pagina<Viaje>>('/api/viajes/', filtros),
  publicar: (datos: DatosViaje) => post<ViajeDetalle>('/api/viajes/', datos),
  mios: (params?: { estado?: string; page?: number }) =>
    get<Pagina<MiViaje>>('/api/viajes/mios/', params),
  detalle: (id: Uuid) => get<ViajeDetalle>(`/api/viajes/${id}/`),
  editar: (id: Uuid, datos: Partial<Omit<DatosViaje, 'punto_referencia' | 'campus' | 'sentido'>>) =>
    patch<ViajeDetalle>(`/api/viajes/${id}/`, datos),
  cancelar: (id: Uuid) => post<ViajeDetalle>(`/api/viajes/${id}/cancelar/`),
  iniciar: (id: Uuid) => post<ViajeDetalle>(`/api/viajes/${id}/iniciar/`),
  finalizar: (id: Uuid) => post<ViajeDetalle>(`/api/viajes/${id}/finalizar/`),
  historial: (params?: { rol?: Papel; page?: number }) =>
    get<Pagina<ViajeHistorial>>('/api/historial/', params),
};

// --- Solicitudes ---

export const solicitudes = {
  pedir: (viajeId: Uuid) => post<MiSolicitud>(`/api/viajes/${viajeId}/solicitudes/`),
  delViaje: (viajeId: Uuid) =>
    get<Pagina<Solicitud> | Solicitud[]>(`/api/viajes/${viajeId}/solicitudes/`),
  mias: (params?: { estado?: string; page?: number }) =>
    get<Pagina<MiSolicitud>>('/api/solicitudes/mias/', params),
  aceptar: (id: Uuid) => post<Solicitud>(`/api/solicitudes/${id}/aceptar/`),
  rechazar: (id: Uuid) => post<Solicitud>(`/api/solicitudes/${id}/rechazar/`),
  cancelar: (id: Uuid) => post<MiSolicitud>(`/api/solicitudes/${id}/cancelar/`),
};

// --- Avisos, calificaciones y reportes ---

export const avisos = {
  lista: (params?: { no_leidas?: 1; page?: number }) =>
    get<Pagina<Notificacion>>('/api/notificaciones/', params),
  conteo: () => get<{ no_leidas: number }>('/api/notificaciones/conteo/'),
  leer: (id: Uuid) => post<Notificacion>(`/api/notificaciones/${id}/leer/`),
  leerTodas: () => post<{ marcadas: number }>('/api/notificaciones/leer-todas/'),
};

export const calificaciones = {
  pendientes: () => get<CalificacionPendiente[]>('/api/calificaciones/pendientes/'),
  calificar: (
    viajeId: Uuid,
    datos: { calificado: Uuid; puntuacion: number; comentario?: string },
  ) => post<unknown>(`/api/viajes/${viajeId}/calificaciones/`, datos),
};

export const reportes = {
  crear: (datos: { viaje: Uuid; reportado: Uuid; motivo: string }) =>
    post<Reporte>('/api/reportes/', datos),
  mios: () => get<Pagina<Reporte> | Reporte[]>('/api/reportes/mios/'),
};

/** Algunos listados pueden venir paginados o no; esto devuelve siempre el arreglo. */
export function comoLista<T>(datos: Pagina<T> | T[]): T[] {
  return Array.isArray(datos) ? datos : datos.results;
}
