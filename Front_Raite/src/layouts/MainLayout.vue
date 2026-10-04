<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />

        <q-toolbar-title> Raite </q-toolbar-title>

        <q-space />

        <q-btn flat dense round icon="person" aria-label="User menu">
          <q-menu anchor="top right" self="top right">
            <q-list style="min-width: 150px" dense>
              <q-item clickable to="/info">
                <q-item-section avatar>
                  <q-icon name="info" />
                </q-item-section>
                <q-item-section>Info</q-item-section>
              </q-item>
              <q-item clickable @click="logout">
                <q-item-section avatar>
                  <q-icon name="logout" />
                </q-item-section>
                <q-item-section>Cerrar sesión</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header> Essential Links </q-item-label>

        <EssentialLink v-for="link in linksList" :key="link.label" v-bind="link" />
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth-store';
import EssentialLink, { type EssentialLinkProps } from '@/components/EssentialLink.vue';

const authStore = useAuthStore();

const linksList: EssentialLinkProps[] = [
  {
    label: 'Iniciar sesión',
    caption: 'quasar.dev',
    icon: 'person',
    link: '/#/login/loginpage',
  },
  {
    label: 'Crear cuenta',
    caption: 'github.com/quasarframework',
    icon: 'add',
    link: '/#/login/signuppage',
  },
  {
    label: 'Segunda página',
    caption: 'chat.quasar.dev',
    icon: 'settings',
    link: '/second',
  },
  {
    label: 'Forum',
    caption: 'forum.quasar.dev',
    icon: 'record_voice_over',
    link: 'https://forum.quasar.dev',
  },
  {
    label: 'Twitter',
    caption: '@quasarframework',
    icon: 'rss_feed',
    link: 'https://twitter.quasar.dev',
  },
  {
    label: 'Facebook',
    caption: '@QuasarFramework',
    icon: 'public',
    link: 'https://facebook.quasar.dev',
  },
  {
    label: 'Quasar Awesome',
    caption: 'Community Quasar projects',
    icon: 'favorite',
    link: 'https://awesome.quasar.dev',
  },
];

const leftDrawerOpen = ref(false);

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}

async function logout() {
  await authStore.logout();
}
</script>