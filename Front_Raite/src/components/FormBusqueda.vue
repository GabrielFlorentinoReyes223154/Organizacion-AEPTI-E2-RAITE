<template>
  <div
    class="form-busqueda raite-pila raite-pila--grupos"
    :class="{ 'form-busqueda--horizontal': horizontal }"
  >
    <SelectorPunto
      v-model="modelo.punto"
      :ubicacion-compacta="horizontal"
      :hint="modelo.ubicacion && !modelo.punto ? 'Usando tu ubicación' : undefined"
      @ubicacion="(lat, lon) => (modelo.ubicacion = [lat, lon])"
    />

    <fieldset class="form-busqueda__grupo form-busqueda__sentido">
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

    <SelectorCampus
      v-model="modelo.campus"
      etiqueta="¿Qué campus?"
      permitir-cualquiera
      :compacto="horizontal"
    />

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
    <p v-if="modelo.dia && modelo.hora && !horizontal" class="raite-ayuda form-busqueda__nota">
      Te mostramos los que salen una hora antes o después.
    </p>

    <div v-if="horizontal" class="form-busqueda__radio">
      <label :for="`${id}-radio`" class="raite-etiqueta">Distancia</label>
      <q-select
        :for="`${id}-radio`"
        v-model="modelo.radio"
        :options="RADIOS.map((r) => ({ label: `${r} km`, value: r }))"
        emit-value
        map-options
        outlined
      />
    </div>
    <fieldset v-else class="form-busqueda__grupo form-busqueda__radio">
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
// horizontal: barra de filtros de computadora (los grupos en fila y se acomodan en dos renglones si no caben).
withDefaults(defineProps<{ horizontal?: boolean }>(), { horizontal: false });
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

// --- Barra horizontal (computadora) ---
// En pantallas anchas (≥1700 px) cabe en un renglón; a 1280 px se acomoda en dos.
.form-busqueda--horizontal {
  flex-direction: row;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 16px;
  > .selector-punto {
    flex: 2 1 300px;
    // El select y el botón de ubicación en el mismo renglón.
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    column-gap: 8px;
    :deep(.raite-etiqueta) {
      grid-column: 1 / -1;
    }
    :deep(.selector-punto__ubicacion) {
      margin-top: 4px;
    }
  }
  > .form-busqueda__sentido {
    flex: 0 0 320px;
    :deep(.q-btn__content) {
      flex-wrap: nowrap;
      white-space: nowrap;
    }
  }
  > .selector-campus {
    flex: 1 1 200px;
  }
  > .form-busqueda__fila {
    flex: 1 1 380px;
  }
  > .form-busqueda__radio {
    flex: 0 0 120px;
  }
  :deep(.raite-opciones.q-btn-group > .q-btn-item) {
    padding: 0 8px;
  }
}
</style>
