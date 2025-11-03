import frappe

def disable_hr_manager():
    """Disable Role 'HR Manager' safely."""
    role_name = 'HR Manager'
    role = frappe.db.get_value('Role', role_name)
    if not role:
        print(f"Role '{role_name}' not found")
        return
    # set disabled flag
    frappe.db.set_value('Role', role_name, 'disabled', 1)
    frappe.db.commit()
    print(f"Role '{role_name}' disabled")

def delete_hr_manager():
    """Delete Role 'HR Manager' completely."""
    role_name = 'HR Manager'
    
    # Check if role exists
    if not frappe.db.exists('Role', role_name):
        print(f"Role '{role_name}' not found")
        return
    
    # Delete all role permissions linked to this role
    frappe.db.sql("""
        DELETE FROM `tabCustom DocPerm` 
        WHERE role = %s
    """, (role_name,))
    
    frappe.db.sql("""
        DELETE FROM `tabDocPerm` 
        WHERE role = %s
    """, (role_name,))
    
    # Delete user roles
    frappe.db.sql("""
        DELETE FROM `tabHas Role` 
        WHERE role = %s
    """, (role_name,))
    
    # Delete the role itself
    frappe.delete_doc('Role', role_name, force=1, ignore_permissions=True)
    frappe.db.commit()
    
    print(f"Role '{role_name}' deleted successfully")

