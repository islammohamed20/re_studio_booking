// Copyright (c) 2023, MASAR TEAM and contributors
// For license information, please see license.txt

frappe.ui.form.on('Service', {
	refresh: function(frm) {
		// Add help message for new services
		if (frm.doc.__islocal) {
			frm.set_intro(__("أدخل معلومات الخدمة الأساسية ثم انقر على حفظ"), 'blue');
		}
		
		// Add custom buttons
		frm.add_custom_button(__("عرض الحجوزات"), function() {
			frappe.set_route('List', 'Booking', {service: frm.doc.name});
		}, __("الإجراءات"));
		
		// Add status indicator
		if (frm.doc.is_active) {
			frm.set_indicator('نشط', 'green');
		} else {
			frm.set_indicator('غير نشط', 'red');
		}
		
		// Update duration display on form load
		update_duration_display(frm);
		
		// Store initial duration unit for conversion tracking
		frm._previous_duration_unit = frm.doc.duration_unit || 'دقيقة';
		
		// Add statistics section if not new
		if (!frm.doc.__islocal) {
			add_booking_stats_section(frm);
		}
		
		// تحديث عرض الحقول بناءً على نوع الوحدة
		toggle_unit_type_fields(frm);
	},
	
	type_unit: function(frm) {
		// تحديث عرض الحقول عند تغيير نوع الوحدة
		toggle_unit_type_fields(frm);
	},
	
	validate: function(frm) {
		// Ensure price is positive
		if (frm.doc.price <= 0) {
			frappe.throw(__("يجب أن يكون سعر الخدمة أكبر من صفر"));
		}
		
		// Ensure duration is positive if type_unit is مدة
		if (frm.doc.type_unit == 'مدة' && frm.doc.duration <= 0) {
			frappe.throw(__("يجب أن تكون مدة الخدمة أكبر من صفر"));
		}
	},
	
	is_active: function(frm) {
		// Update indicator when active status changes
		if (frm.doc.is_active) {
			frm.set_indicator('نشط', 'green');
		} else {
			frm.set_indicator('غير نشط', 'red');
			
			// Show warning when deactivating a service
			frappe.show_alert({
				message: __("تعطيل الخدمة سيؤثر على المصورين المرتبطين بها وعلى إمكانية حجزها"),
				indicator: 'orange'
			}, 5);
		}
	},
	
	price: function(frm) {
		// Validate price on change
		if (frm.doc.price <= 0) {
			frappe.show_alert({
				message: __("يجب أن يكون سعر الخدمة أكبر من صفر"),
				indicator: 'red'
			});
		}
	},
	
	duration: function(frm) {
		// Validate duration on change
		if (frm.doc.duration <= 0) {
			frappe.show_alert({
				message: __("يجب أن تكون مدة الخدمة أكبر من صفر"),
				indicator: 'red'
			});
		}
		
		// Update duration display based on unit
		update_duration_display(frm);
	},
	
	duration_unit: function(frm) {
		// Update duration field label and help text based on selected unit
		update_duration_display(frm);
		
		// Convert existing duration value if needed
		convert_duration_value(frm);
	}
});

// Function to add booking statistics section
function add_booking_stats_section(frm) {
	// Remove existing stats section if any
	frm.dashboard.clear_headline();
	
	// Fetch booking statistics for this service
	frappe.call({
		method: 're_studio_booking.re_studio_booking.doctype.service.service.get_booking_stats',
		args: {
			service: frm.doc.name
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
								<td>${booking.photographer}</td>
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

// Function to update duration display based on selected unit
function update_duration_display(frm) {
	if (!frm.doc.duration_unit) {
		frm.doc.duration_unit = 'دقيقة'; // Default to minutes
	}
	
	const unit = frm.doc.duration_unit;
	let label = 'المدة الافتراضية';
	let description = '';
	
	switch(unit) {
		case 'دقيقة':
			label = 'المدة الافتراضية (دقائق)';
			description = 'أدخل المدة بالدقائق';
			break;
		case 'ساعة':
			label = 'المدة الافتراضية (ساعات)';
			description = 'أدخل المدة بالساعات';
			break;
		case 'يوم':
			label = 'المدة الافتراضية (أيام)';
			description = 'أدخل المدة بالأيام';
			break;
	}
	
	// Update field label and description
	frm.set_df_property('duration', 'label', label);
	frm.set_df_property('duration', 'description', description);
	frm.refresh_field('duration');
}

// Function to convert duration value when unit changes
function convert_duration_value(frm) {
	if (!frm.doc.duration || !frm.doc.duration_unit) {
		return;
	}
	
	const current_unit = frm.doc.duration_unit;
	const previous_unit = frm._previous_duration_unit || 'دقيقة';
	
	if (current_unit === previous_unit) {
		return;
	}
	
	let current_duration = frm.doc.duration;
	let new_duration = current_duration;
	
	// Convert from previous unit to minutes first
	let duration_in_minutes = current_duration;
	switch(previous_unit) {
		case 'ساعة':
			duration_in_minutes = current_duration * 60;
			break;
		case 'يوم':
			duration_in_minutes = current_duration * 24 * 60;
			break;
	}
	
	// Convert from minutes to new unit
	switch(current_unit) {
		case 'دقيقة':
			new_duration = duration_in_minutes;
			break;
		case 'ساعة':
			new_duration = duration_in_minutes / 60;
			break;
		case 'يوم':
			new_duration = duration_in_minutes / (24 * 60);
			break;
	}
	
	// Round to 2 decimal places
	new_duration = Math.round(new_duration * 100) / 100;
	
	// Update the duration field
	frm.set_value('duration', new_duration);
	
	// Store current unit for next conversion
	frm._previous_duration_unit = current_unit;
	
	// Show conversion message
	frappe.show_alert({
		message: __(`تم تحويل المدة من ${current_duration} ${previous_unit} إلى ${new_duration} ${current_unit}`),
		indicator: 'blue'
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

// دالة لإظهار/إخفاء الحقول بناءً على نوع الوحدة
function toggle_unit_type_fields(frm) {
	const type_unit = frm.doc.type_unit;
	
	// إذا كان نوع الوحدة = مدة: إظهار حقول المدة
	const show_duration_fields = (type_unit == 'مدة');
	frm.toggle_display('duration', show_duration_fields);
	frm.toggle_display('min_duration', show_duration_fields);
	frm.toggle_display('max_duration', show_duration_fields);
	frm.toggle_display('duration_unit', show_duration_fields);
	
	// إذا كان نوع الوحدة غير "مدة" أو فارغ: إظهار حقل الكمية
	const show_quantity_field = type_unit && type_unit != 'مدة';
	frm.toggle_display('mount', show_quantity_field);
	
	// تحديث مطلوبية الحقول
	frm.toggle_reqd('duration', show_duration_fields);
	frm.toggle_reqd('mount', show_quantity_field);
}
