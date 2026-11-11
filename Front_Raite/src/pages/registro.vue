<template>
  <q-form class="registro raite-pila raite-pila--grupos" novalidate @submit="enviar">
    <div>
      <h1 class="raite-titulo raite-titulo--marca registro__titulo">Crea tu cuenta</h1>
      <p class="registro__subtitulo">
        Solo para alumnos de la UACJ. Te mandaremos un código a tu correo institucional.
      </p>
    </div>

    <section class="registro__seccion" aria-labelledby="reg-sec-datos">
      <h2 id="reg-sec-datos" class="registro__encabezado">
        <span class="registro__numero" aria-hidden="true">1</span>
        Tus datos
      </h2>
      <div class="registro__rejilla">
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
        <div>
          <label for="reg-password2" class="raite-etiqueta">Confirma tu contraseña</label>
          <q-input
            for="reg-password2"
            v-model="confirmarPassword"
            outlined
            :type="verPassword ? 'text' : 'password'"
            autocomplete="new-password"
            hint="Escríbela otra vez"
            v-bind="campo('confirmarPassword')"
          >
            <template #append>
              <q-btn
                flat
                round
                :icon="verPassword ? 'visibility_off' : 'visibility'"
                :aria-label="verPassword ? 'Ocultar contraseñas' : 'Mostrar contraseñas'"
                @click="verPassword = !verPassword"
              />
            </template>
          </q-input>
        </div>
        <div class="registro__edad">
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
        <SelectorCarrera
          v-model="datos.carrera"
          class="registro__completo"
          :error="errores.carrera ?? ''"
        />
      </div>
    </section>

    <section class="registro__seccion" aria-labelledby="reg-sec-viaje">
      <h2 id="reg-sec-viaje" class="registro__encabezado">
        <span class="registro__numero" aria-hidden="true">2</span>
        Cómo vas a viajar
      </h2>
      <div class="registro__rejilla">
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
            Con "mismo sexo" solo verás y compartirás raites donde todos tengan el mismo sexo que
            tú. Lo puedes cambiar después.
          </p>
        </fieldset>

        <fieldset class="registro__grupo registro__completo">
          <legend class="raite-etiqueta">¿Cómo usarás Raite?</legend>
          <div class="registro__roles">
            <button
              v-for="opcion in roles"
              :key="opcion.valor"
              type="button"
              class="registro__rol"
              :aria-pressed="datos.rol === opcion.valor"
              @click="datos.rol = opcion.valor"
            >
              <span class="registro__rol-icono" aria-hidden="true">
                <q-icon :name="opcion.icono" size="22px" />
              </span>
              <span class="registro__rol-texto">
                <span class="registro__rol-nombre">{{ opcion.nombre }}</span>
                <span class="registro__rol-detalle">{{ opcion.detalle }}</span>
              </span>
            </button>
          </div>
          <p class="raite-ayuda q-mt-sm">{{ ayudaRol }}</p>
        </fieldset>
      </div>
    </section>

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
      class="full-width raite-btn-xl"
    />

    <div class="registro__division">¿Ya tienes cuenta?</div>
    <q-btn outline color="primary" no-caps label="Entrar" to="/entrar" class="full-width" />
  </q-form>
</template>

<script setup lang="ts">
// Registro con correo institucional (RF-01). Después se verifica el código y, si da raite, el vehículo.
import { computed, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import isEmail from 'validator/lib/isEmail';
import { leerError } from '@/api/errores';
import { Rol, type DatosRegistro } from '@/api/tipos';
import SelectorCarrera from '@/components/SelectorCarrera.vue';
import { useSesionStore } from '@/stores/sesion';

definePage({ meta: { publico: true, titulo: 'Crear cuenta', amplio: true } });

const router = useRouter();
const sesion = useSesionStore();

interface FormRegistro extends Omit<DatosRegistro, 'edad' | 'sexo' | 'carrera'> {
  edad: number | null;
  carrera: number | null;
  sexo: DatosRegistro['sexo'] | null;
}

const datos = reactive<FormRegistro>({
  nombre: '',
  apellidos: '',
  correo: '',
  password: '',
  telefono: '',
  edad: null,
  carrera: null,
  sexo: null,
  preferencia_compatibilidad: 'MIXTO',
  rol: Rol.PASAJERO,
});
const errores = reactive<Record<string, string>>({});
const mensaje = ref('');
const enviando = ref(false);
const verPassword = ref(false);
// Solo se compara en el navegador; no se manda al API.
const confirmarPassword = ref('');

const ayudaRol = computed(() =>
  datos.rol === Rol.PASAJERO
    ? 'Buscarás raites. Si después quieres ofrecerlos, registras tu vehículo desde tu perfil.'
    : 'Después del código te pediremos los datos de tu vehículo.',
);

// Papel con el que se registra: se nombra por lo que haces, no por género.
const roles = [
  {
    valor: Rol.PASAJERO,
    nombre: 'Pido raite',
    detalle: 'Busco quién me lleve a mi campus.',
    icono: 'hail',
  },
  {
    valor: Rol.CONDUCTOR,
    nombre: 'Doy raite',
    detalle: 'Tengo auto y me sobran lugares.',
    icono: 'directions_car',
  },
  {
    valor: Rol.AMBOS,
    nombre: 'Las dos',
    detalle: 'Según el día, pido u ofrezco.',
    icono: 'sync_alt',
  },
];

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
  if (!confirmarPassword.value) errores.confirmarPassword = 'Vuelve a escribir tu contraseña.';
  else if (confirmarPassword.value !== datos.password)
    errores.confirmarPassword = 'Las contraseñas no coinciden.';
  if (!/^\d{10}$/.test(datos.telefono)) errores.telefono = 'Escribe los 10 dígitos de tu teléfono.';
  if (!datos.edad || datos.edad < 17 || datos.edad > 70) errores.edad = 'Entre 17 y 70 años.';
  if (!datos.carrera) errores.carrera = 'Elige tu campus y tu carrera.';
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
      carrera: datos.carrera ?? 0,
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
.registro__titulo {
  margin-bottom: 4px;
}
.registro__subtitulo {
  margin: 0;
  font-size: 1rem;
  color: var(--raite-gris);
}
.registro__seccion {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.registro__encabezado {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.125rem;
  font-weight: 700;
  line-height: 1.3;
}
.registro__numero {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--raite-azul-tenue);
  color: var(--raite-azul);
  font-size: 0.875rem;
  font-weight: 700;
}
// Una columna en celular; dos en pantallas anchas (la tarjeta de registro mide hasta 820 px).
.registro__rejilla {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 20px 16px;
  @media (min-width: 1024px) {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
.registro__edad {
  max-width: 160px;
}
.registro__completo {
  grid-column: 1 / -1;
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

// Papel: tres opciones con ícono y explicación.
.registro__roles {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 12px;
  @media (min-width: 1024px) {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
.registro__rol {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
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
    .registro__rol-nombre {
      color: var(--raite-azul);
    }
    .registro__rol-icono {
      background: var(--raite-azul);
      color: var(--raite-blanco);
    }
  }
}
.registro__rol-icono {
  flex: none;
  width: 40px;
  height: 40px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--raite-azul-tenue);
  color: var(--raite-azul);
}
.registro__rol-texto {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.registro__rol-nombre {
  font-size: 1rem;
  font-weight: 700;
}
.registro__rol-detalle {
  font-size: 0.875rem;
  line-height: 1.35;
  color: var(--raite-gris);
}

.registro__division {
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
