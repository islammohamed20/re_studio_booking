import frappe

def create_category_doctype():
    """Create Category DocType"""
    
    try:
        # Create Category doctype if it doesn't exist
        if not frappe.db.exists("DocType", "Category"):
            category_doc = frappe.get_doc({
                "doctype": "DocType",
                "name": "Category",
                "module": "Re Studio Booking",
                "fields": [
                    {
                        "fieldname": "category_name",
                        "fieldtype": "Data",
                        "label": "Category Name",
                        "reqd": 1
                    },
                    {
                        "fieldname": "category_name_ar",
                        "fieldtype": "Data",
                        "label": "Category Name (Arabic)"
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
                    },
                    {
                        "fieldname": "sort_order",
                        "fieldtype": "Int",
                        "label": "Sort Order",
                        "default": 0
                    }
                ]
            })
            category_doc.insert()
            print("✅ Created Category DocType")
            
            # Create some default categories
            default_categories = [
                {"category_name": "Portrait Photography", "category_name_ar": "تصوير شخصي", "is_active": 1},
                {"category_name": "Wedding Photography", "category_name_ar": "تصوير زفاف", "is_active": 1},
                {"category_name": "Event Photography", "category_name_ar": "تصوير مناسبات", "is_active": 1},
                {"category_name": "Product Photography", "category_name_ar": "تصوير منتجات", "is_active": 1}
            ]
            
            for category in default_categories:
                frappe.get_doc({
                    "doctype": "Category",
                    **category
                }).insert()
            
            print("✅ Created default categories")
        else:
            print("ℹ️  Category DocType already exists")
        
        return {"success": True, "message": "Category DocType handled successfully"}
        
    except Exception as e:
        print(f"❌ Error creating Category DocType: {e}")
        frappe.log_error(f"Category DocType creation error: {str(e)}")
        return {"success": False, "error": str(e)}
