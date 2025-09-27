<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
      <!-- Modal Header -->
      <div class="flex items-center justify-between pb-4 border-b">
        <h3 class="text-lg font-medium text-gray-900">
          {{ isEdit ? 'Edit Booking' : 'Create New Booking' }}
        </h3>
        <button
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600"
        >
          <Icon name="x" class="w-6 h-6" />
        </button>
      </div>

      <!-- Modal Body -->
      <form @submit.prevent="handleSubmit" class="mt-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Client Information -->
          <div class="space-y-4">
            <h4 class="text-md font-medium text-gray-900">Client Information</h4>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Client Name *
              </label>
              <input
                v-model="form.client_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter client name"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Client Email *
              </label>
              <input
                v-model="form.client_email"
                type="email"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter client email"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Client Phone
              </label>
              <input
                v-model="form.client_phone"
                type="tel"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter client phone"
              />
            </div>
          </div>

          <!-- Booking Details -->
          <div class="space-y-4">
            <h4 class="text-md font-medium text-gray-900">Booking Details</h4>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Service *
              </label>
              <select
                v-model="form.service"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a service</option>
                <option value="wedding">Wedding Photography</option>
                <option value="portrait">Portrait Session</option>
                <option value="event">Event Photography</option>
                <option value="commercial">Commercial Photography</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Photographer *
              </label>
              <select
                v-model="form.photographer"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a photographer</option>
                <option value="sarah">Sarah Wilson</option>
                <option value="mike">Mike Johnson</option>
                <option value="lisa">Lisa Brown</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Studio
              </label>
              <select
                v-model="form.studio"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a studio</option>
                <option value="studio1">Main Studio</option>
                <option value="studio2">Portrait Studio</option>
                <option value="studio3">Event Hall</option>
              </select>
            </div>
          </div>

          <!-- Date and Time -->
          <div class="space-y-4">
            <h4 class="text-md font-medium text-gray-900">Date & Time</h4>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Booking Date *
              </label>
              <input
                v-model="form.booking_date"
                type="date"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Start Time *
              </label>
              <input
                v-model="form.start_time"
                type="time"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Duration (hours)
              </label>
              <input
                v-model="form.duration"
                type="number"
                min="1"
                max="12"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="2"
              />
            </div>
          </div>

          <!-- Pricing and Status -->
          <div class="space-y-4">
            <h4 class="text-md font-medium text-gray-900">Pricing & Status</h4>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Base Amount *
              </label>
              <input
                v-model="form.base_amount"
                type="number"
                step="0.01"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="0.00"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Additional Charges
              </label>
              <input
                v-model="form.additional_charges"
                type="number"
                step="0.01"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="0.00"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                v-model="form.status"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Pending">Pending</option>
                <option value="Confirmed">Confirmed</option>
                <option value="Completed">Completed</option>
                <option value="Cancelled">Cancelled</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Notes Section -->
        <div class="mt-6">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Notes
          </label>
          <textarea
            v-model="form.notes"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Additional notes or requirements..."
          ></textarea>
        </div>

        <!-- Total Amount Display -->
        <div class="mt-6 p-4 bg-gray-50 rounded-lg">
          <div class="flex justify-between items-center">
            <span class="text-lg font-medium text-gray-900">Total Amount:</span>
            <span class="text-xl font-bold text-blue-600">${{ totalAmount }}</span>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="flex items-center justify-end pt-6 border-t mt-6 space-x-3">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="!isFormValid"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isEdit ? 'Update Booking' : 'Create Booking' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import Icon from '@/components/Icon.vue'

const props = defineProps({
  booking: {
    type: Object,
    default: null
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'save'])

// Form data
const form = ref({
  client_name: '',
  client_email: '',
  client_phone: '',
  service: '',
  photographer: '',
  studio: '',
  booking_date: '',
  start_time: '',
  duration: 2,
  base_amount: 0,
  additional_charges: 0,
  status: 'Pending',
  notes: ''
})

// Computed properties
const totalAmount = computed(() => {
  const base = parseFloat(form.value.base_amount) || 0
  const additional = parseFloat(form.value.additional_charges) || 0
  return (base + additional).toFixed(2)
})

const isFormValid = computed(() => {
  return form.value.client_name &&
         form.value.client_email &&
         form.value.service &&
         form.value.photographer &&
         form.value.booking_date &&
         form.value.start_time &&
         form.value.base_amount > 0
})

// Methods
const handleSubmit = () => {
  if (isFormValid.value) {
    const bookingData = {
      ...form.value,
      total_amount: totalAmount.value
    }
    emit('save', bookingData)
  }
}

// Initialize form with booking data if editing
onMounted(() => {
  if (props.isEdit && props.booking) {
    Object.keys(form.value).forEach(key => {
      if (props.booking[key] !== undefined) {
        form.value[key] = props.booking[key]
      }
    })
  }
})
</script>