<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-10 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
      <!-- Modal Header -->
      <div class="flex items-center justify-between pb-4 border-b">
        <h3 class="text-lg font-medium text-gray-900">
          {{ isEdit ? 'Edit Photographer' : 'Add New Photographer' }}
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
          <!-- Personal Information -->
          <div class="space-y-6">
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">Personal Information</h4>
              
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Full Name *
                  </label>
                  <input
                    v-model="form.name"
                    type="text"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter photographer's full name"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Email Address *
                  </label>
                  <input
                    v-model="form.email"
                    type="email"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="photographer@email.com"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Phone Number *
                  </label>
                  <input
                    v-model="form.phone"
                    type="tel"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="+1 (555) 123-4567"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Bio/Description
                  </label>
                  <textarea
                    v-model="form.bio"
                    rows="4"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Brief description about the photographer..."
                  ></textarea>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Portfolio URL
                  </label>
                  <input
                    v-model="form.portfolio_url"
                    type="url"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="https://photographer-portfolio.com"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Languages
                  </label>
                  <div class="grid grid-cols-2 gap-2 mt-2">
                    <label v-for="language in availableLanguages" :key="language" class="flex items-center">
                      <input
                        v-model="form.languages"
                        :value="language"
                        type="checkbox"
                        class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                      />
                      <span class="ml-2 text-sm text-gray-700">{{ language }}</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Professional Information -->
          <div class="space-y-6">
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">Professional Information</h4>
              
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Primary Specialty *
                  </label>
                  <select
                    v-model="form.specialty"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select specialty</option>
                    <option value="Portrait">Portrait</option>
                    <option value="Wedding">Wedding</option>
                    <option value="Event">Event</option>
                    <option value="Commercial">Commercial</option>
                    <option value="Product">Product</option>
                    <option value="Fashion">Fashion</option>
                    <option value="Architecture">Architecture</option>
                    <option value="Nature">Nature</option>
                  </select>
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Experience (years) *
                    </label>
                    <input
                      v-model="form.experience"
                      type="number"
                      min="0"
                      max="50"
                      required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="5"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Rating (1-5)
                    </label>
                    <input
                      v-model="form.rating"
                      type="number"
                      min="1"
                      max="5"
                      step="0.1"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="4.5"
                    />
                  </div>
                </div>

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
                    placeholder="150.00"
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
                    <option value="Active">Active</option>
                    <option value="Busy">Busy</option>
                    <option value="Vacation">On Vacation</option>
                    <option value="Inactive">Inactive</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Availability Notes
                  </label>
                  <input
                    v-model="form.availability"
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Available, Busy until Dec 15, etc."
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Skills & Expertise
                  </label>
                  <div class="grid grid-cols-2 gap-2 mt-2">
                    <label v-for="skill in availableSkills" :key="skill" class="flex items-center">
                      <input
                        v-model="form.skills"
                        :value="skill"
                        type="checkbox"
                        class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                      />
                      <span class="ml-2 text-sm text-gray-700">{{ skill }}</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Equipment Section -->
        <div class="mt-8">
          <h4 class="text-md font-medium text-gray-900 mb-4">Equipment & Gear</h4>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Camera Equipment
              </label>
              <div class="grid grid-cols-1 gap-2 mt-2">
                <label v-for="camera in availableCameras" :key="camera" class="flex items-center">
                  <input
                    v-model="form.equipment"
                    :value="camera"
                    type="checkbox"
                    class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                  />
                  <span class="ml-2 text-sm text-gray-700">{{ camera }}</span>
                </label>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Additional Equipment
              </label>
              <div class="grid grid-cols-1 gap-2 mt-2">
                <label v-for="equipment in additionalEquipment" :key="equipment" class="flex items-center">
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

          <div class="mt-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Custom Equipment (one per line)
            </label>
            <textarea
              v-model="customEquipment"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter any additional equipment not listed above..."
            ></textarea>
          </div>
        </div>

        <!-- Contact Preferences -->
        <div class="mt-8">
          <h4 class="text-md font-medium text-gray-900 mb-4">Contact Preferences</h4>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Preferred Contact Method
              </label>
              <select
                v-model="form.preferred_contact"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Email">Email</option>
                <option value="Phone">Phone</option>
                <option value="Text">Text Message</option>
                <option value="WhatsApp">WhatsApp</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Response Time
              </label>
              <select
                v-model="form.response_time"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Within 1 hour">Within 1 hour</option>
                <option value="Within 4 hours">Within 4 hours</option>
                <option value="Within 24 hours">Within 24 hours</option>
                <option value="Within 48 hours">Within 48 hours</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Time Zone
              </label>
              <select
                v-model="form.timezone"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="EST">Eastern (EST)</option>
                <option value="CST">Central (CST)</option>
                <option value="MST">Mountain (MST)</option>
                <option value="PST">Pacific (PST)</option>
                <option value="UTC">UTC</option>
              </select>
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
            {{ isEdit ? 'Update Photographer' : 'Add Photographer' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import Icon from '@/components/Icon.vue'

const props = defineProps({
  photographer: {
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
const availableLanguages = [
  'English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese',
  'Arabic', 'Mandarin', 'Japanese', 'Korean', 'Russian', 'Hindi'
]

const availableSkills = [
  'Portrait', 'Wedding', 'Event', 'Commercial', 'Product', 'Fashion',
  'Architecture', 'Nature', 'Street Photography', 'Photojournalism',
  'Studio Lighting', 'Natural Light', 'Photo Editing', 'Retouching',
  'Color Correction', 'Black & White', 'Macro', 'Drone Photography',
  'Low Light', 'High Speed', 'Underwater', 'Sports'
]

const availableCameras = [
  'Canon 5D Mark IV', 'Canon R5', 'Canon R6', 'Canon 1DX Mark III',
  'Nikon D850', 'Nikon Z7', 'Nikon Z6', 'Nikon D780',
  'Sony A7R IV', 'Sony A7 III', 'Sony A9 II', 'Sony FX3',
  'Fujifilm X-T4', 'Fujifilm GFX 100S', 'Hasselblad H6D',
  'Phase One XF', 'Leica SL2', 'Pentax K-1 Mark II'
]

const additionalEquipment = [
  'Professional Lighting Kit', 'Profoto Lighting', 'Godox Lighting',
  'Wireless Flash System', 'Continuous Lighting', 'LED Panels',
  'Tripods & Stands', 'Monopods', 'Gimbals', 'Sliders',
  'Reflectors', 'Diffusers', 'Backdrop System', 'Seamless Paper',
  'Tethering Setup', 'Laptop/Tablet', 'External Monitors',
  'Drone Equipment', 'Underwater Housing', 'Macro Equipment'
]

// Form data
const form = ref({
  name: '',
  email: '',
  phone: '',
  bio: '',
  portfolio_url: '',
  languages: [],
  specialty: '',
  experience: null,
  rating: 4.5,
  hourly_rate: null,
  status: 'Active',
  availability: 'Available',
  skills: [],
  equipment: [],
  preferred_contact: 'Email',
  response_time: 'Within 24 hours',
  timezone: 'EST'
})

const customEquipment = ref('')

// Computed properties
const isFormValid = computed(() => {
  return form.value.name &&
         form.value.email &&
         form.value.phone &&
         form.value.specialty &&
         form.value.experience !== null &&
         form.value.hourly_rate !== null
})

// Watch for custom equipment changes
watch(customEquipment, (newValue) => {
  if (newValue) {
    const customItems = newValue.split('\n').filter(item => item.trim())
    // Remove existing custom items and add new ones
    form.value.equipment = form.value.equipment.filter(item => 
      availableCameras.includes(item) || additionalEquipment.includes(item)
    )
    form.value.equipment.push(...customItems)
  }
})

// Methods
const handleSubmit = () => {
  if (isFormValid.value) {
    emit('save', { ...form.value })
  }
}

// Initialize form with photographer data if editing
onMounted(() => {
  if (props.isEdit && props.photographer) {
    Object.keys(form.value).forEach(key => {
      if (props.photographer[key] !== undefined) {
        form.value[key] = props.photographer[key]
      }
    })
    
    // Extract custom equipment
    const customItems = form.value.equipment.filter(item => 
      !availableCameras.includes(item) && !additionalEquipment.includes(item)
    )
    if (customItems.length > 0) {
      customEquipment.value = customItems.join('\n')
    }
  }
})
</script>