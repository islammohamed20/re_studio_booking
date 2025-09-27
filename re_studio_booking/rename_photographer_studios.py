import frappe

def execute():
    """
    Script to rename the Photographer Studio's DocType to Photographer Studios
    This is needed to avoid issues with apostrophes in file paths
    """
    try:
        # Check if the old doctype exists
        if frappe.db.exists("DocType", "Photographer Studio's"):
            print("Renaming 'Photographer Studio's' DocType to 'Photographer Studios'...")
            
            # Rename the DocType
            frappe.rename_doc("DocType", "Photographer Studio's", "Photographer Studios", force=True)
            
            # Update any references in the database
            frappe.db.sql("""
                UPDATE `tabWorkspace Link` 
                SET link_to = 'Photographer Studios'
                WHERE link_to = 'Photographer Studio''s'
            """)
            
            print("DocType renamed successfully!")
        else:
            print("DocType 'Photographer Studio's' not found in the database. No renaming needed.")
            
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        print(f"Error renaming DocType: {str(e)}")
