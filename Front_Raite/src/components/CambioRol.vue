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
.cambio-rol {
  display: inline-flex;
  flex-shrink: 0;
  padding: 3px;
  border-radius: 12px;
  background: var(--raite-azul-hondo);
}
.cambio-rol__opcion {
  height: 40px;
  padding: 0 12px;
  border: 0;
  border-radius: 9px;
  background: transparent;
  color: var(--raite-azul-niebla);
  font: inherit;
  font-size: 0.875rem;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
  &[aria-pressed='true'] {
    background: var(--raite-amarillo);
    color: var(--raite-negro);
    font-weight: 700;
  }
  &:focus-visible {
    outline: 2px solid var(--raite-amarillo);
    outline-offset: 2px;
  }
}
@media (max-width: 380px) {
  .cambio-rol__opcion {
    padding: 0 8px;
  }
}
</style>
