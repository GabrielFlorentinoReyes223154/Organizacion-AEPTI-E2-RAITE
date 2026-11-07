<template>
  <span class="chip-estado" :class="`chip-estado--${clave}`">
    <q-icon :name="info.icono" size="16px" aria-hidden="true" />
    {{ info.texto }}
  </span>
</template>

<script setup lang="ts">
// Chips de estado de DESIGN.md: siempre ícono y palabra, nunca solo color.
import { computed } from 'vue';
import type { EstadoSolicitud, EstadoViaje } from '@/api/tipos';
import { TEXTO_ESTADO_SOLICITUD, TEXTO_ESTADO_VIAJE } from '@/utils/formato';

const props = defineProps<{
  estado: EstadoViaje | EstadoSolicitud;
  /** Viaje publicado con más de 2 h de retraso. */
  vencido?: boolean;
}>();

const ICONOS: Record<string, string> = {
  publicado: 'event',
  'en-curso': 'directions_car',
  finalizado: 'flag',
  cancelado: 'block',
  vencido: 'schedule',
  pendiente: 'hourglass_empty',
  aceptada: 'check_circle',
  rechazada: 'cancel',
  cancelada: 'block',
};

const clave = computed(() => {
  if (props.vencido && props.estado === 'PUBLICADO') return 'vencido';
  return props.estado.toLowerCase().replace('_', '-');
});

const info = computed(() => {
  const texto =
    clave.value === 'vencido'
      ? TEXTO_ESTADO_VIAJE.VENCIDO
      : ((TEXTO_ESTADO_VIAJE as Record<string, string>)[props.estado] ??
        (TEXTO_ESTADO_SOLICITUD as Record<string, string>)[props.estado] ??
        props.estado);
  return { texto, icono: ICONOS[clave.value] ?? 'info' };
});
</script>

<style scoped lang="scss">
.chip-estado {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  font-size: 0.875rem;
  font-weight: 600;
  white-space: nowrap;
}
.chip-estado--publicado {
  background: var(--raite-azul-tenue);
  color: var(--raite-azul);
}
.chip-estado--en-curso {
  background: var(--raite-amarillo);
  color: var(--raite-negro);
}
.chip-estado--finalizado {
  background: var(--raite-blanco);
  color: var(--raite-negro);
  box-shadow: inset 0 0 0 1px var(--raite-borde-campo);
}
.chip-estado--cancelado,
.chip-estado--cancelada {
  background: var(--raite-gris-tenue);
  color: var(--raite-gris);
}
.chip-estado--vencido {
  background: var(--raite-gris-tenue);
  color: var(--raite-negro);
}
.chip-estado--pendiente {
  background: var(--raite-amarillo-tenue);
  color: var(--raite-negro);
}
.chip-estado--aceptada {
  background: var(--raite-verde-tenue);
  color: var(--raite-verde-texto);
}
.chip-estado--rechazada {
  background: var(--raite-rojo-tenue);
  color: var(--raite-rojo-texto);
}
</style>
