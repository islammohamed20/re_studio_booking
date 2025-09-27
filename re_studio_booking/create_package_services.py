import frappe

def execute():
    """Create Package Service test data with correct child table name"""
    try:
        print("=== Creating Package Service test data ===")
        
        # Get services
        services = frappe.get_all("Service", fields=["name", "service_name_en", "price"], limit=3)
        print(f"Available services: {len(services)}")
        
        # Get first package
        packages = frappe.get_all("Package", fields=["name"], limit=1)
        if packages and services:
            pkg_name = packages[0].name
            pkg_doc = frappe.get_doc("Package", pkg_name)
            
            print(f"Working with package: {pkg_name}")
            print(f"Current package_services count: {len(pkg_doc.package_services)}")
            
            # Clear existing services first
            pkg_doc.package_services = []
            
            # Add services to package_services child table
            for i, service in enumerate(services):
                pkg_doc.append("package_services", {
                    "service": service.name,
                    "service_name": service.service_name_en,
                    "quantity": i + 1,  # 1, 2, 3 quantities
                    "service_price": service.price,
                    "base_price": service.price,
                    "package_price": service.price * (0.9 - i * 0.05)  # Decreasing discount
                })
                print(f"Added service: {service.name} ({service.service_name_en})")
            
            # Save the package
            pkg_doc.save()
            frappe.db.commit()
            print(f"Saved package with {len(pkg_doc.package_services)} services")
            
            # Verify creation
            new_services = frappe.get_all("Package Service", 
                filters={"parent": pkg_name}, 
                fields=["service", "service_name", "quantity", "base_price", "package_price"],
                ignore_permissions=True)
            print(f"Verification: Found {len(new_services)} Package Service records")
            for svc in new_services:
                print(f"  - {svc.service}: {svc.service_name} (Qty: {svc.quantity}, Base: {svc.base_price}, Package: {svc.package_price})")
            
            # Test our fetch function
            print("\n=== Testing fetch function ===")
            from re_studio_booking.re_studio_booking.doctype.booking.booking import fetch_package_services_for_booking
            result = fetch_package_services_for_booking(pkg_name)
            print(f"Fetch result: {result}")
            
            if result and "rows" in result and len(result["rows"]) > 0:
                print("SUCCESS: Package services are now available!")
                for row in result["rows"]:
                    print(f"  Row: {row}")
            else:
                print("ISSUE: Still no rows returned from fetch function")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return "Package service creation completed"
