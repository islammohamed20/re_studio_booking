<template>
  <div class="p-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Packages & Services</h1>
        <p class="text-gray-600">Manage your photography packages and services</p>
      </div>
      <div class="flex space-x-3">
        <button
          @click="openModal('service')"
          class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center space-x-2"
        >
          <Icon name="plus" class="w-5 h-5" />
          <span>Add Service</span>
        </button>
        <button
          @click="openModal('package')"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
        >
          <Icon name="plus" class="w-5 h-5" />
          <span>Add Package</span>
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="mb-6">
      <div class="border-b border-gray-200">
        <nav class="-mb-px flex space-x-8">
          <button
            @click="activeTab = 'packages'"
            :class="[
              'py-2 px-1 border-b-2 font-medium text-sm',
              activeTab === 'packages'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Packages ({{ packages.length }})
          </button>
          <button
            @click="activeTab = 'services'"
            :class="[
              'py-2 px-1 border-b-2 font-medium text-sm',
              activeTab === 'services'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Services ({{ services.length }})
          </button>
        </nav>
      </div>
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
              :placeholder="`Search ${activeTab}...`"
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        
        <div class="flex space-x-3">
          <select
            v-model="selectedCategory"
            class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Categories</option>
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
            <option value="Inactive">Inactive</option>
            <option value="Draft">Draft</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Packages Tab -->
    <div v-if="activeTab === 'packages'" class="bg-white rounded-lg shadow-sm border">
      <!-- Loading State -->
      <div v-if="loading" class="p-8 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p class="text-gray-500 mt-2">Loading packages...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredPackages.length === 0" class="p-8 text-center">
        <Icon name="package" class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No packages found</h3>
        <p class="text-gray-500 mb-4">
          {{ searchQuery ? 'Try adjusting your search criteria' : 'Get started by creating your first package' }}
        </p>
        <button
          v-if="!searchQuery"
          @click="openModal('package')"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Add Package
        </button>
      </div>

      <!-- Packages Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
        <div
          v-for="pkg in paginatedPackages"
          :key="pkg.id"
          class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
        >
          <!-- Package Header -->
          <div class="flex items-start justify-between mb-4">
            <div>
              <h3 class="font-semibold text-gray-900 text-lg">{{ pkg.name }}</h3>
              <p class="text-sm text-gray-500">{{ pkg.category }}</p>
            </div>
            
            <div class="relative">
              <button
                @click="toggleDropdown('package', pkg.id)"
                class="text-gray-400 hover:text-gray-600"
              >
                <Icon name="dots-vertical" class="w-5 h-5" />
              </button>
              
              <div
                v-if="activeDropdown === `package-${pkg.id}`"
                class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border"
              >
                <button
                  @click="openModal('package', pkg)"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Edit Package
                </button>
                <button
                  @click="duplicateItem('package', pkg)"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Duplicate
                </button>
                <hr class="my-1">
                <button
                  @click="deleteItem('package', pkg)"
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
              :class="getStatusClass(pkg.status)"
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
            >
              {{ pkg.status }}
            </span>
          </div>

          <!-- Description -->
          <p class="text-gray-600 text-sm mb-4 line-clamp-3">{{ pkg.description }}</p>

          <!-- Package Details -->
          <div class="space-y-3 mb-4">
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-500">Duration</span>
              <span class="font-medium text-gray-900">{{ pkg.duration }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-500">Sessions</span>
              <span class="font-medium text-gray-900">{{ pkg.sessions }} session{{ pkg.sessions > 1 ? 's' : '' }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-500">Photos Included</span>
              <span class="font-medium text-gray-900">{{ pkg.photos_included }}</span>
            </div>
          </div>

          <!-- Services Included -->
          <div class="mb-4">
            <p class="text-xs text-gray-500 mb-2">Services Included</p>
            <div class="flex flex-wrap gap-1">
              <span
                v-for="service in pkg.services.slice(0, 2)"
                :key="service"
                class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800"
              >
                {{ service }}
              </span>
              <span
                v-if="pkg.services.length > 2"
                class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-600"
              >
                +{{ pkg.services.length - 2 }} more
              </span>
            </div>
          </div>

          <!-- Price -->
          <div class="border-t pt-4">
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-500">Total Price</span>
              <span class="text-xl font-bold text-gray-900">${{ pkg.price }}</span>
            </div>
            <div v-if="pkg.discount > 0" class="text-xs text-green-600 text-right">
              {{ pkg.discount }}% discount applied
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Services Tab -->
    <div v-if="activeTab === 'services'" class="bg-white rounded-lg shadow-sm border">
      <!-- Loading State -->
      <div v-if="loading" class="p-8 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p class="text-gray-500 mt-2">Loading services...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredServices.length === 0" class="p-8 text-center">
        <Icon name="cog" class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No services found</h3>
        <p class="text-gray-500 mb-4">
          {{ searchQuery ? 'Try adjusting your search criteria' : 'Get started by creating your first service' }}
        </p>
        <button
          v-if="!searchQuery"
          @click="openModal('service')"
          class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
        >
          Add Service
        </button>
      </div>

      <!-- Services List -->
      <div v-else class="divide-y divide-gray-200">
        <div
          v-for="service in paginatedServices"
          :key="service.id"
          class="p-6 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-4">
                <div>
                  <h3 class="font-semibold text-gray-900">{{ service.name }}</h3>
                  <p class="text-sm text-gray-500">{{ service.category }}</p>
                </div>
                
                <span
                  :class="getStatusClass(service.status)"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                >
                  {{ service.status }}
                </span>
              </div>
              
              <p class="text-gray-600 text-sm mt-2">{{ service.description }}</p>
              
              <div class="flex items-center space-x-6 mt-3">
                <div class="flex items-center text-sm text-gray-500">
                  <Icon name="clock" class="w-4 h-4 mr-1" />
                  <span>{{ service.duration }}</span>
                </div>
                <div class="flex items-center text-sm text-gray-500">
                  <Icon name="dollar-sign" class="w-4 h-4 mr-1" />
                  <span>${{ service.price }}</span>
                </div>
                <div v-if="service.add_ons.length > 0" class="flex items-center text-sm text-gray-500">
                  <Icon name="plus" class="w-4 h-4 mr-1" />
                  <span>{{ service.add_ons.length }} add-on{{ service.add_ons.length > 1 ? 's' : '' }}</span>
                </div>
              </div>
            </div>
            
            <div class="relative">
              <button
                @click="toggleDropdown('service', service.id)"
                class="text-gray-400 hover:text-gray-600"
              >
                <Icon name="dots-vertical" class="w-5 h-5" />
              </button>
              
              <div
                v-if="activeDropdown === `service-${service.id}`"
                class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border"
              >
                <button
                  @click="openModal('service', service)"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Edit Service
                </button>
                <button
                  @click="duplicateItem('service', service)"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Duplicate
                </button>
                <hr class="my-1">
                <button
                  @click="deleteItem('service', service)"
                  class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="bg-white border-t px-6 py-4 rounded-b-lg">
      <div class="flex items-center justify-between">
        <div class="text-sm text-gray-700">
          Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to {{ Math.min(currentPage * itemsPerPage, currentItems.length) }} of {{ currentItems.length }} {{ activeTab }}
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

    <!-- Package/Service Modal -->
    <PackageServiceModal
      v-if="showModal"
      :type="modalType"
      :item="selectedItem"
      :is-edit="isEditMode"
      @close="closeModal"
      @save="saveItem"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Icon from '@/components/Icon.vue'
import PackageServiceModal from '@/components/Modals/PackageServiceModal.vue'

// Reactive data
const loading = ref(false)
const activeTab = ref('packages')
const searchQuery = ref('')
const selectedCategory = ref('')
const selectedStatus = ref('')
const currentPage = ref(1)
const itemsPerPage = ref(12)
const showModal = ref(false)
const modalType = ref('package')
const selectedItem = ref(null)
const isEditMode = ref(false)
const activeDropdown = ref(null)

// Mock data
const packages = ref([
  {
    id: 1,
    name: 'Wedding Essential Package',
    category: 'Wedding',
    status: 'Active',
    description: 'Complete wedding photography package including ceremony and reception coverage with professional editing.',
    duration: '8 hours',
    sessions: 1,
    photos_included: '200-300 edited photos',
    services: ['Ceremony Coverage', 'Reception Coverage', 'Professional Editing', 'Online Gallery'],
    price: 2500,
    discount: 0,
    add_ons: ['Engagement Session', 'Wedding Album', 'USB Drive']
  },
  {
    id: 2,
    name: 'Portrait Premium Package',
    category: 'Portrait',
    status: 'Active',
    description: 'Professional portrait session with multiple outfit changes and locations.',
    duration: '2 hours',
    sessions: 1,
    photos_included: '50-75 edited photos',
    services: ['Studio Session', 'Professional Editing', 'Online Gallery', 'Print Release'],
    price: 450,
    discount: 10,
    add_ons: ['Additional Outfits', 'Makeup Artist', 'Extra Locations']
  },
  {
    id: 3,
    name: 'Corporate Event Package',
    category: 'Event',
    status: 'Active',
    description: 'Comprehensive corporate event coverage including keynotes, networking, and team photos.',
    duration: '6 hours',
    sessions: 1,
    photos_included: '150-200 edited photos',
    services: ['Event Coverage', 'Team Photos', 'Professional Editing', 'Same Day Preview'],
    price: 1800,
    discount: 0,
    add_ons: ['Video Coverage', 'Live Streaming', 'Social Media Package']
  }
])

const services = ref([
  {
    id: 1,
    name: 'Professional Photo Editing',
    category: 'Post-Production',
    status: 'Active',
    description: 'High-quality photo editing including color correction, retouching, and artistic enhancements.',
    duration: '2-3 days turnaround',
    price: 25,
    unit: 'per photo',
    add_ons: ['Rush Delivery', 'Advanced Retouching', 'Black & White Conversion']
  },
  {
    id: 2,
    name: 'Studio Rental',
    category: 'Studio',
    status: 'Active',
    description: 'Fully equipped photography studio with professional lighting and backdrop systems.',
    duration: '1 hour minimum',
    price: 150,
    unit: 'per hour',
    add_ons: ['Equipment Rental', 'Assistant', 'Makeup Station']
  },
  {
    id: 3,
    name: 'Drone Photography',
    category: 'Aerial',
    status: 'Active',
    description: 'Professional aerial photography and videography services using certified drone operators.',
    duration: '2 hours minimum',
    price: 400,
    unit: 'per session',
    add_ons: ['4K Video', 'Raw Files', 'Extended Flight Time']
  },
  {
    id: 4,
    name: 'Makeup & Hair Styling',
    category: 'Beauty',
    status: 'Active',
    description: 'Professional makeup and hair styling services for photo shoots and events.',
    duration: '1-2 hours',
    price: 200,
    unit: 'per session',
    add_ons: ['Trial Session', 'Touch-up Kit', 'Multiple Looks']
  }
])

// Computed properties
const filteredPackages = computed(() => {
  return packages.value.filter(pkg => {
    const matchesSearch = pkg.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         pkg.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    const matchesCategory = !selectedCategory.value || pkg.category === selectedCategory.value
    const matchesStatus = !selectedStatus.value || pkg.status === selectedStatus.value
    
    return matchesSearch && matchesCategory && matchesStatus
  })
})

const filteredServices = computed(() => {
  return services.value.filter(service => {
    const matchesSearch = service.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         service.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    const matchesCategory = !selectedCategory.value || service.category === selectedCategory.value
    const matchesStatus = !selectedStatus.value || service.status === selectedStatus.value
    
    return matchesSearch && matchesCategory && matchesStatus
  })
})

const currentItems = computed(() => {
  return activeTab.value === 'packages' ? filteredPackages.value : filteredServices.value
})

const totalPages = computed(() => {
  return Math.ceil(currentItems.value.length / itemsPerPage.value)
})

const paginatedPackages = computed(() => {
  if (activeTab.value !== 'packages') return []
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredPackages.value.slice(start, end)
})

const paginatedServices = computed(() => {
  if (activeTab.value !== 'services') return []
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredServices.value.slice(start, end)
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
    'Inactive': 'bg-gray-100 text-gray-800',
    'Draft': 'bg-yellow-100 text-yellow-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const openModal = (type, item = null) => {
  modalType.value = type
  selectedItem.value = item
  isEditMode.value = !!item
  showModal.value = true
  activeDropdown.value = null
}

const closeModal = () => {
  showModal.value = false
  selectedItem.value = null
  isEditMode.value = false
  modalType.value = 'package'
}

const saveItem = (itemData) => {
  if (modalType.value === 'package') {
    if (isEditMode.value) {
      const index = packages.value.findIndex(p => p.id === selectedItem.value.id)
      if (index !== -1) {
        packages.value[index] = { ...packages.value[index], ...itemData }
      }
    } else {
      const newPackage = {
        id: Date.now(),
        ...itemData
      }
      packages.value.unshift(newPackage)
    }
  } else {
    if (isEditMode.value) {
      const index = services.value.findIndex(s => s.id === selectedItem.value.id)
      if (index !== -1) {
        services.value[index] = { ...services.value[index], ...itemData }
      }
    } else {
      const newService = {
        id: Date.now(),
        ...itemData
      }
      services.value.unshift(newService)
    }
  }
  closeModal()
}

const toggleDropdown = (type, itemId) => {
  const dropdownId = `${type}-${itemId}`
  activeDropdown.value = activeDropdown.value === dropdownId ? null : dropdownId
}

const duplicateItem = (type, item) => {
  const duplicatedItem = {
    ...item,
    id: Date.now(),
    name: `${item.name} (Copy)`,
    status: 'Draft'
  }
  
  if (type === 'package') {
    packages.value.unshift(duplicatedItem)
  } else {
    services.value.unshift(duplicatedItem)
  }
  
  activeDropdown.value = null
}

const deleteItem = (type, item) => {
  if (confirm(`Are you sure you want to delete ${item.name}?`)) {
    if (type === 'package') {
      const index = packages.value.findIndex(p => p.id === item.id)
      if (index !== -1) {
        packages.value.splice(index, 1)
      }
    } else {
      const index = services.value.findIndex(s => s.id === item.id)
      if (index !== -1) {
        services.value.splice(index, 1)
      }
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