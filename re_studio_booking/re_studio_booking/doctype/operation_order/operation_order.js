// Copyright (c) 2025, Masar Digital Group and contributors
// For license information, please see license.txt

frappe.ui.form.on('Operation Order', {
	refresh: function(frm) {
		// إضافة زر لتحميل بيانات الحجز
		if (frm.doc.booking && !frm.doc.__islocal) {
			frm.add_custom_button(__('تحديث من الحجز'), function() {
				frm.call({
					method: 'load_booking_data',
					doc: frm.doc,
					callback: function(r) {
						frm.refresh_fields();
						frappe.show_alert({
							message: __('تم تحديث البيانات من الحجز'),
							indicator: 'green'
						}, 5);
					}
				});
			});
		}
		
		// تلوين الحالة
		if (frm.doc.status) {
			frm.set_indicator_color(frm.doc.status);
		}
	},
	
	booking: function(frm) {
		// تحميل بيانات الحجز عند الاختيار
		if (frm.doc.booking) {
			frm.call({
				method: 'load_booking_data',
				doc: frm.doc,
				callback: function(r) {
					frm.refresh_fields();
					frappe.show_alert({
						message: __('تم تحميل بيانات الحجز'),
						indicator: 'green'
					}, 3);
				}
			});
		}
	},
	
	status: function(frm) {
		// تلوين الحالة
		frm.set_indicator_color(frm.doc.status);
	}
});

// تحديث حالة صف التنفيذ
frappe.ui.form.on('Operation Order Execution Time', {
	status: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		// تحديث تاريخ التنفيذ عند تغيير الحالة
		update_execution_date(frm);
		
		// تلوين الصف حسب الحالة
		if (row.status === 'مكتمل') {
			frappe.show_alert({
				message: __('تم وضع علامة كمكتمل - سيتم تحديث تاريخ التنفيذ'),
				indicator: 'green'
			}, 3);
		}
	}
});

// دالة لتحديث تاريخ التنفيذ
function update_execution_date(frm) {
	if (!frm.doc.execution_times || frm.doc.execution_times.length === 0) {
		return;
	}
	
	// البحث عن أول تاريخ غير مكتمل
	let next_date = null;
	for (let row of frm.doc.execution_times) {
		if (row.status !== 'مكتمل') {
			next_date = row.booking_date;
			break;
		}
	}
	
	// إذا لم يوجد تاريخ غير مكتمل، استخدم آخر تاريخ
	if (!next_date && frm.doc.execution_times.length > 0) {
		next_date = frm.doc.execution_times[frm.doc.execution_times.length - 1].booking_date;
	}
	
	// تحديث حقل تاريخ التنفيذ
	if (next_date) {
		frm.set_value('execution_date', next_date);
	}
}

// دالة مساعدة لتلوين المؤشر
frappe.ui.form.set_indicator_color = function(status) {
	let color_map = {
		'مسودة': 'gray',
		'معتمد': 'blue',
		'قيد التنفيذ': 'orange',
		'مكتمل': 'green',
		'ملغي': 'red'
	};
	
	return color_map[status] || 'gray';
};
