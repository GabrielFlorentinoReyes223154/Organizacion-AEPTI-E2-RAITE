<template>
  <q-page v-if="usuario" class="raite-contenedor raite-contenedor--angosto">
    <h1 class="raite-titulo gt-sm">Perfil</h1>

    <div class="raite-pila raite-pila--grupos">
      <section class="raite-tarjeta cabecera" aria-label="Tu cuenta">
        <AvatarIniciales :nombre="usuario.nombre_completo" :tam="56" tono="solido" />
        <div class="cabecera__datos">
          <p class="cabecera__nombre">{{ usuario.nombre_completo }}</p>
          <p class="raite-ayuda">{{ usuario.correo }}</p>
        </div>
        <span class="cabecera__calif">
          <q-icon name="star" size="20px" aria-hidden="true" />
          {{ calificacion(usuario.calificacion) ?? 'Nuevo' }}
        </span>
      </section>

      <!-- Cómo usa Raite -->
      <section v-if="sesion.esAmbos" class="raite-pila" aria-labelledby="perfil-uso">
        <h2 id="perfil-uso" class="raite-seccion">Ahora estás usando Raite para</h2>
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

      <!-- Datos que se pueden editar -->
      <q-form class="raite-tarjeta raite-pila" novalidate @submit="guardar">
        <h2 class="raite-seccion">Tus datos</h2>
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
        <div>
          <label for="perfil-carrera" class="raite-etiqueta">Carrera</label>
          <q-input
            hide-bottom-space
            for="perfil-carrera"
            v-model="datos.carrera"
            outlined
            maxlength="120"
            :error="!!errores.carrera"
            :error-message="errores.carrera"
          />
        </div>
        <fieldset class="perfil__grupo">
          <legend class="raite-etiqueta">¿Con quién prefieres viajar?</legend>
          <q-btn-toggle
            v-model="datos.preferencia_compatibilidad"
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
            Con "mismo sexo" solo verás y compartirás raites donde todos tengan el mismo sexo que
            tú.
          </p>
        </fieldset>
        <q-btn
          type="submit"
          color="primary"
          unelevated
          no-caps
          label="Guardar cambios"
          :disable="!hayCambios"
          :loading="guardando"
        />
      </q-form>

      <section
        v-if="usuario.vehiculo"
        class="raite-tarjeta raite-pila"
        aria-labelledby="perfil-vehiculo"
      >
        <div class="row items-center justify-between no-wrap">
          <h2 id="perfil-vehiculo" class="raite-seccion">Tu vehículo</h2>
          <q-btn flat no-caps color="primary" icon="edit" label="Editar" to="/vehiculo" />
        </div>
        <p class="vehiculo">
          {{ usuario.vehiculo.marca }} {{ usuario.vehiculo.modelo }}
          {{ usuario.vehiculo.color.toLowerCase() }} · {{ usuario.vehiculo.asientos_disponibles }}
          {{ usuario.vehiculo.asientos_disponibles === 1 ? 'asiento' : 'asientos' }}
          <span class="raite-dato vehiculo__placas">{{ usuario.vehiculo.placas }}</span>
        </p>
      </section>

      <q-expansion-item
        class="raite-tarjeta reportes"
        icon="flag"
        label="Mis reportes"
        :caption="
          reportes === null
            ? undefined
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

      <q-btn
        outline
        color="primary"
        no-caps
        icon="logout"
        label="Cerrar sesión"
        :loading="saliendo"
        @click="salir"
      />
    </div>
  </q-page>
</template>

<script setup lang="ts">
// Perfil: datos editables (RF-07), vehículo, papel activo y reportes enviados (RF-12).
import { computed, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { comoLista, cuenta, reportes as apiReportes } from '@/api';
import { leerError } from '@/api/errores';
import type { Papel, Preferencia, Reporte } from '@/api/tipos';
import AvatarIniciales from '@/components/AvatarIniciales.vue';
import { useSesionStore } from '@/stores/sesion';
import { avisarError, avisarExito } from '@/utils/avisar';
import { calificacion, diaCorto } from '@/utils/formato';

definePage({ meta: { titulo: 'Perfil' } });

const router = useRouter();
const sesion = useSesionStore();
const usuario = computed(() => sesion.usuario);

const datos = reactive<{
  telefono: string;
  carrera: string;
  preferencia_compatibilidad: Preferencia;
}>({
  telefono: usuario.value?.telefono ?? '',
  carrera: usuario.value?.carrera ?? '',
  preferencia_compatibilidad: usuario.value?.preferencia_compatibilidad ?? 'MIXTO',
});
const errores = reactive<Record<string, string>>({});
const guardando = ref(false);
const saliendo = ref(false);
const reportes = ref<Reporte[] | null>(null);

const hayCambios = computed(
  () =>
    !!usuario.value &&
    (datos.telefono !== usuario.value.telefono ||
      datos.carrera.trim() !== usuario.value.carrera ||
      datos.preferencia_compatibilidad !== usuario.value.preferencia_compatibilidad),
);

async function guardar() {
  for (const clave of Object.keys(errores)) delete errores[clave];
  if (!/^\d{10}$/.test(datos.telefono)) errores.telefono = 'Escribe los 10 dígitos de tu teléfono.';
  if (!datos.carrera.trim()) errores.carrera = 'Escribe tu carrera.';
  if (Object.keys(errores).length) return;
  guardando.value = true;
  try {
    sesion.usuario = await cuenta.editarPerfil({ ...datos, carrera: datos.carrera.trim() });
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
.cabecera {
  display: flex;
  align-items: center;
  gap: 16px;
}
.cabecera__datos {
  flex-grow: 1;
  min-width: 0;
  p {
    margin: 0;
    overflow-wrap: anywhere;
  }
}
.cabecera__nombre {
  font-size: 1.125rem;
  font-weight: 700;
}
.cabecera__calif {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 1.125rem;
  font-weight: 700;
}
.ofrecer {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 16px;
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
.perfil__grupo {
  margin: 0;
  padding: 0;
  border: 0;
}
.vehiculo {
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px 12px;
}
.vehiculo__placas {
  font-weight: 600;
  letter-spacing: 0.08em;
}
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
