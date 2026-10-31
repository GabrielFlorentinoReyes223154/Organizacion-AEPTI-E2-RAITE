<template>
  <q-page class="flex flex-center">
    <div class="text-center">
      <h3 class="q-mb-md">Pasajero</h3>
      <q-btn label="Cerrar sesión" color="negative" @click="logout" />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth-store';

const authStore = useAuthStore();

const logout = async () => {
  await authStore.logout();
};
</script>