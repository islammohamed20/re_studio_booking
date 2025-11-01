// Booking Form JS

frappe.ui.form.on('Booking', {
    refresh: function(frm) {
        // Add custom buttons based on status
        if (frm.doc.docstatus === 1) {
            if (frm.doc.status === 'Confirmed') {
                // Add Complete button
                frm.add_custom_button(__('إكمال الحجز'), function() {
                    update_booking_status(frm, 'Completed');
                }, __('تغيير الحالة'));
                
                // Add Cancel button
                frm.add_custom_button(__('إلغاء الحجز'), function() {
                    update_booking_status(frm, 'Cancelled');
                }, __('تغيير الحالة'));
            } else if (frm.doc.status === 'Pending') {
                // Add Confirm button
                frm.add_custom_button(__('تأكيد الحجز'), function() {
                    update_booking_status(frm, 'Confirmed');
                }, __('تغيير الحالة'));
                
                // Add Cancel button
                frm.add_custom_button(__('إلغاء الحجز'), function() {
                    update_booking_status(frm, 'Cancelled');
                }, __('تغيير الحالة'));
            } else if (frm.doc.status === 'Cancelled') {
                // Add Restore button
                frm.add_custom_button(__('استعادة الحجز'), function() {
                    update_booking_status(frm, 'Confirmed');
                }, __('تغيير الحالة'));
            }
            
            // Add Create Quotation button
            if (['Draft', 'Pending'].includes(frm.doc.status) && !frm.doc.quotation) {
                frm.add_custom_button(__('إنشاء عرض سعر'), function() {
                    create_quotation(frm);
                }, __('إجراءات'));
            }
            
            // Add View Quotation button if quotation exists
            if (frm.doc.quotation) {
                frm.add_custom_button(__('عرض العرض'), function() {
                    frappe.set_route('Form', 'Booking Quotation', frm.doc.quotation);
                }, __('إجراءات'));
            }
            
            // Add Create Invoice button if not already created
            if (['Confirmed', 'Completed'].includes(frm.doc.status) && !frm.doc.invoice) {
                frm.add_custom_button(__('إنشاء فاتورة'), function() {
                    create_invoice(frm);
                }, __('إجراءات'));
            }
            
            // Add View Invoice button if invoice exists
            if (frm.doc.invoice) {
                frm.add_custom_button(__('عرض الفاتورة'), function() {
                    frappe.set_route('Form', 'Booking Invoice', frm.doc.invoice);
                }, __('إجراءات'));
            }
            
            // Add Send Confirmation button
            if (['Confirmed', 'Completed'].includes(frm.doc.status)) {
                frm.add_custom_button(__('إرسال تأكيد الحجز'), function() {
                    send_booking_confirmation(frm);
                }, __('إجراءات'));
            }
        }
        
        // Add custom indicators
        if (frm.doc.docstatus === 1) {
            let status_colors = {
                'Pending': 'orange',
                'Confirmed': 'blue',
                'Completed': 'green',
                'Cancelled': 'red'
            };
            
            frm.page.set_indicator(__(frm.doc.status), status_colors[frm.doc.status] || 'gray');
        }
        
        // Add custom CSS
        frm.set_intro('');
        if (frm.doc.docstatus === 1) {
            let intro_html = '';
            
            if (frm.doc.status === 'Confirmed') {
                intro_html = `<div class="alert alert-info">
                    ${__('هذا الحجز مؤكد. تاريخ الحجز')}: ${frappe.datetime.str_to_user(frm.doc.booking_date)}
                </div>`;
            } else if (frm.doc.status === 'Completed') {
                intro_html = `<div class="alert alert-success">
                    ${__('تم إكمال هذا الحجز بنجاح')}
                </div>`;
            } else if (frm.doc.status === 'Cancelled') {
                intro_html = `<div class="alert alert-danger">
                    ${__('تم إلغاء هذا الحجز')}
                </div>`;
            }
            
            if (intro_html) {
                frm.set_intro(intro_html);
            }
        }
        
        // Make fields read-only after submit
        if (frm.doc.docstatus === 1) {
            frm.set_df_property('booking_date', 'read_only', 1);
            frm.set_df_property('start_time', 'read_only', 1);
            frm.set_df_property('end_time', 'read_only', 1);
            frm.set_df_property('client', 'read_only', 1);
            frm.set_df_property('client_name', 'read_only', 1);
            frm.set_df_property('phone', 'read_only', 1);
            frm.set_df_property('client_email', 'read_only', 1);
            frm.set_df_property('service', 'read_only', 1);
            frm.set_df_property('photographer', 'read_only', 1);
        }
        
        // Add timeline message for status changes
        if (frm.doc.status_history && frm.doc.status_history.length > 0) {
            frm.timeline.insert_comment('Status History', '');
            
            frm.doc.status_history.forEach(function(history) {
                let status_colors = {
                    'Pending': 'orange',
                    'Confirmed': 'blue',
                    'Completed': 'green',
                    'Cancelled': 'red'
                };
                
                let color = status_colors[history.status] || 'gray';
                let icon = '';
                
                if (history.status === 'Confirmed') {
                    icon = 'fa fa-check-circle';
                } else if (history.status === 'Completed') {
                    icon = 'fa fa-trophy';
                } else if (history.status === 'Cancelled') {
                    icon = 'fa fa-times-circle';
                } else {
                    icon = 'fa fa-clock-o';
                }
                
                let html = `<div class="timeline-badge ${color}">
                    <i class="${icon}"></i>
                </div>
                <div class="timeline-content">
                    <div class="timeline-head">
                        <span class="timeline-title">${__('تغيير الحالة إلى')} ${__(history.status)}</span>
                        <span class="timeline-time">${frappe.datetime.str_to_user(history.timestamp)}</span>
                    </div>
                    <div class="timeline-body">
                        ${__('تم تغيير الحالة بواسطة')}: ${history.user}
                    </div>
                </div>`;
                
                frm.timeline.insert_comment('Status Change', html);
            });
        }
    },
    
    onload: function(frm) {
        // Set default values for new document
        if (frm.is_new()) {
            frm.set_value('booking_date', frappe.datetime.get_today());
            
            // Get default booking time from General Settings
            frappe.call({
                method: 're_studio_booking.re_studio_booking.doctype.general_settings.general_settings.get_booking_settings',
                callback: function(r) {
                    if (r.message && r.message.business_start_time) {
                        frm.set_value('start_time', r.message.business_start_time);
                    }
                }
            });
        }
        
        // Set up field dependencies
        setup_field_dependencies(frm);
    },
    
    validate: function(frm) {
        // Calculate booking duration and end time
        calculate_booking_duration(frm);
    },
    
    booking_date: function(frm) {
        // Check if date is valid (not in the past, not a holiday)
        validate_booking_date(frm);
        
        // Update available photographers and time slots
        update_available_photographers(frm);
        update_available_time_slots(frm);
    },
    
    start_time: function(frm) {
        // Update available photographers based on time
        update_available_photographers(frm);
        
        // Calculate booking end time
        calculate_booking_duration(frm);
    },
    
    service: function(frm) {
        // Get service details and update fields
        if (frm.doc.service) {
            frappe.call({
                method: 're_studio_booking.re_studio_booking.doctype.booking.booking.get_service_details',
                args: {
                    service: frm.doc.service
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('service_name', r.message.service_name);
                        frm.set_value('service_name_ar', r.message.service_name_ar);
                        frm.set_value('duration', r.message.duration);
                        frm.set_value('price', r.message.price);
                        
                        // Calculate booking end time
                        calculate_booking_duration(frm);
                        
                        // Update available photographers based on service
                        update_available_photographers(frm);
                    }
                }
            });
        }
    },
    
    photographer: function(frm) {
        // Get photographer details
        if (frm.doc.photographer) {
            frappe.call({
                method: 're_studio_booking.re_studio_booking.doctype.booking.booking.get_photographer_details',
                args: {
                    photographer: frm.doc.photographer
                },
                callback: function(r) {
                    if (r.message) {
                        // photographer_name field removed from Booking DocType
                        // The photographer name can be accessed via the link field
                    }
                }
            });
        }
        
        // Update available time slots when photographer changes
        if (frm.doc.booking_date) {
            update_available_time_slots(frm);
        }
    },
    
    client: function(frm) {
        // Get client details
        if (frm.doc.client) {
            frappe.call({
                method: 're_studio_booking.re_studio_booking.doctype.booking.booking.get_client_details',
                args: {
                    client: frm.doc.client
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('client_name', r.message.client_name);
                        frm.set_value('phone', r.message.phone);
                        frm.set_value('client_email', r.message.email);
                    }
                }
            });
        }
    },
    
    duration: function(frm) {
        // Calculate booking end time when duration changes
        calculate_booking_duration(frm);
    }
});

// Helper functions
function update_booking_status(frm, status) {
    frappe.confirm(
        __('هل أنت متأكد من تغيير حالة الحجز إلى') + ' ' + __(status) + '?',
        function() {
            frappe.call({
                method: 're_studio_booking.re_studio_booking.doctype.booking.booking.update_booking_status',
                args: {
                    booking: frm.doc.name,
                    status: status
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.show_alert({
                            message: __('تم تحديث حالة الحجز'),
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    }
                }
            });
        }
    );
}

function create_quotation(frm) {
    frappe.call({
        method: 're_studio_booking.re_studio_booking.doctype.booking.booking.create_booking_quotation',
        args: {
            booking: frm.doc.name
        },
        callback: function(r) {
            if (r.message && r.message.success) {
                frappe.show_alert({
                    message: r.message.message,
                    indicator: 'green'
                });
                frm.reload_doc();
                if (r.message.quotation) {
                    frappe.set_route('Form', 'Booking Quotation', r.message.quotation);
                }
            } else {
                frappe.show_alert({
                    message: r.message ? r.message.message : __('خطأ في إنشاء العرض'),
                    indicator: 'red'
                });
            }
        }
    });
}

function create_invoice(frm) {
    frappe.call({
        method: 're_studio_booking.re_studio_booking.doctype.booking.booking.create_booking_invoice',
        args: {
            booking: frm.doc.name
        },
        callback: function(r) {
            if (r.message && r.message.success) {
                frappe.show_alert({
                    message: r.message.message,
                    indicator: 'green'
                });
                frm.reload_doc();
                if (r.message.invoice) {
                    frappe.set_route('Form', 'Booking Invoice', r.message.invoice);
                }
            } else {
                frappe.show_alert({
                    message: r.message ? r.message.message : __('خطأ في إنشاء الفاتورة'),
                    indicator: 'red'
                });
            }
        }
    });
}

function send_booking_confirmation(frm) {
    frappe.call({
        method: 're_studio_booking.re_studio_booking.doctype.booking.booking.send_booking_confirmation',
        args: {
            booking: frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                frappe.show_alert({
                    message: __('تم إرسال تأكيد الحجز بنجاح'),
                    indicator: 'green'
                });
            }
        }
    });
}

function validate_booking_date(frm) {
    if (!frm.doc.booking_date) return;
    
    let today = frappe.datetime.get_today();
    if (frm.doc.booking_date < today) {
        frappe.msgprint({
            title: __('تاريخ غير صالح'),
            indicator: 'red',
            message: __('لا يمكن الحجز في تاريخ سابق')
        });
        frm.set_value('booking_date', today);
        return;
    }
    
    // Check if date is a holiday or outside business days
    frappe.call({
        method: 're_studio_booking.re_studio_booking.doctype.booking.booking.validate_booking_date',
        args: {
            booking_date: frm.doc.booking_date
        },
        callback: function(r) {
            if (r.message && !r.message.valid) {
                frappe.msgprint({
                    title: __('تاريخ غير صالح'),
                    indicator: 'red',
                    message: r.message.message
                });
                frm.set_value('booking_date', r.message.next_available_date);
            }
        }
    });
}

function update_available_photographers(frm) {
    if (!frm.doc.booking_date || !frm.doc.start_time || !frm.doc.service) return;
    
    frappe.call({
        method: 're_studio_booking.re_studio_booking.doctype.booking.booking.get_available_photographers',
        args: {
            booking_date: frm.doc.booking_date,
            booking_time: frm.doc.start_time,
            service: frm.doc.service,
            duration: frm.doc.duration
        },
        callback: function(r) {
            if (r.message) {
                // Update photographer options
                frm.set_query('photographer', function() {
                    return {
                        filters: {
                            'name': ['in', r.message]
                        }
                    };
                });
                
                // Check if current photographer is available
                if (frm.doc.photographer && !r.message.includes(frm.doc.photographer)) {
                    frappe.msgprint({
                        title: __('المصور غير متاح'),
                        indicator: 'red',
                        message: __('المصور المحدد غير متاح في هذا الوقت. الرجاء اختيار مصور آخر.')
                    });
                    frm.set_value('photographer', '');
                }
            }
        }
    });
}

function update_available_time_slots(frm) {
    if (!frm.doc.booking_date) return;
    
    frappe.call({
        method: 're_studio_booking.re_studio_booking.doctype.booking.booking.get_available_time_slots',
        args: {
            booking_date: frm.doc.booking_date,
            service: frm.doc.service,
            photographer: frm.doc.photographer
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                // Update time field options
                frm.set_df_property('start_time', 'options', r.message.join('\n'));
                
                // Check if current time is available (normalize format for comparison)
                if (frm.doc.start_time) {
                    // Normalize current time format (remove microseconds if any)
                    let current_time = String(frm.doc.start_time).split('.')[0];
                    
                    // Check if time exists in available slots
                    let time_available = r.message.some(slot => {
                        let slot_time = String(slot).split('.')[0];
                        return slot_time === current_time;
                    });
                    
                    if (!time_available) {
                        // Only show message if we're editing an existing booking
                        if (!frm.is_new()) {
                            frappe.msgprint({
                                title: __('الوقت غير متاح'),
                                indicator: 'orange',
                                message: __('الوقت المحدد سابقاً غير متاح الآن. سيتم اختيار أول وقت متاح.')
                            });
                        }
                        // Set to first available slot silently for new bookings
                        frm.set_value('start_time', r.message[0]);
                    }
                }
            } else {
                // No available slots
                frappe.msgprint({
                    title: __('لا توجد أوقات متاحة'),
                    indicator: 'orange',
                    message: __('جميع الأوقات محجوزة لهذا اليوم. الرجاء اختيار يوم آخر.')
                });
                frm.set_df_property('start_time', 'options', '');
            }
        }
    });
}

function calculate_booking_duration(frm) {
    if (!frm.doc.booking_date || !frm.doc.start_time || !frm.doc.duration) return;
    
    // Calculate booking end time
    let booking_datetime = frappe.datetime.user_to_str(frm.doc.booking_date + ' ' + frm.doc.start_time);
    let end_datetime = moment(booking_datetime).add(frm.doc.duration, 'minutes').format('YYYY-MM-DD HH:mm:ss');
    let end_time = moment(end_datetime).format('HH:mm:ss');
    
    frm.set_value('end_time', end_time);
}

function setup_field_dependencies(frm) {
    // Set up queries for link fields
    frm.set_query('service', function() {
        return {
            filters: {
                'is_active': 1
            }
        };
    });
    
    frm.set_query('photographer', function() {
        return {
            filters: {
                'is_active': 1
            }
        };
    });

    // Show only active clients, ignore user permissions server-side already
    frm.set_query('client', function() {
        return {
            filters: {
                'status': 'Active'
            }
        };
    });
}

// Child table logic: toggle Booking Service Item fields by service unit type
frappe.ui.form.on('Booking Service Item', {
    form_render: function(frm, cdt, cdn) {
        // When a row is opened, ensure unit fields are populated
        update_service_unit_fields(frm, cdt, cdn);
    },
    service: function(frm, cdt, cdn) {
        // When service changes, fetch unit type and duration unit and update hidden fields
        update_service_unit_fields(frm, cdt, cdn);
    }
});

function update_service_unit_fields(frm, cdt, cdn) {
    const row = frappe.get_doc(cdt, cdn);
    if (!row || !row.service) {
        return;
    }
    frappe.db.get_value('Service', row.service, ['type_unit', 'duration_unit']).then(r => {
        const sv = r && r.message ? r.message : {};
        const unit_type = sv.type_unit || '';
        const duration_unit = sv.duration_unit || '';
        // Store in hidden helper fields on the row so depends_on can react
        row.service_unit_type = unit_type;
        row.service_duration_unit = duration_unit;

        // Optional: clear irrelevant fields to avoid confusion
        if (unit_type === 'مدة') {
            if (duration_unit === 'ساعة') {
                row.min_duration = 0;
                row.mount = 0;
                if (!row.quantity || row.quantity < 0) row.quantity = 1;
            } else if (duration_unit === 'دقيقة') {
                row.quantity = 0;
                row.mount = 0;
                if (!row.min_duration || row.min_duration < 0) row.min_duration = 1;
            }
        } else {
            row.quantity = 0;
            row.min_duration = 0;
            if (!row.mount || row.mount < 0) row.mount = 1;
        }

        // Refresh the table so depends_on/make_required take effect visually
        frm.refresh_field('selected_services_table');
    });
}