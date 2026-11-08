<template>
  <q-layout view="hHh lpR fFf">
    <q-page-container>
      <q-page class="publico" :class="{ 'publico--amplio': route.meta.amplio }">
        <section class="publico__panel raite-sobre-azul" aria-label="Raite">
          <span class="publico__circulo publico__circulo--grande" aria-hidden="true" />
          <span class="publico__circulo publico__circulo--chico" aria-hidden="true" />
          <span class="publico__punto" aria-hidden="true" />

          <img :src="logoSobreAzul" alt="Raite" class="publico__logo" width="228" height="103" />

          <div class="publico__mensaje">
            <p class="publico__titular">Comparte el camino a tu campus.</p>
            <p class="publico__texto">
              Alumnos de la UACJ que ya van para allá ofrecen sus lugares libres. Tú pides uno desde
              un punto que todos conocen.
            </p>
            <ul class="publico__beneficios">
              <li v-for="beneficio in beneficios" :key="beneficio.texto">
                <span class="publico__icono" aria-hidden="true">
                  <q-icon :name="beneficio.icono" size="22px" />
                </span>
                {{ beneficio.texto }}
              </li>
            </ul>
          </div>

          <p class="publico__pie">Proyecto de Innovación Tecnológica · UACJ 2026</p>
        </section>

        <div class="publico__contenido">
          <div class="publico__tarjeta">
            <slot />
          </div>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
// Marco de entrar, registro y verificación.
// Celular: franja azul con la marca y el formulario en una hoja blanca.
// Escritorio (≥1024 px): panel azul con el mensaje a la izquierda y el formulario en una tarjeta a la derecha.
// Logo en versión para fondo azul: blanco con el amarillo UACJ (original en RaiteDocs/Design/logo/).
import { useRoute } from 'vue-router';
import logoSobreAzul from '@/assets/logo-raite-sobre-azul.png';

const route = useRoute();

const beneficios = [
  { icono: 'verified_user', texto: 'Solo alumnos con correo @alumnos.uacj.mx' },
  { icono: 'place', texto: 'Lugares conocidos, nunca tu dirección' },
  { icono: 'phone', texto: 'Tu teléfono solo se comparte al confirmar' },
];
</script>

<style scoped lang="scss">
.publico {
  display: flex;
  flex-direction: column;
  background: var(--raite-azul);
}

// --- Panel azul ---
.publico__panel {
  position: relative;
  overflow: hidden;
  padding: 48px 24px 32px;
  color: var(--raite-blanco);
}
.publico__circulo,
.publico__punto {
  position: absolute;
  border-radius: 999px;
  pointer-events: none;
}
.publico__circulo--grande {
  width: 260px;
  height: 260px;
  right: -90px;
  top: -80px;
  background: var(--raite-azul-hondo);
}
.publico__circulo--chico {
  width: 120px;
  height: 120px;
  left: -40px;
  bottom: -50px;
  background: rgba(255, 255, 255, 0.07);
}
.publico__punto {
  width: 18px;
  height: 18px;
  right: 64px;
  top: 56px;
  background: var(--raite-amarillo);
}
.publico__logo,
.publico__mensaje,
.publico__pie {
  position: relative;
}
.publico__logo {
  display: block;
  width: auto;
  height: 56px;
}
.publico__titular {
  margin: 12px 0 0;
  max-width: 300px;
  font-size: 1.125rem;
  line-height: 1.4;
  font-weight: 600;
  color: var(--raite-azul-niebla);
}
// En celular solo van la marca y el titular; el resto aparece en escritorio.
.publico__texto,
.publico__beneficios,
.publico__pie {
  display: none;
}

// --- Formulario ---
.publico__contenido {
  flex: 1;
  display: flex;
  justify-content: center;
  background: var(--raite-blanco);
  border-radius: 28px 28px 0 0;
}
.publico__tarjeta {
  width: 100%;
  max-width: 480px;
  box-sizing: border-box;
  padding: 28px 24px 40px;
}

@media (min-width: 1024px) {
  .publico {
    flex-direction: row;
  }
  // Fijo mientras el formulario (registro es largo) se desplaza.
  .publico__panel {
    flex: 1 1 50%;
    position: sticky;
    top: 0;
    align-self: flex-start;
    height: 100vh;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 40px;
    padding: 56px 64px;
  }
  .publico__circulo--grande {
    width: 520px;
    height: 520px;
    right: -200px;
    top: -180px;
  }
  .publico__circulo--chico {
    width: 240px;
    height: 240px;
    left: -80px;
    bottom: 120px;
  }
  .publico__punto {
    width: 28px;
    height: 28px;
    right: 120px;
    top: 110px;
  }
  .publico__logo {
    align-self: flex-start;
    height: 80px;
  }
  .publico__mensaje {
    display: flex;
    flex-direction: column;
    gap: 28px;
    max-width: 480px;
  }
  .publico__titular {
    margin: 0;
    max-width: none;
    font-size: 2.75rem;
    line-height: 1.15;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--raite-blanco);
  }
  .publico__texto {
    display: block;
    margin: 0;
    font-size: 1.125rem;
    line-height: 1.5;
    color: var(--raite-azul-niebla);
  }
  .publico__beneficios {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin: 0;
    padding: 0;
    list-style: none;
    li {
      display: flex;
      align-items: center;
      gap: 14px;
      font-size: 1.0625rem;
      font-weight: 600;
    }
  }
  .publico__icono {
    flex: none;
    width: 44px;
    height: 44px;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--raite-azul-hondo);
    color: var(--raite-amarillo); // 9.06:1 sobre azul hondo
  }
  .publico__pie {
    display: block;
    margin: 0;
    font-size: 0.875rem;
    color: var(--raite-azul-niebla);
  }

  .publico__contenido {
    flex: 1 1 50%;
    align-items: center;
    padding: 56px 32px;
    background: var(--raite-fondo);
    border-radius: 0;
  }
  .publico__tarjeta {
    max-width: 480px;
    padding: 40px;
    border-radius: 28px;
    background: var(--raite-blanco);
    box-shadow: 0 8px 24px rgba(35, 31, 32, 0.08);
  }

  // Formulario largo (registro): el panel cede espacio y la tarjeta se ensancha a dos columnas.
  .publico--amplio {
    .publico__panel {
      flex-basis: 40%;
    }
    .publico__contenido {
      flex-basis: 60%;
    }
    .publico__tarjeta {
      max-width: 820px;
    }
  }
}
</style>
