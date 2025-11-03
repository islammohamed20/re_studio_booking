// Copyright (c) 2025, Masar Digital Group and contributors
// For license information, please see license.txt


function refresh_payment_summary(frm) {
	// For new (unsaved) docs, aggregate locally without server round-trip
	if (frm.is_new()) {
		aggregate_local_payments(frm);
		return;
	}
	
	// لتجنب خطأ "Document has been modified"، نستخدم set_value بدون حفظ
	frappe.call({
		method: 're_studio_booking.re_studio_booking.doctype.booking_invoice.booking_invoice.recalc_invoice_payments',
		args: { invoice: frm.doc.name },
		freeze: true,
		freeze_message: __('جاري حساب المدفوعات...'),
		callback: function(r) {
			if (r.message) {
				// تحديث القيم في الذاكرة بدون إطلاق events
				frm.doc.paid_amount = r.message.paid_amount;
				frm.doc.outstanding_amount = r.message.outstanding_amount;
				frm.doc.status = r.message.status;
				frm.refresh_fields(['paid_amount','outstanding_amount','status']);
			}
		}
	});
}

function aggregate_local_payments(frm) {
	let total = 0;
	(frm.doc.payment_table || []).forEach(r => {
		if (r.paid_amount) total += flt(r.paid_amount);
	});
	frm.set_value('paid_amount', total);
	let invoice_total = flt(frm.doc.total_amount) || 0;
	frm.set_value('outstanding_amount', invoice_total - total);
	
	// تحديث الحالة محلياً للفواتير الجديدة
	if (invoice_total > 0) {
		if (total >= invoice_total) {
			frm.set_value('status', 'Paid');
		} else if (total > 0) {
			frm.set_value('status', 'Partially Paid');
		}
	}
	
	frm.refresh_fields(['paid_amount','outstanding_amount','status']);
}

frappe.ui.form.on('Booking Invoice', {
	refresh: function(frm) {
		// تحميل الشروط الافتراضية للمستندات الجديدة
		if (frm.is_new() && !frm.doc.tc_name) {
			frappe.call({
				method: 're_studio_booking.re_studio_booking.doctype.terms_and_conditions.terms_and_conditions.get_default_terms',
				callback: function(r) {
					if (r.message) {
						frm.set_value('tc_name', r.message.name);
						frm.set_value('terms', r.message.terms);
					}
				}
			});
		}
		
		// تحديث تاريخ الاستحقاق التالي
		update_next_due_date(frm);
		
		if (!frm.is_new()) {
			if (!frm.custom_buttons_added) {
				frm.add_custom_button('إضافة دفعة', () => {
					frappe.prompt([
						{fieldname:'amount', fieldtype:'Currency', label:'المبلغ', reqd:1},
						{fieldname:'payment_method', fieldtype:'Link', label:'طريقة الدفع', options:'Payment Method', reqd:1},
						{fieldname:'date', fieldtype:'Date', label:'التاريخ', default: frappe.datetime.get_today(), reqd:1},
						{fieldname:'reference', fieldtype:'Data', label:'المرجع'}
					], values => {
						frappe.call({
							method: 're_studio_booking.re_studio_booking.doctype.booking_invoice.booking_invoice.add_payment',
							args: {
								name: frm.doc.name,
								amount: values.amount,
								payment_method: values.payment_method,
								payment_reference: values.reference,
								payment_date: values.date
							}
						}).then(r => {
							if (r.message) {
								frm.reload_doc();
							}
						});
					});
				}, 'المدفوعات');
				
				frm.add_custom_button('إعادة حساب المدفوعات', () => {
					refresh_payment_summary(frm);
				}, 'المدفوعات');
				
				// زر إنشاء القيد المحاسبي
				if (frm.doc.docstatus == 1 && frm.doc.paid_amount > 0 && !frm.doc.journal_entry) {
					if (frm.doc.cost_center && frm.doc.debit_to && frm.doc.income_account) {
						frm.add_custom_button('إنشاء قيد محاسبي', () => {
							frappe.confirm(
								__('هل تريد إنشاء قيد محاسبي للمبلغ المدفوع ({0} ريال)?', [frm.doc.paid_amount]),
								function() {
									frappe.call({
										method: 're_studio_booking.re_studio_booking.doctype.booking_invoice.booking_invoice.create_journal_entry_for_invoice',
										args: {
											invoice: frm.doc.name
										},
										freeze: true,
										freeze_message: __('جاري إنشاء القيد المحاسبي...'),
										callback: function(r) {
											if (r.message) {
												frappe.show_alert({
													message: __('تم إنشاء القيد المحاسبي: {0}', [r.message]),
													indicator: 'green'
												}, 5);
												frm.reload_doc();
											}
										}
									});
								}
							);
						}, 'المحاسبة');
					}
				}
				
				// زر لعرض القيد المحاسبي المرتبط
				if (frm.doc.journal_entry) {
					frm.add_custom_button('عرض القيد المحاسبي', () => {
						frappe.set_route('Form', 'Journal Entry', frm.doc.journal_entry);
					}, 'المحاسبة');
				}
				
				frm.custom_buttons_added = true;
			}
		}
	},
	
	tc_name: function(frm) {
		// جلب نص الشروط والأحكام عند اختيار قالب
		if (frm.doc.tc_name) {
			console.log('🔍 Fetching terms for template:', frm.doc.tc_name);
			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Terms and Conditions',
					filters: { name: frm.doc.tc_name },
					fieldname: 'terms'
				},
				callback: function(r) {
					console.log('📥 Response:', r);
					if (r && r.message && r.message.terms) {
						console.log('✅ Setting terms:', r.message.terms.substring(0, 100) + '...');
						frm.set_value('terms', r.message.terms);
						frm.refresh_field('terms');
					} else {
						console.log('⚠️ No terms found in response');
					}
				},
				error: function(err) {
					console.error('❌ Error fetching terms:', err);
				}
			});
		} else {
			console.log('🗑️ Clearing terms field');
			frm.set_value('terms', '');
		}
	},
	
	booking_type: function(frm) {
		// إخفاء/إظهار الحقول بناءً على نوع الحجز
		toggle_booking_type_fields(frm);
	},
	booking: function(frm) {
		if (!frm.doc.booking) return;
		frappe.call({
			method: 'frappe.client.get',
			args: { doctype: 'Booking', name: frm.doc.booking },
			callback: function(r) {
				if (!r.message) return;
				const b = r.message;
				// Basic fields
				frm.set_value('booking_type', b.booking_type);
				frm.set_value('package', b.package);
				frm.set_value('package_name', b.package_name);
				frm.set_value('photographer', b.photographer);
				frm.set_value('booking_date', b.booking_date);
				frm.set_value('start_time', b.start_time);
				frm.set_value('end_time', b.end_time);
				frm.set_value('client', b.client);
				frm.set_value('client_name', b.client_name || b.customer_name);
				// Map client_email from Booking to customer_email in Invoice
				frm.set_value('customer_email', b.client_email || b.customer_email);
				// Use phone field consistently
				frm.set_value('phone', b.phone);
				frm.set_value('mobile_no', b.mobile_no);
				
				// نسخ تاريخ إنشاء الحجز
				frm.set_value('booking_creation_date', b.booking_creation_date);

				// Map financials: set total_amount and calculate outstanding
				// Get correct total based on booking type
				let booking_total = 0;
				if (b.booking_type === 'Service') {
					booking_total = b.total_amount || 0;
				} else if (b.booking_type === 'Package') {
					// Package bookings use total_amount_package field
					booking_total = b.total_amount_package || b.total_amount || 0;
				}
				
				if (booking_total > 0) {
					frm.set_value('total_amount', booking_total);
					// لا نضبط paid_amount هنا - سيتم حسابه من payment_table
					// سيتم حساب outstanding_amount بعد ملء payment_table
					frm.refresh_field('total_amount');
				}

				// Force refresh booking_type dependent UI
				frm.refresh_field('booking_type');
				
				// إخفاء/إظهار الحقول بناءً على نوع الحجز
				toggle_booking_type_fields(frm);

				// Explicit toggle (in case depends_on not re-evaluated yet)
				const isService = b.booking_type === 'Service';
				const isPackage = b.booking_type === 'Package';
				frm.toggle_display('service_section', isService);
				frm.toggle_display('selected_services_table', isService);
				frm.toggle_display('package_section', isPackage);
				frm.toggle_display('package_name', isPackage);
				frm.toggle_display('package_services_table', isPackage);

				// Clear existing child tables
				frm.clear_table('selected_services_table');
				frm.clear_table('package_services_table');
				
				// مسح جدول المدفوعات فقط للفواتير الجديدة
				// حتى لا نحذف التعديلات اليدوية عند تعديل الفاتورة
				if (frm.is_new()) {
					frm.clear_table('payment_table');
				}

				// Fetch child tables through a server method to ensure proper structure
				frappe.call({
					method: 're_studio_booking.re_studio_booking.doctype.booking_invoice.booking_invoice.get_booking_child_rows',
					args: { booking: b.name },
				}).then(res => {
					if (res && res.message) {
						const { services, package_services, package_dates } = res.message;
						(services || []).forEach(row => {
							const d = frm.add_child('selected_services_table');
							Object.assign(d, row);
						});
						(package_services || []).forEach(row => {
							const d = frm.add_child('package_services_table');
							Object.assign(d, row);
						});
						frm.refresh_field('selected_services_table');
						frm.refresh_field('package_services_table');
						
						// ملء جدول المدفوعات فقط للفواتير الجديدة
						// للحفاظ على التعديلات اليدوية في الفواتير الموجودة
						if (frm.is_new()) {
							// الصف الأول دائماً: تاريخ إنشاء الحجز + العربون
							if (b.booking_creation_date) {
								const deposit_row = frm.add_child('payment_table');
								deposit_row.date = b.booking_creation_date;
								deposit_row.paid_amount = b.deposit_amount || 0;
								deposit_row.payment_method = b.payment_method || 'Cash';
								deposit_row.transaction_reference_number = b.deposit_amount > 0 ? `عربون حجز ${b.name}` : '';
							}
							
							// الصفوف التالية تعتمد على نوع الحجز
							if (b.booking_type === 'Service') {
								// Service: صف واحد إضافي = تاريخ الحجز (booking_date)
								if (b.booking_date) {
									const service_row = frm.add_child('payment_table');
									service_row.date = b.booking_date;
									service_row.paid_amount = 0; // يُملأ لاحقاً
								}
								
								frappe.show_alert({
									message: `تم إضافة صفين: تاريخ الإنشاء (${b.booking_creation_date}) + تاريخ الحجز (${b.booking_date})`,
									indicator: 'green'
								}, 5);
								
							} else if (b.booking_type === 'Package') {
								// Package: صفوف من جدول package_booking_dates
								if (package_dates && package_dates.length > 0) {
									package_dates.forEach((date_row) => {
										const payment_row = frm.add_child('payment_table');
										payment_row.date = date_row.booking_date;
										payment_row.paid_amount = 0; // يُملأ لاحقاً
									});
									
									frappe.show_alert({
										message: `تم إضافة ${package_dates.length + 1} صف: تاريخ الإنشاء + ${package_dates.length} تاريخ من الباقة`,
										indicator: 'green'
									}, 5);
								}
							}
							
							frm.refresh_field('payment_table');
						}
						
						// إعادة حساب المدفوعات وتحديد تاريخ الاستحقاق التالي
						refresh_payment_summary(frm);
						update_next_due_date(frm);
					}
				}).catch(() => {
					// Fallback if whitelisted method not yet available (cache / deploy delay)
					const fetchChildren = (doctype, target_field, fields) => {
						frappe.call({
							method: 'frappe.client.get_list',
							args: {
								doctype: doctype,
								fields: fields,
								filters: { parent: b.name, parenttype: 'Booking' },
								limit_page_length: 500
							}
						}).then(res2 => {
							(res2.message || []).forEach(row => {
								const d = frm.add_child(target_field);
								Object.assign(d, row);
							});
							frm.refresh_field(target_field);
						});
					};
					// Services table
					fetchChildren('Booking Service Item', 'selected_services_table', [
						'service','service_name','quantity','service_price','discounted_price','total_amount','service_options'
					]);
					// Package services table
					fetchChildren('Booking Package Service', 'package_services_table', [
						'service','service_name','quantity','is_required','base_price','package_price','photographer_discount_percentage','photographer_discount_amount','photographer_discounted_price','total_amount'
					]);
				});
			}
		});
	}
});

frappe.ui.form.on('Payment Table', {
	paid_amount: function(frm) { 
		refresh_payment_summary(frm);
		update_next_due_date(frm);
	},
	payment_method: function(frm) { /* no-op */ },
	transaction_reference_number: function(frm) { /* no-op */ },
	date: function(frm) { /* no-op */ }
});

// دالة لتحديث تاريخ الاستحقاق التالي
function update_next_due_date(frm) {
	if (!frm.doc.payment_table || frm.doc.payment_table.length === 0) {
		frm.set_value('due_date', null);
		return;
	}
	
	// البحث عن أول تاريخ بدون مبلغ مدفوع
	let next_due = null;
	for (let row of frm.doc.payment_table) {
		if (!row.paid_amount || row.paid_amount === 0) {
			if (!next_due || row.date < next_due) {
				next_due = row.date;
			}
		}
	}
	
	if (next_due && next_due !== frm.doc.due_date) {
		frm.set_value('due_date', next_due);
	}
}

// دالة لإخفاء/إظهار الحقول بناءً على نوع الحجز
function toggle_booking_type_fields(frm) {
	const isService = frm.doc.booking_type === 'Service';
	const isPackage = frm.doc.booking_type === 'Package';
	
	// Service: إظهار booking_date فقط
	// Package: إخفاء booking_date (لأن التواريخ في جدول package_booking_dates)
	frm.toggle_display('booking_date', isService);
	frm.toggle_display('start_time', isService);
	frm.toggle_display('end_time', isService);
}
