import frappe

def test_photographer_name():
    try:
        # Test basic query
        photographers = frappe.get_all('Photographer', 
                                     fields=['name', 'photographer_name'], 
                                     limit=2)
        
        print(f"✅ SUCCESS: Found {len(photographers)} photographers with photographer_name field")
        for p in photographers:
            print(f"  - Name: {p.name}")
            print(f"    photographer_name: {p.photographer_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

# Execute the test
if test_photographer_name():
    print("\n🎉 photographer_name field is working correctly!")
else:
    print("\n💥 photographer_name field has issues")
