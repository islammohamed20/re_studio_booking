import os
import shutil

def execute():
    """Delete the Photographer Studios DocType and its related files"""
    try:
        doctype_name = "Photographer Studios"
        apostrophe_doctype_name = "Photographer Studio's"
        
        # Check if DocType exists in database
        if frappe.db.exists("DocType", doctype_name):
            print(f"Found DocType '{doctype_name}' in the database")
            
            # Check for records
            count = frappe.db.count(doctype_name)
            if count > 0:
                print(f"WARNING: Found {count} records of '{doctype_name}'. These will be deleted.")
                
            # Check for references in workspace
            workspace_links = frappe.db.sql("""
                SELECT parent FROM `tabWorkspace Link` 
                WHERE link_to = %s
            """, doctype_name, as_dict=1)
            
            if workspace_links:
                print(f"Removing references from {len(workspace_links)} workspaces:")
                for wl in workspace_links:
                    print(f"  - {wl.parent}")
                
                frappe.db.sql("""
                    DELETE FROM `tabWorkspace Link` 
                    WHERE link_to = %s
                """, doctype_name)
                
                print("Workspace references removed")
            
            # Delete the DocType from database
            frappe.delete_doc("DocType", doctype_name, force=1)
            print(f"Deleted DocType '{doctype_name}' from database")
            
            frappe.db.commit()
        else:
            print(f"DocType '{doctype_name}' not found in database")
        
        # Check for apostrophe version
        if frappe.db.exists("DocType", apostrophe_doctype_name):
            frappe.delete_doc("DocType", apostrophe_doctype_name, force=1)
            print(f"Deleted DocType '{apostrophe_doctype_name}' from database")
            frappe.db.commit()
        
        # Delete directory structure
        base_path = "/home/frappe/frappe/apps/re_studio_booking/re_studio_booking/re_studio_booking/doctype"
        
        # Delete the regular version
        regular_path = os.path.join(base_path, "photographer_studios")
        if os.path.exists(regular_path):
            print(f"Deleting directory: {regular_path}")
            shutil.rmtree(regular_path)
            print("Directory deleted successfully")
        else:
            print(f"Directory not found: {regular_path}")
        
        # Delete the apostrophe version
        apostrophe_path = os.path.join(base_path, "photographer_studio's")
        if os.path.exists(apostrophe_path):
            print(f"Deleting directory: {apostrophe_path}")
            shutil.rmtree(apostrophe_path)
            print("Directory deleted successfully")
        else:
            print(f"Directory not found: {apostrophe_path}")
        
        # Remove from patches.txt
        patches_file = "/home/frappe/frappe/apps/re_studio_booking/re_studio_booking/patches.txt"
        if os.path.exists(patches_file):
            with open(patches_file, 'r') as file:
                lines = file.readlines()
            
            with open(patches_file, 'w') as file:
                for line in lines:
                    if "rename_photographer_studios_doctype" not in line:
                        file.write(line)
            
            print("Removed patch from patches.txt")
        
        print("Deletion process complete. Please run 'bench build' and 'bench migrate' to apply changes.")
        
    except Exception as e:
        print(f"Error during deletion process: {str(e)}")

execute()
