<template>
  <MainLayout>
    <template #default>
      <q-page class="flex flex-center">
        <q-btn color="secondary" to="/" label="Go to Index Page" no-caps />
      </q-page>
    </template>
  </MainLayout>
</template>

<script setup lang="ts">
import MainLayout from '@/layouts/MainLayout.vue';
</script>