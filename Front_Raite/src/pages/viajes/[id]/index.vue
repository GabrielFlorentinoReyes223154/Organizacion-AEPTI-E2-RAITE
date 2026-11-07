<template>
  <q-page :class="{ 'con-barra': hayBarra }">
    <div v-if="cargando && !viaje" class="raite-contenedor raite-contenedor--angosto">
      <q-skeleton type="rect" height="180px" class="q-mb-md" style="border-radius: 16px" />
      <q-skeleton type="rect" height="96px" class="q-mb-md" style="border-radius: 16px" />
      <q-skeleton type="rect" height="140px" style="border-radius: 16px" />
    </div>

    <div v-else-if="error" class="raite-contenedor raite-contenedor--angosto">
      <EstadoVacio icono="cloud_off" :titulo="error">
        <template #acciones>
          <q-btn color="primary" unelevated no-caps label="Intentar de nuevo" @click="cargar" />
        </template>
      </EstadoVacio>
    </div>

    <template v-else-if="viaje">
      <!-- Letrero: hora y ruta sobre azul -->
      <section class="letrero" aria-label="Horario y ruta">
        <div class="letrero__contenido">
          <div class="letrero__arriba">
            <div>
              <p class="letrero__hora raite-dato">{{ hora(viaje.fecha_hora) }}</p>
              <p class="letrero__dia">{{ diaLargo(viaje.fecha_hora) }}</p>
            </div>
            <ChipEstado :estado="viaje.estado" :vencido="viaje.esta_vencido" />
          </div>
          <RutaViaje
            :punto="viaje.punto_referencia.nombre"
            :campus="viaje.campus"
            :sentido="viaje.sentido"
            sobre-azul
            grande
          >
            {{ textoSentido(viaje.sentido) }} ·
            {{ lugares(viaje.lugares_disponibles, viaje.lugares_ofrecidos) }} libres
          </RutaViaje>
        </div>
      </section>

      <div class="raite-contenedor raite-contenedor--angosto raite-pila">
        <!-- Pasajero: quién maneja -->
        <section v-if="!esConductor" class="raite-tarjeta persona" aria-label="Quién maneja">
          <AvatarIniciales :nombre="viaje.conductor.nombre_completo" />
          <div class="persona__datos">
            <p class="persona__nombre">{{ viaje.conductor.nombre_completo }}</p>
            <p class="raite-ayuda">{{ viaje.conductor.carrera }}</p>
          </div>
          <span class="persona__calif">
            <q-icon name="star" size="18px" aria-hidden="true" />
            <span class="sr-only">Calificación</span>
            {{ calificacion(viaje.conductor.calificacion) ?? 'Nuevo' }}
          </span>
        </section>

        <!-- Conductor: pasajeros confirmados -->
        <section v-else class="raite-tarjeta raite-pila" aria-labelledby="det-pasajeros">
          <div class="row items-center justify-between no-wrap">
            <h2 id="det-pasajeros" class="raite-seccion">Tus pasajeros</h2>
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
          <ul v-else class="lista-personas">
            <li v-for="p in viaje.pasajeros_confirmados" :key="p.id" class="persona persona--fila">
              <AvatarIniciales :nombre="p.nombre_completo" :tam="40" tono="verde" />
              <div class="persona__datos">
                <p class="persona__nombre">{{ p.nombre_completo }}</p>
                <p class="raite-dato persona__telefono">{{ telefono(p.telefono) }}</p>
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

        <dl class="raite-tarjeta datos">
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
          <div v-if="viaje.notas" class="datos__ancho">
            <dt>Notas</dt>
            <dd class="datos__notas">{{ viaje.notas }}</dd>
          </div>
        </dl>

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

          <section v-if="estadoSolicitud === 'ACEPTADA'" class="contacto" aria-label="Contacto">
            <ChipEstado estado="ACEPTADA" class="self-start" />
            <div class="contacto__datos">
              <div>
                <p class="contacto__etiqueta">Teléfono / WhatsApp</p>
                <p class="contacto__valor raite-dato">{{ telefono(viaje.conductor.telefono) }}</p>
              </div>
              <div v-if="viaje.vehiculo.placas" class="text-right">
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

        <section class="raite-tarjeta mapa-tarjeta" aria-labelledby="det-mapa">
          <h2 id="det-mapa" class="raite-seccion q-mb-sm">Ruta</h2>
          <div class="mapa-tarjeta__mapa">
            <MapaRaite
              :puntos="[viaje.punto_referencia]"
              :seleccionado="viaje.punto_referencia.id"
              :campus="[viaje.campus]"
              :ruta="ruta"
              :etiqueta="`Mapa de ${viaje.punto_referencia.nombre} a ${viaje.campus.nombre}`"
            />
          </div>
        </section>

        <!-- Acciones secundarias -->
        <div class="secundarias">
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
      </div>

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
              outline
              color="primary"
              no-caps
              label="Solicitudes"
              :to="`/viajes/${viaje.id}/solicitudes`"
            />
            <q-btn
              color="primary"
              unelevated
              no-caps
              label="Iniciar viaje"
              :disable="!puedeIniciar"
              :loading="ocupado === 'iniciar'"
              @click="iniciar"
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
    </template>
  </q-page>
</template>

<script setup lang="ts">
// Detalle del viaje (RF-05, RF-06, RF-08), variante A: letrero azul arriba y la acción en la barra fija.
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
import RutaViaje from '@/components/RutaViaje.vue';
import { useSesionStore } from '@/stores/sesion';
import { avisarError, avisarExito, confirmar } from '@/utils/avisar';
import {
  calificacion,
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
.letrero {
  background: var(--raite-azul);
  color: var(--raite-blanco);
}
.letrero__contenido {
  max-width: 720px;
  margin: 0 auto;
  padding: 8px 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  @media (min-width: 600px) {
    padding: 16px 24px 32px;
  }
}
.letrero__arriba {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 8px;
}
.letrero__hora {
  margin: 0;
  font-size: 2.75rem;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.02em;
}
.letrero__dia {
  margin: 6px 0 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--raite-azul-niebla);
}

.persona {
  display: flex;
  align-items: center;
  gap: 12px;
}
.persona__datos {
  flex-grow: 1;
  min-width: 0;
  p {
    margin: 0;
  }
}
.persona__nombre {
  font-weight: 700;
}
.persona__telefono {
  color: var(--raite-azul);
  letter-spacing: 0.04em;
}
.persona__calif {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 700;
}
.lista-personas {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.datos {
  margin: 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
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
.datos__ancho {
  grid-column: 1 / -1;
}
.datos__notas {
  font-weight: 400 !important;
  white-space: pre-line;
}

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

.contacto {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border-radius: 16px;
  background: var(--raite-azul-tenue);
}
.contacto__datos {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
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

.mapa-tarjeta__mapa {
  height: 220px;
  border-radius: 12px;
  overflow: hidden;
  @media (min-width: 1024px) {
    height: 280px;
  }
}

.secundarias {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-left: -8px;
}
</style>
