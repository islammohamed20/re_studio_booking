<template>
  <div id="app">
    <DesktopLayout v-if="session.isLoggedIn">
      <router-view />
    </DesktopLayout>
    <router-view v-else />
  </div>
</template>

<script>
import { session } from '@/data/session'
import DesktopLayout from '@/components/Layouts/DesktopLayout.vue'

export default {
  name: "App",
  components: {
    DesktopLayout
  },
  data() {
    return {
      session
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>
