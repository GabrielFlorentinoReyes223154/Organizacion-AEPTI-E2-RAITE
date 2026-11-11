<template>
  <div class="selector-carrera">
    <SelectorCampus
      v-model="campus"
      etiqueta="Campus donde estudias"
      :disabled="disabled || cargando"
    />
    <div>
      <label :for="idCarrera" class="raite-etiqueta">Carrera</label>
      <q-select
        :for="idCarrera"
        :model-value="seleccionada"
        :options="opciones"
        option-value="id"
        option-label="nombre"
        outlined
        use-input
        fill-input
        hide-selected
        input-debounce="0"
        :disable="disabled || campus === null"
        :loading="cargando"
        :placeholder="campus === null ? 'Primero elige tu campus' : 'Busca o elige tu carrera'"
        :hint="campus === null ? '' : `${carrerasDelCampus.length} carreras en ${codigoCampus}`"
        :error="!!error"
        :error-message="error"
        hide-bottom-space
        @filter="filtrar"
        @update:model-value="(c: Carrera | null) => (modelo = c?.id ?? null)"
      >
        <template #option="{ itemProps, opt }">
          <q-item v-bind="itemProps">
            <q-item-section>
              <q-item-label>{{ opt.nombre }}</q-item-label>
              <q-item-label caption>{{ opt.area }}</q-item-label>
            </q-item-section>
          </q-item>
        </template>
        <template #no-option>
          <q-item>
            <q-item-section class="text-grey-8">
              No encontramos esa carrera en {{ codigoCampus }}.
            </q-item-section>
          </q-item>
        </template>
      </q-select>
    </div>
  </div>
</template>

<script setup lang="ts">
// Campus y carrera en cascada: la carrera se habilita al elegir el campus y solo muestra las de ese
// campus (catálogo oficial de la UACJ). El v-model es el id de la carrera; el campus sale de ella.
import { computed, onMounted, ref, useId, watch } from 'vue';
import type { Carrera } from '@/api/tipos';
import SelectorCampus from '@/components/SelectorCampus.vue';
import { useCatalogosStore } from '@/stores/catalogos';
import { avisarError } from '@/utils/avisar';

withDefaults(defineProps<{ error?: string; disabled?: boolean }>(), {
  error: '',
  disabled: false,
});
const modelo = defineModel<number | null>({ default: null });

const catalogos = useCatalogosStore();
const idCarrera = useId();
const cargando = ref(false);
const campus = ref<number | null>(null);

const seleccionada = computed(() => catalogos.carreraPorId(modelo.value));
const carrerasDelCampus = computed(() =>
  catalogos.carreras.filter((c) => c.campus === campus.value),
);
const codigoCampus = computed(() => catalogos.campusPorId(campus.value)?.codigo ?? '');

// Sin acentos ni mayúsculas, para que "mecatronica" encuentre "Mecatrónica".
const normalizar = (texto: string) =>
  texto
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase();

// Las opciones se fijan dentro del callback de @filter (patrón de Quasar): así la lista que ve
// el usuario y la que usa el q-select al elegir (clic o Enter) son siempre la misma.
const opciones = ref<Carrera[]>([]);

function coinciden(texto: string) {
  const buscado = normalizar(texto.trim());
  if (!buscado) return carrerasDelCampus.value;
  return carrerasDelCampus.value.filter((c) => normalizar(c.nombre).includes(buscado));
}

function filtrar(texto: string, actualizar: (fn: () => void) => void) {
  actualizar(() => {
    opciones.value = coinciden(texto);
  });
}

// Al cambiar de campus, la carrera elegida se borra si no se imparte en el nuevo.
watch(campus, (nuevo) => {
  opciones.value = coinciden('');
  if (seleccionada.value && seleccionada.value.campus !== nuevo) modelo.value = null;
});

// Si llega una carrera ya elegida (perfil), su campus queda marcado.
watch(
  seleccionada,
  (carrera) => {
    if (carrera && campus.value !== carrera.campus) campus.value = carrera.campus;
  },
  { immediate: true },
);

onMounted(async () => {
  cargando.value = true;
  try {
    await catalogos.cargarCarreras();
  } catch (e) {
    avisarError(e);
  } finally {
    cargando.value = false;
  }
});
</script>

<style scoped lang="scss">
.selector-carrera {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 20px 16px;
  @media (min-width: 1024px) {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    align-items: start;
  }
}
</style>
