<template>
  <q-layout view="hHh lpR fFf">
    <q-header class="bg-primary text-white">
      <q-toolbar class="barra">
        <q-btn v-if="atras" flat round icon="arrow_back" aria-label="Regresar" @click="regresar" />
        <router-link v-else to="/" class="barra__marca gt-sm" aria-label="Raite, inicio"
          >Raite</router-link
        >

        <h1 class="barra__titulo" :class="{ 'lt-md': !atras }">{{ titulo }}</h1>

        <q-tabs
          v-if="!atras"
          class="barra__pestanas gt-sm text-azul-niebla"
          active-color="white"
          active-bg-color="azul-hondo"
          indicator-color="accent"
          no-caps
          dense
          inline-label
        >
          <q-route-tab
            v-for="p in pestanas"
            :key="p.ruta"
            :to="p.ruta"
            :icon="p.icono"
            :label="p.texto"
          />
        </q-tabs>

        <q-space />
        <CambioRol v-if="sesion.esAmbos" />
        <q-btn
          flat
          round
          icon="notifications"
          :aria-label="etiquetaAvisos"
          to="/avisos"
          class="barra__avisos"
        >
          <q-badge
            v-if="avisos.noLeidas"
            floating
            rounded
            color="accent"
            text-color="dark"
            class="barra__contador"
          >
            {{ avisos.noLeidas > 9 ? '9+' : avisos.noLeidas }}
          </q-badge>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-footer v-if="!atras" class="bg-primary lt-md">
      <nav aria-label="Navegación principal">
        <q-tabs
          class="inferior text-azul-niebla"
          active-color="white"
          active-bg-color="azul-hondo"
          indicator-color="accent"
          switch-indicator
          no-caps
        >
          <q-route-tab
            v-for="p in pestanas"
            :key="p.ruta"
            :to="p.ruta"
            :icon="p.icono"
            :label="p.texto"
          />
        </q-tabs>
      </nav>
    </q-footer>

    <q-page-container>
      <slot />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
// Marco de la app con sesión: encabezado azul, campanita, cambio de rol y navegación (DESIGN.md, Navigation).
import { computed, onBeforeUnmount, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import CambioRol from '@/components/CambioRol.vue';
import { useAvisosStore } from '@/stores/avisos';
import { useSesionStore } from '@/stores/sesion';

const route = useRoute();
const router = useRouter();
const sesion = useSesionStore();
const avisos = useAvisosStore();

const atras = computed(() => route.meta.atras);
const titulo = computed(() => route.meta.titulo ?? 'Raite');

const pestanas = computed(() =>
  sesion.papel === 'conductor'
    ? [
        { ruta: '/mis-viajes', texto: 'Mis viajes', icono: 'directions_car' },
        { ruta: '/publicar', texto: 'Publicar', icono: 'add_circle_outline' },
        { ruta: '/historial', texto: 'Historial', icono: 'history' },
        { ruta: '/perfil', texto: 'Perfil', icono: 'person_outline' },
      ]
    : [
        { ruta: '/buscar', texto: 'Buscar', icono: 'search' },
        { ruta: '/mis-raites', texto: 'Mis raites', icono: 'directions_car' },
        { ruta: '/historial', texto: 'Historial', icono: 'history' },
        { ruta: '/perfil', texto: 'Perfil', icono: 'person_outline' },
      ],
);

const etiquetaAvisos = computed(() =>
  avisos.noLeidas ? `Avisos, ${avisos.noLeidas} sin leer` : 'Avisos, ninguno sin leer',
);

function regresar() {
  const anterior = (window.history.state as { back?: string | null } | null)?.back;
  if (anterior) router.back();
  else void router.push(atras.value ?? sesion.inicio);
}

onMounted(() => avisos.iniciar());
onBeforeUnmount(() => avisos.detener());
</script>

<style scoped lang="scss">
.barra {
  min-height: 56px;
  gap: 4px;
  padding: 0 4px 0 8px;
}
.barra__marca {
  padding: 0 16px 0 8px;
  color: var(--raite-blanco);
  font-size: 1.375rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  text-decoration: none;
  box-shadow: inset 0 -3px 0 var(--raite-amarillo);
  line-height: 40px;
  border-radius: 4px;
}
.barra__titulo {
  margin: 0 0 0 8px;
  min-width: 0;
  font-size: 1.125rem;
  font-weight: 700;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.barra__pestanas {
  align-self: stretch;
  margin-left: 16px;
  :deep(.q-tab) {
    min-height: 56px;
    padding: 0 16px;
  }
}
.barra__contador {
  top: 2px;
  right: 2px;
  font-weight: 700;
  font-size: 14px;
  min-height: 22px;
  min-width: 22px;
  padding: 0 5px;
}
.inferior {
  height: calc(64px + env(safe-area-inset-bottom));
  padding-bottom: env(safe-area-inset-bottom);
  :deep(.q-tabs__content) {
    height: 64px;
  }
  :deep(.q-tab) {
    flex: 1 1 0;
    min-height: 64px;
    padding: 0 4px;
  }
  :deep(.q-tab__indicator) {
    height: 3px;
  }
  :deep(.q-tab__icon) {
    font-size: 24px;
  }
}
</style>
