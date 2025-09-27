from __future__ import unicode_literals
from frappe import _

def get_data():
    return [
        {
            "label": _("📸 Re Studio"),
            "icon": "fa fa-camera",
            "items": [
                {
                    "type": "link",
                    "name": "admin-dashboard",
                    "label": _("📊 لوحة التحكم الرئيسية"),
                    "link": "/app/admin-dashboard",
                    "description": _("Dashboard for studio management")
                },
                {
                    "type": "doctype",
                    "name": "Booking",
                    "label": _("📅 إدارة الحجوزات"),
                    "description": _("Manage all studio bookings")
                },
                {
                    "type": "doctype",
                    "name": "Service",
                    "label": _("📸 إدارة الخدمات"),
                    "description": _("Manage studio services")
                },
                {
                    "type": "doctype",
                    "name": "Photographer",
                    "label": _("👥 إدارة المصورين"),
                    "description": _("Manage photographers")
                },
                {
                    "type": "doctype",
                    "name": "Category",
                    "label": _("🏷️ إدارة الفئات"),
                    "description": _("Manage service categories")
                },
                {
                    "type": "doctype",
                    "name": "Package_Service",
                    "label": _("📦 إدارة الباقات"),
                    "description": _("Manage service packages")
                },
                {
                    "type": "link",
                    "name": "User",
                    "label": _("👤 إدارة المستخدمين"),
                    "link": "/app/user",
                    "description": _("Manage system users")
                },
                {
                    "type": "doctype",
                    "name": "Booking_Settings",
                    "label": _("🔧 الإعدادات"),
                    "description": _("System settings")
                },
                {
                    "type": "doctype",
                    "name": "Booking_Report",
                    "label": _("📊 التقارير"),
                    "description": _("View and generate reports")
                }
            ]
        }
    ]
