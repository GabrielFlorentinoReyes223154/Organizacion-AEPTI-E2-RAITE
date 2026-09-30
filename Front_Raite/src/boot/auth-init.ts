import { boot } from '#q-app'
import { useAuthStore } from 'stores/auth-store'

export default boot(async () => {
  const authStore = useAuthStore()
  await authStore.initializeAuth()
})