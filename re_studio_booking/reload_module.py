import frappe
import importlib
import sys

def reload_module():
    """Reload the photographer module"""
    try:
        # Clear the cache for the module
        module_path = "re_studio_booking.re_studio_booking.doctype.photographer.photographer"
        if module_path in sys.modules:
            del sys.modules[module_path]
        
        # Reload the module
        import re_studio_booking.re_studio_booking.doctype.photographer.photographer as phot_mod
        importlib.reload(phot_mod)
        
        # Check if get_booking_stats exists
        if hasattr(phot_mod, "get_booking_stats"):
            print("✅ get_booking_stats function exists in the module")
        else:
            print("❌ get_booking_stats function does NOT exist in the module")
        
        return "Module reloaded successfully"
    except Exception as e:
        return f"Error reloading module: {str(e)}"

if __name__ == "__main__":
    print(reload_module())
