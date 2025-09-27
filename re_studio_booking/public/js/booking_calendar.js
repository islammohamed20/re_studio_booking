// Booking Calendar JS

frappe.views.calendar['Booking'] = {
    field_map: {
        'start': 'booking_datetime',
        'end': 'booking_end_datetime',
        'id': 'name',
        'title': 'client_name',
        'allDay': 'all_day',
        'color': 'color'
    },
    
    style_map: {
        'Confirmed': 'success',
        'Completed': 'info',
        'Cancelled': 'danger',
        'Pending': 'warning'
    },
    
    get_events_method: 're_studio_booking.re_studio_booking.doctype.booking.booking.get_events',
    
    filters: [
        {
            'fieldtype': 'Link',
            'fieldname': 'photographer',
            'options': 'Photographer',
            'label': __('المصور')
        },
        {
            'fieldtype': 'Link',
            'fieldname': 'service',
            'options': 'Service',
            'label': __('الخدمة')
        },
        {
            'fieldtype': 'Select',
            'fieldname': 'status',
            'options': 'Pending\nConfirmed\nCompleted\nCancelled',
            'label': __('الحالة')
        }
    ],
    
    gantt: false,
    
    get_css_class: function(data) {
        if (data.status === 'Cancelled') {
            return 'strikethrough';
        }
        return '';
    },
    
    onload: function(calendar) {
        // Add custom buttons
        calendar.page.add_menu_item(__('إنشاء حجز جديد'), function() {
            frappe.new_doc('Booking');
        });
        
        calendar.page.add_menu_item(__('عرض قائمة الحجوزات'), function() {
            frappe.set_route('List', 'Booking');
        });
        
        // Add custom filters
        calendar.page.add_menu_item(__('الحجوزات اليوم'), function() {
            calendar.set_filter('booking_date', frappe.datetime.get_today());
        });
        
        calendar.page.add_menu_item(__('الحجوزات هذا الأسبوع'), function() {
            calendar.set_filter('booking_date', ['Between', [frappe.datetime.week_start(), frappe.datetime.week_end()]]);
        });
        
        // Add custom view options
        calendar.page.add_menu_item(__('عرض حسب المصور'), function() {
            frappe.prompt({
                fieldtype: 'Link',
                fieldname: 'photographer',
                options: 'Photographer',
                label: __('اختر المصور'),
                reqd: 1
            }, function(values) {
                calendar.set_filter('photographer', values.photographer);
            }, __('عرض حسب المصور'), __('عرض'));
        });
    },
    
    get_header_html: function(data) {
        // Customize the event popup header
        return `<div>
            <div class="row">
                <div class="col-xs-12">
                    <h4>${data.client_name || ''}</h4>
                </div>
            </div>
            <div class="row">
                <div class="col-xs-6">
                    <span class="indicator ${this.style_map[data.status] || 'gray'}">
                        ${__(data.status)}
                    </span>
                </div>
                <div class="col-xs-6 text-right text-muted">
                    ${data.name}
                </div>
            </div>
        </div>`;
    },
    
    get_body_html: function(data) {
        // Customize the event popup body
        return `<div>
            <div class="row">
                <div class="col-xs-6 text-muted">${__('التاريخ')}</div>
                <div class="col-xs-6">${frappe.datetime.str_to_user(data.booking_date)}</div>
            </div>
            <div class="row">
                <div class="col-xs-6 text-muted">${__('الوقت')}</div>
                <div class="col-xs-6">${frappe.datetime.get_time(data.booking_datetime)} - ${frappe.datetime.get_time(data.booking_end_datetime)}</div>
            </div>
            <div class="row">
                <div class="col-xs-6 text-muted">${__('المصور')}</div>
                <div class="col-xs-6">${data.photographer || '-'}</div>
            </div>
            <div class="row">
                <div class="col-xs-6 text-muted">${__('الخدمة')}</div>
                <div class="col-xs-6">${data.service_name || '-'}</div>
            </div>
            <div class="row">
                <div class="col-xs-6 text-muted">${__('رقم الهاتف')}</div>
                <div class="col-xs-6">${data.phone || data.client_phone || '-'}</div>
            </div>
        </div>`;
    },
    
    get_footer_html: function(data) {
        // Customize the event popup footer with action buttons
        let html = `<div class="row">`;
        
        // View button
        html += `<div class="col-xs-4 text-center">
            <button class="btn btn-xs btn-default btn-view">${__('عرض')}</button>
        </div>`;
        
        // Status-based buttons
        if (data.status === 'Pending' || data.status === 'Confirmed') {
            html += `<div class="col-xs-4 text-center">
                <button class="btn btn-xs btn-success btn-complete">${__('إكمال')}</button>
            </div>`;
            
            html += `<div class="col-xs-4 text-center">
                <button class="btn btn-xs btn-danger btn-cancel">${__('إلغاء')}</button>
            </div>`;
        } else if (data.status === 'Completed') {
            html += `<div class="col-xs-8 text-center">
                <button class="btn btn-xs btn-default btn-invoice">${__('عرض الفاتورة')}</button>
            </div>`;
        } else if (data.status === 'Cancelled') {
            html += `<div class="col-xs-8 text-center">
                <button class="btn btn-xs btn-default btn-restore">${__('استعادة')}</button>
            </div>`;
        }
        
        html += `</div>`;
        return html;
    },
    
    handle_footer_buttons: function(calendar, data) {
        // Handle footer button clicks
        calendar.wrapper.find('.btn-view').on('click', function() {
            frappe.set_route('Form', 'Booking', data.name);
        });
        
        calendar.wrapper.find('.btn-complete').on('click', function() {
            frappe.confirm(
                __('هل أنت متأكد من إكمال هذا الحجز؟'),
                function() {
                    frappe.call({
                        method: 're_studio_booking.re_studio_booking.doctype.booking.booking.update_booking_status',
                        args: {
                            booking: data.name,
                            status: 'Completed'
                        },
                        callback: function(r) {
                            if (r.message) {
                                frappe.show_alert({
                                    message: __('تم تحديث حالة الحجز'),
                                    indicator: 'green'
                                });
                                calendar.refresh();
                            }
                        }
                    });
                }
            );
        });
        
        calendar.wrapper.find('.btn-cancel').on('click', function() {
            frappe.confirm(
                __('هل أنت متأكد من إلغاء هذا الحجز؟'),
                function() {
                    frappe.call({
                        method: 're_studio_booking.re_studio_booking.doctype.booking.booking.update_booking_status',
                        args: {
                            booking: data.name,
                            status: 'Cancelled'
                        },
                        callback: function(r) {
                            if (r.message) {
                                frappe.show_alert({
                                    message: __('تم إلغاء الحجز'),
                                    indicator: 'red'
                                });
                                calendar.refresh();
                            }
                        }
                    });
                }
            );
        });
        
        calendar.wrapper.find('.btn-invoice').on('click', function() {
            frappe.call({
                method: 're_studio_booking.re_studio_booking.doctype.booking.booking.get_invoice',
                args: {
                    booking: data.name
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.set_route('Form', 'Booking Invoice', r.message);
                    } else {
                        frappe.show_alert({
                            message: __('لا توجد فاتورة مرتبطة بهذا الحجز'),
                            indicator: 'red'
                        });
                    }
                }
            });
        });
        
        calendar.wrapper.find('.btn-restore').on('click', function() {
            frappe.confirm(
                __('هل أنت متأكد من استعادة هذا الحجز؟'),
                function() {
                    frappe.call({
                        method: 're_studio_booking.re_studio_booking.doctype.booking.booking.update_booking_status',
                        args: {
                            booking: data.name,
                            status: 'Confirmed'
                        },
                        callback: function(r) {
                            if (r.message) {
                                frappe.show_alert({
                                    message: __('تم استعادة الحجز'),
                                    indicator: 'green'
                                });
                                calendar.refresh();
                            }
                        }
                    });
                }
            );
        });
    }
};