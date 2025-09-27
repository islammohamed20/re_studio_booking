import frappe

def execute():
    """Update Friday working status in all photographer schedules and working hours"""
    
    try:
        # Update all photographer schedules to include Friday as working day
        photographer_schedules = frappe.get_all("Photographer Schedule", fields=["name"])
        
        for schedule in photographer_schedules:
            doc = frappe.get_doc("Photographer Schedule", schedule.name)
            
            # Enable Friday working
            if not doc.friday_working:
                doc.friday_working = 1
                doc.friday_from = "09:00:00"
                doc.friday_to = "17:00:00"
                doc.save(ignore_permissions=True)
        
        # Update photographer working hours
        photographers = frappe.get_all("Photographer", fields=["name"])
        
        for photographer in photographers:
            doc = frappe.get_doc("Photographer", photographer.name)
            
            # Find Friday row in working_hours
            for row in doc.working_hours:
                if row.day in ["Friday", "الجمعة"]:
                    if not row.is_working_day:
                        row.is_working_day = 1
                        row.start_time = "09:00:00"
                        row.end_time = "17:00:00"
            
            doc.save(ignore_permissions=True)
        
        frappe.db.commit()
        print("Successfully updated Friday working status for all photographers")
        
    except Exception as e:
        frappe.db.rollback()
        print(f"Error updating Friday working status: {str(e)}")