#!/usr/bin/env python3
"""
Test script for B2B/B2C functionality and payment reference fields
"""
import frappe
import json

def test_b2b_functionality():
    """Test B2B discount functionality"""
    
    # Initialize site
    frappe.init(site="site1.local")
    frappe.connect()
    
    print("🧪 Testing B2B/B2C Functionality")
    print("=" * 50)
    
    # Test 1: Client DocType fields
    print("📋 Testing Client DocType...")
    
    try:
        # Create test B2B client
        test_client = frappe.get_doc({
            "doctype": "Client",
            "client_name": "Test B2B Company",
            "client_type": "B2B",
            "b2b_discount_percentage": 15.0,
            "mobile": "966501234567",
            "email": "test@b2bcompany.com"
        })
        test_client.insert(ignore_permissions=True)
        
        print(f"✅ B2B Client created: {test_client.name}")
        print(f"   - Client Type: {test_client.client_type}")
        print(f"   - B2B Discount: {test_client.b2b_discount_percentage}%")
        
        # Create test B2C client
        test_client_b2c = frappe.get_doc({
            "doctype": "Client",
            "client_name": "Test Individual Customer",
            "client_type": "B2C",
            "mobile": "966509876543",
            "email": "test@individual.com"
        })
        test_client_b2c.insert(ignore_permissions=True)
        
        print(f"✅ B2C Client created: {test_client_b2c.name}")
        print(f"   - Client Type: {test_client_b2c.client_type}")
        
    except Exception as e:
        print(f"❌ Error creating clients: {str(e)}")
    
    # Test 2: Service DocType B2B discount field
    print("\n🛠️ Testing Service DocType...")
    
    try:
        # Create test service with B2B discount enabled
        test_service = frappe.get_doc({
            "doctype": "Service",
            "service_name_ar": "خدمة تصوير تجاري",
            "service_name_en": "Commercial Photography Service",
            "price": 1000.0,
            "apply_b2b_discount": 1,
            "duration": 2,
            "duration_unit": "ساعة"
        })
        test_service.insert(ignore_permissions=True)
        
        print(f"✅ Service created: {test_service.name}")
        print(f"   - Price: {test_service.price} SAR")
        print(f"   - B2B Discount Enabled: {test_service.apply_b2b_discount}")
        
        # Create service without B2B discount
        test_service_no_discount = frappe.get_doc({
            "doctype": "Service", 
            "service_name_ar": "خدمة تصوير عادي",
            "service_name_en": "Regular Photography Service",
            "price": 500.0,
            "apply_b2b_discount": 0,
            "duration": 1,
            "duration_unit": "ساعة"
        })
        test_service_no_discount.insert(ignore_permissions=True)
        
        print(f"✅ Service (no B2B discount) created: {test_service_no_discount.name}")
        
    except Exception as e:
        print(f"❌ Error creating services: {str(e)}")
    
    # Test 3: Booking with B2B discount
    print("\n📅 Testing Booking with B2B Discount...")
    
    try:
        # Create booking for B2B client
        test_booking = frappe.get_doc({
            "doctype": "Booking",
            "client": test_client.name,
            "service": test_service.name,
            "booking_date": "2024-12-31",
            "start_time": "10:00:00",
            "end_time": "12:00:00",
            "booking_type": "Service",
            "payment_status": "Pending",
            "electronic_wallet_reference": "WALLET123456789",
            "visa_reference": "VISA987654321"
        })
        test_booking.insert(ignore_permissions=True)
        
        print(f"✅ B2B Booking created: {test_booking.name}")
        print(f"   - Original Service Price: 1000 SAR")
        print(f"   - B2B Client Discount: 15%")
        print(f"   - Final Total: {test_booking.total_amount} SAR")
        print(f"   - Electronic Wallet Ref: {test_booking.electronic_wallet_reference}")
        print(f"   - Visa Reference: {test_booking.visa_reference}")
        
        # Calculate expected discounted price
        expected_discount = 1000 * 0.15
        expected_total = 1000 - expected_discount
        
        if abs(test_booking.total_amount - expected_total) < 0.01:
            print("✅ B2B Discount applied correctly!")
        else:
            print(f"❌ Discount calculation error. Expected: {expected_total}, Got: {test_booking.total_amount}")
        
    except Exception as e:
        print(f"❌ Error creating B2B booking: {str(e)}")
    
    # Test 4: Booking for B2C client (no discount)
    print("\n📅 Testing Booking for B2C Client...")
    
    try:
        test_booking_b2c = frappe.get_doc({
            "doctype": "Booking",
            "client": test_client_b2c.name,
            "service": test_service.name,
            "booking_date": "2024-12-31", 
            "start_time": "14:00:00",
            "end_time": "16:00:00",
            "booking_type": "Service",
            "payment_status": "Paid"
        })
        test_booking_b2c.insert(ignore_permissions=True)
        
        print(f"✅ B2C Booking created: {test_booking_b2c.name}")
        print(f"   - Service Price: 1000 SAR")
        print(f"   - Total Amount: {test_booking_b2c.total_amount} SAR")
        
        if test_booking_b2c.total_amount == 1000:
            print("✅ No discount applied for B2C client - correct!")
        else:
            print(f"❌ Unexpected total for B2C booking: {test_booking_b2c.total_amount}")
            
    except Exception as e:
        print(f"❌ Error creating B2C booking: {str(e)}")
    
    # Test 5: Check existing clients migration
    print("\n🔄 Testing Client Type Migration...")
    
    try:
        # Check if any old Individual/Company types exist
        old_individual = frappe.db.count("Client", {"client_type": "Individual"})
        old_company = frappe.db.count("Client", {"client_type": "Company"})
        new_b2c = frappe.db.count("Client", {"client_type": "B2C"})
        new_b2b = frappe.db.count("Client", {"client_type": "B2B"})
        
        print(f"📊 Client Type Counts:")
        print(f"   - Old Individual: {old_individual}")
        print(f"   - Old Company: {old_company}")
        print(f"   - New B2C: {new_b2c}")
        print(f"   - New B2B: {new_b2b}")
        
        if old_individual == 0 and old_company == 0:
            print("✅ Migration completed successfully!")
        else:
            print("⚠️ Some old client types still exist")
            
    except Exception as e:
        print(f"❌ Error checking migration: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 B2B/B2C Testing Complete!")
    
    frappe.destroy()

if __name__ == "__main__":
    test_b2b_functionality()
