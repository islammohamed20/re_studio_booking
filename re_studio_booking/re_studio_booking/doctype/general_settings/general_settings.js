// Copyright (c) 2024, Masar Digital Group and contributors
// For license information, please see license.txt

frappe.ui.form.on('General Settings', {
	refresh: function(frm) {
		// Set form title
		frm.set_df_property('company_section', 'label', __('Company Information'));
		frm.set_df_property('currency_section', 'label', __('Currency & Pricing'));
		frm.set_df_property('booking_section', 'label', __('Booking Settings'));
		frm.set_df_property('notification_section', 'label', __('Notifications'));
		frm.set_df_property('print_section', 'label', __('Print Settings'));
		frm.set_df_property('system_section', 'label', __('System Settings'));
		frm.set_df_property('localization_section', 'label', __('Localization'));
		frm.set_df_property('status_section', 'label', __('Status Settings'));
		
		// Add custom buttons
		frm.add_custom_button(__('Test Email Settings'), function() {
			test_email_settings(frm);
		});
		
		frm.add_custom_button(__('Test SMS Settings'), function() {
			test_sms_settings(frm);
		});
		
		frm.add_custom_button(__('Preview Print Format'), function() {
			preview_print_format(frm);
		});
		
		// Set field dependencies
		set_field_dependencies(frm);
		
		// Set default values if new
		if (frm.is_new()) {
			set_default_values(frm);
		}
	},
	
	default_currency: function(frm) {
		// Update currency symbol when currency changes
		if (frm.doc.default_currency) {
			update_currency_symbol(frm);
		}
	},
	
	currency_position: function(frm) {
		// Update currency format preview
		update_currency_preview(frm);
	},
	
	currency_symbol: function(frm) {
		// Update currency format preview
		update_currency_preview(frm);
	},
	
	decimal_places: function(frm) {
		// Update currency format preview
		update_currency_preview(frm);
	},
	
	business_start_time: function(frm) {
		// Validate business hours
		validate_business_hours(frm);
	},
	
	business_end_time: function(frm) {
		// Validate business hours
		validate_business_hours(frm);
	},
	
	tax_rate: function(frm) {
		// Validate tax rate
		if (frm.doc.tax_rate && (frm.doc.tax_rate < 0 || frm.doc.tax_rate > 100)) {
			frappe.msgprint(__('Tax rate must be between 0 and 100'));
			frm.set_value('tax_rate', 15);
		}
	},
	
	deposit_percentage: function(frm) {
		// Validate deposit percentage
		if (frm.doc.deposit_percentage && (frm.doc.deposit_percentage < 0 || frm.doc.deposit_percentage > 100)) {
			frappe.msgprint(__('Deposit percentage must be between 0 and 100'));
			frm.set_value('deposit_percentage', 30);
		}
	},
	
	time_slot_duration: function(frm) {
		// Validate time slot duration
		if (frm.doc.time_slot_duration && frm.doc.time_slot_duration <= 0) {
			frappe.msgprint(__('Time slot duration must be greater than 0'));
			frm.set_value('time_slot_duration', 60);
		}
	},
	
	send_email_notifications: function(frm) {
		// Toggle email fields visibility
		toggle_email_fields(frm);
	},
	
	send_sms_notifications: function(frm) {
		// Toggle SMS fields visibility
		toggle_sms_fields(frm);
	},
	
	show_company_logo: function(frm) {
		// Toggle logo field requirement
		if (frm.doc.show_company_logo) {
			frm.set_df_property('company_logo', 'reqd', 1);
		} else {
			frm.set_df_property('company_logo', 'reqd', 0);
		}
	}
});

// Helper functions
function set_field_dependencies(frm) {
	// Email notification dependencies
	toggle_email_fields(frm);
	
	// SMS notification dependencies
	toggle_sms_fields(frm);
	
	// Company logo dependency
	if (frm.doc.show_company_logo) {
		frm.set_df_property('company_logo', 'reqd', 1);
	}
}

function set_default_values(frm) {
	// Set default currency settings
	if (!frm.doc.default_currency) {
		frm.set_value('default_currency', 'SAR');
	}
	if (!frm.doc.currency_symbol) {
		frm.set_value('currency_symbol', 'ر.س');
	}
	if (!frm.doc.currency_position) {
		frm.set_value('currency_position', 'Right');
	}
	if (!frm.doc.decimal_places) {
		frm.set_value('decimal_places', 2);
	}
	
	// Set default business hours
	if (!frm.doc.business_start_time) {
		frm.set_value('business_start_time', '09:00:00');
	}
	if (!frm.doc.business_end_time) {
		frm.set_value('business_end_time', '18:00:00');
	}
	
	// Set default working days
	if (!frm.doc.saturday) frm.set_value('saturday', 1);
	if (!frm.doc.sunday) frm.set_value('sunday', 1);
	if (!frm.doc.monday) frm.set_value('monday', 1);
	if (!frm.doc.tuesday) frm.set_value('tuesday', 1);
	if (!frm.doc.wednesday) frm.set_value('wednesday', 1);
	if (!frm.doc.thursday) frm.set_value('thursday', 1);
	if (!frm.doc.friday) frm.set_value('friday', 0);
	
	// Set default tax rate
	if (!frm.doc.tax_rate) {
		frm.set_value('tax_rate', 15);
	}
	
	// Set default deposit percentage
	if (!frm.doc.deposit_percentage) {
		frm.set_value('deposit_percentage', 30);
	}
	
	// Set default time slot duration
	if (!frm.doc.time_slot_duration) {
		frm.set_value('time_slot_duration', 60);
	}
}

function update_currency_symbol(frm) {
	const currency_symbols = {
		'SAR': 'ر.س',
		'USD': '$',
		'EUR': '€',
		'GBP': '£',
		'AED': 'د.إ',
		'KWD': 'د.ك',
		'QAR': 'ر.ق',
		'BHD': 'د.ب',
		'OMR': 'ر.ع',
		'JOD': 'د.أ',
		'EGP': 'ج.م'
	};
	
	if (currency_symbols[frm.doc.default_currency]) {
		frm.set_value('currency_symbol', currency_symbols[frm.doc.default_currency]);
	}
	
	update_currency_preview(frm);
}

function update_currency_preview(frm) {
	if (!frm.doc.currency_symbol) return;
	
	const amount = 1234.56;
	const decimal_places = frm.doc.decimal_places || 2;
	const formatted_amount = amount.toFixed(decimal_places);
	
	let preview;
	if (frm.doc.currency_position === 'Left') {
		preview = `${frm.doc.currency_symbol} ${formatted_amount}`;
	} else {
		preview = `${formatted_amount} ${frm.doc.currency_symbol}`;
	}
	
	// Show preview in a message
	if (frm.currency_preview_timeout) {
		clearTimeout(frm.currency_preview_timeout);
	}
	
	frm.currency_preview_timeout = setTimeout(() => {
		frappe.show_alert({
			message: __('Currency Preview: {0}', [preview]),
			indicator: 'blue'
		}, 3);
	}, 500);
}

function validate_business_hours(frm) {
	if (frm.doc.business_start_time && frm.doc.business_end_time) {
		if (frm.doc.business_start_time >= frm.doc.business_end_time) {
			frappe.msgprint(__('Business start time must be before end time'));
			frm.set_value('business_end_time', '');
		}
	}
}

function toggle_email_fields(frm) {
	const show_email_fields = frm.doc.send_email_notifications;
	frm.toggle_display(['admin_email', 'email_template'], show_email_fields);
	frm.set_df_property('admin_email', 'reqd', show_email_fields);
}

function toggle_sms_fields(frm) {
	const show_sms_fields = frm.doc.send_sms_notifications;
	frm.toggle_display(['sms_api_key'], show_sms_fields);
	frm.set_df_property('sms_api_key', 'reqd', show_sms_fields);
}

function test_email_settings(frm) {
	if (!frm.doc.send_email_notifications) {
		frappe.msgprint(__('Email notifications are disabled'));
		return;
	}
	
	if (!frm.doc.admin_email) {
		frappe.msgprint(__('Please set admin email first'));
		return;
	}
	
	frappe.call({
		method: 'frappe.core.doctype.communication.email.make',
		args: {
			recipients: frm.doc.admin_email,
			subject: __('Test Email from Re Studio Booking'),
			content: __('This is a test email to verify email settings are working correctly.'),
			send_email: 1
		},
		callback: function(r) {
			if (r.message) {
				frappe.msgprint(__('Test email sent successfully'));
			} else {
				frappe.msgprint(__('Failed to send test email'));
			}
		}
	});
}

function test_sms_settings(frm) {
	if (!frm.doc.send_sms_notifications) {
		frappe.msgprint(__('SMS notifications are disabled'));
		return;
	}
	
	if (!frm.doc.sms_api_key) {
		frappe.msgprint(__('Please set SMS API key first'));
		return;
	}
	
	frappe.msgprint(__('SMS testing functionality will be implemented based on your SMS provider'));
}

function preview_print_format(frm) {
	// This would open a preview of the print format
	frappe.msgprint(__('Print format preview will be implemented'));
}

// Currency formatting utility
frappe.provide('re_studio_booking.utils');

re_studio_booking.utils.format_currency = function(amount, settings) {
	if (!amount) return '0';
	
	const decimal_places = settings?.decimal_places || 2;
	const currency_symbol = settings?.currency_symbol || 'ر.س';
	const currency_position = settings?.currency_position || 'Right';
	const thousand_separator = settings?.thousand_separator || ',';
	
	// Format the number
	let formatted_amount = parseFloat(amount).toFixed(decimal_places);
	
	// Add thousand separator
	if (thousand_separator) {
		const parts = formatted_amount.split('.');
		parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, thousand_separator);
		formatted_amount = parts.join('.');
	}
	
	// Add currency symbol
	if (currency_position === 'Left') {
		return `${currency_symbol} ${formatted_amount}`;
	} else {
		return `${formatted_amount} ${currency_symbol}`;
	}
};

// Get settings utility
re_studio_booking.utils.get_settings = function(callback) {
	frappe.call({
		method: 're_studio_booking.re_studio_booking.doctype.general_settings.general_settings.get_general_settings',
		callback: function(r) {
			if (r.message && callback) {
				callback(r.message);
			}
		}
	});
};