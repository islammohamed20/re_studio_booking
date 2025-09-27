frappe.pages['admin-dashboard'].on_page_load = function(wrapper) {
var page = frappe.ui.make_app_page({
parent: wrapper,
title: 'Re Studio - لوحة التحكم المتقدمة',
single_column: true
});

// Add CSS
frappe.require([
'admin_dashboard.bundle.css'
]);

// Add custom buttons
page.set_primary_action('تحديث البيانات', () => loadDashboardData(page), 'refresh');

page.add_menu_item('تصدير التقرير', () => exportDashboardReport());
page.add_menu_item('طباعة', () => printDashboard());
page.add_menu_item('عرض الإحصائيات الشهرية', () => showMonthlyStats());

// Add filters
let today = frappe.datetime.get_today();
let lastMonth = frappe.datetime.add_months(today, -1);

page.add_field({
fieldtype: 'DateRange',
label: 'النطاق الزمني',
default: [lastMonth, today],
change: function() {
loadDashboardData(page);
}
});

page.add_field({
fieldtype: 'Select',
label: 'المصور',
options: 'All Photographers\n',
change: function() {
loadDashboardData(page);
}
});

// Add content areas
$(frappe.render_template("admin_dashboard", {})).appendTo(page.body);

// Load photographers for filter
loadPhotographers(page);

// Load dashboard data
loadDashboardData(page);
}

function loadPhotographers(page) {
frappe.call({
method: "frappe.client.get_list",
args: {
doctype: "Photographer",
fields: ["name", "full_name"],
limit: 100
},
callback: function(r) {
if (r.message) {
let options = 'All Photographers\n';
r.message.forEach(p => {
options += p.name + '\n';
});

page.fields_dict['المصور'].set_options(options);
}
}
});
}

function loadDashboardData(page) {
// Show loading state
$('.dashboard-container').html('<div class="text-center" style="padding: 40px;"><i class="fa fa-spinner fa-spin fa-2x"></i><p style="margin-top: 20px;">جاري تحميل البيانات...</p></div>');

// Get filter values
let dateRange = page.fields_dict['النطاق الزمني'].get_value();
let photographer = page.fields_dict['المصور'].get_value();

if (photographer === 'All Photographers') {
photographer = '';
}

// Call backend method
frappe.call({
method: "re_studio_booking.re_studio_booking.page.admin_dashboard.admin_dashboard.get_dashboard_data",
args: {
start_date: dateRange[0],
end_date: dateRange[1],
photographer: photographer
},
callback: function(r) {
if (r.message) {
renderDashboard(r.message);
} else {
$('.dashboard-container').html('<div class="text-center text-muted" style="padding: 40px;"><i class="fa fa-exclamation-triangle fa-2x"></i><p style="margin-top: 20px;">فشل في تحميل البيانات</p></div>');
}
}
});
}

function renderDashboard(data) {
// Generate HTML content for quick stats
let quickStatsHTML = `
<div class="row">
<div class="col-md-3 col-sm-6">
<div class="stat-box" style="background: linear-gradient(to right, #00c6ff, #0072ff);">
<div class="stat-icon"><i class="fa fa-calendar"></i></div>
<div class="stat-details">
<div class="stat-number">${data.quick_stats.total_bookings || 0}</div>
<div class="stat-label">إجمالي الحجوزات</div>
</div>
</div>
</div>
<div class="col-md-3 col-sm-6">
<div class="stat-box" style="background: linear-gradient(to right, #ff9966, #ff5e62);">
<div class="stat-icon"><i class="fa fa-clock-o"></i></div>
<div class="stat-details">
<div class="stat-number">${data.quick_stats.pending_bookings || 0}</div>
<div class="stat-label">الحجوزات المعلقة</div>
</div>
</div>
</div>
<div class="col-md-3 col-sm-6">
<div class="stat-box" style="background: linear-gradient(to right, #11998e, #38ef7d);">
<div class="stat-icon"><i class="fa fa-check-circle"></i></div>
<div class="stat-details">
<div class="stat-number">${data.quick_stats.confirmed_bookings || 0}</div>
<div class="stat-label">الحجوزات المؤكدة</div>
</div>
</div>
</div>
<div class="col-md-3 col-sm-6">
<div class="stat-box" style="background: linear-gradient(to right, #834d9b, #d04ed6);">
<div class="stat-icon"><i class="fa fa-money"></i></div>
<div class="stat-details">
<div class="stat-number">${frappe.format(data.quick_stats.total_revenue || 0, {fieldtype: 'Currency'})}</div>
<div class="stat-label">إجمالي الإيرادات</div>
</div>
</div>
</div>
</div>
`;

// Generate HTML for revenue trends
let chartSectionHTML = `
<div class="row" style="margin-top: 20px;">
<div class="col-md-7">
<div class="dashboard-card">
<h5 class="card-title">اتجاهات الحجوزات والإيرادات</h5>
<div id="booking-revenue-chart" style="height: 300px;"></div>
</div>
</div>
<div class="col-md-5">
<div class="dashboard-card">
<h5 class="card-title">توزيع الخدمات</h5>
<div id="service-distribution-chart" style="height: 300px;"></div>
</div>
</div>
</div>
`;

// Generate HTML for recent bookings
let recentBookingsHTML = `
<div class="row" style="margin-top: 20px;">
<div class="col-md-8">
<div class="dashboard-card">
<h5 class="card-title">آخر الحجوزات</h5>
<div class="table-responsive">
<table class="table table-hover">
<thead>
<tr>
<th>العميل</th>
<th>الخدمة</th>
<th>المصور</th>
<th>التاريخ</th>
<th>الحالة</th>
<th>السعر</th>
</tr>
</thead>
<tbody>
${generateRecentBookingsHTML(data.recent_bookings)}
</tbody>
</table>
</div>
<div class="text-center" style="margin-top: 15px;">
<button class="btn btn-default btn-sm" onclick="frappe.set_route('List', 'Booking')">
عرض كل الحجوزات
</button>
</div>
</div>
</div>
<div class="col-md-4">
<div class="dashboard-card">
<h5 class="card-title">أداء المصورين</h5>
<div id="photographer-performance-chart" style="height: 300px;"></div>
</div>
</div>
</div>
`;

// Update dashboard content
$('.dashboard-container').html(quickStatsHTML + chartSectionHTML + recentBookingsHTML);

// Initialize charts
setTimeout(function() {
renderBookingRevenueChart(data.booking_trends);
renderServiceDistributionChart(data.service_distribution);
renderPhotographerPerformanceChart(data.photographer_performance);
}, 100);
}

function generateRecentBookingsHTML(bookings) {
let html = '';

if (bookings && bookings.length) {
bookings.forEach(function(booking) {
html += `
<tr data-name="${booking.name}" style="cursor: pointer;" onclick="frappe.set_route('Form', 'Booking', '${booking.name}')">
<td>${booking.customer_name || '-'}</td>
<td>${booking.service_name || '-'}</td>
<td>${booking.photographer || '-'}</td>
<td>${frappe.datetime.str_to_user(booking.booking_date) || '-'}</td>
<td><span class="indicator ${getStatusColor(booking.status)}"></span> ${booking.status || '-'}</td>
<td>${frappe.format(booking.amount || 0, {fieldtype: 'Currency'})}</td>
</tr>
`;
});
} else {
html = '<tr><td colspan="6" class="text-center text-muted">لا توجد حجوزات حديثة</td></tr>';
}

return html;
}

function getStatusColor(status) {
switch(status) {
case 'Confirmed': return 'green';
case 'Pending': return 'orange';
case 'Cancelled': return 'red';
case 'Completed': return 'blue';
default: return 'gray';
}
}

function renderBookingRevenueChart(data) {
if (!data || !data.labels.length) return;

const chart = new frappe.Chart('#booking-revenue-chart', {
data: {
labels: data.labels,
datasets: [
{
name: 'الحجوزات',
values: data.bookings,
chartType: 'bar'
},
{
name: 'الإيرادات',
values: data.revenue,
chartType: 'line'
}
]
},
type: 'axis-mixed',
height: 300,
colors: ['#7453ff', '#11998e'],
axisOptions: {
xIsSeries: true
},
tooltipOptions: {
formatTooltipY: (value, datasetIndex) => {
if (datasetIndex === 1) {
return frappe.format(value, {fieldtype: 'Currency'});
}
return value;
}
}
});
}

function renderServiceDistributionChart(data) {
if (!data || !data.labels.length) return;

const chart = new frappe.Chart('#service-distribution-chart', {
data: {
labels: data.labels,
datasets: [
{
name: 'الخدمات',
values: data.values
}
]
},
type: 'pie',
height: 300,
colors: ['#ff9966', '#36a2eb', '#ff6384', '#4bc0c0', '#9966ff', '#ffcd56'],
});
}

function renderPhotographerPerformanceChart(data) {
if (!data || !data.labels.length) return;

const chart = new frappe.Chart('#photographer-performance-chart', {
data: {
labels: data.labels,
datasets: [
{
name: 'الحجوزات',
values: data.bookings
},
{
name: 'الإيرادات',
values: data.revenue
}
]
},
type: 'bar',
height: 300,
colors: ['#36a2eb', '#ff6384'],
tooltipOptions: {
formatTooltipY: (value, datasetIndex) => {
if (datasetIndex === 1) {
return frappe.format(value, {fieldtype: 'Currency'});
}
return value;
}
}
});
}

function exportDashboardReport() {
// Get filter values
let dateRange = cur_page.page.fields_dict['النطاق الزمني'].get_value();
let photographer = cur_page.page.fields_dict['المصور'].get_value();

frappe.call({
method: "re_studio_booking.re_studio_booking.page.admin_dashboard.admin_dashboard.export_dashboard_data",
args: {
start_date: dateRange[0],
end_date: dateRange[1],
photographer: photographer === 'All Photographers' ? '' : photographer
},
callback: function(r) {
if (r.message) {
// Download the file
const blob = new Blob([r.message.content], { type: 'application/octet-stream' });
const link = document.createElement('a');
link.href = window.URL.createObjectURL(blob);
link.download = r.message.filename;
link.click();
}
}
});
}

function printDashboard() {
window.print();
}

function showMonthlyStats() {
frappe.set_route('Report', 'Booking', 'Monthly Booking Statistics');
}

// Direction RTL
$(document).ready(function() {
$('body').attr('dir', 'rtl');
});
