<template>
  <div class="flex items-center space-x-3 p-3 hover:bg-gray-50 rounded-lg cursor-pointer">
    <div class="flex-shrink-0">
      <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
        <Icon name="calendar" class="w-5 h-5 text-blue-600" />
      </div>
    </div>
    <div class="flex-1 min-w-0">
      <p class="text-sm font-medium text-gray-900 truncate">
        {{ booking.client_name || 'Unknown Client' }}
      </p>
      <p class="text-sm text-gray-500 truncate">
        {{ booking.service_name || 'Service' }} • {{ formatDate(booking.booking_date) }}
      </p>
    </div>
    <div class="flex-shrink-0">
      <span :class="statusClasses" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
        {{ booking.status || 'Pending' }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import Icon from '../Icon.vue'

const props = defineProps({
  booking: {
    type: Object,
    required: true
  }
})

const statusClasses = computed(() => {
  const status = props.booking.status?.toLowerCase()
  const statusMap = {
    confirmed: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
    cancelled: 'bg-red-100 text-red-800',
    completed: 'bg-blue-100 text-blue-800'
  }
  return statusMap[status] || statusMap.pending
})

const formatDate = (date) => {
  if (!date) return 'No date'
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}
</script>