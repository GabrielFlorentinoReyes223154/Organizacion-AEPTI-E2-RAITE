<template>
  <q-layout view="hHh lpR fFf">
    <q-header class="encabezado">
      <!-- Celular: título grande a la izquierda o, en pantallas secundarias, regresar y título centrado. -->
      <div class="encabezado__movil lt-md">
        <template v-if="atras">
          <q-btn
            flat
            round
            icon="arrow_back"
            aria-label="Regresar"
            class="text-negro"
            @click="regresar"
          />
          <h1 class="encabezado__titulo encabezado__titulo--centro">{{ titulo }}</h1>
          <span class="encabezado__hueco" aria-hidden="true" />
        </template>
        <template v-else>
          <h1 class="encabezado__titulo">{{ titulo }}</h1>
          <q-btn
            round
            unelevated
            icon="notifications_none"
            :aria-label="etiquetaAvisos"
            to="/avisos"
            class="campana campana--tenue"
          >
            <q-badge v-if="avisos.noLeidas" floating rounded class="campana__contador">
              {{ contador }}
            </q-badge>
          </q-btn>
        </template>
      </div>
      <!-- Con rol AMBOS, el cambio de papel va en una segunda fila a todo el ancho. -->
      <div v-if="sesion.esAmbos && !atras" class="encabezado__fila-rol lt-md">
        <CambioRol class="encabezado__rol-movil" />
      </div>

      <!-- Computadora: marca, cambio de papel, campanita y usuario. -->
      <div class="encabezado__escritorio gt-sm">
        <div class="encabezado__fila">
          <router-link to="/" class="encabezado__marca" aria-label="Raite, inicio">
            <img :src="logo" alt="" width="228" height="103" />
          </router-link>
          <q-space />
          <CambioRol v-if="sesion.esAmbos" class="encabezado__rol" />
          <q-btn
            round
            unelevated
            icon="notifications_none"
            :aria-label="etiquetaAvisos"
            to="/avisos"
            class="campana campana--blanca"
          >
            <q-badge v-if="avisos.noLeidas" floating rounded class="campana__contador">
              {{ contador }}
            </q-badge>
          </q-btn>
          <router-link to="/perfil" class="encabezado__usuario" aria-label="Tu perfil">
            <AvatarIniciales :nombre="nombreCompleto" :tam="36" tono="solido" />
            <span>{{ nombreCorto }}</span>
          </router-link>
        </div>
      </div>
    </q-header>

    <!-- Barra inferior (celular): blanca, la pestaña activa en azul con un punto. -->
    <q-footer v-if="!atras" class="pie lt-md">
      <nav aria-label="Navegación principal">
        <q-tabs class="pie__pestanas" active-color="primary" indicator-color="transparent" no-caps>
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
      <div class="cuerpo">
        <!-- Menú lateral (computadora): lo mismo que la barra inferior, más avisos y cerrar sesión. -->
        <aside class="lateral gt-sm">
          <nav aria-label="Navegación principal">
            <p class="lateral__papel">{{ esConductor ? 'Como conductor' : 'Como pasajero' }}</p>
            <q-list class="lateral__lista">
              <q-item
                v-for="p in menu"
                :key="p.ruta"
                :to="p.ruta"
                clickable
                class="lateral__item"
                active-class="lateral__item--activo"
              >
                <q-item-section avatar class="lateral__icono">
                  <q-icon :name="p.icono" size="22px" />
                </q-item-section>
                <q-item-section>{{ p.texto }}</q-item-section>
                <q-item-section v-if="p.ruta === '/avisos' && avisos.noLeidas" side>
                  <span class="lateral__contador">
                    {{ contador }}<span class="sr-only"> sin leer</span>
                  </span>
                </q-item-section>
              </q-item>
            </q-list>
            <q-separator class="q-my-sm" />
            <q-item
              clickable
              class="lateral__item lateral__item--salir"
              :disable="saliendo"
              @click="salir"
            >
              <q-item-section avatar class="lateral__icono">
                <q-icon name="logout" size="22px" />
              </q-item-section>
              <q-item-section>Cerrar sesión</q-item-section>
            </q-item>
          </nav>
        </aside>

        <div class="cuerpo__principal">
          <!-- Pantallas secundarias en computadora: regresar y título arriba del contenido. -->
          <div v-if="atras" class="cuerpo__atras gt-sm">
            <q-btn
              flat
              no-caps
              color="primary"
              icon="arrow_back"
              label="Regresar"
              class="cuerpo__regresar"
              @click="regresar"
            />
            <h1 class="raite-titulo q-mb-none">{{ titulo }}</h1>
          </div>
          <slot />
        </div>
      </div>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
// Marco de la app con sesión (DESIGN.md, Navigation).
// Celular: encabezado blanco y barra inferior blanca. Computadora: barra azul tenue y menú lateral.
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import logo from '@/assets/logo-raite.png';
import AvatarIniciales from '@/components/AvatarIniciales.vue';
import CambioRol from '@/components/CambioRol.vue';
import { useAvisosStore } from '@/stores/avisos';
import { useSesionStore } from '@/stores/sesion';

const route = useRoute();
const router = useRouter();
const sesion = useSesionStore();
const avisos = useAvisosStore();

const atras = computed(() => route.meta.atras);
const titulo = computed(() => route.meta.titulo ?? 'Raite');
const esConductor = computed(() => sesion.papel === 'conductor');

const pestanas = computed(() =>
  esConductor.value
    ? [
        { ruta: '/mis-viajes', texto: 'Mis viajes', icono: 'directions_car' },
        { ruta: '/publicar', texto: 'Publicar', icono: 'add_circle_outline' },
        { ruta: '/historial', texto: 'Historial', icono: 'history' },
        { ruta: '/perfil', texto: 'Perfil', icono: 'person_outline' },
      ]
    : [
        { ruta: '/buscar', texto: 'Buscar raite', icono: 'search' },
        { ruta: '/mis-raites', texto: 'Mis raites', icono: 'receipt_long' },
        { ruta: '/historial', texto: 'Historial', icono: 'history' },
        { ruta: '/perfil', texto: 'Perfil', icono: 'person_outline' },
      ],
);

// En el menú lateral también van los avisos (en celular se abren con la campanita).
const menu = computed(() => {
  const lista = [...pestanas.value];
  lista.splice(lista.length - 1, 0, {
    ruta: '/avisos',
    texto: 'Avisos',
    icono: 'notifications_none',
  });
  return lista;
});

const contador = computed(() => (avisos.noLeidas > 9 ? '9+' : String(avisos.noLeidas)));
const etiquetaAvisos = computed(() =>
  avisos.noLeidas ? `Avisos, ${avisos.noLeidas} sin leer` : 'Avisos, ninguno sin leer',
);

const nombreCompleto = computed(() => sesion.usuario?.nombre_completo ?? '');
const nombreCorto = computed(() => {
  const u = sesion.usuario;
  if (!u) return '';
  const inicial = u.apellidos.trim().charAt(0);
  return inicial ? `${u.nombre} ${inicial}.` : u.nombre;
});

function regresar() {
  const anterior = (window.history.state as { back?: string | null } | null)?.back;
  if (anterior) router.back();
  else void router.push(atras.value ?? sesion.inicio);
}

const saliendo = ref(false);
async function salir() {
  saliendo.value = true;
  await sesion.salir();
  await router.replace('/entrar');
  saliendo.value = false;
}

onMounted(() => avisos.iniciar());
onBeforeUnmount(() => avisos.detener());
</script>

<style scoped lang="scss">
// --- Encabezado ---
.encabezado {
  background: var(--raite-blanco);
  color: var(--raite-negro);
  box-shadow: 0 1px 0 var(--raite-borde-sutil);
}
.encabezado__movil {
  min-height: 64px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px 8px 16px;
}
.encabezado__titulo {
  flex: 1;
  min-width: 0;
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.01em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
// Pantallas secundarias: título centrado en azul, como en la maqueta.
.encabezado__titulo--centro {
  text-align: center;
  font-size: 1.125rem;
  color: var(--raite-azul);
}
.encabezado__hueco {
  width: 48px;
  flex: none;
}
.encabezado__movil :deep(.q-btn .q-icon) {
  font-size: 24px;
}
.encabezado__fila-rol {
  padding: 0 16px 12px;
}
.encabezado__rol-movil {
  display: flex;
  :deep(.cambio-rol__opcion) {
    flex: 1 1 0;
    height: 44px;
    font-size: 1rem;
  }
}

.campana {
  flex: none;
  color: var(--raite-azul);
  :deep(.q-icon) {
    font-size: 24px;
  }
}
.campana--tenue {
  background: var(--raite-azul-tenue);
}
.campana--blanca {
  background: var(--raite-blanco);
}
.campana__contador {
  top: 2px;
  right: 2px;
  min-width: 22px;
  min-height: 22px;
  padding: 0 5px;
  background: var(--raite-amarillo);
  color: var(--raite-negro);
  font-size: 0.75rem;
  font-weight: 700;
  box-shadow: 0 0 0 2px var(--raite-blanco);
}

.encabezado__escritorio {
  background: var(--raite-azul-tenue);
}
.encabezado__fila {
  max-width: 1280px;
  min-height: 72px;
  margin: 0 auto;
  padding: 0 32px;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  gap: 16px;
}
.encabezado__marca {
  display: flex;
  align-items: center;
  border-radius: 8px;
  img {
    display: block;
    width: auto;
    height: 48px;
  }
}
.encabezado__rol {
  background: var(--raite-blanco);
}
.encabezado__usuario {
  height: 48px;
  padding: 0 16px 0 6px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--raite-blanco);
  color: var(--raite-negro);
  font-weight: 700;
  text-decoration: none;
  &:hover {
    background: var(--raite-blanco-hover);
  }
}

// --- Barra inferior ---
.pie {
  background: var(--raite-blanco);
  box-shadow: 0 -1px 0 var(--raite-borde-sutil);
}
.pie__pestanas {
  height: calc(72px + env(safe-area-inset-bottom));
  padding-bottom: env(safe-area-inset-bottom);
  color: var(--raite-gris);
  :deep(.q-tabs__content) {
    height: 72px;
  }
  :deep(.q-tab) {
    flex: 1 1 0;
    min-height: 72px;
    padding: 0 4px 6px;
  }
  :deep(.q-tab__icon) {
    font-size: 24px;
  }
  // La pestaña activa lleva un punto azul debajo del texto.
  :deep(.q-tab--active::after) {
    content: '';
    position: absolute;
    left: 50%;
    bottom: 8px;
    width: 5px;
    height: 5px;
    margin-left: -2.5px;
    border-radius: 999px;
    background: var(--raite-azul);
  }
  :deep(.q-tab--active .q-tab__label) {
    font-weight: 700;
  }
}

// --- Cuerpo (computadora: menú lateral + contenido) ---
@media (min-width: 1024px) {
  .cuerpo {
    max-width: 1280px;
    margin: 0 auto;
    padding-left: 32px;
    box-sizing: border-box;
    display: flex;
    align-items: flex-start;
  }
}
.cuerpo__principal {
  flex: 1;
  min-width: 0;
}
.cuerpo__atras {
  padding: 24px 32px 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}
.cuerpo__regresar {
  margin-left: -12px;
}

.lateral {
  position: sticky;
  top: 104px; // 72 de la barra + 32 de margen
  flex: 0 0 240px;
  margin-top: 32px;
  padding: 16px;
  box-sizing: border-box;
  border-radius: 20px;
  background: var(--raite-blanco);
  box-shadow: var(--raite-sombra-tarjeta);
}
.lateral__papel {
  margin: 0;
  padding: 4px 12px 8px;
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--raite-gris);
}
.lateral__lista {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.lateral__item {
  min-height: 48px;
  padding: 0 12px;
  border-radius: 12px;
  color: var(--raite-negro);
  font-weight: 600;
}
.lateral__icono {
  min-width: 0;
  padding-right: 12px;
}
.lateral__item--activo {
  background: var(--raite-azul-tenue);
  color: var(--raite-azul);
  font-weight: 700;
}
.lateral__item--salir {
  color: var(--raite-rojo-texto);
  font-weight: 700;
}
.lateral__contador {
  min-width: 24px;
  height: 24px;
  padding: 0 6px;
  box-sizing: border-box;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--raite-amarillo-tenue);
  color: var(--raite-negro);
  font-size: 0.875rem;
  font-weight: 700;
}
</style>
