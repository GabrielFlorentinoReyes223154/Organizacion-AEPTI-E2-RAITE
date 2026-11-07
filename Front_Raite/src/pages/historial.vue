<template>
  <q-page class="raite-contenedor raite-contenedor--angosto">
    <h1 class="raite-titulo gt-sm">Historial</h1>

    <section
      v-if="pendientes.length"
      class="por-calificar raite-pila"
      aria-labelledby="hist-calificar"
    >
      <h2 id="hist-calificar" class="raite-seccion">Te falta calificar</h2>
      <ul class="por-calificar__lista">
        <li v-for="p in pendientesPorViaje" :key="p.viajeId" class="por-calificar__fila">
          <div class="por-calificar__texto">
            <p class="text-weight-bold">{{ p.nombres }}</p>
            <p class="raite-ayuda">{{ p.cuando }} · {{ p.punto }} · {{ p.campus }}</p>
          </div>
          <q-btn
            color="primary"
            unelevated
            no-caps
            label="Calificar"
            :to="`/viajes/${p.viajeId}/calificar`"
          />
        </li>
      </ul>
    </section>

    <q-btn-toggle
      v-if="sesion.esAmbos"
      v-model="filtro"
      class="raite-opciones q-mb-lg"
      no-caps
      unelevated
      toggle-color="primary"
      :options="[
        { label: 'Todos', value: 'todos' },
        { label: 'Como pasajero', value: 'pasajero' },
        { label: 'Como conductor', value: 'conductor' },
      ]"
    />

    <div v-if="cargando && !lista.length" class="raite-pila">
      <q-skeleton v-for="n in 3" :key="n" type="rect" height="180px" style="border-radius: 16px" />
    </div>

    <EstadoVacio v-else-if="error" icono="cloud_off" :titulo="error">
      <template #acciones>
        <q-btn color="primary" unelevated no-caps label="Intentar de nuevo" @click="cargar()" />
      </template>
    </EstadoVacio>

    <EstadoVacio
      v-else-if="!lista.length"
      icono="history"
      titulo="Aquí aparecerán tus viajes terminados"
    >
      Cuando termines o se cancele un raite, lo verás en esta lista.
    </EstadoVacio>

    <ul v-else class="lista">
      <li v-for="v in lista" :key="v.id">
        <TarjetaViaje
          :viaje="v"
          :to="`/viajes/${v.id}`"
          :mostrar-conductor="v.mi_papel === 'pasajero'"
          compacta
        >
          <template #estado><ChipEstado :estado="v.estado" /></template>
          <template #abajo>
            <span v-if="v.mi_papel === 'conductor'" class="text-gris">Manejaste tú</span>
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
// Historial de viajes finalizados y cancelados (RF-11), con lo que falta calificar (RF-10).
import { computed, onMounted, ref, watch } from 'vue';
import { calificaciones, viajes } from '@/api';
import { leerError } from '@/api/errores';
import type { CalificacionPendiente, Papel, ViajeHistorial } from '@/api/tipos';
import ChipEstado from '@/components/ChipEstado.vue';
import EstadoVacio from '@/components/EstadoVacio.vue';
import TarjetaViaje from '@/components/TarjetaViaje.vue';
import { useSesionStore } from '@/stores/sesion';
import { diaCorto, nombreCorto } from '@/utils/formato';

definePage({ meta: { titulo: 'Historial' } });

const sesion = useSesionStore();
const filtro = ref<Papel | 'todos'>('todos');
const lista = ref<ViajeHistorial[]>([]);
const pendientes = ref<CalificacionPendiente[]>([]);
const cargando = ref(true);
const error = ref('');
const pagina = ref(1);
const hayMas = ref(false);

const pendientesPorViaje = computed(() => {
  const grupos = new Map<string, CalificacionPendiente[]>();
  for (const p of pendientes.value) grupos.set(p.viaje.id, [...(grupos.get(p.viaje.id) ?? []), p]);
  return [...grupos.entries()].map(([viajeId, items]) => {
    const primero = items[0] as CalificacionPendiente;
    return {
      viajeId,
      nombres: items.map((i) => nombreCorto(i.usuario.nombre_completo)).join(', '),
      cuando: diaCorto(primero.viaje.fecha_hora),
      punto: primero.viaje.punto_referencia,
      campus: primero.viaje.campus,
    };
  });
});

async function cargar(numero = 1) {
  cargando.value = true;
  error.value = '';
  try {
    const params =
      filtro.value === 'todos' ? { page: numero } : { rol: filtro.value, page: numero };
    const respuesta = await viajes.historial(params);
    lista.value = numero === 1 ? respuesta.results : [...lista.value, ...respuesta.results];
    hayMas.value = !!respuesta.next;
    pagina.value = numero;
  } catch (e) {
    error.value = leerError(e).mensaje;
  } finally {
    cargando.value = false;
  }
}

watch(filtro, () => void cargar());
onMounted(async () => {
  void cargar();
  pendientes.value = await calificaciones.pendientes().catch(() => []);
});
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
.por-calificar {
  margin-bottom: 24px;
  padding: 16px;
  border-radius: 16px;
  background: var(--raite-azul-tenue);
}
.por-calificar__lista {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.por-calificar__fila {
  display: flex;
  align-items: center;
  gap: 12px;
}
.por-calificar__texto {
  flex-grow: 1;
  min-width: 0;
  p {
    margin: 0;
  }
}
</style>
