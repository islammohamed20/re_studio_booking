// Booking Dashboard JS

frappe.pages['booking-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('لوحة معلومات الحجز'),
        single_column: true
    });
    
    // Initialize the dashboard
    wrapper.dashboard = new BookingDashboard(wrapper, page);
    
    // Add refresh button
    page.set_primary_action(__('تحديث'), function() {
        wrapper.dashboard.refresh_data();
    }, 'refresh');
    
    // Add quick actions menu
    page.add_menu_item(__('إنشاء حجز جديد'), function() {
        frappe.new_doc('Booking');
    });
    
    page.add_menu_item(__('إنشاء تقرير'), function() {
        frappe.new_doc('Booking Report');
    });
    
    page.add_menu_item(__('إعدادات الحجز'), function() {
        frappe.set_route('Form', 'General Settings', 'General Settings');
    });
};

frappe.pages['booking-dashboard'].on_page_show = function(wrapper) {
    // Refresh data when page is shown
    if (wrapper.dashboard) {
        wrapper.dashboard.refresh_data();
    }
};

// Booking Dashboard Class
if (typeof BookingDashboard === 'undefined') {
    window.BookingDashboard = class {
    constructor(wrapper, page) {
        this.wrapper = wrapper;
        this.page = page;
        this.make();
        this.refresh_data();
    }
    
    make() {
        // Create dashboard sections
        this.make_dashboard_container();
        this.make_stats_section();
        this.make_bookings_section();
        this.make_charts_section();
    }
    
    make_dashboard_container() {
        this.dashboard_container = $('<div class="booking-dashboard-container"></div>').appendTo(this.wrapper);
        
        // Add dashboard CSS
        this.add_dashboard_styles();
    }
    
    make_stats_section() {
        this.stats_section = $('<div class="dashboard-section stats-section"></div>')
            .appendTo(this.dashboard_container);
        
        $('<h3 class="dashboard-section-title">' + __('إحصائيات الحجوزات') + '</h3>')
            .appendTo(this.stats_section);
        
        this.stats_container = $('<div class="row"></div>')
            .appendTo(this.stats_section);
    }
    
    make_bookings_section() {
        // Create container for recent and upcoming bookings
        this.bookings_section = $('<div class="dashboard-section bookings-section row"></div>')
            .appendTo(this.dashboard_container);
        
        // Recent bookings
        this.recent_bookings_container = $('<div class="col-md-6 recent-bookings"></div>')
            .appendTo(this.bookings_section);
        
        $('<h3 class="dashboard-section-title">' + __('الحجوزات الأخيرة') + '</h3>')
            .appendTo(this.recent_bookings_container);
        
        this.recent_bookings_list = $('<div class="booking-list"></div>')
            .appendTo(this.recent_bookings_container);
        
        // Upcoming bookings
        this.upcoming_bookings_container = $('<div class="col-md-6 upcoming-bookings"></div>')
            .appendTo(this.bookings_section);
        
        $('<h3 class="dashboard-section-title">' + __('الحجوزات القادمة') + '</h3>')
            .appendTo(this.upcoming_bookings_container);
        
        this.upcoming_bookings_list = $('<div class="booking-list"></div>')
            .appendTo(this.upcoming_bookings_container);
    }
    
    make_charts_section() {
        // Create container for charts
        this.charts_section = $('<div class="dashboard-section charts-section row"></div>')
            .appendTo(this.dashboard_container);
        
        // Status chart
        this.status_chart_container = $('<div class="col-md-6 status-chart"></div>')
            .appendTo(this.charts_section);
        
        $('<h3 class="dashboard-section-title">' + __('الحجوزات حسب الحالة') + '</h3>')
            .appendTo(this.status_chart_container);
        
        this.status_chart_div = $('<div id="status-chart"></div>')
            .appendTo(this.status_chart_container);
        
        // Service chart
        this.service_chart_container = $('<div class="col-md-6 service-chart"></div>')
            .appendTo(this.charts_section);
        
        $('<h3 class="dashboard-section-title">' + __('الخدمات الأكثر حجزاً') + '</h3>')
            .appendTo(this.service_chart_container);
        
        this.service_chart_div = $('<div id="service-chart"></div>')
            .appendTo(this.service_chart_container);
    }
    
    refresh_data() {
        var me = this;
        
        // Show loading state
        this.page.set_indicator(__('جاري التحميل...'), 'blue');
        
        // Call backend method to get dashboard data
        frappe.call({
            method: 're_studio_booking.re_studio_booking.page.booking_dashboard.booking_dashboard.get_dashboard_data',
            callback: function(r) {
                if (r.message) {
                    me.render_dashboard(r.message);
                    me.page.set_indicator(__('تم التحديث'), 'green');
                    
                    // Clear indicator after 2 seconds
                    setTimeout(function() {
                        me.page.set_indicator('');
                    }, 2000);
                }
            }
        });
    }
    
    render_dashboard(data) {
        this.render_stats(data.booking_stats);
        this.render_recent_bookings(data.recent_bookings);
        this.render_upcoming_bookings(data.upcoming_bookings);
        this.render_status_chart(data.booking_stats.status_counts);
        this.render_service_chart(data.service_stats.top_services);
    }
    
    render_stats(stats) {
        this.stats_container.empty();
        
        // Add stat cards for today, this week, this month
        this.add_stat_card(__('اليوم'), stats.today, 'col-md-4');
        this.add_stat_card(__('هذا الأسبوع'), stats.this_week, 'col-md-4');
        this.add_stat_card(__('هذا الشهر'), stats.this_month, 'col-md-4');
        
        // Add stat cards for status counts
        this.add_stat_card(__('مؤكدة'), stats.status_counts.Confirmed, 'col-md-4', 'confirmed');
        this.add_stat_card(__('مكتملة'), stats.status_counts.Completed, 'col-md-4', 'completed');
        this.add_stat_card(__('ملغاة'), stats.status_counts.Cancelled, 'col-md-4', 'cancelled');
    }
    
    add_stat_card(label, value, column_class, status_class) {
        var card = $('<div class="' + column_class + '"></div>')
            .appendTo(this.stats_container);
        
        var card_content = $('<div class="stat-card"></div>')
            .appendTo(card);
        
        if (status_class) {
            card_content.addClass(status_class);
        }
        
        $('<div class="stat-value">' + (value || 0) + '</div>')
            .appendTo(card_content);
        
        $('<div class="stat-label">' + label + '</div>')
            .appendTo(card_content);
    }
    
    render_recent_bookings(bookings) {
        var me = this;
        this.recent_bookings_list.empty();
        
        if (!bookings || bookings.length === 0) {
            this.recent_bookings_list.html('<div class="text-muted text-center p-4">' + __('لا توجد حجوزات حديثة') + '</div>');
            return;
        }
        
        // Create table for bookings
        var table = $('<table class="table table-hover"></table>')
            .appendTo(this.recent_bookings_list);
        
        // Add table header
        var header = $('<thead></thead>').appendTo(table);
        var header_row = $('<tr></tr>').appendTo(header);
        
        $('<th>' + __('رقم الحجز') + '</th>').appendTo(header_row);
        $('<th>' + __('العميل') + '</th>').appendTo(header_row);
        $('<th>' + __('التاريخ') + '</th>').appendTo(header_row);
        $('<th>' + __('الحالة') + '</th>').appendTo(header_row);
        
        // Add table body
        var body = $('<tbody></tbody>').appendTo(table);
        
        // Add bookings to table
        $.each(bookings, function(i, booking) {
            var row = $('<tr data-booking="' + booking.name + '"></tr>')
                .appendTo(body)
                .click(function() {
                    frappe.set_route('Form', 'Booking', booking.name);
                });
            
            $('<td>' + booking.name + '</td>').appendTo(row);
            $('<td>' + booking.customer_name + '</td>').appendTo(row);
            $('<td>' + frappe.datetime.str_to_user(booking.booking_date) + '</td>').appendTo(row);
            
            var status_cell = $('<td></td>').appendTo(row);
            $('<span class="status-indicator ' + me.get_status_color(booking.status) + '">' + 
                __(booking.status) + '</span>').appendTo(status_cell);
        });
    }
    
    render_upcoming_bookings(bookings) {
        var me = this;
        this.upcoming_bookings_list.empty();
        
        if (!bookings || bookings.length === 0) {
            this.upcoming_bookings_list.html('<div class="text-muted text-center p-4">' + __('لا توجد حجوزات قادمة') + '</div>');
            return;
        }
        
        // Create table for bookings
        var table = $('<table class="table table-hover"></table>')
            .appendTo(this.upcoming_bookings_list);
        
        // Add table header
        var header = $('<thead></thead>').appendTo(table);
        var header_row = $('<tr></tr>').appendTo(header);
        
        $('<th>' + __('رقم الحجز') + '</th>').appendTo(header_row);
        $('<th>' + __('العميل') + '</th>').appendTo(header_row);
        $('<th>' + __('التاريخ') + '</th>').appendTo(header_row);
        $('<th>' + __('المصور') + '</th>').appendTo(header_row);
        
        // Add table body
        var body = $('<tbody></tbody>').appendTo(table);
        
        // Add bookings to table
        $.each(bookings, function(i, booking) {
            var row = $('<tr data-booking="' + booking.name + '"></tr>')
                .appendTo(body)
                .click(function() {
                    frappe.set_route('Form', 'Booking', booking.name);
                });
            
            $('<td>' + booking.name + '</td>').appendTo(row);
            $('<td>' + booking.customer_name + '</td>').appendTo(row);
            $('<td>' + frappe.datetime.str_to_user(booking.booking_date) + '</td>').appendTo(row);
            $('<td>' + (booking.photographer || '-') + '</td>').appendTo(row);
        });
    }
    
    get_status_color(status) {
        const statusColors = {
            'Confirmed': 'confirmed',
            'Completed': 'completed',
            'Cancelled': 'cancelled',
            'Pending': 'pending'
        };
        
        return statusColors[status] || '';
    }
    
    render_status_chart(status_counts) {
        // Prepare data for chart
        var labels = [];
        var values = [];
        var colors = [];
        
        if (status_counts.Confirmed) {
            labels.push(__('مؤكدة'));
            values.push(status_counts.Confirmed);
            colors.push('#5e64ff');
        }
        
        if (status_counts.Completed) {
            labels.push(__('مكتملة'));
            values.push(status_counts.Completed);
            colors.push('#28a745');
        }
        
        if (status_counts.Cancelled) {
            labels.push(__('ملغاة'));
            values.push(status_counts.Cancelled);
            colors.push('#ff5858');
        }
        
        if (status_counts.Pending) {
            labels.push(__('معلقة'));
            values.push(status_counts.Pending);
            colors.push('#f8814f');
        }
        
        // Create chart
        if (this.status_chart) {
            this.status_chart.update({
                labels: labels,
                datasets: [{ values: values }],
                colors: colors
            });
        } else {
            this.status_chart = new frappe.Chart("#status-chart", {
                title: "",
                data: {
                    labels: labels,
                    datasets: [{ values: values }],
                    colors: colors
                },
                type: 'pie',
                height: 250,
                colors: colors
            });
        }
    }
    
    render_service_chart(services) {
        // Prepare data for chart
        var labels = [];
        var values = [];
        
        $.each(services, function(i, service) {
            labels.push(service.service_name_ar || service.service_name);
            values.push(service.booking_count);
        });
        
        // Create chart
        if (this.service_chart) {
            this.service_chart.update({
                labels: labels,
                datasets: [{ values: values }]
            });
        } else {
            this.service_chart = new frappe.Chart("#service-chart", {
                title: "",
                data: {
                    labels: labels,
                    datasets: [{ values: values }]
                },
                type: 'bar',
                height: 250,
                colors: ['#5e64ff']
            });
        }
    }
    
    add_dashboard_styles() {
        // Add custom CSS for dashboard
        $('<style>\
            .booking-dashboard-container {\
                padding: 15px;\
            }\
            \
            .dashboard-section {\
                margin-bottom: 30px;\
            }\
            \
            .stat-card {\
                background-color: var(--card-bg);\
                border-radius: 8px;\
                padding: 15px;\
                box-shadow: var(--card-shadow);\
                margin-bottom: 15px;\
                transition: all 0.3s ease;\
                text-align: center;\
            }\
            \
            .stat-card:hover {\
                transform: translateY(-3px);\
                box-shadow: var(--shadow-lg);\
            }\
            \
            .stat-card.confirmed {\
                border-top: 3px solid #5e64ff;\
            }\
            \
            .stat-card.completed {\
                border-top: 3px solid #28a745;\
            }\
            \
            .stat-card.cancelled {\
                border-top: 3px solid #ff5858;\
            }\
            \
            .stat-value {\
                font-size: 24px;\
                font-weight: bold;\
                color: var(--text-color);\
            }\
            \
            .stat-label {\
                font-size: 13px;\
                color: var(--text-muted);\
                margin-top: 5px;\
            }\
            \
            .booking-list {\
                background-color: var(--card-bg);\
                border-radius: 8px;\
                padding: 15px;\
                box-shadow: var(--card-shadow);\
                height: 350px;\
                overflow-y: auto;\
            }\
            \
            .booking-list .table {\
                margin-bottom: 0;\
            }\
            \
            .booking-list tr {\
                cursor: pointer;\
            }\
            \
            .status-indicator {\
                display: inline-block;\
                width: 8px;\
                height: 8px;\
                border-radius: 50%;\
                margin-right: 5px;\
            }\
            \
            .status-indicator.confirmed {\
                background-color: #5e64ff;\
            }\
            \
            .status-indicator.completed {\
                background-color: #28a745;\
            }\
            \
            .status-indicator.cancelled {\
                background-color: #ff5858;\
            }\
            \
            .status-indicator.pending {\
                background-color: #f8814f;\
            }\
            \
            @media (max-width: 767px) {\
                .booking-list {\
                    height: auto;\
                    max-height: 350px;\
                    margin-bottom: 20px;\
                }\
                \
                .stat-card {\
                    margin-bottom: 10px;\
                }\
            }\
            \
            /* RTL Support */\
            .rtl .stat-card {\
                text-align: center;\
            }\
            \
            .rtl .status-indicator {\
                margin-right: 0;\
                margin-left: 5px;\
            }\
        </style>').appendTo(this.dashboard_container);
    }
    };
}