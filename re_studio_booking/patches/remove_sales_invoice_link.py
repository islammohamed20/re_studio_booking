# -*- coding: utf-8 -*-
# Remove Sales Invoice link and add Booking Invoice link

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
    """Remove Sales Invoice link and add Booking Invoice link to Booking DocType"""
    
    try:
        # Remove sales_invoice custom field if it exists
        existing_sales_invoice_field = frappe.get_all('Custom Field', 
            filters={
                'dt': 'Booking',
                'fieldname': 'sales_invoice'
            }
        )
        
        if existing_sales_invoice_field:
            for field in existing_sales_invoice_field:
                frappe.delete_doc('Custom Field', field.name)
                print(f"✅ Removed sales_invoice custom field")
        
        # Add new invoice field linking to Booking Invoice
        invoice_field = {
            'doctype': 'Booking',
            'fieldname': 'invoice',
            'label': 'Invoice',
            'fieldtype': 'Link',
            'options': 'Booking Invoice',
            'insert_after': 'status_history',
            'read_only': 1,
            'description': 'Related booking invoice'
        }
        
        # Check if invoice field already exists
        existing_invoice_field = frappe.get_all('Custom Field', 
            filters={
                'dt': 'Booking',
                'fieldname': 'invoice'
            }
        )
        
        if not existing_invoice_field:
            create_custom_field('Booking', invoice_field)
            print(f"✅ Created invoice custom field")
        else:
            print(f"ℹ️  Invoice field already exists")
        
        # Add quotation field linking to Booking Quotation
        quotation_field = {
            'doctype': 'Booking',
            'fieldname': 'quotation',
            'label': 'Quotation',
            'fieldtype': 'Link',
            'options': 'Booking Quotation',
            'insert_after': 'invoice',
            'read_only': 1,
            'description': 'Related booking quotation'
        }
        
        # Check if quotation field already exists
        existing_quotation_field = frappe.get_all('Custom Field', 
            filters={
                'dt': 'Booking',
                'fieldname': 'quotation'
            }
        )
        
        if not existing_quotation_field:
            create_custom_field('Booking', quotation_field)
            print(f"✅ Created quotation custom field")
        else:
            print(f"ℹ️  Quotation field already exists")
        
        # Clear cache to ensure fields are loaded
        frappe.clear_cache(doctype='Booking')
        print("✅ Sales Invoice link removal completed successfully")
        
    except Exception as e:
        print(f"❌ Error in execute: {str(e)}")
        frappe.log_error(f"Error removing sales invoice link: {str(e)}")