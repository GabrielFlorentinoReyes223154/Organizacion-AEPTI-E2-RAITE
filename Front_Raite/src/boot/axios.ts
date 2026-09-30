import axios, { type AxiosError, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios';
import type { App } from 'vue';
import { useAuthStore } from '@/stores/auth-store';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

let isRefreshing = false;
let failedQueue: Array<(token: string | null) => void> = [];

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((cb) => cb(token));
  failedQueue = [];
};

api.interceptors.response.use(
  (res: AxiosResponse) => res,
  async (error: AxiosError) => {
    const authStore = useAuthStore();
    const originalRequest = error.config as RetryableRequestConfig;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push((token) => {
            if (token) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              resolve(api(originalRequest));
            } else {
              reject(new Error('Token refresh failed'));
            }
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        await authStore.refreshAccessToken();
        const token = authStore.accessToken!;
        processQueue(null, token);
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return api(originalRequest);
      } catch (err) {
        processQueue(err as Error, null);
        await authStore.logout();
        return Promise.reject(new Error('Authentication failed'));
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(new Error(error.message));
  },
);

export default ({ app }: { app: App }) => {
  app.config.globalProperties.$api = api;
};

export { api };
