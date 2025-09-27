import frappe

def create_photographer_availability_doctype():
    """Create Photographer Availability DocType"""
    
    try:
        if not frappe.db.exists("DocType", "Photographer Availability"):
            doctype = frappe.get_doc({
                "doctype": "DocType",
                "name": "Photographer Availability",
                "module": "Re Studio Booking",
                "naming_series": "PA-.YYYY.-.MM.-.#####",
                "title_field": "photographer",
                "fields": [
                    {
                        "fieldname": "photographer",
                        "fieldtype": "Link",
                        "label": "Photographer",
                        "options": "Photographer",
                        "reqd": 1,
                        "in_list_view": 1
                    },
                    {
                        "fieldname": "date",
                        "fieldtype": "Date",
                        "label": "Date",
                        "reqd": 1,
                        "in_list_view": 1
                    },
                    {
                        "fieldname": "column_break_1",
                        "fieldtype": "Column Break"
                    },
                    {
                        "fieldname": "status",
                        "fieldtype": "Select",
                        "label": "Status",
                        "options": "Available\nUnavailable\nPartially Available",
                        "default": "Available",
                        "reqd": 1,
                        "in_list_view": 1
                    },
                    {
                        "fieldname": "section_break_1",
                        "fieldtype": "Section Break",
                        "label": "Time Slots"
                    },
                    {
                        "fieldname": "from_time", 
                        "fieldtype": "Time",
                        "label": "Available From",
                        "default": "09:00:00"
                    },
                    {
                        "fieldname": "to_time",
                        "fieldtype": "Time", 
                        "label": "Available To",
                        "default": "17:00:00"
                    },
                    {
                        "fieldname": "column_break_2",
                        "fieldtype": "Column Break"
                    },
                    {
                        "fieldname": "break_from",
                        "fieldtype": "Time",
                        "label": "Break From"
                    },
                    {
                        "fieldname": "break_to",
                        "fieldtype": "Time",
                        "label": "Break To"
                    },
                    {
                        "fieldname": "section_break_2",
                        "fieldtype": "Section Break",
                        "label": "Additional Information"
                    },
                    {
                        "fieldname": "notes",
                        "fieldtype": "Text",
                        "label": "Notes"
                    },
                    {
                        "fieldname": "is_recurring",
                        "fieldtype": "Check",
                        "label": "Is Recurring"
                    },
                    {
                        "fieldname": "column_break_3",
                        "fieldtype": "Column Break"
                    },
                    {
                        "fieldname": "created_by",
                        "fieldtype": "Link",
                        "label": "Created By",
                        "options": "User",
                        "read_only": 1
                    }
                ],
                "permissions": [
                    {
                        "role": "System Manager",
                        "read": 1,
                        "write": 1,
                        "create": 1,
                        "delete": 1
                    },
                    {
                        "role": "Re Studio Manager", 
                        "read": 1,
                        "write": 1,
                        "create": 1,
                        "delete": 1
                    }
                ]
            })
            doctype.insert()
            print("✅ Created Photographer Availability DocType")
        else:
            print("ℹ️  Photographer Availability DocType already exists")
        
        return {"success": True}
        
    except Exception as e:
        print(f"❌ Error creating Photographer Availability DocType: {e}")
        frappe.log_error(f"Photographer Availability DocType creation error: {str(e)}")
        return {"success": False, "error": str(e)}
