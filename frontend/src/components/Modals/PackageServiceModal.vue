<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-10 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
      <!-- Modal Header -->
      <div class="flex items-center justify-between pb-4 border-b">
        <h3 class="text-lg font-medium text-gray-900">
          {{ isEdit ? `Edit ${type}` : `Add New ${type}` }}
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
        <!-- Basic Information -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div class="space-y-6">
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">Basic Information</h4>
              
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    {{ type === 'package' ? 'Package' : 'Service' }} Name *
                  </label>
                  <input
                    v-model="form.name"
                    type="text"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    :placeholder="`Enter ${type} name`"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Category *
                  </label>
                  <select
                    v-model="form.category"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select category</option>
                    <option value="Portrait">Portrait</option>
                    <option value="Wedding">Wedding</option>
                    <option value="Event">Event</option>
                    <option value="Commercial">Commercial</option>
                    <option value="Product">Product</option>
                    <option value="Fashion">Fashion</option>
                    <option value="Studio">Studio</option>
                    <option value="Post-Production">Post-Production</option>
                    <option value="Aerial">Aerial</option>
                    <option value="Beauty">Beauty</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Description *
                  </label>
                  <textarea
                    v-model="form.description"
                    rows="4"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    :placeholder="`Describe the ${type}...`"
                  ></textarea>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Status
                  </label>
                  <select
                    v-model="form.status"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="Active">Active</option>
                    <option value="Inactive">Inactive</option>
                    <option value="Draft">Draft</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- Pricing & Duration -->
          <div class="space-y-6">
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">Pricing & Duration</h4>
              
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Duration *
                  </label>
                  <input
                    v-model="form.duration"
                    type="text"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., 2 hours, 1 day, 2-3 days turnaround"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Price ($) *
                  </label>
                  <input
                    v-model="form.price"
                    type="number"
                    min="0"
                    step="0.01"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="0.00"
                  />
                </div>

                <div v-if="type === 'service'">
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Unit
                  </label>
                  <select
                    v-model="form.unit"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="per session">per session</option>
                    <option value="per hour">per hour</option>
                    <option value="per photo">per photo</option>
                    <option value="per day">per day</option>
                    <option value="per event">per event</option>
                    <option value="per item">per item</option>
                  </select>
                </div>

                <div v-if="type === 'package'">
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Discount (%)
                  </label>
                  <input
                    v-model="form.discount"
                    type="number"
                    min="0"
                    max="100"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="0"
                  />
                </div>

                <div v-if="type === 'package'">
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Number of Sessions
                  </label>
                  <input
                    v-model="form.sessions"
                    type="number"
                    min="1"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="1"
                  />
                </div>

                <div v-if="type === 'package'">
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Photos Included
                  </label>
                  <input
                    v-model="form.photos_included"
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., 50-75 edited photos, 200-300 edited photos"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Services/Features Included -->
        <div class="mt-8">
          <h4 class="text-md font-medium text-gray-900 mb-4">
            {{ type === 'package' ? 'Services Included' : 'Features Included' }}
          </h4>
          
          <div class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div v-for="(service, index) in form.services" :key="index" class="flex items-center space-x-2">
                <input
                  v-model="form.services[index]"
                  type="text"
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  :placeholder="`${type === 'package' ? 'Service' : 'Feature'} ${index + 1}`"
                />
                <button
                  type="button"
                  @click="removeService(index)"
                  class="text-red-600 hover:text-red-800"
                >
                  <Icon name="x" class="w-5 h-5" />
                </button>
              </div>
            </div>
            
            <button
              type="button"
              @click="addService"
              class="text-blue-600 hover:text-blue-800 text-sm flex items-center space-x-1"
            >
              <Icon name="plus" class="w-4 h-4" />
              <span>Add {{ type === 'package' ? 'Service' : 'Feature' }}</span>
            </button>
          </div>
        </div>

        <!-- Add-ons -->
        <div class="mt-8">
          <h4 class="text-md font-medium text-gray-900 mb-4">Available Add-ons</h4>
          
          <div class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div v-for="(addon, index) in form.add_ons" :key="index" class="flex items-center space-x-2">
                <input
                  v-model="form.add_ons[index]"
                  type="text"
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  :placeholder="`Add-on ${index + 1}`"
                />
                <button
                  type="button"
                  @click="removeAddon(index)"
                  class="text-red-600 hover:text-red-800"
                >
                  <Icon name="x" class="w-5 h-5" />
                </button>
              </div>
            </div>
            
            <button
              type="button"
              @click="addAddon"
              class="text-blue-600 hover:text-blue-800 text-sm flex items-center space-x-1"
            >
              <Icon name="plus" class="w-4 h-4" />
              <span>Add Add-on</span>
            </button>
          </div>
        </div>

        <!-- Terms & Conditions -->
        <div class="mt-8">
          <h4 class="text-md font-medium text-gray-900 mb-4">Terms & Conditions</h4>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Cancellation Policy
              </label>
              <select
                v-model="form.cancellation_policy"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="24 hours">24 hours notice</option>
                <option value="48 hours">48 hours notice</option>
                <option value="1 week">1 week notice</option>
                <option value="2 weeks">2 weeks notice</option>
                <option value="Non-refundable">Non-refundable</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Payment Terms
              </label>
              <select
                v-model="form.payment_terms"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Full payment upfront">Full payment upfront</option>
                <option value="50% deposit">50% deposit, 50% on completion</option>
                <option value="30% deposit">30% deposit, 70% on completion</option>
                <option value="Payment on completion">Payment on completion</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Delivery Timeline
              </label>
              <input
                v-model="form.delivery_timeline"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., 2-3 weeks, 5-7 business days"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Additional Terms
              </label>
              <textarea
                v-model="form.additional_terms"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Any additional terms and conditions..."
              ></textarea>
            </div>
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
            {{ isEdit ? `Update ${type}` : `Add ${type}` }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Icon from '@/components/Icon.vue'

const props = defineProps({
  type: {
    type: String,
    required: true,
    validator: value => ['package', 'service'].includes(value)
  },
  item: {
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
  name: '',
  category: '',
  description: '',
  status: 'Active',
  duration: '',
  price: null,
  unit: 'per session',
  discount: 0,
  sessions: 1,
  photos_included: '',
  services: [''],
  add_ons: [''],
  cancellation_policy: '48 hours',
  payment_terms: '50% deposit',
  delivery_timeline: '',
  additional_terms: ''
})

// Computed properties
const isFormValid = computed(() => {
  return form.value.name &&
         form.value.category &&
         form.value.description &&
         form.value.duration &&
         form.value.price !== null
})

// Methods
const addService = () => {
  form.value.services.push('')
}

const removeService = (index) => {
  if (form.value.services.length > 1) {
    form.value.services.splice(index, 1)
  }
}

const addAddon = () => {
  form.value.add_ons.push('')
}

const removeAddon = (index) => {
  if (form.value.add_ons.length > 1) {
    form.value.add_ons.splice(index, 1)
  }
}

const handleSubmit = () => {
  if (isFormValid.value) {
    // Filter out empty services and add-ons
    const cleanedData = {
      ...form.value,
      services: form.value.services.filter(service => service.trim()),
      add_ons: form.value.add_ons.filter(addon => addon.trim())
    }
    
    emit('save', cleanedData)
  }
}

// Initialize form with item data if editing
onMounted(() => {
  if (props.isEdit && props.item) {
    Object.keys(form.value).forEach(key => {
      if (props.item[key] !== undefined) {
        form.value[key] = props.item[key]
      }
    })
    
    // Ensure arrays have at least one empty item for adding new entries
    if (form.value.services.length === 0) {
      form.value.services = ['']
    }
    if (form.value.add_ons.length === 0) {
      form.value.add_ons = ['']
    }
  }
})
</script>