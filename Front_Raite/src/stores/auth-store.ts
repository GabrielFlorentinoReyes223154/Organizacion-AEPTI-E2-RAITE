import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from '@/boot/axios';
import { Router } from '@/router';

interface User {
  id: string;
  correo: string;
  nombre: string;
  apellidos: string;
  rol: number;
  rol_display: string;
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    user: null as User | null,
    // Role selection modal state (for rol=4 AMBOS)
    roleSelectionModal: ref(false),
    roleSelectionResolve: null as ((role: 'pasajero' | 'conductor') => void) | null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    authHeader: (state) => (state.accessToken ? `Bearer ${state.accessToken}` : ''),
    isAdmin: (state) => state.user?.rol === 1,
    isConductor: (state) => state.user?.rol === 3 || state.user?.rol === 4,
    isPasajero: (state) => state.user?.rol === 2 || state.user?.rol === 4,
  },

  actions: {
    async login(credentials: { correo: string; password: string }) {
      const { data } = await api.post('/api/auth/token/', credentials);
      this.setTokens(data.access, data.refresh);
      await this.fetchUser();

      // Redirect based on role
      const role = this.user?.rol;
      switch (role) {
        case 2: // PASAJERO
          await Router.push('/home-pasajero');
          break;
        case 3: // CONDUCTOR
          await Router.push('/home-conductor');
          break;
        case 4: { // AMBOS - show modal to choose
          const chosenRole = await this.showRoleSelectionModal();
          await Router.push(chosenRole === 'pasajero' ? '/home-pasajero' : '/home-conductor');
          break;
        }
        default:
          await Router.push('/');
      }
    },

    async logout() {
      if (this.refreshToken) {
        try {
          await api.post('/api/auth/token/blacklist/', { refresh: this.refreshToken });
        } catch {
          /* ignore */
        }
      }
      this.clearTokens();
      await Router.push('/login/LoginPage');
    },

    async register(data: {
      nombre: string;
      apellidos: string;
      correo: string;
      password: string;
      edad: number;
      sexo: string;
      carrera: string;
      rol: number;
    }) {
      const { data: response } = await api.post('/api/auth/register/', data);
      return response;
    },

    async refreshAccessToken() {
      if (!this.refreshToken) throw new Error('No refresh token');
      const { data } = await api.post('/api/auth/token/refresh/', { refresh: this.refreshToken });
      this.setTokens(data.access, this.refreshToken);
    },

    async fetchUser() {
      const { data } = await api.get('/api/auth/me/');
      this.user = data;
    },

    setTokens(access: string, refresh: string) {
      this.accessToken = access;
      this.refreshToken = refresh;
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      api.defaults.headers.common.Authorization = `Bearer ${access}`;
    },

    clearTokens() {
      this.accessToken = this.refreshToken = this.user = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      delete api.defaults.headers.common.Authorization;
    },

    async initializeAuth() {
      if (this.accessToken) {
        api.defaults.headers.common.Authorization = `Bearer ${this.accessToken}`;
        try {
          await this.fetchUser();
        } catch {
          try {
            await this.refreshAccessToken();
            await this.fetchUser();
          } catch {
            this.clearTokens();
          }
        }
      }
    },

    // Show role selection modal for users with rol=4 (AMBOS)
    showRoleSelectionModal(): Promise<'pasajero' | 'conductor'> {
      this.roleSelectionModal = true;
      return new Promise((resolve) => {
        this.roleSelectionResolve = resolve;
      });
    },

    // Called from RoleSelectionModal when user selects a role
    onRoleSelected(role: 'pasajero' | 'conductor') {
      this.roleSelectionModal = false;
      if (this.roleSelectionResolve) {
        this.roleSelectionResolve(role);
        this.roleSelectionResolve = null;
      }
    },
  },
});