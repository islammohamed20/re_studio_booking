import frappe

def test_discount_calculation():
    """Test discount calculation method directly"""
    
    print("🧪 Testing Discount Calculation Method")
    print("=" * 50)
    
    try:
        # Test the server method directly
        result = frappe.call('re_studio_booking.re_studio_booking.doctype.booking.booking.calculate_service_discounted_price', {
            'client': 'TEST-CLIENT-001',  # This won't exist but should handle gracefully
            'service_price': 1000
        })
        
        print(f"Test with non-existent client: {result}")
        
        # Create a test B2B client
        test_client = frappe.get_doc({
            "doctype": "Client",
            "client_name": "Test Discount Client",
            "client_type": "Company",
            "b2b_discount_percentage": 25.0,
            "mobile": "966555123456",
            "email": "testdiscount@example.com"
        })
        
        try:
            test_client.insert(ignore_permissions=True)
            print(f"✅ Created test client: {test_client.name}")
            
            # Test discount calculation
            result = frappe.call('re_studio_booking.re_studio_booking.doctype.booking.booking.calculate_service_discounted_price', {
                'client': test_client.name,
                'service_price': 1000
            })
            
            expected = 1000 - (1000 * 0.25)  # 25% discount = 750
            
            print(f"Original Price: 1000 SAR")
            print(f"Expected Discounted Price: {expected} SAR")
            print(f"Actual Result: {result} SAR")
            
            if result == expected:
                print("✅ Discount calculation is working correctly!")
            else:
                print("❌ Discount calculation has an issue!")
                
        except Exception as e:
            print(f"Error with test client: {str(e)}")
            
    except Exception as e:
        print(f"❌ Error testing discount calculation: {str(e)}")
    
    print("=" * 50)

test_discount_calculation()
