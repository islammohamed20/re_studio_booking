// Copyright (c) 2025, Masar Digital Group and contributors
// For license information, please see license.txt

frappe.ui.form.on("Photographer Team", {
	refresh(frm) {

	},
});

// تعبئة الـ Check boxes تلقائياً عند اختيار المصور
frappe.ui.form.on('Operation Order Team', {
	employee: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		if (row.employee) {
			// جلب بيانات المصور
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Photographer',
					name: row.employee
				},
				callback: function(r) {
					if (r.message) {
						// تعبئة الـ Check boxes تلقائياً
						frappe.model.set_value(cdt, cdn, 'photographer', r.message.photographer || 0);
						frappe.model.set_value(cdt, cdn, 'videographer', r.message.videographer || 0);
						frappe.model.set_value(cdt, cdn, 'editor', r.message.editor || 0);
						frappe.model.set_value(cdt, cdn, 'montage', r.message.montage || 0);
						
						frm.refresh_field('table_photographer');
					}
				}
			});
		}
	}
});
