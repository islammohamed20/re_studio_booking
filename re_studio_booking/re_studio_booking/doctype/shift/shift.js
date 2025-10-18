// Copyright (c) 2025, MASAR TEAM and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shift', {
	refresh: function(frm) {
		// Set indicator based on status
		set_status_indicator(frm);
		
		// Add custom buttons based on status
		if (!frm.doc.__islocal) {
			if (frm.doc.status === 'Open') {
				// Add Transaction button
				frm.add_custom_button(__('إضافة معاملة'), function() {
					add_transaction_dialog(frm);
				}, __('العمليات'));
				
				// Request Handover button
				frm.add_custom_button(__('طلب تسليم'), function() {
					request_handover_dialog(frm);
				}, __('العمليات'));
				
				// Close Shift button
				frm.add_custom_button(__('إغلاق الوردية'), function() {
					close_shift_dialog(frm);
				}, __('العمليات')).addClass('btn-primary');
			}
			
			// View Handovers button
			if (frm.doc.status === 'Handed Over') {
				frm.add_custom_button(__('عرض التسليمات'), function() {
					frappe.set_route('List', 'Shift Handover', {shift: frm.doc.name});
				});
			}
		}
		
		// Refresh totals section
		frm.trigger('calculate_totals');
	},
	
	status: function(frm) {
		set_status_indicator(frm);
	},
	
	calculate_totals: function(frm) {
		// This is triggered automatically by validate, but can be called manually
		frm.refresh_field('total_payments');
		frm.refresh_field('total_refunds');
		frm.refresh_field('total_expenses');
		frm.refresh_field('theoretical_closing_balance');
		frm.refresh_field('difference');
	}
});

function set_status_indicator(frm) {
	const status_colors = {
		'Open': 'blue',
		'Closed': 'green',
		'Handed Over': 'orange',
		'Cancelled': 'red'
	};
	
	frm.set_indicator(frm.doc.status, status_colors[frm.doc.status] || 'gray');
}

function add_transaction_dialog(frm) {
	let d = new frappe.ui.Dialog({
		title: __('إضافة معاملة جديدة'),
		fields: [
			{
				label: __('نوع المعاملة'),
				fieldname: 'trx_type',
				fieldtype: 'Select',
				options: 'Payment\\nRefund\\nExpense\\nDeposit\\nWithdrawal',
				reqd: 1
			},
			{
				label: __('طريقة الدفع'),
				fieldname: 'payment_method',
				fieldtype: 'Select',
				options: 'Cash\\nWallet\\nBank\\nCard',
				reqd: 1,
				default: 'Cash'
			},
			{
				label: __('المبلغ'),
				fieldname: 'amount',
				fieldtype: 'Currency',
				reqd: 1
			},
			{
				fieldtype: 'Column Break'
			},
			{
				label: __('نوع المرجع'),
				fieldname: 'reference_doctype',
				fieldtype: 'Data'
			},
			{
				label: __('رقم المرجع'),
				fieldname: 'reference_name',
				fieldtype: 'Data'
			},
			{
				label: __('العميل'),
				fieldname: 'party',
				fieldtype: 'Link',
				options: 'Customer'
			},
			{
				fieldtype: 'Section Break'
			},
			{
				label: __('الوصف'),
				fieldname: 'description',
				fieldtype: 'Small Text'
			}
		],
		primary_action_label: __('إضافة'),
		primary_action(values) {
			frappe.call({
				method: 're_studio_booking.re_studio_booking.api.cost_centers.add_shift_transaction',
				args: {
					shift_name: frm.doc.name,
					trx_type: values.trx_type,
					payment_method: values.payment_method,
					amount: values.amount,
					reference_doctype: values.reference_doctype,
					reference_name: values.reference_name,
					party: values.party,
					description: values.description
				},
				callback: function(r) {
					if (r.message) {
						frappe.show_alert({
							message: __('تم إضافة المعاملة بنجاح'),
							indicator: 'green'
						}, 3);
						d.hide();
						frm.reload_doc();
					}
				}
			});
		}
	});
	
	d.show();
}

function close_shift_dialog(frm) {
	let d = new frappe.ui.Dialog({
		title: __('إغلاق الوردية'),
		fields: [
			{
				label: __('الرصيد الختامي النظري'),
				fieldname: 'theoretical_closing',
				fieldtype: 'Currency',
				read_only: 1,
				default: frm.doc.theoretical_closing_balance
			},
			{
				fieldtype: 'Column Break'
			},
			{
				label: __('الرصيد الختامي الفعلي'),
				fieldname: 'actual_closing_balance',
				fieldtype: 'Currency',
				reqd: 1,
				default: frm.doc.theoretical_closing_balance
			},
			{
				fieldtype: 'Section Break'
			},
			{
				label: __('إنشاء قيد محاسبي'),
				fieldname: 'create_journal',
				fieldtype: 'Check',
				default: 1
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
		primary_action_label: __('إغلاق'),
		primary_action(values) {
			frappe.call({
				method: 're_studio_booking.re_studio_booking.api.cost_centers.close_shift',
				args: {
					shift_name: frm.doc.name,
					actual_closing_balance: values.actual_closing_balance,
					create_journal: values.create_journal
				},
				callback: function(r) {
					if (r.message) {
						frappe.show_alert({
							message: __('تم إغلاق الوردية بنجاح'),
							indicator: 'green'
						}, 3);
						
						if (r.message.difference != 0) {
							frappe.msgprint({
								title: __('تنبيه'),
								message: __('يوجد فرق بين الرصيد الفعلي والنظري: ') + r.message.difference,
								indicator: 'orange'
							});
						}
						
						d.hide();
						frm.reload_doc();
					}
				}
			});
		}
	});
	
	d.show();
}

function request_handover_dialog(frm) {
	let d = new frappe.ui.Dialog({
		title: __('طلب تسليم الوردية'),
		fields: [
			{
				label: __('المستلم'),
				fieldname: 'to_user',
				fieldtype: 'Link',
				options: 'User',
				reqd: 1
			},
			{
				fieldtype: 'Column Break'
			},
			{
				label: __('المبلغ المسلم'),
				fieldname: 'handed_amount',
				fieldtype: 'Currency',
				default: frm.doc.theoretical_closing_balance,
				reqd: 1
			},
			{
				fieldtype: 'Section Break'
			},
			{
				label: __('ملاحظات'),
				fieldname: 'notes',
				fieldtype: 'Text'
			}
		],
		primary_action_label: __('طلب التسليم'),
		primary_action(values) {
			frappe.call({
				method: 're_studio_booking.re_studio_booking.api.cost_centers.request_handover',
				args: {
					shift_name: frm.doc.name,
					to_user: values.to_user,
					handed_amount: values.handed_amount,
					notes: values.notes
				},
				callback: function(r) {
					if (r.message) {
						frappe.show_alert({
							message: __('تم إرسال طلب التسليم'),
							indicator: 'green'
						}, 3);
						d.hide();
						frm.reload_doc();
					}
				}
			});
		}
	});
	
	d.show();
}
