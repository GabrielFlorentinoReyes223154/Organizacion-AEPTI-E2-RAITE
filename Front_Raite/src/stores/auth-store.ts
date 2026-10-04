import { defineStore } from 'pinia';
import { api } from '@/boot/axios';
import { Router } from '@/router';

interface User {
  id: string;
  correo: string;
  nombre: string;
  apellidos: string;
  roles: string[];
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    user: null as User | null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    authHeader: (state) => (state.accessToken ? `Bearer ${state.accessToken}` : ''),
    isAdmin: (state) => state.user?.roles.includes('admin') ?? false,
    isConductor: (state) => state.user?.roles.includes('conductor') ?? false,
    isPasajero: (state) => state.user?.roles.includes('pasajero') ?? false,
  },

  actions: {
    async login(credentials: { correo: string; password: string }) {
      const { data } = await api.post('/api/auth/token/', credentials);
      this.setTokens(data.access, data.refresh);
      await this.fetchUser();
      await Router.push('/second');
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
      await Router.push('/login/loginpage');
    },

    async register(data: {
      nombre: string;
      apellidos: string;
      correo: string;
      password: string;
      edad: number;
      sexo: string;
      carrera: string;
      roles: string[];
    }) {
      const { data: response } = await api.post('/api/auth/register/', data);
      // Registration returns: id, roles, suspendido, requiere_vehiculo
      // If requiere_vehiculo is true, user needs to register vehicle
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
  },
});