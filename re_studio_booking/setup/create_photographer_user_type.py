import frappe

def create_photographer_user_type():
    """Create Photographer User role and user type"""
    
    # Create Role if it doesn't exist
    if not frappe.db.exists("Role", "Photographer User"):
        role_doc = frappe.get_doc({
            "doctype": "Role",
            "role_name": "Photographer User",
            "desk_access": 1,
            "is_custom": 1,
            "disabled": 0,
            "home_page": "/photographer_dashboard"
        })
        role_doc.insert(ignore_permissions=True)
        print("Created Photographer User role")
    
    # Create User Type if it doesn't exist
    if not frappe.db.exists("User Type", "Photographer User"):
        user_type_doc = frappe.get_doc({
            "doctype": "User Type",
            "name": "Photographer User",
            "user_type": "Photographer User",
            "role": "Photographer User",
            "user_doctypes": [
                {
                    "document_type": "Booking",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 0
                },
                {
                    "document_type": "Photographer",
                    "read": 1,
                    "write": 1,
                    "create": 0,
                    "delete": 0
                },
                {
                    "document_type": "Photographer Studio",
                    "read": 1,
                    "write": 1,
                    "create": 0,
                    "delete": 0
                },
                {
                    "document_type": "Service",
                    "read": 1,
                    "write": 0,
                    "create": 0,
                    "delete": 0
                }
            ],
            "user_id_field": "user_account",
            "apply_user_permission_on": "Photographer",
            "user_doctypes_and_fields": [
                {
                    "document_type": "Booking",
                    "fields": ["*"]
                },
                {
                    "document_type": "Photographer",
                    "fields": ["*"]
                },
                {
                    "document_type": "Photographer Studio",
                    "fields": ["*"]
                },
                {
                    "document_type": "Service",
                    "fields": ["*"]
                }
            ],
            "select_doctypes": [
                {
                    "document_type": "Booking",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 0
                },
                {
                    "document_type": "Photographer",
                    "read": 1,
                    "write": 1,
                    "create": 0,
                    "delete": 0
                },
                {
                    "document_type": "Photographer Studio",
                    "read": 1,
                    "write": 1,
                    "create": 0,
                    "delete": 0
                },
                {
                    "document_type": "Service",
                    "read": 1,
                    "write": 0,
                    "create": 0,
                    "delete": 0
                }
            ],
            "custom_select_doctypes": [
                {
                    "document_type": "Re Studio Booking",
                    "read": 1,
                    "write": 0,
                    "create": 0,
                    "delete": 0
                },
                {
                    "document_type": "Core",
                    "read": 1,
                    "write": 0,
                    "create": 0,
                    "delete": 0
                },
                {
                    "document_type": "Desk",
                    "read": 1,
                    "write": 0,
                    "create": 0,
                    "delete": 0
                }
            ]
        })
        user_type_doc.insert(ignore_permissions=True)
        print("Created Photographer User type")
    
    frappe.db.commit()
    print("Photographer User role and type created successfully")

if __name__ == "__main__":
    create_photographer_user_type()