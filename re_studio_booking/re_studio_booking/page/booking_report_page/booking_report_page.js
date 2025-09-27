// Copyright (c) 2023, MASAR TEAM and contributors
// For license information, please see license.txt

frappe.pages['booking-report-page'].on_page_load = function(wrapper) {
	let page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('تقارير الحجوزات'),
		single_column: true
	});
	
	// Initialize page
	page.report_view = new BookingReportView(page);
};

class BookingReportView {
	constructor(page) {
		this.page = page;
		this.make();
		this.setup_filters();
		this.setup_actions();
	}
	
	make() {
		let me = this;
		
		// Create page layout
		$(this.page.body).html(`
			<div class="booking-report-page">
				<div class="report-filters"></div>
				<div class="report-content">
					<div class="report-summary"></div>
					<div class="report-visualization"></div>
					<div class="report-details"></div>
				</div>
			</div>
		`);
		
		// Add custom CSS
		$(this.page.body).append(`
			<style>
				.booking-report-page {
					padding: 15px 0;
				}
				.report-filters {
					margin-bottom: 20px;
					padding: 15px;
					background-color: #f8f8f8;
					border-radius: 5px;
				}
				.filter-section {
					display: flex;
					flex-wrap: wrap;
					gap: 15px;
					margin-bottom: 15px;
				}
				.filter-field {
					width: 200px;
				}
				.filter-buttons {
					display: flex;
					gap: 10px;
				}
				.report-summary {
					display: flex;
					flex-wrap: wrap;
					gap: 15px;
					margin-bottom: 20px;
				}
				.summary-box {
					background-color: #fff;
					border: 1px solid #e5e5e5;
					border-radius: 5px;
					padding: 15px;
					width: 200px;
					text-align: center;
				}
				.summary-value {
					font-size: 24px;
					font-weight: bold;
					margin-bottom: 5px;
				}
				.summary-label {
					font-size: 12px;
					color: #888;
				}
				.report-visualization {
					display: flex;
					flex-wrap: wrap;
					gap: 20px;
					margin-bottom: 20px;
				}
				.chart-container {
					background-color: #fff;
					border: 1px solid #e5e5e5;
					border-radius: 5px;
					padding: 15px;
					width: calc(50% - 10px);
					min-width: 400px;
				}
				.chart-container h4 {
					margin-top: 0;
					margin-bottom: 15px;
					padding-bottom: 10px;
					border-bottom: 1px solid #eee;
				}
				.report-details {
					background-color: #fff;
					border: 1px solid #e5e5e5;
					border-radius: 5px;
					padding: 15px;
				}
				.report-details h4 {
					margin-top: 0;
					margin-bottom: 15px;
					padding-bottom: 10px;
					border-bottom: 1px solid #eee;
				}
				.status-badge {
					display: inline-block;
					padding: 3px 8px;
					border-radius: 10px;
					font-size: 12px;
					color: #fff;
				}
				.status-Draft { background-color: #6c757d; }
				.status-Confirmed { background-color: #007bff; }
				.status-Completed { background-color: #28a745; }
				.status-Cancelled { background-color: #dc3545; }
			</style>
		`);
	}
	
	setup_filters() {
		let me = this;
		let $filters = $(this.page.body).find('.report-filters');
		
		// Create filter layout
		$filters.html(`
			<div class="filter-section">
				<div class="filter-field report-type-filter"></div>
				<div class="filter-field date-range-filter"></div>
				<div class="filter-field start-date-filter" style="display: none;"></div>
				<div class="filter-field end-date-filter" style="display: none;"></div>
				<div class="filter-field status-filter" style="display: none;"></div>
				<div class="filter-field photographer-filter" style="display: none;"></div>
			</div>
			<div class="filter-buttons">
				<button class="btn btn-primary generate-report">${__('إنشاء التقرير')}</button>
				<button class="btn btn-default reset-filters">${__('إعادة تعيين')}</button>
				<div class="dropdown">
					<button class="btn btn-default dropdown-toggle" type="button" data-toggle="dropdown">
						${__('تقارير سريعة')} <span class="caret"></span>
					</button>
					<ul class="dropdown-menu">
						<li><a href="#" class="quick-report" data-report="today">${__('تقرير اليوم')}</a></li>
						<li><a href="#" class="quick-report" data-report="week">${__('تقرير هذا الأسبوع')}</a></li>
						<li><a href="#" class="quick-report" data-report="month">${__('تقرير هذا الشهر')}</a></li>
						<li class="divider"></li>
						<li><a href="#" class="quick-report" data-report="photographer">${__('أداء المصورين')}</a></li>
						<li><a href="#" class="quick-report" data-report="service">${__('شعبية الخدمات')}</a></li>
						<li><a href="#" class="quick-report" data-report="revenue">${__('تقرير الإيرادات')}</a></li>
					</ul>
				</div>
			</div>
		`);
		
		// Create report type filter
		this.report_type_field = frappe.ui.form.make_control({
			parent: $filters.find('.report-type-filter'),
			df: {
				fieldtype: 'Select',
				options: 'Booking Summary\nPhotographer Performance\nService Popularity\nRevenue Report',
				label: __('نوع التقرير'),
				fieldname: 'report_type',
				reqd: 1
			},
			render_input: true
		});
		
		// Create date range filter
		this.date_range_field = frappe.ui.form.make_control({
			parent: $filters.find('.date-range-filter'),
			df: {
				fieldtype: 'Select',
				options: 'Today\nThis Week\nThis Month\nLast Month\nThis Year\nCustom',
				label: __('النطاق الزمني'),
				fieldname: 'date_range',
				reqd: 1
			},
			render_input: true
		});
		
		// Create start date filter
		this.start_date_field = frappe.ui.form.make_control({
			parent: $filters.find('.start-date-filter'),
			df: {
				fieldtype: 'Date',
				label: __('تاريخ البدء'),
				fieldname: 'start_date',
				reqd: 1
			},
			render_input: true
		});
		
		// Create end date filter
		this.end_date_field = frappe.ui.form.make_control({
			parent: $filters.find('.end-date-filter'),
			df: {
				fieldtype: 'Date',
				label: __('تاريخ الانتهاء'),
				fieldname: 'end_date',
				reqd: 1
			},
			render_input: true
		});
		
		// Create status filter
		this.status_field = frappe.ui.form.make_control({
			parent: $filters.find('.status-filter'),
			df: {
				fieldtype: 'Select',
				options: 'All\nDraft\nConfirmed\nCompleted\nCancelled',
				label: __('حالة الحجز'),
				fieldname: 'status'
			},
			render_input: true
		});
		
		// Create photographer filter
		this.photographer_field = frappe.ui.form.make_control({
			parent: $filters.find('.photographer-filter'),
			df: {
				fieldtype: 'Link',
				options: 'Photographer',
				label: __('المصور'),
				fieldname: 'photographer'
			},
			render_input: true
		});
		
		// Set default values
		this.report_type_field.set_value('Booking Summary');
		this.date_range_field.set_value('This Month');
		this.status_field.set_value('All');
		
		// Set up event handlers
		this.report_type_field.$input.on('change', function() {
			me.toggle_filters();
		});
		
		this.date_range_field.$input.on('change', function() {
			me.toggle_date_filters();
		});
		
		$filters.find('.generate-report').on('click', function() {
			me.generate_report();
		});
		
		$filters.find('.reset-filters').on('click', function() {
			me.reset_filters();
		});
		
		$filters.find('.quick-report').on('click', function() {
			let report_type = $(this).data('report');
			me.set_quick_report(report_type);
			return false;
		});
		
		// Initial toggle
		this.toggle_filters();
		this.toggle_date_filters();
	}
	
	toggle_filters() {
		let report_type = this.report_type_field.get_value();
		
		// Show/hide status filter
		if (report_type === 'Booking Summary') {
			$(this.page.body).find('.status-filter').show();
		} else {
			$(this.page.body).find('.status-filter').hide();
		}
		
		// Show/hide photographer filter
		if (report_type === 'Photographer Performance') {
			$(this.page.body).find('.photographer-filter').show();
		} else {
			$(this.page.body).find('.photographer-filter').hide();
		}
	}
	
	toggle_date_filters() {
		let date_range = this.date_range_field.get_value();
		
		// Show/hide custom date filters
		if (date_range === 'Custom') {
			$(this.page.body).find('.start-date-filter, .end-date-filter').show();
		} else {
			$(this.page.body).find('.start-date-filter, .end-date-filter').hide();
		}
	}
	
	reset_filters() {
		this.report_type_field.set_value('Booking Summary');
		this.date_range_field.set_value('This Month');
		this.status_field.set_value('All');
		this.photographer_field.set_value('');
		this.start_date_field.set_value('');
		this.end_date_field.set_value('');
		
		// Clear report content
		$(this.page.body).find('.report-summary, .report-visualization, .report-details').empty();
	}
	
	set_quick_report(report_type) {
		// Set filters based on quick report type
		if (report_type === 'today') {
			this.report_type_field.set_value('Booking Summary');
			this.date_range_field.set_value('Today');
		} else if (report_type === 'week') {
			this.report_type_field.set_value('Booking Summary');
			this.date_range_field.set_value('This Week');
		} else if (report_type === 'month') {
			this.report_type_field.set_value('Booking Summary');
			this.date_range_field.set_value('This Month');
		} else if (report_type === 'photographer') {
			this.report_type_field.set_value('Photographer Performance');
			this.date_range_field.set_value('This Month');
		} else if (report_type === 'service') {
			this.report_type_field.set_value('Service Popularity');
			this.date_range_field.set_value('This Month');
		} else if (report_type === 'revenue') {
			this.report_type_field.set_value('Revenue Report');
			this.date_range_field.set_value('This Month');
		}
		
		// Generate report
		this.generate_report();
	}
	
	setup_actions() {
		let me = this;
		
		// Add page actions
		this.page.add_menu_item(__('إنشاء تقرير جديد'), function() {
			frappe.new_doc('Booking Report');
		});
		
		this.page.add_menu_item(__('عرض قائمة التقارير'), function() {
			frappe.set_route('List', 'Booking Report');
		});
		
		this.page.add_menu_item(__('تصدير إلى Excel'), function() {
			me.export_report();
		});
		
		this.page.add_menu_item(__('طباعة التقرير'), function() {
			me.print_report();
		});
	}
	
	generate_report() {
		let me = this;
		let filters = this.get_filters();
		
		// Validate filters
		if (!this.validate_filters(filters)) {
			return;
		}
		
		// Show loading state
		$(this.page.body).find('.report-summary, .report-visualization, .report-details').empty();
		$(this.page.body).find('.report-content').html('<div class="text-center" style="padding: 30px;">' + __('جاري تحميل البيانات...') + '</div>');
		
		// Call server to generate report
		frappe.call({
			method: 're_studio_booking.re_studio_booking.doctype.booking_report.booking_report_page.generate_report',
			args: {
				filters: filters
			},
			callback: function(r) {
				if (r.message) {
					// Clear loading state
					$(me.page.body).find('.report-content').empty();
					
					// Render report
					me.render_report(r.message);
				}
			}
		});
	}
	
	get_filters() {
		let filters = {
			report_type: this.report_type_field.get_value(),
			date_range: this.date_range_field.get_value()
		};
		
		// Add custom date range if selected
		if (filters.date_range === 'Custom') {
			filters.start_date = this.start_date_field.get_value();
			filters.end_date = this.end_date_field.get_value();
		}
		
		// Add status filter if applicable
		if (filters.report_type === 'Booking Summary' && this.status_field.get_value() !== 'All') {
			filters.status = this.status_field.get_value();
		}
		
		// Add photographer filter if applicable
		if (filters.report_type === 'Photographer Performance' && this.photographer_field.get_value()) {
			filters.photographer = this.photographer_field.get_value();
		}
		
		return filters;
	}
	
	validate_filters(filters) {
		// Validate required fields
		if (!filters.report_type) {
			frappe.throw(__('يرجى تحديد نوع التقرير'));
			return false;
		}
		
		if (!filters.date_range) {
			frappe.throw(__('يرجى تحديد النطاق الزمني'));
			return false;
		}
		
		// Validate custom date range
		if (filters.date_range === 'Custom') {
			if (!filters.start_date) {
				frappe.throw(__('يرجى تحديد تاريخ البدء'));
				return false;
			}
			
			if (!filters.end_date) {
				frappe.throw(__('يرجى تحديد تاريخ الانتهاء'));
				return false;
			}
			
			if (frappe.datetime.str_to_obj(filters.end_date) < frappe.datetime.str_to_obj(filters.start_date)) {
				frappe.throw(__('يجب أن يكون تاريخ الانتهاء بعد أو يساوي تاريخ البدء'));
				return false;
			}
		}
		
		return true;
	}
	
	render_report(data) {
		let me = this;
		let report_type = this.report_type_field.get_value();
		
		// Render report based on type
		if (report_type === 'Booking Summary') {
			this.render_booking_summary(data);
		} else if (report_type === 'Photographer Performance') {
			this.render_photographer_performance(data);
		} else if (report_type === 'Service Popularity') {
			this.render_service_popularity(data);
		} else if (report_type === 'Revenue Report') {
			this.render_revenue_report(data);
		}
		
		// Store report data for export
		this.report_data = data;
	}
	
	render_booking_summary(data) {
		let $content = $(this.page.body).find('.report-content');
		
		// Render summary
		let $summary = $('<div class="report-summary"></div>');
		$summary.append(`
			<div class="summary-box">
				<div class="summary-value">${data.total_bookings}</div>
				<div class="summary-label">${__('إجمالي الحجوزات')}</div>
			</div>
		`);
		
		// Add status summary
		for (let status in data.status_counts) {
			let status_class = '';
			if (status === 'Completed') status_class = 'text-success';
			else if (status === 'Cancelled') status_class = 'text-danger';
			else if (status === 'Confirmed') status_class = 'text-primary';
			
			$summary.append(`
				<div class="summary-box">
					<div class="summary-value ${status_class}">${data.status_counts[status]}</div>
					<div class="summary-label">${status}</div>
				</div>
			`);
		}
		
		// Render visualization
		let $visualization = $('<div class="report-visualization"></div>');
		
		// Add status chart
		let $status_chart = $('<div class="chart-container"><h4>' + __('حالة الحجوزات') + '</h4><div class="status-chart"></div></div>');
		$visualization.append($status_chart);
		
		// Add booking date chart
		let $date_chart = $('<div class="chart-container"><h4>' + __('الحجوزات حسب التاريخ') + '</h4><div class="date-chart"></div></div>');
		$visualization.append($date_chart);
		
		// Render details
		let $details = $('<div class="report-details"><h4>' + __('تفاصيل الحجوزات') + '</h4></div>');
		
		// Create bookings table
		let $table = $('<table class="table table-bordered table-hover"><thead><tr>' +
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
		data.bookings.forEach(booking => {
			$tbody.append('<tr>' +
				'<td><a href="#Form/Booking/' + booking.name + '">' + booking.name + '</a></td>' +
				'<td>' + booking.customer_name + '</td>' +
				'<td>' + frappe.datetime.str_to_user(booking.booking_date) + '</td>' +
				'<td>' + booking.start_time + '</td>' +
				'<td>' + booking.end_time + '</td>' +
				'<td>' + booking.service + '</td>' +
				'<td>' + booking.photographer + '</td>' +
				'<td><span class="status-badge status-' + booking.status + '">' + booking.status + '</span></td>' +
				'</tr>');
		});
		
		$details.append($table);
		
		// Append to content
		$content.append($summary);
		$content.append($visualization);
		$content.append($details);
		
		// Initialize charts
		setTimeout(() => {
			// Status chart
			if (Object.keys(data.status_counts).length) {
				new frappe.Chart($status_chart.find('.status-chart')[0], {
					data: {
						labels: Object.keys(data.status_counts),
						datasets: [{
							name: __('عدد الحجوزات'),
							values: Object.values(data.status_counts)
						}]
					},
					type: 'pie',
					height: 250,
					colors: ['#5e64ff', '#28a745', '#ffc107', '#dc3545', '#6c757d']
				});
			}
			
			// Date chart
			if (data.bookings_by_date && Object.keys(data.bookings_by_date).length) {
				new frappe.Chart($date_chart.find('.date-chart')[0], {
					data: {
						labels: Object.keys(data.bookings_by_date),
						datasets: [{
							name: __('عدد الحجوزات'),
							values: Object.values(data.bookings_by_date)
						}]
					},
					type: 'bar',
					height: 250,
					colors: ['#5e64ff']
				});
			}
		}, 300);
	}
	
	render_photographer_performance(data) {
		let $content = $(this.page.body).find('.report-content');
		
		// Render summary
		let $summary = $('<div class="report-summary"></div>');
		$summary.append(`
			<div class="summary-box">
				<div class="summary-value">${data.photographer_performance.length}</div>
				<div class="summary-label">${__('عدد المصورين')}</div>
			</div>
			<div class="summary-box">
				<div class="summary-value">${data.total_bookings}</div>
				<div class="summary-label">${__('إجمالي الحجوزات')}</div>
			</div>
			<div class="summary-box">
				<div class="summary-value">${(data.total_hours).toFixed(1)}</div>
				<div class="summary-label">${__('إجمالي الساعات')}</div>
			</div>
		`);
		
		// Render visualization
		let $visualization = $('<div class="report-visualization"></div>');
		
		// Add bookings chart
		let $bookings_chart = $('<div class="chart-container"><h4>' + __('عدد الحجوزات لكل مصور') + '</h4><div class="bookings-chart"></div></div>');
		$visualization.append($bookings_chart);
		
		// Add hours chart
		let $hours_chart = $('<div class="chart-container"><h4>' + __('عدد الساعات لكل مصور') + '</h4><div class="hours-chart"></div></div>');
		$visualization.append($hours_chart);
		
		// Render details
		let $details = $('<div class="report-details"><h4>' + __('تفاصيل أداء المصورين') + '</h4></div>');
		
		// Create photographer performance table
		let $table = $('<table class="table table-bordered table-hover"><thead><tr>' +
			'<th>' + __('المصور') + '</th>' +
			'<th>' + __('عدد الحجوزات') + '</th>' +
			'<th>' + __('إجمالي الساعات') + '</th>' +
			'<th>' + __('متوسط مدة الجلسة') + '</th>' +
			'</tr></thead><tbody></tbody></table>');
		
		let $tbody = $table.find('tbody');
		data.photographer_performance.forEach(item => {
			let hours = (item.total_minutes / 60).toFixed(1);
			let avg_session = (item.total_minutes / 60 / item.total_bookings).toFixed(1);
			$tbody.append('<tr>' +
				'<td>' + item.photographer + '</td>' +
				'<td>' + item.total_bookings + '</td>' +
				'<td>' + hours + ' ' + __('ساعة') + '</td>' +
				'<td>' + avg_session + ' ' + __('ساعة') + '</td>' +
				'</tr>');
		});
		
		$details.append($table);
		
		// Append to content
		$content.append($summary);
		$content.append($visualization);
		$content.append($details);
		
		// Initialize charts
		setTimeout(() => {
			// Bookings chart
			if (data.photographer_performance.length) {
				new frappe.Chart($bookings_chart.find('.bookings-chart')[0], {
					data: {
						labels: data.photographer_performance.map(item => item.photographer),
						datasets: [{
							name: __('عدد الحجوزات'),
							values: data.photographer_performance.map(item => item.total_bookings)
						}]
					},
					type: 'bar',
					height: 250,
					colors: ['#5e64ff']
				});
			}
			
			// Hours chart
			if (data.photographer_performance.length) {
				new frappe.Chart($hours_chart.find('.hours-chart')[0], {
					data: {
						labels: data.photographer_performance.map(item => item.photographer),
						datasets: [{
							name: __('عدد الساعات'),
							values: data.photographer_performance.map(item => item.total_minutes / 60)
						}]
					},
					type: 'bar',
					height: 250,
					colors: ['#28a745']
				});
			}
		}, 300);
	}
	
	render_service_popularity(data) {
		let $content = $(this.page.body).find('.report-content');
		
		// Render summary
		let $summary = $('<div class="report-summary"></div>');
		$summary.append(`
			<div class="summary-box">
				<div class="summary-value">${data.service_popularity.length}</div>
				<div class="summary-label">${__('عدد الخدمات')}</div>
			</div>
			<div class="summary-box">
				<div class="summary-value">${data.total_bookings}</div>
				<div class="summary-label">${__('إجمالي الحجوزات')}</div>
			</div>
		`);
		
		// Add top services
		if (data.service_popularity.length > 0) {
			$summary.append(`
				<div class="summary-box">
					<div class="summary-value">${data.service_popularity[0].service_name || data.service_popularity[0].service}</div>
					<div class="summary-label">${__('الخدمة الأكثر طلباً')}</div>
				</div>
			`);
		}
		
		// Render visualization
		let $visualization = $('<div class="report-visualization"></div>');
		
		// Add service popularity chart
		let $popularity_chart = $('<div class="chart-container"><h4>' + __('شعبية الخدمات') + '</h4><div class="popularity-chart"></div></div>');
		$visualization.append($popularity_chart);
		
		// Add category chart
		let $category_chart = $('<div class="chart-container"><h4>' + __('الحجوزات حسب الفئة') + '</h4><div class="category-chart"></div></div>');
		$visualization.append($category_chart);
		
		// Render details
		let $details = $('<div class="report-details"><h4>' + __('تفاصيل شعبية الخدمات') + '</h4></div>');
		
		// Create service popularity table
		let $table = $('<table class="table table-bordered table-hover"><thead><tr>' +
			'<th>' + __('الخدمة') + '</th>' +
			'<th>' + __('اسم الخدمة') + '</th>' +
			'<th>' + __('الفئة') + '</th>' +
			'<th>' + __('عدد الحجوزات') + '</th>' +
			'<th>' + __('النسبة من الإجمالي') + '</th>' +
			'</tr></thead><tbody></tbody></table>');
		
		let $tbody = $table.find('tbody');
		data.service_popularity.forEach(item => {
			let percentage = ((item.booking_count / data.total_bookings) * 100).toFixed(1);
			$tbody.append('<tr>' +
				'<td>' + item.service + '</td>' +
				'<td>' + (item.service_name || '') + '</td>' +
				'<td>' + (item.category || '') + '</td>' +
				'<td>' + item.booking_count + '</td>' +
				'<td>' + percentage + '%</td>' +
				'</tr>');
		});
		
		$details.append($table);
		
		// Append to content
		$content.append($summary);
		$content.append($visualization);
		$content.append($details);
		
		// Initialize charts
		setTimeout(() => {
			// Service popularity chart
			if (data.service_popularity.length) {
				// Limit to top 10 services for better visualization
				let top_services = data.service_popularity.slice(0, 10);
				
				new frappe.Chart($popularity_chart.find('.popularity-chart')[0], {
					data: {
						labels: top_services.map(item => item.service_name || item.service),
						datasets: [{
							name: __('عدد الحجوزات'),
							values: top_services.map(item => item.booking_count)
						}]
					},
					type: 'bar',
					height: 250,
					colors: ['#5e64ff']
				});
			}
			
			// Category chart
			if (data.bookings_by_category && Object.keys(data.bookings_by_category).length) {
				new frappe.Chart($category_chart.find('.category-chart')[0], {
					data: {
						labels: Object.keys(data.bookings_by_category),
						datasets: [{
							name: __('عدد الحجوزات'),
							values: Object.values(data.bookings_by_category)
						}]
					},
					type: 'pie',
					height: 250,
					colors: ['#5e64ff', '#28a745', '#ffc107', '#dc3545', '#6c757d']
				});
			}
		}, 300);
	}
	
	render_revenue_report(data) {
		let $content = $(this.page.body).find('.report-content');
		
		// Render summary
		let $summary = $('<div class="report-summary"></div>');
		$summary.append(`
			<div class="summary-box">
				<div class="summary-value">${data.total_revenue} ${__('ريال')}</div>
				<div class="summary-label">${__('إجمالي الإيرادات')}</div>
			</div>
			<div class="summary-box">
				<div class="summary-value">${data.total_bookings}</div>
				<div class="summary-label">${__('إجمالي الحجوزات')}</div>
			</div>
			<div class="summary-box">
				<div class="summary-value">${(data.total_revenue / data.total_bookings).toFixed(1)} ${__('ريال')}</div>
				<div class="summary-label">${__('متوسط سعر الحجز')}</div>
			</div>
		`);
		
		// Render visualization
		let $visualization = $('<div class="report-visualization"></div>');
		
		// Add revenue chart
		let $revenue_chart = $('<div class="chart-container"><h4>' + __('الإيرادات حسب الخدمة') + '</h4><div class="revenue-chart"></div></div>');
		$visualization.append($revenue_chart);
		
		// Add bookings chart
		let $bookings_chart = $('<div class="chart-container"><h4>' + __('عدد الحجوزات حسب الخدمة') + '</h4><div class="bookings-chart"></div></div>');
		$visualization.append($bookings_chart);
		
		// Render details
		let $details = $('<div class="report-details"><h4>' + __('تفاصيل الإيرادات') + '</h4></div>');
		
		// Create revenue table
		let $table = $('<table class="table table-bordered table-hover"><thead><tr>' +
			'<th>' + __('الخدمة') + '</th>' +
			'<th>' + __('عدد الحجوزات') + '</th>' +
			'<th>' + __('إجمالي الإيرادات') + '</th>' +
			'<th>' + __('متوسط سعر الحجز') + '</th>' +
			'<th>' + __('النسبة من الإجمالي') + '</th>' +
			'</tr></thead><tbody></tbody></table>');
		
		let $tbody = $table.find('tbody');
		data.revenue_by_service.forEach(item => {
			let avg_price = (item.total_revenue / item.booking_count).toFixed(1);
			let percentage = ((item.total_revenue / data.total_revenue) * 100).toFixed(1);
			$tbody.append('<tr>' +
				'<td>' + item.service + '</td>' +
				'<td>' + item.booking_count + '</td>' +
				'<td>' + item.total_revenue + ' ' + __('ريال') + '</td>' +
				'<td>' + avg_price + ' ' + __('ريال') + '</td>' +
				'<td>' + percentage + '%</td>' +
				'</tr>');
		});
		
		$details.append($table);
		
		// Append to content
		$content.append($summary);
		$content.append($visualization);
		$content.append($details);
		
		// Initialize charts
		setTimeout(() => {
			// Revenue chart
			if (data.revenue_by_service.length) {
				// Limit to top 10 services for better visualization
				let top_services = data.revenue_by_service.slice(0, 10);
				
				new frappe.Chart($revenue_chart.find('.revenue-chart')[0], {
					data: {
						labels: top_services.map(item => item.service),
						datasets: [{
							name: __('الإيرادات'),
							values: top_services.map(item => item.total_revenue)
						}]
					},
					type: 'bar',
					height: 250,
					colors: ['#5e64ff']
				});
			}
			
			// Bookings chart
			if (data.revenue_by_service.length) {
				// Limit to top 10 services for better visualization
				let top_services = data.revenue_by_service.slice(0, 10);
				
				new frappe.Chart($bookings_chart.find('.bookings-chart')[0], {
					data: {
						labels: top_services.map(item => item.service),
						datasets: [{
							name: __('عدد الحجوزات'),
							values: top_services.map(item => item.booking_count)
						}]
					},
					type: 'bar',
					height: 250,
					colors: ['#28a745']
				});
			}
		}, 300);
	}

	export_report() {
		if (!this.report_data) {
			frappe.msgprint(__('يرجى إنشاء التقرير أولاً'));
			return;
		}
		
		let report_type = this.report_type_field.get_value();
		let data = [];
		let columns = [];
		
		// Format data based on report type
		if (report_type === 'Booking Summary' && this.report_data.bookings) {
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
			data = this.report_data.bookings;
		} else if (report_type === 'Photographer Performance' && this.report_data.photographer_performance) {
			columns = [
				{label: __('المصور'), fieldname: 'photographer'},
				{label: __('عدد الحجوزات'), fieldname: 'total_bookings'},
				{label: __('إجمالي الدقائق'), fieldname: 'total_minutes'}
			];
			data = this.report_data.photographer_performance;
		} else if (report_type === 'Service Popularity' && this.report_data.service_popularity) {
			columns = [
				{label: __('الخدمة'), fieldname: 'service'},
				{label: __('اسم الخدمة'), fieldname: 'service_name'},
				{label: __('الفئة'), fieldname: 'category'},
				{label: __('عدد الحجوزات'), fieldname: 'booking_count'}
			];
			data = this.report_data.service_popularity;
		} else if (report_type === 'Revenue Report' && this.report_data.revenue_by_service) {
			columns = [
				{label: __('الخدمة'), fieldname: 'service'},
				{label: __('عدد الحجوزات'), fieldname: 'booking_count'},
				{label: __('إجمالي الإيرادات'), fieldname: 'total_revenue'}
			];
			data = this.report_data.revenue_by_service;
		}
		
		// Export to Excel
		frappe.tools.downloadify(data, null, 'تقرير_الحجوزات');
	}
	
	print_report() {
		if (!this.report_data) {
			frappe.msgprint(__('يرجى إنشاء التقرير أولاً'));
			return;
		}
		
		// Create a printable version of the report
		let html = this.get_print_html();
		
		// Open print dialog
		frappe.ui.get_print_settings(false, function(print_settings) {
			frappe.render_pdf(html, print_settings);
		}, this.report_type_field.get_value());
	}
	
	get_print_html() {
		let report_type = this.report_type_field.get_value();
		let date_range = this.date_range_field.get_value();
		let date_str = '';
		
		if (date_range === 'Custom') {
			date_str = frappe.datetime.str_to_user(this.start_date_field.get_value()) + ' - ' + 
				frappe.datetime.str_to_user(this.end_date_field.get_value());
		} else if (date_range === 'Today') {
			date_str = __('اليوم');
		} else if (date_range === 'This Week') {
			date_str = __('هذا الأسبوع');
		} else if (date_range === 'This Month') {
			date_str = __('هذا الشهر');
		} else if (date_range === 'Last Month') {
			date_str = __('الشهر الماضي');
		} else if (date_range === 'This Year') {
			date_str = __('هذا العام');
		}
		
		// Create HTML content
		let html = `
			<div class="print-report">
				<h2>${__('تقرير الحجوزات')}: ${report_type}</h2>
				<p>${__('النطاق الزمني')}: ${date_str}</p>
				<hr>
		`;
		
		// Add report content based on type
		if (report_type === 'Booking Summary') {
			html += this.get_booking_summary_html();
		} else if (report_type === 'Photographer Performance') {
			html += this.get_photographer_performance_html();
		} else if (report_type === 'Service Popularity') {
			html += this.get_service_popularity_html();
		} else if (report_type === 'Revenue Report') {
			html += this.get_revenue_report_html();
		}
		
		html += '</div>';
		
		// Add print styles
		html += `
			<style>
				.print-report { font-family: Arial, sans-serif; }
				.print-report h2 { margin-bottom: 5px; }
				.print-report p { margin-top: 0; color: #666; }
				.print-report table { width: 100%; border-collapse: collapse; margin: 15px 0; }
				.print-report th, .print-report td { border: 1px solid #ddd; padding: 8px; text-align: right; }
				.print-report th { background-color: #f2f2f2; }
				.print-report .summary-section { margin-bottom: 20px; }
				.print-report .summary-title { font-weight: bold; margin-bottom: 10px; }
				.print-report .summary-table { width: 100%; }
				.print-report .summary-table td { padding: 5px 10px; }
				.print-report .summary-label { font-weight: bold; }
			</style>
		`;
		
		return html;
	}
	
	get_booking_summary_html() {
		let data = this.report_data;
		let html = '';
		
		// Add summary section
		html += `
			<div class="summary-section">
				<div class="summary-title">${__('ملخص')}</div>
				<table class="summary-table">
					<tr>
						<td class="summary-label">${__('إجمالي الحجوزات')}:</td>
						<td>${data.total_bookings}</td>
					</tr>
		`;
		
		// Add status counts
		for (let status in data.status_counts) {
			html += `
				<tr>
					<td class="summary-label">${status}:</td>
					<td>${data.status_counts[status]}</td>
				</tr>
			`;
		}
		
		html += '</table></div>';
		
		// Add bookings table
		html += `
			<div class="details-section">
				<div class="summary-title">${__('تفاصيل الحجوزات')}</div>
				<table>
					<thead>
						<tr>
							<th>${__('رقم الحجز')}</th>
							<th>${__('اسم العميل')}</th>
							<th>${__('تاريخ الحجز')}</th>
							<th>${__('وقت البدء')}</th>
							<th>${__('وقت الانتهاء')}</th>
							<th>${__('الخدمة')}</th>
							<th>${__('المصور')}</th>
							<th>${__('الحالة')}</th>
						</tr>
					</thead>
					<tbody>
		`;
		
		// Add booking rows
		data.bookings.forEach(booking => {
			html += `
				<tr>
					<td>${booking.name}</td>
					<td>${booking.customer_name}</td>
					<td>${frappe.datetime.str_to_user(booking.booking_date)}</td>
					<td>${booking.start_time}</td>
					<td>${booking.end_time}</td>
					<td>${booking.service}</td>
					<td>${booking.photographer}</td>
					<td>${booking.status}</td>
				</tr>
			`;
		});
		
		html += '</tbody></table></div>';
		
		return html;
	}
	
	get_photographer_performance_html() {
		let data = this.report_data;
		let html = '';
		
		// Add summary section
		html += `
			<div class="summary-section">
				<div class="summary-title">${__('ملخص')}</div>
				<table class="summary-table">
					<tr>
						<td class="summary-label">${__('عدد المصورين')}:</td>
						<td>${data.photographer_performance.length}</td>
					</tr>
					<tr>
						<td class="summary-label">${__('إجمالي الحجوزات')}:</td>
						<td>${data.total_bookings}</td>
					</tr>
					<tr>
						<td class="summary-label">${__('إجمالي الساعات')}:</td>
						<td>${(data.total_hours).toFixed(1)}</td>
					</tr>
				</table>
			</div>
		`;
		
		// Add photographer performance table
		html += `
			<div class="details-section">
				<div class="summary-title">${__('تفاصيل أداء المصورين')}</div>
				<table>
					<thead>
						<tr>
							<th>${__('المصور')}</th>
							<th>${__('عدد الحجوزات')}</th>
							<th>${__('إجمالي الساعات')}</th>
							<th>${__('متوسط مدة الجلسة')}</th>
						</tr>
					</thead>
					<tbody>
		`;
		
		// Add photographer rows
		data.photographer_performance.forEach(item => {
			let hours = (item.total_minutes / 60).toFixed(1);
			let avg_session = (item.total_minutes / 60 / item.total_bookings).toFixed(1);
			html += `
				<tr>
					<td>${item.photographer}</td>
					<td>${item.total_bookings}</td>
					<td>${hours} ${__('ساعة')}</td>
					<td>${avg_session} ${__('ساعة')}</td>
				</tr>
			`;
		});
		
		html += '</tbody></table></div>';
		
		return html;
	}
	
	get_service_popularity_html() {
		let data = this.report_data;
		let html = '';
		
		// Add summary section
		html += `
			<div class="summary-section">
				<div class="summary-title">${__('ملخص')}</div>
				<table class="summary-table">
					<tr>
						<td class="summary-label">${__('عدد الخدمات')}:</td>
						<td>${data.service_popularity.length}</td>
					</tr>
					<tr>
						<td class="summary-label">${__('إجمالي الحجوزات')}:</td>
						<td>${data.total_bookings}</td>
					</tr>
		`;
		
		// Add top service if available
		if (data.service_popularity.length > 0) {
			html += `
				<tr>
					<td class="summary-label">${__('الخدمة الأكثر طلباً')}:</td>
					<td>${data.service_popularity[0].service_name || data.service_popularity[0].service}</td>
				</tr>
			`;
		}
		
		html += '</table></div>';
		
		// Add service popularity table
		html += `
			<div class="details-section">
				<div class="summary-title">${__('تفاصيل شعبية الخدمات')}</div>
				<table>
					<thead>
						<tr>
							<th>${__('الخدمة')}</th>
							<th>${__('اسم الخدمة')}</th>
							<th>${__('الفئة')}</th>
							<th>${__('عدد الحجوزات')}</th>
							<th>${__('النسبة من الإجمالي')}</th>
						</tr>
					</thead>
					<tbody>
		`;
		
		// Add service rows
		data.service_popularity.forEach(item => {
			let percentage = ((item.booking_count / data.total_bookings) * 100).toFixed(1);
			html += `
				<tr>
					<td>${item.service}</td>
					<td>${item.service_name || ''}</td>
					<td>${item.category || ''}</td>
					<td>${item.booking_count}</td>
					<td>${percentage}%</td>
				</tr>
			`;
		});
		
		html += '</tbody></table></div>';
		
		return html;
	}
	
	get_revenue_report_html() {
		let data = this.report_data;
		let html = '';
		
		// Add summary section
		html += `
			<div class="summary-section">
				<div class="summary-title">${__('ملخص')}</div>
				<table class="summary-table">
					<tr>
						<td class="summary-label">${__('إجمالي الإيرادات')}:</td>
						<td>${data.total_revenue} ${__('ريال')}</td>
					</tr>
					<tr>
						<td class="summary-label">${__('إجمالي الحجوزات')}:</td>
						<td>${data.total_bookings}</td>
					</tr>
					<tr>
						<td class="summary-label">${__('متوسط سعر الحجز')}:</td>
						<td>${(data.total_revenue / data.total_bookings).toFixed(1)} ${__('ريال')}</td>
					</tr>
				</table>
			</div>
		`;
		
		// Add revenue table
		html += `
			<div class="details-section">
				<div class="summary-title">${__('تفاصيل الإيرادات')}</div>
				<table>
					<thead>
						<tr>
							<th>${__('الخدمة')}</th>
							<th>${__('عدد الحجوزات')}</th>
							<th>${__('إجمالي الإيرادات')}</th>
							<th>${__('متوسط سعر الحجز')}</th>
							<th>${__('النسبة من الإجمالي')}</th>
						</tr>
					</thead>
					<tbody>
		`;
		
		// Add revenue rows
		data.revenue_by_service.forEach(item => {
			let avg_price = (item.total_revenue / item.booking_count).toFixed(1);
			let percentage = ((item.total_revenue / data.total_revenue) * 100).toFixed(1);
			html += `
				<tr>
					<td>${item.service}</td>
					<td>${item.booking_count}</td>
					<td>${item.total_revenue} ${__('ريال')}</td>
					<td>${avg_price} ${__('ريال')}</td>
					<td>${percentage}%</td>
				</tr>
			`;
		});
		
		html += '</tbody></table></div>';
		
		return html;
	}
};

frappe.pages['booking-report-page'].on_page_show = function(wrapper) {
	// Refresh page when shown
	if (wrapper.page.report_view) {
		// Page is shown - no additional action needed
	}
};