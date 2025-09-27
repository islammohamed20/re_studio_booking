# Real-time hooks for Re Studio Booking
# This file contains hooks that trigger real-time updates when Doctypes are modified

import frappe
from frappe import _

def on_service_update(doc, method):
    """Hook called when Service document is updated"""
    # Emit real-time event for service updates
    frappe.publish_realtime(
        event='service_updated',
        message={
            'service': doc.name,
            'is_active': doc.is_active,
            'service_name': doc.service_name
        },
        user=frappe.session.user
    )
    
    # Log the update for debugging
    frappe.logger().info(f"Service {doc.name} updated - Active: {doc.is_active}")

def on_service_package_update(doc, method):
    """Hook called when Service Package document is updated"""
    # Emit real-time event for package updates
    frappe.publish_realtime(
        event='package_updated',
        message={
            'package': doc.name,
            'is_active': doc.is_active,
            'package_name': doc.package_name_en
        },
        user=frappe.session.user
    )
    
    # Log the update for debugging
    frappe.logger().info(f"Package {doc.name} updated - Active: {doc.is_active}")

def validate_service_deactivation(doc, method):
    """Validate service deactivation and show warnings"""
    if method == "validate" and not doc.is_active:
        # Check if service has active bookings
        active_bookings = frappe.db.count("Booking", {
            "service": doc.name,
            "status": ["in", ["Confirmed", "Pending"]]
        })
        
        if active_bookings > 0:
            frappe.msgprint(
                _("تحذير: هذه الخدمة لديها {0} حجوزات نشطة. تعطيل الخدمة قد يؤثر على هذه الحجوزات.").format(active_bookings),
                indicator="orange",
                alert=True
            )

def validate_package_deactivation(doc, method):
    """Validate package deactivation and show warnings"""
    if method == "validate" and not doc.is_active:
        # Check if package has active bookings
        active_bookings = frappe.db.count("Booking", {
            "service_package": doc.name,
            "status": ["in", ["Confirmed", "Pending"]]
        })
        
        if active_bookings > 0:
            frappe.msgprint(
                _("تحذير: هذه الباقة لديها {0} حجوزات نشطة. تعطيل الباقة قد يؤثر على هذه الحجوزات.").format(active_bookings),
                indicator="orange",
                alert=True
            )

@frappe.whitelist()
def get_realtime_stats():
    """Get current statistics for real-time updates"""
    stats = {
        'services': {
            'total': frappe.db.count("Service"),
            'active': frappe.db.count("Service", {"is_active": 1}),
            'inactive': frappe.db.count("Service", {"is_active": 0})
        },
        'packages': {
            'total': frappe.db.count("Service Package"),
            'active': frappe.db.count("Service Package", {"is_active": 1}),
            'featured': 0,  # No featured field in Service Package doctype
            'inactive': frappe.db.count("Service Package", {"is_active": 0})
        }
    }
    
    return stats

@frappe.whitelist()
def toggle_service_status(service_name, is_active):
    """Toggle service active status"""
    doc = frappe.get_doc("Service", service_name)
    doc.is_active = int(is_active)
    doc.save()
    
    return {
        'success': True,
        'message': _("تم تحديث حالة الخدمة بنجاح"),
        'is_active': doc.is_active
    }

@frappe.whitelist()
def toggle_package_status(package_name, is_active):
    """Toggle package active status"""
    doc = frappe.get_doc("Service Package", package_name)
    doc.is_active = int(is_active)
    doc.save()
    
    return {
        'success': True,
        'message': _("تم تحديث حالة الباقة بنجاح"),
        'is_active': doc.is_active
    }

# Note: toggle_package_featured function removed as 'is_featured' field doesn't exist in Service Package doctype