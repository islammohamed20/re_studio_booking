# Performance Optimization for Re Studio Booking

import frappe
from frappe import _
from datetime import datetime, timedelta
import json

# Database Query Optimization
def get_bookings_optimized(filters=None, fields=None, limit=20, offset=0):
    """Optimized query for fetching bookings with proper indexing"""
    if not fields:
        fields = [
            'name', 'client_name', 'service_name', 'photographer',
            'booking_date', 'status', 'total_amount', 'creation'
        ]
    
    query = """
        SELECT {fields}
        FROM `tabBooking` 
        WHERE 1=1
    """.format(fields=', '.join(fields))
    
    conditions = []
    values = []
    
    if filters:
        for key, value in filters.items():
            if key == 'booking_date_range':
                conditions.append("booking_date BETWEEN %s AND %s")
                values.extend([value[0], value[1]])
            elif key == 'status':
                if isinstance(value, list):
                    placeholders = ', '.join(['%s'] * len(value))
                    conditions.append(f"status IN ({placeholders})")
                    values.extend(value)
                else:
                    conditions.append("status = %s")
                    values.append(value)
            elif key == 'photographer':
                conditions.append("photographer = %s")
                values.append(value)
            elif key == 'service':
                conditions.append("service = %s")
                values.append(value)
    
    if conditions:
        query += " AND " + " AND ".join(conditions)
    
    query += " ORDER BY creation DESC LIMIT %s OFFSET %s"
    values.extend([limit, offset])
    
    return frappe.db.sql(query, values, as_dict=True)

def get_dashboard_stats_cached():
    """Get dashboard statistics with caching"""
    cache_key = f"dashboard_stats_{frappe.session.user}"
    
    # Try to get from cache first
    stats = frappe.cache().get_value(cache_key)
    
    if stats is None:
        stats = {
            'total_bookings': get_total_bookings(),
            'pending_bookings': get_pending_bookings(),
            'confirmed_bookings': get_confirmed_bookings(),
            'today_bookings': get_today_bookings(),
            'this_month_revenue': get_month_revenue(),
            'active_photographers': get_active_photographers_count()
        }
        
        # Cache for 5 minutes
        frappe.cache().set_value(cache_key, stats, expires_in_sec=300)
    
    return stats

def get_total_bookings():
    """Get total bookings count with optimized query"""
    return frappe.db.count('Booking')

def get_pending_bookings():
    """Get pending bookings count"""
    return frappe.db.count('Booking', {'status': 'Pending'})

def get_confirmed_bookings():
    """Get confirmed bookings count"""
    return frappe.db.count('Booking', {'status': 'Confirmed'})

def get_today_bookings():
    """Get today's bookings count"""
    today = frappe.utils.today()
    return frappe.db.count('Booking', {'booking_date': ['like', f'{today}%']})

def get_month_revenue():
    """Get current month revenue"""
    from frappe.utils import get_first_day, get_last_day
    
    first_day = get_first_day(frappe.utils.today())
    last_day = get_last_day(frappe.utils.today())
    
    result = frappe.db.sql("""
        SELECT COALESCE(SUM(total_amount), 0) as revenue
        FROM `tabBooking`
        WHERE booking_date BETWEEN %s AND %s
        AND status IN ('Confirmed', 'Completed', 'Paid')
    """, (first_day, last_day), as_dict=True)
    
    return result[0].revenue if result else 0

def get_active_photographers_count():
    """Get active photographers count based on status field"""
    return frappe.db.count('Photographer', {'status': 'Active'})

# Chart data with caching
@frappe.whitelist()
def get_monthly_bookings_chart():
    """Get monthly bookings data for charts with caching"""
    cache_key = "monthly_bookings_chart"
    
    chart_data = frappe.cache().get_value(cache_key)
    
    if chart_data is None:
        # Get last 6 months data
        six_months_ago = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        
        query = """
            SELECT 
                DATE_FORMAT(booking_date, '%%Y-%%m') as month,
                COUNT(*) as count,
                SUM(total_amount) as revenue
            FROM `tabBooking`
            WHERE booking_date >= %s
            GROUP BY DATE_FORMAT(booking_date, '%%Y-%%m')
            ORDER BY month
        """
        
        results = frappe.db.sql(query, (six_months_ago,), as_dict=True)
        
        chart_data = {
            'labels': [result.month for result in results],
            'datasets': [
                {
                    'label': 'Bookings',
                    'data': [result.count for result in results],
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)'
                },
                {
                    'label': 'Revenue',
                    'data': [float(result.revenue) for result in results],
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'yAxisID': 'revenue'
                }
            ]
        }
        
        # Cache for 1 hour
        frappe.cache().set_value(cache_key, chart_data, expires_in_sec=3600)
    
    return chart_data

@frappe.whitelist()
def get_service_popularity_chart():
    """Get service popularity chart data with caching"""
    cache_key = "service_popularity_chart"
    
    chart_data = frappe.cache().get_value(cache_key)
    
    if chart_data is None:
        query = """
            SELECT 
                s.service_name_en as service,
                COUNT(b.name) as count,
                SUM(b.total_amount) as revenue
            FROM `tabBooking` b
            JOIN `tabService` s ON b.service = s.name
            WHERE b.creation >= DATE_SUB(NOW(), INTERVAL 3 MONTH)
            GROUP BY s.service_name_en
            ORDER BY count DESC
            LIMIT 10
        """
        
        results = frappe.db.sql(query, as_dict=True)
        
        chart_data = {
            'labels': [result.service for result in results],
            'datasets': [{
                'data': [result.count for result in results],
                'backgroundColor': [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
                    '#9966FF', '#FF9F40', '#FF6384', '#36A2EB',
                    '#FFCE56', '#4BC0C0'
                ]
            }]
        }
        
        # Cache for 2 hours
        frappe.cache().set_value(cache_key, chart_data, expires_in_sec=7200)
    
    return chart_data

# Database indexing recommendations
def create_performance_indexes():
    """Create database indexes for better performance"""
    indexes = [
        ("tabBooking", "booking_date", "booking_date_idx"),
        ("tabBooking", "status", "booking_status_idx"),
        ("tabBooking", "photographer", "booking_photographer_idx"),
        ("tabBooking", "service", "booking_service_idx"),
        ("tabBooking", "client", "booking_client_idx"),
        ("tabBooking", "creation", "booking_creation_idx"),
        ("tabService", "is_active", "service_active_idx"),
        ("tabPhotographer", "status", "photographer_status_idx"),
        ("tabClient", "mobile_no", "client_mobile_idx"),
        ("tabClient", "email_id", "client_email_idx"),
    ]
    
    for table, column, index_name in indexes:
        try:
            # Check if index exists
            existing_indexes = frappe.db.sql(f"""
                SELECT COUNT(*) as count
                FROM information_schema.statistics 
                WHERE table_schema = %s 
                AND table_name = %s 
                AND index_name = %s
            """, (frappe.db.get_database(), table, index_name))
            
            if existing_indexes[0][0] == 0:
                # Create index
                frappe.db.sql(f"""
                    ALTER TABLE `{table}` 
                    ADD INDEX `{index_name}` (`{column}`)
                """)
                print(f"✅ Created index {index_name} on {table}.{column}")
            else:
                print(f"ℹ️ Index {index_name} already exists on {table}.{column}")
                
        except Exception as e:
            print(f"❌ Error creating index {index_name}: {str(e)}")

# Background job for cache warming
def warm_dashboard_cache():
    """Warm up dashboard cache in background"""
    try:
        # Warm up stats cache
        get_dashboard_stats_cached()
        
        # Warm up chart data cache
        get_monthly_bookings_chart()
        get_service_popularity_chart()
        
        frappe.logger().info("Dashboard cache warmed up successfully")
    except Exception as e:
        frappe.log_error(f"Error warming dashboard cache: {str(e)}")

# Pagination helper
def get_paginated_data(doctype, filters=None, fields=None, page=1, page_size=20, order_by="creation desc"):
    """Generic pagination function"""
    offset = (page - 1) * page_size
    
    # Get total count
    total_count = frappe.db.count(doctype, filters or {})
    
    # Get paginated data
    data = frappe.get_all(
        doctype,
        filters=filters or {},
        fields=fields or ['*'],
        order_by=order_by,
        limit=page_size,
        start=offset
    )
    
    total_pages = (total_count + page_size - 1) // page_size
    
    return {
        'data': data,
        'pagination': {
            'current_page': page,
            'page_size': page_size,
            'total_count': total_count,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }

# Image optimization
def optimize_service_image(image_path):
    """Optimize service images for better performance"""
    try:
        from PIL import Image
        import os
        
        if not os.path.exists(image_path):
            return None
        
        # Open and optimize image
        with Image.open(image_path) as img:
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large
            max_size = (800, 600)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save optimized version
            optimized_path = image_path.replace('.', '_optimized.')
            img.save(optimized_path, 'JPEG', quality=85, optimize=True)
            
            return optimized_path
            
    except Exception as e:
        frappe.log_error(f"Error optimizing image {image_path}: {str(e)}")
        return image_path

# Memory optimization
def cleanup_old_cache():
    """Clean up old cache entries"""
    try:
        # Clear cache entries older than 24 hours
        cache_keys_to_clean = [
            "dashboard_stats_*",
            "monthly_bookings_chart",
            "service_popularity_chart"
        ]
        
        for pattern in cache_keys_to_clean:
            frappe.cache().delete_keys(pattern)
        
        frappe.logger().info("Old cache entries cleaned up")
    except Exception as e:
        frappe.log_error(f"Error cleaning cache: {str(e)}")

# Performance monitoring
def log_slow_queries(query_time_threshold=1.0):
    """Log slow queries for optimization"""
    # This would be implemented with query monitoring
    # For now, just a placeholder for future implementation
    pass

def setup_performance_optimizations():
    """Setup all performance optimizations"""
    try:
        # Create database indexes
        create_performance_indexes()
        
        # Setup cache warming job
        frappe.get_doc({
            "doctype": "Scheduled Job Type",
            "method": "re_studio_booking.re_studio_booking.utils.performance.warm_dashboard_cache",
            "frequency": "Cron",
            "cron_format": "0 */6 * * *"  # Every 6 hours
        }).insert(ignore_if_duplicate=True)
        
        # Setup cache cleanup job  
        frappe.get_doc({
            "doctype": "Scheduled Job Type",
            "method": "re_studio_booking.re_studio_booking.utils.performance.cleanup_old_cache",
            "frequency": "Daily"
        }).insert(ignore_if_duplicate=True)
        
        frappe.db.commit()
        print("✅ Performance optimizations setup complete")
        
    except Exception as e:
        print(f"❌ Error setting up performance optimizations: {str(e)}")
        frappe.log_error(f"Performance setup error: {str(e)}")
