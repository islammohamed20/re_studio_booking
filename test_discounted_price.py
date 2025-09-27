#!/usr/bin/env python3
"""
Test script for B2B discount functionality with discounted_price field
"""
import frappe

def test_discounted_price_functionality():
    """Test discounted price field functionality"""
    
    print("🧪 Testing Discounted Price Functionality")
    print("=" * 60)
    
    # Test 1: Check Booking Service Item DocType structure
    print("📋 Testing Booking Service Item DocType...")
    
    try:
        meta = frappe.get_meta("Booking Service Item")
        discounted_price_field = None
        
        for field in meta.fields:
            if field.fieldname == "discounted_price":
                discounted_price_field = field
                break
        
        if discounted_price_field:
            print(f"   ✅ discounted_price field found")
            print(f"      Type: {discounted_price_field.fieldtype}")
            print(f"      Label: {discounted_price_field.label}")
            print(f"      Read Only: {discounted_price_field.read_only}")
            print(f"      In List View: {discounted_price_field.in_list_view}")
        else:
            print("   ❌ discounted_price field not found")
            
    except Exception as e:
        print(f"   ❌ Error checking Booking Service Item: {str(e)}")
    
    # Test 2: Check Client DocType B2B functionality
    print("\n👤 Testing Client DocType...")
    
    try:
        # Create test B2B client
        test_client = frappe.get_doc({
            "doctype": "Client",
            "client_name": "Test B2B Company Pro",
            "client_type": "Company",  # Using Company since that's what we see in the files
            "b2b_discount_percentage": 20.0,
            "mobile": "966501111111",
            "email": "test@b2bcompanypro.com"
        })
        test_client.insert(ignore_permissions=True)
        
        print(f"   ✅ B2B Client created: {test_client.name}")
        print(f"      Client Type: {test_client.client_type}")
        print(f"      B2B Discount: {test_client.b2b_discount_percentage}%")
        
        # Create test B2C client
        test_client_b2c = frappe.get_doc({
            "doctype": "Client",
            "client_name": "Test Individual Customer Pro",
            "client_type": "Individual",
            "mobile": "966501111112",
            "email": "test@individualcustomer.com"
        })
        test_client_b2c.insert(ignore_permissions=True)
        
        print(f"   ✅ B2C Client created: {test_client_b2c.name}")
        
    except Exception as e:
        print(f"   ❌ Error creating clients: {str(e)}")
        return
    
    # Test 3: Create test services
    print("\n🛠️ Testing Service Creation...")
    
    try:
        # Service 1: With high price for clear discount visibility
        test_service_1 = frappe.get_doc({
            "doctype": "Service",
            "service_name_ar": "تصوير فوتوغرافي احترافي",
            "service_name_en": "Professional Photography Service",
            "price": 1500.0,  # Higher price for clear discount calculation
            "duration": 3,
            "duration_unit": "ساعة"
        })
        test_service_1.insert(ignore_permissions=True)
        
        print(f"   ✅ Service 1 created: {test_service_1.name}")
        print(f"      Price: {test_service_1.price} SAR")
        
        # Service 2: Different price
        test_service_2 = frappe.get_doc({
            "doctype": "Service", 
            "service_name_ar": "تصوير فيديو",
            "service_name_en": "Video Recording Service",
            "price": 800.0,
            "duration": 2,
            "duration_unit": "ساعة"
        })
        test_service_2.insert(ignore_permissions=True)
        
        print(f"   ✅ Service 2 created: {test_service_2.name}")
        print(f"      Price: {test_service_2.price} SAR")
        
    except Exception as e:
        print(f"   ❌ Error creating services: {str(e)}")
        return
    
    # Test 4: Create booking with B2B client and test discount calculation
    print("\n📅 Testing B2B Booking with Discounted Prices...")
    
    try:
        # Create booking for B2B client
        test_booking = frappe.get_doc({
            "doctype": "Booking",
            "client": test_client.name,
            "booking_date": "2025-01-31",
            "start_time": "10:00:00",
            "end_time": "16:00:00",
            "booking_type": "Service",
            "payment_status": "Pending"
        })
        
        # Add services to the booking
        test_booking.append("selected_services_table", {
            "service": test_service_1.name,
            "service_name": test_service_1.service_name_en,
            "quantity": 2,
            "service_price": test_service_1.price,
            "total_amount": test_service_1.price * 2
        })
        
        test_booking.append("selected_services_table", {
            "service": test_service_2.name,
            "service_name": test_service_2.service_name_en,
            "quantity": 1,
            "service_price": test_service_2.price,
            "total_amount": test_service_2.price * 1
        })
        
        test_booking.insert(ignore_permissions=True)
        
        print(f"   ✅ B2B Booking created: {test_booking.name}")
        print(f"   📊 Service Items Analysis:")
        
        for idx, item in enumerate(test_booking.selected_services_table, 1):
            original_price = float(item.service_price)
            discounted_price = float(item.discounted_price) if item.discounted_price else original_price
            quantity = float(item.quantity)
            total_amount = float(item.total_amount)
            
            expected_discount = (original_price * 20) / 100  # 20% discount
            expected_discounted_price = original_price - expected_discount
            expected_total = expected_discounted_price * quantity
            
            print(f"      Service {idx}: {item.service_name}")
            print(f"         Original Price: {original_price} SAR")
            print(f"         Expected Discounted Price: {expected_discounted_price} SAR")
            print(f"         Actual Discounted Price: {discounted_price} SAR")
            print(f"         Quantity: {quantity}")
            print(f"         Expected Total: {expected_total} SAR")
            print(f"         Actual Total: {total_amount} SAR")
            
            if abs(discounted_price - expected_discounted_price) < 0.01:
                print(f"         ✅ Discount calculation correct!")
            else:
                print(f"         ❌ Discount calculation error!")
            
            if abs(total_amount - expected_total) < 0.01:
                print(f"         ✅ Total amount calculation correct!")
            else:
                print(f"         ❌ Total amount calculation error!")
            print()
        
        print(f"   🔢 Booking Total Amount: {test_booking.total_amount} SAR")
        
        # Calculate expected booking total
        expected_booking_total = 0
        for item in test_booking.selected_services_table:
            original_price = float(item.service_price)
            expected_discounted_price = original_price - ((original_price * 20) / 100)
            expected_item_total = expected_discounted_price * float(item.quantity)
            expected_booking_total += expected_item_total
        
        print(f"   🎯 Expected Booking Total: {expected_booking_total} SAR")
        
        if abs(float(test_booking.total_amount) - expected_booking_total) < 0.01:
            print("   ✅ Booking total calculation correct!")
        else:
            print("   ❌ Booking total calculation error!")
            
    except Exception as e:
        print(f"   ❌ Error creating B2B booking: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 5: Create booking with B2C client (no discount)
    print("\n📅 Testing B2C Booking (No Discount)...")
    
    try:
        test_booking_b2c = frappe.get_doc({
            "doctype": "Booking",
            "client": test_client_b2c.name,
            "booking_date": "2025-01-31",
            "start_time": "17:00:00",
            "end_time": "20:00:00",
            "booking_type": "Service",
            "payment_status": "Pending"
        })
        
        # Add one service
        test_booking_b2c.append("selected_services_table", {
            "service": test_service_1.name,
            "service_name": test_service_1.service_name_en,
            "quantity": 1,
            "service_price": test_service_1.price,
            "total_amount": test_service_1.price
        })
        
        test_booking_b2c.insert(ignore_permissions=True)
        
        print(f"   ✅ B2C Booking created: {test_booking_b2c.name}")
        
        for item in test_booking_b2c.selected_services_table:
            original_price = float(item.service_price)
            discounted_price = float(item.discounted_price) if item.discounted_price else original_price
            
            print(f"      Service: {item.service_name}")
            print(f"         Original Price: {original_price} SAR")
            print(f"         Discounted Price: {discounted_price} SAR")
            print(f"         Total Amount: {item.total_amount} SAR")
            
            if abs(discounted_price - original_price) < 0.01:
                print("         ✅ No discount applied - correct for B2C!")
            else:
                print("         ❌ Unexpected discount applied for B2C client!")
                
    except Exception as e:
        print(f"   ❌ Error creating B2C booking: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 Discounted Price Testing Complete!")
    
    frappe.destroy()

if __name__ == "__main__":
    frappe.init(site="site1.local")
    frappe.connect()
    test_discounted_price_functionality()
