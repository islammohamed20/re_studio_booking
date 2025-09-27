import frappe

def test_page_loading():
    """Test loading various pages to check for errors"""
    
    pages_to_test = [
        'packages',
        'services', 
        'dashboard',
        'booking-form',
        'booking-form-public'
    ]
    
    results = {}
    
    for page in pages_to_test:
        try:
            # Try to get the context for each page
            module_path = f"re_studio_booking.www.{page.replace('-', '_')}"
            page_module = frappe.get_module(module_path)
            
            if hasattr(page_module, 'get_context'):
                context = frappe._dict()
                page_module.get_context(context)
                results[page] = {"success": True, "message": "Page loaded successfully"}
                print(f"✅ {page}: OK")
            else:
                results[page] = {"success": False, "message": "No get_context function"}
                print(f"⚠️  {page}: No get_context function")
                
        except Exception as e:
            results[page] = {"success": False, "error": str(e)}
            print(f"❌ {page}: {str(e)}")
    
    success_count = sum(1 for r in results.values() if r.get('success'))
    total_count = len(results)
    
    print(f"\n📊 Results: {success_count}/{total_count} pages loaded successfully")
    
    return {
        "success": success_count == total_count,
        "results": results,
        "summary": f"{success_count}/{total_count} pages working"
    }
