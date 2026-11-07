<template>
  <q-page class="raite-contenedor raite-contenedor--angosto">
    <div class="row items-center justify-end q-mb-sm">
      <q-btn
        v-if="lista.some((a) => !a.leida)"
        flat
        no-caps
        color="primary"
        icon="done_all"
        label="Marcar todos como leídos"
        :loading="marcando"
        @click="leerTodas"
      />
    </div>

    <div v-if="cargando && !lista.length" class="raite-pila">
      <q-skeleton v-for="n in 4" :key="n" type="rect" height="72px" style="border-radius: 12px" />
    </div>

    <EstadoVacio v-else-if="error" icono="cloud_off" :titulo="error">
      <template #acciones>
        <q-btn color="primary" unelevated no-caps label="Intentar de nuevo" @click="cargar()" />
      </template>
    </EstadoVacio>

    <EstadoVacio v-else-if="!lista.length" icono="notifications_none" titulo="No tienes avisos">
      Aquí te avisamos de solicitudes, confirmaciones, cambios y cancelaciones.
    </EstadoVacio>

    <ul v-else class="avisos">
      <li v-for="a in lista" :key="a.id">
        <button type="button" class="aviso" :class="{ 'aviso--nuevo': !a.leida }" @click="abrir(a)">
          <span class="aviso__icono" :class="`aviso__icono--${tono(a.tipo)}`" aria-hidden="true">
            <q-icon :name="icono(a.tipo)" size="22px" />
          </span>
          <span class="aviso__texto">
            <span class="aviso__tipo">
              {{ a.tipo_display }}
              <span v-if="!a.leida" class="aviso__punto"
                ><span class="sr-only">(sin leer)</span></span
              >
            </span>
            <span class="aviso__mensaje">{{ a.mensaje }}</span>
            <span class="aviso__cuando">{{ haceCuanto(a.created_at) }}</span>
          </span>
        </button>
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
// Avisos dentro de la app (RF-09). La campanita del encabezado cuenta los que no se han leído.
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { avisos as apiAvisos } from '@/api';
import { leerError } from '@/api/errores';
import type { Notificacion, TipoNotificacion } from '@/api/tipos';
import EstadoVacio from '@/components/EstadoVacio.vue';
import { useAvisosStore } from '@/stores/avisos';
import { avisarError } from '@/utils/avisar';
import { haceCuanto } from '@/utils/formato';

definePage({ meta: { titulo: 'Avisos', atras: '/' } });

const router = useRouter();
const contador = useAvisosStore();
const lista = ref<Notificacion[]>([]);
const cargando = ref(true);
const marcando = ref(false);
const error = ref('');
const pagina = ref(1);
const hayMas = ref(false);

const ICONOS: Record<TipoNotificacion, string> = {
  SOLICITUD_NUEVA: 'person_add',
  SOLICITUD_ACEPTADA: 'check_circle',
  SOLICITUD_RECHAZADA: 'cancel',
  SOLICITUD_CANCELADA: 'person_remove',
  VIAJE_MODIFICADO: 'edit_calendar',
  VIAJE_CANCELADO: 'event_busy',
  VIAJE_FINALIZADO: 'star',
};
const icono = (t: TipoNotificacion) => ICONOS[t];
function tono(t: TipoNotificacion) {
  if (t === 'SOLICITUD_ACEPTADA') return 'verde';
  if (t === 'SOLICITUD_RECHAZADA' || t === 'VIAJE_CANCELADO') return 'rojo';
  if (t === 'SOLICITUD_NUEVA') return 'amarillo';
  return 'azul';
}

async function cargar(numero = 1) {
  cargando.value = true;
  error.value = '';
  try {
    const respuesta = await apiAvisos.lista({ page: numero });
    lista.value = numero === 1 ? respuesta.results : [...lista.value, ...respuesta.results];
    hayMas.value = !!respuesta.next;
    pagina.value = numero;
  } catch (e) {
    error.value = leerError(e).mensaje;
  } finally {
    cargando.value = false;
  }
}
onMounted(() => void cargar());

async function abrir(a: Notificacion) {
  if (!a.leida) {
    a.leida = true;
    void apiAvisos
      .leer(a.id)
      .then(() => contador.actualizar())
      .catch(() => (a.leida = false));
  }
  if (!a.viaje) return;
  if (a.tipo === 'SOLICITUD_NUEVA' || a.tipo === 'SOLICITUD_CANCELADA')
    await router.push(`/viajes/${a.viaje}/solicitudes`);
  else if (a.tipo === 'VIAJE_FINALIZADO') await router.push(`/viajes/${a.viaje}/calificar`);
  else await router.push(`/viajes/${a.viaje}`);
}

async function leerTodas() {
  marcando.value = true;
  try {
    await apiAvisos.leerTodas();
    lista.value = lista.value.map((a) => ({ ...a, leida: true }));
    await contador.actualizar();
  } catch (e) {
    avisarError(e);
  } finally {
    marcando.value = false;
  }
}
</script>

<style scoped lang="scss">
.avisos {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.aviso {
  width: 100%;
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 16px;
  border: 1px solid var(--raite-borde-sutil);
  border-radius: 16px;
  background: var(--raite-blanco);
  color: var(--raite-negro);
  font: inherit;
  text-align: left;
  cursor: pointer;
  &:hover {
    background: var(--raite-blanco-hover);
  }
}
.aviso--nuevo {
  background: var(--raite-azul-tenue);
  border-color: transparent;
  &:hover {
    background: var(--raite-azul-tenue-hover);
  }
}
.aviso__icono {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
}
.aviso__icono--azul {
  background: var(--raite-blanco);
  color: var(--raite-azul);
}
.aviso__icono--verde {
  background: var(--raite-verde-tenue);
  color: var(--raite-verde-texto);
}
.aviso__icono--rojo {
  background: var(--raite-rojo-tenue);
  color: var(--raite-rojo-texto);
}
.aviso__icono--amarillo {
  background: var(--raite-amarillo);
  color: var(--raite-negro);
}
.aviso__texto {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.aviso__tipo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
}
.aviso__punto {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: var(--raite-azul);
}
.aviso__mensaje {
  line-height: 1.4;
}
.aviso__cuando {
  font-size: 0.875rem;
  color: var(--raite-gris);
}
</style>
