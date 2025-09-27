// Re Studio Booking Dialogs
// Modern dialog system similar to Frappe CRM

class ReStudioDialogs {
    constructor() {
        this.dialogs = {};
    }

    // Create Booking Dialog
    createBookingDialog(callback) {
        if (this.dialogs.booking) {
            this.dialogs.booking.show();
            return;
        }

        this.dialogs.booking = new frappe.ui.Dialog({
            title: '<i class="fas fa-calendar-plus mr-2"></i>' + __('حجز جديد'),
            fields: [
                {
                    fieldtype: 'Section Break',
                    label: __('معلومات العميل')
                },
                {
                    fieldtype: 'Link',
                    fieldname: 'customer',
                    label: __('العميل'),
                    options: 'Customer',
                    reqd: 1,
                    get_query: function() {
                        return {
                            filters: {
                                disabled: 0
                            }
                        };
                    },
                    onchange: function() {
                        let customer = this.get_value();
                        if (customer) {
                            frappe.call({
                                method: 'frappe.client.get',
                                args: {
                                    doctype: 'Customer',
                                    name: customer
                                },
                                callback: function(r) {
                                    if (r.message) {
                                        let dialog = re_studio_dialogs.dialogs.booking;
                                        dialog.set_value('customer_name', r.message.customer_name);
                        dialog.set_value('phone', r.message.phone || '');
                        dialog.set_value('email_id', r.message.email_id || '');
                                    }
                                }
                            });
                        }
                    }
                },
                {
                    fieldtype: 'Column Break'
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'customer_name',
                    label: __('اسم العميل'),
                    reqd: 1
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'phone',
                    label: __('رقم الجوال'),
                    reqd: 1
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'email_id',
                    label: __('البريد الإلكتروني')
                },
                {
                    fieldtype: 'Section Break',
                    label: __('تفاصيل الحجز')
                },
                {
                    fieldtype: 'Link',
                    fieldname: 'service',
                    label: __('الخدمة'),
                    options: 'Service',
                    reqd: 1,
                    get_query: function() {
                        return {
                            filters: {
                                disabled: 0
                            }
                        };
                    },
                    onchange: function() {
                        let service = this.get_value();
                        if (service) {
                            frappe.call({
                                method: 'frappe.client.get',
                                args: {
                                    doctype: 'Service',
                                    name: service
                                },
                                callback: function(r) {
                                    if (r.message) {
                                        let dialog = re_studio_dialogs.dialogs.booking;
                                        dialog.set_value('service_name', r.message.service_name);
                                        dialog.set_value('price', r.message.price || 0);
                                        dialog.set_value('duration', r.message.duration || 60);
                                    }
                                }
                            });
                        }
                    }
                },
                {
                    fieldtype: 'Column Break'
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'service_name',
                    label: __('اسم الخدمة'),
                    read_only: 1
                },
                {
                    fieldtype: 'Currency',
                    fieldname: 'price',
                    label: __('السعر'),
                    reqd: 1
                },
                {
                    fieldtype: 'Int',
                    fieldname: 'duration',
                    label: __('المدة (دقيقة)'),
                    default: 60
                },
                {
                    fieldtype: 'Section Break',
                    label: __('الموعد والمصور')
                },
                {
                    fieldtype: 'Date',
                    fieldname: 'booking_date',
                    label: __('تاريخ الحجز'),
                    reqd: 1,
                    default: frappe.datetime.get_today()
                },
                {
                    fieldtype: 'Time',
                    fieldname: 'booking_time',
                    label: __('وقت الحجز'),
                    reqd: 1
                },
                {
                    fieldtype: 'Column Break'
                },
                {
                    fieldtype: 'Link',
                    fieldname: 'photographer',
                    label: __('المصور'),
                    options: 'Photographer',
                    get_query: function() {
                        return {
                            filters: {
                                status: 'Active'
                            }
                        };
                    }
                },
                {
                    fieldtype: 'Select',
                    fieldname: 'status',
                    label: __('الحالة'),
                    options: 'Pending\nConfirmed',
                    default: 'Pending'
                },
                {
                    fieldtype: 'Section Break',
                    label: __('ملاحظات')
                },
                {
                    fieldtype: 'Small Text',
                    fieldname: 'notes',
                    label: __('ملاحظات إضافية')
                }
            ],
            size: 'large',
            primary_action_label: __('إنشاء الحجز'),
            primary_action: (values) => {
                this.createBooking(values, callback);
            },
            secondary_action_label: __('إلغاء')
        });

        // Add custom styling
        this.styleDialog(this.dialogs.booking);
        this.dialogs.booking.show();
    }

    // Create Service Dialog
    createServiceDialog(callback) {
        if (this.dialogs.service) {
            this.dialogs.service.show();
            return;
        }

        this.dialogs.service = new frappe.ui.Dialog({
            title: '<i class="fas fa-cogs mr-2"></i>' + __('خدمة جديدة'),
            fields: [
                {
                    fieldtype: 'Section Break',
                    label: __('معلومات الخدمة')
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'service_name',
                    label: __('اسم الخدمة'),
                    reqd: 1
                },
                {
                    fieldtype: 'Column Break'
                },
                {
                    fieldtype: 'Link',
                    fieldname: 'category',
                    label: __('التصنيف'),
                    options: 'Category'
                },
                {
                    fieldtype: 'Section Break',
                    label: __('التسعير والمدة')
                },
                {
                    fieldtype: 'Currency',
                    fieldname: 'price',
                    label: __('السعر'),
                    reqd: 1
                },
                {
                    fieldtype: 'Column Break'
                },
                {
                    fieldtype: 'Int',
                    fieldname: 'duration',
                    label: __('المدة (دقيقة)'),
                    default: 60
                },
                {
                    fieldtype: 'Section Break',
                    label: __('الوصف والتفاصيل')
                },
                {
                    fieldtype: 'Small Text',
                    fieldname: 'description',
                    label: __('وصف الخدمة')
                },
                {
                    fieldtype: 'Column Break'
                },
                {
                    fieldtype: 'Check',
                    fieldname: 'is_active',
                    label: __('نشط'),
                    default: 1
                }
            ],
            size: 'large',
            primary_action_label: __('إنشاء الخدمة'),
            primary_action: (values) => {
                this.createService(values, callback);
            },
            secondary_action_label: __('إلغاء')
        });

        this.styleDialog(this.dialogs.service);
        this.dialogs.service.show();
    }

    // Create Photographer Dialog
    createPhotographerDialog(callback) {
        if (this.dialogs.photographer) {
            this.dialogs.photographer.show();
            return;
        }

        this.dialogs.photographer = new frappe.ui.Dialog({
            title: '<i class="fas fa-camera mr-2"></i>' + __('مصور جديد'),
            fields: [
                {
                    fieldtype: 'Section Break',
                    label: __('المعلومات الشخصية')
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'full_name',
                    label: __('الاسم الكامل'),
                    reqd: 1
                },
                {
                    fieldtype: 'Column Break'
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'phone',
                    label: __('رقم الجوال'),
                    reqd: 1
                },
                {
                    fieldtype: 'Section Break',
                    label: __('معلومات الاتصال')
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'email',
                    label: __('البريد الإلكتروني')
                },
                {
                    fieldtype: 'Column Break'
                },
                {
                    fieldtype: 'Select',
                    fieldname: 'status',
                    label: __('الحالة'),
                    options: 'Active\nInactive',
                    default: 'Active'
                },
                {
                    fieldtype: 'Section Break',
                    label: __('التخصص والخبرة')
                },
                {
                    fieldtype: 'Small Text',
                    fieldname: 'specialization',
                    label: __('التخصص')
                },
                {
                    fieldtype: 'Column Break'
                },
                {
                    fieldtype: 'Int',
                    fieldname: 'years_of_experience',
                    label: __('سنوات الخبرة'),
                    default: 1
                }
            ],
            size: 'large',
            primary_action_label: __('إنشاء المصور'),
            primary_action: (values) => {
                this.createPhotographer(values, callback);
            },
            secondary_action_label: __('إلغاء')
        });

        this.styleDialog(this.dialogs.photographer);
        this.dialogs.photographer.show();
    }

    // Create Customer Dialog
    createCustomerDialog(callback) {
        if (this.dialogs.customer) {
            this.dialogs.customer.show();
            return;
        }

        this.dialogs.customer = new frappe.ui.Dialog({
            title: '<i class="fas fa-user-plus mr-2"></i>' + __('عميل جديد'),
            fields: [
                {
                    fieldtype: 'Section Break',
                    label: __('المعلومات الأساسية')
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'customer_name',
                    label: __('اسم العميل'),
                    reqd: 1
                },
                {
                    fieldtype: 'Column Break'
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'phone',
                    label: __('رقم الجوال'),
                    reqd: 1
                },
                {
                    fieldtype: 'Section Break',
                    label: __('معلومات الاتصال')
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'email_id',
                    label: __('البريد الإلكتروني')
                },
                {
                    fieldtype: 'Column Break'
                },
                {
                    fieldtype: 'Select',
                    fieldname: 'customer_type',
                    label: __('نوع العميل'),
                    options: 'Individual\nCompany',
                    default: 'Individual'
                },
                {
                    fieldtype: 'Section Break',
                    label: __('العنوان')
                },
                {
                    fieldtype: 'Small Text',
                    fieldname: 'address',
                    label: __('العنوان')
                }
            ],
            size: 'large',
            primary_action_label: __('إنشاء العميل'),
            primary_action: (values) => {
                this.createCustomer(values, callback);
            },
            secondary_action_label: __('إلغاء')
        });

        this.styleDialog(this.dialogs.customer);
        this.dialogs.customer.show();
    }

    // Style Dialog with modern design
    styleDialog(dialog) {
        // Add custom CSS classes
        dialog.$wrapper.addClass('re-studio-dialog');
        
        // Add loading state functionality
        const primaryBtn = dialog.$wrapper.find('.btn-primary');
        primaryBtn.on('click', function() {
            $(this).addClass('loading');
            setTimeout(() => {
                $(this).removeClass('loading');
            }, 2000);
        });
        
        // Add form validation styling
        dialog.$wrapper.find('.form-control').on('blur', function() {
            const value = $(this).val();
            const isRequired = $(this).attr('data-reqd') === '1';
            
            if (isRequired && !value) {
                $(this).addClass('error').removeClass('success');
            } else if (value) {
                $(this).addClass('success').removeClass('error');
            } else {
                $(this).removeClass('error success');
            }
        });
    }

    // Create Booking
    createBooking(values, callback) {
        frappe.call({
            method: 'frappe.client.insert',
            args: {
                doc: {
                    doctype: 'Booking',
                    customer: values.customer,
                    customer_name: values.customer_name,
                    phone: values.phone,
                    email_id: values.email_id,
                    service: values.service,
                    service_name: values.service_name,
                    price: values.price,
                    duration: values.duration,
                    booking_date: values.booking_date,
                    booking_time: values.booking_time,
                    photographer: values.photographer,
                    status: values.status,
                    notes: values.notes
                }
            },
            callback: (r) => {
                if (r.message) {
                    this.dialogs.booking.hide();
                    frappe.show_alert({
                        message: __('تم إنشاء الحجز بنجاح'),
                        indicator: 'green'
                    }, 3);
                    
                    if (callback) callback(r.message);
                    
                    // Refresh current page if it's a list
                    if (cur_list) {
                        cur_list.refresh();
                    } else if (window.location.pathname.includes('bookings')) {
                        window.location.reload();
                    }
                }
            },
            error: (r) => {
                frappe.show_alert({
                    message: __('حدث خطأ أثناء إنشاء الحجز'),
                    indicator: 'red'
                }, 5);
            }
        });
    }

    // Create Service
    createService(values, callback) {
        frappe.call({
            method: 'frappe.client.insert',
            args: {
                doc: {
                    doctype: 'Service',
                    service_name: values.service_name,
                    category: values.category,
                    price: values.price,
                    duration: values.duration,
                    description: values.description,
                    disabled: !values.is_active
                }
            },
            callback: (r) => {
                if (r.message) {
                    this.dialogs.service.hide();
                    frappe.show_alert({
                        message: __('تم إنشاء الخدمة بنجاح'),
                        indicator: 'green'
                    }, 3);
                    
                    if (callback) callback(r.message);
                    
                    if (cur_list) {
                        cur_list.refresh();
                    } else if (window.location.pathname.includes('services')) {
                        window.location.reload();
                    }
                }
            },
            error: (r) => {
                frappe.show_alert({
                    message: __('حدث خطأ أثناء إنشاء الخدمة'),
                    indicator: 'red'
                }, 5);
            }
        });
    }

    // Create Photographer
    createPhotographer(values, callback) {
        frappe.call({
            method: 'frappe.client.insert',
            args: {
                doc: {
                    doctype: 'Photographer',
                    full_name: values.full_name,
                    phone: values.phone,
                    email: values.email,
                    status: values.status,
                    specialization: values.specialization,
                    years_of_experience: values.years_of_experience
                }
            },
            callback: (r) => {
                if (r.message) {
                    this.dialogs.photographer.hide();
                    frappe.show_alert({
                        message: __('تم إنشاء المصور بنجاح'),
                        indicator: 'green'
                    }, 3);
                    
                    if (callback) callback(r.message);
                    
                    if (cur_list) {
                        cur_list.refresh();
                    } else if (window.location.pathname.includes('photographers')) {
                        window.location.reload();
                    }
                }
            },
            error: (r) => {
                frappe.show_alert({
                    message: __('حدث خطأ أثناء إنشاء المصور'),
                    indicator: 'red'
                }, 5);
            }
        });
    }

    // Create Customer
    createCustomer(values, callback) {
        frappe.call({
            method: 'frappe.client.insert',
            args: {
                doc: {
                    doctype: 'Customer',
                    customer_name: values.customer_name,
                    phone: values.phone,
                    email_id: values.email_id,
                    customer_type: values.customer_type,
                    customer_group: 'Individual', // Default group
                    territory: 'All Territories' // Default territory
                }
            },
            callback: (r) => {
                if (r.message) {
                    this.dialogs.customer.hide();
                    frappe.show_alert({
                        message: __('تم إنشاء العميل بنجاح'),
                        indicator: 'green'
                    }, 3);
                    
                    if (callback) callback(r.message);
                    
                    if (cur_list) {
                        cur_list.refresh();
                    }
                }
            },
            error: (r) => {
                frappe.show_alert({
                    message: __('حدث خطأ أثناء إنشاء العميل'),
                    indicator: 'red'
                }, 5);
            }
        });
    }
}

// Initialize global instance
window.re_studio_dialogs = new ReStudioDialogs();

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ReStudioDialogs;
}