<template>
  <div class="selector-punto">
    <label :for="id" class="raite-etiqueta">{{ etiqueta }}</label>
    <q-select
      :for="id"
      v-model="modelo"
      :options="opciones"
      option-value="id"
      option-label="nombre"
      emit-value
      map-options
      use-input
      fill-input
      hide-selected
      input-debounce="0"
      outlined
      :disable="disable"
      :error="!!error"
      :error-message="error ?? undefined"
      :placeholder="modelo ? undefined : 'Escribe: Oxxo, Del Río, una calle…'"
      :hint="hint"
      :loading="catalogos.cargando !== null"
      behavior="menu"
      @filter="filtrar"
    >
      <template #prepend>
        <q-icon name="place" color="primary" aria-hidden="true" />
      </template>
      <template #option="{ itemProps, opt }">
        <q-item v-bind="itemProps">
          <q-item-section>
            <q-item-label>{{ (opt as PuntoReferencia).nombre }}</q-item-label>
            <q-item-label v-if="distancias[(opt as PuntoReferencia).id] !== undefined" caption>
              {{ distanciaTexto((opt as PuntoReferencia).id) }}
            </q-item-label>
          </q-item-section>
        </q-item>
      </template>
      <template #no-option>
        <q-item>
          <q-item-section class="text-gris"
            >No hay puntos con ese nombre. Prueba con la calle o la tienda.</q-item-section
          >
        </q-item>
      </template>
    </q-select>
    <q-btn
      v-if="conUbicacion"
      flat
      no-caps
      color="primary"
      icon="my_location"
      label="Usar mi ubicación"
      class="selector-punto__ubicacion"
      :loading="buscandoUbicacion"
      :disable="disable"
      @click="usarUbicacion"
    />
  </div>
</template>

<script setup lang="ts">
// Elegir un punto de referencia del catálogo (regla 1: nunca direcciones exactas).
import { computed, ref, useId } from 'vue';
import type { PuntoReferencia } from '@/api/tipos';
import { useCatalogosStore } from '@/stores/catalogos';
import { avisarAdvertencia } from '@/utils/avisar';
import { distancia } from '@/utils/formato';

withDefaults(
  defineProps<{
    etiqueta?: string;
    hint?: string | undefined;
    error?: string | null;
    conUbicacion?: boolean;
    disable?: boolean;
  }>(),
  { etiqueta: '¿De dónde sales?', error: null, conUbicacion: true, disable: false },
);
const emit = defineEmits<{ ubicacion: [lat: number, lon: number] }>();
const modelo = defineModel<number | null>({ default: null });

const id = useId();
const catalogos = useCatalogosStore();
const filtro = ref('');
const distancias = ref<Record<number, number>>({});
const buscandoUbicacion = ref(false);

void catalogos.cargar();

function normalizar(texto: string) {
  return texto.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
}

const opciones = computed(() => {
  const lista = catalogos.puntos;
  const conDistancia = Object.keys(distancias.value).length
    ? [...lista].sort((a, b) => (distancias.value[a.id] ?? 999) - (distancias.value[b.id] ?? 999))
    : lista;
  if (!filtro.value) return conDistancia;
  const partes = normalizar(filtro.value).split(/\s+/).filter(Boolean);
  return conDistancia.filter((p) => {
    const nombre = normalizar(p.nombre);
    return partes.every((parte) => nombre.includes(parte));
  });
});

function filtrar(valor: string, actualizar: (fn: () => void) => void) {
  actualizar(() => {
    filtro.value = valor;
  });
}

function distanciaTexto(puntoId: number) {
  return distancia(distancias.value[puntoId]);
}

function usarUbicacion() {
  if (!('geolocation' in navigator)) {
    avisarAdvertencia('Tu navegador no comparte la ubicación. Elige el punto de la lista.');
    return;
  }
  buscandoUbicacion.value = true;
  navigator.geolocation.getCurrentPosition(
    (posicion) => {
      const { latitude: lat, longitude: lon } = posicion.coords;
      catalogos
        .cercanos(lat, lon)
        .then((cercanos) => {
          distancias.value = Object.fromEntries(cercanos.map((p) => [p.id, p.distancia_km ?? 999]));
          const masCercano = cercanos[0];
          if (masCercano) modelo.value = masCercano.id;
          emit('ubicacion', lat, lon);
        })
        .catch(() =>
          avisarAdvertencia('No pudimos buscar puntos cerca de ti. Elige el punto de la lista.'),
        )
        .finally(() => {
          buscandoUbicacion.value = false;
        });
    },
    () => {
      buscandoUbicacion.value = false;
      avisarAdvertencia('No pudimos obtener tu ubicación. Elige el punto de la lista.');
    },
    { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 },
  );
}
</script>

<style scoped lang="scss">
.selector-punto {
  display: flex;
  flex-direction: column;
}
.selector-punto__ubicacion {
  align-self: flex-start;
  margin-top: 4px;
  margin-left: -8px;
}
</style>
