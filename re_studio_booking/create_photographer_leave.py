import frappe

def create_photographer_leave_doctype():
    """Create Photographer Leave DocType"""
    
    try:
        if not frappe.db.exists("DocType", "Photographer Leave"):
            doctype = frappe.get_doc({
                "doctype": "DocType",
                "name": "Photographer Leave",
                "module": "Re Studio Booking",
                "naming_series": "PL-.YYYY.-.MM.-.#####",
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
                        "fieldname": "leave_type",
                        "fieldtype": "Select",
                        "label": "Leave Type",
                        "options": "Annual Leave\nSick Leave\nEmergency Leave\nPersonal Leave",
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
                        "options": "Pending\nApproved\nRejected\nCancelled",
                        "default": "Pending",
                        "reqd": 1,
                        "in_list_view": 1
                    },
                    {
                        "fieldname": "section_break_1",
                        "fieldtype": "Section Break",
                        "label": "Leave Period"
                    },
                    {
                        "fieldname": "from_date",
                        "fieldtype": "Date",
                        "label": "From Date",
                        "reqd": 1,
                        "in_list_view": 1
                    },
                    {
                        "fieldname": "to_date",
                        "fieldtype": "Date",
                        "label": "To Date",
                        "reqd": 1,
                        "in_list_view": 1
                    },
                    {
                        "fieldname": "column_break_2",
                        "fieldtype": "Column Break"
                    },
                    {
                        "fieldname": "total_days",
                        "fieldtype": "Int",
                        "label": "Total Days",
                        "read_only": 1
                    },
                    {
                        "fieldname": "half_day",
                        "fieldtype": "Check",
                        "label": "Half Day"
                    },
                    {
                        "fieldname": "section_break_2",
                        "fieldtype": "Section Break",
                        "label": "Details"
                    },
                    {
                        "fieldname": "reason",
                        "fieldtype": "Text",
                        "label": "Reason for Leave",
                        "reqd": 1
                    },
                    {
                        "fieldname": "replacement_photographer",
                        "fieldtype": "Link",
                        "label": "Replacement Photographer",
                        "options": "Photographer"
                    },
                    {
                        "fieldname": "column_break_3",
                        "fieldtype": "Column Break"
                    },
                    {
                        "fieldname": "approved_by",
                        "fieldtype": "Link",
                        "label": "Approved By",
                        "options": "User",
                        "read_only": 1
                    },
                    {
                        "fieldname": "approval_date",
                        "fieldtype": "Date",
                        "label": "Approval Date",
                        "read_only": 1
                    },
                    {
                        "fieldname": "section_break_3",
                        "fieldtype": "Section Break",
                        "label": "Comments"
                    },
                    {
                        "fieldname": "comments",
                        "fieldtype": "Text",
                        "label": "Manager Comments"
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
                    },
                    {
                        "role": "Re Studio Agent",
                        "read": 1,
                        "write": 1,
                        "create": 1
                    }
                ]
            })
            doctype.insert()
            print("✅ Created Photographer Leave DocType")
        else:
            print("ℹ️  Photographer Leave DocType already exists")
        
        return {"success": True}
        
    except Exception as e:
        print(f"❌ Error creating Photographer Leave DocType: {e}")
        frappe.log_error(f"Photographer Leave DocType creation error: {str(e)}")
        return {"success": False, "error": str(e)}
