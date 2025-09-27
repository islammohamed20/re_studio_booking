// Copyright (c) 2024, MASAR TEAM and contributors
// For license information, please see license.txt

frappe.ui.form.on('Price List', {
	refresh: function(frm) {
		// إضافة أزرار مخصصة
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__('تطبيق على العملاء'), function() {
				apply_to_clients(frm);
			});
			
			frm.add_custom_button(__('نسخ قائمة الأسعار'), function() {
				copy_price_list(frm);
			});
		}
		
		// تحديث العملة في التفاصيل
		if (frm.doc.currency) {
			frm.fields_dict.price_list_details.grid.update_docfield_property('price', 'options', 'currency');
			frm.fields_dict.price_list_details.grid.update_docfield_property('final_price', 'options', 'currency');
		}
	},
	
	currency: function(frm) {
		// تحديث العملة في جميع الصفوف
		if (frm.doc.currency) {
			frm.fields_dict.price_list_details.grid.update_docfield_property('price', 'options', 'currency');
			frm.fields_dict.price_list_details.grid.update_docfield_property('final_price', 'options', 'currency');
			frm.refresh_field('price_list_details');
		}
	},
	
	valid_from: function(frm) {
		validate_dates(frm);
	},
	
	valid_upto: function(frm) {
		validate_dates(frm);
	}
});

frappe.ui.form.on('Price List Detail', {
	price: function(frm, cdt, cdn) {
		calculate_final_price(frm, cdt, cdn);
	},
	
	discount_percentage: function(frm, cdt, cdn) {
		calculate_final_price(frm, cdt, cdn);
	},
	
	item_type: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		// مسح الحقول عند تغيير النوع
		if (row.item_type === 'Service') {
			row.service_package = '';
		} else if (row.item_type === 'Service Package') {
			row.service = '';
		}
		frm.refresh_field('price_list_details');
	},
	
	service: function(frm, cdt, cdn) {
		get_default_price(frm, cdt, cdn, 'Service');
	},
	
	service_package: function(frm, cdt, cdn) {
		get_default_price(frm, cdt, cdn, 'Service Package');
	}
});

function calculate_final_price(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	if (row.price && row.discount_percentage) {
		let discount_amount = (row.price * row.discount_percentage) / 100;
		row.final_price = row.price - discount_amount;
	} else {
		row.final_price = row.price || 0;
	}
	frm.refresh_field('price_list_details');
}

function get_default_price(frm, cdt, cdn, item_type) {
	let row = locals[cdt][cdn];
	let item_name = item_type === 'Service' ? row.service : row.service_package;
	
	if (item_name) {
		frappe.db.get_value(item_type, item_name, ['price', 'discount_price'], function(r) {
			if (r && r.price) {
				row.price = r.discount_price || r.price;
				calculate_final_price(frm, cdt, cdn);
			}
		});
	}
}

function validate_dates(frm) {
	if (frm.doc.valid_from && frm.doc.valid_upto) {
		if (frappe.datetime.get_diff(frm.doc.valid_upto, frm.doc.valid_from) < 0) {
			frappe.msgprint(__('تاريخ النهاية يجب أن يكون بعد تاريخ البداية'));
			frm.set_value('valid_upto', '');
		}
	}
}

function apply_to_clients(frm) {
	let d = new frappe.ui.Dialog({
		title: __('تطبيق قائمة الأسعار على العملاء'),
		fields: [
			{
				fieldname: 'clients',
				fieldtype: 'Table MultiSelect',
				label: __('العملاء'),
				options: 'Client',
				reqd: 1
			}
		],
		primary_action_label: __('تطبيق'),
		primary_action: function() {
			let values = d.get_values();
			if (values.clients && values.clients.length > 0) {
				frappe.call({
					method: 'frappe.client.set_value',
					args: {
						doctype: 'Client',
						name: values.clients,
						fieldname: 'price_list',
						value: frm.doc.name
					},
					callback: function(r) {
						if (!r.exc) {
							frappe.msgprint(__('تم تطبيق قائمة الأسعار بنجاح'));
							d.hide();
						}
					}
				});
			}
		}
	});
	d.show();
}

function copy_price_list(frm) {
	let d = new frappe.ui.Dialog({
		title: __('نسخ قائمة الأسعار'),
		fields: [
			{
				fieldname: 'new_name',
				fieldtype: 'Data',
				label: __('اسم قائمة الأسعار الجديدة'),
				reqd: 1
			}
		],
		primary_action_label: __('نسخ'),
		primary_action: function() {
			let values = d.get_values();
			if (values.new_name) {
				frappe.call({
					method: 'frappe.client.copy_doc',
					args: {
						dt: 'Price List',
						dn: frm.doc.name
					},
					callback: function(r) {
						if (!r.exc && r.message) {
							r.message.price_list_name = values.new_name;
							frappe.set_route('Form', 'Price List', r.message.name);
							d.hide();
						}
					}
				});
			}
		}
	});
	d.show();
}