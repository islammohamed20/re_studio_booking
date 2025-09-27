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
				method: 'frappe.client.get_list',
				args: {
					doctype: 'Package Service',
					filters: {'parent': frm.doc.package},
					fields: ['service', 'service_name', 'quantity', 'service_price', 'amount']
				},
				callback: function(r) {
					if (r.message) {
						// Clear existing table
						frm.clear_table('package_services_table');
						
						// Add services to table
						r.message.forEach(function(service) {
							let row = frm.add_child('package_services_table');
							row.service = service.service;
							row.service_name = service.service_name;
							row.quantity = service.quantity;
							row.service_price = service.service_price;
							row.amount = service.amount;
						});
						
						// Refresh table
						frm.refresh_field('package_services_table');
					}
				}
			});
		}
	}
});

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