// Formatos de pantalla. Todas las horas se muestran en la hora de Ciudad Juárez.

import type { Campus, EstadoSolicitud, EstadoViaje, Preferencia, Sentido } from '@/api/tipos';

export const ZONA = 'America/Ciudad_Juarez';

const fmtHora = new Intl.DateTimeFormat('es-MX', {
  timeZone: ZONA,
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
});
const fmtDia = new Intl.DateTimeFormat('es-MX', {
  timeZone: ZONA,
  weekday: 'short',
  day: 'numeric',
  month: 'short',
});
const fmtDiaLargo = new Intl.DateTimeFormat('es-MX', {
  timeZone: ZONA,
  weekday: 'long',
  day: 'numeric',
  month: 'long',
});
const fmtClave = new Intl.DateTimeFormat('en-CA', {
  timeZone: ZONA,
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
});

function capitalizar(texto: string) {
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

/** "2026-11-09" en hora de Juárez. */
export function claveDia(fecha: Date | string = new Date()): string {
  return fmtClave.format(new Date(fecha));
}

export function sumarDias(clave: string, dias: number): string {
  const [a, m, d] = clave.split('-').map(Number) as [number, number, number];
  const fecha = new Date(Date.UTC(a, m - 1, d + dias, 12));
  return fecha.toISOString().slice(0, 10);
}

/** "07:00" */
export function hora(iso: string): string {
  return fmtHora.format(new Date(iso));
}

/** "Hoy", "Mañana" o "Lun 9 nov". */
export function diaCorto(iso: string): string {
  const clave = claveDia(iso);
  const hoy = claveDia();
  if (clave === hoy) return 'Hoy';
  if (clave === sumarDias(hoy, 1)) return 'Mañana';
  return capitalizar(fmtDia.format(new Date(iso)).replace(/\./g, '').replace(',', ''));
}

/** "Lunes 9 de noviembre" (con "Hoy" o "Mañana" al frente cuando aplica). */
export function diaLargo(iso: string): string {
  const largo = capitalizar(fmtDiaLargo.format(new Date(iso)).replace(',', ''));
  const corto = diaCorto(iso);
  return corto === 'Hoy' || corto === 'Mañana' ? `${corto}, ${largo.toLowerCase()}` : largo;
}

/** Día corto a partir de una clave "2026-11-09". */
export function diaDeClave(clave: string): string {
  return diaCorto(`${clave}T12:00:00-07:00`);
}

/** Fecha y hora local sin zona ("2026-11-09T07:00:00"): el backend la toma como hora de Juárez. */
export function fechaHoraLocal(clave: string, hhmm: string): string {
  return `${clave}T${hhmm}:00`;
}

/** "hace 5 min", "hace 2 h", "ayer", o el día. */
export function haceCuanto(iso: string): string {
  const minutos = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  if (minutos < 1) return 'ahora';
  if (minutos < 60) return `hace ${minutos} min`;
  const horas = Math.round(minutos / 60);
  if (horas < 24) return `hace ${horas} h`;
  if (claveDia(iso) === sumarDias(claveDia(), -1)) return 'ayer';
  return diaCorto(iso);
}

/** "4.0", o null si todavía no tiene calificaciones. */
export function calificacion(valor: string | number | null | undefined): string | null {
  const numero = Number(valor ?? 0);
  return numero > 0 ? numero.toFixed(1) : null;
}

export function distancia(km: number | null | undefined): string | null {
  if (km === null || km === undefined) return null;
  if (km < 0.05) return 'en tu punto';
  return km < 1 ? `a ${Math.round(km * 10) * 100} m` : `a ${km.toFixed(1)} km`;
}

export function lugares(libres: number, ofrecidos: number): string {
  return `${libres} de ${ofrecidos} ${ofrecidos === 1 ? 'lugar' : 'lugares'}`;
}

export function iniciales(nombre: string): string {
  return nombre
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p.charAt(0).toUpperCase())
    .join('');
}

/** Nombre y la inicial del primer apellido: "Mariana L." */
export function nombreCorto(nombreCompleto: string): string {
  const [nombre, apellido] = nombreCompleto.split(/\s+/);
  return apellido ? `${nombre} ${apellido.charAt(0)}.` : (nombre ?? '');
}

/** "656 123 4567" */
export function telefono(t: string | null | undefined): string {
  const d = (t ?? '').replace(/\D/g, '');
  return d.length === 10 ? `${d.slice(0, 3)} ${d.slice(3, 6)} ${d.slice(6)}` : (t ?? '');
}

export function enlaceWhatsApp(t: string): string {
  return `https://wa.me/52${t.replace(/\D/g, '')}`;
}

export function textoPreferencia(p: Preferencia): string {
  return p === 'MISMO_SEXO' ? 'Mismo sexo' : 'Grupo mixto';
}

export function textoSentido(s: Sentido): string {
  return s === 'HACIA_CAMPUS' ? 'Hacia el campus' : 'Desde el campus';
}

export function nombreCampus(c: Pick<Campus, 'codigo' | 'nombre'>): string {
  return c.nombre;
}

export const TEXTO_ESTADO_VIAJE: Record<EstadoViaje | 'VENCIDO', string> = {
  PUBLICADO: 'Publicado',
  EN_CURSO: 'En curso',
  FINALIZADO: 'Finalizado',
  CANCELADO: 'Cancelado',
  VENCIDO: 'Vencido',
};

export const TEXTO_ESTADO_SOLICITUD: Record<EstadoSolicitud, string> = {
  PENDIENTE: 'Pendiente',
  ACEPTADA: 'Aceptada',
  RECHAZADA: 'Rechazada',
  CANCELADA: 'Cancelada',
};

/** "Ingeniería de Software · IIT": carrera de otra persona con el campus donde estudia. */
export function conCampus(persona: { carrera: string; campus?: string | null }): string {
  return persona.campus ? `${persona.carrera} · ${persona.campus}` : persona.carrera;
}
