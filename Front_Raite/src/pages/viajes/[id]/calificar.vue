<template>
  <q-page class="raite-contenedor raite-contenedor--formulario">
    <div v-if="cargando" class="raite-pila">
      <q-skeleton v-for="n in 2" :key="n" type="rect" height="200px" style="border-radius: 16px" />
    </div>

    <EstadoVacio
      v-else-if="!porCalificar.length"
      icono="task_alt"
      titulo="No te falta calificar a nadie en este viaje"
    >
      <template #acciones>
        <q-btn color="primary" unelevated no-caps label="Ir al historial" to="/historial" />
      </template>
    </EstadoVacio>

    <div v-else class="raite-pila raite-pila--grupos">
      <p class="raite-ayuda">
        {{ porCalificar[0]?.viaje.punto_referencia }} · {{ porCalificar[0]?.viaje.campus }} ·
        {{ diaCorto(porCalificar[0]?.viaje.fecha_hora ?? '') }}. Tu calificación ayuda a que la
        comunidad viaje con confianza.
      </p>

      <q-form
        v-for="p in porCalificar"
        :key="p.usuario.id"
        class="raite-tarjeta raite-pila"
        @submit="enviar(p)"
      >
        <div class="persona">
          <AvatarIniciales :nombre="p.usuario.nombre_completo" />
          <div>
            <h2 class="raite-seccion">{{ p.usuario.nombre_completo }}</h2>
            <p class="raite-ayuda">{{ p.usuario.carrera }}</p>
          </div>
        </div>

        <fieldset class="calificar__grupo">
          <legend class="raite-etiqueta">¿Cómo te fue?</legend>
          <q-rating
            :model-value="puntuacion[p.usuario.id] ?? 0"
            @update:model-value="(n: number) => (puntuacion[p.usuario.id] = n)"
            :max="5"
            size="40px"
            color="primary"
            color-selected="primary"
            icon="star_border"
            icon-selected="star"
            :aria-label="`Calificación para ${p.usuario.nombre}, de 1 a 5 estrellas`"
          />
          <p class="raite-ayuda q-mt-xs">{{ textoPuntuacion(puntuacion[p.usuario.id]) }}</p>
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
          />
        </div>

        <q-btn
          type="submit"
          color="primary"
          unelevated
          no-caps
          label="Enviar calificación"
          :disable="!puntuacion[p.usuario.id]"
          :loading="enviando === p.usuario.id"
        />
      </q-form>
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
import { diaCorto } from '@/utils/formato';

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
.persona {
  display: flex;
  align-items: center;
  gap: 12px;
  p {
    margin: 0;
  }
}
.calificar__grupo {
  margin: 0;
  padding: 0;
  border: 0;
}
</style>
