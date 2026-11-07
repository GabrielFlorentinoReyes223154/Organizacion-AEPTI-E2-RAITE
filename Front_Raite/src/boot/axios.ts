import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { useSesionStore } from '@/stores/sesion';

const api = axios.create({
  baseURL: (import.meta.env.VITE_API_URL as string | undefined) || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
  timeout: 20000,
});

interface PeticionReintentable extends InternalAxiosRequestConfig {
  _reintento?: boolean;
}

// Peticiones que no se reintentan con un token renovado (no usan sesión o son la propia renovación).
const SIN_RENOVAR = [
  '/api/auth/token/',
  '/api/auth/register/',
  '/api/auth/verificar/',
  '/api/auth/reenviar-codigo/',
];

let renovando: Promise<string | null> | null = null;

api.interceptors.response.use(
  (respuesta) => respuesta,
  async (error: AxiosError) => {
    const original = error.config as PeticionReintentable | undefined;
    const url = original?.url ?? '';
    const esDeSesion = SIN_RENOVAR.some((ruta) => url.startsWith(ruta));

    if (error.response?.status !== 401 || !original || original._reintento || esDeSesion) {
      // Se rechaza con el error original para que la pantalla pueda leer la respuesta del API.
      return Promise.reject(error);
    }

    const sesion = useSesionStore();
    original._reintento = true;
    renovando ??= sesion.renovarToken().finally(() => {
      renovando = null;
    });
    const token = await renovando;
    if (!token) {
      sesion.olvidarSesion();
      window.location.assign('/entrar');
      return Promise.reject(error);
    }
    original.headers.Authorization = `Bearer ${token}`;
    return api(original);
  },
);

export default () => {
  /* La instancia se importa directamente donde se usa. */
};

export { api };
