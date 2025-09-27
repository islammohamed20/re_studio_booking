import frappe

def test_specific_pages():
    """Test specific pages that were fixed"""
    
    pages_to_test = [
        ('packages', 're_studio_booking.www.packages'),
        ('services', 're_studio_booking.www.services'), 
        ('dashboard', 're_studio_booking.www.dashboard')
    ]
    
    results = {}
    
    for page_name, module_path in pages_to_test:
        try:
            page_module = frappe.get_module(module_path)
            
            if hasattr(page_module, 'get_context'):
                context = frappe._dict()
                page_module.get_context(context)
                results[page_name] = {"success": True, "message": "Page loaded successfully"}
                print(f"✅ {page_name}: OK")
            else:
                results[page_name] = {"success": False, "message": "No get_context function"}
                print(f"⚠️  {page_name}: No get_context function")
                
        except Exception as e:
            results[page_name] = {"success": False, "error": str(e)}
            print(f"❌ {page_name}: {str(e)}")
    
    success_count = sum(1 for r in results.values() if r.get('success'))
    total_count = len(results)
    
    print(f"\n📊 Results: {success_count}/{total_count} pages loaded successfully")
    
    if success_count == total_count:
        print("🎉 All pages are working correctly!")
    
    return {
        "success": success_count == total_count,
        "results": results,
        "summary": f"{success_count}/{total_count} pages working"
    }
