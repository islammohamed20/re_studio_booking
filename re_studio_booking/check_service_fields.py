import frappe

def check_service_fields():
    try:
        meta = frappe.get_meta('Service')
        print("Available fields in Service DocType:")
        print("=" * 50)
        
        for field in meta.fields:
            if field.fieldtype in ['Currency', 'Float', 'Int', 'Data', 'Link', 'Check']:
                print(f"- {field.fieldname} ({field.fieldtype}) - {field.label}")
        
        return {"success": True}
    except Exception as e:
        print(f"Error: {e}")
        return {"success": False, "error": str(e)}
