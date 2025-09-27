<template>
  <div class="p-6">
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
      <p class="text-gray-600 mt-2">Welcome to Re Studio Booking Management</p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <StatsCard
        title="Total Bookings"
        :value="stats.totalBookings"
        icon="calendar"
        color="blue"
        :loading="statsLoading"
      />
      <StatsCard
        title="Active Clients"
        :value="stats.activeClients"
        icon="users"
        color="green"
        :loading="statsLoading"
      />
      <StatsCard
        title="Photographers"
        :value="stats.photographers"
        icon="camera"
        color="purple"
        :loading="statsLoading"
      />
      <StatsCard
        title="Studios"
        :value="stats.studios"
        icon="building"
        color="orange"
        :loading="statsLoading"
      />
    </div>

    <!-- Charts and Recent Activity -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- Bookings Chart -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Bookings Overview</h3>
        <div class="h-64 flex items-center justify-center text-gray-500">
          <div v-if="chartLoading" class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <div v-else>Chart will be implemented here</div>
        </div>
      </div>

      <!-- Recent Bookings -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Recent Bookings</h3>
          <router-link
            to="/bookings"
            class="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            View All
          </router-link>
        </div>
        <div class="space-y-4">
          <div v-if="recentBookingsLoading" class="animate-pulse">
            <div v-for="i in 3" :key="i" class="flex items-center space-x-3 p-3">
              <div class="w-10 h-10 bg-gray-200 rounded-full"></div>
              <div class="flex-1">
                <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div class="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            </div>
          </div>
          <div v-else-if="recentBookings.length === 0" class="text-gray-500 text-center py-8">
            No recent bookings
          </div>
          <div v-else>
            <BookingItem
              v-for="booking in recentBookings"
              :key="booking.name"
              :booking="booking"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <QuickActionButton
          to="/bookings/new"
          icon="plus"
          label="New Booking"
          description="Create a new booking"
        />
        <QuickActionButton
          to="/clients/new"
          icon="users"
          label="Add Client"
          description="Register new client"
        />
        <QuickActionButton
          to="/photographers/new"
          icon="camera"
          label="Add Photographer"
          description="Register photographer"
        />
        <QuickActionButton
          to="/studios/new"
          icon="building"
          label="Add Studio"
          description="Register new studio"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import StatsCard from '@/components/Dashboard/StatsCard.vue'
import BookingItem from '@/components/Dashboard/BookingItem.vue'
import QuickActionButton from '@/components/Dashboard/QuickActionButton.vue'

const stats = ref({
  totalBookings: 0,
  activeClients: 0,
  photographers: 0,
  studios: 0
})

const recentBookings = ref([])
const statsLoading = ref(true)
const chartLoading = ref(true)
const recentBookingsLoading = ref(true)

// Resources
const statsResource = createResource({
  url: 'frappe.client.get_count',
  onSuccess(data) {
    // This will be implemented with actual API calls
    stats.value = {
      totalBookings: Math.floor(Math.random() * 100),
      activeClients: Math.floor(Math.random() * 50),
      photographers: Math.floor(Math.random() * 20),
      studios: Math.floor(Math.random() * 10)
    }
    statsLoading.value = false
  },
  onError() {
    statsLoading.value = false
  }
})

const recentBookingsResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Booking',
    limit: 5,
    order_by: 'creation desc'
  },
  onSuccess(data) {
    recentBookings.value = data || []
    recentBookingsLoading.value = false
  },
  onError() {
    recentBookingsLoading.value = false
  }
})

onMounted(() => {
  // Load dashboard data
  setTimeout(() => {
    statsLoading.value = false
    chartLoading.value = false
    recentBookingsLoading.value = false
  }, 1000)
})
</script>