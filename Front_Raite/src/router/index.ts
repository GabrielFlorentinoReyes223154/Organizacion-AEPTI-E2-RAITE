import { defineRouter } from '#q-app';
import { routes, handleHotUpdate } from 'vue-router/auto-routes';
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router';
import { useAuthStore } from '@/stores/auth-store';

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

const createHistory = import.meta.env.QUASAR_SERVER
  ? createMemoryHistory
  : import.meta.env.QUASAR_VUE_ROUTER_MODE === 'history'
    ? createWebHistory
    : createWebHashHistory;

const Router = createRouter({
  scrollBehavior: () => ({ left: 0, top: 0 }),
  routes,
  history: createHistory(import.meta.env.QUASAR_VUE_ROUTER_BASE),
});

// Global auth guard
Router.beforeEach((to) => {
  const authStore = useAuthStore();
  const publicPaths = ['/login', '/login/signuppage'];
  const requiresAuth = !publicPaths.some((p) => to.path.startsWith(p));

  if (requiresAuth && !authStore.isAuthenticated) {
    return { path: '/login/loginpage' };
  }

  if (to.path.startsWith('/login') && authStore.isAuthenticated) {
    return { path: '/' };
  }
});

// enable HMR for it
if (import.meta.hot) {
  handleHotUpdate(Router);
}

export { Router };

export default defineRouter(() => Router);
