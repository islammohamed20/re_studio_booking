// Copyright (c) 2023, MASAR TEAM and contributors
// For license information, please see license.txt

frappe.ui.form.on('Package Service', {
	service: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		
		if (row.service) {
			frappe.call({
				method: 're_studio_booking.re_studio_booking.doctype.package_service.package_service.get_service_details',
				args: {
					service: row.service
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, 'service_name', r.message.service_name);
						frappe.model.set_value(cdt, cdn, 'service_price', r.message.price);
						
						// Calculate amount based on quantity and price
						const quantity = row.quantity || 1;
						frappe.model.set_value(cdt, cdn, 'amount', r.message.price * quantity);
					}
				}
			});
		}
	},
	
	quantity: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		
		// Ensure quantity is at least 1
		if (row.quantity < 1) {
			frappe.model.set_value(cdt, cdn, 'quantity', 1);
			frappe.show_alert({
				message: __("يجب أن تكون الكمية 1 على الأقل"),
				indicator: 'red'
			});
		}
		
		// Update amount based on quantity and service price
		if (row.service_price) {
			frappe.model.set_value(cdt, cdn, 'amount', row.service_price * row.quantity);
		}
	}
});