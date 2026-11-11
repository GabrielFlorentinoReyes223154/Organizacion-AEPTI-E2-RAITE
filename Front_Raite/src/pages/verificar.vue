<template>
  <q-form class="raite-pila raite-pila--grupos" novalidate @submit="enviar">
    <div class="verificar__cabecera">
      <span class="verificar__icono" aria-hidden="true">
        <q-icon name="mark_email_unread" size="28px" />
      </span>
      <h1 class="raite-titulo raite-titulo--marca verificar__titulo">Revisa tu correo</h1>
      <p class="verificar__texto">
        Te mandamos un código de 6 dígitos a <strong class="text-negro">{{ correo }}</strong
        >. Vence en 15 minutos. Tu cuenta se crea al confirmarlo.
      </p>
    </div>

    <div>
      <label for="ver-codigo" class="raite-etiqueta">Código</label>
      <q-input
        hide-bottom-space
        for="ver-codigo"
        v-model="codigo"
        outlined
        mask="######"
        inputmode="numeric"
        autocomplete="one-time-code"
        input-class="verificar__codigo raite-dato"
        :error="!!errorCodigo"
        :error-message="errorCodigo"
        autofocus
      />
    </div>

    <q-btn
      type="submit"
      color="primary"
      unelevated
      no-caps
      label="Verificar y entrar"
      :loading="enviando"
      class="full-width raite-btn-xl"
    />

    <div class="verificar__reenviar">
      <q-btn
        outline
        color="primary"
        no-caps
        :label="espera > 0 ? `Reenviar código en ${espera} s` : 'Reenviar código'"
        :disable="espera > 0"
        :loading="reenviando"
        @click="reenviar"
      />
      <p class="raite-ayuda">¿No llega? Revisa la carpeta de correo no deseado.</p>
    </div>

    <p class="raite-ayuda text-center">
      <router-link to="/registro" class="text-weight-bold">Volver al registro</router-link>
    </p>
  </q-form>
</template>

<script setup lang="ts">
// Verificación del correo con el código de 6 dígitos (RF-01, regla 5).
import { onBeforeUnmount, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { cuenta } from '@/api';
import { leerError } from '@/api/errores';
import { useSesionStore } from '@/stores/sesion';
import { avisarError, avisarExito } from '@/utils/avisar';
import {
  guardarRegistroPendiente,
  leerRegistroPendiente,
  olvidarRegistroPendiente,
} from '@/utils/registro-pendiente';

definePage({ meta: { publico: true, titulo: 'Verificar correo' } });

const ESPERA_SEGUNDOS = 60;

const route = useRoute();
const router = useRouter();
const sesion = useSesionStore();

const correo = typeof route.query.correo === 'string' ? route.query.correo : '';
const token = ref(leerRegistroPendiente());
const codigo = ref('');
const errorCodigo = ref('');
const enviando = ref(false);
const reenviando = ref(false);
const espera = ref(ESPERA_SEGUNDOS);

// Sin registro en curso (otra pestaña, o ya venció) no hay nada que verificar.
if (!token.value) void router.replace('/registro');

const reloj = setInterval(() => {
  if (espera.value > 0) espera.value -= 1;
}, 1000);
onBeforeUnmount(() => clearInterval(reloj));

async function enviar() {
  errorCodigo.value = '';
  if (!/^\d{6}$/.test(codigo.value)) {
    errorCodigo.value = 'El código tiene 6 dígitos.';
    return;
  }
  enviando.value = true;
  try {
    await sesion.verificar(token.value ?? '', codigo.value);
    avisarExito(`¡Listo, ${sesion.usuario?.nombre ?? ''}! Tu cuenta está activa.`);
    const necesitaVehiculo = sesion.usuario?.es_conductor && !sesion.usuario.vehiculo;
    await router.replace(
      necesitaVehiculo ? { path: '/vehiculo', query: { bienvenida: '1' } } : sesion.inicio,
    );
  } catch (error) {
    const legible = leerError(error);
    if (legible.status === 409) {
      olvidarRegistroPendiente();
      avisarExito(legible.mensaje);
      await router.replace({ path: '/entrar', query: { correo } });
      return;
    }
    errorCodigo.value = legible.campos.codigo ?? legible.mensaje;
  } finally {
    enviando.value = false;
  }
}

async function reenviar() {
  reenviando.value = true;
  try {
    const respuesta = await cuenta.reenviarCodigo(token.value ?? '');
    token.value = respuesta.token;
    guardarRegistroPendiente(respuesta.token);
    avisarExito(respuesta.detail);
    espera.value = ESPERA_SEGUNDOS;
  } catch (error) {
    avisarError(error);
  } finally {
    reenviando.value = false;
  }
}
</script>

<style scoped lang="scss">
.verificar__cabecera {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.verificar__icono {
  width: 56px;
  height: 56px;
  margin-bottom: 16px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--raite-azul-tenue);
  color: var(--raite-azul);
}
.verificar__titulo {
  margin-bottom: 4px;
}
.verificar__texto {
  margin: 0;
  font-size: 1rem;
  line-height: 1.5;
  color: var(--raite-gris);
}
:deep(.verificar__codigo) {
  font-size: 1.75rem;
  font-weight: 600;
  letter-spacing: 0.3em;
  text-align: center;
}
.verificar__reenviar {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}
</style>
