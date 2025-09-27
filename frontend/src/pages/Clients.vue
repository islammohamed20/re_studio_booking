<template>
  <div class="p-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Clients</h1>
        <p class="text-gray-600 mt-1">Manage your client database</p>
      </div>
      <button
        @click="showCreateModal = true"
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
      >
        <Icon name="plus" class="w-4 h-4" />
        Add Client
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
              placeholder="Search clients..."
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
          <option value="">All Clients</option>
          <option value="Active">Active</option>
          <option value="Inactive">Inactive</option>
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

    <!-- Clients Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <!-- Loading State -->
      <div v-if="loading" v-for="i in 8" :key="i" class="bg-white rounded-lg shadow p-6 animate-pulse">
        <div class="flex items-center space-x-4">
          <div class="w-12 h-12 bg-gray-200 rounded-full"></div>
          <div class="flex-1">
            <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div class="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
        <div class="mt-4 space-y-2">
          <div class="h-3 bg-gray-200 rounded"></div>
          <div class="h-3 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>

      <!-- No Results -->
      <div v-else-if="filteredClients.length === 0" class="col-span-full">
        <div class="text-center py-12">
          <Icon name="users" class="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p class="text-lg font-medium text-gray-900">No clients found</p>
          <p class="text-sm text-gray-500">Try adjusting your search or add a new client</p>
        </div>
      </div>

      <!-- Client Cards -->
      <div
        v-else
        v-for="client in paginatedClients"
        :key="client.name"
        class="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6"
      >
        <!-- Client Header -->
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center space-x-3">
            <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <span class="text-blue-600 font-medium text-lg">
                {{ getInitials(client.name) }}
              </span>
            </div>
            <div>
              <h3 class="text-lg font-medium text-gray-900">{{ client.name }}</h3>
              <span :class="getStatusClass(client.status)" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium">
                {{ client.status }}
              </span>
            </div>
          </div>
          
          <!-- Actions Dropdown -->
          <div class="relative">
            <button
              @click="toggleDropdown(client.name)"
              class="text-gray-400 hover:text-gray-600"
            >
              <Icon name="dots-vertical" class="w-5 h-5" />
            </button>
            <div
              v-if="activeDropdown === client.name"
              class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border"
            >
              <div class="py-1">
                <button
                  @click="viewClient(client)"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  View Details
                </button>
                <button
                  @click="editClient(client)"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Edit Client
                </button>
                <button
                  @click="viewBookings(client)"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  View Bookings
                </button>
                <hr class="my-1">
                <button
                  @click="deleteClient(client)"
                  class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  Delete Client
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Client Info -->
        <div class="space-y-2">
          <div class="flex items-center text-sm text-gray-600">
            <Icon name="mail" class="w-4 h-4 mr-2" />
            <span class="truncate">{{ client.email }}</span>
          </div>
          <div class="flex items-center text-sm text-gray-600">
            <Icon name="phone" class="w-4 h-4 mr-2" />
            <span>{{ client.phone || 'No phone' }}</span>
          </div>
          <div class="flex items-center text-sm text-gray-600">
            <Icon name="calendar" class="w-4 h-4 mr-2" />
            <span>{{ client.total_bookings }} bookings</span>
          </div>
        </div>

        <!-- Client Stats -->
        <div class="mt-4 pt-4 border-t border-gray-200">
          <div class="flex justify-between text-sm">
            <div class="text-center">
              <div class="font-medium text-gray-900">${{ client.total_spent }}</div>
              <div class="text-gray-500">Total Spent</div>
            </div>
            <div class="text-center">
              <div class="font-medium text-gray-900">{{ formatDate(client.last_booking) }}</div>
              <div class="text-gray-500">Last Booking</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="mt-8 flex items-center justify-center">
      <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
        <button
          :disabled="currentPage === 1"
          @click="currentPage--"
          class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
        >
          Previous
        </button>
        <button
          v-for="page in visiblePages"
          :key="page"
          @click="currentPage = page"
          :class="[
            page === currentPage
              ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
              : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50',
            'relative inline-flex items-center px-4 py-2 border text-sm font-medium'
          ]"
        >
          {{ page }}
        </button>
        <button
          :disabled="currentPage === totalPages"
          @click="currentPage++"
          class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
        >
          Next
        </button>
      </nav>
    </div>

    <!-- Create/Edit Modal -->
    <ClientModal
      v-if="showCreateModal || showEditModal"
      :client="selectedClient"
      :isEdit="showEditModal"
      @close="closeModal"
      @save="handleSave"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import Icon from '@/components/Icon.vue'
import ClientModal from '@/components/Modals/ClientModal.vue'

// Reactive data
const clients = ref([])
const loading = ref(true)
const searchQuery = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 12
const showCreateModal = ref(false)
const showEditModal = ref(false)
const selectedClient = ref(null)
const activeDropdown = ref(null)

// Mock data
const mockClients = [
  {
    name: 'John Doe',
    email: 'john@example.com',
    phone: '+1 234 567 8900',
    status: 'Active',
    total_bookings: 5,
    total_spent: 2500,
    last_booking: '2024-02-10',
    created_date: '2023-08-15'
  },
  {
    name: 'Jane Smith',
    email: 'jane@example.com',
    phone: '+1 234 567 8901',
    status: 'Active',
    total_bookings: 3,
    total_spent: 1200,
    last_booking: '2024-02-08',
    created_date: '2023-09-20'
  },
  {
    name: 'Bob Wilson',
    email: 'bob@example.com',
    phone: '+1 234 567 8902',
    status: 'Inactive',
    total_bookings: 1,
    total_spent: 300,
    last_booking: '2023-12-15',
    created_date: '2023-11-10'
  },
  {
    name: 'Alice Johnson',
    email: 'alice@example.com',
    phone: '+1 234 567 8903',
    status: 'Active',
    total_bookings: 8,
    total_spent: 4200,
    last_booking: '2024-02-12',
    created_date: '2023-06-05'
  }
]

// Computed properties
const filteredClients = computed(() => {
  let filtered = clients.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(client =>
      client.name.toLowerCase().includes(query) ||
      client.email.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(client => client.status === statusFilter.value)
  }

  return filtered
})

const totalPages = computed(() => Math.ceil(filteredClients.value.length / itemsPerPage))

const paginatedClients = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredClients.value.slice(start, end)
})

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// Methods
const getInitials = (name) => {
  return name.split(' ').map(n => n[0]).join('').toUpperCase()
}

const getStatusClass = (status) => {
  return status === 'Active'
    ? 'bg-green-100 text-green-800'
    : 'bg-gray-100 text-gray-800'
}

const formatDate = (date) => {
  if (!date) return 'Never'
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const clearFilters = () => {
  searchQuery.value = ''
  statusFilter.value = ''
  currentPage.value = 1
}

const toggleDropdown = (clientName) => {
  activeDropdown.value = activeDropdown.value === clientName ? null : clientName
}

const viewClient = (client) => {
  console.log('View client:', client)
  activeDropdown.value = null
}

const editClient = (client) => {
  selectedClient.value = client
  showEditModal.value = true
  activeDropdown.value = null
}

const viewBookings = (client) => {
  console.log('View bookings for:', client)
  activeDropdown.value = null
}

const deleteClient = (client) => {
  if (confirm(`Are you sure you want to delete ${client.name}?`)) {
    console.log('Delete client:', client)
  }
  activeDropdown.value = null
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  selectedClient.value = null
}

const handleSave = (clientData) => {
  console.log('Save client:', clientData)
  closeModal()
}

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    activeDropdown.value = null
  }
}

// Load clients on mount
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  
  // Simulate API call
  setTimeout(() => {
    clients.value = mockClients
    loading.value = false
  }, 1000)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>