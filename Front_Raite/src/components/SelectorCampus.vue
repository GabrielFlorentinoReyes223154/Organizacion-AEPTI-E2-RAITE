<template>
  <!-- Compacto: menú desplegable (barra de filtros de computadora). -->
  <div v-if="compacto" class="selector-campus selector-campus--compacto">
    <label :for="id" class="raite-etiqueta">{{ etiqueta }}</label>
    <q-select
      :for="id"
      :model-value="modelo ?? ''"
      :options="opcionesMenu"
      emit-value
      map-options
      outlined
      :disable="disabled"
      @update:model-value="(v: number | '') => (modelo = v === '' ? null : v)"
    />
  </div>
  <fieldset v-else class="selector-campus">
    <legend class="raite-etiqueta">{{ etiqueta }}</legend>
    <div class="selector-campus__opciones">
      <button
        v-if="permitirCualquiera"
        type="button"
        class="selector-campus__opcion selector-campus__opcion--todos"
        :aria-pressed="modelo === null"
        @click="modelo = null"
      >
        Todos
      </button>
      <button
        v-for="c in catalogos.campus"
        :key="c.id"
        type="button"
        class="selector-campus__opcion"
        :aria-pressed="modelo === c.id"
        :aria-label="`${c.codigo}, ${c.nombre}`"
        :disabled="disabled"
        @click="modelo = c.id"
      >
        {{ c.codigo }}
      </button>
    </div>
    <p class="selector-campus__nombre">
      {{ elegido?.nombre ?? (permitirCualquiera ? 'Cualquier campus' : 'Elige un campus') }}
    </p>
  </fieldset>
</template>

<script setup lang="ts">
// Los campus como botones con forma de placa (CU, IIT, ICB, ICSA, IADA).
import { computed, useId } from 'vue';
import { useCatalogosStore } from '@/stores/catalogos';

const props = withDefaults(
  defineProps<{
    etiqueta?: string;
    permitirCualquiera?: boolean;
    disabled?: boolean;
    compacto?: boolean;
  }>(),
  {
    etiqueta: 'Campus',
    permitirCualquiera: false,
    disabled: false,
    compacto: false,
  },
);
const modelo = defineModel<number | null>({ default: null });
const catalogos = useCatalogosStore();
const elegido = computed(() => catalogos.campusPorId(modelo.value));
const id = useId();

const opcionesMenu = computed(() => [
  ...(props.permitirCualquiera ? [{ label: 'Todos los campus', value: '' as const }] : []),
  ...catalogos.campus.map((c) => ({ label: `${c.codigo} · ${c.nombre}`, value: c.id })),
]);
</script>

<style scoped lang="scss">
.selector-campus {
  margin: 0;
  padding: 0;
  border: 0;
  min-width: 0;
}
.selector-campus__opciones {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(56px, 1fr));
  gap: 8px;
}
.selector-campus__opcion {
  height: 48px;
  border: 1px solid var(--raite-borde-campo);
  border-radius: 12px;
  background: var(--raite-blanco);
  color: var(--raite-azul);
  font: inherit;
  font-size: 0.9375rem;
  font-weight: 700;
  cursor: pointer;
  &:hover:not(:disabled) {
    background: var(--raite-azul-tenue);
  }
  &[aria-pressed='true'] {
    border-color: var(--raite-azul);
    background: var(--raite-azul);
    color: var(--raite-blanco);
    box-shadow: inset 0 -4px 0 var(--raite-amarillo);
  }
  &:disabled {
    cursor: default;
    background: var(--raite-gris-tenue);
    color: var(--raite-gris-deshabilitado);
    border-color: transparent;
  }
}
.selector-campus__opcion--todos {
  color: var(--raite-negro);
}
.selector-campus__nombre {
  margin: 8px 0 0;
  font-size: 0.875rem;
  color: var(--raite-gris);
}
</style>
