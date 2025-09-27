<template>
  <header class="bg-white border-b px-6 py-4">
    <div class="flex items-center justify-between">
      <!-- Left side - Breadcrumbs -->
      <div class="flex items-center space-x-2">
        <nav class="flex" aria-label="Breadcrumb">
          <ol class="flex items-center space-x-2">
            <li v-for="(crumb, index) in breadcrumbs" :key="index">
              <div class="flex items-center">
                <router-link
                  v-if="crumb.to"
                  :to="crumb.to"
                  class="text-gray-500 hover:text-gray-700"
                >
                  {{ crumb.label }}
                </router-link>
                <span v-else class="text-gray-900 font-medium">
                  {{ crumb.label }}
                </span>
                <svg
                  v-if="index < breadcrumbs.length - 1"
                  class="flex-shrink-0 h-5 w-5 text-gray-400 ml-2"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
                </svg>
              </div>
            </li>
          </ol>
        </nav>
      </div>

      <!-- Right side - Actions -->
      <div class="flex items-center space-x-4">
        <!-- Search -->
        <div class="relative">
          <input
            type="text"
            placeholder="Search..."
            class="w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <Icon name="search" class="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
        </div>

        <!-- Notifications -->
        <button class="p-2 text-gray-400 hover:text-gray-600 relative">
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5v-5zM10.97 4.97a.235.235 0 0 0-.02 0L9 7h6l-1.95-2.03a.235.235 0 0 0-.02 0L12 4l-1.03.97zM18 8H6l-.83 9.96a1 1 0 0 0 .99 1.04h11.68a1 1 0 0 0 .99-1.04L18 8z"/>
          </svg>
          <span class="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400"></span>
        </button>

        <!-- User Menu -->
        <UserDropdown />
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Icon from '../Icon.vue'
import UserDropdown from '../UserDropdown.vue'

const route = useRoute()

const breadcrumbs = computed(() => {
  const routeMap = {
    '/dashboard': [{ label: 'Dashboard' }],
    '/bookings': [{ label: 'Dashboard', to: '/dashboard' }, { label: 'Bookings' }],
    '/clients': [{ label: 'Dashboard', to: '/dashboard' }, { label: 'Clients' }],
    '/photographers': [{ label: 'Dashboard', to: '/dashboard' }, { label: 'Photographers' }],
    '/studios': [{ label: 'Dashboard', to: '/dashboard' }, { label: 'Studios' }],
    '/packages': [{ label: 'Dashboard', to: '/dashboard' }, { label: 'Packages' }],
    '/services': [{ label: 'Dashboard', to: '/dashboard' }, { label: 'Services' }],
  }
  
  return routeMap[route.path] || [{ label: 'Dashboard', to: '/dashboard' }]
})
</script>