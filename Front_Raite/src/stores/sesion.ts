// Sesión del usuario: tokens, perfil y papel activo (pasajero o conductor).

import { isAxiosError } from 'axios';
import { defineStore } from 'pinia';
import { api } from '@/boot/axios';
import { cuenta } from '@/api';
import { Rol, type DatosRegistro, type Papel, type Tokens, type Usuario } from '@/api/tipos';
import { guardarRegistroPendiente, olvidarRegistroPendiente } from '@/utils/registro-pendiente';

const CLAVE_ACCESO = 'access_token';
const CLAVE_RENOVAR = 'refresh_token';
const CLAVE_PAPEL = 'raite.papel';

function leer(clave: string): string | null {
  try {
    return localStorage.getItem(clave);
  } catch {
    return null;
  }
}

function guardar(clave: string, valor: string | null) {
  try {
    if (valor === null) localStorage.removeItem(clave);
    else localStorage.setItem(clave, valor);
  } catch {
    /* sin almacenamiento: la sesión dura lo que la pestaña */
  }
}

export const useSesionStore = defineStore('sesion', {
  state: () => ({
    acceso: leer(CLAVE_ACCESO),
    renovar: leer(CLAVE_RENOVAR),
    usuario: null as Usuario | null,
    papelElegido: (leer(CLAVE_PAPEL) as Papel | null) ?? 'pasajero',
  }),

  getters: {
    autenticado: (s) => !!s.acceso && !!s.usuario,
    esAmbos: (s) => s.usuario?.rol === Rol.AMBOS,
    esPasajero: (s) => !!s.usuario?.es_pasajero,
    esConductor: (s) => !!s.usuario?.es_conductor,
    /** El papel con el que se está usando la app ahora. */
    papel(s): Papel {
      if (!s.usuario) return 'pasajero';
      if (s.usuario.rol === Rol.AMBOS) return s.papelElegido;
      return s.usuario.es_conductor ? 'conductor' : 'pasajero';
    },
    /** Pantalla de inicio: la misma para los dos papeles; su contenido cambia según el papel. */
    inicio(): string {
      return '/inicio';
    },
  },

  actions: {
    guardarTokens(tokens: Partial<Tokens>) {
      if (tokens.access) this.acceso = tokens.access;
      if (tokens.refresh) this.renovar = tokens.refresh;
      guardar(CLAVE_ACCESO, this.acceso);
      guardar(CLAVE_RENOVAR, this.renovar);
      if (this.acceso) api.defaults.headers.common.Authorization = `Bearer ${this.acceso}`;
    },

    olvidarSesion() {
      this.acceso = this.renovar = null;
      this.usuario = null;
      guardar(CLAVE_ACCESO, null);
      guardar(CLAVE_RENOVAR, null);
      delete api.defaults.headers.common.Authorization;
    },

    /**
     * Al abrir la app: recupera el perfil si hay tokens guardados. Solo olvida la sesión si el API
     * la rechaza; con un error de red los tokens se conservan y se reintenta en la siguiente navegación.
     */
    async iniciar() {
      if (!this.acceso || this.usuario) return;
      api.defaults.headers.common.Authorization = `Bearer ${this.acceso}`;
      try {
        await this.cargarUsuario();
      } catch (error) {
        const status = isAxiosError(error) ? error.response?.status : undefined;
        if (status === 401 || status === 403) this.olvidarSesion();
      }
    },

    async cargarUsuario() {
      this.usuario = await cuenta.yo();
      return this.usuario;
    },

    /** Devuelve el token nuevo, o null si la sesión ya no se puede renovar. */
    async renovarToken(): Promise<string | null> {
      if (!this.renovar) return null;
      try {
        const tokens = await cuenta.renovar(this.renovar);
        this.guardarTokens(tokens);
        return tokens.access;
      } catch {
        return null;
      }
    },

    async entrar(correo: string, password: string) {
      const tokens = await cuenta.entrar(correo.trim().toLowerCase(), password);
      this.guardarTokens(tokens);
      await this.cargarUsuario();
    },

    async registrar(datos: DatosRegistro) {
      const respuesta = await cuenta.registrar({
        ...datos,
        correo: datos.correo.trim().toLowerCase(),
      });
      guardarRegistroPendiente(respuesta.token);
      return respuesta;
    },

    async verificar(token: string, codigo: string) {
      const respuesta = await cuenta.verificar(token, codigo);
      olvidarRegistroPendiente();
      this.guardarTokens(respuesta);
      this.usuario = respuesta.usuario;
      if (respuesta.usuario.rol === Rol.CONDUCTOR) this.cambiarPapel('conductor');
    },

    async salir() {
      if (this.renovar) {
        try {
          await cuenta.salir(this.renovar);
        } catch {
          /* el token ya no era válido: igual se cierra la sesión aquí */
        }
      }
      this.olvidarSesion();
    },

    cambiarPapel(papel: Papel) {
      this.papelElegido = papel;
      guardar(CLAVE_PAPEL, papel);
    },
  },
});
