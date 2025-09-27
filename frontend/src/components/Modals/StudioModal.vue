<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-10 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
      <!-- Modal Header -->
      <div class="flex items-center justify-between pb-4 border-b">
        <h3 class="text-lg font-medium text-gray-900">
          {{ isEdit ? 'Edit Studio' : 'Add New Studio' }}
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
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Basic Information -->
          <div class="space-y-6">
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">Basic Information</h4>
              
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Studio Name *
                  </label>
                  <input
                    v-model="form.name"
                    type="text"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter studio name"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Studio Type *
                  </label>
                  <select
                    v-model="form.type"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select studio type</option>
                    <option value="Portrait">Portrait Studio</option>
                    <option value="Wedding">Wedding Studio</option>
                    <option value="Event">Event Hall</option>
                    <option value="Commercial">Commercial Studio</option>
                    <option value="Product">Product Photography</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    v-model="form.description"
                    rows="4"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Describe the studio and its features..."
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
                    <option value="Maintenance">Maintenance</option>
                    <option value="Inactive">Inactive</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Location & Contact -->
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">Location & Contact</h4>
              
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Address
                  </label>
                  <textarea
                    v-model="form.address"
                    rows="3"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter studio address"
                  ></textarea>
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      City
                    </label>
                    <input
                      v-model="form.city"
                      type="text"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="City"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Postal Code
                    </label>
                    <input
                      v-model="form.postal_code"
                      type="text"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Postal code"
                    />
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Contact Phone
                  </label>
                  <input
                    v-model="form.phone"
                    type="tel"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Studio contact number"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Technical Details -->
          <div class="space-y-6">
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">Technical Details</h4>
              
              <div class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Capacity (people) *
                    </label>
                    <input
                      v-model="form.capacity"
                      type="number"
                      min="1"
                      required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Max capacity"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Size (sq ft) *
                    </label>
                    <input
                      v-model="form.size"
                      type="number"
                      min="1"
                      required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Studio size"
                    />
                  </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Ceiling Height (ft)
                    </label>
                    <input
                      v-model="form.ceiling_height"
                      type="number"
                      min="1"
                      step="0.1"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Height"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Natural Light
                    </label>
                    <select
                      v-model="form.natural_light"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="Excellent">Excellent</option>
                      <option value="Good">Good</option>
                      <option value="Fair">Fair</option>
                      <option value="Poor">Poor</option>
                      <option value="None">None</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Equipment Available
                  </label>
                  <div class="grid grid-cols-2 gap-2 mt-2">
                    <label v-for="equipment in availableEquipment" :key="equipment" class="flex items-center">
                      <input
                        v-model="form.equipment"
                        :value="equipment"
                        type="checkbox"
                        class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                      />
                      <span class="ml-2 text-sm text-gray-700">{{ equipment }}</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <!-- Pricing & Availability -->
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">Pricing & Availability</h4>
              
              <div class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Hourly Rate ($) *
                    </label>
                    <input
                      v-model="form.hourly_rate"
                      type="number"
                      min="0"
                      step="0.01"
                      required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="0.00"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Half Day Rate ($)
                    </label>
                    <input
                      v-model="form.half_day_rate"
                      type="number"
                      min="0"
                      step="0.01"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="0.00"
                    />
                  </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Full Day Rate ($)
                    </label>
                    <input
                      v-model="form.full_day_rate"
                      type="number"
                      min="0"
                      step="0.01"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="0.00"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Minimum Booking (hours)
                    </label>
                    <input
                      v-model="form.minimum_booking"
                      type="number"
                      min="1"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="1"
                    />
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Operating Hours
                  </label>
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">Opening Time</label>
                      <input
                        v-model="form.opening_time"
                        type="time"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">Closing Time</label>
                      <input
                        v-model="form.closing_time"
                        type="time"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Additional Features -->
        <div class="mt-8">
          <h4 class="text-md font-medium text-gray-900 mb-4">Additional Features</h4>
          
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <label v-for="feature in additionalFeatures" :key="feature" class="flex items-center">
              <input
                v-model="form.features"
                :value="feature"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              />
              <span class="ml-2 text-sm text-gray-700">{{ feature }}</span>
            </label>
          </div>
        </div>

        <!-- Notes -->
        <div class="mt-6">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Additional Notes
          </label>
          <textarea
            v-model="form.notes"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Any additional information about the studio..."
          ></textarea>
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
            {{ isEdit ? 'Update Studio' : 'Add Studio' }}
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
  studio: {
    type: Object,
    default: null
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'save'])

// Available options
const availableEquipment = [
  'Professional Lighting',
  'Backdrop System',
  'Props Collection',
  'Makeup Station',
  'Changing Room',
  'Sound System',
  'Video Equipment',
  'Tripods & Stands',
  'Reflectors',
  'Color Correction Lights',
  'Seamless Paper',
  'Product Tables'
]

const additionalFeatures = [
  'WiFi',
  'Air Conditioning',
  'Parking',
  'Kitchen/Catering',
  'Client Lounge',
  'Storage Space',
  'Wheelchair Accessible',
  'Security System'
]

// Form data
const form = ref({
  name: '',
  type: '',
  description: '',
  status: 'Active',
  address: '',
  city: '',
  postal_code: '',
  phone: '',
  capacity: null,
  size: null,
  ceiling_height: null,
  natural_light: 'Good',
  equipment: [],
  hourly_rate: null,
  half_day_rate: null,
  full_day_rate: null,
  minimum_booking: 1,
  opening_time: '09:00',
  closing_time: '18:00',
  features: [],
  notes: ''
})

// Computed properties
const isFormValid = computed(() => {
  return form.value.name &&
         form.value.type &&
         form.value.capacity &&
         form.value.size &&
         form.value.hourly_rate
})

// Methods
const handleSubmit = () => {
  if (isFormValid.value) {
    emit('save', { ...form.value })
  }
}

// Initialize form with studio data if editing
onMounted(() => {
  if (props.isEdit && props.studio) {
    Object.keys(form.value).forEach(key => {
      if (props.studio[key] !== undefined) {
        form.value[key] = props.studio[key]
      }
    })
  }
})
</script>