<template>
  <q-page class="raite-contenedor raite-contenedor--angosto">
    <EstadoVacio icono="wrong_location" titulo="Esta página no existe">
      Puede que el enlace esté mal escrito o que el viaje ya no esté disponible.
      <template #acciones>
        <q-btn color="primary" unelevated no-caps label="Ir al inicio" to="/" />
      </template>
    </EstadoVacio>
  </q-page>
</template>

<script setup lang="ts">
import EstadoVacio from '@/components/EstadoVacio.vue';

definePage({ meta: { titulo: 'No encontrada', atras: '/' } });
</script>
