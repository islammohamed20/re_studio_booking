# Copyright (c) 2023, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, add_to_date, get_first_day, get_last_day

@frappe.whitelist()
def get_dashboard_data(date_range):
    """Get dashboard data based on date range"""
    # Get date filters
    date_filters = get_date_filters(date_range)
    
    # Get booking data
    booking_data = get_booking_data(date_filters)
    
    # Get photographer performance data
    photographer_performance = get_photographer_performance(date_filters)
    
    # Get service popularity data
    service_popularity = get_service_popularity(date_filters)
    
    # Get revenue data
    revenue_data = get_revenue_data(date_filters)
    
    # Combine all data
    dashboard_data = {
        "total_bookings": booking_data["total_bookings"],
        "status_counts": booking_data["status_counts"],
        "photographer_performance": photographer_performance,
        "service_popularity": service_popularity,
        "revenue_by_service": revenue_data["revenue_by_service"],
        "total_revenue": revenue_data["total_revenue"]
    }
    
    return dashboard_data

def get_date_filters(date_range):
    """Get date filters based on date range"""
    if date_range == "Custom":
        # For custom range, we would need start and end dates
        # Since this is a dashboard, we'll default to This Month if Custom is selected
        today = getdate()
        start_date = get_first_day(today)
        end_date = get_last_day(today)
        return {"booking_date": ["between", [start_date, end_date]]}
    elif date_range == "Today":
        today = getdate()
        return {"booking_date": today}
    elif date_range == "This Week":
        today = getdate()
        start_date = add_to_date(today, days=-(today.weekday()), hours=0, minutes=0, seconds=0)
        end_date = add_to_date(start_date, days=6, hours=0, minutes=0, seconds=0)
        return {"booking_date": ["between", [start_date, end_date]]}
    elif date_range == "This Month":
        today = getdate()
        start_date = get_first_day(today)
        end_date = get_last_day(today)
        return {"booking_date": ["between", [start_date, end_date]]}
    elif date_range == "Last Month":
        today = getdate()
        last_month = add_to_date(today, months=-1)
        start_date = get_first_day(last_month)
        end_date = get_last_day(last_month)
        return {"booking_date": ["between", [start_date, end_date]]}
    elif date_range == "This Year":
        today = getdate()
        start_date = getdate(f"{today.year}-01-01")
        end_date = getdate(f"{today.year}-12-31")
        return {"booking_date": ["between", [start_date, end_date]]}
    else:
        return {}

def get_booking_data(date_filters):
    """Get booking data within date range"""
    # Get bookings
    bookings = frappe.get_all(
        "Booking",
        filters=date_filters,
        fields=[
            "name", "customer_name", "booking_date", "start_time", 
            "end_time", "service", "photographer", "status"
        ]
    )
    
    # Calculate summary statistics
    total_bookings = len(bookings)
    status_counts = {}
    
    for booking in bookings:
        status = booking.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        "bookings": bookings,
        "total_bookings": total_bookings,
        "status_counts": status_counts
    }

def get_photographer_performance(date_filters):
    """Get photographer performance data"""
    # Only include completed bookings for performance metrics
    filters = date_filters.copy()
    if "status" not in filters:
        filters["status"] = "Completed"
    
    # Get bookings grouped by photographer
    photographer_bookings = frappe.db.sql("""
        SELECT 
            photographer, 
            COUNT(*) as total_bookings,
            SUM(TIMESTAMPDIFF(MINUTE, start_time, end_time)) as total_minutes
        FROM `tabBooking`
        WHERE booking_date BETWEEN %(start_date)s AND %(end_date)s
        AND status = 'Completed'
        GROUP BY photographer
        ORDER BY total_bookings DESC
    """, {
        "start_date": date_filters.get("booking_date")[1][0] if date_filters.get("booking_date") and isinstance(date_filters.get("booking_date"), list) else getdate(),
        "end_date": date_filters.get("booking_date")[1][1] if date_filters.get("booking_date") and isinstance(date_filters.get("booking_date"), list) else getdate()
    }, as_dict=True)
    
    return photographer_bookings

def get_service_popularity(date_filters):
    """Get service popularity data"""
    # Get services grouped by popularity
    service_popularity = frappe.db.sql("""
        SELECT 
            service, 
            COUNT(*) as booking_count
        FROM `tabBooking`
        WHERE booking_date BETWEEN %(start_date)s AND %(end_date)s
        GROUP BY service
        ORDER BY booking_count DESC
    """, {
        "start_date": date_filters.get("booking_date")[1][0] if date_filters.get("booking_date") and isinstance(date_filters.get("booking_date"), list) else getdate(),
        "end_date": date_filters.get("booking_date")[1][1] if date_filters.get("booking_date") and isinstance(date_filters.get("booking_date"), list) else getdate()
    }, as_dict=True)
    
    # Get service details
    for service in service_popularity:
        try:
            service_doc = frappe.get_doc("Service", service.service)
            service["service_name"] = service_doc.service_name_ar
            service["category"] = service_doc.category
        except:
            service["service_name"] = service.service
            service["category"] = ""
    
    return service_popularity

def get_revenue_data(date_filters):
    """Get revenue data"""
    # Only include completed bookings for revenue metrics
    filters = date_filters.copy()
    if "status" not in filters:
        filters["status"] = "Completed"
    
    # Get revenue by service
    revenue_by_service = frappe.db.sql("""
        SELECT 
            service, 
            COUNT(*) as booking_count,
            SUM(price) as total_revenue
        FROM `tabBooking`
        WHERE booking_date BETWEEN %(start_date)s AND %(end_date)s
        AND status = 'Completed'
        GROUP BY service
        ORDER BY total_revenue DESC
    """, {
        "start_date": date_filters.get("booking_date")[1][0] if date_filters.get("booking_date") and isinstance(date_filters.get("booking_date"), list) else getdate(),
        "end_date": date_filters.get("booking_date")[1][1] if date_filters.get("booking_date") and isinstance(date_filters.get("booking_date"), list) else getdate()
    }, as_dict=True)
    
    # Calculate total revenue
    total_revenue = sum(item.total_revenue for item in revenue_by_service)
    
    return {
        "revenue_by_service": revenue_by_service,
        "total_revenue": total_revenue
    }