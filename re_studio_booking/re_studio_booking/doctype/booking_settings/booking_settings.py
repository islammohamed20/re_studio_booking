import frappe

# Compatibility shim for legacy calls to Booking Settings
# Delegates to General Settings fields and defaults

@frappe.whitelist()
def get_working_days():
    """Return working days list as lowercase day names (sunday..saturday).
    Mirrors legacy booking_settings.get_working_days expected by JS.
    """
    try:
        # Prefer General Settings, fall back to defaults
        working_days = []
        if frappe.db.exists('DocType', 'General Settings'):
            settings = frappe.get_single('General Settings')
            # General Settings JSON uses day flags: saturday..friday (1/0)
            day_flags = {
                'sunday': getattr(settings, 'sunday', 1),
                'monday': getattr(settings, 'monday', 1),
                'tuesday': getattr(settings, 'tuesday', 1),
                'wednesday': getattr(settings, 'wednesday', 1),
                'thursday': getattr(settings, 'thursday', 1),
                'friday': getattr(settings, 'friday', 0),
                'saturday': getattr(settings, 'saturday', 1),
            }
            for day, flag in day_flags.items():
                if flag:
                    working_days.append(day)
        else:
            working_days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'saturday']
        # Ensure non-empty list with sensible defaults
        if not working_days:
            working_days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'saturday']
        return working_days
    except Exception as e:
        frappe.logger().error(f"Booking Settings shim get_working_days error: {str(e)}")
        return ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'saturday']

@frappe.whitelist()
def get_business_hours():
    """Return business hours dict with keys start_time and end_time.
    Mirrors legacy booking_settings.get_business_hours expected by JS.
    """
    try:
        start_time = '09:00:00'
        end_time = '18:00:00'
        if frappe.db.exists('DocType', 'General Settings'):
            settings = frappe.get_single('General Settings')
            # In General Settings these are business_start_time / business_end_time
            start_time = getattr(settings, 'business_start_time', None) or start_time
            end_time = getattr(settings, 'business_end_time', None) or end_time
        return {
            'start_time': start_time,
            'end_time': end_time,
        }
    except Exception as e:
        frappe.logger().error(f"Booking Settings shim get_business_hours error: {str(e)}")
        return {
            'start_time': '09:00:00',
            'end_time': '18:00:00',
        }