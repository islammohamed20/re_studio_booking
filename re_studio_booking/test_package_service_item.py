import frappe

def execute():
    """Check Package Service Item data directly"""
    try:
        print("=== Checking Package Service Item records ===")
        all_items = frappe.get_all("Package Service Item", 
            fields=["name", "parent", "service", "service_name", "quantity", "base_price", "package_price"], 
            ignore_permissions=True)
        print(f"Total Package Service Item records: {len(all_items)}")
        
        for item in all_items:
            print(f"  - {item.name}: {item.parent} -> {item.service} ({item.service_name}) Qty:{item.quantity} Base:{item.base_price} Package:{item.package_price}")
        
        print("\n=== Testing fetch function ===")
        packages = frappe.get_all("Package", fields=["name"], limit=1)
        if packages:
            pkg_name = packages[0].name
            print(f"Testing with package: {pkg_name}")
            
            from re_studio_booking.re_studio_booking.doctype.booking.booking import fetch_package_services_for_booking
            result = fetch_package_services_for_booking(pkg_name)
            print(f"Fetch result: {result}")
            
            if result and "rows" in result and len(result["rows"]) > 0:
                print("SUCCESS: Package services are now working!")
                for row in result["rows"]:
                    print(f"  Row: service={row.get('service')}, name={row.get('service_name')}, qty={row.get('quantity')}")
            else:
                print("ISSUE: Still no rows returned")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return "Direct Package Service Item check completed"
