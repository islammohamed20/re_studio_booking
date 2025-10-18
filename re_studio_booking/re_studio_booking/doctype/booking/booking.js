// Copyright (c) 2023, MASAR TEAM and contributors
// For license information, please see license.txt

frappe.ui.form.on('Booking', {
	refresh: function(frm) {
		// Set default booking type if not set
		if (!frm.doc.booking_type) {
			frm.set_value('booking_type', 'Service');
		}
		
		// عرض إعدادات الاستديو من General Settings
		load_studio_settings(frm);
		
		// Filter services and packages based on booking type
		setup_filters(frm);
	},
	
	booking_type: function(frm) {
		// Clear related fields when booking type changes
		if (frm.doc.booking_type === 'Service') {
			frm.set_value('package', '');
			frm.set_value('package_name', '');
			frm.clear_table('package_services_table');
		} else if (frm.doc.booking_type === 'Package') {
			frm.set_value('service', '');
			frm.set_value('service_name', '');
			frm.set_value('category', '');
			frm.set_value('duration', '');
		}
		
		// Setup filters
		setup_filters(frm);
		frm.refresh();
	},
	
	package: function(frm) {
		// Populate package services when package is selected
		if (frm.doc.package && frm.doc.booking_type === 'Package') {
			frappe.call({
				method: 're_studio_booking.re_studio_booking.doctype.booking.booking.get_package_services',
				args: {
					package_name: frm.doc.package
				},
				callback: function(r) {
					if (r.message && r.message.services) {
						// Clear existing table
						frm.clear_table('package_services_table');
						
						// Set package info
						if (r.message.total_hours) {
							frm.set_value('remaining_hours', r.message.total_hours);
						}
						
						// Add services to table
						r.message.services.forEach(function(service) {
							let row = frm.add_child('package_services_table');
							row.service = service.service;
							row.service_name = service.service_name;
							row.quantity = service.quantity;
							row.service_price = service.service_price;
							row.base_price = service.base_price;
							row.package_price = service.package_price;
							row.amount = service.amount;
							row.is_mandatory = service.is_mandatory;
						});
						
						// Refresh table
						frm.refresh_field('package_services_table');
						
						// Success message
						frappe.show_alert({
							message: __('تم تحميل خدمات الباقة بنجاح'),
							indicator: 'green'
						}, 3);
					}
				},
				error: function(r) {
					frappe.msgprint({
						title: __('خطأ'),
						indicator: 'red',
						message: __('لم يتم العثور على خدمات الباقة')
					});
				}
			});
		}
	}
});

// ================ Package Booking Dates - حساب الساعات تلقائياً ================
frappe.ui.form.on('Package Booking Date', {
	start_time: function(frm, cdt, cdn) {
		calculate_hours_for_row(frm, cdt, cdn);
	},
	
	end_time: function(frm, cdt, cdn) {
		calculate_hours_for_row(frm, cdt, cdn);
	},
	
	package_booking_dates_add: function(frm, cdt, cdn) {
		// منع إضافة صف جديد إذا كانت الساعات المتبقية = 0
		check_remaining_hours_before_add(frm);
	}
});

function calculate_hours_for_row(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	
	if (row.start_time && row.end_time) {
		// حساب الفرق بين الوقتين
		let start = frappe.datetime.str_to_obj(row.start_time);
		let end = frappe.datetime.str_to_obj(row.end_time);
		
		// إذا كان وقت النهاية أصغر من البداية (عبور منتصف الليل)
		if (end <= start) {
			end.setDate(end.getDate() + 1);
		}
		
		// حساب الفرق بالساعات
		let diff_ms = end - start;
		let hours = diff_ms / (1000 * 60 * 60);
		
		// تعيين القيمة
		frappe.model.set_value(cdt, cdn, 'hours', hours.toFixed(2));
		
		// إعادة حساب إجمالي الساعات
		calculate_total_used_hours(frm);
	}
}

function calculate_total_used_hours(frm) {
	// جمع كل الساعات من جدول تواريخ الحجز
	let total_used = 0;
	
	if (frm.doc.package_booking_dates) {
		frm.doc.package_booking_dates.forEach(function(row) {
			if (row.hours) {
				total_used += parseFloat(row.hours);
			}
		});
	}
	
	// تحديث حقل الساعات المستخدمة
	frm.set_value('used_hours', total_used.toFixed(2));
	
	// حساب الساعات المتبقية
	let remaining = 0;
	if (frm.doc.package) {
		// جلب إجمالي ساعات الباقة
		frappe.db.get_value('Package', frm.doc.package, 'total_hours', function(r) {
			if (r && r.total_hours) {
				remaining = parseFloat(r.total_hours) - total_used;
				frm.set_value('remaining_hours', Math.max(0, remaining).toFixed(2));
				
				// إذا وصلت الساعات المتبقية لصفر - عرض تنبيه
				if (remaining <= 0) {
					frappe.show_alert({
						message: __('⚠️ تم استنفاد جميع ساعات الباقة'),
						indicator: 'red'
					}, 5);
				}
			}
		});
	}
}

function check_remaining_hours_before_add(frm) {
	// التحقق من الساعات المتبقية قبل السماح بإضافة صف جديد
	if (frm.doc.remaining_hours !== undefined && parseFloat(frm.doc.remaining_hours) <= 0) {
		// حذف الصف الجديد المضاف
		let last_row = frm.doc.package_booking_dates[frm.doc.package_booking_dates.length - 1];
		frm.get_field("package_booking_dates").grid.grid_rows_by_docname[last_row.name].remove();
		
		// عرض رسالة تحذير
		frappe.show_alert({
			message: __('⚠️ تم استنفاد جميع ساعات الباقة. لا يمكن إضافة تواريخ حجز إضافية'),
			indicator: 'red'
		}, 7);
		
		return false;
	}
	return true;
}

function setup_filters(frm) {
	// Filter services to show only active ones
	frm.set_query('service', function() {
		return {
			filters: {
				'is_active': 1
			}
		};
	});
	
	// Filter packages to show only active ones
	frm.set_query('package', function() {
		return {
			filters: {
				'is_active': 1
			}
		};
	});
	
	// Filter photographers to show only active ones
	frm.set_query('photographer', function() {
		return {
			filters: {
				'is_active': 1
			}
		};
	});
}

// ================ General Settings Integration ================

function load_studio_settings(frm) {
	// جلب إعدادات الاستديو من General Settings
	frappe.call({
		method: 're_studio_booking.re_studio_booking.doctype.booking.booking.get_studio_settings',
		callback: function(r) {
			if (r.message) {
				frm.studio_settings = r.message;
				
				// عرض معلومات أيام العمل في intro
				if (frm.studio_settings.working_days) {
					let days_arabic = {
						'Sunday': 'الأحد',
						'Monday': 'الاثنين',
						'Tuesday': 'الثلاثاء', 
						'Wednesday': 'الأربعاء',
						'Thursday': 'الخميس',
						'Friday': 'الجمعة',
						'Saturday': 'السبت'
					};
					
					let working_days_arabic = frm.studio_settings.working_days.map(day => days_arabic[day]).join('، ');
					let friday_status = frm.studio_settings.is_friday_working ? 'يوم عمل' : 'عطلة رسمية';
					
					frm.set_intro(`
						<div style="background: #e7f3ff; padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid #0693e3;">
							<strong>📅 أيام عمل الاستديو:</strong> ${working_days_arabic}<br>
							<strong>🕐 ساعات العمل:</strong> ${frm.studio_settings.business_hours.opening_time} - ${frm.studio_settings.business_hours.closing_time}<br>
							<strong>🕌 الجمعة:</strong> ${friday_status}<br>
							<small style="color: #6c757d;"><i>حسب إعدادات General Settings</i></small>
						</div>
					`);
				}
			}
		}
	});
}

// تحسين عرض Calendar View
frappe.views.calendar["Booking"] = frappe.views.calendar.extend({
	get_events_method: "frappe.desk.calendar.get_events",
	options: {
		header: {
			left: 'prev,next today',
			center: 'title',
			right: 'month,agendaWeek,agendaDay'
		},
		editable: true,
		selectable: true,
		selectHelper: true,
		forceEventDuration: true,
		displayEventTime: true,
		eventLimit: true,
		eventLimitText: "المزيد",
		locale: 'ar',
		isRTL: true,
		timeFormat: 'H:mm',
		slotLabelFormat: 'H:mm',
		eventRender: function(event, element) {
			// تحسين عرض الأحداث
			element.find('.fc-title').prepend('<i class="fa fa-camera"></i> ');
			if (event.start_time && event.end_time) {
				element.find('.fc-title').append('<br><small>' + event.start_time + ' - ' + event.end_time + '</small>');
			}
			
			// ألوان مختلفة حسب نوع الحجز
			if (event.booking_type === 'Package') {
				element.css('background-color', '#9C27B0');
			} else {
				element.css('background-color', '#4CAF50');
			}
		}
	}
});