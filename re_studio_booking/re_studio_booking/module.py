from __future__ import unicode_literals
import frappe

def get_module_info():
    """Returns module info for Re Studio Booking module"""
    return {
        "title": "Re Studio Booking",
        "description": "Photography studio booking management system",
        "app_icon": "fa fa-camera",
        "custom_sidebar": True,
        "app_name": "re_studio_booking",
        "color": "#764ba2"
    }
