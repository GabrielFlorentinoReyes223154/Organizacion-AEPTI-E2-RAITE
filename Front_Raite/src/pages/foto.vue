<template>
  <q-page v-if="usuario" class="raite-contenedor foto">
    <section class="foto__tarjeta raite-tarjeta" aria-labelledby="foto-titulo">
      <span class="foto__paso">Último paso · Opcional</span>
      <h2 id="foto-titulo" class="foto__titulo">Agrega una foto de perfil</h2>
      <p class="foto__texto">
        Ayuda a que tus compañeros te reconozcan cuando se encuentren para el raite. Solo la ven
        alumnos con sesión en Raite. Puedes agregarla o cambiarla después desde tu perfil.
      </p>

      <AvatarIniciales
        :nombre="usuario.nombre_completo"
        :foto="usuario.foto"
        :tam="160"
        class="foto__avatar"
      />

      <div class="foto__elegir">
        <q-btn
          outline
          color="primary"
          no-caps
          icon="photo_camera"
          :label="usuario.foto ? 'Cambiar foto' : 'Elegir foto'"
          :disable="subiendoFoto"
          @click="elegirFoto"
        />
        <q-btn
          v-if="usuario.foto"
          flat
          no-caps
          color="negative"
          label="Quitar"
          :disable="subiendoFoto"
          @click="quitarFoto"
        />
      </div>
      <p class="raite-ayuda">JPG, PNG o WebP de hasta 5 MB.</p>
      <input
        ref="entradaFoto"
        type="file"
        accept="image/jpeg,image/png,image/webp"
        class="foto__entrada"
        tabindex="-1"
        aria-hidden="true"
        @change="fotoElegida"
      />

      <div class="foto__acciones">
        <q-btn
          v-if="!usuario.foto"
          flat
          color="primary"
          no-caps
          label="Lo hago después"
          :disable="subiendoFoto"
          @click="terminar"
        />
        <q-btn
          color="primary"
          unelevated
          no-caps
          :label="usuario.foto ? 'Continuar' : 'Continuar sin foto'"
          :disable="subiendoFoto"
          class="raite-btn-xl foto__continuar"
          @click="terminar"
        />
      </div>
    </section>

    <RecortarFoto
      :archivo="archivoFoto"
      :guardando="subiendoFoto"
      @guardar="subirFoto"
      @cancelar="archivoFoto = null"
    />
  </q-page>
</template>

<script setup lang="ts">
// Último paso del registro (RF-01): foto de perfil opcional. Llega aquí desde /verificar
// (pasajero) o desde /vehiculo?bienvenida=1 (conductor); `siguiente` dice a dónde seguir.
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import AvatarIniciales from '@/components/AvatarIniciales.vue';
import RecortarFoto from '@/components/RecortarFoto.vue';
import { useSesionStore } from '@/stores/sesion';
import { useFotoPerfil } from '@/utils/foto-perfil';

definePage({ meta: { titulo: 'Tu foto' } });

const route = useRoute();
const router = useRouter();
const sesion = useSesionStore();
const usuario = computed(() => sesion.usuario);

const { entradaFoto, archivoFoto, subiendoFoto, elegirFoto, fotoElegida, subirFoto, quitarFoto } =
  useFotoPerfil();

// Solo rutas internas, para que `?siguiente=` no pueda mandar a otro sitio.
const siguiente = computed(() => {
  const valor = route.query.siguiente;
  return typeof valor === 'string' && valor.startsWith('/') && !valor.startsWith('//')
    ? valor
    : sesion.inicio;
});

async function terminar() {
  await router.replace(siguiente.value);
}
</script>

<style scoped lang="scss">
.foto {
  display: flex;
  justify-content: center;
}
.foto__tarjeta {
  width: 100%;
  max-width: 560px;
  padding: 32px 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 8px;
}
.foto__paso {
  padding: 4px 12px;
  border-radius: 999px;
  background: var(--raite-azul-tenue);
  color: var(--raite-azul);
  font-size: 0.875rem;
  font-weight: 700;
}
.foto__titulo {
  margin: 8px 0 0;
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1.3;
}
.foto__texto {
  margin: 0 0 16px;
  max-width: 44ch;
  font-size: 1rem;
  line-height: 1.5;
  color: var(--raite-gris);
}
.foto__avatar {
  margin-bottom: 12px;
  box-shadow:
    0 0 0 4px var(--raite-blanco),
    0 0 0 6px var(--raite-azul-niebla);
}
.foto__elegir {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}
.foto__entrada {
  display: none;
}
.foto__acciones {
  width: 100%;
  margin-top: 16px;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
}
.foto__continuar {
  min-width: 220px;
}
</style>
