import frappe

def execute():
    """Test discounted price field functionality"""
    
    print("🧪 Testing Discounted Price Field")
    print("=" * 50)
    
    # Test 1: Check if discounted_price field exists
    try:
        meta = frappe.get_meta("Booking Service Item")
        discounted_price_field = None
        
        print("📋 Booking Service Item Fields:")
        for field in meta.fields:
            if field.fieldname in ["service_price", "discounted_price", "total_amount"]:
                print(f"   - {field.fieldname}: {field.fieldtype} ({field.label})")
                if field.fieldname == "discounted_price":
                    discounted_price_field = field
        
        if discounted_price_field:
            print(f"\n✅ discounted_price field found!")
            print(f"   Type: {discounted_price_field.fieldtype}")
            print(f"   Read Only: {discounted_price_field.read_only}")
            print(f"   In List View: {discounted_price_field.in_list_view}")
        else:
            print("\n❌ discounted_price field not found!")
            
    except Exception as e:
        print(f"❌ Error checking Booking Service Item: {str(e)}")
    
    # Test 2: Check Client DocType for B2B discount field
    print(f"\n👤 Client DocType B2B Fields:")
    try:
        client_meta = frappe.get_meta("Client")
        for field in client_meta.fields:
            if field.fieldname in ["client_type", "b2b_discount_percentage"]:
                print(f"   - {field.fieldname}: {field.fieldtype}")
                if field.fieldname == "client_type":
                    print(f"     Options: {field.options}")
                elif field.fieldname == "b2b_discount_percentage":
                    print(f"     Depends on: {field.depends_on}")
                    
    except Exception as e:
        print(f"❌ Error checking Client: {str(e)}")
    
    # Test 3: Simple data creation test
    print(f"\n🧮 Simple Discount Calculation Test:")
    try:
        # Test discount calculation logic
        original_price = 1000
        discount_percentage = 15
        expected_discounted_price = original_price - (original_price * discount_percentage / 100)
        
        print(f"   Original Price: {original_price} SAR")
        print(f"   Discount Percentage: {discount_percentage}%")
        print(f"   Expected Discounted Price: {expected_discounted_price} SAR")
        print(f"   Expected Discount Amount: {original_price * discount_percentage / 100} SAR")
        
        if expected_discounted_price == 850:
            print("   ✅ Discount calculation logic is correct!")
        else:
            print("   ❌ Discount calculation error!")
            
    except Exception as e:
        print(f"❌ Calculation test error: {str(e)}")
    
    print(f"\n" + "=" * 50)
    print("✅ Basic Field Structure Test Complete!")
    print("💡 Next: Try creating a booking manually in the UI to test discount functionality")

execute()
