import frappe

# Manual style test (run with: bench execute re_studio_booking.test_get_photographer_discounted_hourly_price.run )

def run():
    photographer = frappe.db.get_value("Photographer", {}, "name") if frappe.db.exists("Photographer", {}) else None
    service = frappe.db.get_value("Service", {}, "name") if frappe.db.exists("Service", {}) else None
    if not photographer or not service:
        print("Missing Photographer or Service records to test.")
        return
    from re_studio_booking.api import get_photographer_discounted_hourly_price
    result = get_photographer_discounted_hourly_price(photographer, service)
    print("Result:", result)
