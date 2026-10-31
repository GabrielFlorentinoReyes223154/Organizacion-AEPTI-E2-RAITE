<template>
  <div class="full-height flex flex-center" style="max-width: 400px; margin: 0 auto">
    <div class="full-width" style="max-width: 400px">
      <h5 class="q-my-md text-center">Crear cuenta</h5>

      <q-card class="q-pa-md">
        <q-card-section>
          <q-form @submit="onSubmit" ref="formRef">
            <q-input
              v-model="nombre"
              label="Nombre"
              placeholder="Nombre"
              filled
              class="q-mt-md"
              :rules="[required]"
            >
              <template v-slot:prepend>
                <q-icon name="mdi-account" />
              </template>
            </q-input>

            <q-input
              v-model="apellidos"
              label="Apellidos"
              placeholder="Apellidos"
              filled
              class="q-mt-md"
              :rules="[required]"
            >
              <template v-slot:prepend>
                <q-icon name="mdi-account" />
              </template>
            </q-input>

            <q-input
              v-model="email"
              label="Correo electrónico"
              placeholder="email@example.com"
              filled
              class="q-mt-md"
              :rules="[required, isEmailValid]"
            >
              <template v-slot:prepend>
                <q-icon name="mdi-email" />
              </template>
            </q-input>

            <q-input
              v-model="password"
              label="Contraseña"
              type="password"
              filled
              class="q-mt-md"
              :rules="[required, isPasswordValid]"
            >
              <template v-slot:prepend>
                <q-icon name="mdi-lock" />
              </template>
            </q-input>

            <q-input
              v-model="confirmPassword"
              label="Confirmar contraseña"
              type="password"
              filled
              class="q-mt-md"
              :rules="[required, doPasswordsMatch]"
            >
              <template v-slot:prepend>
                <q-icon name="mdi-lock" />
              </template>
            </q-input>

            <div class="row q-mt-md q-gutter-sm">
              <q-input
                v-model="edad"
                label="Edad"
                type="number"
                filled
                class="col"
                :rules="[required, isEdadValid]"
              />
              <q-select
                v-model="sexo"
                label="Sexo"
                filled
                class="col"
                :options="sexoOptions"
                :rules="[required]"
                emit-value
                map-options
              />
            </div>

            <q-input
              v-model="carrera"
              label="Carrera"
              placeholder="Ingeniería, Medicina, etc."
              filled
              class="q-mt-md"
              :rules="[required]"
            >
              <template v-slot:prepend>
                <q-icon name="mdi-school" />
              </template>
            </q-input>

            <q-select
              v-model="rol"
              label="Rol"
              filled
              class="q-mt-md"
              :options="rolOptions"
              :rules="[required]"
              emit-value
              map-options
            />

            <div class="q-mt-sm q-ml-md">
              <q-icon
                :name="hasMinLength ? 'check' : 'close'"
                :color="hasMinLength ? 'green' : 'red'"
              />
              Al menos 8 caracteres

              <br />

              <q-icon
                :name="hasLowercase ? 'check' : 'close'"
                :color="hasLowercase ? 'green' : 'red'"
              />
              Al menos 1 minúscula

              <br />

              <q-icon
                :name="hasUppercase ? 'check' : 'close'"
                :color="hasUppercase ? 'green' : 'red'"
              />
              Al menos 1 mayúscula

              <br />

              <q-icon :name="hasNumber ? 'check' : 'close'" :color="hasNumber ? 'green' : 'red'" />
              Al menos 1 número

              <br />

              <q-icon :name="hasSymbol ? 'check' : 'close'" :color="hasSymbol ? 'green' : 'red'" />
              Al menos 1 símbolo (e.g. !@#$)
            </div>

            <div class="text-center q-mt-md">
<q-btn
              label="¿Ya tienes una cuenta? Inicia sesión"
              flat
              to="/login/LoginPage"
              no-caps
              color="primary"
            />
            </div>

            <div class="row">
              <q-btn
                label="Crear cuenta"
                type="submit"
                class="full-width"
                color="positive"
                :disable="!isPasswordValid || loading"
                :loading="loading"
              />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useAuthStore } from '@/stores/auth-store';
import { Router } from '@/router';
import { Notify } from 'quasar';
import isEmail from 'validator/lib/isEmail';

const authStore = useAuthStore();

const formRef = ref<HTMLElement>();

const nombre = ref('');
const apellidos = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const edad = ref<number | null>(null);
const sexo = ref('');
const carrera = ref('');
const rol = ref<number | null>(null);
const loading = ref(false);

const rolOptions = [
  { label: 'Pasajero', value: 2 },
  { label: 'Conductor', value: 3 },
  { label: 'Ambos (Pasajero y Conductor)', value: 4 },
];

const sexoOptions = [
  { label: 'Masculino', value: 'M' },
  { label: 'Femenino', value: 'F' },
  { label: 'Otro', value: 'X' },
];

const required = (val: string) => !!val || 'Este campo es obligatorio';

const isEmailValid = (val: string) => isEmail(val) || 'Formato de correo inválido';

const isEdadValid = (val: number | null) => {
  if (val === null || val === undefined) return 'Edad requerida';
  if (val < 17 || val > 70) return 'Edad debe ser entre 17 y 70';
  return true;
};

const doPasswordsMatch = (val: string) => val === password.value || 'Las contraseñas no coinciden';

const hasMinLength = computed(() => password.value.length >= 8);
const hasLowercase = computed(() => /[a-z]/.test(password.value));
const hasUppercase = computed(() => /[A-Z]/.test(password.value));
const hasNumber = computed(() => /[0-9]/.test(password.value));
const hasSymbol = computed(() => /[^A-Za-z0-9]/.test(password.value));

const isPasswordValid = (val: string) => val.length >= 8 || 'Contraseña debe tener al menos 8 caracteres';

// const validRoles = (val: string[]) => {
//   if (!val || val.length === 0) return 'Selecciona al menos un rol';
//   if (val.length > 2) return 'Máximo 2 roles';
//   if (new Set(val).size !== val.length) return 'No repitas roles';
//   if (val.includes('ADMIN')) return 'El rol ADMIN no se otorga en el registro público';
//   return true;
// };

const onSubmit = async () => {
  if (!formRef.value) return;
  const form = formRef.value as unknown as { validate: () => boolean; reset: () => void };
  if (!form.validate()) return;

  loading.value = true;
  try {
    await authStore.register({
      nombre: nombre.value,
      apellidos: apellidos.value,
      correo: email.value.toLowerCase(),
      password: password.value,
      edad: edad.value!,
      sexo: sexo.value,
      carrera: carrera.value,
      rol: rol.value!,
    });
    form.reset();
    Notify.create({ type: 'positive', message: 'Cuenta creada satisfactoriamente', position: 'top' });
    await new Promise(r => setTimeout(r, 500));
    try {
      await Router.replace({ path: '/login/LoginPage' });
    } catch {
      window.location.href = '/login/LoginPage';
    }
  } catch (error: unknown) {
    console.error('Error in onSubmit:', error);
    const err = error as { response?: { data?: { detail?: string } }; message?: string };
    const message = err.response?.data?.detail || err.message || 'Error al crear cuenta';
    Notify.create({ type: 'negative', message, position: 'top' });
  } finally {
    loading.value = false;
  }
};
</script>