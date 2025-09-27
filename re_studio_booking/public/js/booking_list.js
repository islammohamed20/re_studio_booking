// Booking List JS

frappe.listview_settings['Booking'] = {
    refresh: function(listview) {
        // Add custom buttons
        listview.page.add_menu_item(__('عرض التقويم'), function() {
            frappe.set_route('List', 'Booking', 'Calendar');
        });
        
        listview.page.add_menu_item(__('إنشاء تقرير'), function() {
            frappe.new_doc('Booking Report');
        });
        
        // Add quick filters
        listview.page.add_menu_item(__('حجوزات اليوم'), function() {
            listview.filter_area.add([["Booking", "booking_date", "=", frappe.datetime.get_today()]]);
        });
        
        listview.page.add_menu_item(__('حجوزات الأسبوع'), function() {
            listview.filter_area.add([["Booking", "booking_date", "Between", [frappe.datetime.week_start(), frappe.datetime.week_end()]]]);
        });
        
        listview.page.add_menu_item(__('حجوزات الشهر'), function() {
            listview.filter_area.add([["Booking", "booking_date", "Between", [frappe.datetime.month_start(), frappe.datetime.month_end()]]]);
        });
        
        // Add bulk actions
        if (frappe.user.has_role(['System Manager', 'Re Studio Manager'])) {
            listview.page.add_menu_item(__('تأكيد الحجوزات المحددة'), function() {
                listview.call_for_selected_items('re_studio_booking.re_studio_booking.doctype.booking.booking.bulk_update_status', {
                    status: 'Confirmed'
                });
            });
            
            listview.page.add_menu_item(__('إكمال الحجوزات المحددة'), function() {
                listview.call_for_selected_items('re_studio_booking.re_studio_booking.doctype.booking.booking.bulk_update_status', {
                    status: 'Completed'
                });
            });
            
            listview.page.add_menu_item(__('إلغاء الحجوزات المحددة'), function() {
                listview.call_for_selected_items('re_studio_booking.re_studio_booking.doctype.booking.booking.bulk_update_status', {
                    status: 'Cancelled'
                });
            });
        }
    },
    
    // Format the list view
    formatters: {
        status: function(value, df, doc) {
            let colors = {
                'Pending': 'orange',
                'Confirmed': 'blue',
                'Completed': 'green',
                'Cancelled': 'red'
            };
            
            return `<span class="indicator ${colors[value] || 'gray'}">${__(value)}</span>`;
        },
        
        booking_datetime: function(value, df, doc) {
            if (!value) return '';
            
            let date = frappe.datetime.str_to_user(doc.booking_date);
            let time = frappe.datetime.get_time(value);
            
            return `<span>${date}</span><br><span class="text-muted">${time}</span>`;
        },
        
        customer_name: function(value, df, doc) {
            if (!value) return '';
            
            let html = `<span>${value}</span>`;
            
            if (doc.customer_phone) {
                html += `<br><span class="text-muted">${doc.customer_phone}</span>`;
            }
            
            return html;
        }
    },
    
    // Add indicator colors
    get_indicator: function(doc) {
        if (doc.status === 'Pending') {
            return [__("Pending"), "orange", "status,=,Pending"];
        } else if (doc.status === 'Confirmed') {
            return [__("Confirmed"), "blue", "status,=,Confirmed"];
        } else if (doc.status === 'Completed') {
            return [__("Completed"), "green", "status,=,Completed"];
        } else if (doc.status === 'Cancelled') {
            return [__("Cancelled"), "red", "status,=,Cancelled"];
        }
    },
    
    // Add custom button in each row
    button: {
        show: function(doc) {
            return doc.status === 'Confirmed';
        },
        get_label: function() {
            return __('إكمال');
        },
        get_description: function(doc) {
            return __('إكمال الحجز') + ' ' + doc.name;
        },
        action: function(doc) {
            frappe.confirm(
                __('هل أنت متأكد من إكمال هذا الحجز؟'),
                function() {
                    frappe.call({
                        method: 're_studio_booking.re_studio_booking.doctype.booking.booking.update_booking_status',
                        args: {
                            booking: doc.name,
                            status: 'Completed'
                        },
                        callback: function(r) {
                            if (r.message) {
                                frappe.show_alert({
                                    message: __('تم تحديث حالة الحجز'),
                                    indicator: 'green'
                                });
                                cur_list.refresh();
                            }
                        }
                    });
                }
            );
        }
    },
    
    // Add custom actions in the menu
    onload: function(listview) {
        // Add custom CSS
        $('<style>\
            .booking-status-legend {\
                display: flex;\
                align-items: center;\
                margin-bottom: 10px;\
                flex-wrap: wrap;\
            }\
            \
            .booking-status-item {\
                display: flex;\
                align-items: center;\
                margin-right: 15px;\
                margin-bottom: 5px;\
            }\
            \
            .booking-status-indicator {\
                width: 10px;\
                height: 10px;\
                border-radius: 50%;\
                margin-right: 5px;\
            }\
            \
            .booking-status-text {\
                font-size: 12px;\
                color: var(--text-muted);\
            }\
            \
            /* RTL Support */\
            .rtl .booking-status-item {\
                margin-right: 0;\
                margin-left: 15px;\
            }\
            \
            .rtl .booking-status-indicator {\
                margin-right: 0;\
                margin-left: 5px;\
            }\
        </style>').appendTo('head');
        
        // Add status legend
        listview.page.wrapper.find('.list-row-head').before(`
            <div class="booking-status-legend">
                <div class="booking-status-item">
                    <div class="booking-status-indicator" style="background-color: orange;"></div>
                    <div class="booking-status-text">${__('معلق')}</div>
                </div>
                <div class="booking-status-item">
                    <div class="booking-status-indicator" style="background-color: blue;"></div>
                    <div class="booking-status-text">${__('مؤكد')}</div>
                </div>
                <div class="booking-status-item">
                    <div class="booking-status-indicator" style="background-color: green;"></div>
                    <div class="booking-status-text">${__('مكتمل')}</div>
                </div>
                <div class="booking-status-item">
                    <div class="booking-status-indicator" style="background-color: red;"></div>
                    <div class="booking-status-text">${__('ملغي')}</div>
                </div>
            </div>
        `);
    }
};