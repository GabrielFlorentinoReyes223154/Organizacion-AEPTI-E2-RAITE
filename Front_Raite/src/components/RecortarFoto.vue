<template>
  <q-dialog :model-value="!!archivo" @update:model-value="(abierto) => !abierto && cancelar()">
    <q-card class="recortar raite-pila">
      <h2 class="recortar__titulo">Acomoda tu foto</h2>
      <p class="recortar__ayuda">
        Arrastra la foto para encuadrar tu cara y usa la barra para acercarla.
      </p>

      <canvas
        ref="lienzo"
        class="recortar__lienzo"
        :style="{ width: `${LADO}px`, height: `${LADO}px` }"
        tabindex="0"
        role="img"
        aria-label="Vista previa de tu foto. Usa las flechas del teclado para moverla."
        @pointerdown="empezarArrastre"
        @pointermove="arrastrar"
        @pointerup="terminarArrastre"
        @pointercancel="terminarArrastre"
        @wheel.prevent="girarRueda"
        @keydown="moverConTeclado"
      />

      <div class="recortar__zoom">
        <q-icon name="zoom_out" size="22px" aria-hidden="true" />
        <q-slider
          v-model="zoom"
          :min="1"
          :max="3"
          :step="0.01"
          color="primary"
          aria-label="Acercar foto"
          class="col"
        />
        <q-icon name="zoom_in" size="22px" aria-hidden="true" />
      </div>

      <div class="recortar__acciones">
        <q-btn
          flat
          no-caps
          color="primary"
          label="Cancelar"
          :disable="guardando"
          @click="cancelar"
        />
        <q-btn
          unelevated
          no-caps
          color="primary"
          label="Guardar foto"
          :loading="guardando"
          :disable="!imagen"
          @click="guardar"
        />
      </div>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
// Recorte cuadrado de la foto de perfil (se muestra en círculo). Sin dependencias: un <canvas>.
// Exporta un cuadrado de 512 px; el API la vuelve a revisar y la guarda como WebP.
import { nextTick, ref, watch } from 'vue';

const LADO = 300; // px en pantalla
const SALIDA = 512; // px del archivo que se sube

const props = defineProps<{ archivo: File | null; guardando?: boolean }>();
const emit = defineEmits<{ guardar: [foto: Blob, nombre: string]; cancelar: [] }>();

const lienzo = ref<HTMLCanvasElement | null>(null);
const imagen = ref<HTMLImageElement | null>(null);
const zoom = ref(1);
const desplazamiento = ref({ x: 0, y: 0 });
let arrastre: { id: number; x: number; y: number } | null = null;
let urlTemporal: string | null = null;

function escala(): number {
  const img = imagen.value;
  if (!img) return 1;
  return Math.max(LADO / img.naturalWidth, LADO / img.naturalHeight) * zoom.value;
}

/** La foto siempre cubre todo el cuadro: no se puede arrastrar más allá de su orilla. */
function acotar() {
  const img = imagen.value;
  if (!img) return;
  const s = escala();
  const maxX = Math.max(0, (img.naturalWidth * s - LADO) / 2);
  const maxY = Math.max(0, (img.naturalHeight * s - LADO) / 2);
  desplazamiento.value = {
    x: Math.min(maxX, Math.max(-maxX, desplazamiento.value.x)),
    y: Math.min(maxY, Math.max(-maxY, desplazamiento.value.y)),
  };
}

function pintarFoto(ctx: CanvasRenderingContext2D, lado: number) {
  const img = imagen.value;
  if (!img) return;
  const k = lado / LADO;
  const s = escala();
  const ancho = img.naturalWidth * s;
  const alto = img.naturalHeight * s;
  ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(
    img,
    (LADO / 2 - ancho / 2 + desplazamiento.value.x) * k,
    (LADO / 2 - alto / 2 + desplazamiento.value.y) * k,
    ancho * k,
    alto * k,
  );
}

function dibujar() {
  const canvas = lienzo.value;
  const ctx = canvas?.getContext('2d');
  if (!canvas || !ctx) return;
  const dpr = window.devicePixelRatio || 1;
  if (canvas.width !== LADO * dpr) {
    canvas.width = LADO * dpr;
    canvas.height = LADO * dpr;
  }
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, LADO, LADO);
  pintarFoto(ctx, LADO);
  // Lo que queda fuera del círculo se oscurece: así se verá el avatar.
  ctx.beginPath();
  ctx.rect(0, 0, LADO, LADO);
  ctx.arc(LADO / 2, LADO / 2, LADO / 2 - 2, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(0, 31, 87, 0.55)';
  ctx.fill('evenodd');
  ctx.beginPath();
  ctx.arc(LADO / 2, LADO / 2, LADO / 2 - 2, 0, Math.PI * 2);
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 2;
  ctx.stroke();
}

function liberar() {
  if (urlTemporal) URL.revokeObjectURL(urlTemporal);
  urlTemporal = null;
  imagen.value = null;
}

watch(
  () => props.archivo,
  (archivo) => {
    liberar();
    if (!archivo) return;
    zoom.value = 1;
    desplazamiento.value = { x: 0, y: 0 };
    urlTemporal = URL.createObjectURL(archivo);
    const img = new Image();
    img.onload = async () => {
      imagen.value = img;
      await nextTick();
      dibujar();
    };
    img.onerror = () => cancelar();
    img.src = urlTemporal;
  },
);

watch(zoom, () => {
  acotar();
  dibujar();
});

function empezarArrastre(evento: PointerEvent) {
  arrastre = { id: evento.pointerId, x: evento.clientX, y: evento.clientY };
  lienzo.value?.setPointerCapture(evento.pointerId);
}

function arrastrar(evento: PointerEvent) {
  if (!arrastre || arrastre.id !== evento.pointerId) return;
  desplazamiento.value = {
    x: desplazamiento.value.x + evento.clientX - arrastre.x,
    y: desplazamiento.value.y + evento.clientY - arrastre.y,
  };
  arrastre = { id: evento.pointerId, x: evento.clientX, y: evento.clientY };
  acotar();
  dibujar();
}

function terminarArrastre(evento: PointerEvent) {
  if (arrastre?.id === evento.pointerId) arrastre = null;
}

function girarRueda(evento: WheelEvent) {
  zoom.value = Math.min(3, Math.max(1, zoom.value - evento.deltaY * 0.002));
}

function moverConTeclado(evento: KeyboardEvent) {
  const paso = 10;
  const mov: Record<string, [number, number]> = {
    ArrowLeft: [paso, 0],
    ArrowRight: [-paso, 0],
    ArrowUp: [0, paso],
    ArrowDown: [0, -paso],
  };
  const delta = mov[evento.key];
  if (!delta) return;
  evento.preventDefault();
  desplazamiento.value = {
    x: desplazamiento.value.x + delta[0],
    y: desplazamiento.value.y + delta[1],
  };
  acotar();
  dibujar();
}

function aBlob(canvas: HTMLCanvasElement, tipo: string): Promise<Blob | null> {
  return new Promise((resolve) => canvas.toBlob(resolve, tipo, 0.9));
}

async function guardar() {
  const salida = document.createElement('canvas');
  salida.width = SALIDA;
  salida.height = SALIDA;
  const ctx = salida.getContext('2d');
  if (!ctx) return;
  pintarFoto(ctx, SALIDA);
  // Safari no exporta WebP (devuelve PNG): en ese caso se usa JPEG, que pesa menos.
  let foto = await aBlob(salida, 'image/webp');
  let nombre = 'foto.webp';
  if (!foto || foto.type !== 'image/webp') {
    foto = await aBlob(salida, 'image/jpeg');
    nombre = 'foto.jpg';
  }
  if (foto) emit('guardar', foto, nombre);
}

function cancelar() {
  emit('cancelar');
}
</script>

<style scoped lang="scss">
.recortar {
  width: calc(100vw - 32px);
  max-width: 380px;
  padding: 24px;
  border-radius: 16px;
}
.recortar__titulo {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
}
.recortar__ayuda {
  margin: 0;
  color: var(--raite-gris);
}
.recortar__lienzo {
  display: block;
  margin: 0 auto;
  max-width: 100%;
  border-radius: 12px;
  background: var(--raite-gris-tenue);
  cursor: grab;
  touch-action: none;
  &:active {
    cursor: grabbing;
  }
  &:focus-visible {
    outline: 3px solid var(--raite-azul);
    outline-offset: 3px;
  }
}
.recortar__zoom {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--raite-gris);
}
.recortar__acciones {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
