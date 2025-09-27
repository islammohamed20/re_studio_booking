import frappe

def execute():
    """
    Rename Photographer Studio's to Photographer Studios
    This patch handles the migration of records from the doctype with apostrophe to without apostrophe
    """
    try:
        # Check if the old doctype exists in DB
        if frappe.db.exists("DocType", "Photographer Studio's"):
            # Check if the new doctype already exists
            if frappe.db.exists("DocType", "Photographer Studios"):
                print("DocType 'Photographer Studios' already exists. Handling record migration...")
                
                # Get all records of the old doctype
                records = frappe.get_all("Photographer Studio's", fields=["name"])
                
                # Copy records from old to new doctype
                for record in records:
                    old_name = record.name
                    new_name = old_name.replace("'", "")
                    
                    # Check if this record already exists in the new doctype
                    if not frappe.db.exists("Photographer Studios", new_name):
                        # Get the old record data
                        old_doc = frappe.get_doc("Photographer Studio's", old_name)
                        
                        # Create a new record in the new doctype
                        new_doc = frappe.new_doc("Photographer Studios")
                        for field in old_doc.meta.get_fieldnames_with_value():
                            if field not in ['name', 'modified', 'creation']:
                                new_doc.set(field, old_doc.get(field))
                        
                        # Insert the new record
                        new_doc.insert(ignore_permissions=True)
                        print(f"Copied record from '{old_name}' to '{new_name}'")
                
                # Update references in the database
                update_references()
            else:
                # Rename the DocType itself
                frappe.rename_doc("DocType", "Photographer Studio's", "Photographer Studios", force=True)
                print("Renamed DocType 'Photographer Studio's' to 'Photographer Studios'")
                
                # Update references
                update_references()
            
            frappe.db.commit()
            print("Migration completed successfully")
        else:
            print("DocType 'Photographer Studio's' not found in database. No migration needed.")
    
    except Exception as e:
        frappe.db.rollback()
        print(f"Error during migration: {str(e)}")
        raise

def update_references():
    """Update references to the old doctype in the database"""
    try:
        # Update workspace references
        frappe.db.sql("""
            UPDATE `tabWorkspace Link` 
            SET link_to = 'Photographer Studios'
            WHERE link_to = 'Photographer Studio''s'
        """)
        print("Updated workspace references")
        
        # Update other references if needed
        # Add more SQL statements here if other tables need updating
    except Exception as e:
        print(f"Error updating references: {str(e)}")
        raise
