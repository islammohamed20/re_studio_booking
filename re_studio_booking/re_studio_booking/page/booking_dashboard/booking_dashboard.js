frappe.pages['booking-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'لوحة معلومات الحجز',
		single_column: true
	});
	
	// Add refresh button
	page.set_primary_action('تحديث', () => {
		page.dashboard.refresh_data();
	}, 'refresh');
	
	// Add quick actions
	page.add_menu_item('إنشاء حجز جديد', () => {
		frappe.new_doc('Booking');
	});
	
	page.add_menu_item('إنشاء تقرير', () => {
		frappe.new_doc('Booking Report');
	});
	
	page.add_menu_item('إعدادات الحجز', () => {
		frappe.set_route('Form', 'Booking Settings', 'Booking Settings');
	});
	
	// Initialize dashboard
	page.dashboard = new BookingDashboard(page);
};

class BookingDashboard {
	constructor(page) {
		this.page = page;
		this.make();
		this.refresh_data();
	}
	
	make() {
		this.body = $('<div class="booking-dashboard-container"></div>').appendTo(this.page.main);
		
		// Create dashboard sections
		this.make_stats_section();
		this.make_bookings_section();
		this.make_charts_section();
	}
	
	make_stats_section() {
		this.stats_section = $(`
			<div class="stats-section">
				<h4>إحصائيات سريعة</h4>
				<div class="row stats-cards"></div>
			</div>
		`).appendTo(this.body);
	}
	
	make_bookings_section() {
		this.bookings_section = $(`
			<div class="bookings-section">
				<div class="row">
					<div class="col-md-6">
						<div class="recent-bookings">
							<h4>أحدث الحجوزات</h4>
							<div class="bookings-list"></div>
						</div>
					</div>
					<div class="col-md-6">
						<div class="upcoming-bookings">
							<h4>الحجوزات القادمة</h4>
							<div class="bookings-list"></div>
						</div>
					</div>
				</div>
			</div>
		`).appendTo(this.body);
	}
	
	make_charts_section() {
		this.charts_section = $(`
			<div class="charts-section">
				<div class="row">
					<div class="col-md-6">
						<div class="status-chart-container">
							<h4>الحجوزات حسب الحالة</h4>
							<div id="status-chart"></div>
						</div>
					</div>
					<div class="col-md-6">
						<div class="service-chart-container">
							<h4>أكثر الخدمات طلباً</h4>
							<div id="service-chart"></div>
						</div>
					</div>
				</div>
			</div>
		`).appendTo(this.body);
	}
	
	refresh_data() {
		this.page.set_indicator('جاري التحميل...', 'blue');
		
		frappe.call({
			method: 're_studio_booking.re_studio_booking.page.booking_dashboard.booking_dashboard.get_dashboard_data',
			callback: (r) => {
				if (r.message) {
					this.render_dashboard(r.message);
					this.page.set_indicator('تم التحديث', 'green');
					
					// Clear indicator after 2 seconds
					setTimeout(() => {
						this.page.set_indicator('');
					}, 2000);
				}
			}
		});
	}
	
	render_dashboard(data) {
		this.render_stats(data.booking_stats);
		this.render_recent_bookings(data.recent_bookings);
		this.render_upcoming_bookings(data.upcoming_bookings);
		this.render_status_chart(data.booking_stats.status_counts);
		this.render_service_chart(data.service_stats.top_services);
	}
	
	render_stats(stats) {
		const stats_cards = this.stats_section.find('.stats-cards');
		stats_cards.empty();
		
		// Add stat cards
		this.add_stat_card(stats_cards, 'حجوزات اليوم', stats.today, 'blue');
		this.add_stat_card(stats_cards, 'حجوزات الأسبوع', stats.this_week, 'green');
		this.add_stat_card(stats_cards, 'حجوزات الشهر', stats.this_month, 'orange');
		
		// Add status counts
		this.add_stat_card(stats_cards, 'مؤكدة', stats.status_counts.Confirmed || 0, 'purple');
		this.add_stat_card(stats_cards, 'مكتملة', stats.status_counts.Completed || 0, 'green');
		this.add_stat_card(stats_cards, 'ملغاة', stats.status_counts.Cancelled || 0, 'red');
	}
	
	add_stat_card(container, title, value, color) {
		$(`
			<div class="col-md-4 col-sm-6">
				<div class="stat-card" style="border-top: 3px solid var(--${color}); background-color: var(--bg-${color})">
					<div class="value">${value}</div>
					<div class="label">${title}</div>
				</div>
			</div>
		`).appendTo(container);
	}
	
	render_recent_bookings(bookings) {
		const container = this.bookings_section.find('.recent-bookings .bookings-list');
		this.render_bookings_list(container, bookings);
	}
	
	render_upcoming_bookings(bookings) {
		const container = this.bookings_section.find('.upcoming-bookings .bookings-list');
		this.render_bookings_list(container, bookings);
	}
	
	render_bookings_list(container, bookings) {
		container.empty();
		
		if (!bookings.length) {
			container.html('<div class="text-muted">لا توجد حجوزات</div>');
			return;
		}
		
		const table = $(`
			<table class="table table-bordered">
				<thead>
					<tr>
						<th>رقم الحجز</th>
						<th>العميل</th>
						<th>التاريخ</th>
						<th>الخدمة</th>
						<th>الحالة</th>
					</tr>
				</thead>
				<tbody></tbody>
			</table>
		`).appendTo(container);
		
		const tbody = table.find('tbody');
		
		bookings.forEach(booking => {
			const row = $(`
				<tr data-booking="${booking.name}">
					<td>${booking.name}</td>
					<td>${booking.customer_name}</td>
					<td>${frappe.datetime.str_to_user(booking.booking_date)} ${frappe.datetime.get_time(booking.start_time)}</td>
					<td>${booking.service}</td>
					<td><span class="status-indicator ${this.get_status_color(booking.status)}">${booking.status}</span></td>
				</tr>
			`).appendTo(tbody);
			
			row.click(() => {
				frappe.set_route('Form', 'Booking', booking.name);
			});
		});
	}
	
	get_status_color(status) {
		const status_colors = {
			'Draft': 'gray',
			'Confirmed': 'blue',
			'Completed': 'green',
			'Cancelled': 'red'
		};
		
		return status_colors[status] || 'gray';
	}
	
	render_status_chart(status_counts) {
		const labels = [];
		const values = [];
		const colors = [];
		
		// Define status colors
		const status_colors = {
			'Draft': '#8d99a6',
			'Confirmed': '#5e64ff',
			'Completed': '#28a745',
			'Cancelled': '#ff5858'
		};
		
		// Prepare data
		Object.keys(status_counts).forEach(status => {
			labels.push(status);
			values.push(status_counts[status]);
			colors.push(status_colors[status] || '#8d99a6');
		});
		
		// Create chart
		if (this.status_chart) {
			this.status_chart.destroy();
		}
		
		const chart_container = document.getElementById('status-chart');
		chart_container.innerHTML = '';
		
		if (!values.length) {
			chart_container.innerHTML = '<div class="text-muted">لا توجد بيانات</div>';
			return;
		}
		
		this.status_chart = new frappe.Chart(chart_container, {
			data: {
				labels: labels,
				datasets: [{
					values: values
				}],
				colors: colors
			},
			type: 'pie',
			height: 250,
			colors: colors
		});
	}
	
	render_service_chart(services) {
		const labels = [];
		const values = [];
		
		// Prepare data
		services.forEach(service => {
			labels.push(service.service_name || service.service);
			values.push(service.booking_count);
		});
		
		// Create chart
		if (this.service_chart) {
			this.service_chart.destroy();
		}
		
		const chart_container = document.getElementById('service-chart');
		chart_container.innerHTML = '';
		
		if (!values.length) {
			chart_container.innerHTML = '<div class="text-muted">لا توجد بيانات</div>';
			return;
		}
		
		this.service_chart = new frappe.Chart(chart_container, {
			data: {
				labels: labels,
				datasets: [{
					values: values
				}]
			},
			type: 'bar',
			height: 250,
			colors: ['#5e64ff']
		});
	}
}

// Add CSS
frappe.dom.set_style(`
.booking-dashboard-container {
	padding: 15px;
}

.booking-dashboard-container h4 {
	margin-top: 20px;
	margin-bottom: 15px;
	font-weight: 600;
}

.stat-card {
	padding: 15px;
	border-radius: 5px;
	box-shadow: 0 1px 3px rgba(0,0,0,0.1);
	margin-bottom: 15px;
}

.stat-card .value {
	font-size: 24px;
	font-weight: bold;
}

.stat-card .label {
	color: var(--text-muted);
	font-size: 14px;
}

.bookings-list {
	margin-bottom: 20px;
}

.bookings-list table {
	margin-bottom: 0;
}

.bookings-list tr {
	cursor: pointer;
}

.bookings-list tr:hover {
	background-color: var(--control-bg);
}

.status-indicator {
	display: inline-block;
	padding: 3px 8px;
	border-radius: 3px;
	font-size: 12px;
}

.status-indicator.gray {
	background-color: var(--gray-300);
	color: var(--gray-800);
}

.status-indicator.blue {
	background-color: var(--blue-100);
	color: var(--blue-800);
}

.status-indicator.green {
	background-color: var(--green-100);
	color: var(--green-800);
}

.status-indicator.red {
	background-color: var(--red-100);
	color: var(--red-800);
}

.charts-section {
	margin-top: 20px;
}

#status-chart, #service-chart {
	height: 250px;
}
`);