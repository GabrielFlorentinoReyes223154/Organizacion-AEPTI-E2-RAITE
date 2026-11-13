<template>
  <span
    class="avatar"
    :class="`avatar--${tono}`"
    :style="{ width: `${tam}px`, height: `${tam}px`, fontSize: `${tam * 0.38}px` }"
    aria-hidden="true"
  >
    <!-- El nombre siempre va junto al avatar, así que la foto es decorativa (alt vacío). -->
    <img
      v-if="src && !fallo"
      :src="src"
      alt=""
      class="avatar__foto"
      loading="lazy"
      decoding="async"
      @error="fallo = true"
    />
    <template v-else>{{ letras }}</template>
  </span>
</template>

<script setup lang="ts">
// Foto de perfil o, si no hay (o la URL firmada ya venció), las iniciales.
import { computed, ref, watch } from 'vue';
import { iniciales, urlFoto } from '@/utils/formato';

const props = withDefaults(
  defineProps<{
    nombre: string;
    foto?: string | null;
    tam?: number;
    tono?: 'azul' | 'verde' | 'solido';
  }>(),
  {
    foto: null,
    tam: 48,
    tono: 'azul',
  },
);

const letras = computed(() => iniciales(props.nombre));
const src = computed(() => urlFoto(props.foto));
const fallo = ref(false);
watch(src, () => (fallo.value = false));
</script>

<style scoped lang="scss">
.avatar {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  font-weight: 700;
  overflow: hidden;
}
.avatar__foto {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
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
