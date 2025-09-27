# Re Studio Booking - System Health Monitor

import frappe
from frappe import _
from datetime import datetime, timedelta
import json
import os

def run_health_check():
    """Run comprehensive health check on the Re Studio Booking system"""
    
    health_report = {
        'timestamp': datetime.now().isoformat(),
        'overall_status': 'healthy',
        'checks': {}
    }
    
    # Database health check
    health_report['checks']['database'] = check_database_health()
    
    # DocTypes health check
    health_report['checks']['doctypes'] = check_doctypes_health()
    
    # API health check
    health_report['checks']['api'] = check_api_health()
    
    # Performance health check  
    health_report['checks']['performance'] = check_performance_health()
    
    # Security health check
    health_report['checks']['security'] = check_security_health()
    
    # File system health check
    health_report['checks']['filesystem'] = check_filesystem_health()
    
    # Integration health check
    health_report['checks']['integrations'] = check_integrations_health()
    
    # Calculate overall status
    failed_checks = [k for k, v in health_report['checks'].items() if v['status'] != 'healthy']
    if failed_checks:
        health_report['overall_status'] = 'warning' if len(failed_checks) <= 2 else 'critical'
        health_report['issues'] = failed_checks
    
    return health_report

def check_database_health():
    """Check database connectivity and table integrity"""
    check_result = {
        'status': 'healthy',
        'details': {},
        'issues': []
    }
    
    try:
        # Test basic connectivity
        frappe.db.sql("SELECT 1")
        check_result['details']['connectivity'] = 'OK'
        
        # Check critical tables exist
        critical_tables = [
            'tabBooking',
            'tabService', 
            'tabPhotographer',
            'tabClient',
            'tabCategory'
        ]
        
        missing_tables = []
        for table in critical_tables:
            try:
                frappe.db.sql(f"SELECT COUNT(*) FROM `{table}` LIMIT 1")
            except Exception:
                missing_tables.append(table)
        
        if missing_tables:
            check_result['status'] = 'critical'
            check_result['issues'].append(f"Missing tables: {', '.join(missing_tables)}")
        else:
            check_result['details']['tables'] = 'All critical tables exist'
        
        # Check data integrity
        integrity_issues = []
        
        # Check for orphaned bookings (bookings without valid client/service/photographer)
        orphaned_bookings = frappe.db.sql("""
            SELECT b.name
            FROM `tabBooking` b
            LEFT JOIN `tabClient` c ON b.client = c.name
            LEFT JOIN `tabService` s ON b.service = s.name  
            LEFT JOIN `tabPhotographer` p ON b.photographer = p.name
            WHERE c.name IS NULL OR s.name IS NULL OR p.name IS NULL
        """)
        
        if orphaned_bookings:
            integrity_issues.append(f"Found {len(orphaned_bookings)} orphaned bookings")
        
        if integrity_issues:
            check_result['status'] = 'warning'
            check_result['issues'].extend(integrity_issues)
        else:
            check_result['details']['data_integrity'] = 'OK'
            
        # Check database size and growth
        db_size = frappe.db.sql("""
            SELECT 
                ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS db_size_mb
            FROM information_schema.tables 
            WHERE table_schema = %s
        """, (frappe.db.get_database(),))
        
        check_result['details']['database_size_mb'] = db_size[0][0] if db_size else 0
        
    except Exception as e:
        check_result['status'] = 'critical'
        check_result['issues'].append(f"Database connectivity error: {str(e)}")
    
    return check_result

def check_doctypes_health():
    """Check DocTypes configuration and consistency"""
    check_result = {
        'status': 'healthy',
        'details': {},
        'issues': []
    }
    
    try:
        critical_doctypes = [
            'Booking',
            'Service',
            'Photographer', 
            'Client',
            'Category',
            'General Settings'
        ]
        
        missing_doctypes = []
        for doctype in critical_doctypes:
            if not frappe.db.exists('DocType', doctype):
                missing_doctypes.append(doctype)
        
        if missing_doctypes:
            check_result['status'] = 'critical'
            check_result['issues'].append(f"Missing DocTypes: {', '.join(missing_doctypes)}")
        else:
            check_result['details']['doctypes'] = 'All critical DocTypes exist'
        
        # Check for DocTypes without proper permissions
        doctypes_without_permissions = []
        for doctype in critical_doctypes:
            if frappe.db.exists('DocType', doctype):
                permissions = frappe.get_all('DocPerm', filters={'parent': doctype})
                if not permissions:
                    doctypes_without_permissions.append(doctype)
        
        if doctypes_without_permissions:
            check_result['status'] = 'warning'
            check_result['issues'].append(f"DocTypes without permissions: {', '.join(doctypes_without_permissions)}")
        
        # Check for mandatory fields
        booking_mandatory_fields = frappe.get_meta('Booking').get_reqd_fields()
        if len(booking_mandatory_fields) < 3:  # Should have at least client, service, booking_date
            check_result['status'] = 'warning'
            check_result['issues'].append("Booking DocType missing required mandatory fields")
        
    except Exception as e:
        check_result['status'] = 'critical'
        check_result['issues'].append(f"DocType check error: {str(e)}")
    
    return check_result

def check_api_health():
    """Check API endpoints functionality"""
    check_result = {
        'status': 'healthy',
        'details': {},
        'issues': []
    }
    
    try:
        # Test critical API endpoints
        from re_studio_booking.re_studio_booking.utils.performance import get_dashboard_stats_cached
        
        # Test dashboard stats API
        try:
            stats = get_dashboard_stats_cached()
            if isinstance(stats, dict) and 'total_bookings' in stats:
                check_result['details']['dashboard_api'] = 'OK'
            else:
                check_result['issues'].append("Dashboard API returning invalid data")
        except Exception as e:
            check_result['issues'].append(f"Dashboard API error: {str(e)}")
        
        # Test booking creation API (dry run)
        try:
            from re_studio_booking.re_studio_booking.api import create_booking
            # This is just checking if the function exists and can be imported
            check_result['details']['booking_api'] = 'OK'
        except Exception as e:
            check_result['issues'].append(f"Booking API import error: {str(e)}")
        
        if check_result['issues']:
            check_result['status'] = 'warning'
        
    except Exception as e:
        check_result['status'] = 'critical'
        check_result['issues'].append(f"API health check error: {str(e)}")
    
    return check_result

def check_performance_health():
    """Check system performance metrics"""
    check_result = {
        'status': 'healthy',
        'details': {},
        'issues': []
    }
    
    try:
        # Check query performance
        start_time = datetime.now()
        frappe.db.sql("SELECT COUNT(*) FROM `tabBooking`")
        query_time = (datetime.now() - start_time).total_seconds()
        
        check_result['details']['booking_count_query_time'] = f"{query_time:.3f}s"
        
        if query_time > 2.0:  # Slow query threshold
            check_result['status'] = 'warning'
            check_result['issues'].append(f"Slow query performance: {query_time:.3f}s")
        
        # Check database indexes
        indexes = frappe.db.sql("""
            SELECT COUNT(*) as index_count
            FROM information_schema.statistics 
            WHERE table_schema = %s 
            AND table_name LIKE 'tab%'
        """, (frappe.db.get_database(),))
        
        index_count = indexes[0][0] if indexes else 0
        check_result['details']['database_indexes'] = index_count
        
        if index_count < 10:  # Should have at least some indexes
            check_result['status'] = 'warning'
            check_result['issues'].append("Low number of database indexes, performance may be impacted")
        
        # Check cache functionality
        try:
            test_key = "health_check_test"
            test_value = "test_data"
            frappe.cache().set_value(test_key, test_value)
            cached_value = frappe.cache().get_value(test_key)
            
            if cached_value == test_value:
                check_result['details']['cache'] = 'OK'
            else:
                check_result['issues'].append("Cache not working properly")
                
            frappe.cache().delete_value(test_key)
        except Exception as e:
            check_result['issues'].append(f"Cache error: {str(e)}")
        
        if check_result['issues']:
            check_result['status'] = 'warning'
    
    except Exception as e:
        check_result['status'] = 'critical'
        check_result['issues'].append(f"Performance check error: {str(e)}")
    
    return check_result

def check_security_health():
    """Check security configurations"""
    check_result = {
        'status': 'healthy',
        'details': {},
        'issues': []
    }
    
    try:
        # Check if default roles exist
        required_roles = ["Studio Manager", "Studio Admin", "Booking Staff", "Photographer"]
        missing_roles = []
        
        for role in required_roles:
            if not frappe.db.exists("Role", role):
                missing_roles.append(role)
        
        if missing_roles:
            check_result['status'] = 'warning' 
            check_result['issues'].append(f"Missing security roles: {', '.join(missing_roles)}")
        else:
            check_result['details']['security_roles'] = 'All required roles exist'
        
        # Check for users with excessive permissions
        admin_users = frappe.get_all("Has Role", 
            filters={"role": "System Manager"},
            fields=["parent"]
        )
        
        if len(admin_users) > 5:  # Too many admins might be a security risk
            check_result['status'] = 'warning'
            check_result['issues'].append(f"High number of System Manager users: {len(admin_users)}")
        
        # Check password policy (if enabled)
        system_settings = frappe.get_single("System Settings")
        if not getattr(system_settings, "enable_password_policy", False):
            check_result['issues'].append("Password policy not enabled")
        
        # Check session security
        if not getattr(system_settings, "session_expiry", None):
            check_result['issues'].append("Session expiry not configured")
        
        if check_result['issues'] and check_result['status'] == 'healthy':
            check_result['status'] = 'warning'
    
    except Exception as e:
        check_result['status'] = 'critical'
        check_result['issues'].append(f"Security check error: {str(e)}")
    
    return check_result

def check_filesystem_health():
    """Check file system and uploads"""
    check_result = {
        'status': 'healthy',
        'details': {},
        'issues': []
    }
    
    try:
        # Check if uploads directory exists and is writable
        uploads_path = frappe.get_site_path("public", "files")
        
        if os.path.exists(uploads_path):
            if os.access(uploads_path, os.W_OK):
                check_result['details']['uploads_directory'] = 'OK'
            else:
                check_result['status'] = 'critical'
                check_result['issues'].append("Uploads directory not writable")
        else:
            check_result['status'] = 'critical'
            check_result['issues'].append("Uploads directory does not exist")
        
        # Check disk space
        import shutil
        total, used, free = shutil.disk_usage(frappe.get_site_path())
        
        free_percentage = (free / total) * 100
        check_result['details']['disk_free_percentage'] = f"{free_percentage:.2f}%"
        
        if free_percentage < 10:  # Less than 10% free space
            check_result['status'] = 'critical'
            check_result['issues'].append(f"Low disk space: {free_percentage:.2f}% free")
        elif free_percentage < 20:  # Less than 20% free space
            check_result['status'] = 'warning'
            check_result['issues'].append(f"Disk space getting low: {free_percentage:.2f}% free")
        
        # Check for orphaned files
        # This would require a more complex check, skipping for now
        
    except Exception as e:
        check_result['status'] = 'critical'
        check_result['issues'].append(f"Filesystem check error: {str(e)}")
    
    return check_result

def check_integrations_health():
    """Check external integrations"""
    check_result = {
        'status': 'healthy',
        'details': {},
        'issues': []
    }
    
    try:
        # Check email configuration
        email_account = frappe.get_single("Email Account")
        if email_account and email_account.enable_outgoing:
            check_result['details']['email_outgoing'] = 'Configured'
        else:
            check_result['status'] = 'warning'
            check_result['issues'].append("Outgoing email not configured")
        
        # Check if required Python packages are installed
        required_packages = ['pillow', 'requests']  # Add more as needed
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            check_result['status'] = 'warning'
            check_result['issues'].append(f"Missing Python packages: {', '.join(missing_packages)}")
        else:
            check_result['details']['python_packages'] = 'All required packages installed'
        
        # Check scheduler status
        scheduler_settings = frappe.get_single("System Settings")
        if not getattr(scheduler_settings, "enable_scheduler", True):
            check_result['status'] = 'warning'
            check_result['issues'].append("Background scheduler is disabled")
        
    except Exception as e:
        check_result['status'] = 'critical'
        check_result['issues'].append(f"Integration check error: {str(e)}")
    
    return check_result

@frappe.whitelist()
def get_system_health():
    """API endpoint to get system health status"""
    if not frappe.has_permission("System Settings", "read"):
        frappe.throw(_("No permission to access system health"))
    
    return run_health_check()

def generate_health_report():
    """Generate a detailed health report"""
    health_data = run_health_check()
    
    report = f"""
# Re Studio Booking - System Health Report
Generated: {health_data['timestamp']}
Overall Status: {health_data['overall_status'].upper()}

## Summary
"""
    
    for check_name, check_data in health_data['checks'].items():
        report += f"\n### {check_name.title()}: {check_data['status'].upper()}\n"
        
        if check_data.get('details'):
            report += "**Details:**\n"
            for key, value in check_data['details'].items():
                report += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        if check_data.get('issues'):
            report += "**Issues:**\n"
            for issue in check_data['issues']:
                report += f"- ❌ {issue}\n"
    
    if health_data.get('issues'):
        report += f"\n## Action Required\nThe following components need attention:\n"
        for issue in health_data['issues']:
            report += f"- {issue}\n"
    
    return report

def setup_health_monitoring():
    """Setup scheduled health monitoring"""
    try:
        # Create scheduled job for health monitoring
        if not frappe.db.exists("Scheduled Job Type", "re_studio_booking_health_check"):
            frappe.get_doc({
                "doctype": "Scheduled Job Type",
                "name": "re_studio_booking_health_check",
                "method": "re_studio_booking.re_studio_booking.utils.health_monitor.log_health_status",
                "frequency": "Daily",
                "description": "Daily health check for Re Studio Booking system"
            }).insert()
        
        frappe.db.commit()
        return True
        
    except Exception as e:
        frappe.log_error(f"Error setting up health monitoring: {str(e)}")
        return False

def log_health_status():
    """Log health status for monitoring"""
    try:
        health_data = run_health_check()
        
        # Log to system
        frappe.logger().info(f"Re Studio Health Check: {health_data['overall_status']}")
        
        # If critical issues, send alert
        if health_data['overall_status'] == 'critical':
            frappe.logger().error(f"Critical health issues detected: {health_data.get('issues', [])}")
            
            # Could send email alert here if configured
            
        return health_data
        
    except Exception as e:
        frappe.log_error(f"Health monitoring error: {str(e)}")
        return None

if __name__ == "__main__":
    # Run health check from command line
    health_report = generate_health_report()
    print(health_report)
