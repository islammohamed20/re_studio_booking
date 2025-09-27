<template>
  <router-link
    :to="to"
    class="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
    :class="{
      'bg-blue-50 text-blue-700 border border-blue-200': isActive
    }"
  >
    <Icon :name="icon" class="w-5 h-5" />
    <span class="font-medium">{{ label }}</span>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Icon from '../Icon.vue'

const props = defineProps({
  to: String,
  icon: String,
  label: String
})

const route = useRoute()
const isActive = computed(() => route.path.startsWith(props.to))
</script>