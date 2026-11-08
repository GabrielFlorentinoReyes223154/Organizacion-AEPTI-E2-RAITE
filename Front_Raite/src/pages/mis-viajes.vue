<template>
  <q-page class="raite-contenedor raite-contenedor--ancho">
    <header class="raite-cabecera">
      <div class="gt-sm">
        <h1 class="raite-titulo">Mis viajes</h1>
        <p class="raite-cabecera__texto">{{ resumen }}</p>
      </div>
      <q-btn
        color="primary"
        unelevated
        no-caps
        icon="add"
        label="Publicar viaje"
        to="/publicar"
        class="raite-btn-xl mis-viajes__accion"
      />
    </header>

    <ul v-if="cargando && !lista.length" class="raite-rejilla-tarjetas">
      <li v-for="n in 3" :key="n">
        <q-skeleton type="rect" height="220px" style="border-radius: 20px" />
      </li>
    </ul>

    <EstadoVacio v-else-if="error" icono="cloud_off" :titulo="error">
      <template #acciones>
        <q-btn color="primary" unelevated no-caps label="Intentar de nuevo" @click="cargar()" />
      </template>
    </EstadoVacio>

    <EstadoVacio
      v-else-if="!lista.length"
      icono="directions_car"
      titulo="No tienes viajes por hacer"
    >
      Publica el trayecto que ya haces y ofrece los lugares que te sobran.
      <template #acciones>
        <q-btn color="primary" unelevated no-caps label="Publicar viaje" to="/publicar" />
      </template>
    </EstadoVacio>

    <ul v-else class="raite-rejilla-tarjetas">
      <li v-for="v in lista" :key="v.id">
        <TarjetaViaje :viaje="v" :to="`/viajes/${v.id}`" :mostrar-conductor="false">
          <template #estado>
            <ChipEstado :estado="v.estado" :vencido="v.esta_vencido" />
          </template>
          <template #abajo>
            <span
              >{{
                lugares(v.lugares_ofrecidos - v.lugares_disponibles, v.lugares_ofrecidos)
              }}
              ocupados</span
            >
          </template>
          <template #pie>
            <router-link
              v-if="v.solicitudes_pendientes"
              :to="`/viajes/${v.id}/solicitudes`"
              class="pendientes"
            >
              <q-icon name="hourglass_empty" size="20px" aria-hidden="true" />
              <span>
                {{ v.solicitudes_pendientes }}
                {{
                  v.solicitudes_pendientes === 1
                    ? 'solicitud por responder'
                    : 'solicitudes por responder'
                }}
              </span>
              <q-icon name="chevron_right" size="20px" aria-hidden="true" class="q-ml-auto" />
            </router-link>
            <p v-else-if="v.esta_vencido" class="vencido">
              Ya pasó la hora y no se inició. Cancélalo para cerrarlo.
            </p>
          </template>
        </TarjetaViaje>
      </li>
    </ul>

    <q-btn
      v-if="hayMas"
      outline
      color="primary"
      no-caps
      label="Ver más"
      class="full-width q-mt-md"
      :loading="cargando"
      @click="cargar(pagina + 1)"
    />
  </q-page>
</template>

<script setup lang="ts">
// Viajes publicados y en curso del conductor, con las solicitudes que esperan respuesta (RF-02, RF-06).
import { computed, onMounted, ref } from 'vue';
import { viajes } from '@/api';
import { leerError } from '@/api/errores';
import type { MiViaje } from '@/api/tipos';
import ChipEstado from '@/components/ChipEstado.vue';
import EstadoVacio from '@/components/EstadoVacio.vue';
import TarjetaViaje from '@/components/TarjetaViaje.vue';
import { lugares } from '@/utils/formato';

definePage({ meta: { titulo: 'Mis viajes', papel: 'conductor' } });

const lista = ref<MiViaje[]>([]);
const cargando = ref(true);
const error = ref('');
const pagina = ref(1);
const hayMas = ref(false);

async function cargar(numero = 1) {
  cargando.value = true;
  error.value = '';
  try {
    const respuesta = await viajes.mios({ page: numero });
    lista.value = (numero === 1 ? respuesta.results : [...lista.value, ...respuesta.results]).sort(
      (a, b) => a.fecha_hora.localeCompare(b.fecha_hora),
    );
    hayMas.value = !!respuesta.next;
    pagina.value = numero;
  } catch (e) {
    error.value = leerError(e).mensaje;
  } finally {
    cargando.value = false;
  }
}
onMounted(() => void cargar());

const resumen = computed(() => {
  if (cargando.value && !lista.value.length) return 'Cargando tus viajes…';
  const n = lista.value.length;
  if (!n) return 'No tienes viajes por hacer.';
  const pendientes = lista.value.reduce((t, v) => t + v.solicitudes_pendientes, 0);
  const viajesTexto = `${n} ${n === 1 ? 'viaje por hacer' : 'viajes por hacer'}`;
  if (!pendientes) return `${viajesTexto}. No tienes solicitudes por responder.`;
  return `${viajesTexto}, ${pendientes} ${pendientes === 1 ? 'solicitud' : 'solicitudes'} por responder.`;
});
</script>

<style scoped lang="scss">
.mis-viajes__accion {
  padding: 0 28px;
}
.pendientes {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 48px;
  padding: 0 16px;
  background: var(--raite-amarillo-tenue);
  color: var(--raite-negro);
  font-weight: 700;
  text-decoration: none;
  &:hover {
    background: var(--raite-amarillo-tenue-hover);
  }
  &:focus-visible {
    outline-offset: -3px;
  }
}
.vencido {
  margin: 0;
  padding: 12px 16px;
  background: var(--raite-gris-tenue);
  font-size: 0.875rem;
}
</style>
