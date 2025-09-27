# Copyright (c) 2023, RE Studio and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, add_days, add_months, get_first_day, get_last_day, nowdate
from datetime import datetime, timedelta
import json

@frappe.whitelist()
def get_dashboard_data(date_range):
    """Get dashboard data for booking reports"""
    try:
        # Get date filters
        filters = get_date_filters(date_range)
        
        # Get booking data
        booking_data = get_booking_data(filters)
        
        # Get photographer performance
        photographer_data = get_photographer_performance(filters)
        
        # Get service popularity
        service_data = get_service_popularity(filters)
        
        # Get revenue data
        revenue_data = get_revenue_data(filters)
        
        return {
            'booking_data': booking_data,
            'photographer_data': photographer_data,
            'service_data': service_data,
            'revenue_data': revenue_data
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _('Error generating dashboard data'))
        return {'error': str(e)}

def get_date_filters(date_range):
    """Get date filters based on selected date range"""
    today = getdate(nowdate())
    
    if date_range == 'Today':
        return {
            'booking_date': ['=', today]
        }
    elif date_range == 'This Week':
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        return {
            'booking_date': ['between', [week_start, week_end]]
        }
    elif date_range == 'This Month':
        month_start = get_first_day(today)
        month_end = get_last_day(today)
        return {
            'booking_date': ['between', [month_start, month_end]]
        }
    elif date_range == 'Last Month':
        last_month = add_months(today, -1)
        month_start = get_first_day(last_month)
        month_end = get_last_day(last_month)
        return {
            'booking_date': ['between', [month_start, month_end]]
        }
    elif date_range == 'This Year':
        year_start = getdate(f"{today.year}-01-01")
        year_end = getdate(f"{today.year}-12-31")
        return {
            'booking_date': ['between', [year_start, year_end]]
        }
    else:
        # Default to This Month
        month_start = get_first_day(today)
        month_end = get_last_day(today)
        return {
            'booking_date': ['between', [month_start, month_end]]
        }

def get_booking_data(filters):
    """Get booking data for dashboard"""
    # Get all bookings within date range
    bookings = frappe.get_all(
        'Booking',
        filters=filters,
        fields=[
            'name', 'customer_name', 'booking_date', 'start_time', 'end_time',
            'service', 'photographer', 'status', 'total_amount'
        ]
    )
    
    # Calculate status counts
    status_counts = {
        'Completed': 0,
        'Confirmed': 0,
        'Cancelled': 0
    }
    
    for booking in bookings:
        if booking.status in status_counts:
            status_counts[booking.status] += 1
        else:
            status_counts[booking.status] = 1
    
    return {
        'total_bookings': len(bookings),
        'status_counts': status_counts
    }

def get_photographer_performance(filters):
    """Get photographer performance data for dashboard"""
    # Add completed status filter for accurate performance metrics
    completed_filters = filters.copy()
    completed_filters['status'] = 'Completed'
    
    # Get bookings grouped by photographer
    photographer_performance = frappe.db.sql("""
        SELECT photographer, COUNT(*) as total_bookings, 
        SUM(TIME_TO_SEC(TIMEDIFF(end_time, start_time)) / 60) as total_minutes
        FROM `tabBooking`
        WHERE {where_conditions}
        GROUP BY photographer
        ORDER BY total_bookings DESC
        LIMIT 10
    """.format(
        where_conditions=get_where_conditions(completed_filters)
    ), completed_filters, as_dict=1)
    
    return photographer_performance

def get_service_popularity(filters):
    """Get service popularity data for dashboard"""
    # Get bookings grouped by service
    service_popularity = frappe.db.sql("""
        SELECT service, COUNT(*) as booking_count
        FROM `tabBooking`
        WHERE {where_conditions}
        GROUP BY service
        ORDER BY booking_count DESC
        LIMIT 5
    """.format(
        where_conditions=get_where_conditions(filters)
    ), filters, as_dict=1)
    
    # Get service details (Arabic name and category)
    for item in service_popularity:
        service_doc = frappe.get_doc('Service', item.service)
        item.service_name = service_doc.service_name_ar
        item.category = service_doc.category
    
    return service_popularity

def get_revenue_data(filters):
    """Get revenue data for dashboard"""
    # Add completed status filter for accurate revenue metrics
    completed_filters = filters.copy()
    completed_filters['status'] = 'Completed'
    
    # Get revenue by service
    revenue_by_service = frappe.db.sql("""
        SELECT service, COUNT(*) as booking_count, SUM(total_amount) as total_revenue
        FROM `tabBooking`
        WHERE {where_conditions}
        GROUP BY service
        ORDER BY total_revenue DESC
        LIMIT 5
    """.format(
        where_conditions=get_where_conditions(completed_filters)
    ), completed_filters, as_dict=1)
    
    # Calculate total revenue
    total_revenue = sum(item.total_revenue for item in revenue_by_service)
    
    return {
        'revenue_by_service': revenue_by_service,
        'total_revenue': total_revenue
    }

def get_where_conditions(filters):
    """Generate WHERE clause for SQL queries based on filters"""
    conditions = []
    
    for key, value in filters.items():
        if isinstance(value, list) and value[0] == 'between':
            conditions.append(f"`{key}` BETWEEN %({key}_start)s AND %({key}_end)s")
            filters[f"{key}_start"] = value[1][0]
            filters[f"{key}_end"] = value[1][1]
            del filters[key]
        elif isinstance(value, list) and value[0] == '=':
            conditions.append(f"`{key}` = %({key})s")
            filters[key] = value[1]
        else:
            conditions.append(f"`{key}` = %({key})s")
    
    return " AND ".join(conditions)