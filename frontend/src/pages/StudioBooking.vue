<template>
  <div class="max-w-6xl mx-auto p-6">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">حجز الاستوديو</h1>
      <p class="text-gray-600">اختر الاستوديو والوقت المناسب لجلسة التصوير</p>
    </div>

    <!-- Studio Selection -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      <div class="lg:col-span-2">
        <Card title="اختيار الاستوديو" class="mb-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div 
              v-for="studio in studios" 
              :key="studio.name"
              class="border rounded-lg p-4 cursor-pointer transition-all hover:shadow-md"
              :class="selectedStudio === studio.name ? 'border-blue-500 bg-blue-50' : 'border-gray-200'"
              @click="selectedStudio = studio.name"
            >
              <div class="flex items-center justify-between mb-2">
                <h3 class="font-semibold text-lg">{{ studio.title }}</h3>
                <Badge :label="studio.status" :theme="studio.status === 'متاح' ? 'green' : 'red'" />
              </div>
              <p class="text-gray-600 text-sm mb-3">{{ studio.description }}</p>
              <div class="flex items-center justify-between">
                <span class="text-lg font-bold text-blue-600">{{ studio.price }} ريال/ساعة</span>
                <Button 
                  size="sm" 
                  :theme="selectedStudio === studio.name ? 'blue' : 'gray'"
                  :variant="selectedStudio === studio.name ? 'solid' : 'outline'"
                >
                  {{ selectedStudio === studio.name ? 'محدد' : 'اختيار' }}
                </Button>
              </div>
            </div>
          </div>
        </Card>

        <!-- Date and Time Selection -->
        <Card title="اختيار التاريخ والوقت" v-if="selectedStudio">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">التاريخ</label>
              <input 
                type="date" 
                v-model="selectedDate"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                :min="today"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">الوقت</label>
              <select 
                v-model="selectedTime"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">اختر الوقت</option>
                <option v-for="time in availableTimes" :key="time" :value="time">{{ time }}</option>
              </select>
            </div>
          </div>
        </Card>
      </div>

      <!-- Booking Summary -->
      <div class="lg:col-span-1">
        <Card title="ملخص الحجز" class="sticky top-6">
          <div v-if="!selectedStudio" class="text-center text-gray-500 py-8">
            اختر استوديو لعرض ملخص الحجز
          </div>
          <div v-else class="space-y-4">
            <div class="border-b pb-4">
              <h4 class="font-semibold">{{ getSelectedStudio()?.title }}</h4>
              <p class="text-sm text-gray-600">{{ getSelectedStudio()?.description }}</p>
            </div>
            
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-gray-600">التاريخ:</span>
                <span>{{ selectedDate || 'غير محدد' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">الوقت:</span>
                <span>{{ selectedTime || 'غير محدد' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">المدة:</span>
                <span>ساعة واحدة</span>
              </div>
              <div class="flex justify-between font-semibold text-lg border-t pt-2">
                <span>المجموع:</span>
                <span class="text-blue-600">{{ getSelectedStudio()?.price }} ريال</span>
              </div>
            </div>

            <Button 
              class="w-full mt-6" 
              theme="blue" 
              variant="solid"
              :disabled="!selectedDate || !selectedTime"
              @click="showBookingDialog = true"
            >
              تأكيد الحجز
            </Button>
          </div>
        </Card>
      </div>
    </div>

    <!-- Booking Dialog -->
    <Dialog 
      title="تأكيد الحجز" 
      v-model="showBookingDialog"
      :dismissable="true"
    >
      <div class="space-y-4">
        <div class="bg-gray-50 p-4 rounded-lg">
          <h4 class="font-semibold mb-2">تفاصيل الحجز:</h4>
          <div class="space-y-1 text-sm">
            <p><strong>الاستوديو:</strong> {{ getSelectedStudio()?.title }}</p>
            <p><strong>التاريخ:</strong> {{ selectedDate }}</p>
            <p><strong>الوقت:</strong> {{ selectedTime }}</p>
            <p><strong>المبلغ:</strong> {{ getSelectedStudio()?.price }} ريال</p>
          </div>
        </div>

        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">اسم العميل</label>
            <input 
              type="text" 
              v-model="customerName"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="أدخل اسم العميل"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">رقم الهاتف</label>
            <input 
              type="tel" 
              v-model="customerPhone"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="أدخل رقم الهاتف"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">ملاحظات إضافية</label>
            <textarea 
              v-model="notes"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="أي ملاحظات خاصة بالجلسة..."
            ></textarea>
          </div>
        </div>

        <div class="flex space-x-3 pt-4">
          <Button 
            theme="blue" 
            variant="solid" 
            class="flex-1"
            @click="confirmBooking"
            :loading="bookingResource.loading"
          >
            تأكيد الحجز
          </Button>
          <Button 
            theme="gray" 
            variant="outline" 
            @click="showBookingDialog = false"
          >
            إلغاء
          </Button>
        </div>
      </div>
    </Dialog>

    <!-- Success Toast -->
    <div 
      v-if="showSuccessMessage"
      class="fixed bottom-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg"
    >
      تم تأكيد الحجز بنجاح!
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Dialog, Button, Card, Badge } from 'frappe-ui'
import { createResource } from 'frappe-ui'

// Reactive data
const selectedStudio = ref('')
const selectedDate = ref('')
const selectedTime = ref('')
const showBookingDialog = ref(false)
const showSuccessMessage = ref(false)
const customerName = ref('')
const customerPhone = ref('')
const notes = ref('')

// Sample data - في التطبيق الحقيقي ستأتي من API
const studios = ref([
  {
    name: 'studio_1',
    title: 'استوديو الضوء الذهبي',
    description: 'استوديو مجهز بأحدث معدات الإضاءة المهنية',
    price: 150,
    status: 'متاح'
  },
  {
    name: 'studio_2', 
    title: 'استوديو البورتريه',
    description: 'مخصص لجلسات التصوير الشخصي والعائلي',
    price: 120,
    status: 'متاح'
  },
  {
    name: 'studio_3',
    title: 'استوديو المنتجات',
    description: 'مثالي لتصوير المنتجات والإعلانات التجارية',
    price: 200,
    status: 'محجوز'
  },
  {
    name: 'studio_4',
    title: 'استوديو الأزياء',
    description: 'مساحة واسعة مع خلفيات متنوعة لتصوير الأزياء',
    price: 180,
    status: 'متاح'
  }
])

const availableTimes = ref([
  '09:00', '10:00', '11:00', '12:00', '13:00', 
  '14:00', '15:00', '16:00', '17:00', '18:00', '19:00'
])

// Computed
const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

// Methods
const getSelectedStudio = () => {
  return studios.value.find(studio => studio.name === selectedStudio.value)
}

// Resource for booking
const bookingResource = createResource({
  url: 'api/method/re_studio_booking.api.create_booking',
  makeParams() {
    return {
      studio: selectedStudio.value,
      date: selectedDate.value,
      time: selectedTime.value,
      customer_name: customerName.value,
      customer_phone: customerPhone.value,
      notes: notes.value
    }
  },
  onSuccess() {
    showBookingDialog.value = false
    showSuccessMessage.value = true
    // Reset form
    selectedStudio.value = ''
    selectedDate.value = ''
    selectedTime.value = ''
    customerName.value = ''
    customerPhone.value = ''
    notes.value = ''
    
    setTimeout(() => {
      showSuccessMessage.value = false
    }, 3000)
  }
})

const confirmBooking = () => {
  if (!customerName.value || !customerPhone.value) {
    alert('يرجى ملء جميع البيانات المطلوبة')
    return
  }
  bookingResource.submit()
}

onMounted(() => {
  // يمكن هنا تحميل البيانات من API
})
</script>

<style scoped>
/* إضافة أي أنماط مخصصة هنا */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>