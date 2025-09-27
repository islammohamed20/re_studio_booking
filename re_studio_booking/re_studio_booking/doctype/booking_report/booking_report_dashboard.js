// Copyright (c) 2023, MASAR TEAM and contributors
// For license information, please see license.txt

frappe.dashboard.set_chart_options = function(options, chart_options) {
	// Set chart options for booking report dashboard
	options.chart_options = chart_options;
};

frappe.provide('re_studio_booking.booking_report');

re_studio_booking.booking_report.dashboard = {
	setup_dashboard: function(wrapper) {
		let me = this;
		this.wrapper = $(wrapper);
		
		// Create dashboard layout
		this.wrapper.empty();
		this.wrapper.append(`
			<div class="dashboard-header">
				<h3>${__('لوحة معلومات الحجوزات')}</h3>
				<div class="dashboard-controls">
					<select class="form-control date-range-filter">
						<option value="Today">${__('اليوم')}</option>
						<option value="This Week">${__('هذا الأسبوع')}</option>
						<option value="This Month" selected>${__('هذا الشهر')}</option>
						<option value="Last Month">${__('الشهر الماضي')}</option>
						<option value="This Year">${__('هذا العام')}</option>
					</select>
					<button class="btn btn-sm btn-default refresh-dashboard">
						${__('تحديث')}
					</button>
				</div>
			</div>
			<div class="dashboard-stats row"></div>
			<div class="dashboard-charts row">
				<div class="col-md-6">
					<div class="chart-container">
						<h4>${__('حالة الحجوزات')}</h4>
						<div class="booking-status-chart"></div>
					</div>
				</div>
				<div class="col-md-6">
					<div class="chart-container">
						<h4>${__('شعبية الخدمات')}</h4>
						<div class="service-popularity-chart"></div>
					</div>
				</div>
			</div>
			<div class="dashboard-tables row">
				<div class="col-md-6">
					<div class="table-container">
						<h4>${__('أداء المصورين')}</h4>
						<div class="photographer-performance-table"></div>
					</div>
				</div>
				<div class="col-md-6">
					<div class="table-container">
						<h4>${__('الإيرادات حسب الخدمة')}</h4>
						<div class="revenue-by-service-table"></div>
					</div>
				</div>
			</div>
		`);
		
		// Add custom CSS
		this.wrapper.append(`
			<style>
				.dashboard-header {
					display: flex;
					justify-content: space-between;
					align-items: center;
					margin-bottom: 20px;
				}
				.dashboard-controls {
					display: flex;
					gap: 10px;
				}
				.dashboard-stats {
					margin-bottom: 20px;
				}
				.stat-box {
					background-color: #f8f8f8;
					border-radius: 5px;
					padding: 15px;
					text-align: center;
					margin-bottom: 15px;
				}
				.stat-value {
					font-size: 24px;
					font-weight: bold;
				}
				.stat-label {
					font-size: 12px;
					color: #888;
				}
				.chart-container, .table-container {
					background-color: #fff;
					border: 1px solid #e5e5e5;
					border-radius: 5px;
					padding: 15px;
					margin-bottom: 20px;
				}
				.chart-container h4, .table-container h4 {
					margin-top: 0;
					margin-bottom: 15px;
					padding-bottom: 10px;
					border-bottom: 1px solid #eee;
				}
			</style>
		`);
		
		// Set up event handlers
		this.wrapper.find('.date-range-filter').on('change', function() {
			me.refresh_dashboard();
		});
		
		this.wrapper.find('.refresh-dashboard').on('click', function() {
			me.refresh_dashboard();
		});
		
		// Initial load
		this.refresh_dashboard();
	},
	
	refresh_dashboard: function() {
		let me = this;
		let date_range = this.wrapper.find('.date-range-filter').val();
		
		// Show loading state
		this.wrapper.find('.dashboard-stats').html('<div class="text-center">' + __('جاري تحميل البيانات...') + '</div>');
		this.wrapper.find('.booking-status-chart, .service-popularity-chart, .photographer-performance-table, .revenue-by-service-table').empty();
		
		// Fetch dashboard data
		frappe.call({
			method: 're_studio_booking.re_studio_booking.doctype.booking_report.booking_report_dashboard.get_dashboard_data',
			args: {
				date_range: date_range
			},
			callback: function(r) {
				if (r.message) {
					me.render_dashboard(r.message);
				}
			}
		});
	},
	
	render_dashboard: function(data) {
		// Render stats
		let $stats = this.wrapper.find('.dashboard-stats');
		$stats.empty();
		
		// Add booking stats
		let stats = [
			{ label: __('إجمالي الحجوزات'), value: data.total_bookings, color: 'blue' },
			{ label: __('الحجوزات المكتملة'), value: data.status_counts.Completed || 0, color: 'green' },
			{ label: __('الحجوزات المؤكدة'), value: data.status_counts.Confirmed || 0, color: 'orange' },
			{ label: __('الحجوزات الملغاة'), value: data.status_counts.Cancelled || 0, color: 'red' },
			{ label: __('إجمالي الإيرادات'), value: data.total_revenue + ' ' + __('ريال'), color: 'purple' }
		];
		
		stats.forEach(stat => {
			$stats.append(`
				<div class="col-md-3 col-sm-6">
					<div class="stat-box">
						<div class="stat-value text-${stat.color}">${stat.value}</div>
						<div class="stat-label">${stat.label}</div>
					</div>
				</div>
			`);
		});
		
		// Render booking status chart
		if (data.status_counts) {
			let status_labels = Object.keys(data.status_counts);
			let status_values = Object.values(data.status_counts);
			
			if (status_labels.length) {
				new frappe.Chart(this.wrapper.find('.booking-status-chart')[0], {
					data: {
						labels: status_labels,
						datasets: [{
							name: __('عدد الحجوزات'),
							values: status_values
						}]
					},
					type: 'pie',
					height: 250,
					colors: ['#5e64ff', '#28a745', '#ffc107', '#dc3545', '#6c757d']
				});
			} else {
				this.wrapper.find('.booking-status-chart').html('<div class="text-center text-muted">' + __('لا توجد بيانات') + '</div>');
			}
		}
		
		// Render service popularity chart
		if (data.service_popularity && data.service_popularity.length) {
			let service_labels = data.service_popularity.map(item => item.service_name || item.service);
			let service_values = data.service_popularity.map(item => item.booking_count);
			
			new frappe.Chart(this.wrapper.find('.service-popularity-chart')[0], {
				data: {
					labels: service_labels.slice(0, 5), // Show top 5 services
					datasets: [{
						name: __('عدد الحجوزات'),
						values: service_values.slice(0, 5)
					}]
				},
				type: 'bar',
				height: 250,
				colors: ['#5e64ff']
			});
		} else {
			this.wrapper.find('.service-popularity-chart').html('<div class="text-center text-muted">' + __('لا توجد بيانات') + '</div>');
		}
		
		// Render photographer performance table
		if (data.photographer_performance && data.photographer_performance.length) {
			let $table = $('<table class="table table-bordered table-hover"><thead><tr>' +
				'<th>' + __('المصور') + '</th>' +
				'<th>' + __('عدد الحجوزات') + '</th>' +
				'<th>' + __('إجمالي الساعات') + '</th>' +
				'</tr></thead><tbody></tbody></table>');
			
			let $tbody = $table.find('tbody');
			data.photographer_performance.forEach(item => {
				let hours = (item.total_minutes / 60).toFixed(1);
				$tbody.append('<tr>' +
					'<td>' + item.photographer + '</td>' +
					'<td>' + item.total_bookings + '</td>' +
					'<td>' + hours + ' ' + __('ساعة') + '</td>' +
					'</tr>');
			});
			
			this.wrapper.find('.photographer-performance-table').html($table);
		} else {
			this.wrapper.find('.photographer-performance-table').html('<div class="text-center text-muted">' + __('لا توجد بيانات') + '</div>');
		}
		
		// Render revenue by service table
		if (data.revenue_by_service && data.revenue_by_service.length) {
			let $table = $('<table class="table table-bordered table-hover"><thead><tr>' +
				'<th>' + __('الخدمة') + '</th>' +
				'<th>' + __('عدد الحجوزات') + '</th>' +
				'<th>' + __('الإيرادات') + '</th>' +
				'<th>' + __('النسبة') + '</th>' +
				'</tr></thead><tbody></tbody></table>');
			
			let $tbody = $table.find('tbody');
			data.revenue_by_service.forEach(item => {
				let percentage = ((item.total_revenue / data.total_revenue) * 100).toFixed(1);
				$tbody.append('<tr>' +
					'<td>' + item.service + '</td>' +
					'<td>' + item.booking_count + '</td>' +
					'<td>' + item.total_revenue + ' ' + __('ريال') + '</td>' +
					'<td>' + percentage + '%</td>' +
					'</tr>');
			});
			
			this.wrapper.find('.revenue-by-service-table').html($table);
		} else {
			this.wrapper.find('.revenue-by-service-table').html('<div class="text-center text-muted">' + __('لا توجد بيانات') + '</div>');
		}
	}
};

frappe.pages['booking-report-dashboard'].on_page_load = function(wrapper) {
	let page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('لوحة معلومات الحجوزات'),
		single_column: true
	});
	
	// Add page actions
	page.add_menu_item(__('إنشاء تقرير جديد'), function() {
		frappe.new_doc('Booking Report');
	});
	
	page.add_menu_item(__('عرض قائمة التقارير'), function() {
		frappe.set_route('List', 'Booking Report');
	});
	
	// Initialize dashboard
	re_studio_booking.booking_report.dashboard.setup_dashboard(page.body);
};

frappe.pages['booking-report-dashboard'].on_page_show = function() {
	// Refresh dashboard when page is shown
	re_studio_booking.booking_report.dashboard.refresh_dashboard();
};