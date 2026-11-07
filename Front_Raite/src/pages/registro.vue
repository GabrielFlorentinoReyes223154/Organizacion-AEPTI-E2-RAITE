<template>
  <q-form class="raite-pila raite-pila--grupos" novalidate @submit="enviar">
    <div>
      <h1 class="raite-titulo q-mb-sm">Crea tu cuenta</h1>
      <p class="raite-ayuda">
        Solo para alumnos de la UACJ. Te mandaremos un código a tu correo institucional.
      </p>
    </div>

    <div class="registro__fila">
      <div>
        <label for="reg-nombre" class="raite-etiqueta">Nombre</label>
        <q-input
          for="reg-nombre"
          v-model="datos.nombre"
          outlined
          autocomplete="given-name"
          maxlength="80"
          v-bind="campo('nombre')"
        />
      </div>
      <div>
        <label for="reg-apellidos" class="raite-etiqueta">Apellidos</label>
        <q-input
          for="reg-apellidos"
          v-model="datos.apellidos"
          outlined
          autocomplete="family-name"
          maxlength="80"
          v-bind="campo('apellidos')"
        />
      </div>
    </div>

    <div>
      <label for="reg-correo" class="raite-etiqueta">Correo institucional</label>
      <q-input
        for="reg-correo"
        v-model="datos.correo"
        outlined
        type="email"
        inputmode="email"
        autocomplete="email"
        placeholder="tu.matricula@alumnos.uacj.mx"
        hint="Termina en @alumnos.uacj.mx"
        v-bind="campo('correo')"
      />
    </div>

    <div>
      <label for="reg-password" class="raite-etiqueta">Contraseña</label>
      <q-input
        for="reg-password"
        v-model="datos.password"
        outlined
        :type="verPassword ? 'text' : 'password'"
        autocomplete="new-password"
        hint="Mínimo 8 caracteres"
        v-bind="campo('password')"
      >
        <template #append>
          <q-btn
            flat
            round
            :icon="verPassword ? 'visibility_off' : 'visibility'"
            :aria-label="verPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
            @click="verPassword = !verPassword"
          />
        </template>
      </q-input>
    </div>

    <div class="registro__fila">
      <div>
        <label for="reg-telefono" class="raite-etiqueta">Teléfono o WhatsApp</label>
        <q-input
          for="reg-telefono"
          v-model="datos.telefono"
          outlined
          type="tel"
          inputmode="tel"
          autocomplete="tel-national"
          mask="### ### ####"
          unmasked-value
          input-class="raite-dato"
          hint="Solo lo ve quien confirme un raite contigo"
          v-bind="campo('telefono')"
        />
      </div>
      <div>
        <label for="reg-edad" class="raite-etiqueta">Edad</label>
        <q-input
          for="reg-edad"
          v-model.number="datos.edad"
          outlined
          type="number"
          inputmode="numeric"
          min="17"
          max="70"
          v-bind="campo('edad')"
        />
      </div>
    </div>

    <div>
      <label for="reg-carrera" class="raite-etiqueta">Carrera</label>
      <q-input
        for="reg-carrera"
        v-model="datos.carrera"
        outlined
        maxlength="120"
        placeholder="Ej. Ingeniería Industrial"
        v-bind="campo('carrera')"
      />
    </div>

    <fieldset class="registro__grupo">
      <legend class="raite-etiqueta">Sexo</legend>
      <q-btn-toggle
        v-model="datos.sexo"
        class="raite-opciones"
        no-caps
        unelevated
        toggle-color="primary"
        :options="[
          { label: 'Femenino', value: 'F' },
          { label: 'Masculino', value: 'M' },
          { label: 'Otro', value: 'X' },
        ]"
      />
      <p v-if="errores.sexo" class="registro__error" role="alert">{{ errores.sexo }}</p>
    </fieldset>

    <fieldset class="registro__grupo">
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
        Con "mismo sexo" solo verás y compartirás raites donde todos tengan el mismo sexo que tú. Lo
        puedes cambiar después.
      </p>
    </fieldset>

    <fieldset class="registro__grupo">
      <legend class="raite-etiqueta">¿Cómo usarás Raite?</legend>
      <q-btn-toggle
        v-model="datos.rol"
        class="raite-opciones raite-opciones--envolver"
        no-caps
        unelevated
        toggle-color="primary"
        :options="[
          { label: 'Pido raite', value: Rol.PASAJERO },
          { label: 'Doy raite', value: Rol.CONDUCTOR },
          { label: 'Las dos', value: Rol.AMBOS },
        ]"
      />
      <p class="raite-ayuda q-mt-sm">{{ ayudaRol }}</p>
    </fieldset>

    <q-banner v-if="mensaje" class="bg-rojo-tenue text-rojo-texto rounded-borders" role="alert">
      <template #avatar><q-icon name="error_outline" aria-hidden="true" /></template>
      {{ mensaje }}
    </q-banner>

    <q-btn
      type="submit"
      color="primary"
      unelevated
      no-caps
      label="Crear cuenta"
      :loading="enviando"
      class="full-width"
    />

    <p class="raite-ayuda text-center">
      ¿Ya tienes cuenta? <router-link to="/entrar" class="text-weight-bold">Entra aquí</router-link>
    </p>
  </q-form>
</template>

<script setup lang="ts">
// Registro con correo institucional (RF-01). Después se verifica el código y, si da raite, el vehículo.
import { computed, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import isEmail from 'validator/lib/isEmail';
import { leerError } from '@/api/errores';
import { Rol, type DatosRegistro } from '@/api/tipos';
import { useSesionStore } from '@/stores/sesion';

definePage({ meta: { publico: true, titulo: 'Crear cuenta' } });

const router = useRouter();
const sesion = useSesionStore();

interface FormRegistro extends Omit<DatosRegistro, 'edad' | 'sexo'> {
  edad: number | null;
  sexo: DatosRegistro['sexo'] | null;
}

const datos = reactive<FormRegistro>({
  nombre: '',
  apellidos: '',
  correo: '',
  password: '',
  telefono: '',
  edad: null,
  carrera: '',
  sexo: null,
  preferencia_compatibilidad: 'MIXTO',
  rol: Rol.PASAJERO,
});
const errores = reactive<Record<string, string>>({});
const mensaje = ref('');
const enviando = ref(false);
const verPassword = ref(false);

const ayudaRol = computed(() =>
  datos.rol === Rol.PASAJERO
    ? 'Buscarás raites. Si después quieres ofrecerlos, registras tu vehículo desde tu perfil.'
    : 'Después del código te pediremos los datos de tu vehículo.',
);

function campo(nombre: string) {
  return { error: !!errores[nombre], errorMessage: errores[nombre] ?? '', hideBottomSpace: true };
}

function validar(): boolean {
  for (const clave of Object.keys(errores)) delete errores[clave];
  const correo = datos.correo.trim().toLowerCase();
  if (!datos.nombre.trim()) errores.nombre = 'Escribe tu nombre.';
  if (!datos.apellidos.trim()) errores.apellidos = 'Escribe tus apellidos.';
  if (!isEmail(correo)) errores.correo = 'Escribe un correo válido.';
  else if (!correo.endsWith('@alumnos.uacj.mx')) errores.correo = 'Usa tu correo @alumnos.uacj.mx.';
  if (datos.password.length < 8) errores.password = 'Usa al menos 8 caracteres.';
  if (!/^\d{10}$/.test(datos.telefono)) errores.telefono = 'Escribe los 10 dígitos de tu teléfono.';
  if (!datos.edad || datos.edad < 17 || datos.edad > 70) errores.edad = 'Entre 17 y 70 años.';
  if (!datos.carrera.trim()) errores.carrera = 'Escribe tu carrera.';
  if (!datos.sexo) errores.sexo = 'Elige una opción.';
  return Object.keys(errores).length === 0;
}

async function enviar() {
  mensaje.value = '';
  if (!validar()) {
    mensaje.value = 'Revisa los datos marcados.';
    return;
  }
  enviando.value = true;
  try {
    await sesion.registrar({
      ...datos,
      nombre: datos.nombre.trim(),
      apellidos: datos.apellidos.trim(),
      carrera: datos.carrera.trim(),
      edad: datos.edad ?? 0,
      sexo: datos.sexo ?? 'X',
    });
    await router.push({
      path: '/verificar',
      query: { correo: datos.correo.trim().toLowerCase(), nuevo: '1' },
    });
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
.registro__fila {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 24px 16px;
  @media (min-width: 440px) {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
.registro__grupo {
  margin: 0;
  padding: 0;
  border: 0;
  min-width: 0;
}
.registro__error {
  margin: 8px 0 0;
  font-size: 0.875rem;
  color: var(--raite-rojo-texto);
}
</style>
