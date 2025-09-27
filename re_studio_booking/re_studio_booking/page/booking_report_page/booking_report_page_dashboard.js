// Copyright (c) 2023, RE Studio and contributors
// For license information, please see license.txt

frappe.provide('re_studio_booking.booking_report_dashboard');

re_studio_booking.booking_report_dashboard = {
	setup_dashboard: function(wrapper) {
		this.wrapper = wrapper;
		this.page = wrapper.page;
		
		// Set up dashboard layout
		this.make_dashboard();
		
		// Set up date range filter
		this.setup_date_filter();
		
		// Load initial data
		this.refresh_dashboard();
	},
	
	make_dashboard: function() {
		$(this.wrapper).empty();
		
		// Create dashboard container
		this.dashboard = $(`
			<div class="booking-dashboard">
				<div class="dashboard-header">
					<h3>${__('لوحة معلومات الحجوزات')}</h3>
					<div class="dashboard-filters"></div>
				</div>
				<div class="dashboard-stats"></div>
				<div class="dashboard-charts">
					<div class="chart-row">
						<div class="chart-column">
							<div class="chart-container">
								<h4>${__('حالة الحجوزات')}</h4>
								<div id="booking-status-chart"></div>
							</div>
						</div>
						<div class="chart-column">
							<div class="chart-container">
								<h4>${__('شعبية الخدمات')}</h4>
								<div id="service-popularity-chart"></div>
							</div>
						</div>
					</div>
				</div>
				<div class="dashboard-tables">
					<div class="table-row">
						<div class="table-column">
							<div class="table-container">
								<h4>${__('أداء المصورين')}</h4>
								<div id="photographer-performance-table"></div>
							</div>
						</div>
						<div class="table-column">
							<div class="table-container">
								<h4>${__('الإيرادات حسب الخدمة')}</h4>
								<div id="revenue-by-service-table"></div>
							</div>
						</div>
					</div>
				</div>
			</div>
		`).appendTo(this.wrapper);
		
		// Add custom CSS
		this.add_dashboard_styles();
	},
	
	add_dashboard_styles: function() {
		$('<style>').text(`
			.booking-dashboard {
				padding: 15px;
				background-color: #f5f7fa;
			}
			.dashboard-header {
				display: flex;
				justify-content: space-between;
				align-items: center;
				margin-bottom: 20px;
			}
			.dashboard-filters {
				display: flex;
				gap: 10px;
			}
			.dashboard-stats {
				display: flex;
				flex-wrap: wrap;
				gap: 15px;
				margin-bottom: 20px;
			}
			.stat-card {
				background-color: white;
				border-radius: 8px;
				padding: 15px;
				box-shadow: 0 1px 3px rgba(0,0,0,0.1);
				flex: 1;
				min-width: 200px;
			}
			.stat-card h4 {
				margin: 0;
				color: #8d99a6;
				font-size: 14px;
			}
			.stat-card .value {
				font-size: 24px;
				font-weight: bold;
				margin: 10px 0 0;
			}
			.chart-row, .table-row {
				display: flex;
				flex-wrap: wrap;
				gap: 20px;
				margin-bottom: 20px;
			}
			.chart-column, .table-column {
				flex: 1;
				min-width: 300px;
			}
			.chart-container, .table-container {
				background-color: white;
				border-radius: 8px;
				padding: 15px;
				box-shadow: 0 1px 3px rgba(0,0,0,0.1);
			}
			.chart-container h4, .table-container h4 {
				margin-top: 0;
				margin-bottom: 15px;
				color: #8d99a6;
			}
			#booking-status-chart, #service-popularity-chart {
				height: 250px;
			}
			.dashboard-table {
				width: 100%;
				border-collapse: collapse;
			}
			.dashboard-table th, .dashboard-table td {
				padding: 8px;
				text-align: right;
				border-bottom: 1px solid #eee;
			}
			.dashboard-table th {
				font-weight: bold;
				color: #8d99a6;
			}
			.completed { color: #28a745; }
			.confirmed { color: #007bff; }
			.cancelled { color: #dc3545; }
		`).appendTo('head');
	},
	
	setup_date_filter: function() {
		const me = this;
		const filters_container = this.dashboard.find('.dashboard-filters');
		
		// Create date range filter
		this.date_filter = $(`
			<div class="date-filter">
				<select class="form-control">
					<option value="Today">${__('اليوم')}</option>
					<option value="This Week">${__('هذا الأسبوع')}</option>
					<option value="This Month" selected>${__('هذا الشهر')}</option>
					<option value="Last Month">${__('الشهر الماضي')}</option>
					<option value="This Year">${__('هذا العام')}</option>
				</select>
			</div>
		`).appendTo(filters_container);
		
		// Add refresh button
		this.refresh_button = $(`
			<button class="btn btn-default btn-sm">
				<i class="fa fa-refresh"></i> ${__('تحديث')}
			</button>
		`).appendTo(filters_container);
		
		// Set up event handlers
		this.date_filter.find('select').on('change', function() {
			me.refresh_dashboard();
		});
		
		this.refresh_button.on('click', function() {
			me.refresh_dashboard();
		});
	},
	
	refresh_dashboard: function() {
		const me = this;
		const date_range = this.date_filter.find('select').val();
		
		// Show loading state
		this.dashboard.find('.dashboard-stats').html(`
			<div class="text-muted">${__('جاري تحميل البيانات...')}</div>
		`);
		this.dashboard.find('#booking-status-chart, #service-popularity-chart, #photographer-performance-table, #revenue-by-service-table').empty();
		
		// Fetch dashboard data
		frappe.call({
			method: 're_studio_booking.re_studio_booking.page.booking_report_page.booking_report_page_dashboard.get_dashboard_data',
			args: {
				date_range: date_range
			},
			callback: function(r) {
				if (r.message && !r.message.error) {
					me.render_dashboard(r.message, date_range);
				} else {
					frappe.msgprint(r.message.error || __('حدث خطأ أثناء تحميل البيانات'));
				}
			}
		});
	},
	
	render_dashboard: function(data, date_range) {
		// Render statistics
		this.render_stats(data);
		
		// Render charts
		this.render_booking_status_chart(data.booking_data);
		this.render_service_popularity_chart(data.service_data);
		
		// Render tables
		this.render_photographer_performance_table(data.photographer_data);
		this.render_revenue_table(data.revenue_data);
	},
	
	render_stats: function(data) {
		const booking_data = data.booking_data;
		const revenue_data = data.revenue_data;
		
		const stats_container = this.dashboard.find('.dashboard-stats');
		stats_container.empty();
		
		// Total bookings
		$(`
			<div class="stat-card">
				<h4>${__('إجمالي الحجوزات')}</h4>
				<div class="value">${booking_data.total_bookings}</div>
			</div>
		`).appendTo(stats_container);
		
		// Completed bookings
		$(`
			<div class="stat-card">
				<h4>${__('الحجوزات المكتملة')}</h4>
				<div class="value completed">${booking_data.status_counts.Completed || 0}</div>
			</div>
		`).appendTo(stats_container);
		
		// Confirmed bookings
		$(`
			<div class="stat-card">
				<h4>${__('الحجوزات المؤكدة')}</h4>
				<div class="value confirmed">${booking_data.status_counts.Confirmed || 0}</div>
			</div>
		`).appendTo(stats_container);
		
		// Cancelled bookings
		$(`
			<div class="stat-card">
				<h4>${__('الحجوزات الملغاة')}</h4>
				<div class="value cancelled">${booking_data.status_counts.Cancelled || 0}</div>
			</div>
		`).appendTo(stats_container);
		
		// Total revenue
		$(`
			<div class="stat-card">
				<h4>${__('إجمالي الإيرادات')}</h4>
				<div class="value">${revenue_data.total_revenue || 0} ${__('ريال')}</div>
			</div>
		`).appendTo(stats_container);
	},
	
	render_booking_status_chart: function(booking_data) {
		const status_counts = booking_data.status_counts;
		const labels = Object.keys(status_counts);
		const values = Object.values(status_counts);
		
		// Define colors for each status
		const colors = {
			'Completed': '#28a745',
			'Confirmed': '#007bff',
			'Cancelled': '#dc3545',
			'Draft': '#6c757d'
		};
		
		// Create color array based on labels
		const chart_colors = labels.map(label => colors[label] || '#6c757d');
		
		// Create pie chart
		const chart = new frappe.Chart("#booking-status-chart", {
			data: {
				labels: labels,
				datasets: [{
					values: values
				}]
			},
			type: 'pie',
			colors: chart_colors,
			height: 250,
			toolTip: {
				formatTooltipY: d => d + ' ' + __('حجز')
			}
		});
	},
	
	render_service_popularity_chart: function(service_data) {
		if (!service_data || !service_data.length) {
			$("#service-popularity-chart").html(`<div class="text-muted">${__('لا توجد بيانات متاحة')}</div>`);
			return;
		}
		
		// Extract data for chart
		const labels = service_data.map(item => item.service_name || item.service);
		const values = service_data.map(item => item.booking_count);
		
		// Create bar chart
		const chart = new frappe.Chart("#service-popularity-chart", {
			data: {
				labels: labels,
				datasets: [{
					name: __('عدد الحجوزات'),
					values: values
				}]
			},
			type: 'bar',
			height: 250,
			colors: ['#5e64ff'],
			barOptions: {
				height: 20,
				depth: 2
			},
			toolTip: {
				formatTooltipY: d => d + ' ' + __('حجز')
			},
			isNavigable: true
		});
	},
	
	render_photographer_performance_table: function(photographer_data) {
		const container = $("#photographer-performance-table");
		container.empty();
		
		if (!photographer_data || !photographer_data.length) {
			container.html(`<div class="text-muted">${__('لا توجد بيانات متاحة')}</div>`);
			return;
		}
		
		// Create table
		const table = $(`
			<table class="dashboard-table">
				<thead>
					<tr>
						<th>${__('المصور')}</th>
						<th>${__('عدد الحجوزات')}</th>
						<th>${__('إجمالي الساعات')}</th>
					</tr>
				</thead>
				<tbody></tbody>
			</table>
		`).appendTo(container);
		
		// Add rows
		photographer_data.forEach(item => {
			const hours = (item.total_minutes / 60).toFixed(1);
			$(`
				<tr>
					<td>${item.photographer}</td>
					<td>${item.total_bookings}</td>
					<td>${hours} ${__('ساعة')}</td>
				</tr>
			`).appendTo(table.find('tbody'));
		});
	},
	
	render_revenue_table: function(revenue_data) {
		const container = $("#revenue-by-service-table");
		container.empty();
		
		if (!revenue_data || !revenue_data.revenue_by_service || !revenue_data.revenue_by_service.length) {
			container.html(`<div class="text-muted">${__('لا توجد بيانات متاحة')}</div>`);
			return;
		}
		
		// Create table
		const table = $(`
			<table class="dashboard-table">
				<thead>
					<tr>
						<th>${__('الخدمة')}</th>
						<th>${__('عدد الحجوزات')}</th>
						<th>${__('الإيرادات')}</th>
						<th>${__('النسبة')}</th>
					</tr>
				</thead>
				<tbody></tbody>
			</table>
		`).appendTo(container);
		
		// Add rows
		revenue_data.revenue_by_service.forEach(item => {
			const percentage = ((item.total_revenue / revenue_data.total_revenue) * 100).toFixed(1);
			$(`
				<tr>
					<td>${item.service}</td>
					<td>${item.booking_count}</td>
					<td>${item.total_revenue} ${__('ريال')}</td>
					<td>${percentage}%</td>
				</tr>
			`).appendTo(table.find('tbody'));
		});
	}
};

frappe.pages['booking-report-page'].on_page_load = function(wrapper) {
	let page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('لوحة معلومات الحجوزات'),
		single_column: true
	});
	
	// Add menu items
	page.add_menu_item(__('إنشاء تقرير جديد'), function() {
		frappe.new_doc('Booking Report');
	});
	
	page.add_menu_item(__('عرض قائمة التقارير'), function() {
		frappe.set_route('List', 'Booking Report');
	});
	
	// Initialize dashboard
	re_studio_booking.booking_report_dashboard.setup_dashboard(wrapper);
	
	// Save reference to page
	wrapper.page.dashboard = re_studio_booking.booking_report_dashboard;
};

frappe.pages['booking-report-page'].on_page_show = function(wrapper) {
	// Refresh dashboard when page is shown
	if (wrapper.page.dashboard) {
		wrapper.page.dashboard.refresh_dashboard();
	}
};