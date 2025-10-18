// Photographer Form JS

frappe.ui.form.on('Photographer', {
    refresh: function(frm) {
        // Add custom buttons
        if (frm.doc.docstatus === 1) {
            // Add View Bookings button
            frm.add_custom_button(__('عرض الحجوزات'), function() {
                frappe.set_route('List', 'Booking', {
                    'photographer': frm.doc.name
                });
            }, __('إجراءات'));
            
            // Add Add Holiday button
            frm.add_custom_button(__('إضافة إجازة'), function() {
                create_holiday(frm);
            }, __('إجراءات'));
            
            // Add View Holidays button
            frm.add_custom_button(__('عرض الإجازات'), function() {
                frappe.set_route('List', 'Photographer Holiday', {
                    'photographer': frm.doc.name
                });
            }, __('إجراءات'));
        }
        
        // Add custom indicators based on status field
        if (frm.doc.docstatus === 1) {
            if (frm.doc.status === 'Active') {
                frm.page.set_indicator(__('نشط'), 'green');
            } else if (frm.doc.status === 'On Leave') {
                frm.page.set_indicator(__('في إجازة'), 'orange');
            } else {
                frm.page.set_indicator(__('غير نشط'), 'red');
            }
        }
        
        // Add custom CSS
        frm.set_intro('');
        if (frm.doc.docstatus === 1) {
            let intro_html = '';
            
            if (frm.doc.status === 'Active') {
                intro_html = `<div class="alert alert-success">
                    ${__('هذا المصور نشط ومتاح للحجوزات')}
                </div>`;
            } else if (frm.doc.status === 'On Leave') {
                intro_html = `<div class="alert alert-warning">
                    ${__('هذا المصور في إجازة حالياً')}
                </div>`;
            } else {
                intro_html = `<div class="alert alert-danger">
                    ${__('هذا المصور غير نشط ولا يمكن حجزه')}
                </div>`;
            }
            
            if (intro_html) {
                frm.set_intro(intro_html);
            }
        }
        
        // Add custom sections
        if (frm.doc.name && !frm.doc.__islocal) {
            add_booking_stats_section(frm);
        }
    },
    
    onload: function(frm) {
        // Set default values for new document
        if (frm.is_new()) {
            // status is already set to "Active" by default in DocType
            
            // Set default working hours
            set_default_working_hours(frm);
        }
    },
    
    validate: function(frm) {
        // Validate working hours
        validate_working_hours(frm);
    }
});

// Child table for Photographer Working Hours
frappe.ui.form.on('Photographer Working Hours', {
    is_working_day: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (row.is_working_day) {
            // Set default start and end time if empty
            if (!row.start_time) {
                frappe.model.set_value(cdt, cdn, 'start_time', '09:00:00');
            }
            
            if (!row.end_time) {
                frappe.model.set_value(cdt, cdn, 'end_time', '18:00:00');
            }
        } else {
            // Clear times if not a working day
            frappe.model.set_value(cdt, cdn, 'start_time', '');
            frappe.model.set_value(cdt, cdn, 'end_time', '');
        }
    },
    
    start_time: function(frm, cdt, cdn) {
        validate_time_range(frm, cdt, cdn);
    },
    
    end_time: function(frm, cdt, cdn) {
        validate_time_range(frm, cdt, cdn);
    }
});

// Child table for Photographer Service
frappe.ui.form.on('Photographer Service', {
    service: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (row.service) {
            frappe.call({
                method: 're_studio_booking.re_studio_booking.doctype.photographer_service.photographer_service.get_service_details',
                args: {
                    service: row.service
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'service_name', r.message.service_name);
                        
                        // Set special price to service price by default if not set
                        if (!row.special_price) {
                            frappe.model.set_value(cdt, cdn, 'special_price', r.message.price);
                        }
                    }
                }
            });
        }
    }
});

// Helper functions
function create_holiday(frm) {
    let d = new frappe.ui.Dialog({
        title: __('إضافة إجازة جديدة'),
        fields: [
            {
                label: __('نوع الإجازة'),
                fieldname: 'holiday_type',
                fieldtype: 'Select',
                options: 'Vacation\nSick Leave\nPersonal Leave\nOther',
                reqd: 1
            },
            {
                label: __('تاريخ البداية'),
                fieldname: 'start_date',
                fieldtype: 'Date',
                default: frappe.datetime.get_today(),
                reqd: 1
            },
            {
                label: __('تاريخ النهاية'),
                fieldname: 'end_date',
                fieldtype: 'Date',
                default: frappe.datetime.get_today(),
                reqd: 1
            },
            {
                label: __('الوصف'),
                fieldname: 'description',
                fieldtype: 'Small Text'
            }
        ],
        primary_action_label: __('إضافة'),
        primary_action: function(values) {
            frappe.call({
                method: 're_studio_booking.re_studio_booking.doctype.photographer_holiday.photographer_holiday.create_holiday',
                args: {
                    photographer: frm.doc.name,
                    holiday_type: values.holiday_type,
                    start_date: values.start_date,
                    end_date: values.end_date,
                    description: values.description
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.show_alert({
                            message: __('تم إضافة الإجازة بنجاح'),
                            indicator: 'green'
                        });
                        d.hide();
                    }
                }
            });
        }
    });
    d.show();
}

function set_default_working_hours(frm) {
    // Get default working hours from settings
    frappe.call({
        method: 're_studio_booking.re_studio_booking.doctype.booking_settings.booking_settings.get_working_days',
        callback: function(r) {
            if (r.message) {
                let working_days = r.message;
                let days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
                let day_names = {
                    'sunday': __('الأحد'),
                    'monday': __('الإثنين'),
                    'tuesday': __('الثلاثاء'),
                    'wednesday': __('الأربعاء'),
                    'thursday': __('الخميس'),
                    'friday': __('الجمعة'),
                    'saturday': __('السبت')
                };
                
                // Get business hours
                frappe.call({
                    method: 're_studio_booking.re_studio_booking.doctype.booking_settings.booking_settings.get_business_hours',
                    callback: function(r2) {
                        if (r2.message) {
                            let business_hours = r2.message;
                            
                            // Clear existing rows
                            frm.clear_table('working_hours');
                            
                            // Add working hours for each day
                            days.forEach(function(day) {
                                // يوم الجمعة هو يوم عمل عادي في الاستديو - ليس عطلة
                                let is_working = working_days.includes(day) || day === 'friday';
                                
                                let row = frm.add_child('working_hours');
                                row.day = day_names[day];
                                row.is_working_day = is_working ? 1 : 0;
                                
                                if (is_working) {
                                    row.start_time = business_hours.start_time;
                                    row.end_time = business_hours.end_time;
                                }
                            });
                            
                            frm.refresh_field('working_hours');
                        }
                    }
                });
            }
        }
    });
}

function validate_working_hours(frm) {
    // (مطلوب سابقاً) تحذير عند عدم تحديد أيام عمل.
    // بناءً على متطلب جديد: ليس شرطاً تحديد أيام عمل للمصور.
    // إبقاء الدالة فارغة لتجنب أي تحذير.
    return;
}

function validate_time_range(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    
    if (row.start_time && row.end_time) {
        // Convert times to minutes for comparison
        let start_minutes = time_to_minutes(row.start_time);
        let end_minutes = time_to_minutes(row.end_time);
        
        if (end_minutes <= start_minutes) {
            frappe.msgprint({
                title: __('خطأ في الوقت'),
                indicator: 'red',
                message: __('وقت النهاية يجب أن يكون بعد وقت البداية')
            });
            
            // Reset end time to start time + 1 hour
            let new_end_time = new Date();
            new_end_time.setHours(parseInt(row.start_time.split(':')[0]));
            new_end_time.setMinutes(parseInt(row.start_time.split(':')[1]));
            new_end_time.setHours(new_end_time.getHours() + 1);
            
            let hours = new_end_time.getHours().toString().padStart(2, '0');
            let minutes = new_end_time.getMinutes().toString().padStart(2, '0');
            
            frappe.model.set_value(cdt, cdn, 'end_time', `${hours}:${minutes}:00`);
        }
    }
}

function time_to_minutes(time_str) {
    let parts = time_str.split(':');
    return parseInt(parts[0]) * 60 + parseInt(parts[1]);
}

function add_booking_stats_section(frm) {
    // Add booking statistics section
    frappe.call({
        method: 're_studio_booking.re_studio_booking.doctype.photographer.photographer.get_booking_stats',
        args: {
            photographer: frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                let stats = r.message;
                
                // Create HTML for stats
                let html = `<div class="row">
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value">${stats.total_bookings || 0}</div>
                            <div class="stat-label">${__('إجمالي الحجوزات')}</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value">${stats.completed_bookings || 0}</div>
                            <div class="stat-label">${__('الحجوزات المكتملة')}</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value">${stats.upcoming_bookings || 0}</div>
                            <div class="stat-label">${__('الحجوزات القادمة')}</div>
                        </div>
                    </div>
                </div>`;
                
                // Add upcoming bookings if available
                if (stats.upcoming_bookings_list && stats.upcoming_bookings_list.length > 0) {
                    html += `<div class="upcoming-bookings-section">
                        <h4>${__('الحجوزات القادمة')}</h4>
                        <div class="table-responsive">
                            <table class="table table-bordered table-hover">
                                <thead>
                                    <tr>
                                        <th>${__('رقم الحجز')}</th>
                                        <th>${__('التاريخ')}</th>
                                        <th>${__('الوقت')}</th>
                                        <th>${__('العميل')}</th>
                                        <th>${__('الخدمة')}</th>
                                    </tr>
                                </thead>
                                <tbody>`;
                    
                    stats.upcoming_bookings_list.forEach(function(booking) {
                        html += `<tr data-booking="${booking.name}" style="cursor: pointer;">
                            <td>${booking.name}</td>
                            <td>${frappe.datetime.str_to_user(booking.booking_date)}</td>
                            <td>${frappe.datetime.get_time(booking.booking_datetime)}</td>
                            <td>${booking.customer_name}</td>
                            <td>${booking.service_name}</td>
                        </tr>`;
                    });
                    
                    html += `</tbody>
                            </table>
                        </div>
                    </div>`;
                }
                
                // Add custom section to form
                $(frm.fields_dict.booking_stats_html.wrapper).html(html);
                
                // Add click handler for booking rows
                $(frm.fields_dict.booking_stats_html.wrapper).find('tr[data-booking]').on('click', function() {
                    let booking = $(this).attr('data-booking');
                    frappe.set_route('Form', 'Booking', booking);
                });
                
                // Add custom CSS
                $(frm.fields_dict.booking_stats_html.wrapper).find('.stat-card').css({
                    'background-color': 'var(--card-bg)',
                    'border-radius': '8px',
                    'padding': '15px',
                    'box-shadow': 'var(--card-shadow)',
                    'margin-bottom': '15px',
                    'text-align': 'center'
                });
                
                $(frm.fields_dict.booking_stats_html.wrapper).find('.stat-value').css({
                    'font-size': '24px',
                    'font-weight': 'bold',
                    'color': 'var(--text-color)'
                });
                
                $(frm.fields_dict.booking_stats_html.wrapper).find('.stat-label').css({
                    'font-size': '13px',
                    'color': 'var(--text-muted)',
                    'margin-top': '5px'
                });
                
                $(frm.fields_dict.booking_stats_html.wrapper).find('.upcoming-bookings-section').css({
                    'margin-top': '20px'
                });
            }
        }
    });
}