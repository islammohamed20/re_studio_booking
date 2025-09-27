<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex items-center">
      <div class="flex-shrink-0">
        <div :class="iconClasses" class="w-12 h-12 rounded-lg flex items-center justify-center">
          <Icon :name="icon" class="w-6 h-6 text-white" />
        </div>
      </div>
      <div class="ml-4 flex-1">
        <div class="text-sm font-medium text-gray-500">{{ title }}</div>
        <div class="text-2xl font-bold text-gray-900">
          <span v-if="loading" class="animate-pulse bg-gray-200 rounded w-16 h-8 block"></span>
          <span v-else>{{ formattedValue }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import Icon from '../Icon.vue'

const props = defineProps({
  title: String,
  value: [Number, String],
  icon: String,
  color: {
    type: String,
    default: 'blue'
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const iconClasses = computed(() => {
  const colorMap = {
    blue: 'bg-blue-600',
    green: 'bg-green-600',
    purple: 'bg-purple-600',
    orange: 'bg-orange-600',
    red: 'bg-red-600',
    yellow: 'bg-yellow-600'
  }
  return colorMap[props.color] || colorMap.blue
})

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return props.value.toLocaleString()
  }
  return props.value
})
</script>