#!/usr/bin/env python3

import frappe

def fix_booking_base_amount(booking_name="BOOK-0010"):
    """Fix the base_amount calculation for a specific booking"""
    
    # Initialize Frappe
    frappe.init(site='site1.local')
    frappe.connect()
    
    try:
        # Get the booking document
        booking = frappe.get_doc("Booking", booking_name)
        
        print(f"=== Fixing {booking_name} ===")
        print(f"Current base_amount: {booking.base_amount}")
        print(f"Current total_amount: {booking.total_amount}")
        
        if booking.booking_type == "Package":
            # Recalculate base_amount manually
            base_amount = 0
            print("\nPackage Services:")
            for service in booking.package_services_table:
                q = float(service.quantity or 1)
                bp = float(service.base_price or 0)
                row_total = q * bp
                base_amount += row_total
                print(f"  {service.service_name}: {bp} × {q} = {row_total}")
            
            print(f"\nCalculated base_amount: {base_amount}")
            
            # Update the booking
            booking.base_amount = base_amount
            
            # Trigger calculate_package_amounts to ensure everything is consistent
            booking.calculate_package_amounts()
            
            # Save the document
            booking.save(ignore_permissions=True)
            frappe.db.commit()
            
            print(f"Updated base_amount: {booking.base_amount}")
            print(f"Updated total_amount: {booking.total_amount}")
            print(f"Updated deposit_amount: {booking.deposit_amount}")
            
        elif booking.booking_type == "Service":
            # Recalculate for service bookings
            base_amount = 0
            print("\nSelected Services:")
            for service in booking.selected_services_table:
                q = float(service.quantity or 1)
                sp = float(service.service_price or 0)
                row_total = q * sp
                base_amount += row_total
                print(f"  {service.service_name}: {sp} × {q} = {row_total}")
            
            print(f"\nCalculated base_amount: {base_amount}")
            booking.base_amount = base_amount
            booking.calculate_service_amount()
            booking.save(ignore_permissions=True)
            frappe.db.commit()
            
            print(f"Updated base_amount: {booking.base_amount}")
        
        print("✅ Fix completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        frappe.destroy()

if __name__ == "__main__":
    fix_booking_base_amount()
