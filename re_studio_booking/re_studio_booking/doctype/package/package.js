// Copyright (c) 2025, Re Studio and contributors
// For license information, please see license.txt

frappe.ui.form.on('Package', {
	refresh: function(frm) {
		// Add custom buttons and setup form
		setup_package_form(frm);
		show_remaining_hours_message(frm);
		update_booking_restrictions(frm);
	},

	total_hours: function(frm) {
		// Recalculate remaining hours when total hours change
		calculate_remaining_hours(frm);
	},

	used_hours: function(frm) {
		// Recalculate remaining hours when used hours change
		calculate_remaining_hours(frm);
	},

	discount_percentage: function(frm) {
		// Recalculate final price when discount changes
		calculate_final_price(frm);
	},

	total_price: function(frm) {
		// Recalculate final price when total price changes
		calculate_final_price(frm);
	}
});

// Package Services table events
frappe.ui.form.on('Package Service Item', {
	service: function(frm, cdt, cdn) {
		// Fetch service details when service is selected
		let row = locals[cdt][cdn];
		if (row.service) {
			frappe.call({
				method: 're_studio_booking.re_studio_booking.doctype.package.package.get_service_details',
				args: {
					service: row.service
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, 'service_name', r.message.service_name);
						frappe.model.set_value(cdt, cdn, 'base_price', r.message.base_price);
						frappe.model.set_value(cdt, cdn, 'package_price', r.message.package_price);
					}
				}
			});
		}
	},

	package_price: function(frm, cdt, cdn) {
		// Calculate total amount when package price changes
		calculate_service_total(frm, cdt, cdn);
		calculate_package_total_price(frm);
	},

	quantity: function(frm, cdt, cdn) {
		// Calculate total amount when quantity changes
		calculate_service_total(frm, cdt, cdn);
		calculate_package_total_price(frm);
	},

	package_services_remove: function(frm) {
		// Recalculate total when service is removed
		calculate_package_total_price(frm);
	}
});

// Package Booking Date table events
frappe.ui.form.on('Package Booking Date', {
	start_time: function(frm, cdt, cdn) {
		// Calculate hours when start time changes
		calculate_booking_hours(frm, cdt, cdn);
	},

	end_time: function(frm, cdt, cdn) {
		// Calculate hours when end time changes
		calculate_booking_hours(frm, cdt, cdn);
	},

	booking_date: function(frm, cdt, cdn) {
		// Validate date when booking date changes
		validate_booking_date(frm, cdt, cdn);
	},

	booking_dates_add: function(frm, cdt, cdn) {
		// Check if more bookings can be added
		if (!can_add_more_bookings(frm)) {
			frappe.msgprint('تم استخدام جميع ساعات الباقة. لا يمكن إضافة حجوزات جديدة.');
			// Remove the newly added row
			frm.get_field('booking_dates').grid.grid_rows.pop();
			frm.refresh_field('booking_dates');
		}
	},

	booking_dates_remove: function(frm) {
		// Recalculate used hours when booking is removed
		calculate_total_used_hours(frm);
	}
});

// Helper functions
function setup_package_form(frm) {
	// Add custom buttons
	if (!frm.is_new()) {
		frm.add_custom_button(__('عرض الحجوزات'), function() {
			// Show related bookings
			frappe.route_options = {
				'package': frm.doc.name
			};
			frappe.set_route('List', 'Booking');
		});

		frm.add_custom_button(__('إنشاء حجز جديد'), function() {
			// Create new booking with this package
			frappe.new_doc('Booking', {
				'package': frm.doc.name
			});
		});
	}

	// Setup calendar view for booking dates
	setup_calendar_view(frm);
}

function show_remaining_hours_message(frm) {
	if (frm.doc.total_hours && frm.doc.used_hours !== undefined) {
		let remaining = frm.doc.total_hours - frm.doc.used_hours;
		let message = '';
		let indicator = 'green';

		if (remaining > 0) {
			message = `متبقي ${remaining.toFixed(1)} ساعة للحجز`;
			if (remaining < frm.doc.total_hours * 0.2) {
				indicator = 'orange';
			}
		} else {
			message = 'تم استخدام جميع ساعات الباقة';
			indicator = 'red';
		}

		frm.dashboard.add_indicator(message, indicator);
	}
}

function update_booking_restrictions(frm) {
	if (frm.doc.total_hours && frm.doc.used_hours !== undefined) {
		let remaining = frm.doc.total_hours - frm.doc.used_hours;
		if (remaining <= 0) {
			// Disable adding new booking dates
			frm.get_field('booking_dates').grid.cannot_add_rows = true;
			frm.refresh_field('booking_dates');
		}
	}
}

function calculate_remaining_hours(frm) {
	if (frm.doc.total_hours && frm.doc.used_hours !== undefined) {
		let remaining = frm.doc.total_hours - frm.doc.used_hours;
		frm.set_value('remaining_hours', remaining);
	}
}

function calculate_final_price(frm) {
	if (frm.doc.total_price && frm.doc.discount_percentage !== undefined) {
		let discount_amount = frm.doc.total_price * frm.doc.discount_percentage / 100;
		let final_price = frm.doc.total_price - discount_amount;
		frm.set_value('final_price', final_price);
	}
}

function calculate_service_total(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	if (row.package_price && row.quantity) {
		let total = row.package_price * row.quantity;
		frappe.model.set_value(cdt, cdn, 'total_amount', total);
	}
}

function calculate_package_total_price(frm) {
	let total = 0;
	frm.doc.package_services.forEach(function(service) {
		if (service.total_amount) {
			total += service.total_amount;
		}
	});
	frm.set_value('total_price', total);
}

function calculate_booking_hours(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	if (row.start_time && row.end_time && row.booking_date) {
		// Calculate hours between start and end time
		let start_datetime = new Date(`${row.booking_date} ${row.start_time}`);
		let end_datetime = new Date(`${row.booking_date} ${row.end_time}`);
		
		if (end_datetime > start_datetime) {
			let hours_diff = (end_datetime - start_datetime) / (1000 * 60 * 60);
			frappe.model.set_value(cdt, cdn, 'hours', hours_diff.toFixed(2));
			
			// Check minimum booking hours
			if (frm.doc.minimum_booking_hours && hours_diff < frm.doc.minimum_booking_hours) {
				frappe.msgprint(`الحد الأدنى للحجز هو ${frm.doc.minimum_booking_hours} ساعة`);
			}
			
			// Recalculate total used hours
			calculate_total_used_hours(frm);
		} else {
			frappe.msgprint('وقت النهاية يجب أن يكون بعد وقت البداية');
		}
	}
}

function calculate_total_used_hours(frm) {
	let total_used = 0;
	frm.doc.booking_dates.forEach(function(booking) {
		if (booking.hours) {
			total_used += parseFloat(booking.hours);
		}
	});
	frm.set_value('used_hours', total_used);
}

function validate_booking_date(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	if (row.booking_date) {
		let booking_date = new Date(row.booking_date);
		let today = new Date();
		today.setHours(0, 0, 0, 0);
		
		if (booking_date < today) {
			frappe.msgprint('لا يمكن حجز تاريخ في الماضي');
			frappe.model.set_value(cdt, cdn, 'booking_date', '');
		}
	}
}

function can_add_more_bookings(frm) {
	if (frm.doc.total_hours && frm.doc.used_hours !== undefined) {
		let remaining = frm.doc.total_hours - frm.doc.used_hours;
		return remaining > 0;
	}
	return true;
}

function setup_calendar_view(frm) {
	// Add calendar view button for booking dates
	if (!frm.is_new() && frm.doc.booking_dates && frm.doc.booking_dates.length > 0) {
		frm.add_custom_button(__('عرض التقويم'), function() {
			show_calendar_dialog(frm);
		}, __('عرض'));
	}
}

function show_calendar_dialog(frm) {
	// Create calendar dialog
	let dialog = new frappe.ui.Dialog({
		title: 'تقويم الحجوزات - ' + frm.doc.package_name,
		fields: [
			{
				fieldtype: 'HTML',
				fieldname: 'calendar_html'
			}
		],
		size: 'large'
	});

	// Generate calendar HTML
	let calendar_html = generate_calendar_html(frm.doc.booking_dates);
	dialog.fields_dict.calendar_html.$wrapper.html(calendar_html);

	dialog.show();
}

function generate_calendar_html(booking_dates) {
	// Simple calendar HTML generation
	let html = '<div class="calendar-container">';
	html += '<h4>الحجوزات المجدولة</h4>';
	html += '<div class="booking-list">';

	booking_dates.forEach(function(booking) {
		if (booking.booking_date) {
			html += `<div class="booking-item">`;
			html += `<strong>${booking.booking_date}</strong> - `;
			html += `${booking.start_time || ''} إلى ${booking.end_time || ''}`;
			html += ` (${booking.hours || 0} ساعة)`;
			html += `</div>`;
		}
	});

	html += '</div></div>';

	// Add some basic styling
	html += `
	<style>
	.calendar-container {
		padding: 20px;
	}
	.booking-item {
		padding: 10px;
		margin: 5px 0;
		border: 1px solid #ddd;
		border-radius: 5px;
		background-color: #f9f9f9;
	}
	</style>
	`;

	return html;
}