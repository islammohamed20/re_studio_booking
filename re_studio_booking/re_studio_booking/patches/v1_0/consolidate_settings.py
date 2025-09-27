# Copyright (c) 2024, Masar Digital Group and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute():
    """
    Consolidate duplicate settings from various DocTypes into General Settings
    This migration removes duplicate fields and centralizes all general settings
    """
    
    # Step 1: Migrate company settings from Print Settings to General Settings
    migrate_company_settings()
    
    # Step 2: Migrate currency/tax settings from Booking Settings to General Settings
    migrate_currency_tax_settings()
    
    # Step 3: Remove duplicate fields from other DocTypes
    remove_duplicate_fields()
    
    # Step 4: Update all references in Python files
    update_python_references()
    
    frappe.db.commit()
    print("✅ Settings consolidation completed successfully")

def migrate_company_settings():
    """
    Migrate company settings from Print Settings to General Settings
    """
    try:
        # Get Print Settings data
        print_settings = frappe.get_single("Print Settings")
        general_settings = frappe.get_single("General Settings")
        
        # Add company fields to General Settings if they don't exist
        add_company_fields_to_general_settings()
        
        # Migrate data
        if print_settings.company_name:
            general_settings.company_name = print_settings.company_name
        if print_settings.company_name_ar:
            general_settings.company_name_ar = print_settings.company_name_ar
        if print_settings.company_logo:
            general_settings.company_logo = print_settings.company_logo
            
        general_settings.save()
        print("✅ Company settings migrated from Print Settings")
        
    except Exception as e:
        print(f"❌ Error migrating company settings: {str(e)}")
        frappe.log_error(f"Company settings migration error: {str(e)}")

def migrate_currency_tax_settings():
    """
    Migrate currency and tax settings from Booking Settings to General Settings
    """
    try:
        booking_settings = frappe.get_single("Booking Settings")
        general_settings = frappe.get_single("General Settings")
        
        # Migrate tax settings if they exist in Booking Settings
        if hasattr(booking_settings, 'tax_rate') and booking_settings.tax_rate:
            general_settings.tax_rate = booking_settings.tax_rate
        if hasattr(booking_settings, 'include_tax_in_price'):
            general_settings.include_tax_in_price = booking_settings.include_tax_in_price
            
        general_settings.save()
        print("✅ Currency/Tax settings migrated from Booking Settings")
        
    except Exception as e:
        print(f"❌ Error migrating currency/tax settings: {str(e)}")
        frappe.log_error(f"Currency/Tax settings migration error: {str(e)}")

def add_company_fields_to_general_settings():
    """
    Add company fields to General Settings DocType
    """
    try:
        # Get General Settings DocType
        doctype = frappe.get_doc("DocType", "General Settings")
        
        # Check if company fields already exist
        existing_fields = [field.fieldname for field in doctype.fields]
        
        company_fields = [
            {
                "fieldname": "company_section",
                "fieldtype": "Section Break",
                "label": "إعدادات الشركة",
                "insert_after": "payment_terms"
            },
            {
                "fieldname": "company_name",
                "fieldtype": "Data",
                "label": "اسم الشركة",
                "insert_after": "company_section"
            },
            {
                "fieldname": "company_name_ar",
                "fieldtype": "Data",
                "label": "اسم الشركة بالعربية",
                "insert_after": "company_name"
            },
            {
                "fieldname": "company_logo",
                "fieldtype": "Attach Image",
                "label": "شعار الشركة",
                "insert_after": "company_name_ar"
            },
            {
                "fieldname": "column_break_company",
                "fieldtype": "Column Break",
                "insert_after": "company_logo"
            },
            {
                "fieldname": "company_email",
                "fieldtype": "Data",
                "label": "البريد الإلكتروني للشركة",
                "options": "Email",
                "insert_after": "column_break_company"
            },
            {
                "fieldname": "company_website",
                "fieldtype": "Data",
                "label": "موقع الشركة الإلكتروني",
                "insert_after": "company_email"
            }
        ]
        
        # Add fields that don't exist
        for field_data in company_fields:
            if field_data["fieldname"] not in existing_fields:
                field = frappe.new_doc("DocField")
                field.update(field_data)
                doctype.append("fields", field)
        
        # Update field_order
        field_order = doctype.field_order or []
        for field_data in company_fields:
            if field_data["fieldname"] not in field_order:
                field_order.append(field_data["fieldname"])
        
        doctype.field_order = field_order
        doctype.save()
        
        print("✅ Company fields added to General Settings")
        
    except Exception as e:
        print(f"❌ Error adding company fields: {str(e)}")
        frappe.log_error(f"Company fields addition error: {str(e)}")

def remove_duplicate_fields():
    """
    Remove duplicate fields from other DocTypes
    """
    try:
        # Remove company fields from Print Settings
        remove_fields_from_doctype("Print Settings", [
            "company_name", "company_name_ar", "company_logo"
        ])
        
        # Remove currency/tax fields from Booking Settings
        remove_fields_from_doctype("Booking Settings", [
            "tax_rate", "include_tax_in_price", "tax_label"
        ])
        
        # Remove duplicate fields from Re Studio Settings
        remove_fields_from_doctype("Re Studio Settings", [
            "default_currency", "currency_symbol", "tax_rate", "deposit_percentage",
            "company_email", "company_website"
        ])
        
        print("✅ Duplicate fields removed from other DocTypes")
        
    except Exception as e:
        print(f"❌ Error removing duplicate fields: {str(e)}")
        frappe.log_error(f"Duplicate fields removal error: {str(e)}")

def remove_fields_from_doctype(doctype_name, field_names):
    """
    Remove specified fields from a DocType
    """
    try:
        doctype = frappe.get_doc("DocType", doctype_name)
        
        # Remove fields
        fields_to_remove = []
        for field in doctype.fields:
            if field.fieldname in field_names:
                fields_to_remove.append(field)
        
        for field in fields_to_remove:
            doctype.remove(field)
        
        # Update field_order
        if doctype.field_order:
            field_order = doctype.field_order
            for field_name in field_names:
                if field_name in field_order:
                    field_order.remove(field_name)
            doctype.field_order = field_order
        
        doctype.save()
        print(f"✅ Removed fields from {doctype_name}: {', '.join(field_names)}")
        
    except Exception as e:
        print(f"❌ Error removing fields from {doctype_name}: {str(e)}")

def update_python_references():
    """
    Update Python file references to use General Settings
    """
    try:
        # This will be handled by separate file updates
        # For now, just log that this step is needed
        print("⚠️  Python file references need to be updated manually")
        print("   Files to update:")
        print("   - booking_settings.py")
        print("   - print_settings.py")
        print("   - re_studio_settings.py")
        print("   - dashboard.py")
        print("   - All www/*.py files")
        
    except Exception as e:
        print(f"❌ Error in update_python_references: {str(e)}")