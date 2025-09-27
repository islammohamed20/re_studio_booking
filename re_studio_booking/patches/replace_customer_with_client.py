# -*- coding: utf-8 -*-
# Replace Customer references with Client

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
    """Replace Customer references with Client in all DocTypes"""
    
    try:
        # Update Booking DocType
        update_booking_doctype()
        
        # Update Booking Quotation DocType
        update_booking_quotation_doctype()
        
        # Update Booking Invoice DocType
        update_booking_invoice_doctype()
        
        # Migrate existing data
        migrate_customer_data_to_client()
        
        print("✅ Customer to Client migration completed successfully")
        
    except Exception as e:
        print(f"❌ Error in execute: {str(e)}")
        frappe.log_error(f"Error replacing customer with client: {str(e)}")

def update_booking_doctype():
    """Update Booking DocType to use Client instead of Customer"""
    try:
        # Remove customer custom field if it exists
        existing_customer_field = frappe.get_all('Custom Field', 
            filters={
                'dt': 'Booking',
                'fieldname': 'customer'
            }
        )
        
        if existing_customer_field:
            for field in existing_customer_field:
                frappe.delete_doc('Custom Field', field.name)
                print(f"✅ Removed customer custom field from Booking")
        
        # Add client field
        client_field = {
            'doctype': 'Booking',
            'fieldname': 'client',
            'label': 'Client',
            'fieldtype': 'Link',
            'options': 'Client',
            'insert_after': 'customer_section',
            'reqd': 1,
            'description': 'Related client'
        }
        
        # Check if client field already exists
        existing_client_field = frappe.get_all('Custom Field', 
            filters={
                'dt': 'Booking',
                'fieldname': 'client'
            }
        )
        
        if not existing_client_field:
            create_custom_field('Booking', client_field)
            print(f"✅ Created client custom field in Booking")
        else:
            print(f"ℹ️  Client field already exists in Booking")
            
    except Exception as e:
        print(f"❌ Error updating Booking DocType: {str(e)}")

def update_booking_quotation_doctype():
    """Update Booking Quotation DocType to use Client instead of Customer"""
    try:
        # Read the JSON file
        doctype_path = frappe.get_app_path('re_studio_booking', 're_studio_booking', 'doctype', 'booking_quotation', 'booking_quotation.json')
        
        with open(doctype_path, 'r', encoding='utf-8') as f:
            doctype_json = frappe.parse_json(f.read())
        
        # Update customer field to client field
        for field in doctype_json.get('fields', []):
            if field.get('fieldname') == 'customer':
                field['fieldname'] = 'client'
                field['label'] = 'Client'
                field['options'] = 'Client'
                break
        
        # Write back to file
        with open(doctype_path, 'w', encoding='utf-8') as f:
            f.write(frappe.as_json(doctype_json, indent=1))
            
        print(f"✅ Updated Booking Quotation DocType")
        
    except Exception as e:
        print(f"❌ Error updating Booking Quotation DocType: {str(e)}")

def update_booking_invoice_doctype():
    """Update Booking Invoice DocType to use Client instead of Customer"""
    try:
        # Read the JSON file
        doctype_path = frappe.get_app_path('re_studio_booking', 're_studio_booking', 'doctype', 'booking_invoice', 'booking_invoice.json')
        
        with open(doctype_path, 'r', encoding='utf-8') as f:
            doctype_json = frappe.parse_json(f.read())
        
        # Update customer field to client field
        for field in doctype_json.get('fields', []):
            if field.get('fieldname') == 'customer':
                field['fieldname'] = 'client'
                field['label'] = 'Client'
                field['options'] = 'Client'
                break
        
        # Write back to file
        with open(doctype_path, 'w', encoding='utf-8') as f:
            f.write(frappe.as_json(doctype_json, indent=1))
            
        print(f"✅ Updated Booking Invoice DocType")
        
    except Exception as e:
        print(f"❌ Error updating Booking Invoice DocType: {str(e)}")

def migrate_customer_data_to_client():
    """Migrate existing Customer data to Client"""
    try:
        # Get all unique customers from bookings
        customers = frappe.db.sql("""
            SELECT DISTINCT 
                customer,
                customer_name,
                customer_email,
                customer_phone
            FROM `tabBooking`
            WHERE customer IS NOT NULL
        """, as_dict=True)
        
        client_mapping = {}
        
        for customer_data in customers:
            try:
                # Check if client already exists
                existing_client = None
                if customer_data.customer_email:
                    existing_client = frappe.db.exists("Client", {"email_id": customer_data.customer_email})
                
                if not existing_client and customer_data.customer_phone:
                    existing_client = frappe.db.exists("Client", {"mobile_no": customer_data.customer_phone})
                
                if existing_client:
                    client_mapping[customer_data.customer] = existing_client
                    continue
                
                # Create new client
                client_doc = frappe.get_doc({
                    "doctype": "Client",
                    "client_name": customer_data.customer_name or customer_data.customer,
                    "email_id": customer_data.customer_email,
                    "mobile_no": customer_data.customer_phone,
                    "status": "Active"
                })
                
                client_doc.insert()
                client_mapping[customer_data.customer] = client_doc.name
                print(f"✅ Created client: {client_doc.name}")
                
            except Exception as e:
                print(f"❌ Error creating client for {customer_data.customer}: {str(e)}")
        
        # Update bookings with new client references
        for customer, client in client_mapping.items():
            try:
                frappe.db.sql("""
                    UPDATE `tabBooking`
                    SET client = %(client)s
                    WHERE customer = %(customer)s
                """, {
                    "client": client,
                    "customer": customer
                })
                print(f"✅ Updated bookings for customer {customer} to client {client}")
            except Exception as e:
                print(f"❌ Error updating bookings for {customer}: {str(e)}")
        
        frappe.db.commit()
        
    except Exception as e:
        print(f"❌ Error migrating customer data: {str(e)}")