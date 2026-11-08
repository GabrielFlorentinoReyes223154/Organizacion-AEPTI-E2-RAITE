<template>
  <q-page class="raite-contenedor raite-contenedor--ancho">
    <div class="avisos-pagina">
      <header class="raite-cabecera">
        <div class="gt-sm">
          <h1 class="raite-titulo">Avisos</h1>
          <p class="raite-cabecera__texto">
            {{ sinLeer ? `${sinLeer} sin leer` : 'Estás al día.' }}
          </p>
        </div>
        <q-btn
          v-if="lista.some((a) => !a.leida)"
          outline
          color="primary"
          no-caps
          icon="done_all"
          label="Marcar todo como leído"
          :loading="marcando"
          @click="leerTodas"
        />
      </header>

      <div class="avisos-pagina__filtros" role="group" aria-label="Qué avisos ver">
        <button
          type="button"
          class="avisos-pagina__filtro"
          :aria-pressed="filtro === 'todos'"
          @click="filtro = 'todos'"
        >
          Todos
        </button>
        <button
          type="button"
          class="avisos-pagina__filtro"
          :aria-pressed="filtro === 'sin-leer'"
          @click="filtro = 'sin-leer'"
        >
          Sin leer
        </button>
      </div>

      <div v-if="cargando && !lista.length" class="raite-pila">
        <q-skeleton v-for="n in 4" :key="n" type="rect" height="84px" style="border-radius: 16px" />
      </div>

      <EstadoVacio v-else-if="error" icono="cloud_off" :titulo="error">
        <template #acciones>
          <q-btn color="primary" unelevated no-caps label="Intentar de nuevo" @click="cargar()" />
        </template>
      </EstadoVacio>

      <EstadoVacio
        v-else-if="!lista.length"
        icono="notifications_none"
        :titulo="filtro === 'sin-leer' ? 'No tienes avisos sin leer' : 'No tienes avisos'"
      >
        Aquí te avisamos de solicitudes, confirmaciones, cambios y cancelaciones.
      </EstadoVacio>

      <template v-else>
        <section
          v-for="g in grupos"
          :key="g.clave"
          class="avisos-pagina__grupo"
          :aria-labelledby="`avisos-${g.clave}`"
        >
          <h2 :id="`avisos-${g.clave}`" class="avisos-pagina__dia">{{ g.titulo }}</h2>
          <ul class="avisos">
            <li v-for="a in g.items" :key="a.id">
              <button
                type="button"
                class="aviso"
                :class="{ 'aviso--nuevo': !a.leida }"
                @click="abrir(a)"
              >
                <span
                  class="aviso__icono"
                  :class="`aviso__icono--${tono(a.tipo)}`"
                  aria-hidden="true"
                >
                  <q-icon :name="icono(a.tipo)" size="22px" />
                </span>
                <span class="aviso__texto">
                  <span class="aviso__tipo">
                    {{ a.tipo_display }}
                    <span v-if="!a.leida" class="aviso__nuevo">Nuevo</span>
                  </span>
                  <span class="aviso__mensaje">{{ a.mensaje }}</span>
                </span>
                <span class="aviso__lado">
                  <span class="aviso__cuando">{{ hora(a.created_at) }}</span>
                  <span v-if="accion(a)" class="aviso__accion">
                    {{ accion(a) }}
                    <q-icon name="chevron_right" size="18px" aria-hidden="true" />
                  </span>
                </span>
              </button>
            </li>
          </ul>
        </section>
      </template>

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
    </div>
  </q-page>
</template>

<script setup lang="ts">
// Avisos dentro de la app (RF-09). La campanita del encabezado cuenta los que no se han leído.
import { computed, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { avisos as apiAvisos } from '@/api';
import { leerError } from '@/api/errores';
import type { Notificacion, TipoNotificacion } from '@/api/tipos';
import EstadoVacio from '@/components/EstadoVacio.vue';
import { useAvisosStore } from '@/stores/avisos';
import { avisarError } from '@/utils/avisar';
import { claveDia, diaCorto, hora, sumarDias } from '@/utils/formato';

definePage({ meta: { titulo: 'Avisos' } });

const router = useRouter();
const contador = useAvisosStore();
const lista = ref<Notificacion[]>([]);
const cargando = ref(true);
const marcando = ref(false);
const error = ref('');
const pagina = ref(1);
const hayMas = ref(false);
const filtro = ref<'todos' | 'sin-leer'>('todos');

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
    const respuesta = await apiAvisos.lista(
      filtro.value === 'sin-leer' ? { no_leidas: 1, page: numero } : { page: numero },
    );
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
watch(filtro, () => void cargar());

const sinLeer = computed(() => contador.noLeidas);

// Agrupados por día: "Hoy", "Ayer" o la fecha.
const grupos = computed(() => {
  const hoy = claveDia();
  const ayer = sumarDias(hoy, -1);
  const mapa = new Map<string, Notificacion[]>();
  for (const a of lista.value) {
    const clave = claveDia(a.created_at);
    mapa.set(clave, [...(mapa.get(clave) ?? []), a]);
  }
  return [...mapa.entries()].map(([clave, items]) => ({
    clave,
    titulo: clave === hoy ? 'Hoy' : clave === ayer ? 'Ayer' : diaCorto(items[0]?.created_at ?? ''),
    items,
  }));
});

function accion(a: Notificacion) {
  if (!a.viaje) return null;
  if (a.tipo === 'SOLICITUD_NUEVA' || a.tipo === 'SOLICITUD_CANCELADA') return 'Ver solicitudes';
  if (a.tipo === 'VIAJE_FINALIZADO') return 'Calificar';
  return 'Ver raite';
}

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
// Computadora: a todo el ancho; la acción de cada aviso queda a la derecha.
.avisos-pagina {
  max-width: none;
}
.avisos-pagina__filtros {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
}
.avisos-pagina__filtro {
  height: 40px;
  padding: 0 18px;
  border: 0;
  border-radius: 999px;
  background: var(--raite-blanco);
  color: var(--raite-azul);
  font: inherit;
  font-size: 0.875rem;
  font-weight: 700;
  box-shadow: var(--raite-sombra-tarjeta);
  cursor: pointer;
  &[aria-pressed='true'] {
    background: var(--raite-azul);
    color: var(--raite-blanco);
  }
}
.avisos-pagina__grupo + .avisos-pagina__grupo {
  margin-top: 24px;
}
.avisos-pagina__dia {
  display: inline-flex;
  align-items: center;
  height: 32px;
  margin: 0 0 12px;
  padding: 0 14px;
  border-radius: 999px;
  background: var(--raite-azul-tenue);
  color: var(--raite-azul);
  font-size: 0.875rem;
  font-weight: 700;
}
.avisos {
  margin: 0;
  padding: 0;
  list-style: none;
  border-radius: 20px;
  background: var(--raite-blanco);
  box-shadow: var(--raite-sombra-tarjeta);
  overflow: hidden;
  > li + li {
    border-top: 1px solid var(--raite-gris-tenue);
  }
}
.aviso {
  width: 100%;
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 16px 20px;
  border: 0;
  background: transparent;
  color: var(--raite-negro);
  font: inherit;
  text-align: left;
  cursor: pointer;
  &:hover {
    background: var(--raite-blanco-hover);
  }
  &:focus-visible {
    outline-offset: -3px;
  }
}
.aviso--nuevo {
  background: var(--raite-azul-tenue);
  &:hover {
    background: var(--raite-azul-tenue-hover);
  }
}
.aviso__icono {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
}
.aviso__icono--azul {
  background: var(--raite-azul-tenue);
  color: var(--raite-azul);
}
.aviso--nuevo .aviso__icono--azul {
  background: var(--raite-blanco);
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
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.aviso__tipo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.0625rem;
  font-weight: 700;
}
.aviso__nuevo {
  height: 24px;
  padding: 0 8px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  background: var(--raite-azul);
  color: var(--raite-blanco);
  font-size: 0.75rem;
  font-weight: 700;
}
.aviso__mensaje {
  line-height: 1.45;
  color: var(--raite-gris);
}
.aviso__lado {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}
.aviso__cuando {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--raite-gris);
}
.aviso__accion {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  height: 36px;
  padding: 0 8px 0 14px;
  border-radius: 999px;
  background: var(--raite-blanco);
  color: var(--raite-azul);
  font-size: 0.875rem;
  font-weight: 700;
  box-shadow: inset 0 0 0 1px var(--raite-borde-sutil);
}
@media (max-width: 599px) {
  .aviso__accion {
    display: none;
  }
}
</style>
