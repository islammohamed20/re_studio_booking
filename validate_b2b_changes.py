import frappe

def test_b2b_functionality():
    """Test B2B/B2C functionality"""
    
    print("🧪 Testing B2B/B2C Functionality")
    print("=" * 50)
    
    # Check Client DocType structure
    client_meta = frappe.get_meta("Client")
    client_type_field = None
    b2b_discount_field = None
    
    for field in client_meta.fields:
        if field.fieldname == "client_type":
            client_type_field = field
        elif field.fieldname == "b2b_discount_percentage":
            b2b_discount_field = field
    
    print("📋 Client DocType Fields:")
    if client_type_field:
        print(f"   ✅ client_type field found")
        print(f"      Options: {client_type_field.options}")
    else:
        print("   ❌ client_type field not found")
    
    if b2b_discount_field:
        print(f"   ✅ b2b_discount_percentage field found")
        print(f"      Type: {b2b_discount_field.fieldtype}")
        print(f"      Depends on: {b2b_discount_field.depends_on}")
    else:
        print("   ❌ b2b_discount_percentage field not found")
    
    # Check Service DocType
    service_meta = frappe.get_meta("Service")
    b2b_discount_service_field = None
    
    for field in service_meta.fields:
        if field.fieldname == "apply_b2b_discount":
            b2b_discount_service_field = field
            break
    
    print("\n🛠️ Service DocType Fields:")
    if b2b_discount_service_field:
        print(f"   ✅ apply_b2b_discount field found")
        print(f"      Type: {b2b_discount_service_field.fieldtype}")
        print(f"      Default: {b2b_discount_service_field.default}")
    else:
        print("   ❌ apply_b2b_discount field not found")
    
    # Check Booking DocType
    booking_meta = frappe.get_meta("Booking")
    wallet_ref_field = None
    visa_ref_field = None
    
    for field in booking_meta.fields:
        if field.fieldname == "electronic_wallet_reference":
            wallet_ref_field = field
        elif field.fieldname == "visa_reference":
            visa_ref_field = field
    
    print("\n📅 Booking DocType Fields:")
    if wallet_ref_field:
        print(f"   ✅ electronic_wallet_reference field found")
        print(f"      Type: {wallet_ref_field.fieldtype}")
        print(f"      Label: {wallet_ref_field.label}")
    else:
        print("   ❌ electronic_wallet_reference field not found")
    
    if visa_ref_field:
        print(f"   ✅ visa_reference field found")
        print(f"      Type: {visa_ref_field.fieldtype}")
        print(f"      Label: {visa_ref_field.label}")
    else:
        print("   ❌ visa_reference field not found")
    
    # Check client types migration
    print("\n🔄 Client Types Migration Status:")
    try:
        old_individual = frappe.db.count("Client", {"client_type": "Individual"})
        old_company = frappe.db.count("Client", {"client_type": "Company"})
        new_b2c = frappe.db.count("Client", {"client_type": "B2C"})
        new_b2b = frappe.db.count("Client", {"client_type": "B2B"})
        
        print(f"   - Old Individual: {old_individual}")
        print(f"   - Old Company: {old_company}")
        print(f"   - New B2C: {new_b2c}")
        print(f"   - New B2B: {new_b2b}")
        
        if old_individual == 0 and old_company == 0:
            print("   ✅ Migration completed successfully!")
        else:
            print("   ⚠️ Some old client types still exist")
            
    except Exception as e:
        print(f"   ❌ Error checking migration: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 B2B/B2C Structure Validation Complete!")

# Execute the test
test_b2b_functionality()
