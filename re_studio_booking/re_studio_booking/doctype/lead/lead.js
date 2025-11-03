// Copyright (c) 2025, Masar Digital Group and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lead', {
	refresh: function(frm) {
		// إضافة أزرار مخصصة
		if (!frm.is_new()) {
			// زر تحويل إلى عميل
			if (frm.doc.status !== 'Converted') {
				frm.add_custom_button(__('تحويل إلى عميل'), function() {
					convert_to_client(frm);
				}, __('الإجراءات'));
			}
			
			// زر إنشاء عرض أسعار
			frm.add_custom_button(__('إنشاء عرض أسعار'), function() {
				frappe.model.open_mapped_doc({
					method: 're_studio_booking.re_studio_booking.doctype.lead.lead.make_quotation',
					frm: frm
				});
			}, __('إنشاء'));
			
			// زر إنشاء حجز
			frm.add_custom_button(__('إنشاء حجز'), function() {
				frappe.model.open_mapped_doc({
					method: 're_studio_booking.re_studio_booking.doctype.lead.lead.make_booking',
					frm: frm
				});
			}, __('إنشاء'));
		}
		
		// تعيين lead_owner تلقائياً
		if (frm.is_new() && !frm.doc.lead_owner) {
			frm.set_value('lead_owner', frappe.session.user);
		}
	}
});

function convert_to_client(frm) {
	frappe.confirm(
		__('هل تريد تحويل هذا العميل المحتمل إلى عميل؟'),
		function() {
			frappe.call({
				method: 're_studio_booking.re_studio_booking.doctype.lead.lead.convert_to_client',
				args: {
					lead_name: frm.doc.name
				},
				freeze: true,
				freeze_message: __('جاري التحويل...'),
				callback: function(r) {
					if (r.message) {
						frappe.show_alert({
							message: __('تم التحويل إلى عميل بنجاح'),
							indicator: 'green'
						}, 5);
						frappe.set_route('Form', 'Client', r.message);
					}
				}
			});
		}
	);
}
