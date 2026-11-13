<template>
  <q-page v-if="usuario" class="raite-contenedor raite-contenedor--ancho">
    <h1 class="raite-titulo gt-sm">Perfil</h1>

    <div class="perfil">
      <!-- Izquierda: quién eres en Raite -->
      <aside class="perfil__lateral">
        <section class="raite-tarjeta perfil__resumen" aria-label="Tu cuenta">
          <AvatarIniciales
            :nombre="usuario.nombre_completo"
            :foto="usuario.foto"
            :tam="112"
            class="perfil__avatar"
          />
          <div class="perfil__foto-acciones">
            <q-btn
              flat
              dense
              no-caps
              color="primary"
              icon="photo_camera"
              :label="usuario.foto ? 'Cambiar foto' : 'Agregar foto'"
              :disable="subiendoFoto"
              @click="elegirFoto"
            />
            <q-btn
              v-if="usuario.foto"
              flat
              dense
              no-caps
              color="negative"
              label="Quitar"
              :disable="subiendoFoto"
              @click="quitarFoto"
            />
          </div>
          <input
            ref="entradaFoto"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            class="perfil__entrada-foto"
            tabindex="-1"
            aria-hidden="true"
            @change="fotoElegida"
          />
          <h2 class="perfil__nombre">{{ usuario.nombre_completo }}</h2>
          <p class="perfil__carrera">
            {{ usuario.carrera
            }}<template v-if="usuario.campus"> · {{ usuario.campus.codigo }}</template>
          </p>
          <p class="perfil__correo">{{ usuario.correo }}</p>
          <span class="perfil__verificado">
            <q-icon name="verified" size="18px" aria-hidden="true" />
            Correo verificado
          </span>
          <dl class="perfil__cifras">
            <div>
              <dt>Calificación</dt>
              <dd class="raite-dato">
                <q-icon name="star" size="20px" aria-hidden="true" />
                {{ calificacion(usuario.calificacion) ?? 'Nuevo' }}
              </dd>
            </div>
            <div>
              <dt>Usas Raite para</dt>
              <dd>{{ usoTexto }}</dd>
            </div>
          </dl>
        </section>

        <section
          v-if="sesion.esAmbos"
          class="raite-tarjeta raite-pila"
          aria-labelledby="perfil-uso"
        >
          <h2 id="perfil-uso" class="perfil__seccion">Ahora estás usando Raite para</h2>
          <q-btn-toggle
            :model-value="sesion.papel"
            class="raite-opciones"
            no-caps
            unelevated
            toggle-color="primary"
            :options="[
              { label: 'Pedir raite', value: 'pasajero' },
              { label: 'Dar raite', value: 'conductor' },
            ]"
            @update:model-value="cambiarPapel"
          />
        </section>

        <router-link v-else-if="!usuario.es_conductor" to="/vehiculo" class="ofrecer">
          <q-icon name="directions_car" size="28px" aria-hidden="true" />
          <span class="ofrecer__texto">
            <span class="ofrecer__titulo">Quiero ofrecer raites</span>
            <span class="ofrecer__detalle"
              >Registra tu vehículo y comparte los lugares que te sobran.</span
            >
          </span>
          <q-icon name="chevron_right" size="24px" aria-hidden="true" />
        </router-link>

        <q-btn
          outline
          color="negative"
          no-caps
          icon="logout"
          label="Cerrar sesión"
          class="full-width perfil__salir"
          :loading="saliendo"
          @click="salir"
        />
      </aside>

      <!-- Derecha: lo que se puede cambiar -->
      <div class="perfil__principal">
        <q-form class="raite-tarjeta perfil__formulario" novalidate @submit="guardar">
          <h2 class="perfil__seccion">Tus datos</h2>
          <div class="perfil__campos">
            <div>
              <label for="perfil-tel" class="raite-etiqueta">Teléfono o WhatsApp</label>
              <q-input
                hide-bottom-space
                for="perfil-tel"
                v-model="datos.telefono"
                outlined
                type="tel"
                inputmode="tel"
                mask="### ### ####"
                unmasked-value
                input-class="raite-dato"
                hint="Solo lo ve quien confirme un raite contigo"
                :error="!!errores.telefono"
                :error-message="errores.telefono"
              />
            </div>
            <SelectorCarrera
              v-if="!usuario.es_admin"
              v-model="datos.carrera"
              class="perfil__completo"
              :error="errores.carrera ?? ''"
            />
          </div>

          <fieldset class="perfil__grupo">
            <legend class="raite-etiqueta">Con quién viajo</legend>
            <div class="perfil__preferencias">
              <button
                v-for="p in preferencias"
                :key="p.valor"
                type="button"
                class="perfil__preferencia"
                :aria-pressed="datos.preferencia_compatibilidad === p.valor"
                @click="datos.preferencia_compatibilidad = p.valor"
              >
                <span class="perfil__preferencia-marca" aria-hidden="true">
                  <q-icon name="check" size="16px" />
                </span>
                <span class="perfil__preferencia-texto">
                  <span class="perfil__preferencia-nombre">{{ p.nombre }}</span>
                  <span class="perfil__preferencia-detalle">{{ p.detalle }}</span>
                </span>
              </button>
            </div>
          </fieldset>

          <div class="perfil__acciones">
            <span v-if="hayCambios" class="raite-ayuda">Tienes cambios sin guardar.</span>
            <q-btn
              type="submit"
              color="primary"
              unelevated
              no-caps
              label="Guardar cambios"
              class="perfil__guardar"
              :disable="!hayCambios"
              :loading="guardando"
            />
          </div>
        </q-form>

        <section
          v-if="usuario.vehiculo"
          class="raite-tarjeta perfil__vehiculo"
          aria-labelledby="perfil-vehiculo"
        >
          <span class="perfil__vehiculo-icono" aria-hidden="true">
            <q-icon name="directions_car" size="28px" />
          </span>
          <div class="perfil__vehiculo-datos">
            <h2 id="perfil-vehiculo" class="perfil__vehiculo-nombre">
              {{ usuario.vehiculo.marca }} {{ usuario.vehiculo.modelo }}
              {{ usuario.vehiculo.color.toLowerCase() }}
            </h2>
            <p class="raite-ayuda">
              {{ usuario.vehiculo.asientos_disponibles }}
              {{ usuario.vehiculo.asientos_disponibles === 1 ? 'asiento' : 'asientos' }} para
              pasajeros · placas
              <span class="raite-dato perfil__placas">{{ usuario.vehiculo.placas }}</span>
            </p>
          </div>
          <q-btn outline color="primary" no-caps icon="edit" label="Editar" to="/vehiculo" />
        </section>

        <q-expansion-item
          class="raite-tarjeta reportes"
          icon="flag"
          label="Mis reportes"
          :caption="
            reportes === null
              ? 'Los que has enviado y su estado'
              : reportes.length
                ? `${reportes.length} enviados`
                : 'Ninguno'
          "
          @before-show="cargarReportes"
        >
          <p v-if="reportes === null" class="raite-ayuda q-pa-md">Cargando…</p>
          <p v-else-if="!reportes.length" class="raite-ayuda q-pa-md">No has enviado reportes.</p>
          <ul v-else class="reportes__lista">
            <li v-for="r in reportes" :key="r.id" class="reportes__fila">
              <div>
                <p class="text-weight-bold">{{ r.reportado.nombre_completo }}</p>
                <p class="raite-ayuda">
                  {{ diaCorto(r.created_at) }} · {{ r.motivo.slice(0, 80)
                  }}{{ r.motivo.length > 80 ? '…' : '' }}
                </p>
              </div>
              <span class="reportes__estado">{{ r.estado_display }}</span>
            </li>
          </ul>
        </q-expansion-item>
      </div>
    </div>

    <RecortarFoto
      :archivo="archivoFoto"
      :guardando="subiendoFoto"
      @guardar="subirFoto"
      @cancelar="archivoFoto = null"
    />
  </q-page>
</template>

<script setup lang="ts">
// Perfil: datos editables (RF-07), vehículo, papel activo y reportes enviados (RF-12).
import { computed, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { comoLista, cuenta, reportes as apiReportes } from '@/api';
import { leerError } from '@/api/errores';
import { Rol, type Papel, type Preferencia, type Reporte } from '@/api/tipos';
import AvatarIniciales from '@/components/AvatarIniciales.vue';
import RecortarFoto from '@/components/RecortarFoto.vue';
import SelectorCarrera from '@/components/SelectorCarrera.vue';
import { useSesionStore } from '@/stores/sesion';
import { avisarAdvertencia, avisarError, avisarExito, confirmar } from '@/utils/avisar';
import { calificacion, diaCorto } from '@/utils/formato';

definePage({ meta: { titulo: 'Perfil' } });

const router = useRouter();
const sesion = useSesionStore();
const usuario = computed(() => sesion.usuario);

const datos = reactive<{
  telefono: string;
  carrera: number | null;
  preferencia_compatibilidad: Preferencia;
}>({
  telefono: usuario.value?.telefono ?? '',
  carrera: usuario.value?.carrera_id ?? null,
  preferencia_compatibilidad: usuario.value?.preferencia_compatibilidad ?? 'MIXTO',
});
const errores = reactive<Record<string, string>>({});
const guardando = ref(false);
const saliendo = ref(false);
const reportes = ref<Reporte[] | null>(null);

// Foto de perfil: se elige, se recorta en RecortarFoto y se sube. El API la revisa otra vez.
const TIPOS_FOTO = ['image/jpeg', 'image/png', 'image/webp'];
const FOTO_MAX_MB = 5;
const entradaFoto = ref<HTMLInputElement | null>(null);
const archivoFoto = ref<File | null>(null);
const subiendoFoto = ref(false);

function elegirFoto() {
  entradaFoto.value?.click();
}

function fotoElegida(evento: Event) {
  const entrada = evento.target as HTMLInputElement;
  const archivo = entrada.files?.[0];
  entrada.value = ''; // para poder elegir el mismo archivo otra vez
  if (!archivo) return;
  if (!TIPOS_FOTO.includes(archivo.type)) {
    avisarAdvertencia('Elige una imagen JPG, PNG o WebP.');
    return;
  }
  if (archivo.size > FOTO_MAX_MB * 1024 * 1024) {
    avisarAdvertencia(`La foto pesa más de ${FOTO_MAX_MB} MB. Elige una más ligera.`);
    return;
  }
  archivoFoto.value = archivo;
}

async function subirFoto(foto: Blob, nombre: string) {
  subiendoFoto.value = true;
  try {
    sesion.usuario = await cuenta.subirFoto(foto, nombre);
    archivoFoto.value = null;
    avisarExito('Guardamos tu foto.');
  } catch (e) {
    avisarError(e);
  } finally {
    subiendoFoto.value = false;
  }
}

async function quitarFoto() {
  const ok = await confirmar({
    titulo: '¿Quitar tu foto?',
    mensaje: 'En su lugar se mostrarán tus iniciales.',
    confirmar: 'Quitar foto',
    peligro: true,
  });
  if (!ok) return;
  subiendoFoto.value = true;
  try {
    sesion.usuario = await cuenta.quitarFoto();
    avisarExito('Quitamos tu foto.');
  } catch (e) {
    avisarError(e);
  } finally {
    subiendoFoto.value = false;
  }
}

const usoTexto = computed(() => {
  const rol = usuario.value?.rol;
  if (rol === Rol.AMBOS) return 'Pedir y dar raite';
  if (rol === Rol.CONDUCTOR) return 'Dar raite';
  return 'Pedir raite';
});

// "Con quién viajo": dos tarjetas en lugar de botones (textos neutros, sin suponer el sexo de nadie).
const preferencias: { valor: Preferencia; nombre: string; detalle: string }[] = [
  {
    valor: 'MIXTO',
    nombre: 'Grupo mixto',
    detalle: 'Puedes viajar con cualquier alumno verificado.',
  },
  {
    valor: 'MISMO_SEXO',
    nombre: 'Mismo sexo',
    detalle: 'Solo con personas que registraron el mismo sexo que tú. Aplica a todo el viaje.',
  },
];

const hayCambios = computed(
  () =>
    !!usuario.value &&
    (datos.telefono !== usuario.value.telefono ||
      datos.carrera !== usuario.value.carrera_id ||
      datos.preferencia_compatibilidad !== usuario.value.preferencia_compatibilidad),
);

async function guardar() {
  for (const clave of Object.keys(errores)) delete errores[clave];
  if (!/^\d{10}$/.test(datos.telefono)) errores.telefono = 'Escribe los 10 dígitos de tu teléfono.';
  const esAdmin = !!usuario.value?.es_admin;
  if (!esAdmin && !datos.carrera) errores.carrera = 'Elige tu campus y tu carrera.';
  if (Object.keys(errores).length) return;
  guardando.value = true;
  try {
    const { carrera, ...resto } = datos;
    sesion.usuario = await cuenta.editarPerfil(
      esAdmin || carrera === null ? resto : { ...resto, carrera },
    );
    avisarExito('Guardamos tus datos.');
  } catch (e) {
    Object.assign(errores, leerError(e).campos);
    avisarError(e);
  } finally {
    guardando.value = false;
  }
}

function cambiarPapel(papel: Papel) {
  sesion.cambiarPapel(papel);
  void router.push(sesion.inicio);
}

async function cargarReportes() {
  if (reportes.value !== null) return;
  try {
    reportes.value = comoLista(await apiReportes.mios());
  } catch (e) {
    reportes.value = [];
    avisarError(e);
  }
}

async function salir() {
  saliendo.value = true;
  await sesion.salir();
  await router.replace('/entrar');
}
</script>

<style scoped lang="scss">
// Computadora: resumen a la izquierda (fijo) y datos editables a la derecha.
.perfil {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 24px;
  align-items: start;
  @media (min-width: 1024px) {
    grid-template-columns: minmax(300px, 1fr) minmax(0, 2.2fr);
  }
}
.perfil__lateral,
.perfil__principal {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
}
@media (min-width: 1024px) {
  .perfil__lateral {
    position: sticky;
    top: 104px;
  }
}
.perfil__seccion {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 700;
  line-height: 1.3;
}

// --- Resumen ---
.perfil__resumen {
  padding: 28px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 4px;
}
.perfil__avatar {
  margin-bottom: 12px;
  font-size: 2.25rem !important;
  box-shadow:
    0 0 0 4px var(--raite-blanco),
    0 0 0 6px var(--raite-azul-niebla);
}
.perfil__foto-acciones {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 4px;
  margin: -4px 0 8px;
}
.perfil__entrada-foto {
  display: none;
}
.perfil__nombre {
  margin: 0;
  font-size: 1.375rem;
  font-weight: 700;
  line-height: 1.25;
}
.perfil__carrera,
.perfil__correo {
  margin: 0;
  font-size: 0.9375rem;
  color: var(--raite-gris);
  overflow-wrap: anywhere;
}
.perfil__verificado {
  margin-top: 8px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  background: var(--raite-verde-tenue);
  color: var(--raite-verde-texto);
  font-size: 0.875rem;
  font-weight: 600;
}
.perfil__completo {
  grid-column: 1 / -1;
}
.perfil__cifras {
  width: 100%;
  margin: 16px 0 0;
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
    margin: 4px 0 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    font-size: 1.0625rem;
    font-weight: 700;
  }
}

.ofrecer {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 20px;
  background: var(--raite-azul);
  color: var(--raite-blanco);
  text-decoration: none;
  &:hover {
    background: var(--raite-azul-hondo);
  }
  &:focus-visible {
    outline-color: var(--raite-amarillo);
  }
}
.ofrecer__texto {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.ofrecer__titulo {
  font-size: 1.125rem;
  font-weight: 700;
  box-shadow: inset 0 -3px 0 var(--raite-amarillo);
  align-self: flex-start;
}
.ofrecer__detalle {
  font-size: 0.875rem;
  color: var(--raite-azul-niebla);
}
.perfil__salir {
  background: var(--raite-blanco);
}

// --- Datos ---
.perfil__formulario {
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.perfil__campos {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px 24px;
}
.perfil__grupo {
  margin: 0;
  padding: 0;
  border: 0;
  min-width: 0;
}
.perfil__preferencias {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}
.perfil__preferencia {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
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
    .perfil__preferencia-nombre {
      color: var(--raite-azul);
    }
    .perfil__preferencia-marca {
      border-color: var(--raite-azul);
      background: var(--raite-azul);
      color: var(--raite-blanco);
    }
  }
}
.perfil__preferencia-marca {
  flex: none;
  width: 22px;
  height: 22px;
  margin-top: 1px;
  border: 2px solid var(--raite-borde-campo);
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: transparent;
}
.perfil__preferencia-texto {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.perfil__preferencia-nombre {
  font-weight: 700;
}
.perfil__preferencia-detalle {
  font-size: 0.875rem;
  line-height: 1.4;
  color: var(--raite-gris);
}
.perfil__acciones {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 16px;
}
.perfil__guardar {
  min-width: 200px;
}

// --- Vehículo ---
.perfil__vehiculo {
  padding: 20px 24px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
}
.perfil__vehiculo-icono {
  flex: none;
  width: 56px;
  height: 56px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--raite-azul-tenue);
  color: var(--raite-azul);
}
.perfil__vehiculo-datos {
  flex: 1;
  min-width: 220px;
  p {
    margin: 2px 0 0;
  }
}
.perfil__vehiculo-nombre {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 700;
}
.perfil__placas {
  font-weight: 600;
  letter-spacing: 0.08em;
  color: var(--raite-negro);
}

// --- Reportes ---
.reportes {
  padding: 0;
  overflow: hidden;
}
.reportes__lista {
  margin: 0;
  padding: 0 16px 16px;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.reportes__fila {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  p {
    margin: 0;
  }
}
.reportes__estado {
  flex-shrink: 0;
  font-size: 0.875rem;
  font-weight: 600;
}
</style>
