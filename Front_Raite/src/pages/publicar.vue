<template>
  <q-page class="raite-contenedor raite-contenedor--ancho con-barra">
    <h1 class="raite-titulo gt-sm">{{ editando ? 'Editar viaje' : 'Publicar viaje' }}</h1>

    <EstadoVacio
      v-if="!vehiculo"
      icono="directions_car"
      titulo="Registra tu vehículo para ofrecer raites"
    >
      Necesitamos marca, modelo, color, placas y cuántos asientos tienes libres.
      <template #acciones>
        <q-btn color="primary" unelevated no-caps label="Registrar vehículo" to="/vehiculo" />
      </template>
    </EstadoVacio>

    <EstadoVacio
      v-else-if="sesion.usuario?.suspendido"
      icono="block"
      titulo="Tu cuenta está suspendida"
    >
      Mientras revisamos un reporte no puedes publicar viajes.
    </EstadoVacio>

    <div v-else-if="cargandoEdicion" class="publicar__rejilla">
      <q-skeleton type="rect" height="520px" style="border-radius: 20px" />
      <q-skeleton type="rect" height="240px" style="border-radius: 20px" />
    </div>

    <div v-else class="publicar__rejilla">
      <q-form
        id="form-publicar"
        class="raite-tarjeta publicar__formulario"
        novalidate
        @submit="enviar"
      >
        <!-- 1. Ruta -->
        <section class="publicar__seccion" aria-labelledby="pub-sec-ruta">
          <h2 id="pub-sec-ruta" class="publicar__encabezado">
            <span class="publicar__numero" aria-hidden="true">1</span>
            Ruta
          </h2>

          <template v-if="!editando">
            <div>
              <SelectorPunto
                v-model="datos.punto"
                etiqueta="Sales de"
                :con-ubicacion="true"
                hint="Un lugar conocido. El punto exacto lo acuerdas con cada pasajero."
                :error="errores.punto_referencia ?? null"
              />
              <q-btn
                flat
                no-caps
                color="primary"
                :icon="verMapa ? 'expand_less' : 'map'"
                :label="verMapa ? 'Ocultar mapa' : 'Elegir en el mapa'"
                class="q-mt-xs publicar__mapa-boton"
                @click="verMapa = !verMapa"
              />
              <div v-if="verMapa" class="publicar__mapa">
                <MapaRaite
                  :puntos="catalogos.puntos"
                  :seleccionado="datos.punto"
                  :campus="campusElegido ? [campusElegido] : []"
                  elegible
                  etiqueta="Mapa para elegir el punto de salida. También puedes escribirlo arriba."
                  @seleccionar="(id) => (datos.punto = id)"
                />
              </div>
            </div>

            <div class="publicar__fila publicar__fila--ruta">
              <fieldset class="publicar__grupo">
                <legend class="raite-etiqueta">Vas</legend>
                <q-btn-toggle
                  v-model="datos.sentido"
                  class="raite-opciones"
                  no-caps
                  unelevated
                  toggle-color="primary"
                  :options="[
                    { label: 'Hacia el campus', value: 'HACIA_CAMPUS' },
                    { label: 'Desde el campus', value: 'DESDE_CAMPUS' },
                  ]"
                />
              </fieldset>
              <div>
                <SelectorCampus v-model="datos.campus" />
                <p v-if="errores.campus" class="publicar__error" role="alert">
                  {{ errores.campus }}
                </p>
              </div>
            </div>
          </template>

          <div v-else class="publicar__ruta-fija">
            <RutaViaje
              v-if="campusElegido && puntoElegido"
              :punto="puntoElegido.nombre"
              :campus="campusElegido"
              :sentido="datos.sentido"
            />
            <p class="raite-ayuda">
              La ruta no se cambia. Si necesitas otra, cancela este viaje y publica uno nuevo.
            </p>
          </div>
        </section>

        <!-- 2. Horario -->
        <section class="publicar__seccion" aria-labelledby="pub-sec-horario">
          <h2 id="pub-sec-horario" class="publicar__encabezado">
            <span class="publicar__numero" aria-hidden="true">2</span>
            Horario
          </h2>
          <div class="publicar__fila">
            <div>
              <label for="pub-dia" class="raite-etiqueta">Día</label>
              <q-select
                for="pub-dia"
                v-model="datos.dia"
                :options="dias"
                emit-value
                map-options
                outlined
                :error="!!errores.fecha_hora"
              />
            </div>
            <div>
              <label for="pub-hora" class="raite-etiqueta">Sales a las</label>
              <q-select
                for="pub-hora"
                v-model="datos.hora"
                :options="horas"
                emit-value
                map-options
                outlined
                options-dense
                input-class="raite-dato"
                :error="!!errores.fecha_hora"
              />
            </div>
          </div>
          <p v-if="errores.fecha_hora" class="publicar__error" role="alert">
            {{ errores.fecha_hora }}
          </p>
        </section>

        <!-- 3. Lugares y grupo -->
        <section class="publicar__seccion" aria-labelledby="pub-sec-lugares">
          <h2 id="pub-sec-lugares" class="publicar__encabezado">
            <span class="publicar__numero" aria-hidden="true">3</span>
            Lugares y grupo
          </h2>
          <div class="publicar__fila">
            <fieldset class="publicar__grupo">
              <legend class="raite-etiqueta">Lugares que ofreces</legend>
              <q-btn-toggle
                v-model="datos.lugares"
                class="raite-opciones"
                no-caps
                unelevated
                toggle-color="primary"
                :options="
                  [1, 2, 3, 4, 5].map((n) => ({
                    label: String(n),
                    value: n,
                    disable: n > (vehiculo?.asientos_disponibles ?? 5),
                  }))
                "
              />
              <p class="raite-ayuda q-mt-sm">
                Tu {{ vehiculo?.marca }} {{ vehiculo?.modelo }} tiene
                {{ vehiculo?.asientos_disponibles }}
                {{ vehiculo?.asientos_disponibles === 1 ? 'asiento' : 'asientos' }} para pasajeros.
              </p>
              <p v-if="errores.lugares_ofrecidos" class="publicar__error" role="alert">
                {{ errores.lugares_ofrecidos }}
              </p>
            </fieldset>

            <fieldset class="publicar__grupo">
              <legend class="raite-etiqueta">¿Con quién viajas?</legend>
              <q-btn-toggle
                v-model="datos.preferencia"
                class="raite-opciones"
                no-caps
                unelevated
                toggle-color="primary"
                :options="[
                  { label: 'Grupo mixto', value: 'MIXTO' },
                  { label: 'Mismo sexo', value: 'MISMO_SEXO' },
                ]"
              />
              <p class="raite-ayuda q-mt-sm">
                Con "mismo sexo", solo podrán pedir lugar personas con el mismo sexo que tú.
              </p>
              <p v-if="errores.preferencia_compatibilidad" class="publicar__error" role="alert">
                {{ errores.preferencia_compatibilidad }}
              </p>
            </fieldset>
          </div>
        </section>

        <!-- 4. Notas -->
        <section class="publicar__seccion" aria-labelledby="pub-sec-notas">
          <h2 id="pub-sec-notas" class="publicar__encabezado">
            <span class="publicar__numero" aria-hidden="true">4</span>
            Notas
            <span class="publicar__opcional">(opcional)</span>
          </h2>
          <div>
            <label for="pub-notas" class="sr-only">Notas para los pasajeros</label>
            <q-input
              for="pub-notas"
              v-model="datos.notas"
              outlined
              type="textarea"
              autogrow
              maxlength="300"
              counter
              placeholder="Ej. Salgo puntual; espero 5 minutos."
              v-bind="campo('notas')"
            />
          </div>
        </section>

        <q-banner v-if="mensaje" class="bg-rojo-tenue text-rojo-texto rounded-borders" role="alert">
          <template #avatar><q-icon name="error_outline" aria-hidden="true" /></template>
          {{ mensaje }}
        </q-banner>
      </q-form>

      <aside class="publicar__lateral">
        <section class="raite-tarjeta publicar__vista" aria-labelledby="pub-vista">
          <h2 id="pub-vista" class="publicar__vista-titulo">Así te verán los pasajeros</h2>
          <div v-if="puntoElegido && campusElegido" class="vista">
            <div class="vista__arriba">
              <div>
                <p class="vista__hora raite-dato">{{ datos.hora }}</p>
                <p class="vista__dia">{{ datos.dia ? diaDeClave(datos.dia) : '' }}</p>
              </div>
              <span class="vista__lugares">{{ lugares(datos.lugares, datos.lugares) }}</span>
            </div>
            <RutaViaje
              :punto="puntoElegido.nombre"
              :campus="campusElegido"
              :sentido="datos.sentido"
            />
            <p class="vista__abajo">
              <span>{{ nombreCorto(sesion.usuario?.nombre_completo ?? '') }}</span>
              <span class="vista__calif"
                ><q-icon name="star" size="16px" aria-hidden="true" />{{
                  calificacion(sesion.usuario?.calificacion) ?? 'Nuevo'
                }}</span
              >
              <span v-if="datos.preferencia === 'MISMO_SEXO'" class="text-gris">Mismo sexo</span>
            </p>
          </div>
          <div v-else class="vista vista--vacia">
            <q-icon name="route" size="32px" aria-hidden="true" />
            <p>Elige de dónde sales y el campus para ver cómo se verá tu viaje.</p>
          </div>
        </section>

        <BarraAccion v-if="vehiculo && !sesion.usuario?.suspendido && !cargandoEdicion">
          <q-btn
            type="submit"
            form="form-publicar"
            color="primary"
            unelevated
            no-caps
            :label="editando ? 'Guardar cambios' : 'Publicar viaje'"
            :loading="enviando"
          />
        </BarraAccion>

        <p class="publicar__privado">
          <q-icon name="lock" size="18px" aria-hidden="true" />
          Tu teléfono y tus placas solo los ve quien aceptes en el viaje.
        </p>
      </aside>
    </div>
  </q-page>
</template>

<script setup lang="ts">
// Publicar o editar un viaje (RF-02, RF-03, RF-07). Computadora: formulario por secciones a la izquierda;
// vista previa y botón de publicar a la derecha.
import { computed, onMounted, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { viajes } from '@/api';
import { leerError } from '@/api/errores';
import type { Preferencia, Sentido } from '@/api/tipos';
import BarraAccion from '@/components/BarraAccion.vue';
import EstadoVacio from '@/components/EstadoVacio.vue';
import MapaRaite from '@/components/MapaRaite.vue';
import RutaViaje from '@/components/RutaViaje.vue';
import SelectorCampus from '@/components/SelectorCampus.vue';
import SelectorPunto from '@/components/SelectorPunto.vue';
import { useCatalogosStore } from '@/stores/catalogos';
import { useSesionStore } from '@/stores/sesion';
import { avisarExito } from '@/utils/avisar';
import {
  calificacion,
  claveDia,
  diaDeClave,
  fechaHoraLocal,
  hora,
  lugares,
  nombreCorto,
  sumarDias,
} from '@/utils/formato';

definePage({ meta: { titulo: 'Publicar viaje', papel: 'conductor' } });

const route = useRoute();
const router = useRouter();
const sesion = useSesionStore();
const catalogos = useCatalogosStore();

const editarId = typeof route.query.editar === 'string' ? route.query.editar : null;
const editando = !!editarId;
const vehiculo = computed(() => sesion.usuario?.vehiculo ?? null);

function horaSugerida() {
  // La siguiente media hora, al menos 30 minutos después de ahora.
  const ahora = new Date(Date.now() + 30 * 60_000);
  const [h, m] = hora(ahora.toISOString()).split(':').map(Number) as [number, number];
  const minutos = Math.min(Math.ceil((h * 60 + m) / 30) * 30, 23 * 60 + 30);
  return `${String(Math.floor(minutos / 60)).padStart(2, '0')}:${String(minutos % 60).padStart(2, '0')}`;
}

interface FormViaje {
  punto: number | null;
  campus: number | null;
  sentido: Sentido;
  dia: string;
  hora: string;
  lugares: number;
  preferencia: Preferencia;
  notas: string;
}

const datos = reactive<FormViaje>({
  punto: null,
  campus: null,
  sentido: 'HACIA_CAMPUS',
  dia: claveDia(),
  hora: horaSugerida(),
  lugares: Math.min(3, vehiculo.value?.asientos_disponibles ?? 3),
  preferencia: sesion.usuario?.preferencia_compatibilidad ?? 'MIXTO',
  notas: '',
});
const errores = reactive<Record<string, string>>({});
const mensaje = ref('');
const enviando = ref(false);
const cargandoEdicion = ref(editando);
// En computadora el mapa empieza abierto: hay espacio y ayuda a ubicar el punto.
const verMapa = ref(useQuasar().screen.gt.sm);

const puntoElegido = computed(() => catalogos.puntoPorId(datos.punto));
const campusElegido = computed(() => catalogos.campusPorId(datos.campus));

const dias = computed(() => {
  const hoy = claveDia();
  return Array.from({ length: 14 }, (_, i) => {
    const clave = sumarDias(hoy, i);
    return { label: diaDeClave(clave), value: clave };
  });
});
const horas = Array.from({ length: 73 }, (_, i) => {
  const minutos = 5 * 60 + i * 15; // de 05:00 a 23:00
  const hhmm = `${String(Math.floor(minutos / 60)).padStart(2, '0')}:${String(minutos % 60).padStart(2, '0')}`;
  return { label: hhmm, value: hhmm };
});

onMounted(async () => {
  await catalogos.cargar();
  if (!editarId) return;
  try {
    const v = await viajes.detalle(editarId);
    Object.assign(datos, {
      punto: v.punto_referencia.id,
      campus: v.campus.id,
      sentido: v.sentido,
      dia: claveDia(v.fecha_hora),
      hora: hora(v.fecha_hora),
      lugares: v.lugares_ofrecidos,
      preferencia: v.preferencia_compatibilidad,
      notas: v.notas,
    });
  } catch (e) {
    mensaje.value = leerError(e).mensaje;
  } finally {
    cargandoEdicion.value = false;
  }
});

function campo(nombre: string) {
  return { error: !!errores[nombre], errorMessage: errores[nombre] ?? '', hideBottomSpace: true };
}

function validar() {
  for (const clave of Object.keys(errores)) delete errores[clave];
  if (!editando && !datos.punto) errores.punto_referencia = 'Elige de dónde sales.';
  if (!editando && !datos.campus) errores.campus = 'Elige el campus.';
  if (new Date(`${fechaHoraLocal(datos.dia, datos.hora)}-07:00`).getTime() <= Date.now()) {
    errores.fecha_hora = 'Esa hora ya pasó. Elige una más tarde.';
  }
  return Object.keys(errores).length === 0;
}

async function enviar() {
  mensaje.value = '';
  if (!validar()) {
    mensaje.value = 'Revisa los datos marcados.';
    return;
  }
  enviando.value = true;
  const comunes = {
    fecha_hora: fechaHoraLocal(datos.dia, datos.hora),
    lugares_ofrecidos: datos.lugares,
    preferencia_compatibilidad: datos.preferencia,
    notas: datos.notas.trim(),
  };
  try {
    if (editarId) {
      await viajes.editar(editarId, comunes);
      avisarExito('Guardamos los cambios. Les avisamos a tus pasajeros.');
      await router.replace(`/viajes/${editarId}`);
    } else {
      const nuevo = await viajes.publicar({
        ...comunes,
        punto_referencia: datos.punto ?? 0,
        campus: datos.campus ?? 0,
        sentido: datos.sentido,
      });
      avisarExito('Tu viaje ya está publicado. Te avisamos cuando alguien pida lugar.');
      await router.replace(`/viajes/${nuevo.id}`);
    }
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
// Computadora: formulario por secciones a la izquierda; vista previa y botón a la derecha.
.publicar__rejilla {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 24px;
  align-items: start;
  @media (min-width: 1024px) {
    grid-template-columns: minmax(0, 3fr) minmax(340px, 2fr);
  }
}
.publicar__formulario {
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 28px;
}
.publicar__seccion {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.publicar__seccion + .publicar__seccion {
  padding-top: 24px;
  border-top: 1px solid var(--raite-gris-tenue);
}
.publicar__encabezado {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.125rem;
  font-weight: 700;
  line-height: 1.3;
}
.publicar__numero {
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
.publicar__opcional {
  font-size: 0.875rem;
  font-weight: 400;
  color: var(--raite-gris);
}
.publicar__grupo {
  margin: 0;
  padding: 0;
  border: 0;
  min-width: 0;
}
.publicar__fila {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px 24px;
}
// "Vas" y "Campus" lado a lado solo cuando el formulario es ancho (pantallas de 1440 px o más).
.publicar__fila--ruta {
  @media (max-width: 1439px) {
    grid-template-columns: minmax(0, 1fr);
  }
}
.publicar__error {
  margin: 8px 0 0;
  font-size: 0.875rem;
  color: var(--raite-rojo-texto);
}
.publicar__mapa-boton {
  margin-left: -8px;
}
.publicar__mapa {
  height: 300px;
  margin-top: 8px;
  border-radius: 16px;
  overflow: hidden;
}
.publicar__ruta-fija {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border-radius: 16px;
  background: var(--raite-fondo);
}

// --- Columna derecha ---
.publicar__lateral {
  display: flex;
  flex-direction: column;
  gap: 16px;
  @media (min-width: 1024px) {
    position: sticky;
    top: 104px;
  }
}
.publicar__vista {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.publicar__vista-titulo {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: var(--raite-gris);
}
.vista {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border: 1px solid var(--raite-borde-sutil);
  border-radius: 16px;
  background: var(--raite-blanco);
}
.vista--vacia {
  align-items: center;
  text-align: center;
  padding: 28px 16px;
  border-style: dashed;
  color: var(--raite-gris);
  p {
    margin: 0;
    max-width: 280px;
  }
}
.vista__arriba {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  p {
    margin: 0;
  }
}
.vista__hora {
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.1;
  color: var(--raite-azul);
}
.vista__dia {
  margin-top: 4px !important;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--raite-gris);
}
.vista__lugares {
  display: inline-flex;
  align-items: center;
  height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  background: var(--raite-azul-tenue);
  color: var(--raite-azul);
  font-size: 0.875rem;
  font-weight: 600;
  white-space: nowrap;
}
.vista__abajo {
  margin: 0;
  display: flex;
  gap: 16px;
  font-size: 0.875rem;
  font-weight: 600;
}
.vista__calif {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.publicar__privado {
  margin: 0;
  padding: 0 4px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: var(--raite-gris);
}
</style>
