// Copyright (c) 2023, MASAR TEAM and contributors
// For license information, please see license.txt

frappe.ui.form.on('Service Package', {
	refresh: function(frm) {
		// Add help message for new packages
		if (frm.doc.__islocal) {
			frm.set_intro(__("أدخل معلومات الباقة الأساسية ثم انقر على حفظ"), 'blue');
		}
		
		// Add custom buttons
		frm.add_custom_button(__("عرض الحجوزات"), function() {
			frappe.set_route('List', 'Booking', {package: frm.doc.name});
		}, __("الإجراءات"));
		
		// Add status indicator
		if (frm.doc.is_active) {
			frm.set_indicator('نشط', 'green');
		} else {
			frm.set_indicator('غير نشط', 'red');
		}
		
		// Add calculate price button
		frm.add_custom_button(__("حساب السعر"), function() {
			frm.trigger('calculate_total_price');
		});
		
		// Add statistics section if not new
		if (!frm.doc.__islocal) {
			add_booking_stats_section(frm);
		}
	},
	
	validate: function(frm) {
		// Ensure price is positive
		if (frm.doc.price <= 0) {
			frappe.throw(__("يجب أن يكون سعر الباقة أكبر من صفر"));
		}
		
		// Ensure there's at least one service
		if (!frm.doc.package_services || frm.doc.package_services.length === 0) {
			frappe.throw(__("يجب إضافة خدمة واحدة على الأقل للباقة"));
		}
	},
	
	is_active: function(frm) {
		// Update indicator when active status changes
		if (frm.doc.is_active) {
			frm.set_indicator('نشط', 'green');
		} else {
			frm.set_indicator('غير نشط', 'red');
			
			// Show warning when deactivating a package
			frappe.show_alert({
				message: __("تعطيل الباقة سيؤثر على إمكانية حجزها"),
				indicator: 'orange'
			}, 5);
		}
	},
	
	price: function(frm) {
		// Validate price on change
		if (frm.doc.price <= 0) {
			frappe.show_alert({
				message: __("يجب أن يكون سعر الباقة أكبر من صفر"),
				indicator: 'red'
			});
		}
		
		// Calculate discount
		frm.trigger('calculate_discount');
	},
	
	calculate_total_price: function(frm) {
		let total = 0;
		
		// Sum up the prices of all services
		if (frm.doc.package_services && frm.doc.package_services.length > 0) {
			frm.doc.package_services.forEach(service => {
				total += service.amount || 0;
			});
		}
		
		// Update the total price field
		frm.set_value('total_services_price', total);
		
		// Calculate discount
		frm.trigger('calculate_discount');
		
		return total;
	},
	
	calculate_discount: function(frm) {
		if (frm.doc.total_services_price && frm.doc.price) {
			const discount = frm.doc.total_services_price - frm.doc.price;
			const discount_percentage = (discount / frm.doc.total_services_price) * 100;
			
			frm.set_value('discount_amount', discount);
			frm.set_value('discount_percentage', Math.round(discount_percentage));
		}
	},
	
	total_services_price: function(frm) {
		// Calculate discount when total services price changes
		frm.trigger('calculate_discount');
	}
});

// Child table for Package Service
frappe.ui.form.on('Package Service', {
	package_services_add: function(frm, cdt, cdn) {
		// Set default quantity to 1
		const row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, 'quantity', 1);
	},
	
	service: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		
		if (row.service) {
			frappe.call({
				method: 're_studio_booking.re_studio_booking.doctype.package_service.package_service.get_service_details',
				args: {
					service: row.service
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, 'service_name', r.message.service_name);
						frappe.model.set_value(cdt, cdn, 'service_price', r.message.price);
						
						// Calculate amount based on quantity and price
						const quantity = row.quantity || 1;
						frappe.model.set_value(cdt, cdn, 'amount', r.message.price * quantity);
						
						// Recalculate total price
						frm.trigger('calculate_total_price');
					}
				}
			});
		}
	},
	
	quantity: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		
		// Ensure quantity is at least 1
		if (row.quantity < 1) {
			frappe.model.set_value(cdt, cdn, 'quantity', 1);
			frappe.show_alert({
				message: __("يجب أن تكون الكمية 1 على الأقل"),
				indicator: 'red'
			});
		}
		
		// Update amount based on quantity and service price
		if (row.service_price) {
			frappe.model.set_value(cdt, cdn, 'amount', row.service_price * row.quantity);
		}
		
		// Recalculate total price
		frm.trigger('calculate_total_price');
	},
	
	package_services_remove: function(frm) {
		// Recalculate total price when a service is removed
		frm.trigger('calculate_total_price');
	}
});

// Function to add booking statistics section
function add_booking_stats_section(frm) {
	// Remove existing stats section if any
	frm.dashboard.clear_headline();
	
	// Fetch booking statistics for this package
	frappe.call({
		method: 're_studio_booking.re_studio_booking.doctype.service_package.service_package.get_booking_stats',
		args: {
			package: frm.doc.name
		},
		callback: function(r) {
			if (r.message) {
				const stats = r.message;
				
				// Create stats HTML
				let html = `
					<div class="row stats-container">
						<div class="col-sm-4">
							<div class="stat-box">
								<div class="stat-value">${stats.total_bookings}</div>
								<div class="stat-label">إجمالي الحجوزات</div>
							</div>
						</div>
						<div class="col-sm-4">
							<div class="stat-box">
								<div class="stat-value">${stats.completed_bookings}</div>
								<div class="stat-label">الحجوزات المكتملة</div>
							</div>
						</div>
						<div class="col-sm-4">
							<div class="stat-box">
								<div class="stat-value">${stats.upcoming_bookings}</div>
								<div class="stat-label">الحجوزات القادمة</div>
							</div>
						</div>
					</div>
				`;
				
				// Add upcoming bookings list if any
				if (stats.upcoming_list && stats.upcoming_list.length > 0) {
					html += `
						<div class="upcoming-bookings-container">
							<h5>الحجوزات القادمة</h5>
							<div class="table-responsive">
								<table class="table table-bordered table-hover">
									<thead>
										<tr>
											<th>التاريخ</th>
											<th>الوقت</th>
											<th>المصور</th>
											<th>العميل</th>
											<th>الحالة</th>
										</tr>
									</thead>
									<tbody>
					`;
					
					stats.upcoming_list.forEach(booking => {
						html += `
							<tr class="booking-row" data-name="${booking.name}">
								<td>${booking.booking_date}</td>
								<td>${booking.booking_time}</td>
								<td>${booking.photographer_name || booking.photographer}</td>
								<td>${booking.customer_name}</td>
								<td><span class="indicator ${get_status_color(booking.status)}"></span> ${booking.status}</td>
							</tr>
						`;
					});
					
					html += `
									</tbody>
								</table>
							</div>
						</div>
					`;
				}
				
				// Set dashboard headline
				frm.dashboard.set_headline_alert(html);
				
				// Add click handler for booking rows
				$('.booking-row').click(function() {
					const booking_name = $(this).data('name');
					frappe.set_route('Form', 'Booking', booking_name);
				});
				
				// Add custom CSS
				$('<style>').html(`
					.stats-container {
						margin-bottom: 15px;
					}
					.stat-box {
						text-align: center;
						padding: 10px;
						background-color: #f8f8f8;
						border-radius: 5px;
					}
					.stat-value {
						font-size: 24px;
						font-weight: bold;
						color: #2490ef;
					}
					.stat-label {
						font-size: 12px;
						color: #6c7680;
					}
					.upcoming-bookings-container {
						margin-top: 15px;
					}
					.booking-row {
						cursor: pointer;
					}
					.booking-row:hover {
						background-color: #f0f4f9;
					}
				`).appendTo('head');
			}
		}
	});
}

// Helper function to get status color
function get_status_color(status) {
	const status_colors = {
		'Confirmed': 'blue',
		'Completed': 'green',
		'Cancelled': 'red',
		'Pending': 'orange',
		'No Show': 'gray'
	};
	
	return status_colors[status] || 'gray';
}