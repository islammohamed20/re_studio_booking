// Copyright (c) 2023, MASAR TEAM and contributors
// For license information, please see license.txt

frappe.ui.form.on('Booking Report', {
	refresh: function(frm) {
		// Add help message
		frm.set_intro(__("هذه الصفحة تسمح لك بإنشاء تقارير مختلفة عن الحجوزات. اختر نوع التقرير والنطاق الزمني ثم انقر على زر 'حفظ' لإنشاء التقرير."));
		
		// Add custom buttons
		if (frm.doc.report_data) {
			frm.add_custom_button(__('طباعة التقرير'), function() {
				frm.print_doc();
			});
			
			frm.add_custom_button(__('تصدير إلى Excel'), function() {
				frm.export_report_to_excel();
			});
			
			// Add visualization button based on report type
			frm.add_custom_button(__('عرض الرسم البياني'), function() {
				frm.show_report_visualization();
			});
		}
		
		// Add quick report buttons
		frm.add_custom_button(__('تقرير اليوم'), function() {
			frm.set_value('report_type', 'Booking Summary');
			frm.set_value('date_range', 'Today');
			frm.save();
		}, __('تقارير سريعة'));
		
		frm.add_custom_button(__('تقرير هذا الأسبوع'), function() {
			frm.set_value('report_type', 'Booking Summary');
			frm.set_value('date_range', 'This Week');
			frm.save();
		}, __('تقارير سريعة'));
		
		frm.add_custom_button(__('تقرير هذا الشهر'), function() {
			frm.set_value('report_type', 'Booking Summary');
			frm.set_value('date_range', 'This Month');
			frm.save();
		}, __('تقارير سريعة'));
		
		// Display report data if available
		if (frm.doc.report_data) {
			frm.display_report_data();
		}
	},
	
	report_type: function(frm) {
		// Clear previous report data
		frm.set_value('summary', '');
		frm.set_value('report_data', '');
		
		// Show/hide fields based on report type
		frm.toggle_display('status', frm.doc.report_type === 'Booking Summary');
		frm.toggle_display('photographer', frm.doc.report_type === 'Photographer Performance');
	},
	
	date_range: function(frm) {
		// Show/hide date fields based on date range
		frm.toggle_reqd('start_date', frm.doc.date_range === 'Custom');
		frm.toggle_reqd('end_date', frm.doc.date_range === 'Custom');
		
		// Clear previous report data
		frm.set_value('summary', '');
		frm.set_value('report_data', '');
	},
	
	export_report_to_excel: function(frm) {
		if (!frm.doc.report_data) return;
		
		let report_data = JSON.parse(frm.doc.report_data);
		let data = [];
		let columns = [];
		
		// Format data based on report type
		if (frm.doc.report_type === 'Booking Summary' && report_data.bookings) {
			columns = [
				{label: __('رقم الحجز'), fieldname: 'name'},
				{label: __('اسم العميل'), fieldname: 'customer_name'},
				{label: __('تاريخ الحجز'), fieldname: 'booking_date'},
				{label: __('وقت البدء'), fieldname: 'start_time'},
				{label: __('وقت الانتهاء'), fieldname: 'end_time'},
				{label: __('الخدمة'), fieldname: 'service'},
				{label: __('المصور'), fieldname: 'photographer'},
				{label: __('الحالة'), fieldname: 'status'}
			];
			data = report_data.bookings;
		} else if (frm.doc.report_type === 'Photographer Performance' && report_data.photographer_performance) {
			columns = [
				{label: __('المصور'), fieldname: 'photographer'},
				{label: __('عدد الحجوزات'), fieldname: 'total_bookings'},
				{label: __('إجمالي الدقائق'), fieldname: 'total_minutes'}
			];
			data = report_data.photographer_performance;
		} else if (frm.doc.report_type === 'Service Popularity' && report_data.service_popularity) {
			columns = [
				{label: __('الخدمة'), fieldname: 'service'},
				{label: __('اسم الخدمة'), fieldname: 'service_name'},
				{label: __('الفئة'), fieldname: 'category'},
				{label: __('عدد الحجوزات'), fieldname: 'booking_count'}
			];
			data = report_data.service_popularity;
		} else if (frm.doc.report_type === 'Revenue Report' && report_data.revenue_by_service) {
			columns = [
				{label: __('الخدمة'), fieldname: 'service'},
				{label: __('عدد الحجوزات'), fieldname: 'booking_count'},
				{label: __('إجمالي الإيرادات'), fieldname: 'total_revenue'}
			];
			data = report_data.revenue_by_service;
		}
		
		// Export to Excel
		frappe.tools.downloadify(data, null, frm.doc.name);
	},
	
	show_report_visualization: function(frm) {
		if (!frm.doc.report_data) return;
		
		let report_data = JSON.parse(frm.doc.report_data);
		let dialog = new frappe.ui.Dialog({
			title: __('تصور التقرير'),
			fields: [
				{
					fieldtype: 'HTML',
					fieldname: 'chart_area'
				}
			]
		});
		
		dialog.show();
		
		// Create chart based on report type
		setTimeout(() => {
			let $chart_area = dialog.fields_dict.chart_area.$wrapper;
			$chart_area.empty();
			
			let chart_data = {};
			let chart_type = 'bar';
			
			if (frm.doc.report_type === 'Booking Summary' && report_data.status_counts) {
				chart_data = {
					labels: Object.keys(report_data.status_counts),
					datasets: [{
						name: __('عدد الحجوزات'),
						values: Object.values(report_data.status_counts)
					}]
				};
				chart_type = 'pie';
			} else if (frm.doc.report_type === 'Photographer Performance' && report_data.photographer_performance) {
				chart_data = {
					labels: report_data.photographer_performance.map(item => item.photographer),
					datasets: [{
						name: __('عدد الحجوزات'),
						values: report_data.photographer_performance.map(item => item.total_bookings)
					}]
				};
			} else if (frm.doc.report_type === 'Service Popularity' && report_data.service_popularity) {
				chart_data = {
					labels: report_data.service_popularity.map(item => item.service_name || item.service),
					datasets: [{
						name: __('عدد الحجوزات'),
						values: report_data.service_popularity.map(item => item.booking_count)
					}]
				};
			} else if (frm.doc.report_type === 'Revenue Report' && report_data.revenue_by_service) {
				chart_data = {
					labels: report_data.revenue_by_service.map(item => item.service),
					datasets: [{
						name: __('الإيرادات'),
						values: report_data.revenue_by_service.map(item => item.total_revenue)
					}]
				};
			}
			
			if (chart_data.labels && chart_data.labels.length) {
				new frappe.Chart($chart_area[0], {
					data: chart_data,
					type: chart_type,
					height: 300,
					colors: ['#5e64ff', '#743ee2', '#ff5858', '#ffa00a', '#00a8ff'],
					formatTooltipX: d => d,
					formatTooltipY: d => d
				});
			} else {
				$chart_area.html('<div class="text-center text-muted">' + __('لا توجد بيانات كافية لعرض الرسم البياني') + '</div>');
			}
		}, 300);
	},
	
	display_report_data: function(frm) {
		if (!frm.doc.report_data) return;
		
		let report_data = JSON.parse(frm.doc.report_data);
		let $report_area = $('<div class="report-data-container"></div>');
		
		// Create report display based on report type
		if (frm.doc.report_type === 'Booking Summary' && report_data.bookings) {
			// Create bookings table
			let $table = $('<table class="table table-bordered"><thead><tr>' +
				'<th>' + __('رقم الحجز') + '</th>' +
				'<th>' + __('اسم العميل') + '</th>' +
				'<th>' + __('تاريخ الحجز') + '</th>' +
				'<th>' + __('وقت البدء') + '</th>' +
				'<th>' + __('وقت الانتهاء') + '</th>' +
				'<th>' + __('الخدمة') + '</th>' +
				'<th>' + __('المصور') + '</th>' +
				'<th>' + __('الحالة') + '</th>' +
				'</tr></thead><tbody></tbody></table>');
			
			let $tbody = $table.find('tbody');
			report_data.bookings.forEach(booking => {
				let status_class = '';
				if (booking.status === 'Completed') status_class = 'text-success';
				else if (booking.status === 'Cancelled') status_class = 'text-danger';
				else if (booking.status === 'Confirmed') status_class = 'text-primary';
				
				$tbody.append('<tr>' +
					'<td><a href="#Form/Booking/' + booking.name + '">' + booking.name + '</a></td>' +
					'<td>' + booking.customer_name + '</td>' +
					'<td>' + frappe.datetime.str_to_user(booking.booking_date) + '</td>' +
					'<td>' + booking.start_time + '</td>' +
					'<td>' + booking.end_time + '</td>' +
					'<td>' + booking.service + '</td>' +
					'<td>' + booking.photographer + '</td>' +
					'<td class="' + status_class + '">' + booking.status + '</td>' +
					'</tr>');
			});
			
			$report_area.append('<h4>' + __('ملخص الحجوزات') + '</h4>');
			$report_area.append('<p>' + __('إجمالي الحجوزات') + ': ' + report_data.total_bookings + '</p>');
			
			// Add status summary
			let $status_summary = $('<div class="row status-summary"></div>');
			for (let status in report_data.status_counts) {
				let status_class = '';
				if (status === 'Completed') status_class = 'text-success';
				else if (status === 'Cancelled') status_class = 'text-danger';
				else if (status === 'Confirmed') status_class = 'text-primary';
				
				$status_summary.append('<div class="col-md-3 col-sm-6">' +
					'<div class="stat-box">' +
					'<div class="stat-value ' + status_class + '">' + report_data.status_counts[status] + '</div>' +
					'<div class="stat-label">' + status + '</div>' +
					'</div>' +
					'</div>');
			}
			$report_area.append($status_summary);
			$report_area.append($table);
			
		} else if (frm.doc.report_type === 'Photographer Performance' && report_data.photographer_performance) {
			$report_area.append('<h4>' + __('أداء المصورين') + '</h4>');
			
			// Create photographer performance table
			let $table = $('<table class="table table-bordered"><thead><tr>' +
				'<th>' + __('المصور') + '</th>' +
				'<th>' + __('عدد الحجوزات') + '</th>' +
				'<th>' + __('إجمالي الساعات') + '</th>' +
				'</tr></thead><tbody></tbody></table>');
			
			let $tbody = $table.find('tbody');
			report_data.photographer_performance.forEach(data => {
				let hours = (data.total_minutes / 60).toFixed(1);
				$tbody.append('<tr>' +
					'<td>' + data.photographer + '</td>' +
					'<td>' + data.total_bookings + '</td>' +
					'<td>' + hours + ' ' + __('ساعة') + '</td>' +
					'</tr>');
			});
			
			$report_area.append($table);
			
		} else if (frm.doc.report_type === 'Service Popularity' && report_data.service_popularity) {
			$report_area.append('<h4>' + __('شعبية الخدمات') + '</h4>');
			
			// Create service popularity table
			let $table = $('<table class="table table-bordered"><thead><tr>' +
				'<th>' + __('الخدمة') + '</th>' +
				'<th>' + __('اسم الخدمة') + '</th>' +
				'<th>' + __('الفئة') + '</th>' +
				'<th>' + __('عدد الحجوزات') + '</th>' +
				'</tr></thead><tbody></tbody></table>');
			
			let $tbody = $table.find('tbody');
			report_data.service_popularity.forEach(data => {
				$tbody.append('<tr>' +
					'<td>' + data.service + '</td>' +
					'<td>' + data.service_name + '</td>' +
					'<td>' + data.category + '</td>' +
					'<td>' + data.booking_count + '</td>' +
					'</tr>');
			});
			
			$report_area.append($table);
			
		} else if (frm.doc.report_type === 'Revenue Report' && report_data.revenue_by_service) {
			$report_area.append('<h4>' + __('تقرير الإيرادات') + '</h4>');
			$report_area.append('<p>' + __('إجمالي الإيرادات') + ': ' + report_data.total_revenue + ' ' + __('ريال') + '</p>');
			
			// Create revenue report table
			let $table = $('<table class="table table-bordered"><thead><tr>' +
				'<th>' + __('الخدمة') + '</th>' +
				'<th>' + __('عدد الحجوزات') + '</th>' +
				'<th>' + __('إجمالي الإيرادات') + '</th>' +
				'<th>' + __('النسبة من الإجمالي') + '</th>' +
				'</tr></thead><tbody></tbody></table>');
			
			let $tbody = $table.find('tbody');
			report_data.revenue_by_service.forEach(data => {
				let percentage = ((data.total_revenue / report_data.total_revenue) * 100).toFixed(1);
				$tbody.append('<tr>' +
					'<td>' + data.service + '</td>' +
					'<td>' + data.booking_count + '</td>' +
					'<td>' + data.total_revenue + ' ' + __('ريال') + '</td>' +
					'<td>' + percentage + '%</td>' +
					'</tr>');
			});
			
			$report_area.append($table);
		}
		
		// Add custom CSS
		let $style = $('<style>' +
			'.report-data-container { margin-top: 20px; }' +
			'.status-summary { margin-bottom: 20px; }' +
			'.stat-box { text-align: center; padding: 10px; background-color: #f8f8f8; border-radius: 5px; margin-bottom: 10px; }' +
			'.stat-value { font-size: 24px; font-weight: bold; }' +
			'.stat-label { font-size: 12px; }' +
			'</style>');
		
		// Append to form
		frm.get_field('summary').$wrapper.after($style);
		frm.get_field('summary').$wrapper.after($report_area);
	}
});