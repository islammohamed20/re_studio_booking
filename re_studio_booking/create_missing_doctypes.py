import frappe

def create_missing_doctypes():
    """Create missing DocTypes that are referenced in the code"""
    
    try:
        # Create Payment Method doctype if it doesn't exist
        if not frappe.db.exists("DocType", "Payment Method"):
            payment_method_doc = frappe.get_doc({
                "doctype": "DocType",
                "name": "Payment Method",
                "module": "Re Studio Booking",
                "fields": [
                    {
                        "fieldname": "method_name",
                        "fieldtype": "Data",
                        "label": "Payment Method Name",
                        "reqd": 1
                    },
                    {
                        "fieldname": "is_active",
                        "fieldtype": "Check",
                        "label": "Is Active",
                        "default": 1
                    },
                    {
                        "fieldname": "description",
                        "fieldtype": "Text",
                        "label": "Description"
                    }
                ]
            })
            payment_method_doc.insert()
            print("✅ Created Payment Method DocType")
            
            # Create some default payment methods
            default_methods = [
                {"method_name": "Cash", "is_active": 1, "description": "Cash payment"},
                {"method_name": "Credit Card", "is_active": 1, "description": "Credit card payment"},
                {"method_name": "Bank Transfer", "is_active": 1, "description": "Bank transfer payment"}
            ]
            
            for method in default_methods:
                frappe.get_doc({
                    "doctype": "Payment Method",
                    **method
                }).insert()
            
            print("✅ Created default payment methods")
        else:
            print("ℹ️  Payment Method DocType already exists")
        
        return {"success": True, "message": "Missing DocTypes handled successfully"}
        
    except Exception as e:
        print(f"❌ Error creating missing DocTypes: {e}")
        frappe.log_error(f"Missing DocTypes creation error: {str(e)}")
        return {"success": False, "error": str(e)}
