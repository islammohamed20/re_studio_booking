/**
 * Modern Calendar UI for Re Studio Booking Form
 * Creates a beautiful month calendar with availability indicators
 */

class ModernCalendar {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.currentDate = new Date();
        this.selectedDate = null;
        this.availabilityData = {};
        this.options = {
            locale: 'ar',
            weekStartsOn: 1, // Monday
            minDate: new Date(),
            onDateSelect: null,
            ...options
        };
        
        // Arabic month names
        this.arabicMonths = [
            'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
            'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
        ];
        
        // Arabic day names (Monday to Sunday)
        this.arabicDays = ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد'];
        
        this.init();
    }
    
    init() {
        this.container.innerHTML = this.generateCalendarHTML();
        this.attachEventListeners();
        this.loadAvailabilityData();
    }
    
    generateCalendarHTML() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        const monthName = this.arabicMonths[month];
        
        return `
            <div class="modern-calendar">
                <!-- Calendar Header -->
                <div class="calendar-header">
                    <button class="nav-btn prev-btn" id="prevMonth">
                        <i class="fas fa-chevron-right"></i>
                    </button>
                    <div class="month-year">
                        <h3>${monthName} ${year}</h3>
                    </div>
                    <button class="nav-btn next-btn" id="nextMonth">
                        <i class="fas fa-chevron-left"></i>
                    </button>
                </div>
                
                <!-- Days Header -->
                <div class="days-header">
                    ${this.arabicDays.map(day => `<div class="day-header">${day}</div>`).join('')}
                </div>
                
                <!-- Calendar Grid -->
                <div class="calendar-grid" id="calendarGrid">
                    ${this.generateDaysHTML()}
                </div>
                
                <!-- Calendar Legend -->
                <div class="calendar-legend">
                    <div class="legend-item">
                        <div class="legend-dot available"></div>
                        <span>متاح</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-dot partial"></div>
                        <span>محجوز جزئياً</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-dot booked"></div>
                        <span>محجوز بالكامل</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-dot today"></div>
                        <span>اليوم</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    generateDaysHTML() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        const firstDayOfMonth = new Date(year, month, 1);
        const lastDayOfMonth = new Date(year, month + 1, 0);
        const firstDayWeekday = (firstDayOfMonth.getDay() + 6) % 7; // Adjust for Monday start
        const daysInMonth = lastDayOfMonth.getDate();
        const today = new Date();
        
        let daysHTML = '';
        
        // Previous month's trailing days
        const prevMonth = new Date(year, month - 1, 0);
        const prevMonthDays = prevMonth.getDate();
        
        for (let i = firstDayWeekday - 1; i >= 0; i--) {
            const day = prevMonthDays - i;
            const date = new Date(year, month - 1, day);
            daysHTML += this.generateDayHTML(day, date, 'other-month');
        }
        
        // Current month days
        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(year, month, day);
            let classes = '';
            
            // Check if it's today
            if (this.isSameDate(date, today)) {
                classes += ' today';
            }
            
            // Check if it's selected
            if (this.selectedDate && this.isSameDate(date, this.selectedDate)) {
                classes += ' selected';
            }
            
            // Check if it's in the past
            if (date < today.setHours(0, 0, 0, 0)) {
                classes += ' disabled';
            }
            
            daysHTML += this.generateDayHTML(day, date, classes);
        }
        
        // Next month's leading days
        const totalCells = Math.ceil((firstDayWeekday + daysInMonth) / 7) * 7;
        const remainingCells = totalCells - (firstDayWeekday + daysInMonth);
        
        for (let day = 1; day <= remainingCells; day++) {
            const date = new Date(year, month + 1, day);
            daysHTML += this.generateDayHTML(day, date, 'other-month');
        }
        
        return daysHTML;
    }
    
    generateDayHTML(day, date, classes = '') {
        const dateStr = this.formatDate(date);
        const availability = this.availabilityData[dateStr] || { status: 'unknown', available_slots: 0 };
        
        let availabilityClass = '';
        let title = '';
        
        if (!classes.includes('disabled') && !classes.includes('other-month')) {
            switch (availability.status) {
                case 'available':
                    availabilityClass = 'available';
                    title = `متاح - ${availability.available_slots} موعد متاح`;
                    break;
                case 'partially_booked':
                    availabilityClass = 'partial';
                    title = `محجوز جزئياً - ${availability.available_slots} موعد متاح`;
                    break;
                case 'fully_booked':
                    availabilityClass = 'booked';
                    title = 'محجوز بالكامل';
                    classes += ' disabled';
                    break;
                default:
                    availabilityClass = 'loading';
                    title = 'جاري التحميل...';
            }
        }
        
        return `
            <div class="calendar-day ${classes} ${availabilityClass}" 
                 data-date="${dateStr}" 
                 title="${title}"
                 ${!classes.includes('disabled') && !classes.includes('other-month') ? 'onclick="calendar.selectDate(this)"' : ''}>
                <span class="day-number">${day}</span>
                ${!classes.includes('other-month') && !classes.includes('disabled') ? 
                  `<div class="availability-indicator ${availabilityClass}"></div>` : ''}
            </div>
        `;
    }
    
    attachEventListeners() {
        // Previous month button
        document.getElementById('prevMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
            this.refresh();
        });
        
        // Next month button
        document.getElementById('nextMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
            this.refresh();
        });
    }
    
    selectDate(dayElement) {
        // Remove previous selection
        this.container.querySelectorAll('.calendar-day').forEach(day => {
            day.classList.remove('selected');
        });
        
        // Add selection to clicked day
        dayElement.classList.add('selected');
        
        // Store selected date
        const dateStr = dayElement.dataset.date;
        this.selectedDate = new Date(dateStr);
        
        // Add circle hover effect
        dayElement.style.borderRadius = '50%';
        dayElement.style.transform = 'scale(1.1)';
        
        // Reset other days
        this.container.querySelectorAll('.calendar-day:not(.selected)').forEach(day => {
            day.style.borderRadius = '50%';  // Make all days circular
            day.style.transform = 'scale(1)';
        });
        
        // Update global selected date for time slots
        window.selectedDate = dateStr;
        
        // Trigger callback
        if (this.options.onDateSelect) {
            this.options.onDateSelect(this.selectedDate, dateStr);
        }
    }
    
    refresh() {
        const grid = document.getElementById('calendarGrid');
        const header = this.container.querySelector('.month-year h3');
        
        // Update header
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        header.textContent = `${this.arabicMonths[month]} ${year}`;
        
        // Update grid
        grid.innerHTML = this.generateDaysHTML();
        
        // Reload availability data
        this.loadAvailabilityData();
    }
    
    loadAvailabilityData() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        const startDate = new Date(year, month, 1);
        const endDate = new Date(year, month + 1, 0);
        
        const startDateStr = this.formatDate(startDate);
        const endDateStr = this.formatDate(endDate);
        
        // Fetch availability data from API
        fetch('/api/method/re_studio_booking.api.get_calendar_availability', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Frappe-CSRF-Token': window.csrf_token || ''
            },
            body: JSON.stringify({
                start_date: startDateStr,
                end_date: endDateStr
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message && data.message.success) {
                this.availabilityData = data.message.calendar_data;
                this.updateAvailabilityDisplay();
            }
        })
        .catch(error => {
            console.error('Error loading calendar availability:', error);
        });
    }
    
    updateAvailabilityDisplay() {
        this.container.querySelectorAll('.calendar-day[data-date]').forEach(dayElement => {
            const dateStr = dayElement.dataset.date;
            const availability = this.availabilityData[dateStr];
            
            if (availability && !dayElement.classList.contains('other-month') && !dayElement.classList.contains('disabled')) {
                // Remove old classes
                dayElement.classList.remove('available', 'partial', 'booked', 'loading');
                
                // Add new class based on availability
                switch (availability.status) {
                    case 'available':
                        dayElement.classList.add('available');
                        dayElement.title = `متاح - ${availability.available_slots} موعد متاح`;
                        break;
                    case 'partially_booked':
                        dayElement.classList.add('partial');
                        dayElement.title = `محجوز جزئياً - ${availability.available_slots} موعد متاح`;
                        break;  
                    case 'fully_booked':
                        dayElement.classList.add('booked', 'disabled');
                        dayElement.title = 'محجوز بالكامل';
                        dayElement.onclick = null;
                        break;
                }
                
                // Update availability indicator
                const indicator = dayElement.querySelector('.availability-indicator');
                if (indicator) {
                    indicator.className = `availability-indicator ${availability.status === 'available' ? 'available' : 
                                                                   availability.status === 'partially_booked' ? 'partial' : 'booked'}`;
                }
            }
        });
    }
    
    // Utility methods
    formatDate(date) {
        return date.toISOString().split('T')[0];
    }
    
    isSameDate(date1, date2) {
        return date1.getFullYear() === date2.getFullYear() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getDate() === date2.getDate();
    }
    
    getSelectedDate() {
        return this.selectedDate;
    }
    
    getSelectedDateString() {
        return this.selectedDate ? this.formatDate(this.selectedDate) : null;
    }
}

// Global calendar instance
let calendar;

// Initialize calendar when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('modernCalendar')) {
        calendar = new ModernCalendar('modernCalendar', {
            onDateSelect: function(date, dateStr) {
                // Update selected date display
                const selectedDateInfo = document.getElementById('selectedDateInfo');
                if (selectedDateInfo) {
                    selectedDateInfo.innerHTML = `
                        <div class="text-sm text-gray-600 mb-2">التاريخ المحدد:</div>
                        <div class="font-semibold" style="color: #569ff7;">${formatArabicDate(date)}</div>
                    `;
                    selectedDateInfo.style.display = 'block';
                }
                
                // Load time slots for selected date
                loadTimeSlots(dateStr);
            }
        });
    }
});

// Helper function to format Arabic date
function formatArabicDate(date) {
    const months = [
        'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
        'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
    ];
    const day = date.getDate();
    const month = months[date.getMonth()];
    const year = date.getFullYear();
    return `${day} ${month} ${year}`;
}

// Load available time slots for selected date
function loadTimeSlots(date) {
    const timeSlotsContainer = document.getElementById('timeSlots');
    if (!timeSlotsContainer) return;
    
    timeSlotsContainer.innerHTML = '<div class="col-span-3 text-center text-gray-500">جاري التحميل...</div>';
    
    fetch('/api/method/re_studio_booking.api.get_available_time_slots', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Frappe-CSRF-Token': window.csrf_token || ''
        },
        body: JSON.stringify({ date: date })
    })
    .then(response => response.json())
    .then(data => {
        timeSlotsContainer.innerHTML = '';
        
        if (data.message && data.message.success) {
            const availableSlots = data.message.available_slots || [];
            const allTimeSlots = [
                '09:00', '10:00', '11:00', '12:00', '13:00', '14:00',
                '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00'
            ];
            
            if (availableSlots.length === 0) {
                // Show all time slots as available if no specific data
                allTimeSlots.forEach(time => {
                    const slot = document.createElement('div');
                    slot.className = 'time-slot';
                    slot.textContent = time;
                    slot.onclick = () => selectTimeSlot(slot, time);
                    timeSlotsContainer.appendChild(slot);
                });
            } else {
                allTimeSlots.forEach(time => {
                    const slot = document.createElement('div');
                    slot.className = 'time-slot';
                    slot.textContent = time;
                    
                    if (availableSlots.includes(time)) {
                        slot.onclick = () => selectTimeSlot(slot, time);
                    } else {
                        slot.classList.add('disabled');
                        slot.title = 'هذا الموعد محجوز';
                    }
                    
                    timeSlotsContainer.appendChild(slot);
                });
            }
        } else {
            // Fallback: Show all slots as available
            const allTimeSlots = [
                '09:00', '10:00', '11:00', '12:00', '13:00', '14:00',
                '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00'
            ];
            
            allTimeSlots.forEach(time => {
                const slot = document.createElement('div');
                slot.className = 'time-slot';
                slot.textContent = time;
                slot.onclick = () => selectTimeSlot(slot, time);
                timeSlotsContainer.appendChild(slot);
            });
        }
    })
    .catch(error => {
        console.error('Error loading time slots:', error);
        
        // Fallback: Show all slots as available
        timeSlotsContainer.innerHTML = '';
        const allTimeSlots = [
            '09:00', '10:00', '11:00', '12:00', '13:00', '14:00',
            '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00'
        ];
        
        allTimeSlots.forEach(time => {
            const slot = document.createElement('div');
            slot.className = 'time-slot';
            slot.textContent = time;
            slot.onclick = () => selectTimeSlot(slot, time);
            timeSlotsContainer.appendChild(slot);
        });
    });
}

// Select time slot
function selectTimeSlot(element, time) {
    document.querySelectorAll('.time-slot').forEach(slot => {
        slot.classList.remove('selected');
        slot.style.borderRadius = '4px';
    });
    
    element.classList.add('selected');
    element.style.borderRadius = '50%'; // Circle effect
    
    window.selectedTime = time;
}
