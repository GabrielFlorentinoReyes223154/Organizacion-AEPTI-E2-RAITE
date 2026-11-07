<template>
  <q-page class="buscar" :style-fn="altoPagina">
    <h1 class="sr-only gt-sm">Buscar raite</h1>

    <div class="buscar__marco" :class="{ 'buscar__marco--escritorio': escritorio }">
      <!-- Controles y resultados van primero en el documento: con teclado o lector se llega a la lista antes que al mapa. -->
      <section
        class="buscar__panel"
        :class="escritorio ? null : `buscar__panel--${hoja}`"
        :style="escritorio ? undefined : { height: `${altoHoja}px` }"
        aria-labelledby="buscar-titulo-resultados"
      >
        <template v-if="!escritorio">
          <div v-touch-pan.vertical.prevent.mouse="arrastrar" class="buscar__asa">
            <span class="buscar__agarre" aria-hidden="true" />
            <div class="buscar__cabecera">
              <h2 id="buscar-titulo-resultados" class="raite-seccion">{{ tituloResultados }}</h2>
              <q-btn
                flat
                dense
                no-caps
                color="primary"
                class="buscar__ver"
                :icon-right="hoja === 'completa' ? 'expand_more' : 'expand_less'"
                :label="hoja === 'completa' ? 'Ver mapa' : 'Ver lista'"
                :aria-expanded="hoja === 'completa'"
                aria-controls="buscar-lista"
                @click="alternarHoja"
              />
            </div>
          </div>
        </template>

        <template v-else>
          <FormBusqueda v-model="busqueda" />
          <q-separator class="q-my-lg" />
          <h2 id="buscar-titulo-resultados" class="raite-seccion q-mb-md">
            {{ tituloResultados }}
          </h2>
        </template>

        <p v-if="resumenFiltros && !escritorio" class="buscar__resumen">
          <q-btn
            outline
            dense
            no-caps
            color="primary"
            icon="tune"
            :label="resumenFiltros"
            class="buscar__filtros"
            @click="abrirFiltros"
          />
        </p>

        <div id="buscar-lista" class="buscar__lista" aria-live="polite" :aria-busy="cargando">
          <template v-if="!tieneOrigen">
            <EstadoVacio icono="place" titulo="¿De dónde sales?">
              Elige un punto de referencia cerca de ti, como un Oxxo o un súper, y te mostramos los
              raites que pasan por ahí.
              <template #acciones>
                <q-btn
                  v-if="!escritorio"
                  color="primary"
                  unelevated
                  no-caps
                  label="Elegir punto"
                  @click="abrirFiltros"
                />
              </template>
            </EstadoVacio>
          </template>

          <template v-else-if="cargando && !resultados.length">
            <q-skeleton
              v-for="n in 3"
              :key="n"
              type="rect"
              height="168px"
              class="buscar__esqueleto"
            />
          </template>

          <template v-else-if="error">
            <EstadoVacio icono="cloud_off" :titulo="error">
              <template #acciones>
                <q-btn
                  color="primary"
                  unelevated
                  no-caps
                  label="Intentar de nuevo"
                  @click="buscar()"
                />
              </template>
            </EstadoVacio>
          </template>

          <template v-else-if="!resultados.length">
            <EstadoVacio
              icono="search_off"
              :titulo="`No hay raites cerca de ${nombreOrigen} con estos filtros`"
            >
              Prueba con otro horario o más distancia. Los viajes aparecen en cuanto alguien los
              publica.
              <template #acciones>
                <q-btn
                  v-if="siguienteRadio"
                  color="primary"
                  unelevated
                  no-caps
                  :label="`Buscar a ${siguienteRadio} km`"
                  @click="busqueda.radio = siguienteRadio"
                />
                <q-btn
                  v-if="busqueda.hora"
                  outline
                  color="primary"
                  no-caps
                  label="Cualquier hora"
                  @click="busqueda.hora = null"
                />
                <q-btn
                  v-else-if="busqueda.dia"
                  outline
                  color="primary"
                  no-caps
                  label="Cualquier día"
                  @click="busqueda.dia = null"
                />
                <q-btn
                  v-if="busqueda.campus"
                  outline
                  color="primary"
                  no-caps
                  label="Cualquier campus"
                  @click="busqueda.campus = null"
                />
              </template>
            </EstadoVacio>
          </template>

          <template v-else>
            <ul class="buscar__tarjetas">
              <li v-for="v in resultados" :key="v.id">
                <TarjetaViaje :viaje="v" :to="`/viajes/${v.id}`" />
              </li>
            </ul>
            <q-btn
              v-if="hayMas"
              outline
              color="primary"
              no-caps
              label="Ver más raites"
              class="full-width q-mt-md"
              :loading="cargando"
              @click="buscar(pagina + 1)"
            />
          </template>
        </div>
      </section>

      <div class="buscar__mapa">
        <MapaRaite
          :puntos="catalogos.puntos"
          :seleccionado="busqueda.punto"
          :campus="campusEnMapa"
          :centro="busqueda.ubicacion"
          :radio-km="tieneOrigen ? busqueda.radio : null"
          :margen-abajo="escritorio ? 0 : altoHoja"
          elegible
          etiqueta="Mapa de puntos de referencia. También puedes elegir el punto en el buscador."
          @seleccionar="elegirEnMapa"
        />
        <div v-if="!escritorio" class="buscar__flotante">
          <button type="button" class="buscar__origen" @click="abrirFiltros">
            <q-icon name="place" color="primary" size="22px" aria-hidden="true" />
            <span class="buscar__origen-texto">
              <span class="buscar__origen-etiqueta">Sales de</span>
              <span class="buscar__origen-nombre">{{ nombreOrigen || 'Elige un punto' }}</span>
            </span>
          </button>
          <q-btn
            color="primary"
            unelevated
            icon="tune"
            aria-label="Filtros: campus, sentido, día y hora"
            class="buscar__boton-filtros"
            @click="abrirFiltros"
          />
        </div>
      </div>
    </div>

    <q-dialog v-model="editando" position="bottom" class="buscar__dialogo">
      <q-card class="buscar__hoja-filtros">
        <q-card-section class="row items-center no-wrap q-pb-none">
          <h2 class="raite-seccion col">Tu búsqueda</h2>
          <q-btn flat round icon="close" aria-label="Cerrar" v-close-popup />
        </q-card-section>
        <q-card-section class="buscar__hoja-cuerpo">
          <FormBusqueda v-model="borrador" />
        </q-card-section>
        <q-card-actions class="buscar__hoja-acciones">
          <q-btn
            color="primary"
            unelevated
            no-caps
            label="Ver raites"
            class="full-width"
            @click="aplicarFiltros"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
// Búsqueda del pasajero (RF-04, RF-08), variante B: mapa a pantalla completa con la hoja de resultados.
// En escritorio: filtros y lista a la izquierda, mapa a la derecha.
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { useQuasar } from 'quasar';
import { viajes } from '@/api';
import { leerError } from '@/api/errores';
import type { FiltrosBusqueda, Viaje } from '@/api/tipos';
import EstadoVacio from '@/components/EstadoVacio.vue';
import FormBusqueda from '@/components/FormBusqueda.vue';
import type { Busqueda } from '@/components/busqueda';
import MapaRaite from '@/components/MapaRaite.vue';
import TarjetaViaje from '@/components/TarjetaViaje.vue';
import { useCatalogosStore } from '@/stores/catalogos';
import { diaDeClave, fechaHoraLocal, textoSentido } from '@/utils/formato';

definePage({ meta: { titulo: 'Buscar raite', papel: 'pasajero' } });

const CLAVE_GUARDADA = 'raite.busqueda';
const RADIOS = [3, 5, 10, 15];

const $q = useQuasar();
const catalogos = useCatalogosStore();

const escritorio = computed(() => $q.screen.gt.sm);

// --- Estado de la búsqueda (se recuerda en este dispositivo) ---

function leerGuardada(): Partial<Busqueda> {
  try {
    return JSON.parse(localStorage.getItem(CLAVE_GUARDADA) ?? '{}') as Partial<Busqueda>;
  } catch {
    return {};
  }
}

const guardada = leerGuardada();
const busqueda = reactive<Busqueda>({
  punto: guardada.punto ?? null,
  ubicacion: null,
  sentido: guardada.sentido ?? 'HACIA_CAMPUS',
  campus: guardada.campus ?? null,
  dia: null,
  hora: null,
  radio: guardada.radio ?? 3,
});
const borrador = ref<Busqueda>({ ...busqueda });
const editando = ref(false);

watch(
  () => ({
    punto: busqueda.punto,
    sentido: busqueda.sentido,
    campus: busqueda.campus,
    radio: busqueda.radio,
  }),
  (valor) => {
    try {
      localStorage.setItem(CLAVE_GUARDADA, JSON.stringify(valor));
    } catch {
      /* sin almacenamiento */
    }
  },
);

function abrirFiltros() {
  borrador.value = { ...busqueda };
  editando.value = true;
}

function aplicarFiltros() {
  Object.assign(busqueda, borrador.value);
  editando.value = false;
  hoja.value = 'media';
}

function elegirEnMapa(id: number) {
  busqueda.punto = id;
  busqueda.ubicacion = null;
}

const tieneOrigen = computed(() => busqueda.punto !== null || busqueda.ubicacion !== null);
const nombreOrigen = computed(
  () => catalogos.puntoPorId(busqueda.punto)?.nombre ?? (busqueda.ubicacion ? 'tu ubicación' : ''),
);
const campusElegido = computed(() => catalogos.campusPorId(busqueda.campus));
const campusEnMapa = computed(() =>
  campusElegido.value ? [campusElegido.value] : catalogos.campus,
);

const resumenFiltros = computed(() => {
  if (!tieneOrigen.value) return '';
  const partes = [
    textoSentido(busqueda.sentido),
    campusElegido.value?.codigo ?? 'Todos los campus',
  ];
  if (busqueda.dia)
    partes.push(diaDeClave(busqueda.dia) + (busqueda.hora ? ` · ${busqueda.hora}` : ''));
  partes.push(`${busqueda.radio} km`);
  return partes.join(' · ');
});

const siguienteRadio = computed(() => RADIOS.find((r) => r > busqueda.radio) ?? null);

// --- Resultados ---

const resultados = ref<Viaje[]>([]);
const total = ref(0);
const pagina = ref(1);
const hayMas = ref(false);
const cargando = ref(false);
const error = ref('');

const tituloResultados = computed(() => {
  if (!tieneOrigen.value) return 'Buscar raite';
  if (cargando.value && !resultados.value.length) return 'Buscando raites…';
  const destino = campusElegido.value
    ? ` ${busqueda.sentido === 'HACIA_CAMPUS' ? 'hacia' : 'desde'} ${campusElegido.value.codigo}`
    : '';
  return `${total.value} ${total.value === 1 ? 'raite' : 'raites'}${destino}`;
});

function filtros(numero: number): FiltrosBusqueda {
  const f: FiltrosBusqueda = { sentido: busqueda.sentido, radio_km: busqueda.radio, page: numero };
  if (busqueda.punto) f.punto = busqueda.punto;
  else if (busqueda.ubicacion) [f.lat, f.lon] = busqueda.ubicacion;
  if (busqueda.campus) f.campus = busqueda.campus;
  if (busqueda.dia) {
    if (busqueda.hora) {
      const [h, m] = busqueda.hora.split(':').map(Number) as [number, number];
      const desde = Math.max(0, h * 60 + m - 60);
      const hasta = Math.min(23 * 60 + 59, h * 60 + m + 60);
      const hhmm = (min: number) =>
        `${String(Math.floor(min / 60)).padStart(2, '0')}:${String(min % 60).padStart(2, '0')}`;
      f.desde = fechaHoraLocal(busqueda.dia, hhmm(desde));
      f.hasta = fechaHoraLocal(busqueda.dia, hhmm(hasta));
    } else {
      f.desde = fechaHoraLocal(busqueda.dia, '00:00');
      f.hasta = fechaHoraLocal(busqueda.dia, '23:59');
    }
  }
  return f;
}

let ultimaPeticion = 0;
async function buscar(numero = 1) {
  if (!tieneOrigen.value) return;
  const esta = ++ultimaPeticion;
  cargando.value = true;
  error.value = '';
  try {
    const respuesta = await viajes.buscar(filtros(numero));
    if (esta !== ultimaPeticion) return;
    resultados.value =
      numero === 1 ? respuesta.results : [...resultados.value, ...respuesta.results];
    total.value = respuesta.count;
    hayMas.value = !!respuesta.next;
    pagina.value = numero;
  } catch (e) {
    if (esta === ultimaPeticion) error.value = leerError(e).mensaje;
  } finally {
    if (esta === ultimaPeticion) cargando.value = false;
  }
}

let espera: ReturnType<typeof setTimeout> | undefined;
watch(
  () => ({ ...busqueda }),
  () => {
    clearTimeout(espera);
    espera = setTimeout(() => void buscar(), 250);
  },
  { deep: true },
);

onMounted(() => {
  void catalogos.cargar();
  void buscar();
});

// --- Hoja de resultados (celular) ---

type EstadoHoja = 'mini' | 'media' | 'completa';
const hoja = ref<EstadoHoja>('media');
const altoDisponible = ref(600);

function altoPagina(offset: number, alto: number) {
  altoDisponible.value = alto - offset;
  return { height: `${alto - offset}px` };
}

const altoHoja = computed(() => {
  const total = altoDisponible.value;
  if (hoja.value === 'completa') return Math.max(total - 84, 240);
  if (hoja.value === 'mini') return 128;
  return Math.round(total * 0.48);
});

function alternarHoja() {
  hoja.value = hoja.value === 'completa' ? 'media' : 'completa';
}

const ORDEN: EstadoHoja[] = ['mini', 'media', 'completa'];
function arrastrar(evento: { isFinal?: boolean; offset?: { y: number } }) {
  if (!evento.isFinal || !evento.offset) return;
  const i = ORDEN.indexOf(hoja.value);
  if (evento.offset.y < -40) hoja.value = ORDEN[Math.min(i + 1, 2)] ?? 'completa';
  else if (evento.offset.y > 40) hoja.value = ORDEN[Math.max(i - 1, 0)] ?? 'mini';
}
</script>

<style scoped lang="scss">
.buscar {
  position: relative;
  overflow: hidden;
}
.buscar__marco {
  position: relative;
  height: 100%;
}
.buscar__mapa {
  position: absolute;
  inset: 0;
  z-index: 0;
}

// --- Celular: hoja inferior sobre el mapa ---
.buscar__panel {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000; // por encima de los controles de Leaflet
  display: flex;
  flex-direction: column;
  background: var(--raite-blanco);
  border-radius: 24px 24px 0 0;
  box-shadow: var(--raite-sombra-hoja);
  transition: height 240ms var(--raite-ease-out);
}
.buscar__asa {
  flex-shrink: 0;
  padding: 8px 16px 4px;
  touch-action: none;
  cursor: grab;
}
.buscar__agarre {
  display: block;
  width: 40px;
  height: 4px;
  margin: 0 auto 8px;
  border-radius: 999px;
  background: var(--raite-borde-campo);
}
.buscar__cabecera {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.buscar__ver {
  min-height: 48px;
  padding: 0 8px;
}
.buscar__resumen {
  margin: 0;
  padding: 0 16px 8px;
}
.buscar__filtros {
  min-height: 36px;
  max-width: 100%;
  font-size: 0.875rem;
  :deep(.q-btn__content) {
    flex-wrap: nowrap;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
.buscar__lista {
  flex-grow: 1;
  min-height: 0;
  overflow-y: auto;
  overscroll-behavior: contain;
  padding: 4px 16px 16px;
}
.buscar__tarjetas {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.buscar__esqueleto {
  border-radius: 16px;
  margin-bottom: 12px;
}
.buscar__flotante {
  position: absolute;
  top: 12px;
  left: 12px;
  right: 12px;
  z-index: 1000;
  display: flex;
  gap: 8px;
}
.buscar__origen {
  flex-grow: 1;
  min-width: 0;
  height: 56px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 16px;
  border: 1px solid var(--raite-borde-campo);
  border-radius: 12px;
  background: var(--raite-blanco);
  color: var(--raite-negro);
  font: inherit;
  text-align: left;
  box-shadow: var(--raite-sombra-flotante);
  cursor: pointer;
}
.buscar__origen-texto {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.buscar__origen-etiqueta {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--raite-gris);
  line-height: 1.2;
}
.buscar__origen-nombre {
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.buscar__boton-filtros {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  box-shadow: var(--raite-sombra-flotante);
}
// Leaflet pone sus controles arriba a la izquierda; aquí van abajo del buscador flotante.
.buscar__mapa :deep(.leaflet-top) {
  top: 76px;
}

// --- Filtros (hoja inferior en celular) ---
.buscar__hoja-filtros {
  width: 100%;
  max-height: 92vh;
  display: flex;
  flex-direction: column;
}
.buscar__hoja-cuerpo {
  overflow-y: auto;
}
.buscar__hoja-acciones {
  padding: 12px 16px calc(16px + env(safe-area-inset-bottom));
  box-shadow: var(--raite-sombra-barra);
}

// --- Escritorio: lista a la izquierda, mapa a la derecha ---
.buscar__marco--escritorio {
  display: grid;
  grid-template-columns: minmax(0, 5fr) minmax(0, 7fr);
  .buscar__panel {
    position: static;
    height: 100%;
    overflow-y: auto;
    border-radius: 0;
    box-shadow: none;
    border-right: 1px solid var(--raite-borde-sutil);
    background: var(--raite-fondo);
    padding: 32px;
    transition: none;
  }
  .buscar__lista {
    overflow: visible;
    padding: 0;
  }
  .buscar__mapa {
    position: relative;
    inset: auto;
  }
  .buscar__mapa :deep(.leaflet-top) {
    top: 0;
  }
}
</style>
