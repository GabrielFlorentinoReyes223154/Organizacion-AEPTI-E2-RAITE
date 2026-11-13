<template>
  <q-page class="raite-contenedor inicio">
    <header class="inicio__cabecera">
      <div>
        <p class="inicio__fecha">{{ hoyTexto }}</p>
        <h1 class="raite-titulo q-mb-none">Hola, {{ nombre }}</h1>
      </div>
      <q-btn
        color="primary"
        unelevated
        no-caps
        class="raite-btn-xl inicio__principal-accion"
        :icon="esConductor ? 'add' : 'search'"
        :label="esConductor ? 'Publicar viaje' : 'Buscar raite'"
        :to="esConductor ? '/publicar' : '/buscar'"
      />
    </header>

    <EstadoVacio v-if="error" icono="cloud_off" :titulo="error">
      <template #acciones>
        <q-btn color="primary" unelevated no-caps label="Intentar de nuevo" @click="cargar" />
      </template>
    </EstadoVacio>

    <template v-else>
      <!-- Conductor: cifras de sus viajes próximos. -->
      <ul v-if="esConductor" class="inicio__cifras" aria-label="Resumen de tus viajes">
        <li v-for="c in cifras" :key="c.etiqueta" class="inicio__cifra">
          <span class="inicio__cifra-icono" :class="`inicio__tono--${c.tono}`" aria-hidden="true">
            <q-icon :name="c.icono" size="24px" />
          </span>
          <span class="inicio__cifra-texto">
            <q-skeleton v-if="cargando" type="text" width="48px" height="32px" />
            <span v-else class="inicio__cifra-valor raite-dato">{{ c.valor }}</span>
            <span class="inicio__cifra-etiqueta">{{ c.etiqueta }}</span>
          </span>
        </li>
      </ul>

      <div class="inicio__fila">
        <q-skeleton v-if="cargando" type="rect" class="inicio__esqueleto" />

        <!-- Pasajero: su próxima solicitud aceptada o pendiente. -->
        <TarjetaDestacada
          v-else-if="!esConductor"
          :etiqueta="etiquetaDestacada"
          :viaje="proxima?.viaje ?? null"
        >
          <template v-if="proxima" #estado>
            <ChipEstado :estado="proxima.estado" />
          </template>
          <template v-if="proxima" #pie>
            <span class="inicio__persona">
              <AvatarIniciales
                :nombre="proxima.viaje.conductor.nombre_completo"
                :foto="proxima.viaje.conductor.foto"
                :tam="48"
              />
              <span class="inicio__persona-texto">
                <span class="inicio__persona-nombre">
                  {{ nombreCorto(proxima.viaje.conductor.nombre_completo) }}
                </span>
                <span class="inicio__persona-detalle">
                  <q-icon name="star" size="16px" color="accent" aria-hidden="true" />
                  {{ calificacion(proxima.viaje.conductor.calificacion) ?? 'Nuevo' }} ·
                  {{ proxima.viaje.vehiculo.marca }} {{ proxima.viaje.vehiculo.modelo }}
                  {{ proxima.viaje.vehiculo.color.toLowerCase() }}
                </span>
              </span>
            </span>
          </template>
          <template v-if="proxima" #accion>
            <q-btn
              unelevated
              no-caps
              color="white"
              text-color="primary"
              label="Ver detalle"
              :to="`/viajes/${proxima.viaje.id}`"
            />
          </template>
          <template #vacia>
            <p class="inicio__vacia-titulo">Todavía no tienes un raite próximo</p>
            <p class="inicio__vacia-texto">
              Busca uno que salga cerca de ti y pide lugar. Aquí lo verás en cuanto te acepten.
            </p>
            <q-btn
              unelevated
              no-caps
              color="white"
              text-color="primary"
              label="Buscar raite"
              to="/buscar"
            />
          </template>
        </TarjetaDestacada>

        <!-- Conductor: su próximo viaje. -->
        <TarjetaDestacada v-else :etiqueta="etiquetaDestacada" :viaje="proximoViaje">
          <template v-if="proximoViaje" #estado>
            <ChipEstado :estado="proximoViaje.estado" />
          </template>
          <template v-if="proximoViaje" #pie>
            <span class="inicio__dato-azul">
              <q-icon name="group" size="20px" aria-hidden="true" />
              {{ ocupadosTexto(proximoViaje) }}
            </span>
            <span v-if="proximoViaje.solicitudes_pendientes" class="inicio__dato-azul">
              <q-icon name="hourglass_empty" size="20px" aria-hidden="true" />
              {{ pendientesTexto(proximoViaje.solicitudes_pendientes) }}
            </span>
          </template>
          <template v-if="proximoViaje" #accion>
            <q-btn
              unelevated
              no-caps
              color="white"
              text-color="primary"
              :label="proximoViaje.solicitudes_pendientes ? 'Ver solicitudes' : 'Ver detalle'"
              :to="
                proximoViaje.solicitudes_pendientes
                  ? `/viajes/${proximoViaje.id}/solicitudes`
                  : `/viajes/${proximoViaje.id}`
              "
            />
          </template>
          <template #vacia>
            <p class="inicio__vacia-titulo">No tienes viajes próximos</p>
            <p class="inicio__vacia-texto">
              Publica el recorrido que ya haces y te avisamos cuando alguien pida lugar.
            </p>
            <q-btn
              unelevated
              no-caps
              color="white"
              text-color="primary"
              label="Publicar viaje"
              to="/publicar"
            />
          </template>
        </TarjetaDestacada>

        <section class="inicio__pendientes raite-tarjeta" aria-labelledby="inicio-pendientes">
          <h2 id="inicio-pendientes" class="inicio__seccion">Pendientes</h2>

          <template v-if="cargando">
            <q-skeleton
              v-for="n in 2"
              :key="n"
              type="rect"
              height="64px"
              class="inicio__fila-esqueleto"
            />
          </template>

          <ul v-else-if="hayPendientes" class="inicio__lista">
            <li
              v-for="p in porCalificar.slice(0, 3)"
              :key="`cal-${p.viaje.id}-${p.usuario.id}`"
              class="inicio__pendiente inicio__pendiente--amarillo"
            >
              <span class="inicio__pendiente-icono" aria-hidden="true">
                <q-icon name="star_outline" size="20px" />
              </span>
              <span class="inicio__pendiente-texto">
                <span class="inicio__pendiente-titulo"
                  >Califica a {{ nombreCorto(p.usuario.nombre_completo) }}</span
                >
                <span class="inicio__pendiente-detalle">
                  {{ diaCorto(p.viaje.fecha_hora) }} · {{ p.viaje.punto_referencia }}
                </span>
              </span>
              <q-btn
                unelevated
                no-caps
                color="dark"
                label="Calificar"
                class="inicio__pendiente-boton"
                :to="`/viajes/${p.viaje.id}/calificar`"
              />
            </li>

            <template v-if="esConductor">
              <li v-for="v in conPendientes" :key="`sol-${v.id}`" class="inicio__pendiente">
                <span class="inicio__pendiente-icono" aria-hidden="true">
                  <q-icon name="hourglass_empty" size="20px" />
                </span>
                <span class="inicio__pendiente-texto">
                  <span class="inicio__pendiente-titulo">{{
                    pendientesTexto(v.solicitudes_pendientes)
                  }}</span>
                  <span class="inicio__pendiente-detalle">
                    {{ diaCorto(v.fecha_hora) }}, {{ hora(v.fecha_hora) }} ·
                    {{ v.punto_referencia.nombre }}
                  </span>
                </span>
                <q-btn
                  unelevated
                  no-caps
                  color="primary"
                  label="Responder"
                  class="inicio__pendiente-boton"
                  :to="`/viajes/${v.id}/solicitudes`"
                />
              </li>
            </template>

            <template v-else>
              <li v-for="s in enEspera" :key="`esp-${s.id}`" class="inicio__pendiente">
                <span class="inicio__pendiente-icono" aria-hidden="true">
                  <q-icon name="hourglass_empty" size="20px" />
                </span>
                <span class="inicio__pendiente-texto">
                  <span class="inicio__pendiente-titulo">Esperando respuesta</span>
                  <span class="inicio__pendiente-detalle">
                    {{ diaCorto(s.viaje.fecha_hora) }}, {{ hora(s.viaje.fecha_hora) }} hacia
                    {{ s.viaje.campus.codigo }}
                  </span>
                </span>
                <q-btn
                  flat
                  no-caps
                  color="primary"
                  label="Ver"
                  class="inicio__pendiente-boton"
                  :to="`/viajes/${s.viaje.id}`"
                />
              </li>
            </template>
          </ul>

          <div v-else class="inicio__al-dia">
            <q-icon name="check_circle" size="28px" class="text-verde-texto" aria-hidden="true" />
            <span>Todo al día. No tienes nada pendiente.</span>
          </div>

          <router-link to="/avisos" class="inicio__ver-avisos">
            Ver todos los avisos<template v-if="avisos.noLeidas">
              ({{ avisos.noLeidas }} sin leer)</template
            >
            <q-icon name="chevron_right" size="20px" aria-hidden="true" />
          </router-link>
        </section>
      </div>

      <section aria-labelledby="inicio-accesos">
        <h2 id="inicio-accesos" class="inicio__seccion inicio__seccion--accesos">
          Accesos rápidos
        </h2>
        <ul class="inicio__accesos">
          <li v-for="a in accesos" :key="a.ruta">
            <router-link :to="a.ruta" class="inicio__acceso">
              <span class="inicio__acceso-icono" aria-hidden="true">
                <q-icon :name="a.icono" size="26px" />
              </span>
              {{ a.texto }}
            </router-link>
          </li>
        </ul>
      </section>
    </template>
  </q-page>
</template>

<script setup lang="ts">
// Inicio por papel: el próximo raite (o viaje) destacado, lo pendiente y accesos rápidos.
// Pasajero: sus solicitudes. Conductor: sus viajes con las cifras de arriba.
import { computed, onMounted, ref, watch } from 'vue';
import { calificaciones, solicitudes, viajes } from '@/api';
import { leerError } from '@/api/errores';
import {
  Rol,
  type CalificacionPendiente,
  type MiSolicitud,
  type MiViaje,
  type Viaje,
} from '@/api/tipos';
import AvatarIniciales from '@/components/AvatarIniciales.vue';
import ChipEstado from '@/components/ChipEstado.vue';
import EstadoVacio from '@/components/EstadoVacio.vue';
import TarjetaDestacada from '@/components/TarjetaDestacada.vue';
import { useAvisosStore } from '@/stores/avisos';
import { useSesionStore } from '@/stores/sesion';
import { calificacion, diaCorto, diaLargo, hora, nombreCorto } from '@/utils/formato';

definePage({ meta: { titulo: 'Inicio' } });

const sesion = useSesionStore();
const avisos = useAvisosStore();

const esConductor = computed(() => sesion.papel === 'conductor');
const nombre = computed(() => sesion.usuario?.nombre ?? '');
const hoyTexto = diaLargo(new Date().toISOString());

const misSolicitudes = ref<MiSolicitud[]>([]);
const misViajes = ref<MiViaje[]>([]);
const porCalificar = ref<CalificacionPendiente[]>([]);
const cargando = ref(true);
const error = ref('');

async function cargar() {
  cargando.value = true;
  error.value = '';
  try {
    const pendientes = calificaciones.pendientes().catch(() => [] as CalificacionPendiente[]);
    if (esConductor.value) misViajes.value = (await viajes.mios()).results;
    else misSolicitudes.value = (await solicitudes.mias()).results;
    porCalificar.value = await pendientes;
  } catch (e) {
    error.value = leerError(e).mensaje;
  } finally {
    cargando.value = false;
  }
}
onMounted(() => void cargar());
// Con rol AMBOS, cambiar de papel se queda en /inicio: se recarga con los datos del otro papel.
watch(esConductor, () => void cargar());

const vigente = (v: Viaje) =>
  (v.estado === 'PUBLICADO' && !v.esta_vencido) || v.estado === 'EN_CURSO';
const porFecha = (a: string, b: string) => a.localeCompare(b);

// --- Pasajero ---
const activas = computed(() =>
  misSolicitudes.value
    .filter((s) => (s.estado === 'PENDIENTE' || s.estado === 'ACEPTADA') && vigente(s.viaje))
    .sort((a, b) => porFecha(a.viaje.fecha_hora, b.viaje.fecha_hora)),
);
const proxima = computed(() => activas.value[0] ?? null);
const enEspera = computed(() => activas.value.slice(1).filter((s) => s.estado === 'PENDIENTE'));

// --- Conductor ---
const proximos = computed(() =>
  misViajes.value.filter(vigente).sort((a, b) => porFecha(a.fecha_hora, b.fecha_hora)),
);
const proximoViaje = computed(() => proximos.value[0] ?? null);
const conPendientes = computed(() => proximos.value.filter((v) => v.solicitudes_pendientes > 0));

const cifras = computed(() => {
  const lista = proximos.value;
  const ofrecidos = lista.reduce((t, v) => t + v.lugares_ofrecidos, 0);
  const ocupados = lista.reduce((t, v) => t + v.lugares_ofrecidos - v.lugares_disponibles, 0);
  return [
    {
      etiqueta: 'Solicitudes por responder',
      valor: String(lista.reduce((t, v) => t + v.solicitudes_pendientes, 0)),
      icono: 'hourglass_empty',
      tono: 'amarillo',
    },
    {
      etiqueta: lista.length === 1 ? 'Viaje próximo' : 'Viajes próximos',
      valor: String(lista.length),
      icono: 'event',
      tono: 'azul',
    },
    {
      etiqueta: 'Lugares ocupados',
      valor: `${ocupados}/${ofrecidos}`,
      icono: 'group',
      tono: 'verde',
    },
    {
      etiqueta: 'Tu calificación',
      valor: calificacion(sesion.usuario?.calificacion) ?? 'Nuevo',
      icono: 'star',
      tono: 'azul',
    },
  ];
});

// --- Comunes ---
const etiquetaDestacada = computed(() => {
  const base = esConductor.value ? 'Tu próximo viaje' : 'Tu próximo raite';
  const fecha = esConductor.value
    ? proximoViaje.value?.fecha_hora
    : proxima.value?.viaje.fecha_hora;
  return fecha ? `${base} · ${diaCorto(fecha)}` : base;
});

const hayPendientes = computed(
  () =>
    porCalificar.value.length > 0 ||
    (esConductor.value ? conPendientes.value.length > 0 : enEspera.value.length > 0),
);

function ocupadosTexto(v: Viaje) {
  return `${v.lugares_ofrecidos - v.lugares_disponibles} de ${v.lugares_ofrecidos} lugares ocupados`;
}
function pendientesTexto(n: number) {
  return n === 1 ? '1 solicitud por responder' : `${n} solicitudes por responder`;
}

const accesos = computed(() =>
  esConductor.value
    ? [
        { ruta: '/publicar', texto: 'Publicar viaje', icono: 'add_circle_outline' },
        { ruta: '/mis-viajes', texto: 'Mis viajes', icono: 'directions_car' },
        { ruta: '/historial', texto: 'Historial', icono: 'history' },
        { ruta: '/avisos', texto: 'Avisos', icono: 'notifications_none' },
        { ruta: '/vehiculo', texto: 'Mi vehículo', icono: 'garage' },
        { ruta: '/perfil', texto: 'Perfil', icono: 'person_outline' },
      ]
    : [
        { ruta: '/buscar', texto: 'Buscar raite', icono: 'search' },
        { ruta: '/mis-raites', texto: 'Mis raites', icono: 'receipt_long' },
        { ruta: '/historial', texto: 'Historial', icono: 'history' },
        { ruta: '/avisos', texto: 'Avisos', icono: 'notifications_none' },
        { ruta: '/perfil', texto: 'Con quién viajo', icono: 'verified_user' },
        sesion.usuario?.rol === Rol.PASAJERO
          ? { ruta: '/vehiculo', texto: 'Dar raite', icono: 'directions_car' }
          : { ruta: '/publicar', texto: 'Publicar viaje', icono: 'add_circle_outline' },
      ],
);
</script>

<style scoped lang="scss">
// A todo el ancho, alineado con el menú lateral.
.inicio {
  max-width: none;
  margin: 0;
}
.inicio__cabecera {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}
.inicio__fecha {
  margin: 0 0 2px;
  font-size: 1rem;
  font-weight: 600;
  color: var(--raite-gris);
}
.inicio__principal-accion {
  padding: 0 28px;
}
.inicio__seccion {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.3;
}
.inicio__seccion--accesos {
  margin-bottom: 16px;
}

// --- Cifras (conductor) ---
.inicio__cifras {
  margin: 0 0 24px;
  padding: 0;
  list-style: none;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}
.inicio__cifra {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 20px;
  background: var(--raite-blanco);
  box-shadow: var(--raite-sombra-tarjeta);
}
.inicio__cifra-icono {
  flex: none;
  width: 52px;
  height: 52px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.inicio__tono--amarillo {
  background: var(--raite-amarillo-tenue);
  color: var(--raite-negro);
}
.inicio__tono--azul {
  background: var(--raite-azul-tenue);
  color: var(--raite-azul);
}
.inicio__tono--verde {
  background: var(--raite-verde-tenue);
  color: var(--raite-verde-texto);
}
.inicio__cifra-texto {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.inicio__cifra-valor {
  font-size: 1.875rem;
  font-weight: 700;
  line-height: 1.1;
}
.inicio__cifra-etiqueta {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--raite-gris);
}

// --- Tarjeta destacada + pendientes ---
.inicio__fila {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 24px;
  margin-bottom: 32px;
  @media (min-width: 1024px) {
    grid-template-columns: minmax(0, 3fr) minmax(340px, 2fr);
  }
}
.inicio__esqueleto {
  min-height: 280px;
  border-radius: 24px;
}
.inicio__persona {
  display: flex;
  align-items: center;
  gap: 12px;
}
.inicio__persona-texto {
  display: flex;
  flex-direction: column;
}
.inicio__persona-nombre {
  font-size: 1rem;
  font-weight: 700;
}
.inicio__persona-detalle {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.875rem;
  color: var(--raite-azul-niebla);
}
.inicio__dato-azul {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  font-weight: 600;
}
.inicio__vacia-titulo {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1.25;
}
.inicio__vacia-texto {
  margin: 0;
  max-width: 460px;
  font-size: 1rem;
  line-height: 1.5;
  color: var(--raite-azul-niebla);
}

.inicio__pendientes {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.inicio__fila-esqueleto {
  border-radius: 16px;
}
.inicio__lista {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.inicio__pendiente {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 16px;
  background: var(--raite-fondo);
}
.inicio__pendiente--amarillo {
  background: var(--raite-amarillo-tenue);
  .inicio__pendiente-detalle {
    color: var(--raite-negro);
  }
}
.inicio__pendiente-icono {
  flex: none;
  width: 40px;
  height: 40px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--raite-blanco);
  color: var(--raite-azul);
}
.inicio__pendiente--amarillo .inicio__pendiente-icono {
  color: var(--raite-negro);
}
.inicio__pendiente-texto {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.inicio__pendiente-titulo {
  font-size: 1rem;
  font-weight: 700;
}
.inicio__pendiente-detalle {
  font-size: 0.875rem;
  line-height: 1.35;
  color: var(--raite-gris);
}
.inicio__pendiente-boton {
  flex: none;
  min-height: 40px;
  padding: 0 16px;
  font-size: 0.875rem;
}
.inicio__al-dia {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 16px;
  background: var(--raite-verde-tenue);
  color: var(--raite-verde-texto);
  font-weight: 600;
}
.inicio__ver-avisos {
  margin-top: auto;
  padding-top: 4px;
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-weight: 700;
  text-decoration: none;
  min-height: 40px;
}

// --- Accesos rápidos ---
.inicio__accesos {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
}
.inicio__acceso {
  height: 128px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border-radius: 20px;
  background: var(--raite-blanco);
  box-shadow: var(--raite-sombra-tarjeta);
  color: var(--raite-negro);
  font-size: 1rem;
  font-weight: 700;
  text-decoration: none;
  &:hover {
    background: var(--raite-blanco-hover);
    .inicio__acceso-icono {
      background: var(--raite-azul-tenue-hover);
    }
  }
}
.inicio__acceso-icono {
  width: 56px;
  height: 56px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--raite-azul-tenue);
  color: var(--raite-azul);
}
</style>
