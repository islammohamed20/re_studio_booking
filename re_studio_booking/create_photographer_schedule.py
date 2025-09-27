import frappe

def create_photographer_schedule_doctype():
    """Create Photographer Schedule DocType"""
    
    try:
        if not frappe.db.exists("DocType", "Photographer Schedule"):
            doctype = frappe.get_doc({
                "doctype": "DocType",
                "name": "Photographer Schedule",
                "module": "Re Studio Booking", 
                "naming_series": "PS-.YYYY.-.MM.-.#####",
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
                        "fieldname": "week_start_date",
                        "fieldtype": "Date",
                        "label": "Week Start Date",
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
                        "options": "Draft\nActive\nInactive",
                        "default": "Draft",
                        "reqd": 1,
                        "in_list_view": 1
                    },
                    {
                        "fieldname": "section_break_1",
                        "fieldtype": "Section Break",
                        "label": "Monday"
                    },
                    {
                        "fieldname": "monday_working",
                        "fieldtype": "Check",
                        "label": "Working on Monday",
                        "default": 1
                    },
                    {
                        "fieldname": "monday_from",
                        "fieldtype": "Time",
                        "label": "Monday From",
                        "default": "09:00:00",
                        "depends_on": "monday_working"
                    },
                    {
                        "fieldname": "monday_to",
                        "fieldtype": "Time",
                        "label": "Monday To",
                        "default": "17:00:00",
                        "depends_on": "monday_working"
                    },
                    {
                        "fieldname": "section_break_2",
                        "fieldtype": "Section Break",
                        "label": "Tuesday"
                    },
                    {
                        "fieldname": "tuesday_working",
                        "fieldtype": "Check",
                        "label": "Working on Tuesday",
                        "default": 1
                    },
                    {
                        "fieldname": "tuesday_from",
                        "fieldtype": "Time",
                        "label": "Tuesday From",
                        "default": "09:00:00",
                        "depends_on": "tuesday_working"
                    },
                    {
                        "fieldname": "tuesday_to",
                        "fieldtype": "Time",
                        "label": "Tuesday To",
                        "default": "17:00:00",
                        "depends_on": "tuesday_working"
                    },
                    {
                        "fieldname": "section_break_3",
                        "fieldtype": "Section Break",
                        "label": "Wednesday"
                    },
                    {
                        "fieldname": "wednesday_working",
                        "fieldtype": "Check",
                        "label": "Working on Wednesday",
                        "default": 1
                    },
                    {
                        "fieldname": "wednesday_from",
                        "fieldtype": "Time",
                        "label": "Wednesday From",
                        "default": "09:00:00",
                        "depends_on": "wednesday_working"
                    },
                    {
                        "fieldname": "wednesday_to",
                        "fieldtype": "Time",
                        "label": "Wednesday To",
                        "default": "17:00:00",
                        "depends_on": "wednesday_working"
                    },
                    {
                        "fieldname": "section_break_4",
                        "fieldtype": "Section Break",
                        "label": "Thursday"
                    },
                    {
                        "fieldname": "thursday_working",
                        "fieldtype": "Check",
                        "label": "Working on Thursday",
                        "default": 1
                    },
                    {
                        "fieldname": "thursday_from",
                        "fieldtype": "Time",
                        "label": "Thursday From",
                        "default": "09:00:00",
                        "depends_on": "thursday_working"
                    },
                    {
                        "fieldname": "thursday_to",
                        "fieldtype": "Time",
                        "label": "Thursday To",
                        "default": "17:00:00",
                        "depends_on": "thursday_working"
                    },
                    {
                        "fieldname": "section_break_5",
                        "fieldtype": "Section Break",
                        "label": "Friday"  
                    },
                    {
                        "fieldname": "friday_working",
                        "fieldtype": "Check",
                        "label": "Working on Friday",
                        "default": 1
                    },
                    {
                        "fieldname": "friday_from",
                        "fieldtype": "Time",
                        "label": "Friday From",
                        "default": "09:00:00",
                        "depends_on": "friday_working"
                    },
                    {
                        "fieldname": "friday_to",
                        "fieldtype": "Time",
                        "label": "Friday To",
                        "default": "17:00:00",
                        "depends_on": "friday_working"
                    },
                    {
                        "fieldname": "section_break_6",
                        "fieldtype": "Section Break",
                        "label": "Saturday"
                    },
                    {
                        "fieldname": "saturday_working",
                        "fieldtype": "Check",
                        "label": "Working on Saturday",
                        "default": 1
                    },
                    {
                        "fieldname": "saturday_from",
                        "fieldtype": "Time",
                        "label": "Saturday From",
                        "default": "09:00:00",
                        "depends_on": "saturday_working"
                    },
                    {
                        "fieldname": "saturday_to", 
                        "fieldtype": "Time",
                        "label": "Saturday To",
                        "default": "17:00:00",
                        "depends_on": "saturday_working"
                    },
                    {
                        "fieldname": "section_break_7",
                        "fieldtype": "Section Break",
                        "label": "Sunday"
                    },
                    {
                        "fieldname": "sunday_working",
                        "fieldtype": "Check",
                        "label": "Working on Sunday",
                        "default": 1
                    },
                    {
                        "fieldname": "sunday_from",
                        "fieldtype": "Time",
                        "label": "Sunday From", 
                        "default": "09:00:00",
                        "depends_on": "sunday_working"
                    },
                    {
                        "fieldname": "sunday_to",
                        "fieldtype": "Time",
                        "label": "Sunday To",
                        "default": "17:00:00",
                        "depends_on": "sunday_working"
                    },
                    {
                        "fieldname": "section_break_8",
                        "fieldtype": "Section Break",
                        "label": "Notes"
                    },
                    {
                        "fieldname": "notes",
                        "fieldtype": "Text",
                        "label": "Notes"
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
            print("✅ Created Photographer Schedule DocType")
        else:
            print("ℹ️  Photographer Schedule DocType already exists")
        
        return {"success": True}
        
    except Exception as e:
        print(f"❌ Error creating Photographer Schedule DocType: {e}")
        frappe.log_error(f"Photographer Schedule DocType creation error: {str(e)}")
        return {"success": False, "error": str(e)}
