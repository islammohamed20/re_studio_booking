// Copyright (c) 2025, MASAR TEAM and contributors
// For license information, please see license.txt

frappe.ui.form.on('Booking Service Item', {
	service: function(frm, cdt, cdn) {
		// حدث On Select للخدمة في الجدول الفرعي
		var row = locals[cdt][cdn];
		
		if (row.service) {
			// جلب تفاصيل الخدمة مباشرة من القائمة المنسدلة
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Service',
					name: row.service
				},
				callback: function(r) {
					if (r.message) {
						var service = r.message;
						
						// تحديث الأعمدة الأخرى تلقائياً
						frappe.model.set_value(cdt, cdn, 'service_name', service.service_name || service.name);
						frappe.model.set_value(cdt, cdn, 'service_description', service.description || '');
						frappe.model.set_value(cdt, cdn, 'service_price', service.price || 0);
						
						// حساب السعر المخفض والمجموع
						calculate_row_totals(frm, cdt, cdn);
						
						// تحديث الجدول
						frm.refresh_field('selected_services_table');
						
						// رسالة تأكيد
						frappe.show_alert({
							message: __('تم تحديث تفاصيل الخدمة: {0}', [service.service_name || service.name]),
							indicator: 'green'
						}, 2);
					}
				}
			});
		} else {
			// مسح جميع الحقول عند عدم اختيار خدمة
			clear_row_data(cdt, cdn);
			frm.refresh_field('selected_services_table');
		}
	},
	
	// أحداث إضافية للحقول الأخرى
	service_price: function(frm, cdt, cdn) {
		calculate_row_totals(frm, cdt, cdn);
	},
	
	quantity: function(frm, cdt, cdn) {
		update_total_amount(frm, cdt, cdn);
	},
	
	discounted_price: function(frm, cdt, cdn) {
		update_total_amount(frm, cdt, cdn);
	}
});

// دالة مساعدة لحساب مجاميع الصف
function calculate_row_totals(frm, cdt, cdn) {
	update_discounted_price(frm, cdt, cdn);
}

// دالة مساعدة لمسح بيانات الصف
function clear_row_data(cdt, cdn) {
	frappe.model.set_value(cdt, cdn, 'service_name', '');
	frappe.model.set_value(cdt, cdn, 'service_description', '');
	frappe.model.set_value(cdt, cdn, 'service_price', 0);
	frappe.model.set_value(cdt, cdn, 'discounted_price', 0);
	frappe.model.set_value(cdt, cdn, 'total_amount', 0);
}

function update_discounted_price(frm, cdt, cdn) {
	var row = locals[cdt][cdn];
	
	// Always set fallback first
	if (!row.discounted_price && row.service_price) {
		row.discounted_price = row.service_price;
	}
	
	if (!row.service_price || !frm.doc.client) {
		row.discounted_price = row.service_price || 0;
		frm.refresh_field('selected_services_table');
		update_total_amount(frm, cdt, cdn);
		return;
	}
	
	// Use server method for accurate calculation
	frappe.call({
		method: 're_studio_booking.re_studio_booking.doctype.booking.booking.calculate_service_discounted_price',
		args: {
			client: frm.doc.client,
			service_price: row.service_price
		},
		callback: function(r) {
			if (r.message !== undefined) {
				row.discounted_price = r.message;
				console.log('Server calculated discounted price:', r.message);
			} else {
				row.discounted_price = row.service_price;
			}
			frm.refresh_field('selected_services_table');
			update_total_amount(frm, cdt, cdn);
		},
		error: function() {
			row.discounted_price = row.service_price;
			frm.refresh_field('selected_services_table');
			update_total_amount(frm, cdt, cdn);
		}
	});
}

function update_total_amount(frm, cdt, cdn) {
	var row = locals[cdt][cdn];
	var price_to_use = parseFloat(row.discounted_price) || parseFloat(row.service_price) || 0;
	var quantity = parseFloat(row.quantity) || 1;
	
	row.total_amount = price_to_use * quantity;
	frm.refresh_field('selected_services_table');
	
	console.log('Total calculated:', price_to_use, 'x', quantity, '=', row.total_amount);
}
