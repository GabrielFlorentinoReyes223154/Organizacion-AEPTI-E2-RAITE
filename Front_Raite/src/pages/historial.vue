<template>
  <q-page class="raite-contenedor raite-contenedor--ancho">
    <header class="raite-cabecera">
      <div class="gt-sm">
        <h1 class="raite-titulo">Historial</h1>
        <p class="raite-cabecera__texto">{{ resumen }}</p>
      </div>
      <div
        v-if="sesion.esAmbos"
        class="historial__filtros"
        role="group"
        aria-label="Qué viajes ver"
      >
        <button
          v-for="f in filtros"
          :key="f.valor"
          type="button"
          class="historial__filtro"
          :aria-pressed="filtro === f.valor"
          @click="filtro = f.valor"
        >
          {{ f.texto }}
        </button>
      </div>
    </header>

    <section v-if="pendientes.length" class="por-calificar" aria-labelledby="hist-calificar">
      <h2 id="hist-calificar" class="por-calificar__titulo">
        <q-icon name="star_outline" size="22px" aria-hidden="true" />
        Te falta calificar
      </h2>
      <ul class="por-calificar__lista">
        <li v-for="p in pendientesPorViaje" :key="p.viajeId" class="por-calificar__fila">
          <div class="por-calificar__texto">
            <p class="text-weight-bold">{{ p.nombres }}</p>
            <p class="por-calificar__detalle">{{ p.cuando }} · {{ p.punto }} · {{ p.campus }}</p>
          </div>
          <q-btn
            color="dark"
            unelevated
            no-caps
            label="Calificar"
            :to="`/viajes/${p.viajeId}/calificar`"
          />
        </li>
      </ul>
    </section>

    <ul v-if="cargando && !lista.length" class="raite-rejilla-tarjetas">
      <li v-for="n in 3" :key="n">
        <q-skeleton type="rect" height="190px" style="border-radius: 20px" />
      </li>
    </ul>

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

    <ul v-else class="raite-rejilla-tarjetas">
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
const total = ref(0);

const resumen = computed(() => {
  if (cargando.value && !lista.value.length) return 'Cargando tu historial…';
  if (!total.value) return 'Todavía no tienes viajes terminados.';
  return `${total.value} ${total.value === 1 ? 'viaje terminado o cancelado' : 'viajes terminados o cancelados'}.`;
});

const filtros: { valor: Papel | 'todos'; texto: string }[] = [
  { valor: 'todos', texto: 'Todos' },
  { valor: 'pasajero', texto: 'Como pasajero' },
  { valor: 'conductor', texto: 'Como conductor' },
];

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
    total.value = respuesta.count;
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
.historial__filtros {
  display: flex;
  gap: 8px;
}
.historial__filtro {
  height: 44px;
  padding: 0 18px;
  border: 0;
  border-radius: 999px;
  background: var(--raite-blanco);
  color: var(--raite-azul);
  font: inherit;
  font-size: 0.9375rem;
  font-weight: 700;
  box-shadow: var(--raite-sombra-tarjeta);
  cursor: pointer;
  &[aria-pressed='true'] {
    background: var(--raite-azul);
    color: var(--raite-blanco);
  }
}

// Lo que falta calificar: amarillo tenue, arriba de la lista.
.por-calificar {
  margin-bottom: 24px;
  padding: 20px 24px;
  border-radius: 20px;
  background: var(--raite-amarillo-tenue);
}
.por-calificar__titulo {
  margin: 0 0 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.125rem;
  font-weight: 700;
}
.por-calificar__lista {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 12px;
}
.por-calificar__fila {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 16px;
  background: var(--raite-blanco);
}
.por-calificar__texto {
  flex-grow: 1;
  min-width: 0;
  p {
    margin: 0;
  }
}
.por-calificar__detalle {
  font-size: 0.875rem;
  color: var(--raite-gris);
}
</style>
