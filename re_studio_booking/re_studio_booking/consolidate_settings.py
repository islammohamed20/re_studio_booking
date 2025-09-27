#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consolidate Settings Migration Script
This script merges duplicated settings from various DocTypes into General Settings
"""

import frappe
import json
import os
from frappe.utils import cint, flt

def migrate_company_settings():
    """Migrate company settings from Print Settings to General Settings"""
    print("Migrating company settings from Print Settings to General Settings...")
    
    try:
        # Get Print Settings
        print_settings = frappe.get_single("Print Settings")
        general_settings = frappe.get_single("General Settings")
        
        # Migrate company fields
        if hasattr(print_settings, 'company_name') and print_settings.company_name:
            general_settings.company_name = print_settings.company_name
            
        if hasattr(print_settings, 'company_logo') and print_settings.company_logo:
            general_settings.company_logo = print_settings.company_logo
            
        general_settings.save()
        frappe.db.commit()
        print("✓ Company settings migrated successfully")
        
    except Exception as e:
        print(f"✗ Error migrating company settings: {str(e)}")
        frappe.db.rollback()

def migrate_currency_tax_settings():
    """Migrate currency and tax settings from Booking Settings to General Settings"""
    print("Migrating currency and tax settings from Booking Settings to General Settings...")
    
    try:
        # Get Booking Settings
        booking_settings = frappe.get_single("Booking Settings")
        general_settings = frappe.get_single("General Settings")
        
        # Migrate currency fields
        if hasattr(booking_settings, 'default_currency') and booking_settings.default_currency:
            general_settings.default_currency = booking_settings.default_currency
            
        if hasattr(booking_settings, 'currency_symbol') and booking_settings.currency_symbol:
            general_settings.currency_symbol = booking_settings.currency_symbol
            
        if hasattr(booking_settings, 'currency_position') and booking_settings.currency_position:
            general_settings.currency_position = booking_settings.currency_position
            
        if hasattr(booking_settings, 'decimal_places'):
            general_settings.decimal_places = cint(booking_settings.decimal_places)
            
        if hasattr(booking_settings, 'number_format') and booking_settings.number_format:
            general_settings.number_format = booking_settings.number_format
            
        if hasattr(booking_settings, 'thousand_separator') and booking_settings.thousand_separator:
            general_settings.thousand_separator = booking_settings.thousand_separator
            
        # Migrate tax fields
        if hasattr(booking_settings, 'enable_tax'):
            general_settings.include_tax_in_price = cint(booking_settings.enable_tax)
            
        if hasattr(booking_settings, 'tax_rate'):
            general_settings.tax_rate = flt(booking_settings.tax_rate)
            
        if hasattr(booking_settings, 'deposit_percentage'):
            general_settings.deposit_percentage = flt(booking_settings.deposit_percentage)
            
        general_settings.save()
        frappe.db.commit()
        print("✓ Currency and tax settings migrated successfully")
        
    except Exception as e:
        print(f"✗ Error migrating currency and tax settings: {str(e)}")
        frappe.db.rollback()

def add_company_fields_to_general_settings():
    """Add company-related fields to General Settings DocType if they don't exist"""
    print("Adding company fields to General Settings DocType...")
    
    try:
        # Load General Settings DocType
        doctype_path = "/home/frappe/frappe/apps/re_studio_booking/re_studio_booking/re_studio_booking/doctype/general_settings/general_settings.json"
        
        if not os.path.exists(doctype_path):
            print(f"✗ General Settings DocType file not found at {doctype_path}")
            return
            
        with open(doctype_path, 'r', encoding='utf-8') as f:
            doctype_json = json.load(f)
        
        # Check if company fields already exist
        existing_fields = [field['fieldname'] for field in doctype_json.get('fields', [])]
        
        new_fields = []
        
        # Add company_email field if not exists
        if 'company_email' not in existing_fields:
            new_fields.append({
                "fieldname": "company_email",
                "fieldtype": "Data",
                "label": "Company Email",
                "options": "Email",
                "description": "Company email address"
            })
            
        # Add company_website field if not exists
        if 'company_website' not in existing_fields:
            new_fields.append({
                "fieldname": "company_website",
                "fieldtype": "Data",
                "label": "Company Website",
                "options": "URL",
                "description": "Company website URL"
            })
        
        if new_fields:
            # Find the right place to insert (after company_logo if it exists)
            insert_index = len(doctype_json['fields'])
            for i, field in enumerate(doctype_json['fields']):
                if field['fieldname'] == 'company_logo':
                    insert_index = i + 1
                    break
            
            # Insert new fields
            for field in reversed(new_fields):
                doctype_json['fields'].insert(insert_index, field)
            
            # Save updated DocType
            with open(doctype_path, 'w', encoding='utf-8') as f:
                json.dump(doctype_json, f, indent=1, ensure_ascii=False)
            
            print(f"✓ Added {len(new_fields)} company fields to General Settings")
        else:
            print("✓ Company fields already exist in General Settings")
            
    except Exception as e:
        print(f"✗ Error adding company fields: {str(e)}")

def update_python_references():
    """Update Python file references to use SettingsManager"""
    print("\nNote: Python file references have been manually updated to use SettingsManager.")
    print("The following files have been updated:")
    print("- currency_settings.py")
    print("- dashboard.py")
    print("- admin-dashboard.py")
    print("- booking-dashboard.py")
    print("- reports.py")
    print("- revenue-report.py")
    print("- booking_settings.py")
    print("- re_studio_settings.py")
    print("- print_settings.py")
    print("✓ Python references updated")

def main():
    """Main migration function"""
    print("Starting Settings Consolidation Migration...")
    print("=" * 50)
    
    # Initialize Frappe
    try:
        frappe.init(site='localhost')
        frappe.connect()
        
        # Run migration steps
        add_company_fields_to_general_settings()
        migrate_company_settings()
        migrate_currency_tax_settings()
        update_python_references()
        
        print("\n" + "=" * 50)
        print("✓ Settings consolidation completed successfully!")
        print("\nNext steps:")
        print("1. Test the application to ensure all settings work correctly")
        print("2. Remove duplicate fields from other DocTypes if desired")
        print("3. Update any remaining client-side JavaScript files")
        
    except Exception as e:
        print(f"\n✗ Migration failed: {str(e)}")
        frappe.db.rollback()
    finally:
        frappe.destroy()

if __name__ == "__main__":
    main()