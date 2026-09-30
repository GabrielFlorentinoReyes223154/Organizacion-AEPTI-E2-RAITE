import { defineStore } from 'pinia'
import { api } from 'boot/axios'
import { router } from 'router'

interface User {
  id: number
  email: string
  name: string
  roles: string[]
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    user: null as User | null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    authHeader: (state) => state.accessToken ? `Bearer ${state.accessToken}` : '',
    isAdmin: (state) => state.user?.roles.includes('admin') ?? false,
    isConductor: (state) => state.user?.roles.includes('conductor') ?? false,
    isPasajero: (state) => state.user?.roles.includes('pasajero') ?? false,
  },

  actions: {
    async login(credentials: { email: string; password: string }) {
      const { data } = await api.post('/api/token/', credentials)
      this.setTokens(data.access, data.refresh)
      await this.fetchUser()
      router.push('/')
    },

    async logout() {
      if (this.refreshToken) {
        try { await api.post('/api/token/blacklist/', { refresh: this.refreshToken }) } catch {}
      }
      this.clearTokens()
      router.push('/login/loginpage')
    },

    async refreshAccessToken() {
      if (!this.refreshToken) throw new Error('No refresh token')
      const { data } = await api.post('/api/token/refresh/', { refresh: this.refreshToken })
      this.setTokens(data.access, this.refreshToken)
    },

    async fetchUser() {
      const { data } = await api.get('/api/me/')
      this.user = data
    },

    setTokens(access: string, refresh: string) {
      this.accessToken = access
      this.refreshToken = refresh
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      api.defaults.headers.common.Authorization = `Bearer ${access}`
    },

    clearTokens() {
      this.accessToken = this.refreshToken = this.user = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      delete api.defaults.headers.common.Authorization
    },

    async initializeAuth() {
      if (this.accessToken) {
        api.defaults.headers.common.Authorization = `Bearer ${this.accessToken}`
        try {
          await this.fetchUser()
        } catch {
          try {
            await this.refreshAccessToken()
            await this.fetchUser()
          } catch {
            this.clearTokens()
          }
        }
      }
    },
  },
})