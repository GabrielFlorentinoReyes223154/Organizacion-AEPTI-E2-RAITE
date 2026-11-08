<template>
  <section class="destacada raite-sobre-azul" :aria-label="etiqueta">
    <span class="destacada__circulo destacada__circulo--grande" aria-hidden="true" />
    <span class="destacada__circulo destacada__circulo--chico" aria-hidden="true" />
    <span class="destacada__punto" aria-hidden="true" />

    <p class="destacada__etiqueta">{{ etiqueta }}</p>

    <template v-if="viaje">
      <div class="destacada__fila">
        <div class="destacada__hora-grupo">
          <p class="destacada__hora raite-dato">{{ hora(viaje.fecha_hora) }}</p>
          <slot name="estado" />
        </div>
        <RutaViaje
          class="destacada__ruta"
          :punto="viaje.punto_referencia.nombre"
          :campus="viaje.campus"
          :sentido="viaje.sentido"
          sobre-azul
          grande
        />
      </div>
      <div class="destacada__separador" aria-hidden="true" />
      <div class="destacada__pie">
        <div class="destacada__info"><slot name="pie" /></div>
        <slot name="accion" />
      </div>
    </template>

    <div v-else class="destacada__vacia">
      <slot name="vacia" />
    </div>
  </section>
</template>

<script setup lang="ts">
// "Tu próximo raite": la única tarjeta azul de una pantalla (DESIGN.md, la regla del azul que señala).
import type { Viaje } from '@/api/tipos';
import { hora } from '@/utils/formato';
import RutaViaje from './RutaViaje.vue';

defineProps<{ etiqueta: string; viaje: Viaje | null }>();
</script>

<style scoped lang="scss">
.destacada {
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 28px;
  border-radius: 24px;
  background: var(--raite-azul);
  color: var(--raite-blanco);
  box-shadow: var(--raite-sombra-destacada);
  > *:not(.destacada__circulo):not(.destacada__punto) {
    position: relative;
  }
}
.destacada__circulo,
.destacada__punto {
  position: absolute;
  border-radius: 999px;
  pointer-events: none;
}
.destacada__circulo--grande {
  width: 280px;
  height: 280px;
  right: -80px;
  top: -110px;
  background: var(--raite-azul-hondo);
}
.destacada__circulo--chico {
  width: 130px;
  height: 130px;
  right: 180px;
  bottom: -70px;
  background: rgba(255, 255, 255, 0.07);
}
.destacada__punto {
  width: 16px;
  height: 16px;
  right: 56px;
  top: 40px;
  background: var(--raite-amarillo);
}
.destacada__etiqueta {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--raite-azul-niebla);
}
.destacada__fila {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 16px 32px;
}
.destacada__hora-grupo {
  display: flex;
  align-items: flex-end;
  gap: 12px;
}
.destacada__hora {
  margin: 0;
  font-size: 4rem;
  line-height: 0.95;
  font-weight: 700;
  letter-spacing: -0.02em;
}
.destacada__ruta {
  flex: 1 1 260px;
  min-width: 0;
}
.destacada__separador {
  height: 1px;
  background: rgba(255, 255, 255, 0.18);
}
.destacada__pie {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.destacada__info {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px 24px;
}
.destacada__vacia {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 16px;
  padding: 8px 0 4px;
}
</style>
