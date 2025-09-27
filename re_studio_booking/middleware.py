import frappe
import json
import re

def api_permission_middleware():
    """
    Middleware to handle custom permission logic for API calls
    This middleware intercepts certain API requests and applies custom permission logic
    """
    if not frappe.local.request:
        return
    
    # Skip for non-API requests
    if not frappe.local.request.path.startswith('/api/'):
        return
    
    # Skip for authentication requests
    if frappe.local.request.path.startswith('/api/method/login'):
        return
    
    # Special handling for package services
    if 'package_services' in frappe.local.request.path or 'get_package_services' in frappe.local.request.path:
        # Always allow these requests by setting user to Administrator temporarily
        original_user = frappe.session.user
        try:
            frappe.set_user('Administrator')
            # Process the request
            frappe.local.response = process_request_with_admin_permissions()
        finally:
            # Restore original user
            frappe.set_user(original_user)
        return frappe.local.response

def process_request_with_admin_permissions():
    """Process the current request with Administrator permissions"""
    # This is a placeholder function that would need to be implemented
    # to correctly process the request with Administrator permissions
    pass
