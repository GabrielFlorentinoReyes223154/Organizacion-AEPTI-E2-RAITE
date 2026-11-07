<template>
  <q-page class="raite-contenedor raite-contenedor--angosto">
    <h1 class="raite-titulo gt-sm">Mis raites</h1>

    <div v-if="cargando && !lista.length" class="raite-pila">
      <q-skeleton v-for="n in 3" :key="n" type="rect" height="180px" style="border-radius: 16px" />
    </div>

    <EstadoVacio v-else-if="error" icono="cloud_off" :titulo="error">
      <template #acciones>
        <q-btn color="primary" unelevated no-caps label="Intentar de nuevo" @click="cargar" />
      </template>
    </EstadoVacio>

    <EstadoVacio
      v-else-if="!activas.length && !anteriores.length"
      icono="search"
      titulo="Aún no pides ningún raite"
    >
      Busca un viaje que salga cerca de ti y pide un lugar.
      <template #acciones>
        <q-btn color="primary" unelevated no-caps label="Buscar raite" to="/buscar" />
      </template>
    </EstadoVacio>

    <template v-else>
      <section v-if="activas.length" class="raite-pila" aria-labelledby="mr-activas">
        <h2 id="mr-activas" class="raite-seccion">Próximos</h2>
        <ul class="lista">
          <li v-for="s in activas" :key="s.id">
            <TarjetaViaje :viaje="s.viaje" :to="`/viajes/${s.viaje.id}`">
              <template #estado><ChipEstado :estado="s.estado" /></template>
            </TarjetaViaje>
          </li>
        </ul>
      </section>
      <EstadoVacio v-else icono="event_available" titulo="No tienes raites próximos">
        <template #acciones>
          <q-btn color="primary" unelevated no-caps label="Buscar raite" to="/buscar" />
        </template>
      </EstadoVacio>

      <section v-if="anteriores.length" class="raite-pila q-mt-xl" aria-labelledby="mr-anteriores">
        <h2 id="mr-anteriores" class="raite-seccion">Respondidas y canceladas</h2>
        <ul class="lista">
          <li v-for="s in anteriores" :key="s.id">
            <TarjetaViaje :viaje="s.viaje" :to="`/viajes/${s.viaje.id}`" compacta>
              <template #estado><ChipEstado :estado="s.estado" /></template>
            </TarjetaViaje>
          </li>
        </ul>
      </section>
    </template>
  </q-page>
</template>

<script setup lang="ts">
// Solicitudes del pasajero y su estado (RF-05). Las de viajes ya terminados están en Historial.
import { computed, onMounted, ref } from 'vue';
import { solicitudes } from '@/api';
import { leerError } from '@/api/errores';
import type { MiSolicitud } from '@/api/tipos';
import ChipEstado from '@/components/ChipEstado.vue';
import EstadoVacio from '@/components/EstadoVacio.vue';
import TarjetaViaje from '@/components/TarjetaViaje.vue';

definePage({ meta: { titulo: 'Mis raites', papel: 'pasajero' } });

const lista = ref<MiSolicitud[]>([]);
const cargando = ref(true);
const error = ref('');

const vigente = (s: MiSolicitud) =>
  (s.viaje.estado === 'PUBLICADO' && !s.viaje.esta_vencido) || s.viaje.estado === 'EN_CURSO';

const activas = computed(() =>
  lista.value
    .filter((s) => (s.estado === 'PENDIENTE' || s.estado === 'ACEPTADA') && vigente(s))
    .sort((a, b) => a.viaje.fecha_hora.localeCompare(b.viaje.fecha_hora)),
);
const anteriores = computed(() =>
  lista.value
    .filter((s) => (s.estado === 'RECHAZADA' || s.estado === 'CANCELADA') && vigente(s))
    .slice(0, 10),
);

async function cargar() {
  cargando.value = true;
  error.value = '';
  try {
    lista.value = (await solicitudes.mias()).results;
  } catch (e) {
    error.value = leerError(e).mensaje;
  } finally {
    cargando.value = false;
  }
}
onMounted(() => void cargar());
</script>

<style scoped lang="scss">
.lista {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
