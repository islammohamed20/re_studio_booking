import frappe

def create_all_photographer_doctypes():
    """Create all photographer-related DocTypes"""
    
    print("🔧 Creating Photographer-related DocTypes...")
    print("=" * 50)
    
    try:
        # Import and run all creation functions
        from re_studio_booking.create_photographer_availability import create_photographer_availability_doctype
        from re_studio_booking.create_photographer_leave import create_photographer_leave_doctype  
        from re_studio_booking.create_photographer_schedule import create_photographer_schedule_doctype
        
        results = []
        
        # Create Photographer Availability
        result1 = create_photographer_availability_doctype()
        results.append(result1)
        
        # Create Photographer Leave
        result2 = create_photographer_leave_doctype()
        results.append(result2)
        
        # Create Photographer Schedule
        result3 = create_photographer_schedule_doctype()
        results.append(result3)
        
        # Count successful creations
        successful = sum(1 for r in results if r.get('success'))
        total = len(results)
        
        print("=" * 50)
        print(f"📊 Summary: {successful}/{total} DocTypes created successfully")
        
        if successful == total:
            print("🎉 All photographer DocTypes created successfully!")
        else:
            print("⚠️  Some DocTypes had issues, check logs for details")
        
        return {
            "success": successful == total,
            "results": results,
            "summary": f"{successful}/{total} DocTypes created"
        }
        
    except Exception as e:
        print(f"❌ Error in create_all_photographer_doctypes: {e}")
        frappe.log_error(f"Photographer DocTypes creation error: {str(e)}")
        return {"success": False, "error": str(e)}
