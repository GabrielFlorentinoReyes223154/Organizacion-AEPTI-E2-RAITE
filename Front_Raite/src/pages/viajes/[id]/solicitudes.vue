<template>
  <q-page>
    <div v-if="cargando && !viaje" class="raite-contenedor raite-contenedor--angosto">
      <q-skeleton type="rect" height="140px" class="q-mb-md" style="border-radius: 16px" />
      <q-skeleton
        v-for="n in 2"
        :key="n"
        type="rect"
        height="120px"
        class="q-mb-md"
        style="border-radius: 16px"
      />
    </div>

    <div v-else-if="error" class="raite-contenedor raite-contenedor--angosto">
      <EstadoVacio icono="cloud_off" :titulo="error">
        <template #acciones>
          <q-btn color="primary" unelevated no-caps label="Intentar de nuevo" @click="cargar" />
        </template>
      </EstadoVacio>
    </div>

    <template v-else-if="viaje">
      <!-- Cupo a la vista -->
      <section class="cupo" aria-labelledby="sol-cupo">
        <div class="cupo__contenido">
          <p class="cupo__viaje">
            <span
              >{{ diaCorto(viaje.fecha_hora) }} ·
              <span class="raite-dato">{{ hora(viaje.fecha_hora) }}</span></span
            >
            <PlacaCampus :codigo="viaje.campus.codigo" :nombre="viaje.campus.nombre" clara />
          </p>
          <p class="cupo__punto">{{ viaje.punto_referencia.nombre }}</p>
          <h2 id="sol-cupo" class="cupo__titulo">
            {{ ocupados }} de {{ viaje.lugares_ofrecidos }} lugares ocupados
          </h2>
          <ul class="cupo__asientos">
            <li
              v-for="(asiento, i) in asientos"
              :key="i"
              :class="asiento ? 'cupo__asiento cupo__asiento--ocupado' : 'cupo__asiento'"
            >
              <template v-if="asiento">
                <span class="cupo__iniciales" aria-hidden="true">{{
                  iniciales(asiento.nombre_completo)
                }}</span>
                <span class="cupo__nombre">{{ asiento.nombre }}</span>
              </template>
              <span v-else>Libre</span>
            </li>
          </ul>
        </div>
      </section>

      <div class="raite-contenedor raite-contenedor--angosto raite-pila">
        <h2 class="raite-seccion">Quieren un lugar · {{ pendientes.length }}</h2>

        <EstadoVacio
          v-if="!pendientes.length"
          icono="inbox"
          titulo="No hay solicitudes por responder"
        >
          Te avisamos con la campanita cuando alguien pida lugar.
        </EstadoVacio>

        <ul v-else class="lista">
          <li v-for="s in pendientes" :key="s.id">
            <article
              class="raite-tarjeta solicitud"
              :aria-label="`Solicitud de ${s.pasajero.nombre_completo}`"
            >
              <div class="solicitud__persona">
                <AvatarIniciales :nombre="s.pasajero.nombre_completo" />
                <div class="solicitud__datos">
                  <p class="solicitud__nombre">{{ s.pasajero.nombre_completo }}</p>
                  <p class="raite-ayuda solicitud__resumen">
                    <q-icon name="star" size="14px" aria-hidden="true" />
                    {{ calificacion(s.pasajero.calificacion) ?? 'Nuevo' }} ·
                    {{ s.pasajero.carrera }}
                  </p>
                </div>
              </div>
              <div class="solicitud__acciones">
                <q-btn
                  flat
                  no-caps
                  label="Rechazar"
                  class="text-rojo-texto"
                  :loading="ocupado === `rechazar-${s.id}`"
                  :disable="!!ocupado"
                  @click="rechazar(s)"
                />
                <q-btn
                  color="primary"
                  unelevated
                  no-caps
                  icon="check"
                  label="Aceptar"
                  :disable="!!ocupado || !libres"
                  :loading="ocupado === `aceptar-${s.id}`"
                  @click="aceptar(s)"
                />
              </div>
            </article>
          </li>
        </ul>
        <p v-if="pendientes.length && !libres" class="raite-ayuda">
          Ya no tienes lugares libres. Rechaza las demás o edita el viaje para ofrecer más.
        </p>

        <template v-if="confirmados.length">
          <h2 class="raite-seccion q-mt-md">Confirmados · {{ confirmados.length }}</h2>
          <ul class="lista">
            <li v-for="s in confirmados" :key="s.id" class="raite-tarjeta confirmado">
              <AvatarIniciales :nombre="s.pasajero.nombre_completo" :tam="40" tono="verde" />
              <div class="solicitud__datos">
                <p class="solicitud__nombre">{{ s.pasajero.nombre_completo }}</p>
                <p class="raite-dato confirmado__telefono">{{ telefono(s.pasajero.telefono) }}</p>
              </div>
              <q-btn
                v-if="s.pasajero.telefono"
                outline
                round
                color="primary"
                icon="call"
                :href="`tel:${s.pasajero.telefono}`"
                :aria-label="`Llamar a ${s.pasajero.nombre}`"
              />
            </li>
          </ul>
        </template>

        <template v-if="respondidas.length">
          <h2 class="raite-seccion q-mt-md">Respondidas</h2>
          <ul class="lista">
            <li v-for="s in respondidas" :key="s.id" class="respondida">
              <span>{{ s.pasajero.nombre_completo }}</span>
              <ChipEstado :estado="s.estado" />
            </li>
          </ul>
        </template>

        <p v-if="viaje.estado === 'PUBLICADO'" class="raite-ayuda nota-inicio">
          <q-icon name="schedule" size="18px" aria-hidden="true" />
          Puedes iniciar el viaje desde las {{ hora(viaje.inicio_permitido_desde) }}. Las
          solicitudes que sigan pendientes se rechazan al iniciar.
        </p>
      </div>
    </template>
  </q-page>
</template>

<script setup lang="ts">
// Solicitudes del conductor (RF-06), variante B: el cupo como asientos y la lista para responder.
// Aceptar responde 409 si otro aceptó antes el último lugar (el backend bloquea el viaje).
import { computed, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { comoLista, solicitudes as apiSolicitudes, viajes } from '@/api';
import { leerError } from '@/api/errores';
import type { Solicitud, UsuarioPublico, ViajeDetalle } from '@/api/tipos';
import AvatarIniciales from '@/components/AvatarIniciales.vue';
import ChipEstado from '@/components/ChipEstado.vue';
import EstadoVacio from '@/components/EstadoVacio.vue';
import PlacaCampus from '@/components/PlacaCampus.vue';
import { avisarError, avisarExito, confirmar } from '@/utils/avisar';
import { calificacion, diaCorto, hora, iniciales, telefono } from '@/utils/formato';

definePage({ meta: { titulo: 'Solicitudes', papel: 'conductor', atras: '/mis-viajes' } });

const route = useRoute();
const id = computed(() => String((route.params as { id?: string }).id ?? ''));

const viaje = ref<ViajeDetalle | null>(null);
const lista = ref<Solicitud[]>([]);
const cargando = ref(true);
const error = ref('');
const ocupado = ref<string | null>(null);

async function cargar() {
  cargando.value = true;
  error.value = '';
  try {
    const [detalle, respuesta] = await Promise.all([
      viajes.detalle(id.value),
      apiSolicitudes.delViaje(id.value),
    ]);
    viaje.value = detalle;
    lista.value = comoLista(respuesta);
  } catch (e) {
    error.value = leerError(e).mensaje;
  } finally {
    cargando.value = false;
  }
}
watch(id, () => void cargar(), { immediate: true });

const pendientes = computed(() => lista.value.filter((s) => s.estado === 'PENDIENTE'));
const confirmados = computed(() => lista.value.filter((s) => s.estado === 'ACEPTADA'));
const respondidas = computed(() =>
  lista.value.filter((s) => s.estado === 'RECHAZADA' || s.estado === 'CANCELADA'),
);
const ocupados = computed(() => confirmados.value.length);
const libres = computed(() => Math.max((viaje.value?.lugares_ofrecidos ?? 0) - ocupados.value, 0));

const asientos = computed<(UsuarioPublico | null)[]>(() => {
  const total = viaje.value?.lugares_ofrecidos ?? 0;
  return Array.from({ length: total }, (_, i) => confirmados.value[i]?.pasajero ?? null);
});

async function aceptar(s: Solicitud) {
  ocupado.value = `aceptar-${s.id}`;
  try {
    await apiSolicitudes.aceptar(s.id);
    avisarExito(`Aceptaste a ${s.pasajero.nombre}. Ya puede ver tu teléfono y tus placas.`);
  } catch (e) {
    avisarError(e);
  } finally {
    ocupado.value = null;
    await cargar();
  }
}

async function rechazar(s: Solicitud) {
  const ok = await confirmar({
    titulo: `¿Rechazar a ${s.pasajero.nombre}?`,
    mensaje: 'Le avisaremos que esta vez no puedes llevarle. Esto no se puede deshacer.',
    confirmar: 'Rechazar',
    regresar: 'No, regresar',
    peligro: true,
  });
  if (!ok) return;
  ocupado.value = `rechazar-${s.id}`;
  try {
    await apiSolicitudes.rechazar(s.id);
    avisarExito(`Rechazaste la solicitud de ${s.pasajero.nombre}.`);
  } catch (e) {
    avisarError(e);
  } finally {
    ocupado.value = null;
    await cargar();
  }
}
</script>

<style scoped lang="scss">
.cupo {
  background: var(--raite-azul);
  color: var(--raite-blanco);
}
.cupo__contenido {
  max-width: 720px;
  margin: 0 auto;
  padding: 8px 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  @media (min-width: 600px) {
    padding: 16px 24px 28px;
  }
}
.cupo__viaje {
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: 1.125rem;
  font-weight: 700;
}
.cupo__punto {
  margin: 0;
  font-size: 0.875rem;
  color: var(--raite-azul-niebla);
}
.cupo__titulo {
  margin: 8px 0 4px;
  font-size: 1rem;
  font-weight: 700;
}
.cupo__asientos {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(64px, 1fr));
  gap: 8px;
}
.cupo__asiento {
  height: 72px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  border: 2px dashed var(--raite-azul-niebla);
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--raite-azul-niebla);
}
.cupo__asiento--ocupado {
  border: 0;
  background: var(--raite-amarillo);
  color: var(--raite-negro);
}
.cupo__iniciales {
  font-size: 1.125rem;
  font-weight: 700;
}
.cupo__nombre {
  max-width: 100%;
  padding: 0 4px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.lista {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.solicitud {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-bottom: 8px;
}
.solicitud__persona {
  display: flex;
  align-items: center;
  gap: 12px;
}
.solicitud__datos {
  flex-grow: 1;
  min-width: 0;
  p {
    margin: 0;
  }
}
.solicitud__nombre {
  font-weight: 700;
}
.solicitud__resumen {
  display: flex;
  align-items: center;
  gap: 4px;
}
.solicitud__acciones {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin-left: -8px;
}
.confirmado {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
}
.confirmado__telefono {
  color: var(--raite-azul);
  letter-spacing: 0.04em;
}
.respondida {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 4px 0;
  border-bottom: 1px solid var(--raite-borde-sutil);
  font-weight: 600;
}
.nota-inicio {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  margin-top: 8px;
}
</style>
