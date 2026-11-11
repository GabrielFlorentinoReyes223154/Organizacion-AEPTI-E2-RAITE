<template>
  <q-page class="raite-contenedor raite-contenedor--ancho">
    <div v-if="cargando" class="calificar">
      <q-skeleton type="rect" height="260px" style="border-radius: 20px" />
      <q-skeleton type="rect" height="360px" style="border-radius: 20px" />
    </div>

    <div v-else-if="!porCalificar.length" class="raite-tarjeta calificar__vacio">
      <EstadoVacio icono="task_alt" titulo="No te falta calificar a nadie en este viaje">
        <template #acciones>
          <q-btn color="primary" unelevated no-caps label="Ir al historial" to="/historial" />
        </template>
      </EstadoVacio>
    </div>

    <div v-else class="calificar">
      <!-- Izquierda: de qué viaje se trata -->
      <aside class="raite-tarjeta calificar__resumen" aria-labelledby="calif-viaje">
        <span class="calificar__icono" aria-hidden="true">
          <q-icon name="star" size="32px" />
        </span>
        <h2 id="calif-viaje" class="calificar__titulo">¿Cómo te fue en tu raite?</h2>
        <dl v-if="viaje" class="calificar__datos">
          <div>
            <dt>Cuándo</dt>
            <dd>{{ diaLargo(viaje.fecha_hora) }}, {{ hora(viaje.fecha_hora) }}</dd>
          </div>
          <div>
            <dt>Desde</dt>
            <dd>{{ viaje.punto_referencia }}</dd>
          </div>
          <div>
            <dt>Campus</dt>
            <dd>{{ viaje.campus }}</dd>
          </div>
        </dl>
        <p class="calificar__nota">
          Tu calificación ayuda a que la comunidad viaje con confianza. Califica con honestidad: así
          cada quien sabe con quién comparte el camino.
        </p>
      </aside>

      <!-- Derecha: una tarjeta por persona -->
      <ul class="calificar__personas">
        <li v-for="p in porCalificar" :key="p.usuario.id">
          <q-form class="raite-tarjeta calificar__persona" @submit="enviar(p)">
            <div class="calificar__quien">
              <AvatarIniciales :nombre="p.usuario.nombre_completo" :tam="56" />
              <div>
                <h3 class="calificar__nombre">{{ p.usuario.nombre_completo }}</h3>
                <p class="raite-ayuda">{{ conCampus(p.usuario) }}</p>
              </div>
            </div>

            <fieldset class="calificar__grupo">
              <legend class="raite-etiqueta">¿Cómo te fue?</legend>
              <q-rating
                :model-value="puntuacion[p.usuario.id] ?? 0"
                @update:model-value="(n: number) => (puntuacion[p.usuario.id] = n)"
                :max="5"
                size="44px"
                color="primary"
                color-selected="primary"
                icon="star_border"
                icon-selected="star"
                :aria-label="`Calificación para ${p.usuario.nombre}, de 1 a 5 estrellas`"
              />
              <p class="calificar__texto-nota">{{ textoPuntuacion(puntuacion[p.usuario.id]) }}</p>
            </fieldset>

            <div>
              <label :for="`calif-${p.usuario.id}`" class="raite-etiqueta"
                >Comentario <span class="text-gris text-weight-regular">(opcional)</span></label
              >
              <q-input
                :for="`calif-${p.usuario.id}`"
                v-model="comentario[p.usuario.id]"
                outlined
                type="textarea"
                autogrow
                maxlength="500"
                counter
                placeholder="Ej. Muy puntual y buena plática."
              />
            </div>

            <q-btn
              type="submit"
              color="primary"
              unelevated
              no-caps
              label="Enviar calificación"
              class="full-width"
              :disable="!puntuacion[p.usuario.id]"
              :loading="enviando === p.usuario.id"
            />
          </q-form>
        </li>
      </ul>
    </div>
  </q-page>
</template>

<script setup lang="ts">
// Calificación mutua al terminar el viaje (RF-10): de 1 a 5 estrellas y un comentario opcional.
import { computed, onMounted, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { calificaciones } from '@/api';
import type { CalificacionPendiente } from '@/api/tipos';
import AvatarIniciales from '@/components/AvatarIniciales.vue';
import EstadoVacio from '@/components/EstadoVacio.vue';
import { avisarError, avisarExito } from '@/utils/avisar';
import { conCampus, diaLargo, hora } from '@/utils/formato';

definePage({ meta: { titulo: 'Calificar', atras: '/historial' } });

const route = useRoute();
const router = useRouter();
const id = computed(() => String((route.params as { id?: string }).id ?? ''));

const pendientes = ref<CalificacionPendiente[]>([]);
const cargando = ref(true);
const enviando = ref<string | null>(null);
const puntuacion = reactive<Record<string, number>>({});
const comentario = reactive<Record<string, string>>({});

const porCalificar = computed(() => pendientes.value.filter((p) => p.viaje.id === id.value));
const viaje = computed(() => porCalificar.value[0]?.viaje ?? null);

const TEXTOS = ['', 'Muy mal', 'Mal', 'Regular', 'Bien', 'Excelente'];
function textoPuntuacion(n: number | undefined) {
  return n ? TEXTOS[n] : 'Toca las estrellas';
}

async function cargar() {
  pendientes.value = await calificaciones.pendientes().catch(() => []);
  cargando.value = false;
}
onMounted(() => void cargar());

async function enviar(p: CalificacionPendiente) {
  const nota = puntuacion[p.usuario.id];
  if (!nota) return;
  enviando.value = p.usuario.id;
  try {
    await calificaciones.calificar(id.value, {
      calificado: p.usuario.id,
      puntuacion: nota,
      comentario: (comentario[p.usuario.id] ?? '').trim(),
    });
    avisarExito(`Gracias. Calificaste a ${p.usuario.nombre}.`);
    pendientes.value = pendientes.value.filter(
      (x) => !(x.viaje.id === p.viaje.id && x.usuario.id === p.usuario.id),
    );
    if (!porCalificar.value.length) await router.replace('/historial');
  } catch (e) {
    avisarError(e);
  } finally {
    enviando.value = null;
  }
}
</script>

<style scoped lang="scss">
// Computadora: el viaje a la izquierda (fijo) y las personas por calificar a la derecha.
.calificar {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 24px;
  align-items: start;
  @media (min-width: 1024px) {
    grid-template-columns: minmax(300px, 1fr) minmax(0, 2.4fr);
  }
}
.calificar__vacio {
  max-width: 640px;
}
.calificar__resumen {
  padding: 28px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  @media (min-width: 1024px) {
    position: sticky;
    top: 104px;
  }
}
.calificar__icono {
  width: 64px;
  height: 64px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--raite-azul-tenue);
  color: var(--raite-azul);
}
.calificar__titulo {
  margin: 0;
  font-size: 1.375rem;
  font-weight: 700;
}
.calificar__datos {
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
  dt {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--raite-gris);
  }
  dd {
    margin: 2px 0 0;
    font-weight: 700;
  }
}
.calificar__nota {
  margin: 0;
  padding-top: 16px;
  border-top: 1px solid var(--raite-gris-tenue);
  font-size: 0.9375rem;
  line-height: 1.5;
  color: var(--raite-gris);
}

.calificar__personas {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}
.calificar__persona {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.calificar__quien {
  display: flex;
  align-items: center;
  gap: 14px;
  p {
    margin: 0;
  }
}
.calificar__nombre {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
}
.calificar__grupo {
  margin: 0;
  padding: 0;
  border: 0;
}
.calificar__texto-nota {
  margin: 4px 0 0;
  font-weight: 700;
  color: var(--raite-azul);
}
</style>
