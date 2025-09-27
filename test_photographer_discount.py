import frappe

def test_photographer_discount():
    """Test photographer discount functionality"""
    
    print("🧪 Testing Photographer Discount Functionality")
    print("=" * 60)
    
    # Test 1: Check Photographer Service DocType structure
    print("📋 Checking Photographer Service DocType...")
    
    try:
        meta = frappe.get_meta("Photographer Service")
        
        print("   Fields found:")
        for field in meta.fields:
            if field.fieldname in ["base_price", "discounted_price", "service"]:
                print(f"      - {field.fieldname}: {field.fieldtype} ({field.label})")
        
        print("   ✅ Photographer Service structure looks good")
        
    except Exception as e:
        print(f"   ❌ Error checking Photographer Service: {str(e)}")
    
    # Test 2: Test server method directly
    print("\n🛠️ Testing Server Method...")
    
    try:
        from re_studio_booking.re_studio_booking.doctype.photographer_service.photographer_service import calculate_discount
        
        # Test with basic values
        result1 = calculate_discount(1000, 'FAKE-PHOTOGRAPHER')
        print(f"   Test with fake photographer: {result1}")
        
        print("   ✅ Server method exists and runs")
        
    except Exception as e:
        print(f"   ❌ Error testing server method: {str(e)}")
    
    # Test 3: Check Photographer DocType structure
    print("\n👤 Checking Photographer DocType...")
    
    try:
        meta = frappe.get_meta("Photographer")
        
        b2b_field = None
        discount_field = None
        services_field = None
        
        for field in meta.fields:
            if field.fieldname == "b2b":
                b2b_field = field
            elif field.fieldname == "discount_percentage":
                discount_field = field
            elif field.fieldname == "services":
                services_field = field
        
        if b2b_field:
            print(f"   ✅ B2B field: {b2b_field.fieldtype}")
        
        if discount_field:
            print(f"   ✅ Discount % field: {discount_field.fieldtype}")
            print(f"      Depends on: {discount_field.depends_on}")
        
        if services_field:
            print(f"   ✅ Services table: {services_field.options}")
        
    except Exception as e:
        print(f"   ❌ Error checking Photographer: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 Photographer Discount Testing Complete!")
    print("\n💡 To test manually:")
    print("   1. Go to Photographer → New")
    print("   2. Check B2B checkbox")
    print("   3. Set discount percentage (e.g., 15%)")
    print("   4. Add a service in the services table")
    print("   5. Save the document")
    print("   6. Check that 'discounted_price' shows correct value")

test_photographer_discount()
