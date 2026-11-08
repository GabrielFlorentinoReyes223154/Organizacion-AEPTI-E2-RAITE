<template>
  <!-- Computadora: tarjeta dentro del contenido (no tapa el menú lateral). -->
  <section v-if="escritorio" class="barra-accion-linea" aria-label="Acciones">
    <p v-if="nota" class="barra-accion__nota">{{ nota }}</p>
    <div class="barra-accion-linea__botones"><slot /></div>
  </section>

  <!-- Celular: barra fija abajo, sobre la navegación. -->
  <q-page-sticky v-else position="bottom" expand class="barra-accion-sticky">
    <div class="barra-accion">
      <div class="barra-accion__contenido">
        <p v-if="nota" class="barra-accion__nota">{{ nota }}</p>
        <div class="barra-accion__botones"><slot /></div>
      </div>
    </div>
  </q-page-sticky>
</template>

<script setup lang="ts">
// La acción principal de una pantalla de detalle (DESIGN.md, Layout).
// En celular es una barra fija abajo; la página que la use debe llevar la clase `con-barra` para que el
// contenido no quede debajo. En computadora se dibuja donde esté en la página, como una tarjeta.
import { computed } from 'vue';
import { useQuasar } from 'quasar';

defineProps<{ nota?: string | undefined }>();

const $q = useQuasar();
const escritorio = computed(() => $q.screen.gt.sm);
</script>

<style scoped lang="scss">
.barra-accion-sticky {
  z-index: 2;
}
.barra-accion {
  width: 100%;
  background: var(--raite-blanco);
  box-shadow: var(--raite-sombra-barra);
  padding: 12px 16px calc(16px + env(safe-area-inset-bottom));
}
.barra-accion__contenido {
  max-width: 720px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.barra-accion__nota {
  margin: 0;
  text-align: center;
  font-size: 0.875rem;
  color: var(--raite-gris);
}
.barra-accion__botones {
  display: flex;
  gap: 8px;
  > * {
    flex: 1 1 0;
  }
}

.barra-accion-linea {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px;
  border-radius: 20px;
  background: var(--raite-blanco);
  box-shadow: var(--raite-sombra-tarjeta);
  .barra-accion__nota {
    text-align: left;
  }
}
.barra-accion-linea__botones {
  display: flex;
  flex-direction: column;
  gap: 10px;
  > :deep(.q-btn) {
    width: 100%;
    min-height: 52px;
  }
}
</style>
