<template>
  <q-layout view="hHh lpR fFf">
    <q-page-container>
      <q-page class="publico">
        <header class="publico__marca">
          <p class="publico__nombre">Raite</p>
          <p class="publico__lema">Raites entre alumnos de la UACJ</p>
        </header>
        <div class="publico__tarjeta">
          <slot />
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
// Marco de entrar, registro y verificación: franja azul con la marca y el formulario en una hoja blanca.
</script>

<style scoped lang="scss">
.publico {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: var(--raite-azul);
  padding-bottom: 32px;
}
.publico__marca {
  width: 100%;
  max-width: 480px;
  padding: 40px 24px 32px;
  color: var(--raite-blanco);
}
.publico__nombre {
  display: inline-block;
  margin: 0;
  font-size: 2.5rem;
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.02em;
  box-shadow: inset 0 -5px 0 var(--raite-amarillo);
}
.publico__lema {
  margin: 12px 0 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--raite-azul-niebla);
}
.publico__tarjeta {
  width: calc(100% - 32px);
  max-width: 480px;
  box-sizing: border-box;
  padding: 24px 16px 32px;
  border-radius: 24px;
  background: var(--raite-blanco);
}
@media (min-width: 600px) {
  .publico__tarjeta {
    padding: 32px;
  }
}
</style>
