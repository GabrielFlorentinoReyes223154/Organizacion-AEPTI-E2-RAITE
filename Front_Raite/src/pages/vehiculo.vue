<template>
  <q-page class="raite-contenedor vehiculo">
    <div class="vehiculo__rejilla">
      <q-form
        class="vehiculo__formulario raite-tarjeta raite-pila raite-pila--grupos"
        novalidate
        @submit="enviar"
      >
        <div>
          <h2 class="vehiculo__titulo">
            {{ editando ? 'Datos de tu vehículo' : 'Registra tu vehículo' }}
          </h2>
          <p class="raite-ayuda">
            {{
              editando
                ? 'Puedes cambiar la marca, el modelo, el color y los asientos.'
                : 'Con esto tus pasajeros reconocen tu auto cuando pases por ellos.'
            }}
          </p>
        </div>

        <div class="vehiculo__campos">
          <div>
            <label for="veh-marca" class="raite-etiqueta">Marca</label>
            <q-input
              for="veh-marca"
              v-model="datos.marca"
              outlined
              maxlength="60"
              placeholder="Nissan"
              v-bind="campo('marca')"
            />
          </div>
          <div>
            <label for="veh-modelo" class="raite-etiqueta">Modelo</label>
            <q-input
              for="veh-modelo"
              v-model="datos.modelo"
              outlined
              maxlength="60"
              placeholder="Versa"
              v-bind="campo('modelo')"
            />
          </div>
          <div>
            <label for="veh-color" class="raite-etiqueta">Color</label>
            <q-input
              for="veh-color"
              v-model="datos.color"
              outlined
              maxlength="40"
              placeholder="Gris"
              v-bind="campo('color')"
            />
          </div>
          <div>
            <label for="veh-placas" class="raite-etiqueta">Placas</label>
            <q-input
              for="veh-placas"
              v-model="datos.placas"
              outlined
              maxlength="12"
              input-class="raite-dato text-uppercase"
              :readonly="editando"
              :hint="editando ? 'Las placas no se cambian' : undefined"
              v-bind="campo('placas')"
            />
          </div>
        </div>

        <fieldset class="vehiculo__grupo">
          <legend class="raite-etiqueta">Tipo</legend>
          <div class="vehiculo__tipos">
            <button
              v-for="t in tipos"
              :key="t.valor"
              type="button"
              class="vehiculo__tipo"
              :aria-pressed="datos.tipo === t.valor"
              :disabled="editando"
              @click="datos.tipo = t.valor"
            >
              <q-icon :name="t.icono" size="28px" aria-hidden="true" />
              {{ t.nombre }}
            </button>
          </div>
          <p v-if="editando" class="raite-ayuda q-mt-sm">El tipo no se cambia.</p>
          <p v-if="errores.tipo" class="vehiculo__error" role="alert">{{ errores.tipo }}</p>
        </fieldset>

        <fieldset class="vehiculo__grupo">
          <legend class="raite-etiqueta">Asientos para pasajeros</legend>
          <q-btn-toggle
            v-model="datos.asientos_disponibles"
            class="raite-opciones"
            no-caps
            unelevated
            toggle-color="primary"
            :options="[1, 2, 3, 4, 5].map((n) => ({ label: String(n), value: n }))"
          />
          <p class="raite-ayuda q-mt-sm">
            Sin contarte a ti. En cada viaje decides cuántos ofreces.
          </p>
          <p v-if="errores.asientos_disponibles" class="vehiculo__error" role="alert">
            {{ errores.asientos_disponibles }}
          </p>
        </fieldset>

        <q-banner v-if="mensaje" class="bg-rojo-tenue text-rojo-texto rounded-borders" role="alert">
          <template #avatar><q-icon name="error_outline" aria-hidden="true" /></template>
          {{ mensaje }}
        </q-banner>

        <div class="vehiculo__acciones">
          <q-btn
            v-if="bienvenida"
            flat
            color="primary"
            no-caps
            label="Lo hago después"
            :to="sesion.inicio"
          />
          <q-btn
            type="submit"
            color="primary"
            unelevated
            no-caps
            :label="editando ? 'Guardar cambios' : 'Registrar vehículo'"
            :loading="enviando"
            class="raite-btn-xl vehiculo__enviar"
          />
        </div>
      </q-form>

      <aside class="vehiculo__lateral">
        <div
          v-if="bienvenida || (!editando && sesion.usuario?.rol === Rol.PASAJERO)"
          class="vehiculo__aviso"
        >
          <q-icon name="directions_car" size="24px" color="primary" aria-hidden="true" />
          <p>
            {{
              bienvenida
                ? 'Último paso para dar raite: los datos de tu auto.'
                : 'Al registrar tu vehículo podrás pedir raite y también ofrecerlo. Cambias entre las dos cosas arriba, con "Pido raite / Doy raite".'
            }}
          </p>
        </div>

        <section class="vehiculo__previa raite-tarjeta" aria-labelledby="veh-previa">
          <h2 id="veh-previa" class="vehiculo__previa-titulo">Así lo verán tus pasajeros</h2>
          <div class="vehiculo__auto">
            <span class="vehiculo__auto-icono" aria-hidden="true">
              <q-icon :name="tipoElegido?.icono ?? 'directions_car'" size="32px" />
            </span>
            <div>
              <p class="vehiculo__auto-nombre">{{ nombreVehiculo }}</p>
              <p class="vehiculo__auto-detalle">{{ detalleVehiculo }}</p>
            </div>
          </div>
          <dl class="vehiculo__datos">
            <div>
              <dt>Asientos</dt>
              <dd>{{ datos.asientos_disponibles }} para pasajeros</dd>
            </div>
            <div>
              <dt>Placas</dt>
              <dd v-if="datos.placas" class="raite-dato vehiculo__placas">
                {{ datos.placas.toUpperCase() }}
              </dd>
              <dd v-else class="vehiculo__sin-placas">Sin capturar</dd>
            </div>
          </dl>
          <p class="vehiculo__privado">
            <q-icon name="lock" size="18px" aria-hidden="true" />
            Las placas solo las ve quien confirme un raite contigo.
          </p>
        </section>
      </aside>
    </div>
  </q-page>
</template>

<script setup lang="ts">
// Vehículo del conductor (RF-01, RF-03). Si quien lo registra era solo pasajero, pasa a AMBOS.
import { computed, onMounted, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { cuenta } from '@/api';
import { leerError } from '@/api/errores';
import { Rol, type TipoVehiculo } from '@/api/tipos';
import { useSesionStore } from '@/stores/sesion';
import { avisarExito } from '@/utils/avisar';

definePage({ meta: { titulo: 'Tu vehículo', atras: '/perfil' } });

const route = useRoute();
const router = useRouter();
const sesion = useSesionStore();

const bienvenida = route.query.bienvenida === '1';
const editando = computed(() => !!sesion.usuario?.vehiculo);
const datos = reactive({
  marca: '',
  modelo: '',
  color: '',
  placas: '',
  tipo: null as TipoVehiculo | null,
  asientos_disponibles: 4,
});
const errores = reactive<Record<string, string>>({});
const mensaje = ref('');
const enviando = ref(false);

onMounted(() => {
  const v = sesion.usuario?.vehiculo;
  if (v)
    Object.assign(datos, {
      marca: v.marca,
      modelo: v.modelo,
      color: v.color,
      placas: v.placas,
      tipo: v.tipo,
      asientos_disponibles: v.asientos_disponibles,
    });
});

const tipos: { valor: TipoVehiculo; nombre: string; icono: string }[] = [
  { valor: 'COCHE', nombre: 'Coche', icono: 'directions_car' },
  { valor: 'CAMIONETA', nombre: 'Camioneta', icono: 'airport_shuttle' },
  { valor: 'TROCA', nombre: 'Troca', icono: 'local_shipping' },
];
const tipoElegido = computed(() => tipos.find((t) => t.valor === datos.tipo));

// Vista previa: se arma con lo que se va escribiendo.
const nombreVehiculo = computed(
  () => [datos.marca.trim(), datos.modelo.trim()].filter(Boolean).join(' ') || 'Tu vehículo',
);
const detalleVehiculo = computed(
  () =>
    [datos.color.trim(), tipoElegido.value?.nombre].filter(Boolean).join(' · ') || 'Color y tipo',
);

function campo(nombre: string) {
  return { error: !!errores[nombre], errorMessage: errores[nombre] ?? '', hideBottomSpace: true };
}

function validar() {
  for (const clave of Object.keys(errores)) delete errores[clave];
  if (!datos.marca.trim()) errores.marca = 'Escribe la marca.';
  if (!datos.modelo.trim()) errores.modelo = 'Escribe el modelo.';
  if (!datos.color.trim()) errores.color = 'Escribe el color.';
  if (!editando.value && datos.placas.replace(/[\s-]/g, '').length < 5)
    errores.placas = 'Escribe las placas completas.';
  if (!datos.tipo) errores.tipo = 'Elige el tipo de vehículo.';
  return Object.keys(errores).length === 0;
}

async function enviar() {
  mensaje.value = '';
  if (!validar()) return;
  enviando.value = true;
  try {
    if (editando.value) {
      await cuenta.editarVehiculo({
        marca: datos.marca.trim(),
        modelo: datos.modelo.trim(),
        color: datos.color.trim(),
        asientos_disponibles: datos.asientos_disponibles,
      });
      await sesion.cargarUsuario();
      avisarExito('Guardamos los cambios de tu vehículo.');
      await router.push('/perfil');
      return;
    }
    const eraPasajero = sesion.usuario?.rol === Rol.PASAJERO;
    await cuenta.registrarVehiculo({
      marca: datos.marca.trim(),
      modelo: datos.modelo.trim(),
      color: datos.color.trim(),
      placas: datos.placas,
      tipo: datos.tipo as TipoVehiculo,
      asientos_disponibles: datos.asientos_disponibles,
    });
    await sesion.cargarUsuario();
    sesion.cambiarPapel('conductor');
    avisarExito(
      eraPasajero
        ? 'Listo. Ya puedes ofrecer raites.'
        : 'Listo. Ya puedes publicar tu primer viaje.',
    );
    await router.replace('/publicar');
  } catch (error) {
    const legible = leerError(error);
    Object.assign(errores, legible.campos);
    mensaje.value = legible.mensaje;
  } finally {
    enviando.value = false;
  }
}
</script>

<style scoped lang="scss">
// En escritorio: formulario a la izquierda y vista previa a la derecha, a todo el ancho y alineados con el título.
.vehiculo {
  max-width: none;
  margin: 0;
}
.vehiculo__rejilla {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 24px;
  align-items: start;
  @media (min-width: 1024px) {
    grid-template-columns: minmax(0, 1.5fr) minmax(300px, 1fr);
  }
}
.vehiculo__formulario {
  padding: 28px;
}
.vehiculo__titulo {
  margin: 0 0 4px;
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.3;
}
.vehiculo__campos {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px 16px;
}
.vehiculo__grupo {
  margin: 0;
  padding: 0;
  border: 0;
  min-width: 0;
}
.vehiculo__error {
  margin: 8px 0 0;
  font-size: 0.875rem;
  color: var(--raite-rojo-texto);
}

.vehiculo__tipos {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}
.vehiculo__tipo {
  height: 88px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px solid var(--raite-borde-campo);
  border-radius: 16px;
  background: var(--raite-blanco);
  color: var(--raite-negro);
  font: inherit;
  font-weight: 700;
  cursor: pointer;
  .q-icon {
    color: var(--raite-azul);
  }
  &:hover:not(:disabled):not([aria-pressed='true']) {
    background: var(--raite-blanco-hover);
  }
  &[aria-pressed='true'] {
    border-color: var(--raite-azul);
    background: var(--raite-azul);
    color: var(--raite-blanco);
    .q-icon {
      color: var(--raite-blanco);
    }
  }
  &:disabled {
    cursor: default;
    &:not([aria-pressed='true']) {
      background: var(--raite-gris-tenue);
      border-color: transparent;
      color: var(--raite-gris-deshabilitado);
      .q-icon {
        color: var(--raite-gris-deshabilitado);
      }
    }
  }
}

.vehiculo__acciones {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
}
.vehiculo__enviar {
  min-width: 240px;
}

// --- Columna derecha ---
.vehiculo__lateral {
  display: flex;
  flex-direction: column;
  gap: 16px;
  @media (min-width: 1024px) {
    position: sticky;
    top: 104px;
  }
}
.vehiculo__aviso {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 16px;
  border-radius: 20px;
  background: var(--raite-azul-tenue);
  p {
    margin: 0;
    font-size: 0.9375rem;
    line-height: 1.45;
  }
}
.vehiculo__previa {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.vehiculo__previa-titulo {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: var(--raite-gris);
}
.vehiculo__auto {
  display: flex;
  align-items: center;
  gap: 14px;
}
.vehiculo__auto-icono {
  flex: none;
  width: 64px;
  height: 64px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--raite-azul-tenue);
  color: var(--raite-azul);
}
.vehiculo__auto-nombre {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.25;
}
.vehiculo__auto-detalle {
  margin: 2px 0 0;
  font-size: 0.9375rem;
  color: var(--raite-gris);
}
.vehiculo__datos {
  margin: 0;
  padding: 16px 0 0;
  border-top: 1px solid var(--raite-gris-tenue);
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  dt {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--raite-gris);
  }
  dd {
    margin: 2px 0 0;
    font-size: 1rem;
    font-weight: 700;
  }
}
.vehiculo__placas {
  font-size: 1.125rem;
  letter-spacing: 0.08em;
}
.vehiculo__sin-placas {
  color: var(--raite-gris);
  font-weight: 600 !important;
}
.vehiculo__privado {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: var(--raite-gris);
}
</style>
