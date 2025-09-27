# -*- coding: utf-8 -*-
# Copyright (c) 2025, Masar Digital Group and contributors
# For license information, please see license.txt

import frappe
import os
import shutil

def execute():
    """
    Migrate data from Studio Settings to Photographer Studio and delete Studio Settings
    """
    try:
        print("Starting migration from Studio Settings to Photographer Studio...")
        
        # Check if Studio Settings exists
        if frappe.db.exists("DocType", "Studio Settings"):
            print("Found Studio Settings DocType")
            
            # Get all records from Studio Settings
            studio_settings_records = frappe.get_all("Studio Settings", fields=["*"])
            
            if studio_settings_records:
                print(f"Found {len(studio_settings_records)} Studio Settings records")
                
                # Copy records to Photographer Studio
                for record in studio_settings_records:
                    # Create new Photographer Studio record
                    new_studio = frappe.new_doc("Photographer Studio")
                    
                    # Copy all fields
                    for field in record:
                        if field not in ['name', 'doctype', 'creation', 'modified', 'modified_by', 'owner']:
                            new_studio.set(field, record[field])
                    
                    # Insert the new record
                    new_studio.insert(ignore_permissions=True)
                    print(f"Migrated record: {record.get('studio_name', 'Unknown')}")
                
                print("All records migrated successfully")
            else:
                print("No Studio Settings records found to migrate")
            
            # Remove workspace references to Studio Settings
            workspace_links = frappe.db.sql("""
                SELECT parent FROM `tabWorkspace Link` 
                WHERE link_to = 'Studio Settings'
            """, as_dict=1)
            
            if workspace_links:
                print(f"Removing {len(workspace_links)} workspace references...")
                frappe.db.sql("""
                    DELETE FROM `tabWorkspace Link` 
                    WHERE link_to = 'Studio Settings'
                """)
                print("Workspace references removed")
            
            # Delete the Studio Settings DocType
            frappe.delete_doc("DocType", "Studio Settings", force=1)
            print("Studio Settings DocType deleted from database")
            
            frappe.db.commit()
            
        else:
            print("Studio Settings DocType not found in database")
        
        print("Migration completed successfully")
        
        # Note about file cleanup
        print("Note: Run 'rm -rf studio_settings' directory manually after migration")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        frappe.db.rollback()
        raise
