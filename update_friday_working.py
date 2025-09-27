#!/usr/bin/env python3

import frappe
from frappe import _

def update_friday_working_status():
    """تحديث حالة يوم الجمعة ليصبح يوم عمل في جميع جداول المصورين"""
    
    print("بدء تحديث إعدادات يوم الجمعة...")
    
    try:
        # تحديث جميع جداول المصورين
        photographer_schedules = frappe.get_all("Photographer Schedule", fields=["name"])
        
        updated_count = 0
        for schedule in photographer_schedules:
            doc = frappe.get_doc("Photographer Schedule", schedule.name)
            
            # تحديث إعدادات يوم الجمعة
            if not doc.friday_working:
                doc.friday_working = 1
                doc.friday_from = "09:00:00"
                doc.friday_to = "17:00:00"
                doc.save()
                updated_count += 1
        
        print(f"تم تحديث {updated_count} جدول مصور")
        
        # تحديث إعدادات ساعات العمل للمصورين
        photographers = frappe.get_all("Photographer", fields=["name"])
        
        updated_photographers = 0
        for photographer in photographers:
            doc = frappe.get_doc("Photographer", photographer.name)
            
            # البحث عن صف الجمعة في working_hours
            friday_row = None
            for row in doc.working_hours:
                if row.day == "الجمعة" or row.day == "Friday":
                    friday_row = row
                    break
            
            if friday_row and not friday_row.is_working_day:
                friday_row.is_working_day = 1
                friday_row.start_time = "09:00:00"
                friday_row.end_time = "17:00:00"
                doc.save()
                updated_photographers += 1
        
        print(f"تم تحديث {updated_photographers} مصور")
        
        frappe.db.commit()
        print("تم حفظ جميع التغييرات بنجاح!")
        
    except Exception as e:
        print(f"خطأ في التحديث: {str(e)}")
        frappe.db.rollback()

if __name__ == "__main__":
    frappe.init(site='site1.local')
    frappe.connect()
    update_friday_working_status()