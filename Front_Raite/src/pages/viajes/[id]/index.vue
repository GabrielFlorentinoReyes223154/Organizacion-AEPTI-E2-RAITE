<template>
  <q-page class="detalle" :class="{ 'con-barra': hayBarra }">
    <div v-if="cargando && !viaje" class="raite-contenedor detalle__rejilla">
      <div class="raite-pila">
        <q-skeleton type="rect" height="240px" class="detalle__esqueleto" />
        <q-skeleton type="rect" height="320px" class="detalle__esqueleto" />
      </div>
      <div class="raite-pila">
        <q-skeleton type="rect" height="140px" class="detalle__esqueleto" />
        <q-skeleton type="rect" height="120px" class="detalle__esqueleto" />
      </div>
    </div>

    <div v-else-if="error" class="raite-contenedor raite-contenedor--angosto">
      <EstadoVacio icono="cloud_off" :titulo="error">
        <template #acciones>
          <q-btn color="primary" unelevated no-caps label="Intentar de nuevo" @click="cargar" />
        </template>
      </EstadoVacio>
    </div>

    <div v-else-if="viaje" class="raite-contenedor detalle__rejilla">
      <!-- Izquierda: horario y ruta, mapa y datos del viaje -->
      <div class="detalle__principal">
        <TarjetaDestacada :etiqueta="diaLargo(viaje.fecha_hora)" :viaje="viaje">
          <template #estado>
            <ChipEstado :estado="viaje.estado" :vencido="viaje.esta_vencido" />
          </template>
          <template #pie>
            <span class="detalle__dato-azul">
              <q-icon
                :name="viaje.sentido === 'HACIA_CAMPUS' ? 'school' : 'home'"
                size="20px"
                aria-hidden="true"
              />
              {{ textoSentido(viaje.sentido) }}
            </span>
            <span class="detalle__dato-azul">
              <q-icon name="event_seat" size="20px" aria-hidden="true" />
              {{ lugares(viaje.lugares_disponibles, viaje.lugares_ofrecidos) }} libres
            </span>
          </template>
        </TarjetaDestacada>

        <section class="raite-tarjeta detalle__mapa-tarjeta" aria-labelledby="det-mapa">
          <h2 id="det-mapa" class="detalle__seccion">Ruta</h2>
          <div class="detalle__mapa">
            <MapaRaite
              :puntos="[viaje.punto_referencia]"
              :seleccionado="viaje.punto_referencia.id"
              :campus="[viaje.campus]"
              :ruta="ruta"
              :etiqueta="`Mapa de ${viaje.punto_referencia.nombre} a ${viaje.campus.nombre}`"
            />
          </div>
        </section>

        <section class="raite-tarjeta" aria-labelledby="det-datos">
          <h2 id="det-datos" class="detalle__seccion">Datos del viaje</h2>
          <dl class="detalle__datos">
            <div>
              <dt>Vehículo</dt>
              <dd>
                {{ viaje.vehiculo.marca }} {{ viaje.vehiculo.modelo }}
                {{ viaje.vehiculo.color.toLowerCase() }}
              </dd>
            </div>
            <div>
              <dt>Grupo</dt>
              <dd>{{ textoPreferencia(viaje.preferencia_compatibilidad) }}</dd>
            </div>
            <div>
              <dt>Lugares</dt>
              <dd>
                {{ viaje.lugares_ofrecidos }} ofrecidos, {{ viaje.lugares_disponibles }} libres
              </dd>
            </div>
            <div>
              <dt>Punto de salida</dt>
              <dd>{{ viaje.punto_referencia.nombre }}</dd>
            </div>
            <div v-if="viaje.notas" class="detalle__ancho">
              <dt>Notas</dt>
              <dd class="detalle__notas">{{ viaje.notas }}</dd>
            </div>
          </dl>
        </section>
      </div>

      <!-- Derecha: personas, estado o contacto, y acciones -->
      <aside class="detalle__lateral">
        <!-- Pasajero: quién maneja -->
        <section
          v-if="!esConductor"
          class="raite-tarjeta detalle__persona"
          aria-labelledby="det-maneja"
        >
          <h2 id="det-maneja" class="detalle__etiqueta">Quién maneja</h2>
          <div class="detalle__persona-fila">
            <AvatarIniciales
              :nombre="viaje.conductor.nombre_completo"
              :foto="viaje.conductor.foto"
              :tam="64"
            />
            <div class="detalle__persona-datos">
              <p class="detalle__persona-nombre">{{ viaje.conductor.nombre_completo }}</p>
              <p class="raite-ayuda">{{ conCampus(viaje.conductor) }}</p>
            </div>
          </div>
          <span class="detalle__calif">
            <q-icon name="star" size="18px" aria-hidden="true" />
            <span class="sr-only">Calificación</span>
            {{ calificacion(viaje.conductor.calificacion) ?? 'Nuevo' }}
          </span>
        </section>

        <!-- Conductor: pasajeros confirmados -->
        <section v-else class="raite-tarjeta raite-pila" aria-labelledby="det-pasajeros">
          <div class="row items-center justify-between no-wrap">
            <h2 id="det-pasajeros" class="detalle__seccion q-mb-none">Tus pasajeros</h2>
            <q-btn
              v-if="viaje.estado === 'PUBLICADO' && !viaje.esta_vencido"
              flat
              no-caps
              color="primary"
              icon-right="chevron_right"
              label="Solicitudes"
              :to="`/viajes/${viaje.id}/solicitudes`"
            />
          </div>
          <p v-if="!viaje.pasajeros_confirmados?.length" class="raite-ayuda">
            Todavía no confirmas a nadie.
          </p>
          <ul v-else class="detalle__lista">
            <li v-for="p in viaje.pasajeros_confirmados" :key="p.id" class="detalle__pasajero">
              <AvatarIniciales :nombre="p.nombre_completo" :foto="p.foto" :tam="44" tono="verde" />
              <div class="detalle__persona-datos">
                <p class="detalle__pasajero-nombre">{{ p.nombre_completo }}</p>
                <p class="raite-dato detalle__telefono">{{ telefono(p.telefono) }}</p>
              </div>
              <q-btn
                v-if="p.telefono"
                outline
                round
                color="primary"
                icon="call"
                :href="`tel:${p.telefono}`"
                :aria-label="`Llamar a ${p.nombre}`"
              />
              <q-btn
                v-if="p.telefono"
                outline
                round
                color="primary"
                icon="chat"
                :href="enlaceWhatsApp(p.telefono)"
                target="_blank"
                :aria-label="`WhatsApp a ${p.nombre}`"
              />
            </li>
          </ul>
        </section>

        <!-- Estado de la solicitud del pasajero -->
        <template v-if="!esConductor">
          <p
            v-if="!solicitudActiva && viaje.estado === 'PUBLICADO'"
            class="aviso-bloque aviso-bloque--simple"
          >
            <q-icon name="lock_outline" size="20px" aria-hidden="true" />
            El teléfono y las placas aparecen cuando {{ viaje.conductor.nombre }} acepte tu
            solicitud.
          </p>
          <div
            v-if="estadoSolicitud === 'RECHAZADA' && !solicitudActiva"
            class="aviso-bloque aviso-bloque--rojo"
            role="status"
          >
            <q-icon name="cancel" size="24px" aria-hidden="true" />
            <p>
              {{ viaje.conductor.nombre }} no pudo llevarte esta vez.
              <router-link to="/buscar">Busca otro raite</router-link>.
            </p>
          </div>
          <div
            v-if="estadoSolicitud === 'PENDIENTE'"
            class="aviso-bloque aviso-bloque--amarillo"
            role="status"
          >
            <q-icon name="hourglass_empty" size="24px" aria-hidden="true" />
            <p>
              <strong>Solicitud pendiente.</strong> Te avisamos cuando
              {{ viaje.conductor.nombre }} responda.
            </p>
          </div>

          <section
            v-if="estadoSolicitud === 'ACEPTADA'"
            class="contacto"
            aria-labelledby="det-contacto"
          >
            <div class="contacto__cabecera">
              <q-icon name="verified_user" size="22px" color="primary" aria-hidden="true" />
              <h2 id="det-contacto" class="contacto__titulo">Contacto confirmado</h2>
            </div>
            <div class="contacto__datos">
              <div>
                <p class="contacto__etiqueta">Teléfono / WhatsApp</p>
                <p class="contacto__valor raite-dato">{{ telefono(viaje.conductor.telefono) }}</p>
              </div>
              <div v-if="viaje.vehiculo.placas">
                <p class="contacto__etiqueta">Placas</p>
                <p class="contacto__valor contacto__valor--placas raite-dato">
                  {{ viaje.vehiculo.placas }}
                </p>
              </div>
            </div>
            <div v-if="viaje.conductor.telefono" class="contacto__botones">
              <q-btn
                color="primary"
                unelevated
                no-caps
                icon="call"
                label="Llamar"
                :href="`tel:${viaje.conductor.telefono}`"
              />
              <q-btn
                outline
                color="primary"
                no-caps
                icon="chat"
                label="WhatsApp"
                class="bg-white"
                :href="enlaceWhatsApp(viaje.conductor.telefono)"
                target="_blank"
              />
            </div>
            <p class="contacto__nota">Escríbele para acordar el punto exacto donde te recoge.</p>
          </section>
        </template>

        <BarraAccion v-if="hayBarra" :nota="notaBarra">
          <!-- Pasajero -->
          <template v-if="!esConductor">
            <q-btn
              v-if="accionPasajero === 'solicitar'"
              color="primary"
              unelevated
              no-caps
              :label="viaje.lugares_disponibles ? 'Solicitar lugar' : 'Sin lugares libres'"
              :disable="!viaje.lugares_disponibles"
              :loading="ocupado === 'solicitar'"
              @click="solicitar"
            />
            <q-btn
              v-else-if="accionPasajero === 'cancelar'"
              color="negative"
              unelevated
              no-caps
              :label="estadoSolicitud === 'ACEPTADA' ? 'Cancelar mi lugar' : 'Cancelar solicitud'"
              :loading="ocupado === 'cancelarSolicitud'"
              @click="cancelarSolicitud"
            />
            <q-btn
              v-else-if="accionPasajero === 'calificar'"
              color="primary"
              unelevated
              no-caps
              label="Calificar a quien manejó"
              :to="`/viajes/${viaje.id}/calificar`"
            />
          </template>

          <!-- Conductor -->
          <template v-else>
            <template v-if="viaje.estado === 'PUBLICADO' && !viaje.esta_vencido">
              <q-btn
                color="primary"
                unelevated
                no-caps
                label="Iniciar viaje"
                :disable="!puedeIniciar"
                :loading="ocupado === 'iniciar'"
                @click="iniciar"
              />
              <q-btn
                outline
                color="primary"
                no-caps
                label="Ver solicitudes"
                :to="`/viajes/${viaje.id}/solicitudes`"
              />
            </template>
            <q-btn
              v-else-if="viaje.estado === 'EN_CURSO'"
              color="primary"
              unelevated
              no-caps
              label="Terminar viaje"
              :loading="ocupado === 'finalizar'"
              @click="finalizar"
            />
            <q-btn
              v-else-if="pendientesCalificar"
              color="primary"
              unelevated
              no-caps
              label="Calificar a tus pasajeros"
              :to="`/viajes/${viaje.id}/calificar`"
            />
          </template>
        </BarraAccion>

        <!-- Acciones secundarias -->
        <div class="detalle__secundarias">
          <template v-if="esConductor && viaje.estado === 'PUBLICADO'">
            <q-btn
              v-if="!viaje.esta_vencido"
              flat
              no-caps
              color="primary"
              icon="edit"
              label="Editar viaje"
              :to="`/publicar?editar=${viaje.id}`"
            />
            <q-btn
              flat
              no-caps
              class="text-rojo-texto"
              icon="block"
              label="Cancelar viaje"
              :loading="ocupado === 'cancelar'"
              @click="cancelarViaje"
            />
          </template>
          <q-btn
            v-if="puedeReportar"
            flat
            no-caps
            color="primary"
            icon="flag"
            label="Reportar un problema"
            :to="`/viajes/${viaje.id}/reportar`"
          />
        </div>
      </aside>
    </div>
  </q-page>
</template>

<script setup lang="ts">
// Detalle del viaje (RF-05, RF-06, RF-08). Computadora: horario, mapa y datos a la izquierda; personas,
// estado y acciones a la derecha. Celular: una columna con la acción en la barra fija.
// El contacto (teléfono y placas) solo aparece con la solicitud aceptada (regla 4, RNF-02).
import { computed, onBeforeUnmount, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { calificaciones, solicitudes, viajes } from '@/api';
import { leerError } from '@/api/errores';
import type { ViajeDetalle } from '@/api/tipos';
import AvatarIniciales from '@/components/AvatarIniciales.vue';
import BarraAccion from '@/components/BarraAccion.vue';
import ChipEstado from '@/components/ChipEstado.vue';
import EstadoVacio from '@/components/EstadoVacio.vue';
import MapaRaite from '@/components/MapaRaite.vue';
import TarjetaDestacada from '@/components/TarjetaDestacada.vue';
import { useSesionStore } from '@/stores/sesion';
import { avisarError, avisarExito, confirmar } from '@/utils/avisar';
import {
  calificacion,
  conCampus,
  diaLargo,
  enlaceWhatsApp,
  hora,
  lugares,
  telefono,
  textoPreferencia,
  textoSentido,
} from '@/utils/formato';

definePage({ meta: { titulo: 'Detalle del viaje', atras: '/' } });

const route = useRoute();
const sesion = useSesionStore();

const viaje = ref<ViajeDetalle | null>(null);
const cargando = ref(true);
const error = ref('');
const ocupado = ref<string | null>(null);
const pendientesCalificar = ref(0);
const ahora = ref(Date.now());
const reloj = setInterval(() => (ahora.value = Date.now()), 30_000);
onBeforeUnmount(() => clearInterval(reloj));

const id = computed(() => String((route.params as { id?: string }).id ?? ''));

async function cargar() {
  cargando.value = true;
  error.value = '';
  try {
    viaje.value = await viajes.detalle(id.value);
    if (viaje.value.estado === 'FINALIZADO') {
      const pendientes = await calificaciones.pendientes();
      pendientesCalificar.value = pendientes.filter((p) => p.viaje.id === viaje.value?.id).length;
    }
  } catch (e) {
    const legible = leerError(e);
    error.value = legible.status === 404 ? 'Este viaje ya no está disponible.' : legible.mensaje;
  } finally {
    cargando.value = false;
  }
}
watch(id, () => void cargar(), { immediate: true });

const esConductor = computed(
  () => !!viaje.value && viaje.value.conductor.id === sesion.usuario?.id,
);
const estadoSolicitud = computed(() => viaje.value?.mi_solicitud?.estado ?? null);
const solicitudActiva = computed(
  () => estadoSolicitud.value === 'PENDIENTE' || estadoSolicitud.value === 'ACEPTADA',
);
const abierto = computed(() => viaje.value?.estado === 'PUBLICADO' && !viaje.value.esta_vencido);
const puedeIniciar = computed(
  () => !!viaje.value && ahora.value >= new Date(viaje.value.inicio_permitido_desde).getTime(),
);

const puedeReportar = computed(() => {
  if (!viaje.value) return false;
  if (esConductor.value) return !!viaje.value.pasajeros_confirmados?.length;
  return estadoSolicitud.value === 'ACEPTADA';
});

const ruta = computed(() => {
  if (!viaje.value) return null;
  const punto: [number, number] = [
    Number(viaje.value.punto_referencia.latitud),
    Number(viaje.value.punto_referencia.longitud),
  ];
  const campus: [number, number] = [
    Number(viaje.value.campus.latitud),
    Number(viaje.value.campus.longitud),
  ];
  return viaje.value.sentido === 'HACIA_CAMPUS'
    ? { desde: punto, hasta: campus }
    : { desde: campus, hasta: punto };
});

const accionPasajero = computed<'solicitar' | 'cancelar' | 'calificar' | null>(() => {
  if (!viaje.value || esConductor.value) return null;
  if (abierto.value) return solicitudActiva.value ? 'cancelar' : 'solicitar';
  if (viaje.value.estado === 'FINALIZADO' && pendientesCalificar.value) return 'calificar';
  return null;
});

const hayBarra = computed(() => {
  if (!viaje.value) return false;
  if (!esConductor.value) return accionPasajero.value !== null;
  return abierto.value || viaje.value.estado === 'EN_CURSO' || pendientesCalificar.value > 0;
});

const notaBarra = computed(() => {
  if (!viaje.value || !esConductor.value || !abierto.value || puedeIniciar.value) return undefined;
  return `Podrás iniciarlo desde las ${hora(viaje.value.inicio_permitido_desde)}.`;
});

async function ejecutar(nombre: string, accion: () => Promise<unknown>, exito: string) {
  ocupado.value = nombre;
  try {
    await accion();
    avisarExito(exito);
  } catch (e) {
    avisarError(e);
  } finally {
    ocupado.value = null;
    await cargar();
  }
}

function solicitar() {
  void ejecutar(
    'solicitar',
    () => solicitudes.pedir(id.value),
    `Listo. Le avisamos a ${viaje.value?.conductor.nombre ?? 'quien maneja'}.`,
  );
}

async function cancelarSolicitud() {
  const aceptada = estadoSolicitud.value === 'ACEPTADA';
  const ok = await confirmar({
    titulo: aceptada ? '¿Cancelar tu lugar?' : '¿Cancelar tu solicitud?',
    mensaje: aceptada
      ? `Le avisaremos a ${viaje.value?.conductor.nombre ?? 'quien maneja'} que ya no vas.`
      : 'Podrás pedir lugar otra vez mientras el viaje siga abierto.',
    confirmar: aceptada ? 'Cancelar mi lugar' : 'Cancelar solicitud',
    regresar: 'No, regresar',
    peligro: true,
  });
  const solicitudId = viaje.value?.mi_solicitud?.id;
  if (!ok || !solicitudId) return;
  void ejecutar(
    'cancelarSolicitud',
    () => solicitudes.cancelar(solicitudId),
    'Cancelamos tu solicitud.',
  );
}

async function cancelarViaje() {
  const confirmados = viaje.value?.pasajeros_confirmados?.length ?? 0;
  const ok = await confirmar({
    titulo: '¿Cancelar este viaje?',
    mensaje: confirmados
      ? `Le avisaremos a ${confirmados === 1 ? 'tu pasajero' : `tus ${confirmados} pasajeros`} y a quien tenga una solicitud pendiente.`
      : 'Le avisaremos a quien tenga una solicitud pendiente.',
    confirmar: 'Cancelar viaje',
    regresar: 'No, regresar',
    peligro: true,
  });
  if (ok) void ejecutar('cancelar', () => viajes.cancelar(id.value), 'Cancelaste el viaje.');
}

function iniciar() {
  void ejecutar(
    'iniciar',
    () => viajes.iniciar(id.value),
    'Buen viaje. Al llegar, toca "Terminar viaje".',
  );
}

function finalizar() {
  void ejecutar(
    'finalizar',
    () => viajes.finalizar(id.value),
    'Viaje terminado. Ya puedes calificar a tus pasajeros.',
  );
}
</script>

<style scoped lang="scss">
// Computadora: dos columnas a todo el ancho (ruta, mapa y datos | personas, estado y acciones).
.detalle__rejilla {
  max-width: none;
  margin: 0;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 24px;
  align-items: start;
  @media (min-width: 1024px) {
    grid-template-columns: minmax(0, 3fr) minmax(340px, 2fr);
  }
}
.detalle__principal,
.detalle__lateral {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
}
.detalle__esqueleto {
  border-radius: 20px;
}
.detalle__seccion {
  margin: 0 0 12px;
  font-size: 1.125rem;
  font-weight: 700;
  line-height: 1.3;
}
.detalle__etiqueta {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--raite-gris);
}
.detalle__dato-azul {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.detalle__mapa-tarjeta {
  padding: 20px;
}
.detalle__mapa {
  height: 240px;
  border-radius: 16px;
  overflow: hidden;
  @media (min-width: 1024px) {
    height: 360px;
  }
}

.detalle__datos {
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px 24px;
  dt {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--raite-gris);
  }
  dd {
    margin: 4px 0 0;
    font-weight: 600;
  }
}
.detalle__ancho {
  grid-column: 1 / -1;
}
.detalle__notas {
  font-weight: 400 !important;
  white-space: pre-line;
}

// --- Personas ---
.detalle__persona {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px;
}
.detalle__persona-fila {
  display: flex;
  align-items: center;
  gap: 14px;
}
.detalle__persona-datos {
  flex-grow: 1;
  min-width: 0;
  p {
    margin: 0;
  }
}
.detalle__persona-nombre {
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.25;
}
.detalle__calif {
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  background: var(--raite-fondo);
  font-weight: 700;
}
.detalle__lista {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.detalle__pasajero {
  display: flex;
  align-items: center;
  gap: 12px;
}
.detalle__pasajero-nombre {
  font-weight: 700;
}
.detalle__telefono {
  color: var(--raite-azul);
  letter-spacing: 0.04em;
}

// --- Avisos de estado ---
.aviso-bloque {
  margin: 0;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: 16px;
  line-height: 1.4;
  p {
    margin: 0;
  }
}
.aviso-bloque--simple {
  padding: 0 4px;
  font-size: 0.875rem;
  color: var(--raite-gris);
}
.aviso-bloque--amarillo {
  background: var(--raite-amarillo-tenue);
}
.aviso-bloque--rojo {
  background: var(--raite-rojo-tenue);
  color: var(--raite-rojo-texto);
  a {
    color: var(--raite-rojo-texto);
    font-weight: 700;
  }
}

// --- Contacto (solo con la solicitud aceptada) ---
.contacto {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 20px;
  border-radius: 20px;
  background: var(--raite-azul-tenue);
}
.contacto__cabecera {
  display: flex;
  align-items: center;
  gap: 8px;
}
.contacto__titulo {
  margin: 0;
  font-size: 1.0625rem;
  font-weight: 700;
  color: var(--raite-azul);
}
.contacto__datos {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  p {
    margin: 0;
  }
}
.contacto__etiqueta {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--raite-gris);
}
.contacto__valor {
  margin-top: 4px !important;
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: var(--raite-azul);
}
.contacto__valor--placas {
  color: var(--raite-negro);
  letter-spacing: 0.08em;
}
.contacto__botones {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}
.contacto__nota {
  margin: 0;
  font-size: 0.875rem;
}

.detalle__secundarias {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  margin-left: -8px;
}
</style>
