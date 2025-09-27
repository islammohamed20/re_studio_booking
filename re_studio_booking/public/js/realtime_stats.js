// Real-time statistics update for Re Studio Booking
// This file handles updating UI statistics when Doctypes are modified

frappe.ready(function() {
	// Listen for real-time updates
	frappe.realtime.on('service_updated', function(data) {
		updateServiceStats();
	});
	
	frappe.realtime.on('package_updated', function(data) {
		updatePackageStats();
	});
	
	// Update service statistics
	function updateServiceStats() {
		// Update active services count
		frappe.call({
			method: 'frappe.client.get_count',
			args: {
				doctype: 'Service',
				filters: {'is_active': 1}
			},
			callback: function(r) {
				if (r.message !== undefined) {
					// Update UI elements with active services count
					$('.active-services-count').text(r.message);
					
					// Show notification
					frappe.show_alert({
						message: __('تم تحديث إحصائيات الخدمات'),
						indicator: 'green'
					}, 3);
				}
			}
		});
		
		// Update total services count
		frappe.call({
			method: 'frappe.client.get_count',
			args: {
				doctype: 'Service'
			},
			callback: function(r) {
				if (r.message !== undefined) {
					$('.total-services-count').text(r.message);
				}
			}
		});
	}
	
	// Update package statistics
	function updatePackageStats() {
		// Update active packages count
		frappe.call({
			method: 'frappe.client.get_count',
			args: {
				doctype: 'Service Package',
				filters: {'is_active': 1}
			},
			callback: function(r) {
				if (r.message !== undefined) {
					$('.active-packages-count').text(r.message);
					
					// Show notification
					frappe.show_alert({
						message: __('تم تحديث إحصائيات الباقات'),
						indicator: 'green'
					}, 3);
				}
			}
		});
		
		// Update total packages count
		frappe.call({
			method: 'frappe.client.get_count',
			args: {
				doctype: 'Service Package'
			},
			callback: function(r) {
				if (r.message !== undefined) {
					$('.total-packages-count').text(r.message);
				}
			}
		});
		
		// Set featured packages count to 0 (no featured field in Service Package doctype)
		$('.featured-packages-count').text(0);
	}
	
	// Initialize stats on page load
	if (window.location.pathname.includes('/services')) {
		updateServiceStats();
	}
	
	if (window.location.pathname.includes('/packages')) {
		updatePackageStats();
	}
});

// Add hooks for Service doctype
frappe.ui.form.on('Service', {
	after_save: function(frm) {
		// Emit real-time event
		frappe.realtime.publish('service_updated', {
			service: frm.doc.name,
			is_active: frm.doc.is_active
		});
	},
	
	is_active: function(frm) {
		// Update indicator when active status changes
		if (frm.doc.is_active) {
			frm.set_indicator('نشط', 'green');
		} else {
			frm.set_indicator('غير نشط', 'red');
			
			// Show warning when deactivating a service
			frappe.show_alert({
				message: __('تعطيل الخدمة سيؤثر على إمكانية حجزها'),
				indicator: 'orange'
			}, 5);
		}
	}
});

// Add hooks for Service Package doctype
frappe.ui.form.on('Service Package', {
	after_save: function(frm) {
		// Emit real-time event
		frappe.realtime.publish('package_updated', {
			package: frm.doc.name,
			is_active: frm.doc.is_active
		});
	}
});