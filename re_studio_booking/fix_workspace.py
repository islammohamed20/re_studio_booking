import frappe

def fix_workspace():
    """Fix the Re Studio workspace by removing references to Booking Settings"""
    try:
        # Get the Re Studio workspace
        workspace = frappe.get_doc("Workspace", "Re Studio")
        
        # Check if we need to update the links
        updated = False
        new_links = []
        
        for link in workspace.links:
            # Skip any references to Booking Settings
            if link.link_to == "Booking Settings":
                updated = True
                print(f"Removing reference to Booking Settings at position {link.idx}")
                continue
            new_links.append(link)
        
        if updated:
            # Update the links
            workspace.links = new_links
            
            # Save the workspace
            workspace.save()
            print("Workspace updated successfully!")
        else:
            print("No references to Booking Settings found in links.")
            
            # Check if it's in the content
            if "Booking Settings" in workspace.content:
                print("Reference found in workspace content. Updating content...")
                # Parse the content and update it
                import json
                content = json.loads(workspace.content)
                updated_content = []
                
                for item in content:
                    if item.get("type") == "card" and item.get("data", {}).get("card_name") == "Booking Settings":
                        updated = True
                        print(f"Removing Booking Settings card from content")
                        continue
                    updated_content.append(item)
                
                if updated:
                    workspace.content = json.dumps(updated_content)
                    workspace.save()
                    print("Workspace content updated successfully!")
        
        if not updated:
            print("No direct references to Booking Settings found in workspace.")
            print("The issue might be in a custom or user-specific workspace.")
            
            # Check all custom workspaces
            print("Checking custom workspaces...")
            custom_workspaces = frappe.get_all(
                "Workspace",
                filters={"module": "Re Studio Booking", "is_hidden": 0},
                fields=["name"]
            )
            
            for ws in custom_workspaces:
                if ws.name != "Re Studio":
                    print(f"Found custom workspace: {ws.name}")
                    # You could add code here to fix the custom workspace
        
        # Create a General Settings single doctype instance if it doesn't exist
        if not frappe.db.exists("General Settings"):
            print("Creating General Settings document...")
            doc = frappe.new_doc("General Settings")
            doc.save()
            print("General Settings document created.")
            
        return "Workspace fix attempted successfully"
    except Exception as e:
        frappe.log_error(f"Error fixing workspace: {str(e)}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    fix_workspace()
