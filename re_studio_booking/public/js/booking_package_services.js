frappe.ui.form.on('Booking', {
	refresh: function(frm) {
		// Add custom button only (remove edit/delete block completely)
		if (frm.doc.booking_type === "Package" && frm.doc.package) {
			frm.add_custom_button(__('إضافة خدمة'), function() {
				show_add_service_dialog(frm);
			}, __('خدمات الباقة'));
			// Ensure default toolbar delete/edit hidden every refresh
			hide_package_services_edit_delete(frm);
		}
	},
	package_services_table_add: function(frm, cdt, cdn) {
		// Auto-calculate total amount when a new row is added
		let row = locals[cdt][cdn];
		row.total_amount = row.quantity * row.package_price;
		frm.refresh_field('package_services_table');
		// Recompute package totals and deposit
		recalculate_total(frm);
	},
	package_services_table_remove: function(frm) {
		// Recalculate total amount when a row is removed
		recalculate_total(frm);
	}
});

frappe.ui.form.on('Booking Package Service', {
	quantity: function(frm, cdt, cdn) {
		// Update total amount when quantity changes
		let row = locals[cdt][cdn];
		row.total_amount = row.quantity * row.package_price;
		frm.refresh_field('package_services_table');
		recalculate_total(frm);
		
		// Update quantity on server
		update_service_quantity(frm, row);
	},
	
	package_price: function(frm, cdt, cdn) {
		// Update total amount when price changes
		let row = locals[cdt][cdn];
		row.total_amount = row.quantity * row.package_price;
		frm.refresh_field('package_services_table');
		recalculate_total(frm);
		
		// Update service on server
		update_service_data(frm, row);
	},
	
	service_name: function(frm, cdt, cdn) {
		// Update service on server when name changes
		let row = locals[cdt][cdn];
		update_service_data(frm, row);
	}
});

// Function to show dialog for adding a new service
function show_add_service_dialog(frm) {
	frappe.call({
		method: 're_studio_booking.re_studio_booking.doctype.booking.booking.get_available_services',
		args: {
			booking_name: frm.doc.name
		},
		callback: function(r) {
			if (r.message && r.message.status === 'success') {
				let services = r.message.services;
				
				if (services.length === 0) {
					frappe.msgprint(__('لا توجد خدمات إضافية متاحة'));
					return;
				}
				
				let service_options = {};
				services.forEach(function(service) {
					service_options[service.name] = service.service_name;
				});
				
				let d = new frappe.ui.Dialog({
					title: __('إضافة خدمة جديدة'),
					fields: [
						{
							label: __('الخدمة'),
							fieldname: 'service',
							fieldtype: 'Select',
							options: service_options,
							reqd: 1,
							onchange: function() {
								let selected_service = services.find(s => s.name === this.get_value());
								if (selected_service) {
									d.set_value('service_name', selected_service.service_name);
									d.set_value('base_price', selected_service.price);
									d.set_value('package_price', selected_service.price);
								}
							}
						},
						{
							label: __('اسم الخدمة'),
							fieldname: 'service_name',
							fieldtype: 'Data',
							read_only: 1
						},
						{
							label: __('الكمية'),
							fieldname: 'quantity',
							fieldtype: 'Int',
							default: 1,
							min: 1,
							reqd: 1
						},
						{
							label: __('السعر الأساسي'),
							fieldname: 'base_price',
							fieldtype: 'Currency',
							read_only: 1
						},
						{
							label: __('سعر الباقة'),
							fieldname: 'package_price',
							fieldtype: 'Currency',
							reqd: 1
						},
						{
							label: __('إجباري'),
							fieldname: 'is_required',
							fieldtype: 'Check',
							default: 0
						}
					],
					primary_action_label: __('إضافة'),
					primary_action: function() {
						let values = d.get_values();
						
						frappe.call({
							method: 're_studio_booking.re_studio_booking.doctype.booking.booking.add_package_service',
							args: {
								booking_name: frm.doc.name,
								service_data: values
							},
							callback: function(r) {
								if (r.message && r.message.status === 'success') {
									frappe.show_alert({
										message: __('تمت إضافة الخدمة بنجاح'),
										indicator: 'green'
									});
									frm.reload_doc();
								} else {
									frappe.msgprint(r.message.message || __('حدث خطأ أثناء إضافة الخدمة'));
								}
							}
						});
						
						d.hide();
					}
				});
				
				d.show();
			} else {
				frappe.msgprint(r.message.message || __('حدث خطأ أثناء جلب الخدمات المتاحة'));
			}
		}
	});
}

// Function to show dialog for editing an existing service
function show_edit_service_dialog(frm, row_data) {
	// Get the row data from the grid
	let row = locals[row_data.doctype][row_data.name];
	
	let d = new frappe.ui.Dialog({
		title: __('تعديل الخدمة'),
		fields: [
			{
				label: __('اسم الخدمة'),
				fieldname: 'service_name',
				fieldtype: 'Data',
				default: row.service_name
			},
			{
				label: __('الكمية'),
				fieldname: 'quantity',
				fieldtype: 'Int',
				default: row.quantity,
				min: 1,
				reqd: 1
			},
			{
				label: __('السعر الأساسي'),
				fieldname: 'base_price',
				fieldtype: 'Currency',
				default: row.base_price
			},
			{
				label: __('سعر الباقة'),
				fieldname: 'package_price',
				fieldtype: 'Currency',
				default: row.package_price,
				reqd: 1
			},
			{
				label: __('إجباري'),
				fieldname: 'is_required',
				fieldtype: 'Check',
				default: row.is_required
			}
		],
		primary_action_label: __('حفظ'),
		primary_action: function() {
			let values = d.get_values();
			
			frappe.call({
				method: 're_studio_booking.re_studio_booking.doctype.booking.booking.update_package_service',
				args: {
					booking_name: frm.doc.name,
					row_name: row.name,
					service_data: values
				},
				callback: function(r) {
					if (r.message && r.message.status === 'success') {
						frappe.show_alert({
							message: __('تم تحديث الخدمة بنجاح'),
							indicator: 'green'
						});
						frm.reload_doc();
					} else {
						frappe.msgprint(r.message.message || __('حدث خطأ أثناء تحديث الخدمة'));
					}
				}
			});
			
			d.hide();
		}
	});
	
	d.show();
}

// Function to update service quantity on server
function update_service_quantity(frm, row) {
	frappe.call({
		method: 're_studio_booking.re_studio_booking.doctype.booking.booking.update_service_quantity',
		args: {
			booking_name: frm.doc.name,
			row_name: row.name,
			quantity: row.quantity
		},
		callback: function(r) {
			if (r.message && r.message.status === 'success') {
				// Success, no need to show message for better UX
			} else if (r.message && r.message.status === 'error') {
				frappe.msgprint(r.message.message || __('حدث خطأ أثناء تحديث الكمية'));
				frm.reload_doc();
			}
		}
	});
}

// Function to update service data on server
function update_service_data(frm, row) {
	frappe.call({
		method: 're_studio_booking.re_studio_booking.doctype.booking.booking.update_package_service',
		args: {
			booking_name: frm.doc.name,
			row_name: row.name,
			service_data: {
				service: row.service,
				service_name: row.service_name,
				quantity: row.quantity,
				is_required: row.is_required,
				base_price: row.base_price,
				package_price: row.package_price
			}
		},
		callback: function(r) {
			if (r.message && r.message.status === 'success') {
				// Success, no need to show message for better UX
			} else if (r.message && r.message.status === 'error') {
				frappe.msgprint(r.message.message || __('حدث خطأ أثناء تحديث بيانات الخدمة'));
				frm.reload_doc();
			}
		}
	});
}

// Function to delete a package service
function delete_package_service(frm, row) {
	frappe.confirm(
		__('هل أنت متأكد من حذف هذه الخدمة؟'),
		function() {
			frappe.call({
				method: 're_studio_booking.re_studio_booking.doctype.booking.booking.delete_package_service',
				args: {
					booking_name: frm.doc.name,
					row_name: row.name
				},
				callback: function(r) {
					if (r.message && r.message.status === 'success') {
						frappe.show_alert({
							message: __('تم حذف الخدمة بنجاح'),
							indicator: 'green'
						});
						frm.reload_doc();
					} else {
						frappe.msgprint(r.message.message || __('حدث خطأ أثناء حذف الخدمة'));
					}
				}
			});
		}
	);
}

// Function to recalculate total amount
function recalculate_total(frm) {
	let base_total = 0;
	let final_total = 0;
	(frm.doc.package_services_table || []).forEach(function(service) {
		const qty = flt(service.quantity || 1);
		base_total += flt(service.base_price || 0) * qty;
		// Prefer server-computed amount when present (includes photographer discount)
		const row_total = service.amount != null ? flt(service.amount) : flt(service.total_amount || (flt(service.package_price || 0) * qty));
		final_total += row_total;
	});
	// Update package totals on parent
	frm.set_value('base_amount_package', base_total);
	frm.set_value('total_amount_package', final_total);
	
	// Update deposit via unified UI helper if available
	if (typeof update_deposit_ui === 'function') {
		update_deposit_ui(frm);
	} else {
		// Fallback: compute deposit from General Settings
		frappe.call({
			method: 're_studio_booking.re_studio_booking.doctype.general_settings.general_settings.get_pricing_settings',
			callback: function(res) {
				const s = res.message || {};
				const pct = flt(s.deposit_percentage || 30);
				const min_amt = flt(s.minimum_booking_amount || 0);
				let deposit = ((final_total * pct) / 100);
				deposit = Number(deposit.toFixed(2));
				if (min_amt > 0 && deposit < min_amt && final_total > 0) {
					deposit = Math.min(min_amt, final_total);
				}
				frm.set_value('deposit_amount', deposit);
			}
		});
	}
}

// Helper to hide default Edit/Delete buttons of the grid toolbar
function hide_package_services_edit_delete(frm) {
	try {
		let grid = frm.fields_dict['package_services_table'] && frm.fields_dict['package_services_table'].grid;
		if (!grid) return;
		const toolbar = $(grid.wrapper).find('.grid-footer, .grid-buttons');
		toolbar.find('button').filter(function(){
			const t = $(this).text().trim();
			return t === 'Delete' || t === 'Edit';
		}).hide();
	} catch(e) {
		// silent
	}
}