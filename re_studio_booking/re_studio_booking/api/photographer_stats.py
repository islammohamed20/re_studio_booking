import frappe
from frappe.utils import getdate, nowdate, format_date, format_time

@frappe.whitelist()
def get_booking_stats(photographer):
    """Get booking statistics for a photographer"""
    # Get total bookings count
    total_bookings = frappe.db.count("Booking", {"photographer": photographer})
    
    # Get completed bookings count
    completed_bookings = frappe.db.count("Booking", {"photographer": photographer, "status": "Completed"})
    
    # Get upcoming bookings count
    today = nowdate()
    upcoming_bookings = frappe.db.count(
        "Booking", 
        {
            "photographer": photographer, 
            "booking_date": [">", today],
            "status": ["in", ["Confirmed", "Pending"]]
        }
    )
    
    # Get list of upcoming bookings
    upcoming_list = frappe.get_all(
        "Booking",
        filters={
            "photographer": photographer,
            "booking_date": [">", today],
            "status": ["in", ["Confirmed", "Pending"]]
        },
        fields=[
            "name", "booking_date", "start_time", "service", 
            "service_name", "client_name", "status"
        ],
        order_by="booking_date asc, start_time asc",
        limit=10
    )
    
    # Format dates and times for display
    for booking in upcoming_list:
        booking.booking_date = format_date(booking.booking_date)
        booking.start_time = format_time(booking.start_time)
    
    return {
        "total_bookings": total_bookings,
        "completed_bookings": completed_bookings,
        "upcoming_bookings": upcoming_bookings,
        "upcoming_bookings_list": upcoming_list
    }
