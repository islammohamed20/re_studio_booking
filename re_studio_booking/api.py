import frappe
from frappe import _
from datetime import datetime

@frappe.whitelist()
def create_booking(**kwargs):
    """
    Create a new booking from the multi-step form
    """
    try:
        # Get form data
        date = kwargs.get('date')
        time = kwargs.get('time')
        service_type = kwargs.get('service_type')  # 'service' or 'package'
        service_id = kwargs.get('service_id')
        customer_name = kwargs.get('customer_name')
        customer_phone = kwargs.get('customer_phone')
        customer_email = kwargs.get('customer_email')
        notes = kwargs.get('notes')
        payment_method = kwargs.get('payment_method')
        pay_deposit = kwargs.get('pay_deposit', False)
        
        # Validate required fields
        if not all([date, time, service_type, service_id, customer_name, customer_phone]):
            frappe.throw(_("Missing required fields"))
        
        # Get service/package details
        if service_type == 'service':
            service_doc = frappe.get_doc('Service', service_id)
            service_name = service_doc.service_name
            price = service_doc.price
            duration = service_doc.duration
            deposit_amount = service_doc.deposit_amount if service_doc.deposit_required else 0
        else:
            package_doc = frappe.get_doc('Package', service_id)
            service_name = package_doc.package_name
            price = package_doc.price
            duration = package_doc.duration
            deposit_amount = package_doc.deposit_amount if package_doc.deposit_required else 0
        
        # Check if client exists, if not create one
        client = None
        existing_clients = frappe.get_all('Client', 
            filters={'phone': customer_phone}, 
            fields=['name']
        )
        
        if existing_clients:
            client = existing_clients[0].name
        else:
            # Create new client
            client_doc = frappe.get_doc({
                'doctype': 'Client',
                'client_name': customer_name,
                'phone': customer_phone,
                'email': customer_email or ''
            })
            client_doc.insert()
            client = client_doc.name
        
        # Combine date and time
        booking_datetime = f"{date} {time}:00"
        
        # Calculate amounts
        total_amount = price
        paid_amount = 0
        
        if pay_deposit and deposit_amount > 0:
            paid_amount = deposit_amount
            payment_status = 'Partially Paid'
        else:
            payment_status = 'Pending'
        
        # Create booking
        booking_doc = frappe.get_doc({
            'doctype': 'Booking',
            'client': client,
            'booking_date': booking_datetime,
            'service' if service_type == 'service' else 'package': service_id,
            'total_amount': total_amount,
            'paid_amount': paid_amount,
            'payment_status': payment_status,
            'booking_status': 'Confirmed',
            'notes': notes or '',
            'payment_method': payment_method
        })
        
        booking_doc.insert()
        
        # If deposit is paid, create payment record
        if pay_deposit and deposit_amount > 0:
            payment_doc = frappe.get_doc({
                'doctype': 'Payment',
                'booking': booking_doc.name,
                'client': client,
                'amount': deposit_amount,
                'payment_method': payment_method,
                'payment_type': 'Deposit',
                'payment_date': frappe.utils.now(),
                'status': 'Completed'
            })
            payment_doc.insert()
        
        frappe.db.commit()
        
        return {
            'success': True,
            'booking_id': booking_doc.name,
            'message': _('Booking created successfully')
        }
        
    except Exception as e:
        frappe.log_error(f"Booking creation error: {str(e)}")
        frappe.throw(_("Error creating booking: {0}").format(str(e)))

@frappe.whitelist()
def get_available_time_slots(date, service_id=None, service_type='service'):
    """
    Get available time slots for a specific date
    """
    try:
        from frappe.utils import nowdate, getdate
        
        # If no date provided, use today
        if not date:
            date = nowdate()
            
        # Validate and format date
        try:
            date_obj = getdate(date)
            date_str = date_obj.strftime('%Y-%m-%d')
        except:
            date_str = date  # Use as-is if conversion fails
        
        # Generate all possible time slots (9 AM to 9 PM)
        all_slots = []
        for hour in range(9, 22):  # 9 AM to 9 PM
            all_slots.append(f"{hour:02d}:00")
        
        # Try to get existing bookings for the date
        # Check if Booking doctype exists first
        if not frappe.db.exists("DocType", "Booking"):
            return {
                'success': True,
                'available_slots': all_slots,
                'booked_slots': [],
                'total_slots': len(all_slots)
            }
        
        # Get existing bookings
        existing_bookings = frappe.db.sql("""
            SELECT start_time, end_time, name 
            FROM `tabBooking` 
            WHERE DATE(booking_date) = %s 
            AND status NOT IN ('Cancelled')
        """, (date_str,), as_dict=True)
        
        # Extract booked times
        booked_times = []
        for booking in existing_bookings:
            if booking.start_time:
                # Convert time to string format HH:MM
                if isinstance(booking.start_time, str):
                    time_str = booking.start_time[:5]  # HH:MM format
                else:
                    time_str = booking.start_time.strftime('%H:%M')
                booked_times.append(time_str)
        
        # Remove booked slots
        available_slots = [slot for slot in all_slots if slot not in booked_times]
        
        return {
            'success': True,
            'available_slots': available_slots,
            'booked_slots': booked_times,
            'total_slots': len(all_slots)
        }
        
    except Exception as e:
        # Fallback: return all slots as available
        all_slots = []
        for hour in range(9, 22):
            all_slots.append(f"{hour:02d}:00")
            
        return {
            'success': True,
            'available_slots': all_slots,
            'booked_slots': [],
            'total_slots': len(all_slots),
            'error': str(e)
        }

@frappe.whitelist()
def get_service_details(service_id, service_type='service'):
    """
    Get detailed information about a service or package
    """
    try:
        if service_type == 'service':
            doc = frappe.get_doc('Service', service_id)
            return {
                'name': doc.service_name,
                'description': doc.description,
                'price': doc.price,
                'duration': doc.duration,
                'deposit_required': doc.deposit_required,
                'deposit_amount': doc.deposit_amount if doc.deposit_required else 0
            }
        else:
            doc = frappe.get_doc('Package', service_id)
            return {
                'name': doc.package_name,
                'description': doc.description,
                'price': doc.price,
                'duration': doc.duration,
                'deposit_required': doc.deposit_required,
                'deposit_amount': doc.deposit_amount if doc.deposit_required else 0
            }
            
    except Exception as e:
        frappe.log_error(f"Error getting service details: {str(e)}")
        return {}

@frappe.whitelist()
def get_calendar_availability(start_date, end_date):
    """
    Get calendar availability for date range showing available, booked, and partially booked days
    """
    try:
        from datetime import datetime, timedelta
        from frappe.utils import getdate
        
        # Parse dates
        start = getdate(start_date)
        end = getdate(end_date)
        
        # Initialize calendar data
        calendar_data = {}
        current_date = start
        
        # Generate all dates in range
        while current_date <= end:
            date_str = current_date.strftime('%Y-%m-%d')
            calendar_data[date_str] = {
                'status': 'available',
                'bookings_count': 0,
                'total_slots': 13,  # 9 AM to 9 PM = 13 slots
                'available_slots': 13
            }
            current_date += timedelta(days=1)
        
        # Try to get bookings if Booking doctype exists
        if frappe.db.exists("DocType", "Booking"):
            # Get all bookings in the date range using SQL
            bookings = frappe.db.sql("""
                SELECT DATE(booking_date) as booking_date, status 
                FROM `tabBooking` 
                WHERE DATE(booking_date) BETWEEN %s AND %s 
                AND status NOT IN ('Cancelled')
            """, (start_date, end_date), as_dict=True)
            
            # Process bookings
            for booking in bookings:
                booking_date_str = str(booking.booking_date)
                if booking_date_str in calendar_data:
                    calendar_data[booking_date_str]['bookings_count'] += 1
                    calendar_data[booking_date_str]['available_slots'] -= 1
        
        # Determine status for each day
        for date_str, data in calendar_data.items():
            if data['available_slots'] <= 0:
                data['status'] = 'fully_booked'
            elif data['available_slots'] >= 10:  # Most slots available (10+ out of 13)
                data['status'] = 'available'
            else:
                data['status'] = 'partially_booked'  # Some bookings but still has available slots
        
        return {
            'success': True,
            'calendar_data': calendar_data
        }
        
    except Exception as e:
        # Fallback: return all days as available
        from datetime import datetime, timedelta
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            calendar_data = {}
            current_date = start
            
            while current_date <= end:
                date_str = current_date.strftime('%Y-%m-%d')
                calendar_data[date_str] = {
                    'status': 'available',
                    'bookings_count': 0,
                    'total_slots': 13,
                    'available_slots': 13
                }
                current_date += timedelta(days=1)
                
            return {
                'success': True,
                'calendar_data': calendar_data
            }
        except:
            return {
                'success': False,
                'calendar_data': {},
                'error': str(e)
            }

@frappe.whitelist()
def get_photographer_discounted_hourly_price(photographer: str, service: str):
    """ارجاع سعر الساعة للخدمة قبل وبعد الخصم الخاص بالمصور.
    المدخلات:
      photographer: اسم DocType المصور
      service: اسم DocType الخدمة
    المخرجات (dict):
      {
        base_price: السعر الأساسي للخدمة (سعر الساعة)
        discount_percentage: نسبة خصم المصور العامة
        allowed: هل الخدمة ضمن خدمات المصور المفعلة
        discounted_price: السعر بعد الخصم (يساوي base_price إذا غير مسموح أو الخصم صفر)
      }
    """
    if not photographer or not service:
        frappe.throw(_("Photographer and Service are required"))
    try:
        # Get base price from Service
        base_price = float(frappe.db.get_value("Service", service, "price") or 0)
        # Get photographer discount percentage
        discount_pct = float(frappe.db.get_value("Photographer", photographer, "discount_percentage") or 0)
        # Fetch allowed services for photographer (active only)
        photographer_services = frappe.get_all(
            "Photographer Service",
            filters={"parent": photographer, "is_active": 1},
            fields=["service"],
        )
        allowed_services = {ps.service for ps in photographer_services}
        allowed = service in allowed_services
        applied_pct = discount_pct if (discount_pct > 0 and allowed) else 0
        discounted_price = base_price * (1 - applied_pct/100.0) if applied_pct else base_price
        return {
            "base_price": round(base_price, 2),
            "discount_percentage": discount_pct,
            "allowed": allowed,
            "discounted_price": round(discounted_price, 2),
        }
    except Exception as e:
        frappe.log_error(f"get_photographer_discounted_hourly_price error: {str(e)}")
        return {
            "base_price": 0,
            "discount_percentage": 0,
            "allowed": False,
            "discounted_price": 0,
            "error": str(e),
        }

@frappe.whitelist()
def get_booking_package_hours(booking: str):
    """Return used and remaining hours for a package booking.
    Args:
        booking: Booking name
    Returns: {used_hours, remaining_hours, total_package_hours}
    """
    if not booking:
        frappe.throw(_("Booking is required"))
    try:
        doc = frappe.get_doc('Booking', booking)
        if doc.booking_type != 'Package':
            return {"used_hours": 0, "remaining_hours": 0, "total_package_hours": 0, "message": "Not a package booking"}
        # Ensure recalculation
        doc.compute_package_hours_usage()
        total_pkg = 0.0
        if doc.package:
            total_pkg = float(frappe.db.get_value('Package', doc.package, 'total_hours') or 0)
        return {
            "used_hours": doc.used_hours or 0,
            "remaining_hours": doc.remaining_hours or 0,
            "total_package_hours": total_pkg
        }
    except Exception as e:
        frappe.log_error(f"get_booking_package_hours error: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist()
def debug_booking_deposit(booking: str):
    """Return diagnostic info about deposit calculation for a booking."""
    if not booking:
        frappe.throw(_('Booking required'))
    doc = frappe.get_doc('Booking', booking)
    if doc.booking_type == 'Service':
        basis = float(doc.total_amount or 0)
    else:
        basis = float(doc.total_amount_package or 0)
    pct = float(getattr(doc, 'deposit_percentage', 0) or 0)
    recomputed = round(basis * max(0, min(pct, 100)) / 100.0, 2)
    return {
        'booking': booking,
        'booking_type': doc.booking_type,
        'basis_total': basis,
        'deposit_percentage': pct,
        'stored_deposit_amount': float(doc.deposit_amount or 0),
        'recomputed_deposit': recomputed
    }

@frappe.whitelist(allow_guest=True)
def get_services():
    """Get all active services for booking form"""
    try:
        services = frappe.get_all(
            'Service',
            filters={'is_active': 1},
            fields=['name', 'service_name', 'price', 'duration', 'description'],
            order_by='service_name'
        )
        return {
            'success': True,
            'services': services
        }
    except Exception as e:
        frappe.log_error(f"Error getting services: {str(e)}")
        return {
            'success': False,
            'services': [],
            'error': str(e)
        }

@frappe.whitelist(allow_guest=True)
def get_photographers():
    """Get all active photographers for booking form"""
    try:
        photographers = frappe.get_all(
            'Photographer',
            filters={'is_active': 1},
            fields=['name', 'photographer_name', 'specialization', 'hourly_rate'],
            order_by='photographer_name'
        )
        return {
            'success': True,
            'photographers': photographers
        }
    except Exception as e:
        frappe.log_error(f"Error getting photographers: {str(e)}")
        return {
            'success': False,
            'photographers': [],
            'error': str(e)
        }

@frappe.whitelist(allow_guest=True)
def get_service_packages():
    """Get all active service packages for booking form"""
    try:
        packages = frappe.get_all(
            'Package',
            filters={'is_active': 1},
            fields=['name', 'package_name', 'price', 'total_hours', 'description'],
            order_by='package_name'
        )
        return {
            'success': True,
            'packages': packages
        }
    except Exception as e:
        frappe.log_error(f"Error getting packages: {str(e)}")
        return {
            'success': False,
            'packages': [],
            'error': str(e)
        }

@frappe.whitelist(allow_guest=True)
def get_available_photographers(date=None, service_id=None):
    """Get available photographers for a specific date and service"""
    try:
        # Base query for active photographers
        filters = {'is_active': 1}
        
        # If service is specified, filter by photographers who offer this service
        if service_id:
            photographer_services = frappe.get_all(
                'Photographer Service',
                filters={'service': service_id, 'is_active': 1},
                fields=['parent']
            )
            photographer_names = [ps.parent for ps in photographer_services]
            if photographer_names:
                filters['name'] = ['in', photographer_names]
            else:
                # No photographers offer this service
                return {
                    'success': True,
                    'photographers': []
                }
        
        photographers = frappe.get_all(
            'Photographer',
            filters=filters,
            fields=['name', 'photographer_name', 'specialization', 'hourly_rate'],
            order_by='photographer_name'
        )
        
        # TODO: Add availability check based on date if needed
        # For now, return all photographers that match the service filter
        
        return {
            'success': True,
            'photographers': photographers
        }

@frappe.whitelist(allow_guest=True)
def get_bookings(date=None, photographer=None):
    """Return existing bookings (basic fields) for a given date (and optional photographer) to display on public booking page."""
    try:
        if not date:
            return { 'success': True, 'bookings': [] }
        filters = { 'booking_date': date, 'docstatus': ['!=', 2] }
        if photographer:
            filters['photographer'] = photographer
        rows = frappe.get_all(
            'Booking',
            filters=filters,
            fields=['name','booking_type','service','service_package','start_time','end_time','status','photographer'] ,
            order_by='start_time'
        )
        return { 'success': True, 'bookings': rows }
    except Exception as e:
        frappe.log_error(f"Error getting bookings: {str(e)}")
        return { 'success': False, 'bookings': [], 'error': str(e) }
    except Exception as e:
        frappe.log_error(f"Error getting available photographers: {str(e)}")
        return {
            'success': False,
            'photographers': [],
            'error': str(e)
        }