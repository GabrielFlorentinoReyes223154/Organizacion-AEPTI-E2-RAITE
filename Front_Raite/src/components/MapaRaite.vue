<template>
  <div ref="contenedor" class="mapa-raite" role="region" :aria-label="etiqueta" />
</template>

<script setup lang="ts">
// Mapa de Leaflet + OpenStreetMap (RF-08). Es un apoyo: todo lo que se elige aquí también se puede
// elegir en la lista, para quien usa teclado o lector de pantalla y para leer mejor al sol.
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';
import type { Campus, PuntoReferencia } from '@/api/tipos';

type Coordenada = [number, number];

const props = withDefaults(
  defineProps<{
    puntos?: PuntoReferencia[];
    seleccionado?: number | null;
    campus?: Pick<Campus, 'id' | 'codigo' | 'nombre' | 'latitud' | 'longitud'>[];
    /** Centro del radio cuando no hay punto elegido (por ejemplo, la ubicación de la persona). */
    centro?: Coordenada | null;
    radioKm?: number | null;
    ruta?: { desde: Coordenada; hasta: Coordenada } | null;
    etiqueta?: string;
    /** Espacio (px) que tapa algo encima del mapa por abajo, para encuadrar por arriba de eso. */
    margenAbajo?: number;
    /** Permite tocar los puntos para elegirlos. */
    elegible?: boolean;
  }>(),
  {
    puntos: () => [],
    seleccionado: null,
    campus: () => [],
    centro: null,
    radioKm: null,
    ruta: null,
    etiqueta: 'Mapa',
    margenAbajo: 0,
    elegible: false,
  },
);
const emit = defineEmits<{ seleccionar: [id: number] }>();

const AZUL = '#003CA6';
const AMARILLO = '#FFD600';
const NEGRO = '#231F20';
const JUAREZ: Coordenada = [31.69, -106.42];

const contenedor = ref<HTMLElement | null>(null);
let mapa: L.Map | null = null;
let capa: L.LayerGroup | null = null;
let observador: ResizeObserver | null = null;
let ultimoEncuadre = '';

function coord(p: { latitud: string; longitud: string }): Coordenada {
  return [Number(p.latitud), Number(p.longitud)];
}

function escapar(texto: string) {
  return texto.replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
}

function dibujar() {
  if (!mapa || !capa) return;
  capa.clearLayers();

  const elegido = props.puntos.find((p) => p.id === props.seleccionado) ?? null;

  for (const punto of props.puntos) {
    if (punto.id === props.seleccionado) continue;
    const marcador = L.circleMarker(coord(punto), {
      radius: 7,
      color: '#FFFFFF',
      weight: 2,
      fillColor: AZUL,
      fillOpacity: 1,
      interactive: props.elegible,
    });
    if (props.elegible) {
      marcador.bindTooltip(escapar(punto.nombre), { direction: 'top', offset: [0, -6] });
      marcador.on('click', () => emit('seleccionar', punto.id));
    }
    capa.addLayer(marcador);
  }

  const centroRadio = elegido ? coord(elegido) : props.centro;
  let circulo: L.Circle | null = null;
  if (centroRadio && props.radioKm) {
    circulo = L.circle(centroRadio, {
      radius: props.radioKm * 1000,
      color: AZUL,
      weight: 2,
      fillColor: AZUL,
      fillOpacity: 0.08,
      interactive: false,
    });
    capa.addLayer(circulo);
  }

  if (props.ruta) {
    capa.addLayer(
      L.polyline([props.ruta.desde, props.ruta.hasta], {
        color: AZUL,
        weight: 5,
        dashArray: '1 10',
        lineCap: 'round',
        interactive: false,
      }),
    );
  }

  // Campus en el mismo lugar (hoy IIT e IADA) van en una sola placa para que no se tapen.
  const porLugar = new Map<string, typeof props.campus>();
  for (const c of props.campus) {
    const clave = `${c.latitud},${c.longitud}`;
    porLugar.set(clave, [...(porLugar.get(clave) ?? []), c]);
  }
  for (const grupo of porLugar.values()) {
    const primero = grupo[0];
    if (!primero) continue;
    const codigos = grupo.map((c) => c.codigo).join(' · ');
    const nombres = grupo.map((c) => c.nombre).join(' y ');
    const icono = L.divIcon({
      className: 'mapa-raite__placa',
      html: `<span>${escapar(codigos)}</span>`,
      iconSize: undefined,
      iconAnchor: [20, 14],
    });
    capa.addLayer(
      L.marker(coord(primero), { icon: icono, title: nombres, alt: nombres, keyboard: false }),
    );
  }

  if (elegido) {
    const marcador = L.circleMarker(coord(elegido), {
      radius: 10,
      color: NEGRO,
      weight: 2,
      fillColor: AMARILLO,
      fillOpacity: 1,
      interactive: false,
    });
    capa.addLayer(marcador);
  } else if (props.centro) {
    capa.addLayer(
      L.circleMarker(props.centro, {
        radius: 8,
        color: '#FFFFFF',
        weight: 3,
        fillColor: AZUL,
        fillOpacity: 1,
      }),
    );
  }

  encuadrar(elegido, circulo);
}

function encuadrar(elegido: PuntoReferencia | null, circulo: L.Circle | null) {
  if (!mapa) return;
  const clave = JSON.stringify([
    props.seleccionado,
    props.centro,
    props.radioKm,
    props.ruta,
    props.margenAbajo,
  ]);
  if (clave === ultimoEncuadre) return;
  ultimoEncuadre = clave;

  const relleno = {
    paddingTopLeft: [32, 32] as L.PointTuple,
    paddingBottomRight: [32, 32 + props.margenAbajo] as L.PointTuple,
  };
  if (props.ruta) {
    mapa.fitBounds(L.latLngBounds([props.ruta.desde, props.ruta.hasta]), {
      ...relleno,
      maxZoom: 15,
    });
  } else if (circulo) {
    mapa.fitBounds(circulo.getBounds(), relleno);
  } else if (elegido) {
    mapa.setView(coord(elegido), 15);
  } else if (props.centro) {
    mapa.setView(props.centro, 14);
  } else {
    mapa.setView(JUAREZ, 12);
  }
}

onMounted(() => {
  if (!contenedor.value) return;
  // Canvas con tolerancia: cada punto se puede tocar en un área de ~44 px aunque se dibuje de 14 px.
  mapa = L.map(contenedor.value, {
    zoomControl: true,
    attributionControl: true,
    renderer: L.canvas({ tolerance: 14 }),
  }).setView(JUAREZ, 12);
  mapa.attributionControl.setPrefix(false);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(mapa);
  capa = L.layerGroup().addTo(mapa);
  dibujar();

  observador = new ResizeObserver(() => mapa?.invalidateSize());
  observador.observe(contenedor.value);
});

watch(
  () => [
    props.puntos,
    props.seleccionado,
    props.campus,
    props.centro,
    props.radioKm,
    props.ruta,
    props.margenAbajo,
  ],
  dibujar,
  { deep: true },
);

onBeforeUnmount(() => {
  observador?.disconnect();
  mapa?.remove();
  mapa = null;
});
</script>

<style scoped lang="scss">
.mapa-raite {
  // Leaflet usa z-index altos en sus capas; así no pasan por encima de barras y diálogos.
  isolation: isolate;
  position: relative;
  z-index: 0;
  width: 100%;
  height: 100%;
  min-height: 160px;
  background: #eef0f3;
  font-family: inherit;
}
:deep(.leaflet-control-zoom a) {
  width: 44px;
  height: 44px;
  line-height: 44px;
  color: var(--raite-azul);
}
:deep(.leaflet-control-attribution) {
  font-size: 11px;
}
:deep(.leaflet-tooltip) {
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--raite-negro);
}
:deep(.mapa-raite__placa) {
  span {
    display: inline-flex;
    align-items: center;
    height: 28px;
    padding: 0 8px;
    border-radius: 12px;
    background: var(--raite-azul);
    color: #fff;
    font-size: 14px;
    font-weight: 700;
    white-space: nowrap;
    box-shadow:
      inset 0 -3px 0 var(--raite-amarillo),
      var(--raite-sombra-flotante);
  }
}
</style>
