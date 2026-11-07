<template>
  <q-page class="raite-contenedor raite-contenedor--formulario">
    <q-form class="raite-pila raite-pila--grupos" novalidate @submit="enviar">
      <q-banner v-if="bienvenida" class="bg-azul-tenue text-negro rounded-borders">
        <template #avatar
          ><q-icon name="directions_car" color="primary" aria-hidden="true"
        /></template>
        Último paso para dar raite: los datos de tu auto. Las placas solo las ve quien confirme un
        raite contigo.
      </q-banner>
      <q-banner
        v-else-if="!editando && sesion.usuario?.rol === Rol.PASAJERO"
        class="bg-azul-tenue text-negro rounded-borders"
      >
        <template #avatar
          ><q-icon name="directions_car" color="primary" aria-hidden="true"
        /></template>
        Al registrar tu vehículo podrás pedir raite y también ofrecerlo. Cambias entre las dos cosas
        arriba, en el encabezado.
      </q-banner>

      <div class="vehiculo__fila">
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
      </div>

      <div class="vehiculo__fila">
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
        <q-btn-toggle
          v-model="datos.tipo"
          class="raite-opciones"
          no-caps
          unelevated
          toggle-color="primary"
          :disable="editando"
          :options="[
            { label: 'Coche', value: 'COCHE' },
            { label: 'Camioneta', value: 'CAMIONETA' },
            { label: 'Troca', value: 'TROCA' },
          ]"
        />
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
        <p class="raite-ayuda q-mt-sm">Sin contarte a ti. En cada viaje decides cuántos ofreces.</p>
        <p v-if="errores.asientos_disponibles" class="vehiculo__error" role="alert">
          {{ errores.asientos_disponibles }}
        </p>
      </fieldset>

      <q-banner v-if="mensaje" class="bg-rojo-tenue text-rojo-texto rounded-borders" role="alert">
        <template #avatar><q-icon name="error_outline" aria-hidden="true" /></template>
        {{ mensaje }}
      </q-banner>

      <div class="raite-pila">
        <q-btn
          type="submit"
          color="primary"
          unelevated
          no-caps
          :label="editando ? 'Guardar cambios' : 'Registrar vehículo'"
          :loading="enviando"
          class="full-width"
        />
        <q-btn
          v-if="bienvenida"
          flat
          color="primary"
          no-caps
          label="Lo hago después"
          :to="sesion.inicio"
        />
      </div>
    </q-form>
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
.vehiculo__fila {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
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
</style>
