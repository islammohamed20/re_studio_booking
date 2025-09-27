<template>
  <div class="p-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Photographers</h1>
        <p class="text-gray-600">Manage your photography team</p>
      </div>
      <button
        @click="openModal()"
        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
      >
        <Icon name="plus" class="w-5 h-5" />
        <span>Add Photographer</span>
      </button>
    </div>

    <!-- Search and Filters -->
    <div class="bg-white rounded-lg shadow-sm border p-4 mb-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0 md:space-x-4">
        <div class="flex-1 max-w-md">
          <div class="relative">
            <Icon name="search" class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search photographers..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        
        <div class="flex space-x-3">
          <select
            v-model="selectedSpecialty"
            class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Specialties</option>
            <option value="Portrait">Portrait</option>
            <option value="Wedding">Wedding</option>
            <option value="Event">Event</option>
            <option value="Commercial">Commercial</option>
            <option value="Product">Product</option>
            <option value="Fashion">Fashion</option>
          </select>
          
          <select
            v-model="selectedStatus"
            class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Status</option>
            <option value="Active">Active</option>
            <option value="Busy">Busy</option>
            <option value="Vacation">On Vacation</option>
            <option value="Inactive">Inactive</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Photographers Grid -->
    <div class="bg-white rounded-lg shadow-sm border">
      <!-- Loading State -->
      <div v-if="loading" class="p-8 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p class="text-gray-500 mt-2">Loading photographers...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredPhotographers.length === 0" class="p-8 text-center">
        <Icon name="users" class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No photographers found</h3>
        <p class="text-gray-500 mb-4">
          {{ searchQuery ? 'Try adjusting your search criteria' : 'Get started by adding your first photographer' }}
        </p>
        <button
          v-if="!searchQuery"
          @click="openModal()"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Add Photographer
        </button>
      </div>

      <!-- Photographers Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
        <div
          v-for="photographer in paginatedPhotographers"
          :key="photographer.id"
          class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
        >
          <!-- Photographer Header -->
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center space-x-3">
              <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold text-lg">
                {{ photographer.name.charAt(0) }}
              </div>
              <div>
                <h3 class="font-semibold text-gray-900">{{ photographer.name }}</h3>
                <p class="text-sm text-gray-500">{{ photographer.specialty }}</p>
              </div>
            </div>
            
            <div class="relative">
              <button
                @click="toggleDropdown(photographer.id)"
                class="text-gray-400 hover:text-gray-600"
              >
                <Icon name="dots-vertical" class="w-5 h-5" />
              </button>
              
              <div
                v-if="activeDropdown === photographer.id"
                class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border"
              >
                <button
                  @click="openModal(photographer)"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Edit Photographer
                </button>
                <button
                  @click="viewPortfolio(photographer)"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  View Portfolio
                </button>
                <button
                  @click="viewSchedule(photographer)"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  View Schedule
                </button>
                <hr class="my-1">
                <button
                  @click="deletePhotographer(photographer)"
                  class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>

          <!-- Status Badge -->
          <div class="mb-4">
            <span
              :class="getStatusClass(photographer.status)"
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
            >
              {{ photographer.status }}
            </span>
          </div>

          <!-- Contact Info -->
          <div class="space-y-2 mb-4">
            <div class="flex items-center text-sm text-gray-600">
              <Icon name="mail" class="w-4 h-4 mr-2" />
              <span>{{ photographer.email }}</span>
            </div>
            <div class="flex items-center text-sm text-gray-600">
              <Icon name="phone" class="w-4 h-4 mr-2" />
              <span>{{ photographer.phone }}</span>
            </div>
          </div>

          <!-- Experience & Rating -->
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p class="text-xs text-gray-500">Experience</p>
              <p class="font-semibold text-gray-900">{{ photographer.experience }} years</p>
            </div>
            <div>
              <p class="text-xs text-gray-500">Rating</p>
              <div class="flex items-center">
                <span class="font-semibold text-gray-900">{{ photographer.rating }}</span>
                <Icon name="star" class="w-4 h-4 text-yellow-400 ml-1" />
              </div>
            </div>
          </div>

          <!-- Hourly Rate -->
          <div class="mb-4">
            <p class="text-xs text-gray-500">Hourly Rate</p>
            <p class="font-semibold text-gray-900">${{ photographer.hourly_rate }}/hour</p>
          </div>

          <!-- Skills -->
          <div>
            <p class="text-xs text-gray-500 mb-2">Skills</p>
            <div class="flex flex-wrap gap-1">
              <span
                v-for="skill in photographer.skills.slice(0, 3)"
                :key="skill"
                class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800"
              >
                {{ skill }}
              </span>
              <span
                v-if="photographer.skills.length > 3"
                class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-600"
              >
                +{{ photographer.skills.length - 3 }} more
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="border-t px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-700">
            Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to {{ Math.min(currentPage * itemsPerPage, filteredPhotographers.length) }} of {{ filteredPhotographers.length }} photographers
          </div>
          <div class="flex space-x-2">
            <button
              @click="currentPage--"
              :disabled="currentPage === 1"
              class="px-3 py-1 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Previous
            </button>
            <button
              v-for="page in visiblePages"
              :key="page"
              @click="currentPage = page"
              :class="[
                'px-3 py-1 border rounded-md text-sm',
                currentPage === page
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'border-gray-300 hover:bg-gray-50'
              ]"
            >
              {{ page }}
            </button>
            <button
              @click="currentPage++"
              :disabled="currentPage === totalPages"
              class="px-3 py-1 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Photographer Modal -->
    <PhotographerModal
      v-if="showModal"
      :photographer="selectedPhotographer"
      :is-edit="isEditMode"
      @close="closeModal"
      @save="savePhotographer"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Icon from '@/components/Icon.vue'
import PhotographerModal from '@/components/Modals/PhotographerModal.vue'

// Reactive data
const loading = ref(false)
const searchQuery = ref('')
const selectedSpecialty = ref('')
const selectedStatus = ref('')
const currentPage = ref(1)
const itemsPerPage = ref(12)
const showModal = ref(false)
const selectedPhotographer = ref(null)
const isEditMode = ref(false)
const activeDropdown = ref(null)

// Mock data
const photographers = ref([
  {
    id: 1,
    name: 'Ahmed Hassan',
    email: 'ahmed.hassan@email.com',
    phone: '+1 (555) 123-4567',
    specialty: 'Wedding',
    status: 'Active',
    experience: 8,
    rating: 4.9,
    hourly_rate: 150,
    skills: ['Portrait', 'Wedding', 'Event', 'Photo Editing', 'Lighting'],
    bio: 'Experienced wedding photographer with a passion for capturing special moments.',
    portfolio_url: 'https://ahmedhassan.portfolio.com',
    availability: 'Available',
    languages: ['English', 'Arabic'],
    equipment: ['Canon 5D Mark IV', 'Sony A7R III', 'Professional Lighting Kit']
  },
  {
    id: 2,
    name: 'Sarah Johnson',
    email: 'sarah.johnson@email.com',
    phone: '+1 (555) 234-5678',
    specialty: 'Portrait',
    status: 'Busy',
    experience: 5,
    rating: 4.7,
    hourly_rate: 120,
    skills: ['Portrait', 'Fashion', 'Commercial', 'Studio Lighting'],
    bio: 'Creative portrait photographer specializing in fashion and commercial work.',
    portfolio_url: 'https://sarahjohnson.com',
    availability: 'Busy until Dec 15',
    languages: ['English', 'French'],
    equipment: ['Nikon D850', 'Profoto Lighting', 'Medium Format Camera']
  },
  {
    id: 3,
    name: 'Michael Chen',
    email: 'michael.chen@email.com',
    phone: '+1 (555) 345-6789',
    specialty: 'Commercial',
    status: 'Active',
    experience: 12,
    rating: 4.8,
    hourly_rate: 200,
    skills: ['Commercial', 'Product', 'Architecture', 'Drone Photography'],
    bio: 'Commercial photographer with expertise in product and architectural photography.',
    portfolio_url: 'https://michaelchen.photo',
    availability: 'Available',
    languages: ['English', 'Mandarin'],
    equipment: ['Phase One XF', 'DJI Mavic Pro', 'Broncolor Lighting']
  },
  {
    id: 4,
    name: 'Emily Rodriguez',
    email: 'emily.rodriguez@email.com',
    phone: '+1 (555) 456-7890',
    specialty: 'Event',
    status: 'Vacation',
    experience: 6,
    rating: 4.6,
    hourly_rate: 130,
    skills: ['Event', 'Corporate', 'Photojournalism', 'Low Light'],
    bio: 'Event photographer specializing in corporate events and conferences.',
    portfolio_url: 'https://emilyrodriguez.photos',
    availability: 'On vacation until Jan 5',
    languages: ['English', 'Spanish'],
    equipment: ['Canon 1DX Mark III', 'Fast Lenses', 'Wireless Flash System']
  },
  {
    id: 5,
    name: 'David Kim',
    email: 'david.kim@email.com',
    phone: '+1 (555) 567-8901',
    specialty: 'Product',
    status: 'Active',
    experience: 4,
    rating: 4.5,
    hourly_rate: 100,
    skills: ['Product', 'E-commerce', 'Macro', 'Color Correction'],
    bio: 'Product photographer focused on e-commerce and catalog photography.',
    portfolio_url: 'https://davidkim.studio',
    availability: 'Available',
    languages: ['English', 'Korean'],
    equipment: ['Sony A7R IV', 'Macro Lenses', 'Copy Stand Setup']
  },
  {
    id: 6,
    name: 'Lisa Thompson',
    email: 'lisa.thompson@email.com',
    phone: '+1 (555) 678-9012',
    specialty: 'Fashion',
    status: 'Active',
    experience: 10,
    rating: 4.9,
    hourly_rate: 180,
    skills: ['Fashion', 'Beauty', 'Editorial', 'Retouching'],
    bio: 'Fashion photographer with editorial experience for major magazines.',
    portfolio_url: 'https://lisathompson.fashion',
    availability: 'Available',
    languages: ['English', 'Italian'],
    equipment: ['Hasselblad H6D', 'Fashion Lighting Kit', 'Tethering Setup']
  }
])

// Computed properties
const filteredPhotographers = computed(() => {
  return photographers.value.filter(photographer => {
    const matchesSearch = photographer.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         photographer.email.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         photographer.specialty.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    const matchesSpecialty = !selectedSpecialty.value || photographer.specialty === selectedSpecialty.value
    const matchesStatus = !selectedStatus.value || photographer.status === selectedStatus.value
    
    return matchesSearch && matchesSpecialty && matchesStatus
  })
})

const totalPages = computed(() => {
  return Math.ceil(filteredPhotographers.value.length / itemsPerPage.value)
})

const paginatedPhotographers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredPhotographers.value.slice(start, end)
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
      pages.push('...', total)
    } else if (current >= total - 3) {
      pages.push(1, '...')
      for (let i = total - 4; i <= total; i++) {
        pages.push(i)
      }
    } else {
      pages.push(1, '...')
      for (let i = current - 1; i <= current + 1; i++) {
        pages.push(i)
      }
      pages.push('...', total)
    }
  }
  
  return pages
})

// Methods
const getStatusClass = (status) => {
  const classes = {
    'Active': 'bg-green-100 text-green-800',
    'Busy': 'bg-yellow-100 text-yellow-800',
    'Vacation': 'bg-blue-100 text-blue-800',
    'Inactive': 'bg-gray-100 text-gray-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const openModal = (photographer = null) => {
  selectedPhotographer.value = photographer
  isEditMode.value = !!photographer
  showModal.value = true
  activeDropdown.value = null
}

const closeModal = () => {
  showModal.value = false
  selectedPhotographer.value = null
  isEditMode.value = false
}

const savePhotographer = (photographerData) => {
  if (isEditMode.value) {
    // Update existing photographer
    const index = photographers.value.findIndex(p => p.id === selectedPhotographer.value.id)
    if (index !== -1) {
      photographers.value[index] = { ...photographers.value[index], ...photographerData }
    }
  } else {
    // Add new photographer
    const newPhotographer = {
      id: Date.now(),
      ...photographerData
    }
    photographers.value.unshift(newPhotographer)
  }
  closeModal()
}

const toggleDropdown = (photographerId) => {
  activeDropdown.value = activeDropdown.value === photographerId ? null : photographerId
}

const viewPortfolio = (photographer) => {
  window.open(photographer.portfolio_url, '_blank')
  activeDropdown.value = null
}

const viewSchedule = (photographer) => {
  // Navigate to photographer schedule page
  console.log('View schedule for:', photographer.name)
  activeDropdown.value = null
}

const deletePhotographer = (photographer) => {
  if (confirm(`Are you sure you want to delete ${photographer.name}?`)) {
    const index = photographers.value.findIndex(p => p.id === photographer.id)
    if (index !== -1) {
      photographers.value.splice(index, 1)
    }
  }
  activeDropdown.value = null
}

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    activeDropdown.value = null
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  loading.value = true
  
  // Simulate loading
  setTimeout(() => {
    loading.value = false
  }, 1000)
})
</script>