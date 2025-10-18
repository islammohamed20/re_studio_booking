// Copyright (c) 2025, MASAR TEAM and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cost Center', {
	refresh: function(frm) {
		// Add status indicator
		if (frm.doc.is_active) {
			frm.set_indicator('نشط', 'green');
		} else {
			frm.set_indicator('غير نشط', 'red');
		}
		
		// Add custom buttons
		if (!frm.doc.__islocal && frm.doc.is_active) {
			// Open Shift button
			frm.add_custom_button(__('فتح وردية'), function() {
				open_shift_dialog(frm);
			}, __('العمليات'));
			
			// View Shifts button
			frm.add_custom_button(__('عرض الورديات'), function() {
				frappe.set_route('List', 'Shift', {cost_center: frm.doc.name});
			}, __('العمليات'));
			
			// View Transactions button
			frm.add_custom_button(__('عرض المعاملات'), function() {
				frappe.set_route('query-report', 'Cost Center Ledger', {cost_center: frm.doc.name});
			}, __('التقارير'));
		}
	},
	
	is_active: function(frm) {
		// Update indicator when active status changes
		if (frm.doc.is_active) {
			frm.set_indicator('نشط', 'green');
		} else {
			frm.set_indicator('غير نشط', 'red');
			frappe.show_alert({
				message: __('تعطيل الخزنة سيمنع فتح ورديات جديدة'),
				indicator: 'orange'
			}, 5);
		}
	}
});

function open_shift_dialog(frm) {
	let d = new frappe.ui.Dialog({
		title: __('فتح وردية جديدة'),
		fields: [
			{
				label: __('الخزنة'),
				fieldname: 'cost_center',
				fieldtype: 'Link',
				options: 'Cost Center',
				default: frm.doc.name,
				read_only: 1
			},
			{
				fieldtype: 'Column Break'
			},
			{
				label: __('العملة'),
				fieldname: 'currency',
				fieldtype: 'Link',
				options: 'Currency',
				default: frm.doc.currency,
				read_only: 1
			},
			{
				fieldtype: 'Section Break'
			},
			{
				label: __('الرصيد الافتتاحي المتوقع'),
				fieldname: 'expected_opening_balance',
				fieldtype: 'Currency',
				default: frm.doc.current_balance || 0
			},
			{
				fieldtype: 'Section Break'
			},
			{
				label: __('ملاحظات'),
				fieldname: 'notes',
				fieldtype: 'Small Text'
			}
		],
		primary_action_label: __('فتح الوردية'),
		primary_action(values) {
			frappe.call({
				method: 're_studio_booking.re_studio_booking.api.cost_centers.open_shift',
				args: {
					cost_center_name: values.cost_center,
					expected_opening_balance: values.expected_opening_balance
				},
				callback: function(r) {
					if (r.message) {
						frappe.show_alert({
							message: __('تم فتح الوردية بنجاح'),
							indicator: 'green'
						}, 3);
						d.hide();
						frappe.set_route('Form', 'Shift', r.message);
					}
				}
			});
		}
	});
	
	d.show();
}
