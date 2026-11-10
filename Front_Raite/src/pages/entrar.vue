<template>
  <q-form class="raite-pila raite-pila--grupos" novalidate @submit="enviar">
    <div>
      <h1 class="raite-titulo raite-titulo--marca entrar__titulo">¡Qué onda!</h1>
      <p class="entrar__subtitulo">Entra con tu correo institucional.</p>
    </div>

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
      class="full-width raite-btn-xl q-mt-sm"
    />

    <div class="entrar__division">¿Primera vez?</div>

    <q-btn
      outline
      color="primary"
      no-caps
      label="Crea tu cuenta"
      to="/registro"
      class="full-width"
    />
  </q-form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
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

<style scoped lang="scss">
.entrar__titulo {
  margin-bottom: 4px;
}
.entrar__subtitulo {
  margin: 0;
  font-size: 1rem;
  color: var(--raite-gris);
}
.entrar__division {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.875rem;
  color: var(--raite-gris);
  &::before,
  &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--raite-borde-sutil);
  }
}
</style>
