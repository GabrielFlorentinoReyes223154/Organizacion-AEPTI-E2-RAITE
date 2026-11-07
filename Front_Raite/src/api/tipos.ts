// Formas de los datos que devuelve el API (ver RaiteDocs/API.md y los serializers del backend).

export type Uuid = string;
/** Fecha y hora en ISO 8601. */
export type FechaIso = string;

export const Rol = { ADMIN: 1, PASAJERO: 2, CONDUCTOR: 3, AMBOS: 4 } as const;
export type RolId = (typeof Rol)[keyof typeof Rol];
/** El papel con el que se usa la app en este momento. */
export type Papel = 'pasajero' | 'conductor';

export type Sexo = 'M' | 'F' | 'X';
export type Preferencia = 'MIXTO' | 'MISMO_SEXO';
export type Sentido = 'HACIA_CAMPUS' | 'DESDE_CAMPUS';
export type TipoVehiculo = 'COCHE' | 'CAMIONETA' | 'TROCA';
export type EstadoViaje = 'PUBLICADO' | 'EN_CURSO' | 'FINALIZADO' | 'CANCELADO';
export type EstadoSolicitud = 'PENDIENTE' | 'ACEPTADA' | 'RECHAZADA' | 'CANCELADA';
export type EstadoReporte = 'PENDIENTE' | 'RESUELTO' | 'DESCARTADO';
export type TipoNotificacion =
  | 'SOLICITUD_NUEVA'
  | 'SOLICITUD_ACEPTADA'
  | 'SOLICITUD_RECHAZADA'
  | 'SOLICITUD_CANCELADA'
  | 'VIAJE_MODIFICADO'
  | 'VIAJE_CANCELADO'
  | 'VIAJE_FINALIZADO';

export interface Pagina<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Vehiculo {
  id: Uuid;
  marca: string;
  modelo: string;
  color: string;
  placas: string;
  tipo: TipoVehiculo;
  tipo_display: string;
  asientos_disponibles: number;
  activo: boolean;
}

export interface Usuario {
  id: Uuid;
  correo: string;
  nombre: string;
  apellidos: string;
  nombre_completo: string;
  edad: number;
  sexo: Sexo;
  carrera: string;
  telefono: string;
  preferencia_compatibilidad: Preferencia;
  /** "0.00" a "5.00"; "0.00" = sin calificaciones todavía. */
  calificacion: string;
  correo_verificado: boolean;
  suspendido: boolean;
  rol: RolId;
  rol_display: string;
  es_pasajero: boolean;
  es_conductor: boolean;
  es_admin: boolean;
  vehiculo: Vehiculo | null;
}

/** Lo que se ve de otra persona. `telefono` solo llega con el raite confirmado. */
export interface UsuarioPublico {
  id: Uuid;
  nombre: string;
  nombre_completo: string;
  sexo: Sexo;
  carrera: string;
  calificacion: string;
  telefono?: string;
}

export interface Campus {
  id: number;
  codigo: string;
  nombre: string;
  latitud: string;
  longitud: string;
}

export interface PuntoReferencia {
  id: number;
  nombre: string;
  latitud: string;
  longitud: string;
  distancia_km: number | null;
}

export interface VehiculoDeViaje {
  marca: string;
  modelo: string;
  color: string;
  tipo: TipoVehiculo;
  /** Solo con el raite confirmado (o para el conductor). */
  placas?: string;
}

export interface Viaje {
  id: Uuid;
  conductor: UsuarioPublico;
  vehiculo: VehiculoDeViaje;
  punto_referencia: PuntoReferencia;
  campus: Campus;
  sentido: Sentido;
  sentido_display: string;
  fecha_hora: FechaIso;
  lugares_ofrecidos: number;
  lugares_disponibles: number;
  preferencia_compatibilidad: Preferencia;
  notas: string;
  estado: EstadoViaje;
  estado_display: string;
  esta_vencido: boolean;
  inicio_permitido_desde: FechaIso;
  distancia_km: number | null;
}

export interface MiViaje extends Viaje {
  solicitudes_pendientes: number;
}

export interface ViajeDetalle extends Viaje {
  mi_solicitud: { id: Uuid; estado: EstadoSolicitud } | null;
  /** Solo para el conductor del viaje. */
  pasajeros_confirmados: UsuarioPublico[] | null;
}

export interface ViajeHistorial extends Viaje {
  mi_papel: Papel;
}

/** Solicitud vista por el conductor. */
export interface Solicitud {
  id: Uuid;
  viaje: Uuid;
  pasajero: UsuarioPublico;
  preferencia_compatibilidad: Preferencia;
  estado: EstadoSolicitud;
  estado_display: string;
  created_at: FechaIso;
  respondida_en: FechaIso | null;
}

/** Solicitud vista por el pasajero. */
export interface MiSolicitud {
  id: Uuid;
  viaje: Viaje;
  estado: EstadoSolicitud;
  estado_display: string;
  created_at: FechaIso;
  respondida_en: FechaIso | null;
}

export interface Notificacion {
  id: Uuid;
  tipo: TipoNotificacion;
  tipo_display: string;
  mensaje: string;
  viaje: Uuid | null;
  leida: boolean;
  created_at: FechaIso;
}

export interface CalificacionPendiente {
  viaje: {
    id: Uuid;
    punto_referencia: string;
    campus: string;
    sentido: Sentido;
    fecha_hora: FechaIso;
  };
  usuario: UsuarioPublico;
}

export interface Reporte {
  id: Uuid;
  viaje: Uuid;
  reportado: UsuarioPublico;
  motivo: string;
  estado: EstadoReporte;
  estado_display: string;
  created_at: FechaIso;
  resuelto_en: FechaIso | null;
}

export interface Tokens {
  access: string;
  refresh: string;
}

export interface DatosRegistro {
  nombre: string;
  apellidos: string;
  correo: string;
  password: string;
  edad: number;
  sexo: Sexo;
  carrera: string;
  telefono: string;
  preferencia_compatibilidad: Preferencia;
  rol: RolId;
}

export interface DatosVehiculo {
  marca: string;
  modelo: string;
  color: string;
  placas: string;
  tipo: TipoVehiculo;
  asientos_disponibles: number;
}

export interface DatosViaje {
  punto_referencia: number;
  campus: number;
  sentido: Sentido;
  fecha_hora: string;
  lugares_ofrecidos: number;
  preferencia_compatibilidad: Preferencia;
  notas: string;
}

export interface FiltrosBusqueda {
  punto?: number;
  lat?: number;
  lon?: number;
  radio_km?: number;
  campus?: number;
  sentido?: Sentido;
  desde?: string;
  hasta?: string;
  page?: number;
}
