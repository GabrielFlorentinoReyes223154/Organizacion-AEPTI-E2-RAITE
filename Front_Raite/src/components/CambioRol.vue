<template>
  <div class="cambio-rol" role="group" :aria-label="'Usar Raite para'">
    <button
      v-for="opcion in opciones"
      :key="opcion.papel"
      type="button"
      class="cambio-rol__opcion"
      :aria-pressed="sesion.papel === opcion.papel"
      @click="elegir(opcion.papel)"
    >
      {{ opcion.texto }}
    </button>
  </div>
</template>

<script setup lang="ts">
// Cambio entre pasajero y conductor para quien tiene rol AMBOS (reemplaza al RoleSelectionModal).
import { useRouter } from 'vue-router';
import type { Papel } from '@/api/tipos';
import { useSesionStore } from '@/stores/sesion';

const sesion = useSesionStore();
const router = useRouter();

// Textos neutros: el papel se nombra por lo que haces, no por género.
const opciones: { papel: Papel; texto: string }[] = [
  { papel: 'pasajero', texto: 'Pido raite' },
  { papel: 'conductor', texto: 'Doy raite' },
];

function elegir(papel: Papel) {
  if (sesion.papel === papel) return;
  sesion.cambiarPapel(papel);
  void router.push(sesion.inicio);
}
</script>

<style scoped lang="scss">
// Píldoras sobre fondo claro: la opción elegida en azul con texto blanco (9.56:1),
// la otra en azul sobre azul tenue (8.12:1). Sobre la barra azul tenue de escritorio el fondo pasa a blanco.
.cambio-rol {
  display: inline-flex;
  flex-shrink: 0;
  gap: 2px;
  padding: 3px;
  border-radius: 999px;
  background: var(--raite-azul-tenue);
}
.cambio-rol__opcion {
  height: 40px;
  padding: 0 14px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--raite-azul);
  font: inherit;
  font-size: 0.875rem;
  font-weight: 700;
  white-space: nowrap;
  cursor: pointer;
  &:hover:not([aria-pressed='true']) {
    background: var(--raite-azul-tenue-hover);
  }
  &[aria-pressed='true'] {
    background: var(--raite-azul);
    color: var(--raite-blanco);
  }
  &:focus-visible {
    outline: 2px solid var(--raite-azul);
    outline-offset: 2px;
  }
}
@media (max-width: 380px) {
  .cambio-rol__opcion {
    padding: 0 8px;
  }
}
</style>
