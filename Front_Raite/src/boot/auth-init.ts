import { useSesionStore } from '@/stores/sesion';

// Recupera la sesión guardada antes de la primera navegación.
export default async () => {
  await useSesionStore().iniciar();
};
