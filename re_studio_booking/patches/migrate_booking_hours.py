import frappe
from datetime import datetime, timedelta

def execute():
    """Migrate existing bookings to calculate total booked hours and update service quantities"""
    
    # Get all existing service bookings that have start_time and end_time
    bookings = frappe.get_all(
        "Booking",
        filters={
            "booking_type": "Service",
            "start_time": ["is", "set"],
            "end_time": ["is", "set"]
        },
        fields=["name", "start_time", "end_time"]
    )
    
    frappe.db.commit()
    
    for booking_data in bookings:
        try:
            booking = frappe.get_doc("Booking", booking_data.name)
            
            start_time = booking_data.start_time
            end_time = booking_data.end_time
            
            if not start_time or not end_time:
                continue
                
            # Convert to datetime objects if they are strings
            if isinstance(start_time, str):
                start_time = datetime.strptime(start_time, "%H:%M:%S").time()
            if isinstance(end_time, str):
                end_time = datetime.strptime(end_time, "%H:%M:%S").time()
            
            # Calculate hours difference
            start_datetime = datetime.combine(datetime.today(), start_time)
            end_datetime = datetime.combine(datetime.today(), end_time)
            
            # Handle case where end time is next day
            if end_datetime < start_datetime:
                end_datetime = datetime.combine(datetime.today() + timedelta(days=1), end_time)
            
            # Calculate total hours
            time_diff = end_datetime - start_datetime
            total_hours = time_diff.total_seconds() / 3600
            
            # Update the booking
            booking.total_booked_hours = round(total_hours, 2)
            
            # Update services table with calculated hours
            if hasattr(booking, 'selected_services_table') and booking.selected_services_table:
                for service_row in booking.selected_services_table:
                    service_row.quantity = round(total_hours, 2)
                    # Recalculate total amount based on new quantity
                    if service_row.service_price:
                        service_row.total_amount = service_row.quantity * service_row.service_price
            
            # Save without running validation to avoid conflicts
            booking.save(ignore_permissions=True, ignore_validate=True)
            
            print(f"Updated booking {booking.name} with {total_hours} hours")
            
        except Exception as e:
            print(f"Error updating booking {booking_data.name}: {str(e)}")
            frappe.log_error(f"Error migrating booking hours for {booking_data.name}: {str(e)}")
            continue
    
    frappe.db.commit()
    print("Migration completed")
