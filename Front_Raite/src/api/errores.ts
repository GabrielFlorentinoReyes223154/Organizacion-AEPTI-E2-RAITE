// Convierte los errores del API (RaiteDocs/API.md, "Respuestas de error") en textos para la pantalla.

import { isAxiosError } from 'axios';

export interface ErrorLegible {
  /** Mensaje general para un aviso. */
  mensaje: string;
  /** Mensajes por campo (respuestas 400). */
  campos: Record<string, string>;
  status: number | null;
  /** Código del backend, por ejemplo `correo_no_verificado`. */
  codigo: string | null;
}

const SIN_CONEXION = 'No pudimos conectar con Raite. Revisa tu internet e inténtalo de nuevo.';
const GENERICO = 'Algo salió mal. Inténtalo de nuevo.';

function primerTexto(valor: unknown): string | null {
  if (typeof valor === 'string') return valor;
  if (Array.isArray(valor) && valor.length) return primerTexto(valor[0]);
  return null;
}

export function leerError(error: unknown): ErrorLegible {
  if (!isAxiosError(error)) {
    return { mensaje: GENERICO, campos: {}, status: null, codigo: null };
  }
  if (!error.response) {
    return { mensaje: SIN_CONEXION, campos: {}, status: null, codigo: null };
  }

  const { status, data } = error.response as { status: number; data: unknown };
  const campos: Record<string, string> = {};
  let mensaje: string | null = null;
  let codigo: string | null = null;

  if (data && typeof data === 'object' && !Array.isArray(data)) {
    for (const [clave, valor] of Object.entries(data as Record<string, unknown>)) {
      const texto = primerTexto(valor);
      if (clave === 'detail') mensaje = texto;
      else if (clave === 'codigo' || clave === 'code') codigo = texto;
      else if (clave === 'non_field_errors') mensaje = mensaje ?? texto;
      else if (texto) campos[clave] = texto;
    }
  } else {
    mensaje = primerTexto(data);
  }

  if (!mensaje) {
    const [primero] = Object.values(campos);
    if (status === 400 && primero) mensaje = 'Revisa los datos marcados.';
    else if (status === 404) mensaje = 'No encontramos lo que buscabas, o ya no está disponible.';
    else if (status >= 500) mensaje = 'Raite tuvo un problema. Inténtalo en unos minutos.';
    else mensaje = GENERICO;
  }

  return { mensaje, campos, status, codigo };
}
