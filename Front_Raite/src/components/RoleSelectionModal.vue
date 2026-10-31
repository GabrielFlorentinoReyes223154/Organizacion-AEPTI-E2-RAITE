<template>
  <q-dialog v-model="show" persistent no-backdrop-dismiss no-esc-dismiss>
    <q-card style="min-width: 320px">
      <q-card-section class="text-center">
        <q-icon name="person" size="xl" color="primary" class="q-mb-sm" />
        <div class="text-h6">¿Cómo quieres entrar?</div>
        <div class="text-caption text-grey-7 q-mt-sm">
          Tu cuenta tiene ambos roles. Elige uno para continuar.
        </div>
      </q-card-section>

      <q-card-section class="q-pt-none q-gutter-sm flex flex-center">
        <q-btn
          label="Entrar como Pasajero"
          color="primary"
          size="lg"
          class="full-width"
          @click="select('pasajero')"
          :loading="loading"
        />
        <q-btn
          label="Entrar como Conductor"
          color="secondary"
          size="lg"
          class="full-width"
          @click="select('conductor')"
          :loading="loading"
        />
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

interface Props {
  modelValue: boolean;
}

interface Emits {
  (e: 'select', role: 'pasajero' | 'conductor'): void;
  (e: 'update:modelValue', value: boolean): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const loading = ref(false);

const show = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
});

const select = (role: 'pasajero' | 'conductor') => {
  loading.value = true;
  emit('select', role);
};
</script>