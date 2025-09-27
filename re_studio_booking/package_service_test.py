import frappe

def execute():
    """Check Package Service data and create test entries if needed"""
    try:
        print("=== Checking all Package Service records ===")
        all_services = frappe.get_all("Package Service", fields=["name", "parent", "service", "service_name"], ignore_permissions=True)
        print(f"Total Package Service records: {len(all_services)}")
        
        if len(all_services) == 0:
            print("No Package Service records found. Let's check if Services exist:")
            services = frappe.get_all("Service", fields=["name", "service_name", "price"], limit=5)
            print(f"Found {len(services)} services:")
            for svc in services:
                print(f"  - {svc.name}: {svc.service_name} (Price: {svc.price})")
            
            if len(services) > 0:
                print("\nCreating test Package Service entries...")
                # Get first package
                packages = frappe.get_all("Package", fields=["name"], limit=1)
                if packages:
                    pkg_name = packages[0].name
                    pkg_doc = frappe.get_doc("Package", pkg_name)
                    
                    # Add first service to package
                    first_service = services[0]
                    pkg_doc.append("services", {
                        "service": first_service.name,
                        "service_name": first_service.service_name,
                        "quantity": 1,
                        "service_price": first_service.price,
                        "base_price": first_service.price,
                        "package_price": first_service.price * 0.9  # 10% package discount
                    })
                    
                    # Add second service if available
                    if len(services) > 1:
                        second_service = services[1]
                        pkg_doc.append("services", {
                            "service": second_service.name,
                            "service_name": second_service.service_name,
                            "quantity": 2,
                            "service_price": second_service.price,
                            "base_price": second_service.price,
                            "package_price": second_service.price * 0.85  # 15% package discount
                        })
                    
                    pkg_doc.save()
                    frappe.db.commit()
                    print(f"Added services to package {pkg_name}")
                    
                    # Verify creation
                    new_services = frappe.get_all("Package Service", 
                        filters={"parent": pkg_name}, 
                        fields=["service", "service_name", "quantity", "base_price", "package_price"],
                        ignore_permissions=True)
                    print(f"Verification: Found {len(new_services)} services in package")
                    for svc in new_services:
                        print(f"  - {svc.service}: {svc.service_name} (Qty: {svc.quantity}, Base: {svc.base_price}, Package: {svc.package_price})")
        else:
            print("Existing Package Service records:")
            for svc in all_services:
                print(f"  - {svc.name}: {svc.parent} -> {svc.service} ({svc.service_name})")
        
        print("\n=== Testing fetch function again ===")
        packages = frappe.get_all("Package", fields=["name"], limit=1)
        if packages:
            pkg_name = packages[0].name
            from re_studio_booking.re_studio_booking.doctype.booking.booking import fetch_package_services_for_booking
            result = fetch_package_services_for_booking(pkg_name)
            print(f"Fetch result: {result}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return "Package service check completed"
