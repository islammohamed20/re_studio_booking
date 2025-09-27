import frappe

def test_permissions():
    try:
        # Save original permission flag
        original_flag = frappe.flags.ignore_permissions
        
        # Test with permissions enforcement
        frappe.flags.ignore_permissions = False
        print("\n=== Testing with normal permissions ===")
        
        # Try to get Package Service directly
        try:
            result = frappe.get_all(
                "Package Service",
                filters={"parent": "PKG-00001"},  # Use a real package ID
                fields=["service", "service_name", "quantity", "service_price"],
            )
            print(f"Direct Package Service access (normal permissions): {len(result)} rows found")
        except Exception as e:
            print(f"Direct Package Service access failed: {str(e)}")
        
        # Try our improved fetch function
        try:
            from re_studio_booking.re_studio_booking.doctype.booking.booking import fetch_package_services_for_booking
            result = fetch_package_services_for_booking("PKG-00001")
            if result and "rows" in result:
                print(f"fetch_package_services_for_booking: {len(result['rows'])} rows found")
                if len(result['rows']) > 0:
                    sample_row = result['rows'][0]
                    print(f"Sample row fields: {', '.join(sample_row.keys())}")
                    if 'service' in sample_row:
                        print(f"Sample service field value: {sample_row['service']}")
            else:
                print(f"fetch_package_services_for_booking returned unexpected result: {result}")
        except Exception as e:
            print(f"fetch_package_services_for_booking failed: {str(e)}")
        
        # Test with permissions bypassed
        frappe.flags.ignore_permissions = True
        print("\n=== Testing with ignore_permissions=True ===")
        
        # Try to get Package Service with bypassed permissions
        try:
            result = frappe.get_all(
                "Package Service",
                filters={"parent": "PKG-00001"},  # Use a real package ID
                fields=["service", "service_name", "quantity", "service_price"],
                ignore_permissions=True
            )
            print(f"Direct Package Service access (ignore_permissions): {len(result)} rows found")
        except Exception as e:
            print(f"Direct Package Service access failed: {str(e)}")
        
    finally:
        # Restore original permission flag
        frappe.flags.ignore_permissions = original_flag
    
    return "Tests completed"
