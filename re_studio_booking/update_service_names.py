import frappe

def update_service_arabic_names():
    """
    Update all services with Arabic names based on the English names
    """
    frappe.db.sql("""
        UPDATE `tabService`
        SET service_name_ar = service_name_en
        WHERE IFNULL(service_name_ar, '') = ''
    """)
    frappe.db.commit()
    print("Updated all services with Arabic names")

if __name__ == "__main__":
    update_service_arabic_names()
