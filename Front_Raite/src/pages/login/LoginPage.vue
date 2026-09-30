<template>
  <div class="full-height flex flex-center" style="max-width: 400px; margin: 0 auto">
    <div class="full-width" style="max-width: 400px">
      <h5 class="q-my-md text-center">Raite</h5>

      <img alt="Raite logo" src="~@/assets/raite.svg" style="width: 40vh; height: 40vh" />

      <q-card class="q-pa-md">
        <q-card-title class="text-h6 q-mb-md bg-primary text-white flex flex-center">
          Iniciar sesión
        </q-card-title>

        <q-card-section>
          <q-form @submit="onSubmit" ref="formRef">
            <q-input
              v-model="email"
              label="Correo electrónico"
              placeholder="email@example.com"
              filled
              class="q-mb-md"
              :rules="[required, isEmailValid]"
            >
              <template v-slot:prepend>
                <q-icon name="mdi-email" />
              </template>
            </q-input>

            <q-input
              v-model="password"
              label="Contraseña"
              placeholder="password"
              filled
              class="q-mb-md"
              :rules="[required, isPasswordValid]"
              type="password"
            >
              <template v-slot:prepend>
                <q-icon name="mdi-lock" />
              </template>
            </q-input>

            <div class="row q-mb-md">
              <q-checkbox v-model="rememberMeCheckbox" label="Recordarme" class="q-mt-mx col" />

              <q-btn
                label="¿No tienes una cuenta?"
                flat
                to="/login/signuppage"
                class="q-mt-mx col"
                no-caps
              />
            </div>

            <div class="row q-gutter-sm">
              <q-btn
                label="Iniciar sesión"
                type="submit"
                class="full-width col-3 q-mb-md"
                color="primary"
                :loading="loading"
                :disable="loading"
              />

              <q-btn label="¿Olvidaste tu contraseña?" class="full-width col-3" color="primary" />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth-store';
import { Notify } from 'quasar';
import isEmail from 'validator/lib/isEmail';
import isStrongPassword from 'validator/lib/isStrongPassword';

const authStore = useAuthStore();

const email = ref('');
const password = ref('');
const rememberMeCheckbox = ref(true);
const loading = ref(false);

const required = (val: string) => !!val || 'This field is required';
const isEmailValid = (val: string) => isEmail(val) || 'Invalid email format';
const isPasswordValid = (val: string) =>
  isStrongPassword(val, { minLowercase: 1, minUppercase: 1, minNumbers: 1, minSymbols: 1 }) ||
  'Password must be strong (e.g., 8+ chars, 1 uppercase, 1 lowercase, 1 number, 1 symbol)';

const onSubmit = async () => {
  loading.value = true;
  try {
    await authStore.login({ email: email.value, password: password.value });
    Notify.create({ type: 'positive', message: 'Bienvenido', position: 'top' });
  } catch (error: unknown) {
    const err = error as { response?: { data?: { detail?: string } }; message?: string };
    const message = err.response?.data?.detail || err.message || 'Credenciales inválidas';
    Notify.create({ type: 'negative', message, position: 'top' });
  } finally {
    loading.value = false;
  }
};
</script>
