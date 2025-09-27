import frappe
from frappe import _
import json
from datetime import datetime, timedelta
import calendar

@frappe.whitelist()
def get_dashboard_data(start_date=None, end_date=None, photographer=None):
    """Get all data required for the admin dashboard"""
    try:
        if not start_date:
            start_date = frappe.utils.add_months(frappe.utils.today(), -1)
        if not end_date:
            end_date = frappe.utils.today()

        filters = {}
        if photographer:
            filters["photographer"] = photographer

        # Get quick stats
        quick_stats = get_quick_stats(start_date, end_date, filters)
        
        # Get booking and revenue trends
        booking_trends = get_booking_trends(start_date, end_date, filters)
        
        # Get service distribution
        service_distribution = get_service_distribution(start_date, end_date, filters)
        
        # Get recent bookings
        recent_bookings = get_recent_bookings(filters)
        
        # Get photographer performance
        photographer_performance = get_photographer_performance(start_date, end_date)
        
        return {
            "quick_stats": quick_stats,
            "booking_trends": booking_trends,
            "service_distribution": service_distribution,
            "recent_bookings": recent_bookings,
            "photographer_performance": photographer_performance
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Admin Dashboard Data Error"))
        return None

def get_quick_stats(start_date, end_date, filters=None):
    """Get quick stats for the dashboard"""
    if not filters:
        filters = {}
    
    date_filters = filters.copy()
    date_filters.update({
        "booking_date": ["between", [start_date, end_date]]
    })
    
    # Get total bookings in date range
    total_bookings = frappe.db.count("Booking", date_filters)
    
    # Get pending bookings in date range
    pending_filters = date_filters.copy()
    pending_filters.update({"status": "Pending"})
    pending_bookings = frappe.db.count("Booking", pending_filters)
    
    # Get confirmed bookings in date range
    confirmed_filters = date_filters.copy()
    confirmed_filters.update({"status": "Confirmed"})
    confirmed_bookings = frappe.db.count("Booking", confirmed_filters)
    
    # Get total revenue in date range
    total_revenue = frappe.db.sql("""
        SELECT IFNULL(SUM(amount), 0) as total_revenue
        FROM `tabBooking`
        WHERE booking_date BETWEEN %s AND %s
        AND status IN ('Confirmed', 'Completed')
        {photographer_filter}
    """.format(
        photographer_filter = "AND photographer = '%s'" % filters.get("photographer") if filters.get("photographer") else ""
    ), (start_date, end_date), as_dict=True)[0].total_revenue
    
    return {
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "confirmed_bookings": confirmed_bookings,
        "total_revenue": total_revenue
    }

def get_booking_trends(start_date, end_date, filters=None):
    """Get booking and revenue trends for the chart"""
    if not filters:
        filters = {}
        
    photographer_filter = ""
    if filters.get("photographer"):
        photographer_filter = "AND photographer = '{}'".format(filters.get("photographer"))
    
    # Parse dates
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Determine the grouping (day, week, month) based on date range
    days_diff = (end - start).days
    
    if days_diff <= 31:
        # Daily grouping for a month or less
        date_format = "%Y-%m-%d"
        group_by = "DATE(booking_date)"
        date_label_format = "%d %b"
    elif days_diff <= 90:
        # Weekly grouping for 3 months or less
        date_format = "%Y-%U"
        group_by = "YEARWEEK(booking_date, 1)"
        date_label_format = "Week %W"
    else:
        # Monthly grouping for more than 3 months
        date_format = "%Y-%m"
        group_by = "DATE_FORMAT(booking_date, '%Y-%m')"
        date_label_format = "%b %Y"
    
    # Query for bookings and revenue trends
    trends = frappe.db.sql("""
        SELECT 
            {group_by} as date_group,
            COUNT(*) as booking_count,
            IFNULL(SUM(amount), 0) as revenue
        FROM 
            `tabBooking` 
        WHERE 
            booking_date BETWEEN %s AND %s
            {photographer_filter}
        GROUP BY 
            date_group
        ORDER BY 
            date_group
    """.format(
        group_by=group_by,
        photographer_filter=photographer_filter
    ), (start_date, end_date), as_dict=True)
    
    # Process results into chart format
    labels = []
    bookings = []
    revenue = []
    
    # Create a complete date range with zeros for missing dates
    if days_diff <= 31:
        # Daily format
        current = start
        while current <= end:
            current_str = current.strftime(date_format)
            
            # Find if there's data for this date
            data_for_date = next((t for t in trends if t.date_group == current_str), None)
            
            labels.append(current.strftime(date_label_format))
            bookings.append(data_for_date.booking_count if data_for_date else 0)
            revenue.append(float(data_for_date.revenue) if data_for_date else 0)
            
            current += timedelta(days=1)
    elif days_diff <= 90:
        # Weekly format
        current = start
        while current <= end:
            week_num = int(current.strftime("%U"))
            year = current.strftime("%Y")
            current_str = f"{year}-{week_num:02d}"
            
            # Find if there's data for this week
            data_for_week = next((t for t in trends if t.date_group == current_str), None)
            
            labels.append(f"W{week_num}")
            bookings.append(data_for_week.booking_count if data_for_week else 0)
            revenue.append(float(data_for_week.revenue) if data_for_week else 0)
            
            # Move to next week
            current += timedelta(days=7)
    else:
        # Monthly format
        current_year = start.year
        current_month = start.month
        
        while (current_year < end.year) or (current_year == end.year and current_month <= end.month):
            current_str = f"{current_year}-{current_month:02d}"
            
            # Find if there's data for this month
            data_for_month = next((t for t in trends if t.date_group == current_str), None)
            
            month_name = calendar.month_abbr[current_month]
            labels.append(f"{month_name} {current_year}")
            bookings.append(data_for_month.booking_count if data_for_month else 0)
            revenue.append(float(data_for_month.revenue) if data_for_month else 0)
            
            # Move to next month
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1
    
    return {
        "labels": labels,
        "bookings": bookings,
        "revenue": revenue
    }

def get_service_distribution(start_date, end_date, filters=None):
    """Get service distribution data for the pie chart"""
    if not filters:
        filters = {}
        
    photographer_filter = ""
    if filters.get("photographer"):
        photographer_filter = "AND b.photographer = '{}'".format(filters.get("photographer"))
    
    services = frappe.db.sql("""
        SELECT 
            s.service_name as service,
            COUNT(b.name) as count
        FROM 
            `tabBooking` b
        JOIN 
            `tabService` s ON b.service = s.name
        WHERE 
            b.booking_date BETWEEN %s AND %s
            {photographer_filter}
        GROUP BY 
            s.service_name
        ORDER BY 
            count DESC
        LIMIT 6
    """.format(photographer_filter=photographer_filter), (start_date, end_date), as_dict=True)
    
    labels = []
    values = []
    
    for service in services:
        labels.append(service.service)
        values.append(service.count)
    
    return {
        "labels": labels,
        "values": values
    }

def get_recent_bookings(filters=None):
    """Get recent booking data for the table"""
    if not filters:
        filters = {}
        
    conditions = []
    if filters.get("photographer"):
        conditions.append("b.photographer = '{}'".format(filters.get("photographer")))
    
    conditions_str = " AND ".join(conditions) if conditions else ""
    if conditions_str:
        conditions_str = "WHERE " + conditions_str
    
    bookings = frappe.db.sql("""
        SELECT 
            b.name,
            b.customer_name,
            s.service_name,
            p.full_name as photographer,
            b.booking_date,
            b.status,
            b.amount
        FROM 
            `tabBooking` b
        LEFT JOIN 
            `tabService` s ON b.service = s.name
        LEFT JOIN 
            `tabPhotographer` p ON b.photographer = p.name
        {conditions}
        ORDER BY 
            b.creation DESC
        LIMIT 10
    """.format(conditions=conditions_str), as_dict=True)
    
    return bookings

def get_photographer_performance(start_date, end_date):
    """Get photographer performance data for the bar chart"""
    photographers = frappe.db.sql("""
        SELECT 
            p.full_name as photographer,
            COUNT(b.name) as bookings,
            IFNULL(SUM(b.amount), 0) as revenue
        FROM 
            `tabBooking` b
        JOIN 
            `tabPhotographer` p ON b.photographer = p.name
        WHERE
            b.booking_date BETWEEN %s AND %s
        GROUP BY 
            p.full_name
        ORDER BY 
            bookings DESC
        LIMIT 5
    """, (start_date, end_date), as_dict=True)
    
    labels = []
    bookings_data = []
    revenue_data = []
    
    for p in photographers:
        labels.append(p.photographer)
        bookings_data.append(p.bookings)
        revenue_data.append(float(p.revenue))
    
    return {
        "labels": labels,
        "bookings": bookings_data,
        "revenue": revenue_data
    }

@frappe.whitelist()
def export_dashboard_data(start_date=None, end_date=None, photographer=None):
    """Export dashboard data as CSV or Excel"""
    from frappe.utils.xlsxutils import make_xlsx
    import csv
    import io
    
    # Get dashboard data
    data = get_dashboard_data(start_date, end_date, photographer)
    
    if not data:
        return None
    
    # Generate filename
    filename = "re_studio_dashboard_{0}_to_{1}.xlsx".format(
        start_date.replace("-", ""), 
        end_date.replace("-", "")
    )
    
    # Prepare worksheets data
    xlsx_data = {
        "Quick Stats": [
            ["Statistic", "Value"],
            ["Total Bookings", data["quick_stats"]["total_bookings"]],
            ["Pending Bookings", data["quick_stats"]["pending_bookings"]],
            ["Confirmed Bookings", data["quick_stats"]["confirmed_bookings"]],
            ["Total Revenue", data["quick_stats"]["total_revenue"]]
        ],
        "Booking Trends": [
            ["Date", "Bookings", "Revenue"]
        ],
        "Service Distribution": [
            ["Service", "Bookings"]
        ],
        "Photographer Performance": [
            ["Photographer", "Bookings", "Revenue"]
        ],
        "Recent Bookings": [
            ["Customer", "Service", "Photographer", "Date", "Status", "Amount"]
        ]
    }
    
    # Add booking trends data
    for i in range(len(data["booking_trends"]["labels"])):
        xlsx_data["Booking Trends"].append([
            data["booking_trends"]["labels"][i],
            data["booking_trends"]["bookings"][i],
            data["booking_trends"]["revenue"][i]
        ])
    
    # Add service distribution data
    for i in range(len(data["service_distribution"]["labels"])):
        xlsx_data["Service Distribution"].append([
            data["service_distribution"]["labels"][i],
            data["service_distribution"]["values"][i]
        ])
    
    # Add photographer performance data
    for i in range(len(data["photographer_performance"]["labels"])):
        xlsx_data["Photographer Performance"].append([
            data["photographer_performance"]["labels"][i],
            data["photographer_performance"]["bookings"][i],
            data["photographer_performance"]["revenue"][i]
        ])
    
    # Add recent bookings data
    for booking in data["recent_bookings"]:
        xlsx_data["Recent Bookings"].append([
            booking["customer_name"],
            booking["service_name"],
            booking["photographer"],
            booking["booking_date"],
            booking["status"],
            booking["amount"]
        ])
    
    # Create Excel file
    xlsx_file = make_xlsx(xlsx_data, "Re Studio Booking")
    
    return {
        "filename": filename,
        "content": xlsx_file.getvalue()
    }
