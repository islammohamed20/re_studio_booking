<template>
  <component :is="iconComponent" v-bind="$attrs" />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: String
})

const iconComponent = computed(() => {
  const icons = {
    home: () => import('./Icons/HomeIcon.vue'),
    calendar: () => import('./Icons/CalendarIcon.vue'),
    users: () => import('./Icons/UsersIcon.vue'),
    camera: () => import('./Icons/CameraIcon.vue'),
    building: () => import('./Icons/BuildingIcon.vue'),
    package: () => import('./Icons/PackageIcon.vue'),
    star: () => import('./Icons/StarIcon.vue'),
    plus: () => import('./Icons/PlusIcon.vue'),
    search: () => import('./Icons/SearchIcon.vue'),
    mail: () => import('./Icons/MailIcon.vue'),
    phone: () => import('./Icons/PhoneIcon.vue'),
    'dots-vertical': () => import('./Icons/DotsVerticalIcon.vue'),
    x: () => import('./Icons/XIcon.vue'),
  }
  
  return icons[props.name] || (() => import('./Icons/HomeIcon.vue'))
})
</script>