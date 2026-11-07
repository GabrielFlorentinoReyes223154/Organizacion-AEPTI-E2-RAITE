<template>
  <span
    class="avatar"
    :class="`avatar--${tono}`"
    :style="{ width: `${tam}px`, height: `${tam}px`, fontSize: `${tam * 0.38}px` }"
    aria-hidden="true"
  >
    {{ letras }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { iniciales } from '@/utils/formato';

const props = withDefaults(
  defineProps<{ nombre: string; tam?: number; tono?: 'azul' | 'verde' | 'solido' }>(),
  {
    tam: 48,
    tono: 'azul',
  },
);

const letras = computed(() => iniciales(props.nombre));
</script>

<style scoped lang="scss">
.avatar {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  font-weight: 700;
}
.avatar--azul {
  background: var(--raite-azul-tenue);
  color: var(--raite-azul);
}
.avatar--verde {
  background: var(--raite-verde-tenue);
  color: var(--raite-verde-texto);
}
.avatar--solido {
  background: var(--raite-azul);
  color: var(--raite-blanco);
}
</style>
