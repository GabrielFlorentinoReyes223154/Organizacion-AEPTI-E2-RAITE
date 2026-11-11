<template>
  <q-page class="raite-contenedor raite-contenedor--ancho">
    <div v-if="cargando" class="reportar">
      <q-skeleton type="rect" height="420px" style="border-radius: 20px" />
      <q-skeleton type="rect" height="240px" style="border-radius: 20px" />
    </div>

    <div v-else-if="!personas.length" class="raite-tarjeta reportar__vacio">
      <EstadoVacio icono="flag" titulo="No hay a quién reportar en este viaje">
        Solo puedes reportar a alguien con quien compartiste un raite confirmado.
      </EstadoVacio>
    </div>

    <div v-else class="reportar">
      <q-form class="raite-tarjeta reportar__formulario" novalidate @submit="enviar">
        <fieldset class="reportar__grupo">
          <legend class="raite-etiqueta">¿A quién quieres reportar?</legend>
          <div class="reportar__personas">
            <button
              v-for="p in personas"
              :key="p.id"
              type="button"
              class="reportar__persona"
              :aria-pressed="reportado === p.id"
              @click="reportado = p.id"
            >
              <AvatarIniciales :nombre="p.nombre_completo" :tam="44" />
              <span class="reportar__persona-texto">
                <span class="reportar__persona-nombre">{{ p.nombre_completo }}</span>
                <span class="reportar__persona-detalle">{{ conCampus(p) }}</span>
              </span>
              <span class="reportar__marca" aria-hidden="true">
                <q-icon name="check" size="16px" />
              </span>
            </button>
          </div>
          <p v-if="errores.reportado" class="reportar__error" role="alert">
            {{ errores.reportado }}
          </p>
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
            input-style="min-height: 140px"
            maxlength="1000"
            counter
            hint="Cuéntalo con tus palabras: qué pasó y cuándo."
            :error="!!errores.motivo"
            :error-message="errores.motivo"
          />
        </div>

        <q-banner
          v-if="mensaje"
          class="bg-rojo-tenue text-rojo-texto rounded-borders"
          role="alert"
          >{{ mensaje }}</q-banner
        >

        <div class="reportar__acciones">
          <q-btn
            type="submit"
            color="primary"
            unelevated
            no-caps
            label="Enviar reporte"
            class="raite-btn-xl reportar__enviar"
            :loading="enviando"
          />
        </div>
      </q-form>

      <aside class="reportar__lateral">
        <div class="riesgo" role="note">
          <q-icon name="emergency" size="28px" aria-hidden="true" />
          <p>
            <strong>¿Estás en peligro ahora?</strong> Llama al 911 o pide ayuda a la seguridad de tu
            campus. Este reporte no llega de inmediato.
          </p>
        </div>

        <section class="raite-tarjeta reportar__pasos" aria-labelledby="rep-despues">
          <h2 id="rep-despues" class="reportar__pasos-titulo">Qué pasa después</h2>
          <ol class="reportar__lista">
            <li>
              <span class="reportar__numero" aria-hidden="true">1</span>
              <span>El equipo de Raite revisa cada caso.</span>
            </li>
            <li>
              <span class="reportar__numero" aria-hidden="true">2</span>
              <span>La persona reportada no sabrá quién la reportó.</span>
            </li>
            <li>
              <span class="reportar__numero" aria-hidden="true">3</span>
              <span>Puedes ver el estado de tu reporte en Perfil, en "Mis reportes".</span>
            </li>
          </ol>
        </section>
      </aside>
    </div>
  </q-page>
</template>

<script setup lang="ts">
// Reportar comportamiento inadecuado (RF-12). Lo resuelve el admin de Django.
import { computed, onMounted, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { reportes, viajes } from '@/api';
import { leerError } from '@/api/errores';
import type { UsuarioPublico, ViajeDetalle } from '@/api/tipos';
import AvatarIniciales from '@/components/AvatarIniciales.vue';
import EstadoVacio from '@/components/EstadoVacio.vue';
import { useSesionStore } from '@/stores/sesion';
import { avisarExito } from '@/utils/avisar';
import { conCampus } from '@/utils/formato';

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
// Computadora: el reporte a la izquierda; el aviso de emergencia y qué sigue a la derecha.
.reportar {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 24px;
  align-items: start;
  @media (min-width: 1024px) {
    grid-template-columns: minmax(0, 2fr) minmax(320px, 1fr);
  }
}
.reportar__vacio {
  max-width: 640px;
}
.reportar__formulario {
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.reportar__grupo {
  margin: 0;
  padding: 0;
  border: 0;
  min-width: 0;
}
.reportar__personas {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}
.reportar__persona {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border: 1px solid var(--raite-borde-campo);
  border-radius: 16px;
  background: var(--raite-blanco);
  color: var(--raite-negro);
  font: inherit;
  text-align: left;
  cursor: pointer;
  &:hover:not([aria-pressed='true']) {
    background: var(--raite-blanco-hover);
  }
  &[aria-pressed='true'] {
    border-color: var(--raite-azul);
    background: var(--raite-azul-tenue);
    box-shadow: inset 0 0 0 1px var(--raite-azul);
    .reportar__marca {
      border-color: var(--raite-azul);
      background: var(--raite-azul);
      color: var(--raite-blanco);
    }
  }
}
.reportar__persona-texto {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.reportar__persona-nombre {
  font-weight: 700;
}
.reportar__persona-detalle {
  font-size: 0.875rem;
  color: var(--raite-gris);
}
.reportar__marca {
  flex: none;
  width: 22px;
  height: 22px;
  border: 2px solid var(--raite-borde-campo);
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: transparent;
}
.reportar__error {
  margin: 8px 0 0;
  font-size: 0.875rem;
  color: var(--raite-rojo-texto);
}
.reportar__acciones {
  display: flex;
  justify-content: flex-end;
}
.reportar__enviar {
  min-width: 240px;
}

// --- Columna derecha ---
.reportar__lateral {
  display: flex;
  flex-direction: column;
  gap: 16px;
  @media (min-width: 1024px) {
    position: sticky;
    top: 104px;
  }
}
.riesgo {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 20px;
  border-radius: 20px;
  background: var(--raite-rojo-tenue);
  color: var(--raite-rojo-texto);
  p {
    margin: 0;
    line-height: 1.45;
  }
}
.reportar__pasos {
  padding: 24px;
}
.reportar__pasos-titulo {
  margin: 0 0 16px;
  font-size: 1.125rem;
  font-weight: 700;
}
.reportar__lista {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 14px;
  li {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    line-height: 1.45;
  }
}
.reportar__numero {
  flex: none;
  width: 28px;
  height: 28px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--raite-azul-tenue);
  color: var(--raite-azul);
  font-size: 0.875rem;
  font-weight: 700;
}
</style>
