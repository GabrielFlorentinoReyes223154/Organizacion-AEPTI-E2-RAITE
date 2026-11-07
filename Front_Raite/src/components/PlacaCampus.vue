<template>
  <span class="placa-campus" :class="{ 'placa-campus--clara': clara }" :title="nombre">{{
    codigo
  }}</span>
</template>

<script setup lang="ts">
// La señal del sistema (DESIGN.md): código del campus en azul con una barra amarilla abajo.
defineProps<{
  codigo: string;
  nombre?: string;
  /** Versión blanca, para usarla sobre fondos azules. */
  clara?: boolean;
}>();
</script>

<style scoped lang="scss">
.placa-campus {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  height: 28px;
  padding: 0 8px;
  border-radius: 12px;
  background: var(--raite-azul);
  color: var(--raite-blanco);
  font-size: 0.875rem;
  font-weight: 700;
  line-height: 1;
  box-shadow: inset 0 -3px 0 var(--raite-amarillo);
}
.placa-campus--clara {
  background: var(--raite-blanco);
  color: var(--raite-azul);
}
</style>
