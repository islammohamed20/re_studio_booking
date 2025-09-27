/**
 * New Booking Page JavaScript
 * Handles multi-step form navigation and booking creation
 */

// Global variables
let currentStep = 1;
let totalSteps = 5;
let bookingData = {
    booking_type: '',
    service: '',
    service_package: '',
    booking_date: '',
    start_time: '',
    end_time: '',
    photographer: '',
    client_name: '',
    phone: '',
    client_email: '',
    payment_method: '',
    notes: ''
};

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('New Booking page loaded');
    updateStepIndicator();
    setMinDate();
});

// Set minimum date to today
function setMinDate() {
    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('booking-date');
    if (dateInput) {
        dateInput.min = today;
    }
}

// Step navigation functions
function nextStep() {
    if (validateCurrentStep()) {
        if (currentStep < totalSteps) {
            currentStep++;
            showStep(currentStep);
            updateStepIndicator();
            updateNavigationButtons();
        }
    }
}

function previousStep() {
    if (currentStep > 1) {
        currentStep--;
        showStep(currentStep);
        updateStepIndicator();
        updateNavigationButtons();
    }
}

function showStep(step) {
    // Hide all steps
    document.querySelectorAll('.form-step').forEach(stepEl => {
        stepEl.classList.remove('active');
    });
    
    // Show current step
    const currentStepEl = document.getElementById(`step-${step}`);
    if (currentStepEl) {
        currentStepEl.classList.add('active');
    }
    
    // Special handling for step 5 (confirmation)
    if (step === 5) {
        generateBookingSummary();
    }
}

function updateStepIndicator() {
    for (let i = 1; i <= totalSteps; i++) {
        const indicator = document.getElementById(`step-${i}-indicator`);
        if (indicator) {
            indicator.classList.remove('active', 'completed');
            
            if (i < currentStep) {
                indicator.classList.add('completed');
                indicator.innerHTML = '<i class="fas fa-check"></i>';
            } else if (i === currentStep) {
                indicator.classList.add('active');
                indicator.innerHTML = i;
            } else {
                indicator.innerHTML = i;
            }
        }
    }
}

function updateNavigationButtons() {
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const submitBtn = document.getElementById('submit-btn');
    
    // Show/hide previous button
    if (prevBtn) {
        prevBtn.style.display = currentStep > 1 ? 'block' : 'none';
    }
    
    // Show/hide next and submit buttons
    if (currentStep === totalSteps) {
        if (nextBtn) nextBtn.style.display = 'none';
        if (submitBtn) submitBtn.style.display = 'block';
    } else {
        if (nextBtn) nextBtn.style.display = 'block';
        if (submitBtn) submitBtn.style.display = 'none';
    }
}

// Validation functions
function validateCurrentStep() {
    switch (currentStep) {
        case 1:
            return validateStep1();
        case 2:
            return validateStep2();
        case 3:
            return validateStep3();
        case 4:
            return validateStep4();
        default:
            return true;
    }
}

function validateStep1() {
    if (!bookingData.booking_type) {
        showError('يرجى اختيار نوع الحجز');
        return false;
    }
    return true;
}

function validateStep2() {
    if (bookingData.booking_type === 'Service' && !bookingData.service) {
        showError('يرجى اختيار الخدمة');
        return false;
    }
    if (bookingData.booking_type === 'Package' && !bookingData.service_package) {
        showError('يرجى اختيار الباقة');
        return false;
    }
    return true;
}

function validateStep3() {
    if (!bookingData.booking_date) {
        showError('يرجى اختيار التاريخ');
        return false;
    }
    if (!bookingData.start_time) {
        showError('يرجى اختيار الوقت');
        return false;
    }
    return true;
}

function validateStep4() {
    if (!bookingData.client_name) {
        showError('يرجى إدخال اسم العميل');
        return false;
    }
    if (!bookingData.phone) {
        showError('يرجى إدخال رقم الهاتف');
        return false;
    }
    if (!bookingData.payment_method) {
        showError('يرجى اختيار طريقة الدفع');
        return false;
    }
    
    // Validate phone number format
    const phoneRegex = /^05\d{8}$/;
    if (!phoneRegex.test(bookingData.phone)) {
        showError('يرجى إدخال رقم هاتف صحيح (05xxxxxxxx)');
        return false;
    }
    
    return true;
}

// Booking type selection
function selectBookingType(type) {
    bookingData.booking_type = type;
    
    // Update UI
    document.querySelectorAll('.service-card').forEach(card => {
        card.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
    
    // Update step 2 content
    const step2Title = document.getElementById('step-2-title');
    const servicesList = document.getElementById('services-list');
    const packagesList = document.getElementById('packages-list');
    
    if (type === 'Service') {
        if (step2Title) step2Title.textContent = 'اختر الخدمة';
        if (servicesList) servicesList.style.display = 'block';
        if (packagesList) packagesList.style.display = 'none';
    } else {
        if (step2Title) step2Title.textContent = 'اختر الباقة';
        if (servicesList) servicesList.style.display = 'none';
        if (packagesList) packagesList.style.display = 'block';
    }
}

// Service selection
function selectService(serviceName) {
    bookingData.service = serviceName;
    bookingData.service_package = ''; // Clear package selection
    
    // Update UI
    document.querySelectorAll('.service-card').forEach(card => {
        card.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
}

// Package selection
function selectPackage(packageName) {
    bookingData.service_package = packageName;
    bookingData.service = ''; // Clear service selection
    
    // Update UI
    document.querySelectorAll('.package-card').forEach(card => {
        card.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
}

// Time slot selection
function selectTimeSlot(startTime, endTime) {
    bookingData.start_time = startTime;
    bookingData.end_time = endTime;
    
    // Update UI
    document.querySelectorAll('.time-slot').forEach(slot => {
        slot.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
}

// Load available time slots
function loadAvailableSlots() {
    const date = document.getElementById('booking-date').value;
    const photographer = document.getElementById('photographer').value;
    
    if (!date) return;
    
    bookingData.booking_date = date;
    bookingData.photographer = photographer;
    
    const slotsContainer = document.getElementById('available-slots');
    slotsContainer.innerHTML = '<div class="loading-spinner"></div>';
    
    // Make API call to get available slots
    frappe.call({
        method: 'new-booking.get_available_slots',
        args: {
            date: date,
            photographer: photographer
        },
        callback: function(response) {
            if (response.message && response.message.success) {
                displayAvailableSlots(response.message.slots);
            } else {
                slotsContainer.innerHTML = '<p class="text-red-500">حدث خطأ في تحميل الأوقات المتاحة</p>';
            }
        },
        error: function() {
            slotsContainer.innerHTML = '<p class="text-red-500">حدث خطأ في تحميل الأوقات المتاحة</p>';
        }
    });
}

function displayAvailableSlots(slots) {
    const slotsContainer = document.getElementById('available-slots');
    
    if (slots.length === 0) {
        slotsContainer.innerHTML = '<p class="text-gray-500">لا توجد أوقات متاحة في هذا التاريخ</p>';
        return;
    }
    
    let slotsHTML = '';
    slots.forEach(slot => {
        slotsHTML += `
            <div class="time-slot" onclick="selectTimeSlot('${slot.start_time}', '${slot.end_time}')">
                ${slot.display}
            </div>
        `;
    });
    
    slotsContainer.innerHTML = slotsHTML;
}

// Collect form data
function collectFormData() {
    // Client information
    bookingData.client_name = document.getElementById('client-name').value;
    bookingData.phone = document.getElementById('client-phone').value;
    bookingData.client_email = document.getElementById('client-email').value;
    bookingData.payment_method = document.getElementById('payment-method').value;
    bookingData.notes = document.getElementById('notes').value;
}

// Generate booking summary
function generateBookingSummary() {
    collectFormData();
    
    const summaryContainer = document.getElementById('booking-summary');
    let summaryHTML = '';
    
    // Booking type and service/package
    summaryHTML += `
        <div class="flex justify-between">
            <span class="font-medium">نوع الحجز:</span>
            <span>${bookingData.booking_type === 'Service' ? 'خدمة فردية' : 'باقة خدمات'}</span>
        </div>
    `;
    
    if (bookingData.service) {
        summaryHTML += `
            <div class="flex justify-between">
                <span class="font-medium">الخدمة:</span>
                <span>${bookingData.service}</span>
            </div>
        `;
    }
    
    if (bookingData.service_package) {
        summaryHTML += `
            <div class="flex justify-between">
                <span class="font-medium">الباقة:</span>
                <span>${bookingData.service_package}</span>
            </div>
        `;
    }
    
    // Date and time
    summaryHTML += `
        <div class="flex justify-between">
            <span class="font-medium">التاريخ:</span>
            <span>${bookingData.booking_date}</span>
        </div>
        <div class="flex justify-between">
            <span class="font-medium">الوقت:</span>
            <span>${bookingData.start_time} - ${bookingData.end_time}</span>
        </div>
    `;
    
    // Photographer
    if (bookingData.photographer) {
        summaryHTML += `
            <div class="flex justify-between">
                <span class="font-medium">المصور:</span>
                <span>${bookingData.photographer}</span>
            </div>
        `;
    }
    
    // Client information
    summaryHTML += `
        <div class="flex justify-between">
            <span class="font-medium">اسم العميل:</span>
            <span>${bookingData.client_name}</span>
        </div>
        <div class="flex justify-between">
            <span class="font-medium">رقم الهاتف:</span>
            <span>${bookingData.phone}</span>
        </div>
    `;
    
    if (bookingData.client_email) {
        summaryHTML += `
            <div class="flex justify-between">
                <span class="font-medium">البريد الإلكتروني:</span>
                <span>${bookingData.client_email}</span>
            </div>
        `;
    }
    
    summaryHTML += `
        <div class="flex justify-between">
            <span class="font-medium">طريقة الدفع:</span>
            <span>${bookingData.payment_method}</span>
        </div>
    `;
    
    if (bookingData.notes) {
        summaryHTML += `
            <div class="flex justify-between">
                <span class="font-medium">الملاحظات:</span>
                <span>${bookingData.notes}</span>
            </div>
        `;
    }
    
    summaryContainer.innerHTML = summaryHTML;
}

// Submit booking
function submitBooking() {
    const submitBtn = document.getElementById('submit-btn');
    const resultContainer = document.getElementById('booking-result');
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<div class="loading-spinner"></div>';
    resultContainer.innerHTML = '';
    
    // Make API call to create booking
    frappe.call({
        method: 'new-booking.create_booking',
        args: {
            booking_data: JSON.stringify(bookingData)
        },
        callback: function(response) {
            if (response.message && response.message.success) {
                showSuccess(response.message.message, response.message.booking_id);
            } else {
                showError(response.message ? response.message.message : 'حدث خطأ أثناء إنشاء الحجز');
                resetSubmitButton();
            }
        },
        error: function(error) {
            console.error('Booking creation error:', error);
            showError('حدث خطأ أثناء إنشاء الحجز. يرجى المحاولة مرة أخرى.');
            resetSubmitButton();
        }
    });
}

function resetSubmitButton() {
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="fas fa-check mr-2"></i>تأكيد الحجز';
}

// Utility functions
function showError(message) {
    const resultContainer = document.getElementById('booking-result') || document.body;
    resultContainer.innerHTML = `
        <div class="error-message">
            <i class="fas fa-exclamation-triangle mr-2"></i>
            ${message}
        </div>
    `;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        const errorEl = resultContainer.querySelector('.error-message');
        if (errorEl) errorEl.remove();
    }, 5000);
}

function showSuccess(message, bookingId) {
    const resultContainer = document.getElementById('booking-result');
    resultContainer.innerHTML = `
        <div class="success-message success-animation">
            <i class="fas fa-check-circle mr-2"></i>
            ${message}
            <br>
            <strong>رقم الحجز: ${bookingId}</strong>
        </div>
        <div class="mt-4">
            <button class="btn-primary" onclick="window.location.href='/re_studio_booking'">
                <i class="fas fa-home mr-2"></i>
                العودة للرئيسية
            </button>
        </div>
    `;
    
    // Hide submit button
    const submitBtn = document.getElementById('submit-btn');
    if (submitBtn) submitBtn.style.display = 'none';
}

// Frappe integration
if (typeof frappe === 'undefined') {
    window.frappe = {
        call: function(options) {
            fetch('/api/method/' + options.method, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Frappe-CSRF-Token': frappe.csrf_token || ''
                },
                body: JSON.stringify(options.args || {})
            })
            .then(response => response.json())
            .then(data => {
                if (options.callback) {
                    options.callback(data);
                }
            })
            .catch(error => {
                console.error('API Error:', error);
                if (options.error) {
                    options.error(error);
                }
            });
        }
    };
}