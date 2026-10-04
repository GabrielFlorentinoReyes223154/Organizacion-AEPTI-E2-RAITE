<template>
  <MainLayout>
    <template #default>
      <q-page class="flex flex-center">
        <div class="column items-center">
          <img alt="Raite logo" src="~@/assets/raite.svg" style="width: 200px; height: 200px" />

          <q-btn class="q-mt-md" color="primary" to="/second" label="Go to Second Page" no-caps />
        </div>
      </q-page>
    </template>
  </MainLayout>
</template>

<script setup lang="ts">
import MainLayout from '@/layouts/MainLayout.vue';
</script>