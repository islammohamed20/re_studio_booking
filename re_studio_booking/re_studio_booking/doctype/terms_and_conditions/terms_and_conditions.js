// Copyright (c) 2025, Re Studio and contributors
// For license information, please see license.txt

frappe.ui.form.on('Terms and Conditions', {
	refresh: function(frm) {
		// Set default content if empty
		if (frm.is_new() && !frm.doc.terms) {
			frm.set_value('terms', get_default_terms());
		}
		
		// تحذير عند تفعيل default
		if (frm.doc.default && !frm.is_new()) {
			frm.set_df_property('default', 'description', 'سيتم إلغاء تفعيل جميع الشروط الافتراضية الأخرى');
		}
	},
	
	default: function(frm) {
		if (frm.doc.default) {
			frappe.show_alert({
				message: __('سيتم تعيين هذه الشروط كافتراضية لجميع المستندات'),
				indicator: 'blue'
			}, 5);
		}
	}
});

function get_default_terms() {
	return `
		<h3>الشروط والأحكام العامة</h3>
		<ol>
			<li>يجب تأكيد الحجز قبل 24 ساعة على الأقل من موعد الجلسة.</li>
			<li>في حالة الإلغاء قبل 48 ساعة من الموعد، يتم استرداد المبلغ بالكامل.</li>
			<li>الإلغاء قبل 24 ساعة من الموعد يستحق استرداد 50% من المبلغ.</li>
			<li>لا يتم استرداد المبلغ في حالة الإلغاء قبل أقل من 24 ساعة.</li>
			<li>يجب الالتزام بالمواعيد المحددة للحجز.</li>
			<li>العميل مسؤول عن جميع المعدات والأدوات المستخدمة خلال الجلسة.</li>
		</ol>
	`;
}
