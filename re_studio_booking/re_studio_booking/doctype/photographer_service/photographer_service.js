// Copyright (c) 2023, MASAR TEAM and contributors
// For license information, please see license.txt

frappe.ui.form.on('Photographer Service', {
	service: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.service) {
			// Get service details and set base price
			frappe.call({
				method: 're_studio_booking.re_studio_booking.doctype.photographer_service.photographer_service.get_service_details',
				args: {
					service: row.service
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, 'service_name', r.message.service_name);
						frappe.model.set_value(cdt, cdn, 'base_price', r.message.base_price);
						// Calculate discounted price
						calculate_discounted_price(frm, cdt, cdn);
					}
				}
			});
		}
	},
	
	base_price: function(frm, cdt, cdn) {
		// Recalculate discounted price when base price changes
		calculate_discounted_price(frm, cdt, cdn);
	}
});

function calculate_discounted_price(frm, cdt, cdn) {
	var row = locals[cdt][cdn];
	if (row.base_price && frm.doc.name) {
		frappe.call({
			method: 're_studio_booking.re_studio_booking.doctype.photographer_service.photographer_service.calculate_discount',
			args: {
				base_price: row.base_price,
				photographer_name: frm.doc.name
			},
			callback: function(r) {
				if (r.message !== undefined) {
					frappe.model.set_value(cdt, cdn, 'discounted_price', r.message);
				}
			}
		});
	}
}

// Recalculate all discounted prices when photographer B2B or discount percentage changes
frappe.ui.form.on('Photographer', {
	b2b: function(frm) {
		recalculate_all_discounts(frm);
	},
	
	discount_percentage: function(frm) {
		recalculate_all_discounts(frm);
	}
});

function recalculate_all_discounts(frm) {
	if (frm.doc.services) {
		frm.doc.services.forEach(function(row) {
			if (row.base_price) {
				calculate_discounted_price(frm, row.doctype, row.name);
			}
		});
	}
}