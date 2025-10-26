// Copyright (c) 2023, MASAR TEAM and contributors
// For license information, please see license.txt

frappe.ui.form.on('Booking', {
	refresh: function(frm) {
		// Set default booking type if not set
		if (!frm.doc.booking_type) {
			frm.set_value('booking_type', 'Service');
		}
		
		// تعيين الموظف الحالي تلقائياً للمستندات الجديدة
		if (frm.is_new() && !frm.doc.current_employee) {
			frm.set_value('current_employee', frappe.session.user);
		}
		
		// عرض إعدادات الاستديو من General Settings
		load_studio_settings(frm);
		
		// Filter services and packages based on booking type
		setup_filters(frm);
		
		// ملاحظة مهمة:
		// لتجنب ظهور "Not Saved" فور فتح مستند محفوظ، لا نقوم بتعديل الحقول
		// في حدث refresh للمستندات غير الجديدة. سنكتفي بالحسابات أثناء التعديل الفعلي فقط.

		const is_new_or_unsaved = frm.is_new() || frm.doc.__unsaved;

		// حساب الساعات والمجاميع فقط إذا كان المستند جديداً أو غير محفوظ
		if (is_new_or_unsaved) {
			if (frm.doc.booking_type === 'Service' && frm.doc.start_time && frm.doc.end_time) {
				calculate_service_hours(frm);
			}

			if (frm.doc.booking_type === 'Service' && frm.doc.selected_services_table) {
				calculate_service_totals(frm);
			}

			if (frm.doc.booking_type === 'Package') {
				calculate_total_used_hours(frm);
			}
		}
	},
	
	booking_type: function(frm) {
		// Clear related fields when booking type changes
		if (frm.doc.booking_type === 'Service') {
			frm.set_value('package', '');
			frm.set_value('package_name', '');
			frm.clear_table('package_services_table');
		} else if (frm.doc.booking_type === 'Package') {
			frm.set_value('service', '');
			frm.set_value('service_name', '');
			frm.set_value('category', '');
			frm.set_value('duration', '');
		}
		
		// Setup filters
		setup_filters(frm);
		frm.refresh();
		// تحديث العربون بناءً على النوع الحالي
		update_deposit_ui(frm);
	},
	
	package: function(frm) {
		// Populate package services when package is selected
		if (frm.doc.package && frm.doc.booking_type === 'Package') {
			frappe.db.get_value('Package', frm.doc.package, 'total_hours')
				.then(r => {
					if (r && r.message) {
						let total_hours = flt(r.message.total_hours);
						frm.set_value('remaining_hours', total_hours);
						frm.set_value('used_hours', 0);

						// Clear existing dates and recalculate
						frm.clear_table('package_booking_dates');
						frm.refresh_field('package_booking_dates');
						calculate_total_used_hours(frm);
					}
				});
			reload_package_services_with_photographer_discount(frm);
		} else if (!frm.doc.package && frm.doc.booking_type === 'Package') {
			// إذا تم إلغاء اختيار الباقة، إعادة تعيين الحقول
			frm.set_value('used_hours', 0);
			frm.set_value('remaining_hours', 0);
			frm.clear_table('package_booking_dates');
			frm.refresh_field('package_booking_dates');
			hide_package_hours_alert(frm);
		}
	},
	
	photographer: function(frm) {
		// إعادة حساب الأسعار عند اختيار المصور
		apply_photographer_discount(frm);
		
		// إذا كان نوع الحجز Package وتم اختيار باقة، إعادة تحميل الخدمات
		if (frm.doc.booking_type === 'Package' && frm.doc.package) {
			reload_package_services_with_photographer_discount(frm);
		}
	},
	
	photographer_b2b: function(frm) {
		// إعادة حساب الأسعار عند تفعيل/إلغاء B2B
		apply_photographer_discount(frm);
		
		// إذا كان نوع الحجز Package وتم اختيار باقة، إعادة تحميل الخدمات
		if (frm.doc.booking_type === 'Package' && frm.doc.package) {
			reload_package_services_with_photographer_discount(frm);
		}
	},
	
	start_time: function(frm) {
		// حساب الساعات للخدمات
		if (frm.doc.booking_type === 'Service') {
			calculate_service_hours(frm);
			// تحديث كميات الخدمات المختارة
			update_services_quantity_from_hours(frm);
		}
	},
	
	end_time: function(frm) {
		// حساب الساعات للخدمات
		if (frm.doc.booking_type === 'Service') {
			calculate_service_hours(frm);
			// تحديث كميات الخدمات المختارة
			update_services_quantity_from_hours(frm);
		}
	}
});

// ================ Booking Service Item - حساب المبلغ الإجمالي تلقائياً ================
frappe.ui.form.on('Booking Service Item', {
	service: function(frm, cdt, cdn) {
		// إعادة حساب المبلغ عند تغيير الخدمة
		calculate_service_item_total(frm, cdt, cdn);
	},
	
	quantity: function(frm, cdt, cdn) {
		// إعادة حساب المبلغ عند تغيير الكمية
		calculate_service_item_total(frm, cdt, cdn);
	},
	
	service_price: function(frm, cdt, cdn) {
		// إعادة حساب المبلغ عند تغيير السعر
		calculate_service_item_total(frm, cdt, cdn);
	},
	
	discounted_price: function(frm, cdt, cdn) {
		// إعادة حساب المبلغ عند تغيير السعر المخصوم
		calculate_service_item_total(frm, cdt, cdn);
	},
	
	selected_services_table_add: function(frm, cdt, cdn) {
		// حساب المبلغ للصف الجديد
		calculate_service_item_total(frm, cdt, cdn);
	}
});

// ================ Package Service Item Events ================
frappe.ui.form.on('Package Service Item', {
	quantity: function(frm, cdt, cdn) {
		// إعادة حساب المبلغ عند تغيير الكمية
		calculate_package_service_item_total(frm, cdt, cdn);
	},
	
	package_price: function(frm, cdt, cdn) {
		// إعادة حساب المبلغ عند تغيير سعر الباقة
		calculate_package_service_item_total(frm, cdt, cdn);
	},
	
	package_services_table_add: function(frm, cdt, cdn) {
		// حساب المبلغ للصف الجديد
		calculate_package_service_item_total(frm, cdt, cdn);
	}
});

function calculate_package_service_item_total(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	
	if (!row) return;
	
	let quantity = flt(row.quantity || 1);
	let package_price = flt(row.package_price || 0);
	
	// حساب المبلغ الإجمالي
	let amount = quantity * package_price;
	frappe.model.set_value(cdt, cdn, 'amount', amount);
	
	// إعادة حساب إجماليات الباقة
	setTimeout(function() {
		calculate_package_totals_ui(frm);
	}, 100);
}

function calculate_service_item_total(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	
	if (!row) return;
	
	let quantity = flt(row.quantity || 1);
	let price = flt(row.discounted_price || 0);
	
	// إذا لم يكن هناك سعر مخصوم، استخدم السعر الأصلي
	if (price === 0) {
		price = flt(row.service_price || 0);
	}
	
	// حساب المبلغ الإجمالي
	let total = quantity * price;
	frappe.model.set_value(cdt, cdn, 'total_amount', total);
	
	// إعادة حساب المجاميع
	setTimeout(function() {
		calculate_service_totals(frm);
	}, 100);
}

// ================ Package Booking Dates - حساب الساعات تلقائياً ================
frappe.ui.form.on('Package Booking Date', {
	start_time: function(frm, cdt, cdn) {
		calculate_hours_for_row(frm, cdt, cdn);
	},
	
	end_time: function(frm, cdt, cdn) {
		calculate_hours_for_row(frm, cdt, cdn);
	},
	
	package_booking_dates_add: function(frm, cdt, cdn) {
		// منع إضافة صف جديد إذا كانت الساعات المتبقية = 0
		setTimeout(() => {
			check_remaining_hours_before_add(frm);
		}, 100);
	},
	
	package_booking_dates_remove: function(frm, cdt, cdn) {
		// إعادة حساب الساعات بعد حذف صف
		setTimeout(() => {
			calculate_total_used_hours(frm);
		}, 100);
	}
});

/**
 * حساب عدد الساعات لصف واحد في جدول تواريخ الحجز
 * يتم استدعاؤها عند تغيير start_time أو end_time
 */
function calculate_hours_for_row(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	
	if (row.start_time && row.end_time) {
		// استخدام التاريخ من الصف (أو التاريخ الحالي إذا لم يكن محدداً)
		let booking_date = row.booking_date || frappe.datetime.nowdate();
		
		// دمج التاريخ مع الوقت لإنشاء DateTime كامل
		let start = frappe.datetime.str_to_obj(booking_date + ' ' + row.start_time);
		let end = frappe.datetime.str_to_obj(booking_date + ' ' + row.end_time);
		
		// إذا كان وقت النهاية أصغر من البداية (عبور منتصف الليل)
		if (end <= start) {
			end.setDate(end.getDate() + 1);
		}
		
		// حساب الفرق بالساعات
		let diff_ms = end - start;
		let hours = diff_ms / (1000 * 60 * 60);
		
		// تعيين القيمة في حقل hours للصف
		frappe.model.set_value(cdt, cdn, 'hours', hours.toFixed(2));
		
		// إعادة حساب إجمالي الساعات المستخدمة والمتبقية
		setTimeout(() => {
			calculate_total_used_hours(frm);
		}, 100);
	}
}

/**
 * حساب إجمالي الساعات المستخدمة والمتبقية
 * يتم جمع جميع الساعات من جدول package_booking_dates
 */
function calculate_total_used_hours(frm) {
	// التأكد من أن نوع الحجز Package
	if (frm.doc.booking_type !== 'Package') {
		return;
	}
	
	// جمع كل الساعات من جدول تواريخ الحجز
	let total_used = 0;
	
	if (frm.doc.package_booking_dates && frm.doc.package_booking_dates.length > 0) {
		frm.doc.package_booking_dates.forEach(function(row) {
			if (row.hours) {
				total_used += parseFloat(row.hours);
			}
		});
	}
	
	// تحديث حقل الساعات المستخدمة
	frm.set_value('used_hours', total_used.toFixed(2));
	
	// حساب الساعات المتبقية من إجمالي ساعات الباقة
	if (frm.doc.package) {
		frappe.db.get_value('Package', frm.doc.package, 'total_hours').then(r => {
			if (r && r.message && r.message.total_hours) {
				let package_total_hours = parseFloat(r.message.total_hours);
				let remaining = package_total_hours - total_used;
				
				// التأكد من أن الساعات المتبقية لا تقل عن صفر
				remaining = Math.max(0, remaining);
				
				// تحديث حقل الساعات المتبقية
				frm.set_value('remaining_hours', remaining.toFixed(2));
				
				// عرض/إخفاء تنبيه استنفاد الساعات حسب الحالة
				if (remaining <= 0 && total_used > 0) {
					show_hours_exhausted_alert();
				} else {
					hide_package_hours_alert(frm);
				}
			}
		});
	}
}

/**
 * التحقق من الساعات المتبقية قبل السماح بإضافة صف جديد
 * إذا كانت الساعات المتبقية = 0، يتم حذف الصف وعرض رسالة تحذير
 */
function check_remaining_hours_before_add(frm) {
	// التحقق من أن نوع الحجز Package وأن الباقة محددة
	if (frm.doc.booking_type !== 'Package' || !frm.doc.package) {
		return true;
	}
	
	// التحقق من الساعات المتبقية
	let remaining_hours = parseFloat(frm.doc.remaining_hours || 0);
	
	if (remaining_hours <= 0) {
		// حذف الصف الأخير المضاف
		if (frm.doc.package_booking_dates && frm.doc.package_booking_dates.length > 0) {
			let last_row = frm.doc.package_booking_dates[frm.doc.package_booking_dates.length - 1];
			frm.get_field("package_booking_dates").grid.grid_rows_by_docname[last_row.name].remove();
		}
		
		// عرض رسالة تحذير بنمط alert-container
		show_hours_exhausted_alert();
		
		return false;
	}
	return true;
}

/**
 * عرض رسالة تنبيه عند استنفاد ساعات الباقة
 * تستخدم نمط frappe.show_alert الذي يظهر من الأسفل
 */
function show_hours_exhausted_alert() {
	let message = __('تم استنفاد جميع ساعات الباقة');
	frappe.show_alert({
		message: message,
		indicator: 'red'
	}, 7);
	// For persistent message
	if(cur_frm.fields_dict.hours_alert_html) {
		show_package_hours_alert(cur_frm, message, 'red');
	}
}

function show_package_hours_alert(frm, message, color) {
    if (frm.fields_dict.hours_alert_html) {
        $(frm.fields_dict.hours_alert_html.wrapper).html(
            `<div class="alert-container-message" style="color: ${color};">
                ${message}
            </div>`
        );
    }
}

function hide_package_hours_alert(frm) {
    if (frm.fields_dict.hours_alert_html) {
        $(frm.fields_dict.hours_alert_html.wrapper).empty();
    }
}

function setup_filters(frm) {
	// Filter services to show only active ones
	frm.set_query('service', function() {
		return {
			filters: {
				'is_active': 1
			}
		};
	});
	
	// Filter packages to show only active ones
	frm.set_query('package', function() {
		return {
			filters: {
				'is_active': 1
			}
		};
	});
	
	// Filter photographers to show only active ones
	frm.set_query('photographer', function() {
		return {
			filters: {
				'is_active': 1
			}
		};
	});
}

// ================ General Settings Integration ================

function load_studio_settings(frm) {
	// جلب إعدادات الاستديو من General Settings
	frappe.call({
		method: 're_studio_booking.re_studio_booking.doctype.booking.booking.get_studio_settings',
		callback: function(r) {
			if (r.message) {
				frm.studio_settings = r.message;
				
				// عرض معلومات أيام العمل في intro
				if (frm.studio_settings.working_days) {
					let days_arabic = {
						'Sunday': 'الأحد',
						'Monday': 'الاثنين',
						'Tuesday': 'الثلاثاء', 
						'Wednesday': 'الأربعاء',
						'Thursday': 'الخميس',
						'Friday': 'الجمعة',
						'Saturday': 'السبت'
					};
					
					let working_days_arabic = frm.studio_settings.working_days.map(day => days_arabic[day]).join('، ');
					let friday_status = frm.studio_settings.is_friday_working ? 'يوم عمل' : 'عطلة رسمية';
					
					frm.set_intro(`
						<div style="background: #e7f3ff; padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid #0693e3;">
							<strong>📅 أيام عمل الاستديو:</strong> ${working_days_arabic}<br>
							<strong>🕐 ساعات العمل:</strong> ${frm.studio_settings.business_hours.opening_time} - ${frm.studio_settings.business_hours.closing_time}<br>
							<strong>🕌 الجمعة:</strong> ${friday_status}<br>
							<small style="color: #6c757d;"><i>حسب إعدادات General Settings</i></small>
						</div>
					`);
				}
			}
		}
	});
}

// ================ تطبيق خصم المصور ================
function apply_photographer_discount(frm) {
	// التحقق من تفعيل B2B واختيار المصور
	if (!frm.doc.photographer || !frm.doc.photographer_b2b) {
		// إعادة تعيين الأسعار للقيم الأصلية
		reset_prices_to_original(frm);
		return;
	}
	
	// جلب بيانات المصور وخدماته
	frappe.call({
		method: 'frappe.client.get',
		args: {
			doctype: 'Photographer',
			name: frm.doc.photographer
		},
		callback: function(r) {
			if (r.message && r.message.b2b) {
				let discount_pct = flt(r.message.discount_percentage || 0);
				let photographer_services = r.message.services || [];
				
				// إنشاء خريطة للخدمات مع أسعارها المخصومة
				let service_prices = {};
				photographer_services.forEach(function(ps) {
					service_prices[ps.service] = {
						base_price: flt(ps.base_price || 0),
						discounted_price: flt(ps.discounted_price || 0)
					};
				});
				
				// تطبيق الخصم على جدول الخدمات المختارة
				if (frm.doc.booking_type === 'Service' && frm.doc.selected_services_table) {
					let services_with_discount = [];
					let services_count = 0;
					
					frm.doc.selected_services_table.forEach(function(row) {
						let service_price = flt(row.service_price || 0);
						
						// التحقق من أن الخدمة موجودة في جدول المصور
						if (service_prices[row.service]) {
							services_count++;
							let photographer_price = service_prices[row.service];
							
							// استخدام السعر المخصوم من المصور إذا كان موجوداً
							if (photographer_price.discounted_price > 0) {
								row.discounted_price = photographer_price.discounted_price;
								row.total_amount = flt(row.quantity || 1) * row.discounted_price;
								services_with_discount.push(row.service_name || row.service);
							}
							// وإلا استخدام نسبة الخصم العامة
							else if (discount_pct > 0 && service_price > 0) {
								row.discounted_price = service_price * (1 - discount_pct / 100);
								row.total_amount = flt(row.quantity || 1) * row.discounted_price;
								services_with_discount.push(row.service_name || row.service);
							}
							// وإلا السعر الأصلي
							else {
								row.discounted_price = service_price;
								row.total_amount = flt(row.quantity || 1) * service_price;
							}
						} else {
							// الخدمة غير موجودة في جدول المصور
							row.discounted_price = service_price;
							row.total_amount = flt(row.quantity || 1) * service_price;
						}
					});
					
					frm.refresh_field('selected_services_table');
					
					// إعادة حساب المجاميع
					calculate_service_totals(frm);
					
					// رسالة توضيحية
					if (services_with_discount.length > 0) {
						frappe.show_alert({
							message: __(`✅ تم تطبيق خصم المصور على ${services_with_discount.length} من ${services_count} خدمة`),
							indicator: 'green'
						}, 5);
					} else if (services_count > 0) {
						frappe.show_alert({
							message: __(`ℹ️ ${services_count} خدمة من المصور بدون خصم إضافي`),
							indicator: 'blue'
						}, 3);
					} else {
						frappe.show_alert({
							message: __('⚠️ لا توجد خدمات من هذا المصور'),
							indicator: 'orange'
						}, 3);
					}
				}
			}
		}
	});
}

function reset_prices_to_original(frm) {
	// إعادة تعيين الأسعار للقيم الأصلية (بدون خصم)
	if (frm.doc.booking_type === 'Service' && frm.doc.selected_services_table) {
		frm.doc.selected_services_table.forEach(function(row) {
			let service_price = flt(row.service_price || 0);
			row.discounted_price = service_price;
			row.total_amount = flt(row.quantity || 1) * service_price;
		});
		frm.refresh_field('selected_services_table');
		calculate_service_totals(frm);
	}
}

/**
 * إعادة تحميل خدمات الباقة مع تطبيق خصم المصور
 * يتم استدعاؤها عند:
 * 1. اختيار الباقة (وكان المصور محدد مسبقاً)
 * 2. اختيار المصور (وكانت الباقة محددة مسبقاً)
 * 3. تغيير حالة photographer_b2b
 */
function reload_package_services_with_photographer_discount(frm) {
	if (!frm.doc.package) {
		return;
	}
	
	// استدعاء الدالة الخلفية لجلب خدمات الباقة مع خصم المصور
	frappe.call({
		method: 're_studio_booking.re_studio_booking.doctype.booking.booking.get_package_services_with_photographer',
		args: {
			package_name: frm.doc.package,
			photographer: frm.doc.photographer || null,
			photographer_b2b: frm.doc.photographer_b2b || 0
		},
		callback: function(r) {
			if (r.message && r.message.services) {
				// Clear existing table
				frm.clear_table('package_services_table');
				
				// Set package total hours to remaining_hours (initially all hours are available)
				if (r.message.total_hours) {
					// تعيين إجمالي ساعات الباقة في حقل الساعات المتبقية
					frm.set_value('remaining_hours', r.message.total_hours);
					// إعادة تعيين الساعات المستخدمة إلى صفر
					frm.set_value('used_hours', 0);
				}
				
				// Add services to table
				r.message.services.forEach(function(service) {
					let row = frm.add_child('package_services_table');
					row.service = service.service;
					row.service_name = service.service_name;
					row.quantity = service.quantity;
					row.base_price = service.base_price;
					row.package_price = service.package_price;  // السعر النهائي بعد خصم المصور
					row.amount = service.amount;  // المبلغ الإجمالي
					row['أجباري'] = service.is_mandatory || 0;
				});
				
				// Refresh table
				frm.refresh_field('package_services_table');
				
				// إعادة حساب الساعات المستخدمة والمتبقية
				setTimeout(() => {
					calculate_total_used_hours(frm);
					// تحديث مجاميع الباقة والعربون
					calculate_package_totals_ui(frm);
				}, 100);
				
				// Success message
				let message = 'تم تحميل خدمات الباقة بنجاح';
				if (frm.doc.photographer && frm.doc.photographer_b2b) {
					message = '✅ تم تطبيق خصم المصور على خدمات الباقة';
				}
				frappe.show_alert({
					message: __(message),
					indicator: 'green'
				}, 3);
			}
		},
		error: function(r) {
			frappe.msgprint({
				title: __('خطأ'),
				indicator: 'red',
				message: __('لم يتم العثور على خدمات الباقة')
			});
		}
	});
}

function calculate_service_totals(frm) {
	// حساب المبلغ الأساسي والإجمالي للخدمات
	let base_total = 0;
	let final_total = 0;
	
	if (frm.doc.selected_services_table) {
		frm.doc.selected_services_table.forEach(function(row) {
			base_total += flt(row.service_price || 0) * flt(row.quantity || 1);
			final_total += flt(row.total_amount || 0);
		});
	}
	
	frm.set_value('base_amount', base_total);
	frm.set_value('total_amount', final_total);
	
	// تحديث العربون تلقائياً بعد تحديث المجاميع
	update_deposit_ui(frm);
}

function calculate_package_totals_ui(frm) {
	// حساب المجاميع للباقة من جدول الخدمات
	let base_total = 0;
	let final_total = 0;
	(frm.doc.package_services_table || []).forEach(function(row) {
		const qty = flt(row.quantity || 1);
		const base_price = flt(row.base_price || 0);
		const package_price = flt(row.package_price || 0);
		const amount = flt(row.amount || 0);
		
		base_total += base_price * qty;
		// استخدام amount إذا كان موجوداً، وإلا احسب من package_price × quantity
		final_total += amount > 0 ? amount : (package_price * qty);
	});
	frm.set_value('base_amount_package', base_total);
	frm.set_value('total_amount_package', final_total);
	
	update_deposit_ui(frm);
}

function update_deposit_ui(frm) {
	// تحديث قيمة العربون بشكل فوري في الواجهة
	let basis = 0;
	if (frm.doc.booking_type === 'Service') {
		basis = flt(frm.doc.total_amount || 0);
	} else {
		basis = flt(frm.doc.total_amount_package || 0);
	}
	
	if (basis <= 0) {
		frm.set_value('deposit_amount', 0);
		return;
	}
	
	// إن كان المستند محفوظاً بالفعل، لا نقوم بتعديل الحقول هنا حتى لا يظهر "Not Saved"
	// سيتم احتساب العربون وحفظه ضمن تدفق validate/save في السيرفر.
	if (frm.doc.name && !frm.doc.__islocal) {
		return;
	}
	
	// مستند جديد غير محفوظ: استخدم إعدادات التسعير لحساب العربون محلياً
	frappe.call({
		method: 're_studio_booking.re_studio_booking.doctype.general_settings.general_settings.get_pricing_settings',
		callback: function(res) {
			const s = res.message || {};
			const pct = flt(s.deposit_percentage || 30);
			const min_amt = flt(s.minimum_booking_amount || 0);
			let deposit = ((basis * pct) / 100);
			deposit = Number(deposit.toFixed(2));
			if (min_amt > 0 && deposit < min_amt && basis > 0) {
				deposit = Math.min(min_amt, basis);
			}
			frm.set_value('deposit_amount', deposit);
		}
	});
}

function calculate_service_hours(frm) {
	// حساب عدد الساعات من start_time و end_time للخدمات
	if (!frm.doc.start_time || !frm.doc.end_time) {
		return;
	}
	
	try {
		// تحويل الأوقات إلى كائنات Date
		let start_time_str = frm.doc.start_time;
		let end_time_str = frm.doc.end_time;
		
		// إنشاء كائنات Date باستخدام تاريخ عشوائي
		let base_date = '2000-01-01';
		let start = new Date(`${base_date} ${start_time_str}`);
		let end = new Date(`${base_date} ${end_time_str}`);
		
		// إذا كان وقت النهاية أصغر من البداية (عبور منتصف الليل)
		if (end <= start) {
			end.setDate(end.getDate() + 1);
		}
		
		// حساب الفرق بالساعات
		let diff_ms = end - start;
		let hours = diff_ms / (1000 * 60 * 60);
		
		// تحديث الحقل
		frm.set_value('total_booked_hours', hours.toFixed(2));
		
		// رسالة توضيحية
		console.log(`✅ حساب الساعات: ${start_time_str} → ${end_time_str} = ${hours.toFixed(2)} ساعة`);
	} catch (e) {
		console.error('خطأ في حساب الساعات:', e);
	}
}

function update_services_quantity_from_hours(frm) {
	// تحديث كميات الخدمات المختارة من إجمالي الساعات المحجوزة
	if (!frm.doc.total_booked_hours || !frm.doc.selected_services_table) {
		return;
	}
	
	let total_hours = flt(frm.doc.total_booked_hours);
	
	if (total_hours <= 0) {
		return;
	}
	
	// المرور على كل الخدمات المختارة
	frm.doc.selected_services_table.forEach(function(row) {
		// التحقق من أن الخدمة ليست مرنة
		frappe.db.get_value('Service', row.service, 'is_flexible_service', function(r) {
			if (r && !r.is_flexible_service) {
				// تحديث الكمية = إجمالي الساعات
				frappe.model.set_value(row.doctype, row.name, 'quantity', total_hours);
				console.log(`📊 تحديث كمية الخدمة ${row.service}: ${total_hours} ساعة`);
			} else if (r && r.is_flexible_service) {
				console.log(`⚙️ الخدمة ${row.service} مرنة - لا يتم تحديث الكمية`);
			}
		});
	});
	
	// إعادة حساب المجاميع بعد تحديث الكميات
	setTimeout(function() {
		calculate_service_totals(frm);
	}, 500);
}

// تحسين عرض Calendar View
frappe.views.calendar["Booking"] = frappe.views.calendar.extend({
	get_events_method: "frappe.desk.calendar.get_events",
	options: {
		header: {
			left: 'prev,next today',
			center: 'title',
			right: 'month,agendaWeek,agendaDay'
		},
		editable: true,
		selectable: true,
		selectHelper: true,
		forceEventDuration: true,
		displayEventTime: true,
		eventLimit: true,
		eventLimitText: "المزيد",
		locale: 'ar',
		isRTL: true,
		timeFormat: 'H:mm',
		slotLabelFormat: 'H:mm',
		eventRender: function(event, element) {
			// تحسين عرض الأحداث
			element.find('.fc-title').prepend('<i class="fa fa-camera"></i> ');
			if (event.start_time && event.end_time) {
				element.find('.fc-title').append('<br><small>' + event.start_time + ' - ' + event.end_time + '</small>');
			}
			
			// ألوان مختلفة حسب نوع الحجز
			if (event.booking_type === 'Package') {
				element.css('background-color', '#9C27B0');
			} else {
				element.css('background-color', '#4CAF50');
			}
		}
	}
});