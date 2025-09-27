# -*- coding: utf-8 -*-
# Copyright (c) 2025, Masar Digital Group and contributors
# For license information, please see license.txt

import frappe
import os
import shutil

def execute():
    """
    This patch handles the complete deletion of Photographer Studios DocType
    and ensures all references are updated or removed
    """
    try:
        # Mark the start of execution
        print("Starting cleanup of Photographer Studios DocType...")
        
        # Check for workspace references and clean them
        workspace_links = frappe.db.sql("""
            SELECT parent FROM `tabWorkspace Link` 
            WHERE link_to IN ('Photographer Studios', 'Photographer Studio''s')
        """, as_dict=1)
        
        if workspace_links:
            print(f"Found {len(workspace_links)} workspace references. Cleaning...")
            
            # Update workspace content
            for ws in workspace_links:
                workspace = frappe.get_doc("Workspace", ws.parent)
                content_updated = False
                
                try:
                    # Find and remove link
                    for i, link in enumerate(workspace.links):
                        if link.link_to in ["Photographer Studios", "Photographer Studio's"]:
                            print(f"Removing link from workspace: {workspace.name}")
                            del workspace.links[i]
                            content_updated = True
                            break
                    
                    if content_updated:
                        workspace.save()
                        print(f"Updated workspace: {workspace.name}")
                except Exception as e:
                    print(f"Error updating workspace {workspace.name}: {str(e)}")
        
        # Check if we still have the DocType in database
        doctype_exists = frappe.db.exists("DocType", "Photographer Studios")
        apostrophe_exists = frappe.db.exists("DocType", "Photographer Studio's")
        
        if doctype_exists:
            print("DocType still exists in database, deleting...")
            try:
                frappe.delete_doc("DocType", "Photographer Studios", force=1)
                print("DocType deleted from database")
            except Exception as e:
                print(f"Error deleting DocType: {str(e)}")
        
        if apostrophe_exists:
            print("Apostrophe version exists in database, deleting...")
            try:
                frappe.delete_doc("DocType", "Photographer Studio's", force=1)
                print("Apostrophe DocType deleted from database")
            except Exception as e:
                print(f"Error deleting apostrophe DocType: {str(e)}")
        
        # Mark completion
        print("Database cleanup complete")
        frappe.db.commit()
        
        # Note: File cleanup will be handled separately as it requires OS operations
        print("Patch execution complete. Run 'bench build' to apply changes.")
        
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")
        frappe.db.rollback()
        raise
