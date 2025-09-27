# -*- coding: utf-8 -*-
# Update Booking DocType to add missing fields

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
    """Add missing fields to Booking DocType"""
    
    try:
        # List of custom fields to add
        custom_fields = [
            {
                'doctype': 'Booking',
                'fieldname': 'booking_datetime',
                'label': 'Booking DateTime',
                'fieldtype': 'Datetime',
                'insert_after': 'booking_date',
                'read_only': 1,
                'description': 'Combined booking date and time'
            },
            {
                'doctype': 'Booking',
                'fieldname': 'booking_end_datetime', 
                'label': 'Booking End DateTime',
                'fieldtype': 'Datetime',
                'insert_after': 'booking_datetime',
                'read_only': 1,
                'description': 'Booking end date and time'
            },
            {
                'doctype': 'Booking',
                'fieldname': 'service_name_ar',
                'label': 'Service Name (Arabic)',
                'fieldtype': 'Data',
                'insert_after': 'service_name',
                'read_only': 1,
                'description': 'Service name in Arabic'
            },
            {
                'doctype': 'Booking',
                'fieldname': 'confirmation_sent',
                'label': 'Confirmation Sent',
                'fieldtype': 'Check',
                'insert_after': 'status',
                'default': 0,
                'description': 'Whether confirmation email was sent'
            },
            {
                'doctype': 'Booking',
                'fieldname': 'status_history',
                'label': 'Status History',
                'fieldtype': 'JSON',
                'insert_after': 'confirmation_sent',
                'hidden': 1,
                'description': 'History of status changes'
            },
            {
                'doctype': 'Booking',
                'fieldname': 'booking_time',
                'label': 'Booking Time',
                'fieldtype': 'Time',
                'insert_after': 'booking_date',
                'description': 'Booking time'
            },
            {
                'doctype': 'Booking',
                'fieldname': 'duration',
                'label': 'Duration (Minutes)',
                'fieldtype': 'Int',
                'insert_after': 'booking_time',
                'default': 60,
                'description': 'Booking duration in minutes'
            },
            {
                'doctype': 'Booking',
                'fieldname': 'sales_invoice',
                'label': 'Sales Invoice',
                'fieldtype': 'Link',
                'options': 'Sales Invoice',
                'insert_after': 'status_history',
                'read_only': 1,
                'description': 'Related sales invoice'
            }
        ]
        
        # Create custom fields
        for field in custom_fields:
            try:
                # Check if field already exists
                existing_field = frappe.get_all('Custom Field', 
                    filters={
                        'dt': field['doctype'],
                        'fieldname': field['fieldname']
                    }
                )
                
                if not existing_field:
                    create_custom_field(field['doctype'], field)
                    print(f"✅ Created custom field: {field['fieldname']}")
                else:
                    print(f"ℹ️  Field already exists: {field['fieldname']}")
                    
            except Exception as e:
                print(f"❌ Error creating field {field['fieldname']}: {str(e)}")
        
        # Clear cache to ensure fields are loaded
        frappe.clear_cache(doctype='Booking')
        print("✅ Custom fields update completed successfully")
        
    except Exception as e:
        print(f"❌ Error in execute: {str(e)}")
        frappe.log_error(f"Error updating booking fields: {str(e)}")
