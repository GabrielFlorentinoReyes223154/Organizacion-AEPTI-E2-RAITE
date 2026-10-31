<template>
  <div>
    <component :is="homeComponent" v-if="homeComponent" />
    <q-page v-else class="flex flex-center">
      <div v-if="authStore.user?.rol === 1" class="text-center">
        <h3 class="q-mb-md">Admin</h3>
        <q-btn label="Cerrar sesión" color="negative" @click="logout" />
      </div>
      <q-spinner v-else color="primary" size="3em" />
    </q-page>

    <RoleSelectionModal
      v-model="authStore.roleSelectionModal"
      @select="authStore.onRoleSelected"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth-store';
import RoleSelectionModal from '@/components/RoleSelectionModal.vue';
import HomePasajero from './home-pasajero.vue';
import HomeConductor from './home-conductor.vue';

const authStore = useAuthStore();

const homeComponent = computed(() => {
  if (authStore.user?.rol === 2) return HomePasajero;
  if (authStore.user?.rol === 3) return HomeConductor;
  if (authStore.user?.rol === 4) {
    if (authStore.activeRole === 'pasajero') return HomePasajero;
    if (authStore.activeRole === 'conductor') return HomeConductor;
  }
  return null;
});

const logout = async () => {
  await authStore.logout();
};

onMounted(() => {
  if (authStore.user?.rol === 4 && !authStore.activeRole) {
    void authStore.showRoleSelectionModal();
  }
});
</script>
