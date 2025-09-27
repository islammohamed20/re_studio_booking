frappe.ui.form.on('Booking Package Service', {
	refresh: function(frm) {
		// This is a child table, so we handle the logic in the parent form
	}
});

// Handle row deletion logic for package services
frappe.ui.form.on('Booking', {
	package_services_table_remove: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		
		// Check if the service is required (mandatory)
		if (row.is_required) {
			// Prevent deletion of mandatory services
			frappe.msgprint({
				title: __('خدمة إجبارية'),
				message: __('لا يمكن حذف هذه الخدمة لأنها إجبارية في الباقة'),
				indicator: 'red'
			});
			
			// Cancel the deletion by returning false
			return false;
		}
		
		// Allow deletion for optional services
		return true;
	}
});

// Alternative approach using before_remove event
frappe.ui.form.on('Booking Package Service', {
	before_remove: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		
		// Check if the service is required (mandatory)
		if (row.is_required) {
			// Show error message
			frappe.msgprint({
				title: __('خدمة إجبارية'),
				message: __('لا يمكن حذف هذه الخدمة لأنها إجبارية في الباقة'),
				indicator: 'red'
			});
			
			// Prevent deletion
			return false;
		}
		
		// Allow deletion for optional services
		return true;
	}
});