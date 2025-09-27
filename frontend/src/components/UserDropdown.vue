<template>
  <div class="relative">
    <button
      @click="isOpen = !isOpen"
      class="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100"
    >
      <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
        <span class="text-white text-sm font-medium">
          {{ userInitials }}
        </span>
      </div>
      <span class="text-gray-700 font-medium">{{ userName }}</span>
      <svg class="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
      </svg>
    </button>

    <!-- Dropdown Menu -->
    <div
      v-if="isOpen"
      class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border z-50"
    >
      <div class="py-1">
        <a href="#" class="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100">
          <Icon name="users" class="w-4 h-4 mr-3" />
          Profile
        </a>
        <a href="#" class="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100">
          <Icon name="home" class="w-4 h-4 mr-3" />
          Settings
        </a>
        <hr class="my-1">
        <button
          @click="logout"
          class="flex items-center w-full px-4 py-2 text-gray-700 hover:bg-gray-100"
        >
          <Icon name="x" class="w-4 h-4 mr-3" />
          Logout
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { sessionStore } from '@/stores/session'
import Icon from './Icon.vue'

const isOpen = ref(false)

const userName = computed(() => {
  return sessionStore.user?.full_name || 'User'
})

const userInitials = computed(() => {
  const name = userName.value
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

const logout = async () => {
  await sessionStore.logout()
  isOpen.value = false
}
</script>