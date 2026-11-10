// Token del registro en curso. Vive solo en esta pestaña: la cuenta no existe hasta confirmar el código.
const CLAVE = 'raite.registro-pendiente';

let enMemoria: string | null = null;

export function leerRegistroPendiente(): string | null {
  try {
    return sessionStorage.getItem(CLAVE) ?? enMemoria;
  } catch {
    return enMemoria;
  }
}

export function guardarRegistroPendiente(token: string) {
  enMemoria = token;
  try {
    sessionStorage.setItem(CLAVE, token);
  } catch {
    /* sin almacenamiento disponible: basta con la memoria mientras siga abierta la página */
  }
}

export function olvidarRegistroPendiente() {
  enMemoria = null;
  try {
    sessionStorage.removeItem(CLAVE);
  } catch {
    /* no había nada guardado */
  }
}
