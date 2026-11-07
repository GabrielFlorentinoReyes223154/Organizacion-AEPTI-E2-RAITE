<template>
  <q-form class="raite-pila raite-pila--grupos" novalidate @submit="enviar">
    <h1 class="raite-titulo q-mb-none">Entrar</h1>

    <div>
      <label for="entrar-correo" class="raite-etiqueta">Correo institucional</label>
      <q-input
        hide-bottom-space
        for="entrar-correo"
        v-model="correo"
        outlined
        type="email"
        autocomplete="username"
        inputmode="email"
        placeholder="tu.matricula@alumnos.uacj.mx"
        :error="!!errores.correo"
        :error-message="errores.correo"
      />
    </div>

    <div>
      <label for="entrar-password" class="raite-etiqueta">Contraseña</label>
      <q-input
        hide-bottom-space
        for="entrar-password"
        v-model="password"
        outlined
        :type="verPassword ? 'text' : 'password'"
        autocomplete="current-password"
        :error="!!errores.password"
        :error-message="errores.password"
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

    <q-banner v-if="mensaje" class="bg-rojo-tenue text-rojo-texto rounded-borders" role="alert">
      <template #avatar><q-icon name="error_outline" aria-hidden="true" /></template>
      {{ mensaje }}
    </q-banner>

    <q-btn
      type="submit"
      color="primary"
      unelevated
      no-caps
      label="Entrar"
      :loading="enviando"
      class="full-width"
    />

    <p class="raite-ayuda text-center">
      ¿Aún no tienes cuenta?
      <router-link to="/registro" class="text-weight-bold"
        >Regístrate con tu correo de la UACJ</router-link
      >
    </p>
  </q-form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { cuenta } from '@/api';
import { leerError } from '@/api/errores';
import { useSesionStore } from '@/stores/sesion';

definePage({ meta: { publico: true, titulo: 'Entrar' } });

const route = useRoute();
const router = useRouter();
const sesion = useSesionStore();

const correo = ref(typeof route.query.correo === 'string' ? route.query.correo : '');
const password = ref('');
const verPassword = ref(false);
const enviando = ref(false);
const mensaje = ref('');
const errores = reactive<Record<string, string>>({});

function validar() {
  errores.correo = correo.value.trim() ? '' : 'Escribe tu correo institucional.';
  errores.password = password.value ? '' : 'Escribe tu contraseña.';
  return !errores.correo && !errores.password;
}

async function enviar() {
  mensaje.value = '';
  if (!validar()) return;
  enviando.value = true;
  try {
    await sesion.entrar(correo.value, password.value);
    const siguiente =
      typeof route.query.siguiente === 'string' ? route.query.siguiente : sesion.inicio;
    await router.replace(siguiente);
  } catch (error) {
    const legible = leerError(error);
    if (legible.codigo === 'correo_no_verificado') {
      // Se manda un código nuevo; si se pidió uno hace menos de 60 s, el que ya llegó sigue sirviendo.
      await cuenta.reenviarCodigo(correo.value).catch(() => undefined);
      await router.push({
        path: '/verificar',
        query: { correo: correo.value.trim().toLowerCase() },
      });
      return;
    }
    mensaje.value =
      legible.status === 401
        ? 'El correo o la contraseña no coinciden. Revísalos e inténtalo de nuevo.'
        : legible.mensaje;
    Object.assign(errores, legible.campos);
  } finally {
    enviando.value = false;
  }
}
</script>
