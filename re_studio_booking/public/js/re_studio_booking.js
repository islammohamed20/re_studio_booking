// Re Studio Booking JS

frappe.provide('re_studio_booking');

// Initialize the app
re_studio_booking = {
    init: function() {
        // Set up RTL support based on user language
        this.setupRTL();
        
        // Set up custom event handlers
        this.setupEventHandlers();
    },
    
    setupRTL: function() {
        // Check if current language is RTL (Arabic)
        const isRTL = ['ar', 'ar-SA'].includes(frappe.boot.lang);
        
        if (isRTL) {
            $('body').addClass('rtl');
        } else {
            $('body').removeClass('rtl');
        }
    },
    
    setupEventHandlers: function() {
        // Add custom event handlers here
        $(document).on('app_ready', function() {
            // Code to run when Frappe app is ready
        });
    },
    
    // Format date according to user's locale
    formatDate: function(date) {
        if (!date) return '';
        
        const isRTL = ['ar', 'ar-SA'].includes(frappe.boot.lang);
        const dateFormat = isRTL ? 'DD-MM-YYYY' : 'MM-DD-YYYY';
        
        return moment(date).format(dateFormat);
    },
    
    // Format time according to user's locale
    formatTime: function(time) {
        if (!time) return '';
        
        return moment(time, 'HH:mm:ss').format('hh:mm A');
    },
    
    // Get status color class
    getStatusColor: function(status) {
        const statusColors = {
            'Confirmed': 'confirmed',
            'Completed': 'completed',
            'Cancelled': 'cancelled',
            'Pending': 'pending'
        };
        
        return statusColors[status] || '';
    },
    
    // Show a custom message
    showMessage: function(message, type = 'success') {
        frappe.show_alert({
            message: __(message),
            indicator: type
        }, 5);
    },
    
    // Navigate to booking form
    navigateToBooking: function(bookingName) {
        frappe.set_route('Form', 'Booking', bookingName);
    },
    
    // Create a new booking
    createNewBooking: function() {
        frappe.new_doc('Booking');
    }
};

// Initialize when document is ready
$(document).ready(function() {
    re_studio_booking.init();
});