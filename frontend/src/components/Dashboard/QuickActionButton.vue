<template>
  <router-link
    :to="to"
    class="group p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all duration-200"
  >
    <div class="flex flex-col items-center text-center">
      <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-3 group-hover:bg-blue-200 transition-colors">
        <Icon :name="icon" class="w-6 h-6 text-blue-600" />
      </div>
      <h4 class="text-sm font-medium text-gray-900 mb-1">{{ label }}</h4>
      <p class="text-xs text-gray-500">{{ description }}</p>
    </div>
  </router-link>
</template>

<script setup>
import Icon from '../Icon.vue'

defineProps({
  to: String,
  icon: String,
  label: String,
  description: String
})
</script>