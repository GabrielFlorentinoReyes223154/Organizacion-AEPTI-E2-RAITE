<template>
  <q-page-sticky position="bottom" expand class="barra-accion-sticky">
    <div class="barra-accion">
      <div class="barra-accion__contenido">
        <p v-if="nota" class="barra-accion__nota">{{ nota }}</p>
        <div class="barra-accion__botones"><slot /></div>
      </div>
    </div>
  </q-page-sticky>
</template>

<script setup lang="ts">
// Barra fija con la acción principal de una pantalla de detalle (DESIGN.md, Layout).
// La página que la use debe llevar la clase `con-barra` para que el contenido no quede debajo.
defineProps<{ nota?: string | undefined }>();
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
</style>
