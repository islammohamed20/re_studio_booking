<template>
  <div class="p-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Studios</h1>
        <p class="text-gray-600 mt-1">Manage your photography studios</p>
      </div>
      <button
        @click="showCreateModal = true"
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
      >
        <Icon name="plus" class="w-4 h-4" />
        Add Studio
      </button>
    </div>

    <!-- Search and Filters -->
    <div class="bg-white rounded-lg shadow mb-6 p-4">
      <div class="flex flex-wrap items-center gap-4">
        <!-- Search -->
        <div class="flex-1 min-w-64">
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search studios..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <Icon name="search" class="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
          </div>
        </div>

        <!-- Status Filter -->
        <select
          v-model="statusFilter"
          class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">All Status</option>
          <option value="Active">Active</option>
          <option value="Maintenance">Maintenance</option>
          <option value="Inactive">Inactive</option>
        </select>

        <!-- Type Filter -->
        <select
          v-model="typeFilter"
          class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">All Types</option>
          <option value="Portrait">Portrait Studio</option>
          <option value="Wedding">Wedding Studio</option>
          <option value="Event">Event Hall</option>
          <option value="Commercial">Commercial Studio</option>
        </select>

        <!-- Clear Filters -->
        <button
          @click="clearFilters"
          class="px-3 py-2 text-gray-600 hover:text-gray-800"
        >
          Clear Filters
        </button>
      </div>
    </div>

    <!-- Studios Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Loading State -->
      <div v-if="loading" v-for="i in 6" :key="i" class="bg-white rounded-lg shadow overflow-hidden animate-pulse">
        <div class="h-48 bg-gray-200"></div>
        <div class="p-6">
          <div class="h-6 bg-gray-200 rounded mb-2"></div>
          <div class="h-4 bg-gray-200 rounded w-2/3 mb-4"></div>
          <div class="space-y-2">
            <div class="h-3 bg-gray-200 rounded"></div>
            <div class="h-3 bg-gray-200 rounded w-3/4"></div>
          </div>
        </div>
      </div>

      <!-- No Results -->
      <div v-else-if="filteredStudios.length === 0" class="col-span-full">
        <div class="text-center py-12">
          <Icon name="building" class="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p class="text-lg font-medium text-gray-900">No studios found</p>
          <p class="text-sm text-gray-500">Try adjusting your search or add a new studio</p>
        </div>
      </div>

      <!-- Studio Cards -->
      <div
        v-else
        v-for="studio in filteredStudios"
        :key="studio.name"
        class="bg-white rounded-lg shadow hover:shadow-lg transition-shadow overflow-hidden"
      >
        <!-- Studio Image -->
        <div class="h-48 bg-gradient-to-br from-blue-400 to-purple-500 relative">
          <img
            v-if="studio.image"
            :src="studio.image"
            :alt="studio.name"
            class="w-full h-full object-cover"
          />
          <div class="absolute inset-0 bg-black bg-opacity-20 flex items-center justify-center">
            <Icon name="camera" class="w-12 h-12 text-white opacity-80" />
          </div>
          
          <!-- Status Badge -->
          <div class="absolute top-4 right-4">
            <span :class="getStatusClass(studio.status)" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
              {{ studio.status }}
            </span>
          </div>

          <!-- Actions Dropdown -->
          <div class="absolute top-4 left-4">
            <div class="relative">
              <button
                @click="toggleDropdown(studio.name)"
                class="text-white hover:text-gray-200 bg-black bg-opacity-30 rounded-full p-2"
              >
                <Icon name="dots-vertical" class="w-5 h-5" />
              </button>
              <div
                v-if="activeDropdown === studio.name"
                class="absolute left-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border"
              >
                <div class="py-1">
                  <button
                    @click="viewStudio(studio)"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    View Details
                  </button>
                  <button
                    @click="editStudio(studio)"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Edit Studio
                  </button>
                  <button
                    @click="viewBookings(studio)"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    View Bookings
                  </button>
                  <hr class="my-1">
                  <button
                    @click="deleteStudio(studio)"
                    class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    Delete Studio
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Studio Info -->
        <div class="p-6">
          <div class="flex items-start justify-between mb-2">
            <h3 class="text-lg font-semibold text-gray-900">{{ studio.name }}</h3>
            <span class="text-sm text-gray-500">{{ studio.type }}</span>
          </div>
          
          <p class="text-gray-600 text-sm mb-4 line-clamp-2">{{ studio.description }}</p>

          <!-- Studio Details -->
          <div class="space-y-2 mb-4">
            <div class="flex items-center text-sm text-gray-600">
              <Icon name="users" class="w-4 h-4 mr-2" />
              <span>Capacity: {{ studio.capacity }} people</span>
            </div>
            <div class="flex items-center text-sm text-gray-600">
              <Icon name="building" class="w-4 h-4 mr-2" />
              <span>{{ studio.size }} sq ft</span>
            </div>
            <div class="flex items-center text-sm text-gray-600">
              <Icon name="star" class="w-4 h-4 mr-2" />
              <span>{{ studio.rating }}/5 ({{ studio.reviews }} reviews)</span>
            </div>
          </div>

          <!-- Pricing -->
          <div class="flex items-center justify-between pt-4 border-t border-gray-200">
            <div>
              <span class="text-2xl font-bold text-gray-900">${{ studio.hourly_rate }}</span>
              <span class="text-gray-500 text-sm">/hour</span>
            </div>
            <div class="text-right">
              <div class="text-sm font-medium text-gray-900">{{ studio.bookings_count }} bookings</div>
              <div class="text-sm text-gray-500">this month</div>
            </div>
          </div>

          <!-- Equipment Tags -->
          <div class="mt-4">
            <div class="flex flex-wrap gap-1">
              <span
                v-for="equipment in studio.equipment.slice(0, 3)"
                :key="equipment"
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                {{ equipment }}
              </span>
              <span
                v-if="studio.equipment.length > 3"
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600"
              >
                +{{ studio.equipment.length - 3 }} more
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <StudioModal
      v-if="showCreateModal || showEditModal"
      :studio="selectedStudio"
      :isEdit="showEditModal"
      @close="closeModal"
      @save="handleSave"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import Icon from '@/components/Icon.vue'
import StudioModal from '@/components/Modals/StudioModal.vue'

// Reactive data
const studios = ref([])
const loading = ref(true)
const searchQuery = ref('')
const statusFilter = ref('')
const typeFilter = ref('')
const showCreateModal = ref(false)
const showEditModal = ref(false)
const selectedStudio = ref(null)
const activeDropdown = ref(null)

// Mock data
const mockStudios = [
  {
    name: 'Main Photography Studio',
    type: 'Portrait',
    description: 'Our flagship studio with professional lighting and backdrop systems. Perfect for portrait sessions and commercial photography.',
    status: 'Active',
    capacity: 15,
    size: 800,
    hourly_rate: 150,
    rating: 4.8,
    reviews: 24,
    bookings_count: 18,
    equipment: ['Professional Lighting', 'Backdrop System', 'Props Collection', 'Makeup Station'],
    image: null
  },
  {
    name: 'Wedding Studio',
    type: 'Wedding',
    description: 'Elegant studio designed specifically for wedding photography with romantic lighting and beautiful backdrops.',
    status: 'Active',
    capacity: 25,
    size: 1200,
    hourly_rate: 200,
    rating: 4.9,
    reviews: 31,
    bookings_count: 12,
    equipment: ['Romantic Lighting', 'Wedding Backdrops', 'Flower Arrangements', 'Bridal Prep Area'],
    image: null
  },
  {
    name: 'Event Hall Studio',
    type: 'Event',
    description: 'Large space perfect for corporate events, parties, and group photography sessions.',
    status: 'Active',
    capacity: 50,
    size: 2000,
    hourly_rate: 300,
    rating: 4.7,
    reviews: 18,
    bookings_count: 8,
    equipment: ['Stage Lighting', 'Sound System', 'Projection Screen', 'Catering Area'],
    image: null
  },
  {
    name: 'Commercial Studio B',
    type: 'Commercial',
    description: 'Professional commercial photography studio with product photography setup.',
    status: 'Maintenance',
    capacity: 10,
    size: 600,
    hourly_rate: 120,
    rating: 4.6,
    reviews: 15,
    bookings_count: 0,
    equipment: ['Product Tables', 'Macro Lenses', 'Color Correction Lights', 'Seamless Paper'],
    image: null
  }
]

// Computed properties
const filteredStudios = computed(() => {
  let filtered = studios.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(studio =>
      studio.name.toLowerCase().includes(query) ||
      studio.description.toLowerCase().includes(query) ||
      studio.type.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(studio => studio.status === statusFilter.value)
  }

  if (typeFilter.value) {
    filtered = filtered.filter(studio => studio.type === typeFilter.value)
  }

  return filtered
})

// Methods
const getStatusClass = (status) => {
  const statusMap = {
    'Active': 'bg-green-100 text-green-800',
    'Maintenance': 'bg-yellow-100 text-yellow-800',
    'Inactive': 'bg-red-100 text-red-800'
  }
  return statusMap[status] || statusMap['Active']
}

const clearFilters = () => {
  searchQuery.value = ''
  statusFilter.value = ''
  typeFilter.value = ''
}

const toggleDropdown = (studioName) => {
  activeDropdown.value = activeDropdown.value === studioName ? null : studioName
}

const viewStudio = (studio) => {
  console.log('View studio:', studio)
  activeDropdown.value = null
}

const editStudio = (studio) => {
  selectedStudio.value = studio
  showEditModal.value = true
  activeDropdown.value = null
}

const viewBookings = (studio) => {
  console.log('View bookings for:', studio)
  activeDropdown.value = null
}

const deleteStudio = (studio) => {
  if (confirm(`Are you sure you want to delete ${studio.name}?`)) {
    console.log('Delete studio:', studio)
  }
  activeDropdown.value = null
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  selectedStudio.value = null
}

const handleSave = (studioData) => {
  console.log('Save studio:', studioData)
  closeModal()
}

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    activeDropdown.value = null
  }
}

// Load studios on mount
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  
  // Simulate API call
  setTimeout(() => {
    studios.value = mockStudios
    loading.value = false
  }, 1000)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>