<template>
  <q-page class="raite-contenedor raite-contenedor--ancho no-encontrada">
    <section class="raite-tarjeta no-encontrada__tarjeta">
      <span class="no-encontrada__icono" aria-hidden="true">
        <q-icon name="wrong_location" size="44px" />
      </span>
      <p class="no-encontrada__codigo raite-dato">404</p>
      <h2 class="no-encontrada__titulo">Esta página no existe</h2>
      <p class="no-encontrada__texto">
        Puede que el enlace esté mal escrito o que el viaje ya no esté disponible.
      </p>
      <div class="no-encontrada__acciones">
        <q-btn color="primary" unelevated no-caps icon="home" label="Ir al inicio" to="/" />
        <q-btn
          outline
          color="primary"
          no-caps
          icon="history"
          label="Ver historial"
          to="/historial"
        />
      </div>
    </section>
  </q-page>
</template>

<script setup lang="ts">
// Ruta que no existe: una salida clara al inicio, nunca una pantalla en blanco.
definePage({ meta: { titulo: 'No encontrada', atras: '/' } });
</script>

<style scoped lang="scss">
.no-encontrada {
  display: flex;
  justify-content: center;
  align-items: flex-start;
}
.no-encontrada__tarjeta {
  width: 100%;
  max-width: 560px;
  margin-top: 24px;
  padding: 48px 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 8px;
}
.no-encontrada__icono {
  width: 88px;
  height: 88px;
  margin-bottom: 8px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--raite-azul-tenue);
  color: var(--raite-azul);
}
.no-encontrada__codigo {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  color: var(--raite-gris);
}
.no-encontrada__titulo {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
}
.no-encontrada__texto {
  margin: 0;
  max-width: 40ch;
  color: var(--raite-gris);
}
.no-encontrada__acciones {
  margin-top: 16px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
}
</style>
