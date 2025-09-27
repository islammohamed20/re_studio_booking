<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-11/12 max-w-2xl shadow-lg rounded-md bg-white">
      <!-- Modal Header -->
      <div class="flex items-center justify-between pb-4 border-b">
        <h3 class="text-lg font-medium text-gray-900">
          {{ isEdit ? 'Edit Client' : 'Add New Client' }}
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
          <!-- Personal Information -->
          <div class="space-y-4">
            <h4 class="text-md font-medium text-gray-900">Personal Information</h4>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Full Name *
              </label>
              <input
                v-model="form.name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter full name"
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
                placeholder="Enter email address"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Phone Number
              </label>
              <input
                v-model="form.phone"
                type="tel"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter phone number"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Date of Birth
              </label>
              <input
                v-model="form.date_of_birth"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <!-- Contact & Preferences -->
          <div class="space-y-4">
            <h4 class="text-md font-medium text-gray-900">Contact & Preferences</h4>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Address
              </label>
              <textarea
                v-model="form.address"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter address"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Preferred Contact Method
              </label>
              <select
                v-model="form.preferred_contact"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="email">Email</option>
                <option value="phone">Phone</option>
                <option value="sms">SMS</option>
              </select>
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
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Client Type
              </label>
              <select
                v-model="form.client_type"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Individual">Individual</option>
                <option value="Corporate">Corporate</option>
                <option value="Wedding">Wedding</option>
                <option value="Event">Event</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Additional Information -->
        <div class="mt-6">
          <h4 class="text-md font-medium text-gray-900 mb-4">Additional Information</h4>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Company Name
              </label>
              <input
                v-model="form.company"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter company name (if applicable)"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Referral Source
              </label>
              <select
                v-model="form.referral_source"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select source</option>
                <option value="Google">Google Search</option>
                <option value="Social Media">Social Media</option>
                <option value="Referral">Friend Referral</option>
                <option value="Website">Website</option>
                <option value="Advertisement">Advertisement</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          <div class="mt-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Notes
            </label>
            <textarea
              v-model="form.notes"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Additional notes about the client..."
            ></textarea>
          </div>
        </div>

        <!-- Marketing Preferences -->
        <div class="mt-6">
          <h4 class="text-md font-medium text-gray-900 mb-4">Marketing Preferences</h4>
          
          <div class="space-y-3">
            <label class="flex items-center">
              <input
                v-model="form.email_marketing"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              />
              <span class="ml-2 text-sm text-gray-700">Send marketing emails</span>
            </label>
            
            <label class="flex items-center">
              <input
                v-model="form.sms_marketing"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              />
              <span class="ml-2 text-sm text-gray-700">Send SMS notifications</span>
            </label>
            
            <label class="flex items-center">
              <input
                v-model="form.newsletter"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              />
              <span class="ml-2 text-sm text-gray-700">Subscribe to newsletter</span>
            </label>
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
            {{ isEdit ? 'Update Client' : 'Add Client' }}
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
  client: {
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
  email: '',
  phone: '',
  date_of_birth: '',
  address: '',
  preferred_contact: 'email',
  status: 'Active',
  client_type: 'Individual',
  company: '',
  referral_source: '',
  notes: '',
  email_marketing: true,
  sms_marketing: false,
  newsletter: true
})

// Computed properties
const isFormValid = computed(() => {
  return form.value.name.trim() && form.value.email.trim()
})

// Methods
const handleSubmit = () => {
  if (isFormValid.value) {
    emit('save', { ...form.value })
  }
}

// Initialize form with client data if editing
onMounted(() => {
  if (props.isEdit && props.client) {
    Object.keys(form.value).forEach(key => {
      if (props.client[key] !== undefined) {
        form.value[key] = props.client[key]
      }
    })
  }
})
</script>