<template>
  <div class="ruta" :class="{ 'ruta--azul': sobreAzul, 'ruta--grande': grande }">
    <template v-for="(parada, i) in paradas" :key="parada.tipo">
      <span v-if="parada.tipo === 'punto'" class="ruta__punto" aria-hidden="true" />
      <span v-else class="ruta__campus" aria-hidden="true" />

      <span v-if="parada.tipo === 'punto'" class="ruta__nombre">{{ punto }}</span>
      <span v-else class="ruta__destino">
        <PlacaCampus :codigo="campus.codigo" :nombre="campus.nombre" :clara="sobreAzul" />
        <span class="ruta__campus-nombre">{{ campus.nombre }}</span>
      </span>

      <template v-if="i === 0">
        <span class="ruta__linea" aria-hidden="true" />
        <span class="ruta__medio"><slot /></span>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
// Las dos paradas del viaje unidas por una línea (tarjeta y detalle, DESIGN.md).
import { computed } from 'vue';
import type { Campus, Sentido } from '@/api/tipos';
import PlacaCampus from './PlacaCampus.vue';

const props = defineProps<{
  punto: string;
  campus: Pick<Campus, 'codigo' | 'nombre'>;
  sentido: Sentido;
  sobreAzul?: boolean;
  grande?: boolean;
}>();

const paradas = computed(() =>
  props.sentido === 'DESDE_CAMPUS'
    ? [{ tipo: 'campus' as const }, { tipo: 'punto' as const }]
    : [{ tipo: 'punto' as const }, { tipo: 'campus' as const }],
);
</script>

<style scoped lang="scss">
.ruta {
  display: grid;
  grid-template-columns: 20px minmax(0, 1fr);
  column-gap: 12px;
  row-gap: 6px;
  align-items: center;
}
.ruta__punto {
  justify-self: center;
  width: 12px;
  height: 12px;
  box-sizing: border-box;
  border: 3px solid var(--raite-azul);
  border-radius: 999px;
}
.ruta__campus {
  justify-self: center;
  width: 10px;
  height: 10px;
  border-radius: 2px;
  background: var(--raite-azul);
}
.ruta__linea {
  justify-self: center;
  width: 2px;
  min-height: 14px;
  height: 100%;
  background: var(--raite-azul-niebla);
}
.ruta__medio {
  font-size: 0.875rem;
  color: var(--raite-gris);
  &:empty {
    min-height: 2px;
  }
}
.ruta__nombre {
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.3;
}
.ruta__destino {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}
.ruta__campus-nombre {
  min-width: 0;
  font-size: 0.875rem;
  color: var(--raite-gris);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ruta--grande {
  .ruta__nombre {
    font-size: 1.125rem;
  }
  .ruta__campus-nombre {
    font-size: 1rem;
    font-weight: 600;
  }
}

.ruta--azul {
  color: var(--raite-blanco);
  .ruta__punto {
    border-color: var(--raite-blanco);
  }
  .ruta__campus {
    background: var(--raite-blanco);
  }
  .ruta__medio,
  .ruta__campus-nombre {
    color: var(--raite-azul-niebla);
  }
  .ruta__campus-nombre {
    color: var(--raite-blanco);
  }
}
</style>
