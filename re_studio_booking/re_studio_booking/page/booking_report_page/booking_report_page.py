# Copyright (c) 2023, RE Studio and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, add_days, add_months, get_first_day, get_last_day, nowdate
from datetime import datetime, timedelta
import json

@frappe.whitelist()
def generate_report(report_type, date_range, start_date=None, end_date=None, status=None, photographer=None):
    """Generate booking report based on filters"""
    try:
        # Get date filters
        filters = get_date_filters(date_range, start_date, end_date)
        
        # Generate report based on type
        if report_type == 'Booking Summary':
            return generate_booking_summary(filters, status)
        elif report_type == 'Photographer Performance':
            return generate_photographer_performance(filters, photographer)
        elif report_type == 'Service Popularity':
            return generate_service_popularity(filters)
        elif report_type == 'Revenue Report':
            return generate_revenue_report(filters)
        else:
            frappe.throw(_('Invalid report type'))
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _('Error generating booking report'))
        frappe.throw(_('Error generating report: {0}').format(str(e)))

def get_date_filters(date_range, start_date=None, end_date=None):
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
    elif date_range == 'Custom':
        if not start_date or not end_date:
            frappe.throw(_('Start date and end date are required for custom date range'))
        return {
            'booking_date': ['between', [getdate(start_date), getdate(end_date)]]
        }
    else:
        frappe.throw(_('Invalid date range'))

def generate_booking_summary(filters, status=None):
    """Generate booking summary report"""
    # Add status filter if provided
    if status and status != 'All':
        filters['status'] = status
    
    # Get bookings
    bookings = frappe.get_all(
        'Booking',
        filters=filters,
        fields=[
            'name', 'client', 'client_name', 'booking_date', 'start_time', 'end_time',
            'service', 'photographer', 'status', 'total_amount'
        ],
        order_by='booking_date desc, start_time desc'
    )
    
    # Calculate status counts
    status_counts = {}
    for booking in bookings:
        if booking.status not in status_counts:
            status_counts[booking.status] = 0
        status_counts[booking.status] += 1
    
    # Get bookings by date for chart
    bookings_by_date = {}
    for booking in bookings:
        date_str = booking.booking_date.strftime('%Y-%m-%d')
        if date_str not in bookings_by_date:
            bookings_by_date[date_str] = 0
        bookings_by_date[date_str] += 1
    
    # Format for chart
    chart_data = {
        'labels': list(bookings_by_date.keys()),
        'datasets': [{
            'name': _('Bookings'),
            'values': list(bookings_by_date.values())
        }]
    }
    
    return {
        'total_bookings': len(bookings),
        'status_counts': status_counts,
        'bookings': bookings,
        'chart_data': chart_data
    }

def generate_photographer_performance(filters, photographer=None):
    """Generate photographer performance report"""
    # Add photographer filter if provided
    if photographer and photographer != 'All':
        filters['photographer'] = photographer
    
    # Add completed status filter for accurate performance metrics
    filters['status'] = 'Completed'
    
    # Get bookings
    bookings = frappe.get_all(
        'Booking',
        filters=filters,
        fields=[
            'name', 'photographer', 'booking_date', 'start_time', 'end_time',
            'service', 'status', 'total_amount'
        ]
    )
    
    # Calculate performance by photographer
    performance = {}
    for booking in bookings:
        if not booking.photographer:
            continue
            
        if booking.photographer not in performance:
            performance[booking.photographer] = {
                'photographer': booking.photographer,
                'total_bookings': 0,
                'total_minutes': 0
            }
        
        # Calculate session duration in minutes
        try:
            start_dt = datetime.combine(booking.booking_date, datetime.strptime(booking.start_time, '%H:%M:%S').time())
            end_dt = datetime.combine(booking.booking_date, datetime.strptime(booking.end_time, '%H:%M:%S').time())
            duration = (end_dt - start_dt).total_seconds() / 60
        except Exception:
            duration = 0
        
        performance[booking.photographer]['total_bookings'] += 1
        performance[booking.photographer]['total_minutes'] += duration
    
    # Convert to list and sort by total bookings
    performance_list = list(performance.values())
    performance_list.sort(key=lambda x: x['total_bookings'], reverse=True)
    
    # Calculate total hours for all photographers
    total_hours = sum(item['total_minutes'] for item in performance_list) / 60
    
    return {
        'photographer_performance': performance_list,
        'total_bookings': sum(item['total_bookings'] for item in performance_list),
        'total_hours': total_hours
    }

def generate_service_popularity(filters):
    """Generate service popularity report"""
    # Get bookings grouped by service
    service_popularity = frappe.db.sql("""
        SELECT service, COUNT(*) as booking_count
        FROM `tabBooking`
        WHERE {where_conditions}
        GROUP BY service
        ORDER BY booking_count DESC
    """.format(
        where_conditions=get_where_conditions(filters)
    ), filters, as_dict=1)
    
    # Get service details (Arabic name and category)
    for item in service_popularity:
        service_doc = frappe.get_doc('Service', item.service)
        item.service_name = service_doc.service_name_ar
        item.category = service_doc.category
    
    # Calculate total bookings
    total_bookings = sum(item.booking_count for item in service_popularity)
    
    # Get bookings by category for chart
    category_counts = {}
    for item in service_popularity:
        if item.category not in category_counts:
            category_counts[item.category] = 0
        category_counts[item.category] += item.booking_count
    
    # Format for chart
    chart_data = {
        'labels': list(category_counts.keys()),
        'datasets': [{
            'name': _('Bookings'),
            'values': list(category_counts.values())
        }]
    }
    
    return {
        'service_popularity': service_popularity,
        'total_bookings': total_bookings,
        'chart_data': chart_data
    }

def generate_revenue_report(filters):
    """Generate revenue report"""
    # Add completed status filter for accurate revenue metrics
    filters['status'] = 'Completed'
    
    # Get revenue by service
    revenue_by_service = frappe.db.sql("""
        SELECT service, COUNT(*) as booking_count, SUM(total_amount) as total_revenue
        FROM `tabBooking`
        WHERE {where_conditions}
        GROUP BY service
        ORDER BY total_revenue DESC
    """.format(
        where_conditions=get_where_conditions(filters)
    ), filters, as_dict=1)
    
    # Calculate total revenue and bookings
    total_revenue = sum(item.total_revenue for item in revenue_by_service)
    total_bookings = sum(item.booking_count for item in revenue_by_service)
    
    return {
        'revenue_by_service': revenue_by_service,
        'total_revenue': total_revenue,
        'total_bookings': total_bookings
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