// Admin Dashboard Utilities
// Additional utility functions for the admin dashboard

class AdminDashboardUtils {
    constructor() {
        this.dateFormats = {
            ar: 'DD/MM/YYYY',
            en: 'YYYY-MM-DD'
        };
        this.currency = 'SAR';
    }
    
    // Format numbers for Arabic locale
    formatNumber(number, decimal_places = 0) {
        if (!number) return '0';
        
        return new Intl.NumberFormat('ar-SA', {
            minimumFractionDigits: decimal_places,
            maximumFractionDigits: decimal_places
        }).format(number);
    }
    
    // Format currency
    formatCurrency(amount, show_currency = true) {
        if (!amount) return '0';
        
        const formatted = this.formatNumber(amount, 2);
        return show_currency ? `${formatted} ريال` : formatted;
    }
    
    // Format date for Arabic
    formatDate(date, format = 'DD/MM/YYYY') {
        if (!date) return '';
        
        return moment(date).locale('ar').format(format);
    }
    
    // Get relative time in Arabic
    getRelativeTime(date) {
        if (!date) return '';
        
        return moment(date).locale('ar').fromNow();
    }
    
    // Calculate percentage change
    calculatePercentageChange(current, previous) {
        if (!previous || previous === 0) return 0;
        
        return ((current - previous) / previous) * 100;
    }
    
    // Get status color
    getStatusColor(status) {
        const colors = {
            'Draft': '#6c757d',
            'Confirmed': '#007bff',
            'Completed': '#28a745',
            'Cancelled': '#dc3545',
            'Pending': '#ffc107'
        };
        
        return colors[status] || '#6c757d';
    }
    
    // Get status text in Arabic
    getStatusTextAr(status) {
        const statusTexts = {
            'Draft': 'مسودة',
            'Confirmed': 'مؤكد',
            'Completed': 'مكتمل',
            'Cancelled': 'ملغي',
            'Pending': 'معلق'
        };
        
        return statusTexts[status] || status;
    }
    
    // Show loading indicator
    showLoading(container) {
        $(container).html(`
            <div class="loading-indicator">
                <div class="spinner-border" role="status">
                    <span class="sr-only">جاري التحميل...</span>
                </div>
                <p>جاري التحميل...</p>
            </div>
        `);
    }
    
    // Hide loading and show error
    showError(container, message = 'حدث خطأ أثناء تحميل البيانات') {
        $(container).html(`
            <div class="alert alert-danger text-center">
                <i class="fa fa-exclamation-triangle"></i>
                <strong>خطأ:</strong> ${message}
                <br>
                <button class="btn btn-outline-danger btn-sm mt-2" onclick="location.reload()">
                    <i class="fa fa-refresh"></i> إعادة تحميل
                </button>
            </div>
        `);
    }
    
    // Show success message
    showSuccess(message, duration = 3000) {
        frappe.show_alert({
            message: message,
            indicator: 'green'
        }, duration);
    }
    
    // Show error message
    showErrorAlert(message, duration = 5000) {
        frappe.show_alert({
            message: message,
            indicator: 'red'
        }, duration);
    }
    
    // Export data to CSV
    exportToCSV(data, filename) {
        if (!data || data.length === 0) {
            this.showErrorAlert('لا توجد بيانات للتصدير');
            return;
        }
        
        const headers = Object.keys(data[0]).join(',');
        const csvContent = [headers, ...data.map(row => Object.values(row).join(','))].join('\n');
        
        const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', `${filename}_${moment().format('YYYY-MM-DD')}.csv`);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.showSuccess('تم تصدير البيانات بنجاح');
    }
    
    // Print dashboard section
    printSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (!section) {
            this.showErrorAlert('القسم المطلوب طباعته غير موجود');
            return;
        }
        
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <!DOCTYPE html>
            <html dir="rtl" lang="ar">
            <head>
                <meta charset="utf-8">
                <title>طباعة - Re Studio Booking</title>
                <style>
                    body { font-family: 'Cairo', Arial, sans-serif; direction: rtl; }
                    .no-print { display: none !important; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
                    th { background-color: #f2f2f2; }
                    @media print {
                        body { margin: 0; }
                        .btn, .quick-actions { display: none !important; }
                    }
                </style>
            </head>
            <body>
                <div style="text-align: center; margin-bottom: 20px;">
                    <h1>📸 Re Studio Booking</h1>
                    <h2>تقرير لوحة التحكم</h2>
                    <p>تاريخ الطباعة: ${this.formatDate(new Date())}</p>
                </div>
                ${section.innerHTML}
                <script>
                    window.onload = function() { 
                        window.print(); 
                        window.onafterprint = function() { window.close(); }
                    }
                </script>
            </body>
            </html>
        `);
        printWindow.document.close();
    }
    
    // Initialize tooltips
    initializeTooltips() {
        $('[data-toggle="tooltip"]').tooltip({
            placement: 'top',
            trigger: 'hover'
        });
    }
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts() {
        $(document).keydown((e) => {
            // Ctrl+Shift+D for dashboard
            if (e.ctrlKey && e.shiftKey && e.keyCode === 68) {
                $('.nav-item[data-section="dashboard"]').click();
                e.preventDefault();
            }
            
            // Ctrl+Shift+B for bookings
            if (e.ctrlKey && e.shiftKey && e.keyCode === 66) {
                $('.nav-item[data-section="bookings"]').click();
                e.preventDefault();
            }
            
            // Ctrl+Shift+R for refresh
            if (e.ctrlKey && e.shiftKey && e.keyCode === 82) {
                if (window.current_admin_dashboard) {
                    window.current_admin_dashboard.load_dashboard_data();
                }
                e.preventDefault();
            }
            
            // ESC to close modals
            if (e.keyCode === 27) {
                $('.modal').modal('hide');
            }
        });
    }
    
    // Auto-refresh data
    setupAutoRefresh(interval = 300000) { // Default 5 minutes
        setInterval(() => {
            if (window.current_admin_dashboard && $('.nav-item.active').data('section') === 'dashboard') {
                window.current_admin_dashboard.load_dashboard_data();
            }
        }, interval);
    }
    
    // Responsive sidebar toggle
    setupResponsiveSidebar() {
        // Add mobile toggle button
        if (window.innerWidth <= 768) {
            $('.admin-sidebar').addClass('mobile-hidden');
            
            if (!$('.mobile-toggle').length) {
                $('.admin-content').prepend(`
                    <button class="btn btn-primary mobile-toggle d-md-none mb-3">
                        <i class="fa fa-bars"></i> القائمة
                    </button>
                `);
            }
            
            $(document).on('click', '.mobile-toggle', function() {
                $('.admin-sidebar').toggleClass('mobile-hidden');
            });
            
            // Hide sidebar when clicking on content (mobile)
            $(document).on('click', '.admin-content', function(e) {
                if ($(e.target).closest('.mobile-toggle').length === 0) {
                    $('.admin-sidebar').addClass('mobile-hidden');
                }
            });
        }
    }
    
    // Initialize all utilities
    init() {
        this.initializeTooltips();
        this.setupKeyboardShortcuts();
        this.setupAutoRefresh();
        this.setupResponsiveSidebar();
        
        // Show keyboard shortcuts help
        console.log(`
🚀 Re Studio Admin Dashboard - Keyboard Shortcuts:
• Ctrl+Shift+D: Dashboard
• Ctrl+Shift+B: Bookings
• Ctrl+Shift+R: Refresh
• ESC: Close modals
        `);
    }
}

// Initialize utilities when document is ready
$(document).ready(function() {
    window.adminUtils = new AdminDashboardUtils();
    window.adminUtils.init();
});

// Export for global use
window.AdminDashboardUtils = AdminDashboardUtils;
