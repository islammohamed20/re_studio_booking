import frappe

def execute():
    """Debug package and permissions issues"""
    try:
        print("=== Checking Package DocType ===")
        packages = frappe.get_all("Package", fields=["name", "package_name"], limit=5)
        print(f"Found {len(packages)} packages:")
        for pkg in packages:
            print(f"  - {pkg.name}: {pkg.package_name}")
        
        print("\n=== Checking Package Service DocType ===")
        if packages:
            pkg_name = packages[0].name
            print(f"Testing with package: {pkg_name}")
            
            # Test direct access
            try:
                services = frappe.get_all("Package Service", 
                    filters={"parent": pkg_name}, 
                    fields=["service", "service_name", "quantity"], 
                    limit=3)
                print(f"Direct access found {len(services)} services")
                for svc in services:
                    print(f"  - Service: {svc.service}, Name: {svc.service_name}")
            except Exception as e:
                print(f"Direct access failed: {str(e)}")
            
            # Test with ignore permissions
            try:
                services = frappe.get_all("Package Service", 
                    filters={"parent": pkg_name}, 
                    fields=["service", "service_name", "quantity"], 
                    ignore_permissions=True,
                    limit=3)
                print(f"Ignore permissions found {len(services)} services")
            except Exception as e:
                print(f"Ignore permissions failed: {str(e)}")
        
        print("\n=== Checking Booking Package Service DocType ===")
        try:
            # Check if the doctype exists and has the service field
            meta = frappe.get_meta("Booking Package Service")
            service_field = meta.get_field("service")
            if service_field:
                print(f"Service field found: {service_field.fieldtype}, options: {service_field.options}")
            else:
                print("Service field NOT found in Booking Package Service")
                
            # List all fields
            fields = [f.fieldname for f in meta.fields]
            print(f"All fields: {', '.join(fields)}")
            
        except Exception as e:
            print(f"Meta check failed: {str(e)}")
        
        print("\n=== Testing fetch_package_services_for_booking ===")
        if packages:
            pkg_name = packages[0].name
            try:
                from re_studio_booking.re_studio_booking.doctype.booking.booking import fetch_package_services_for_booking
                result = fetch_package_services_for_booking(pkg_name)
                print(f"Function result: {result}")
            except Exception as e:
                print(f"Function failed: {str(e)}")
                import traceback
                traceback.print_exc()
        
    except Exception as e:
        print(f"Overall error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return "Debug completed"
