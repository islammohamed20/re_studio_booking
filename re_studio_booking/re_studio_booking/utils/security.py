# Re Studio Booking Security & Permissions Configuration

import frappe
from frappe import _

def has_app_permission():
    """Check if user has permission to access Re Studio Booking app"""
    if frappe.session.user == "Administrator":
        return True
    
    # Check if user has any Re Studio role
    user_roles = frappe.get_roles(frappe.session.user)
    allowed_roles = [
        "Studio Manager", 
        "Photographer", 
        "Booking Staff",
        "Studio Admin"
    ]
    
    return any(role in user_roles for role in allowed_roles)

def has_booking_permission(doc, ptype):
    """Custom permission check for Booking doctype"""
    user = frappe.session.user
    user_roles = frappe.get_roles(user)
    
    # Administrator has all permissions
    if user == "Administrator":
        return True
    
    # Studio Manager has all permissions
    if "Studio Manager" in user_roles:
        return True
    
    # Studio Admin has all permissions except delete
    if "Studio Admin" in user_roles:
        return ptype != "delete"
    
    # Booking Staff can create, read, and update their own bookings
    if "Booking Staff" in user_roles:
        if ptype in ["create", "read"]:
            return True
        elif ptype in ["write", "cancel"]:
            # Can only modify bookings they created
            if doc.owner == user:
                return True
        return False
    
    # Photographer can only read bookings assigned to them
    if "Photographer" in user_roles:
        if ptype == "read":
            # Check if booking is assigned to this photographer
            photographer = frappe.get_value("Photographer", {"user": user}, "name")
            return doc.photographer == photographer if photographer else False
        return False
    
    return False

def has_service_permission(doc, ptype):
    """Custom permission check for Service doctype"""
    user_roles = frappe.get_roles(frappe.session.user)
    
    # Studio Manager and Admin can do everything
    if any(role in user_roles for role in ["Studio Manager", "Studio Admin"]):
        return True
    
    # Booking Staff can only read services
    if "Booking Staff" in user_roles:
        return ptype == "read"
    
    # Photographer can read services assigned to them
    if "Photographer" in user_roles:
        return ptype == "read"
    
    return False

def has_photographer_permission(doc, ptype):
    """Custom permission check for Photographer doctype"""
    user = frappe.session.user
    user_roles = frappe.get_roles(user)
    
    # Studio Manager has all permissions
    if "Studio Manager" in user_roles:
        return True
    
    # Studio Admin can read and write but not delete
    if "Studio Admin" in user_roles:
        return ptype != "delete"
    
    # Photographer can only read and update their own profile
    if "Photographer" in user_roles:
        if ptype == "read":
            return True
        elif ptype == "write":
            # Can only update their own profile
            return doc.user == user
    
    return False

def validate_user_access(doctype, doc_name=None, user=None):
    """Validate if user has access to specific document"""
    if not user:
        user = frappe.session.user
    
    if user == "Administrator":
        return True
    
    user_roles = frappe.get_roles(user)
    
    # Check doctype-specific permissions
    if doctype == "Booking":
        return "Studio Manager" in user_roles or "Booking Staff" in user_roles or "Studio Admin" in user_roles
    elif doctype == "Service":
        return "Studio Manager" in user_roles or "Studio Admin" in user_roles
    elif doctype == "Photographer":
        return "Studio Manager" in user_roles or "Studio Admin" in user_roles
    elif doctype == "Client":
        return "Studio Manager" in user_roles or "Booking Staff" in user_roles or "Studio Admin" in user_roles
    
    return False

def create_default_roles():
    """Create default roles for Re Studio Booking"""
    roles = [
        {
            "role_name": "Studio Manager",
            "description": "Full access to all studio operations"
        },
        {
            "role_name": "Studio Admin", 
            "description": "Administrative access with limited delete permissions"
        },
        {
            "role_name": "Booking Staff",
            "description": "Can manage bookings and customer data"
        },
        {
            "role_name": "Photographer",
            "description": "Can view assigned bookings and update profile"
        }
    ]
    
    for role_data in roles:
        if not frappe.db.exists("Role", role_data["role_name"]):
            role_doc = frappe.get_doc({
                "doctype": "Role",
                "role_name": role_data["role_name"],
                "description": role_data["description"]
            })
            role_doc.insert(ignore_permissions=True)

def setup_role_permissions():
    """Setup permissions for each role"""
    
    # Studio Manager permissions
    studio_manager_perms = [
        ("Booking", ["read", "write", "create", "delete", "submit", "cancel", "amend"]),
        ("Service", ["read", "write", "create", "delete"]),
        ("Photographer", ["read", "write", "create", "delete"]),
        ("Client", ["read", "write", "create", "delete"]),
        ("Category", ["read", "write", "create", "delete"]),
        ("Service Package", ["read", "write", "create", "delete"]),
        ("General Settings", ["read", "write"])
    ]
    
    # Studio Admin permissions  
    studio_admin_perms = [
        ("Booking", ["read", "write", "create", "submit", "cancel"]),
        ("Service", ["read", "write", "create"]),
        ("Photographer", ["read", "write", "create"]),
        ("Client", ["read", "write", "create"]),
        ("Category", ["read", "write", "create"]),
        ("Service Package", ["read", "write", "create"]),
        ("General Settings", ["read", "write"])
    ]
    
    # Booking Staff permissions
    booking_staff_perms = [
        ("Booking", ["read", "write", "create", "cancel"]),
        ("Service", ["read"]),
        ("Photographer", ["read"]),
        ("Client", ["read", "write", "create"]),
        ("Category", ["read"]),
        ("Service Package", ["read"])
    ]
    
    # Photographer permissions
    photographer_perms = [
        ("Booking", ["read"]),
        ("Service", ["read"]),
        ("Photographer", ["read", "write"]),
        ("Client", ["read"]),
        ("Category", ["read"]),
        ("Service Package", ["read"])
    ]
    
    role_permissions = {
        "Studio Manager": studio_manager_perms,
        "Studio Admin": studio_admin_perms, 
        "Booking Staff": booking_staff_perms,
        "Photographer": photographer_perms
    }
    
    for role, permissions in role_permissions.items():
        for doctype, perms in permissions:
            # Remove existing permissions
            frappe.db.delete("Custom DocPerm", {
                "parent": doctype,
                "role": role
            })
            
            # Add new permissions
            perm_dict = {
                "doctype": "Custom DocPerm",
                "parent": doctype,
                "parenttype": "DocType",
                "parentfield": "permissions",
                "role": role,
                "permlevel": 0
            }
            
            for perm in perms:
                perm_dict[perm] = 1
            
            perm_doc = frappe.get_doc(perm_dict)
            perm_doc.insert(ignore_permissions=True)

# Data encryption functions
def encrypt_sensitive_data(data):
    """Encrypt sensitive customer data"""
    try:
        from frappe.utils.password import encrypt
        return encrypt(data)
    except Exception:
        # Fallback if encryption not available
        return data

def decrypt_sensitive_data(encrypted_data):
    """Decrypt sensitive customer data"""
    try:
        from frappe.utils.password import decrypt
        return decrypt(encrypted_data)
    except Exception:
        # Fallback if decryption not available
        return encrypted_data

# Audit trail functions
def log_document_activity(doc, action):
    """Log document activities for audit trail"""
    try:
        frappe.get_doc({
            "doctype": "Activity Log",
            "subject": f"{action} {doc.doctype}: {doc.name}",
            "content": f"User {frappe.session.user} performed {action} on {doc.doctype} {doc.name}",
            "communication_date": frappe.utils.now(),
            "reference_doctype": doc.doctype,
            "reference_name": doc.name,
            "user": frappe.session.user
        }).insert(ignore_permissions=True)
    except Exception as e:
        frappe.log_error(f"Error logging activity: {str(e)}")

# IP restrictions (optional)
def validate_ip_access():
    """Validate if user is accessing from allowed IP"""
    # This can be configured in General Settings
    settings = frappe.get_single("General Settings")
    if hasattr(settings, "allowed_ips") and settings.allowed_ips:
        user_ip = frappe.local.request.environ.get('REMOTE_ADDR')
        allowed_ips = [ip.strip() for ip in settings.allowed_ips.split(',')]
        
        if user_ip not in allowed_ips:
            frappe.throw(_("Access denied from this IP address"))

def init_security():
    """Initialize security configurations"""
    create_default_roles()
    setup_role_permissions()
    frappe.db.commit()
