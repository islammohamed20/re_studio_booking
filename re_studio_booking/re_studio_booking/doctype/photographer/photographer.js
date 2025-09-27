// Copyright (c) 2025, Masar Digital Group and contributors
// For license information, please see license.txt

frappe.ui.form.on("Photographer", {
	refresh(frm) {
		// منع إضافة الأيام تلقائياً في جدول ساعات العمل
		setTimeout(() => {
			if (frm.doc.__islocal && frm.doc.working_hours && frm.doc.working_hours.length > 0) {
				// إذا كان هناك صفوف تلقائية، احذفها
				frm.clear_table("working_hours");
				frm.refresh_field("working_hours");
			}
		}, 500);
	},
	
	after_save(frm) {
		// بعد الحفظ تأكد من عدم وجود صفوف غير مرغوب فيها
		if (frm.doc.working_hours && frm.doc.working_hours.length === 7) {
			let all_empty = frm.doc.working_hours.every(row => 
				!row.start_time && !row.end_time && row.is_working_day === 1
			);
			if (all_empty) {
				frm.clear_table("working_hours");
				frm.save();
			}
		}
	},
	
	setup(frm) {
		// منع إضافة الصفوف تلقائياً
		frm.set_df_property('working_hours', 'cannot_add_rows', false);
		
		// إزالة أي صفوف موجودة عند الإعداد
		if (frm.doc.__islocal) {
			frm.clear_table("working_hours");
		}
	},
	
	onload(frm) {
		// توليد الاسم الكامل من الاسم الأول والأخير
		if (frm.doc.first_name || frm.doc.last_name) {
			frm.set_value('full_name', (frm.doc.first_name || '') + ' ' + (frm.doc.last_name || ''));
		}
		
		// منع إضافة صفوف ساعات العمل تلقائياً عند التحميل
		setTimeout(() => {
			if (frm.doc.__islocal && frm.doc.working_hours) {
				frm.clear_table("working_hours");
				frm.refresh_field("working_hours");
			}
		}, 100);
	},
	
	before_load(frm) {
		// منع التحميل التلقائي لساعات العمل
		if (frm.doc.__islocal) {
			frm.doc.working_hours = [];
		}
	},

	first_name(frm) {
		frm.set_value('full_name', (frm.doc.first_name || '') + ' ' + (frm.doc.last_name || ''));
	},

	last_name(frm) {
		frm.set_value('full_name', (frm.doc.first_name || '') + ' ' + (frm.doc.last_name || ''));
	},
	
	b2b(frm) {
		// عند تغيير حالة B2B، أعد حساب الأسعار المخفضة
		update_discounted_prices(frm);
	},
	
	discount_percentage(frm) {
		// عند تغيير نسبة الخصم، أعد حساب الأسعار المخفضة
		update_discounted_prices(frm);
	}
});

// منع إضافة الأيام تلقائياً في جدول ساعات العمل
frappe.ui.form.on("Photographer Working Hours", {
	working_hours_add(frm, cdt, cdn) {
		// عدم فعل أي شيء تلقائياً عند إضافة صف جديد
		// المستخدم يختار اليوم والوقت بنفسه
	},
	
	before_working_hours_remove(frm, cdt, cdn) {
		return true; // السماح بالحذف
	}
});

// دالة لتحديث الأسعار المخفضة في جدول الخدمات
function update_discounted_prices(frm) {
	if (!frm.doc.services || frm.doc.services.length === 0) {
		return;
	}
	
	// احصل على نسبة الخصم
	let discount_percentage = 0;
	if (frm.doc.b2b && frm.doc.discount_percentage) {
		discount_percentage = parseFloat(frm.doc.discount_percentage) || 0;
	}
	
	// حساب السعر المخفض لكل خدمة
	frm.doc.services.forEach(function(service_row) {
		if (!service_row.service) {
			return;
		}
		
		// احصل على السعر الأساسي
		let base_price = service_row.base_price || 0;
		
		// حساب السعر المخفض
		if (discount_percentage > 0 && base_price > 0) {
			let discounted_price = base_price * (1 - discount_percentage / 100.0);
			service_row.discounted_price = Math.round(discounted_price * 100) / 100; // تقريب لرقمين عشريين
		} else {
			service_row.discounted_price = base_price;
		}
	});
	
	// تحديث الجدول في الواجهة
	frm.refresh_field('services');
}

// تحديث الأسعار عند إضافة خدمة جديدة
frappe.ui.form.on("Photographer Service", {
	service(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.service) {
			// احصل على السعر الأساسي من Service DocType
			frappe.db.get_value('Service', row.service, 'price').then(function(response) {
				if (response.message && response.message.price) {
					row.base_price = response.message.price;
					
					// حساب السعر المخفض
					let discount_percentage = 0;
					if (frm.doc.b2b && frm.doc.discount_percentage) {
						discount_percentage = parseFloat(frm.doc.discount_percentage) || 0;
					}
					
					if (discount_percentage > 0) {
						let discounted_price = response.message.price * (1 - discount_percentage / 100.0);
						row.discounted_price = Math.round(discounted_price * 100) / 100;
					} else {
						row.discounted_price = response.message.price;
					}
					
					frm.refresh_field('services');
				}
			});
		}
	}
});