<template>
  <div class="flex flex-col h-full w-64 bg-white border-r">
    <!-- Logo -->
    <div class="p-4 border-b">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"/>
          </svg>
        </div>
        <span class="font-semibold text-gray-900">Re Studio</span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 p-4 space-y-2">
      <SidebarLink
        to="/dashboard"
        icon="home"
        label="Dashboard"
      />
      <SidebarLink
        to="/bookings"
        icon="calendar"
        label="Bookings"
      />
      <SidebarLink
        to="/clients"
        icon="users"
        label="Clients"
      />
      <SidebarLink
        to="/photographers"
        icon="camera"
        label="Photographers"
      />
      <SidebarLink
        to="/studios"
        icon="building"
        label="Studios"
      />
      <SidebarLink
        to="/packages"
        icon="package"
        label="Packages"
      />
      <SidebarLink
        to="/services"
        icon="star"
        label="Services"
      />
    </nav>

    <!-- User Section -->
    <div class="p-4 border-t">
      <UserDropdown />
    </div>
  </div>
</template>

<script setup>
import SidebarLink from './SidebarLink.vue'
import UserDropdown from '../UserDropdown.vue'
</script>