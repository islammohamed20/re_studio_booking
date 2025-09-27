import frappe

def execute():
    """Update existing client types from Individual/Company to B2C/B2B"""
    
    try:
        frappe.log_error("Starting client type migration from Individual/Company to B2C/B2B")
        
        # Update Individual to B2C
        individual_clients = frappe.db.sql("""
            UPDATE `tabClient` 
            SET client_type = 'B2C' 
            WHERE client_type = 'Individual'
        """)
        
        # Update Company to B2B
        company_clients = frappe.db.sql("""
            UPDATE `tabClient` 
            SET client_type = 'B2B' 
            WHERE client_type = 'Company'
        """)
        
        # Commit the changes
        frappe.db.commit()
        
        frappe.log_error("Successfully updated client types to B2C/B2B")
        
    except Exception as e:
        frappe.log_error(f"Error updating client types: {str(e)}")
        raise
