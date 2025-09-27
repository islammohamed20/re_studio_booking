import frappe
from re_studio_booking.re_studio_booking.doctype.booking.booking import get_available_time_slots

def test_api():
    try:
        result = get_available_time_slots('2025-08-05')
        frappe.log("API Test Result: {} slots available".format(len(result)))
        print("✅ API test successful. Available slots:", len(result))
        return {"success": True, "slots": len(result), "message": "API working correctly"}
    except Exception as e:
        frappe.log_error("API Test Error: {}".format(str(e)))
        print("❌ API test failed:", str(e))
        return {"success": False, "error": str(e)}
