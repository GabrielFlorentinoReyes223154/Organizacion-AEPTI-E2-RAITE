<template>
  <template v-if="route.matched.length">
    <PublicoLayout v-if="route.meta.publico">
      <router-view />
    </PublicoLayout>
    <AppLayout v-else>
      <router-view />
    </AppLayout>
  </template>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router';
import AppLayout from '@/layouts/AppLayout.vue';
import PublicoLayout from '@/layouts/PublicoLayout.vue';

const route = useRoute();
</script>
