# Copyright (c) 2023, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, nowdate, add_days, format_date, format_time, get_datetime
from frappe.utils.data import get_time

@frappe.whitelist()
def get_calendar_events(start, end, filters=None):
    """Get events for the calendar view
    
    Args:
        start: Start date
        end: End date
        filters: Additional filters
        
    Returns:
        list: List of events for the calendar
    """
    if not filters:
        filters = {}
    
    # Convert string filters to dict
    if isinstance(filters, str):
        import json
        filters = json.loads(filters)
    
    # Build filter conditions
    conditions = [
        ["booking_date", "between", [start, end]],
        ["docstatus", "<", 2]  # Include submitted and draft bookings
    ]
    
    # Add additional filters
    for key, value in filters.items():
        if value:
            conditions.append([key, "=", value])
    
    # Get bookings
    bookings = frappe.get_all(
        "Booking",
        fields=[
            "name", "booking_date", "start_time", "end_time", "total_booked_hours",
            "client_name", "phone", "photographer", 
            "status", "notes"
        ],
        filters=conditions
    )
    
    # Format bookings for calendar
    events = []
    for booking in bookings:
        # Create booking datetime
        booking_date = booking.booking_date
        start_time = booking.start_time
        end_time = booking.end_time
        
        # Create event
        event = {
            "id": booking.name,
            "title": booking.client_name,
            "start": f"{booking_date} {start_time}",
            "end": f"{booking_date} {end_time}" if end_time else None,
            "allDay": False,
            "status": booking.status,
            "photographer": booking.photographer,
            "phone": booking.phone,
            "notes": booking.notes
        }
        
        # Add color based on status
        status_colors = {
            "Confirmed": "#4CAF50",  # Green
            "Completed": "#2196F3",  # Blue
            "Cancelled": "#F44336",  # Red
        
        }
        
        event["color"] = status_colors.get(booking.status, "#9E9E9E")  # Default gray
        
        events.append(event)
    
    return events

@frappe.whitelist()
def get_photographer_availability(date, photographer=None):
    """Get photographer availability for a given date
    
    Args:
        date: The date to check
        photographer: Specific photographer to check (optional)
        
    Returns:
        dict: Availability information
    """
    date = getdate(date)
    
    # Default business hours (can be made configurable later)
    business_start = get_time("09:00:00")
    business_end = get_time("18:00:00")
    
    # Get photographers
    if photographer:
        photographers = frappe.get_all(
            "Photographer",
            filters={"name": photographer, "status": "Active"},
            fields=["name", "full_name"]
        )
    else:
        photographers = frappe.get_all(
            "Photographer",
            filters={"status": "Active"},
            fields=["name", "full_name"]
        )
    
    # Get existing bookings for the date
    bookings = frappe.get_all(
        "Booking",
        filters={
            "booking_date": date,
            "status": ["not in", ["Cancelled"]],
            "photographer": ["in", [p.name for p in photographers]] if photographers else ""
        },
        fields=["photographer", "start_time", "end_time"]
    )
    
    # Check photographer availability
    availability = {}
    for p in photographers:
        # Get photographer's bookings
        p_bookings = [b for b in bookings if b.photographer == p.name]
        
        # Check if photographer has any bookings
        if p_bookings:
            # Create time slots
            booked_slots = []
            for booking in p_bookings:
                start_time = get_time(booking.start_time)
                end_time = get_time(booking.end_time) if booking.end_time else add_time(start_time, minutes=60)
                booked_slots.append({
                    "start": start_time,
                    "end": end_time
                })
            
            # Sort booked slots
            booked_slots.sort(key=lambda x: x["start"])
            
            # Find available slots
            available_slots = []
            current_time = business_start
            
            for slot in booked_slots:
                if current_time < slot["start"]:
                    available_slots.append({
                        "start": format_time(current_time),
                        "end": format_time(slot["start"])
                    })
                current_time = slot["end"]
            
            # Add final slot if needed
            if current_time < business_end:
                available_slots.append({
                    "start": format_time(current_time),
                    "end": format_time(business_end)
                })
            
            availability[p.name] = {
                "name": p.name,
                "photographer_name": p.full_name,
                "available": len(available_slots) > 0,
                "available_slots": available_slots,
                "booked_slots": [{
                    "start": format_time(slot["start"]),
                    "end": format_time(slot["end"])
                } for slot in booked_slots]
            }
        else:
            # Photographer is fully available
            availability[p.name] = {
                "name": p.name,
                "photographer_name": p.full_name,
                "available": True,
                "available_slots": [{
                    "start": format_time(business_start),
                    "end": format_time(business_end)
                }],
                "booked_slots": []
            }
    
    return {
        "date": format_date(date),
        "day_of_week": get_arabic_day_name(date.strftime("%A").lower()),
        "business_hours": {
            "start": format_time(business_start),
            "end": format_time(business_end)
        },
        "photographers": availability
    }

def add_time(time, minutes=0, hours=0):
    """Add time to a time object
    
    Args:
        time: Time object
        minutes: Minutes to add
        hours: Hours to add
        
    Returns:
        time: New time object
    """
    import datetime
    
    # Convert to datetime
    dt = datetime.datetime.combine(datetime.date.today(), time)
    
    # Add time
    dt = dt + datetime.timedelta(minutes=minutes, hours=hours)
    
    # Return time
    return dt.time()

def get_arabic_day_name(day_of_week):
    """Get Arabic day name
    
    Args:
        day_of_week: English day name (lowercase)
        
    Returns:
        str: Arabic day name
    """
    day_names = {
        "monday": "الإثنين",
        "tuesday": "الثلاثاء",
        "wednesday": "الأربعاء",
        "thursday": "الخميس",
        "friday": "الجمعة",
        "saturday": "السبت",
        "sunday": "الأحد"
    }
    
    return day_names.get(day_of_week, day_of_week)