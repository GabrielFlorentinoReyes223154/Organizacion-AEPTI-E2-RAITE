<template>
  <article class="tarjeta-viaje" :class="{ 'tarjeta-viaje--compacta': compacta }">
    <router-link :to="to" class="tarjeta-viaje__enlace" :aria-label="etiqueta">
      <div class="tarjeta-viaje__arriba">
        <div>
          <p class="tarjeta-viaje__hora raite-dato">{{ horaTexto }}</p>
          <p class="tarjeta-viaje__dia">{{ diaTexto }}</p>
        </div>
        <slot name="estado">
          <span class="tarjeta-viaje__lugares">{{ lugaresTexto }}</span>
        </slot>
      </div>

      <RutaViaje
        :punto="viaje.punto_referencia.nombre"
        :campus="viaje.campus"
        :sentido="viaje.sentido"
      />

      <div class="tarjeta-viaje__abajo">
        <span v-if="mostrarConductor">{{ conductorTexto }}</span>
        <span v-if="mostrarConductor" class="tarjeta-viaje__calif">
          <q-icon name="star" size="16px" aria-hidden="true" />
          {{ califTexto }}
        </span>
        <slot name="abajo" />
        <span v-if="distanciaTexto" class="tarjeta-viaje__distancia">{{ distanciaTexto }}</span>
      </div>
    </router-link>
    <slot name="pie" />
  </article>
</template>

<script setup lang="ts">
// La tarjeta de viaje de DESIGN.md: hora, ruta con placa de campus, lugares y conductor.
import { computed } from 'vue';
import type { RouteLocationRaw } from 'vue-router';
import type { Viaje } from '@/api/tipos';
import {
  calificacion,
  diaCorto,
  distancia,
  hora,
  lugares,
  nombreCorto,
  textoSentido,
} from '@/utils/formato';
import RutaViaje from './RutaViaje.vue';

const props = withDefaults(
  defineProps<{
    viaje: Viaje;
    to: RouteLocationRaw;
    mostrarConductor?: boolean;
    compacta?: boolean;
  }>(),
  { mostrarConductor: true, compacta: false },
);

const horaTexto = computed(() => hora(props.viaje.fecha_hora));
const diaTexto = computed(() => diaCorto(props.viaje.fecha_hora));
const lugaresTexto = computed(() =>
  lugares(props.viaje.lugares_disponibles, props.viaje.lugares_ofrecidos),
);
const conductorTexto = computed(() => nombreCorto(props.viaje.conductor.nombre_completo));
const califTexto = computed(() => calificacion(props.viaje.conductor.calificacion) ?? 'Nuevo');
const distanciaTexto = computed(() => distancia(props.viaje.distancia_km));

const etiqueta = computed(() => {
  const v = props.viaje;
  const partes = [
    `${diaTexto.value} a las ${horaTexto.value}`,
    `${textoSentido(v.sentido).toLowerCase()} ${v.campus.nombre}`,
    `desde ${v.punto_referencia.nombre}`,
    lugaresTexto.value + ' libres',
  ];
  if (props.mostrarConductor)
    partes.push(`con ${conductorTexto.value}, calificación ${califTexto.value}`);
  if (distanciaTexto.value) partes.push(distanciaTexto.value);
  return partes.join(', ');
});
</script>

<style scoped lang="scss">
.tarjeta-viaje {
  display: flex;
  flex-direction: column;
  background: var(--raite-blanco);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: var(--raite-sombra-tarjeta);
}
// En una cuadrícula las tarjetas de una fila miden lo mismo; el pie queda abajo.
.tarjeta-viaje__enlace {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  color: inherit;
  text-decoration: none;
  border-radius: 20px;
  &:hover {
    background: var(--raite-blanco-hover);
  }
  &:focus-visible {
    outline-offset: -3px;
  }
}
.tarjeta-viaje__arriba {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}
.tarjeta-viaje__hora {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: var(--raite-azul);
}
.tarjeta-viaje__dia {
  margin: 4px 0 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--raite-gris);
}
.tarjeta-viaje__lugares {
  display: inline-flex;
  align-items: center;
  height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  background: var(--raite-azul-tenue);
  color: var(--raite-azul);
  font-size: 0.875rem;
  font-weight: 600;
  white-space: nowrap;
}
.tarjeta-viaje__abajo {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px 16px;
  font-size: 0.875rem;
  font-weight: 600;
  &:empty {
    display: none;
  }
}
.tarjeta-viaje__calif {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.tarjeta-viaje__distancia {
  margin-left: auto;
  color: var(--raite-gris);
}
.tarjeta-viaje--compacta .tarjeta-viaje__hora {
  font-size: 1.5rem;
}
</style>
