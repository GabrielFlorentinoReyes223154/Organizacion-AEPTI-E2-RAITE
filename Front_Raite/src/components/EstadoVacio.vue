<template>
  <div class="vacio" role="status">
    <q-icon :name="icono" size="48px" class="vacio__icono" aria-hidden="true" />
    <p class="vacio__titulo">{{ titulo }}</p>
    <p v-if="$slots.default" class="vacio__texto"><slot /></p>
    <div v-if="$slots.acciones" class="vacio__acciones"><slot name="acciones" /></div>
  </div>
</template>

<script setup lang="ts">
// Estado vacío de DESIGN.md: qué pasa y cómo salir de ahí. Nunca una pantalla en blanco.
defineProps<{ icono: string; titulo: string }>();
</script>

<style scoped lang="scss">
.vacio {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 8px;
  padding: 32px 16px;
}
.vacio__icono {
  color: var(--raite-gris);
}
.vacio__titulo {
  margin: 0;
  max-width: 34ch;
  font-size: 1.125rem;
  font-weight: 700;
  line-height: 1.3;
}
.vacio__texto {
  margin: 0;
  max-width: 40ch;
  color: var(--raite-gris);
}
.vacio__acciones {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin-top: 8px;
}
</style>
