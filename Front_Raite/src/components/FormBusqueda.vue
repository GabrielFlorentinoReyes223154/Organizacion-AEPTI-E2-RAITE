<template>
  <div class="form-busqueda raite-pila raite-pila--grupos">
    <SelectorPunto
      v-model="modelo.punto"
      :hint="modelo.ubicacion && !modelo.punto ? 'Usando tu ubicación' : undefined"
      @ubicacion="(lat, lon) => (modelo.ubicacion = [lat, lon])"
    />

    <fieldset class="form-busqueda__grupo">
      <legend class="raite-etiqueta">¿Vas o regresas?</legend>
      <q-btn-toggle
        v-model="modelo.sentido"
        class="raite-opciones"
        no-caps
        unelevated
        toggle-color="primary"
        :options="[
          { label: 'Hacia el campus', value: 'HACIA_CAMPUS' },
          { label: 'Desde el campus', value: 'DESDE_CAMPUS' },
        ]"
      />
    </fieldset>

    <SelectorCampus v-model="modelo.campus" etiqueta="¿Qué campus?" permitir-cualquiera />

    <div class="form-busqueda__fila">
      <div>
        <label :for="`${id}-dia`" class="raite-etiqueta">Día</label>
        <q-select
          :for="`${id}-dia`"
          :model-value="modelo.dia ?? ''"
          :options="dias"
          emit-value
          map-options
          outlined
          @update:model-value="(v: string) => (modelo.dia = v || null)"
        />
      </div>
      <div>
        <label :for="`${id}-hora`" class="raite-etiqueta">Cerca de las</label>
        <q-select
          :for="`${id}-hora`"
          :model-value="modelo.hora ?? ''"
          :options="horas"
          emit-value
          map-options
          outlined
          :disable="!modelo.dia"
          options-dense
          @update:model-value="(v: string) => (modelo.hora = v || null)"
        />
      </div>
    </div>
    <p v-if="modelo.dia && modelo.hora" class="raite-ayuda form-busqueda__nota">
      Te mostramos los que salen una hora antes o después.
    </p>

    <fieldset class="form-busqueda__grupo">
      <legend class="raite-etiqueta">Qué tan lejos del punto</legend>
      <q-btn-toggle
        v-model="modelo.radio"
        class="raite-opciones"
        no-caps
        unelevated
        toggle-color="primary"
        :options="RADIOS.map((r) => ({ label: `${r} km`, value: r }))"
      />
    </fieldset>
  </div>
</template>

<script setup lang="ts">
// Filtros de la búsqueda (RF-04): punto o ubicación, sentido, campus, día, hora y radio.
import { computed, useId } from 'vue';
import { claveDia, diaDeClave, sumarDias } from '@/utils/formato';
import SelectorCampus from './SelectorCampus.vue';
import SelectorPunto from './SelectorPunto.vue';
import type { Busqueda } from './busqueda';

const RADIOS = [3, 5, 10, 15];

const modelo = defineModel<Busqueda>({ required: true });
const id = useId();

const dias = computed(() => {
  const hoy = claveDia();
  return [
    { label: 'Cualquier día', value: '' },
    ...Array.from({ length: 7 }, (_, i) => {
      const clave = sumarDias(hoy, i);
      return { label: diaDeClave(clave), value: clave };
    }),
  ];
});

const horas = [
  { label: 'Cualquier hora', value: '' },
  ...Array.from({ length: 33 }, (_, i) => {
    const minutos = 6 * 60 + i * 30; // de 06:00 a 22:00
    const hhmm = `${String(Math.floor(minutos / 60)).padStart(2, '0')}:${String(minutos % 60).padStart(2, '0')}`;
    return { label: hhmm, value: hhmm };
  }),
];
</script>

<style scoped lang="scss">
.form-busqueda__grupo {
  margin: 0;
  padding: 0;
  border: 0;
  min-width: 0;
}
.form-busqueda__fila {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}
.form-busqueda__nota {
  margin-top: -16px;
}
</style>
