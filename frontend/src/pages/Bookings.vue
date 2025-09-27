<template>
  <div class="p-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Bookings</h1>
        <p class="text-gray-600 mt-1">Manage all studio bookings</p>
      </div>
      <button
        @click="showCreateModal = true"
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
      >
        <Icon name="plus" class="w-4 h-4" />
        New Booking
      </button>
    </div>

    <!-- Filters and Search -->
    <div class="bg-white rounded-lg shadow mb-6 p-4">
      <div class="flex flex-wrap items-center gap-4">
        <!-- Search -->
        <div class="flex-1 min-w-64">
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search bookings..."
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
          <option value="Pending">Pending</option>
          <option value="Confirmed">Confirmed</option>
          <option value="Completed">Completed</option>
          <option value="Cancelled">Cancelled</option>
        </select>

        <!-- Date Filter -->
        <input
          v-model="dateFilter"
          type="date"
          class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />

        <!-- Clear Filters -->
        <button
          @click="clearFilters"
          class="px-3 py-2 text-gray-600 hover:text-gray-800"
        >
          Clear Filters
        </button>
      </div>
    </div>

    <!-- Bookings Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Client
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Service
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date & Time
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Photographer
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="loading" v-for="i in 5" :key="i" class="animate-pulse">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-gray-200 rounded-full"></div>
                  <div class="ml-4">
                    <div class="h-4 bg-gray-200 rounded w-24 mb-2"></div>
                    <div class="h-3 bg-gray-200 rounded w-32"></div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="h-4 bg-gray-200 rounded w-20"></div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="h-4 bg-gray-200 rounded w-24"></div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="h-4 bg-gray-200 rounded w-20"></div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="h-6 bg-gray-200 rounded w-16"></div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="h-4 bg-gray-200 rounded w-16"></div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <div class="h-8 bg-gray-200 rounded w-20 ml-auto"></div>
              </td>
            </tr>
            
            <tr v-else-if="filteredBookings.length === 0">
              <td colspan="7" class="px-6 py-12 text-center text-gray-500">
                <Icon name="calendar" class="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p class="text-lg font-medium">No bookings found</p>
                <p class="text-sm">Try adjusting your search or filters</p>
              </td>
            </tr>
            
            <tr v-else v-for="booking in filteredBookings" :key="booking.name" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <span class="text-blue-600 font-medium text-sm">
                      {{ getInitials(booking.client_name) }}
                    </span>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">{{ booking.client_name }}</div>
                    <div class="text-sm text-gray-500">{{ booking.client_email }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ booking.service_name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ formatDate(booking.booking_date) }}</div>
                <div class="text-sm text-gray-500">{{ booking.booking_time }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ booking.photographer_name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(booking.status)" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                  {{ booking.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">${{ booking.total_amount }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button
                    @click="viewBooking(booking)"
                    class="text-blue-600 hover:text-blue-900"
                  >
                    View
                  </button>
                  <button
                    @click="editBooking(booking)"
                    class="text-gray-600 hover:text-gray-900"
                  >
                    Edit
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
        <div class="flex-1 flex justify-between sm:hidden">
          <button
            :disabled="currentPage === 1"
            @click="currentPage--"
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            Previous
          </button>
          <button
            :disabled="currentPage === totalPages"
            @click="currentPage++"
            class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            Next
          </button>
        </div>
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p class="text-sm text-gray-700">
              Showing <span class="font-medium">{{ startItem }}</span> to <span class="font-medium">{{ endItem }}</span> of
              <span class="font-medium">{{ totalItems }}</span> results
            </p>
          </div>
          <div>
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
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <BookingModal
      v-if="showCreateModal || showEditModal"
      :booking="selectedBooking"
      :isEdit="showEditModal"
      @close="closeModal"
      @save="handleSave"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import Icon from '@/components/Icon.vue'
import BookingModal from '@/components/Modals/BookingModal.vue'

// Reactive data
const bookings = ref([])
const loading = ref(true)
const searchQuery = ref('')
const statusFilter = ref('')
const dateFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 10
const showCreateModal = ref(false)
const showEditModal = ref(false)
const selectedBooking = ref(null)

// Mock data for demonstration
const mockBookings = [
  {
    name: 'BOOK-001',
    client_name: 'John Doe',
    client_email: 'john@example.com',
    service_name: 'Wedding Photography',
    booking_date: '2024-02-15',
    booking_time: '10:00 AM',
    photographer_name: 'Sarah Wilson',
    status: 'Confirmed',
    total_amount: 1500
  },
  {
    name: 'BOOK-002',
    client_name: 'Jane Smith',
    client_email: 'jane@example.com',
    service_name: 'Portrait Session',
    booking_date: '2024-02-16',
    booking_time: '2:00 PM',
    photographer_name: 'Mike Johnson',
    status: 'Pending',
    total_amount: 300
  },
  {
    name: 'BOOK-003',
    client_name: 'Bob Wilson',
    client_email: 'bob@example.com',
    service_name: 'Event Photography',
    booking_date: '2024-02-14',
    booking_time: '6:00 PM',
    photographer_name: 'Lisa Brown',
    status: 'Completed',
    total_amount: 800
  }
]

// Computed properties
const filteredBookings = computed(() => {
  let filtered = bookings.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(booking =>
      booking.client_name.toLowerCase().includes(query) ||
      booking.service_name.toLowerCase().includes(query) ||
      booking.photographer_name.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(booking => booking.status === statusFilter.value)
  }

  if (dateFilter.value) {
    filtered = filtered.filter(booking => booking.booking_date === dateFilter.value)
  }

  return filtered
})

const totalItems = computed(() => filteredBookings.value.length)
const totalPages = computed(() => Math.ceil(totalItems.value / itemsPerPage))
const startItem = computed(() => (currentPage.value - 1) * itemsPerPage + 1)
const endItem = computed(() => Math.min(currentPage.value * itemsPerPage, totalItems.value))

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
  const statusMap = {
    'Confirmed': 'bg-green-100 text-green-800',
    'Pending': 'bg-yellow-100 text-yellow-800',
    'Cancelled': 'bg-red-100 text-red-800',
    'Completed': 'bg-blue-100 text-blue-800'
  }
  return statusMap[status] || statusMap['Pending']
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const clearFilters = () => {
  searchQuery.value = ''
  statusFilter.value = ''
  dateFilter.value = ''
  currentPage.value = 1
}

const viewBooking = (booking) => {
  // Navigate to booking detail page
  console.log('View booking:', booking)
}

const editBooking = (booking) => {
  selectedBooking.value = booking
  showEditModal.value = true
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  selectedBooking.value = null
}

const handleSave = (bookingData) => {
  // Handle save logic here
  console.log('Save booking:', bookingData)
  closeModal()
  // Refresh bookings list
}

// Load bookings on mount
onMounted(() => {
  // Simulate API call
  setTimeout(() => {
    bookings.value = mockBookings
    loading.value = false
  }, 1000)
})
</script>