import frappe
from frappe import _

def check_permission(doctype, docname=None, ptype="read", ignore_roles=None):
    """
    Check permission for doctype and docname, with customized permission bypass for specific scenarios
    
    Args:
        doctype (str): DocType to check permission
        docname (str, optional): Name of the document
        ptype (str, optional): Permission type (read, write, create, etc.)
        ignore_roles (list, optional): List of roles to bypass permission check
        
    Returns:
        bool: True if permission is granted, False otherwise
    """
    # Define critical roles that should always have permission
    critical_roles = ["System Manager", "Administrator", "Re Studio Manager"]
    
    # Add any roles passed to ignore_roles parameter
    if ignore_roles:
        critical_roles.extend(ignore_roles)
    
    # Check if user has any of the critical roles
    for role in critical_roles:
        if frappe.has_role(role):
            return True
            
    # Special case for Booking doctype
    if doctype == "Booking":
        # All users should be able to read bookings
        if ptype == "read":
            return True
        
        # For package services, bypass permission check
        if "package_services" in frappe.form_dict:
            return True
    
    # For package service items, always allow read access
    if doctype in ["Package Service Item", "Booking Package Service"]:
        if ptype == "read":
            return True
    
    # For normal permission check, use standard Frappe permission system
    return frappe.has_permission(doctype, ptype, docname)

def custom_has_permission(doctype, ptype="read", doc=None):
    """
    Custom permission check function to be used as a replacement for frappe.has_permission
    in custom views and controllers
    """
    return check_permission(doctype, docname=doc.name if doc else None, ptype=ptype)
