<template>
  <q-page class="raite-contenedor raite-contenedor--formulario">
    <div v-if="cargando" class="raite-pila">
      <q-skeleton type="rect" height="80px" style="border-radius: 16px" />
      <q-skeleton type="rect" height="160px" style="border-radius: 16px" />
    </div>

    <EstadoVacio
      v-else-if="!personas.length"
      icono="flag"
      titulo="No hay a quién reportar en este viaje"
    >
      Solo puedes reportar a alguien con quien compartiste un raite confirmado.
    </EstadoVacio>

    <q-form v-else class="raite-pila raite-pila--grupos" novalidate @submit="enviar">
      <div class="riesgo" role="note">
        <q-icon name="emergency" size="24px" aria-hidden="true" />
        <p>
          <strong>¿Estás en peligro ahora?</strong> Llama al 911 o pide ayuda a la seguridad de tu
          campus. Este reporte no llega de inmediato.
        </p>
      </div>

      <fieldset class="reportar__grupo">
        <legend class="raite-etiqueta">¿A quién quieres reportar?</legend>
        <q-option-group v-model="reportado" :options="opciones" type="radio" color="primary" />
        <p v-if="errores.reportado" class="reportar__error" role="alert">{{ errores.reportado }}</p>
      </fieldset>

      <div>
        <label for="rep-motivo" class="raite-etiqueta">¿Qué pasó?</label>
        <q-input
          hide-bottom-space
          for="rep-motivo"
          v-model="motivo"
          outlined
          type="textarea"
          autogrow
          maxlength="1000"
          counter
          hint="Cuéntalo con tus palabras: qué pasó y cuándo."
          :error="!!errores.motivo"
          :error-message="errores.motivo"
        />
      </div>

      <p class="raite-ayuda">
        La persona reportada no sabrá quién la reportó. El equipo de Raite revisa cada caso.
      </p>

      <q-banner v-if="mensaje" class="bg-rojo-tenue text-rojo-texto rounded-borders" role="alert">{{
        mensaje
      }}</q-banner>

      <q-btn
        type="submit"
        color="primary"
        unelevated
        no-caps
        label="Enviar reporte"
        :loading="enviando"
        class="full-width"
      />
    </q-form>
  </q-page>
</template>

<script setup lang="ts">
// Reportar comportamiento inadecuado (RF-12). Lo resuelve el admin de Django.
import { computed, onMounted, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { reportes, viajes } from '@/api';
import { leerError } from '@/api/errores';
import type { UsuarioPublico, ViajeDetalle } from '@/api/tipos';
import EstadoVacio from '@/components/EstadoVacio.vue';
import { useSesionStore } from '@/stores/sesion';
import { avisarExito } from '@/utils/avisar';

definePage({ meta: { titulo: 'Reportar un problema', atras: '/historial' } });

const route = useRoute();
const router = useRouter();
const sesion = useSesionStore();
const id = computed(() => String((route.params as { id?: string }).id ?? ''));

const viaje = ref<ViajeDetalle | null>(null);
const cargando = ref(true);
const enviando = ref(false);
const reportado = ref<string | null>(null);
const motivo = ref('');
const mensaje = ref('');
const errores = reactive<Record<string, string>>({});

const personas = computed<UsuarioPublico[]>(() => {
  if (!viaje.value) return [];
  if (viaje.value.conductor.id === sesion.usuario?.id)
    return viaje.value.pasajeros_confirmados ?? [];
  return viaje.value.mi_solicitud?.estado === 'ACEPTADA' || viaje.value.estado === 'FINALIZADO'
    ? [viaje.value.conductor]
    : [];
});
const opciones = computed(() =>
  personas.value.map((p) => ({ label: p.nombre_completo, value: p.id })),
);

onMounted(async () => {
  try {
    viaje.value = await viajes.detalle(id.value);
    if (personas.value.length === 1) reportado.value = personas.value[0]?.id ?? null;
  } catch (e) {
    mensaje.value = leerError(e).mensaje;
  } finally {
    cargando.value = false;
  }
});

async function enviar() {
  for (const clave of Object.keys(errores)) delete errores[clave];
  mensaje.value = '';
  if (!reportado.value) errores.reportado = 'Elige a la persona.';
  if (motivo.value.trim().length < 10)
    errores.motivo = 'Cuéntanos un poco más (al menos 10 caracteres).';
  if (Object.keys(errores).length) return;
  enviando.value = true;
  try {
    await reportes.crear({
      viaje: id.value,
      reportado: reportado.value as string,
      motivo: motivo.value.trim(),
    });
    avisarExito('Recibimos tu reporte. Lo revisará el equipo de Raite.');
    await router.replace(`/viajes/${id.value}`);
  } catch (e) {
    const legible = leerError(e);
    Object.assign(errores, legible.campos);
    mensaje.value = legible.mensaje;
  } finally {
    enviando.value = false;
  }
}
</script>

<style scoped lang="scss">
.riesgo {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 16px;
  border-radius: 16px;
  background: var(--raite-rojo-tenue);
  color: var(--raite-rojo-texto);
  p {
    margin: 0;
    line-height: 1.4;
  }
}
.reportar__grupo {
  margin: 0;
  padding: 0;
  border: 0;
  :deep(.q-radio) {
    min-height: 48px;
  }
}
.reportar__error {
  margin: 8px 0 0;
  font-size: 0.875rem;
  color: var(--raite-rojo-texto);
}
</style>
