# Copyright (c) 2025, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe import _

@frappe.whitelist()
def get_working_days_from_general_settings():
    """جلب أيام العمل من General Settings"""
    try:
        if not frappe.db.exists('DocType', 'General Settings'):
            return get_default_working_days()
        
        settings = frappe.get_single('General Settings')
        working_days = []
        
        # قراءة إعدادات أيام العمل من General Settings
        days_mapping = {
            'sunday_working': 'Sunday',
            'monday_working': 'Monday', 
            'tuesday_working': 'Tuesday',
            'wednesday_working': 'Wednesday',
            'thursday_working': 'Thursday',
            'friday_working': 'Friday',
            'saturday_working': 'Saturday'
        }
        
        for field_name, day_name in days_mapping.items():
            if hasattr(settings, field_name) and getattr(settings, field_name):
                working_days.append(day_name)
        
        # إذا لم توجد إعدادات، استخدم الافتراضي
        if not working_days:
            working_days = get_default_working_days()
        
        return working_days
        
    except Exception as e:
        frappe.logger().error(f"Error getting working days from General Settings: {str(e)}")
        return get_default_working_days()

def get_default_working_days():
    """أيام العمل الافتراضية (بدون الجمعة إذا كان عطلة في General Settings)"""
    return ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Saturday']

@frappe.whitelist()
def get_business_hours_from_general_settings():
    """جلب ساعات العمل من General Settings"""
    try:
        if not frappe.db.exists('DocType', 'General Settings'):
            return get_default_business_hours()
        
        settings = frappe.get_single('General Settings')
        
        business_hours = {
            'opening_time': getattr(settings, 'opening_time', None) or '09:00:00',
            'closing_time': getattr(settings, 'closing_time', None) or '17:00:00'
        }
        
        return business_hours
        
    except Exception as e:
        frappe.logger().error(f"Error getting business hours from General Settings: {str(e)}")
        return get_default_business_hours()

def get_default_business_hours():
    """ساعات العمل الافتراضية"""
    return {
        'opening_time': '09:00:00',
        'closing_time': '17:00:00'
    }

@frappe.whitelist()
def is_working_day(date_str):
    """فحص إذا كان اليوم المحدد يوم عمل حسب إعدادات General Settings"""
    try:
        import datetime
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        day_name = date_obj.strftime('%A')  # Sunday, Monday, etc.
        
        working_days = get_working_days_from_general_settings()
        return day_name in working_days
        
    except Exception as e:
        frappe.logger().error(f"Error checking working day: {str(e)}")
        return True  # افتراضي: يوم عمل

@frappe.whitelist()
def get_studio_settings():
    """جلب جميع إعدادات الاستديو من General Settings"""
    return {
        'working_days': get_working_days_from_general_settings(),
        'business_hours': get_business_hours_from_general_settings(),
        'is_friday_working': 'Friday' in get_working_days_from_general_settings()
    }