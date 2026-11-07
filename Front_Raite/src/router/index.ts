import { defineRouter } from '#q-app';
import { routes, handleHotUpdate } from 'vue-router/auto-routes';
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router';
import type { Papel } from '@/api/tipos';
import { useSesionStore } from '@/stores/sesion';

declare module 'vue-router' {
  interface RouteMeta {
    /** Se puede abrir sin sesión (entrar, registro, verificar). */
    publico?: boolean;
    /** Papel necesario para la pantalla. */
    papel?: Papel;
    /** Título del encabezado. */
    titulo?: string;
    /** Pantalla secundaria: lleva botón de regresar (a esta ruta si no hay historial) y no lleva barra inferior. */
    atras?: string;
  }
}

const createHistory = import.meta.env.QUASAR_SERVER
  ? createMemoryHistory
  : import.meta.env.QUASAR_VUE_ROUTER_MODE === 'history'
    ? createWebHistory
    : createWebHashHistory;

const Router = createRouter({
  scrollBehavior: (_to, _from, guardada) => guardada ?? { left: 0, top: 0 },
  routes,
  history: createHistory(import.meta.env.QUASAR_VUE_ROUTER_BASE),
});

Router.beforeEach(async (to) => {
  const sesion = useSesionStore();
  // Hay tokens pero el perfil no cargó (por ejemplo, sin señal al abrir la app): se reintenta.
  if (sesion.acceso && !sesion.usuario) await sesion.iniciar();

  if (to.meta.publico) {
    // Con sesión, entrar y registro no tienen caso; verificar sí (puede haber otra cuenta).
    if (sesion.autenticado && to.path !== '/verificar') return sesion.inicio;
    return true;
  }

  if (!sesion.autenticado) {
    return { path: '/entrar', query: to.fullPath !== '/' ? { siguiente: to.fullPath } : {} };
  }

  if (to.path === '/') return sesion.inicio;

  const papel = to.meta.papel;
  if (papel) {
    const puede = papel === 'conductor' ? sesion.esConductor : sesion.esPasajero;
    if (!puede) return sesion.inicio;
    // Con rol AMBOS, abrir una pantalla del otro papel (por ejemplo desde un aviso) cambia el papel activo.
    if (sesion.papel !== papel) sesion.cambiarPapel(papel);
  }
  return true;
});

if (import.meta.hot) {
  handleHotUpdate(Router);
}

export { Router };

export default defineRouter(() => Router);
