"""
Test script for Admin Dashboard APIs
Run this in Frappe console to test all dashboard functions
"""

import frappe
from re_studio_booking.re_studio_booking.page.admin_dashboard.admin_dashboard import *

def test_admin_dashboard_apis():
    """Test all admin dashboard APIs"""
    
    print("🔍 Testing Admin Dashboard APIs...")
    print("=" * 50)
    
    try:
        # Test 1: Dashboard Data
        print("1️⃣ Testing get_admin_dashboard_data()...")
        dashboard_data = get_admin_dashboard_data()
        print(f"   ✅ Quick Stats: {dashboard_data['quick_stats']}")
        print(f"   ✅ Monthly Bookings: {len(dashboard_data['monthly_bookings'])} months")
        print(f"   ✅ Recent Activities: {len(dashboard_data['recent_activities'])} items")
        print(f"   ✅ Popular Services: {len(dashboard_data['service_popularity'])} services")
        print(f"   ✅ Photographers: {len(dashboard_data['photographer_performance'])} photographers")
        
        # Test 2: Booking Management Data
        print("\n2️⃣ Testing get_booking_management_data()...")
        booking_data = get_booking_management_data(page=1, page_size=5)
        print(f"   ✅ Bookings: {len(booking_data['bookings'])} items")
        print(f"   ✅ Total Count: {booking_data['total_count']}")
        print(f"   ✅ Pages: {booking_data['total_pages']}")
        
        # Test 3: Quick Stats Details
        print("\n3️⃣ Testing individual stat functions...")
        total = get_total_bookings()
        pending = get_pending_bookings()
        confirmed = get_confirmed_bookings()
        today = get_today_bookings()
        print(f"   ✅ Total Bookings: {total}")
        print(f"   ✅ Pending Bookings: {pending}")
        print(f"   ✅ Confirmed Bookings: {confirmed}")
        print(f"   ✅ Today's Bookings: {today}")
        
        # Test 4: Chart Data
        print("\n4️⃣ Testing chart data functions...")
        monthly = get_monthly_bookings_chart()
        services = get_service_popularity()
        photographers = get_photographer_performance()
        print(f"   ✅ Monthly Chart: {len(monthly)} data points")
        print(f"   ✅ Service Popularity: {len(services)} services")
        print(f"   ✅ Photographer Performance: {len(photographers)} photographers")
        
        # Test 5: Additional Data
        print("\n5️⃣ Testing additional functions...")
        revenue = get_revenue_overview()
        weekly = get_weekly_bookings_comparison()
        print(f"   ✅ Revenue Overview: Current month {revenue['current_month']}")
        print(f"   ✅ Weekly Comparison: Current {sum(weekly['current_week'])}, Last {sum(weekly['last_week'])}")
        
        # Test 6: Recent Activities
        print("\n6️⃣ Testing recent activities...")
        activities = get_recent_activities()
        print(f"   ✅ Recent Activities: {len(activities)} items")
        if activities:
            print(f"   📋 Sample: {activities[0]['customer_name']} - {activities[0]['service']}")
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")
        print("✅ Admin Dashboard APIs are working correctly")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        print("📋 Full error details:")
        import traceback
        traceback.print_exc()

def create_sample_data():
    """Create sample data for testing (optional)"""
    
    print("📝 Creating sample data for testing...")
    
    try:
        # Check if we have basic data
        bookings_count = frappe.db.count('Booking')
        services_count = frappe.db.count('Service')
        photographers_count = frappe.db.count('Photographer')
        
        print(f"📊 Current data:")
        print(f"   - Bookings: {bookings_count}")
        print(f"   - Services: {services_count}")
        print(f"   - Photographers: {photographers_count}")
        
        if bookings_count == 0:
            print("⚠️  No bookings found. Consider creating some sample bookings for better testing.")
        
        if services_count == 0:
            print("⚠️  No services found. Consider creating some services for better testing.")
            
        if photographers_count == 0:
            print("⚠️  No photographers found. Consider creating some photographers for better testing.")
            
    except Exception as e:
        print(f"❌ Error checking sample data: {str(e)}")

def test_dashboard_performance():
    """Test performance of dashboard APIs"""
    
    import time
    print("⚡ Testing Dashboard Performance...")
    print("=" * 40)
    
    # Test dashboard data loading time
    start_time = time.time()
    dashboard_data = get_admin_dashboard_data()
    end_time = time.time()
    
    load_time = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
    
    print(f"📊 Dashboard Data Load Time: {load_time}ms")
    
    if load_time < 1000:  # Less than 1 second
        print("✅ Excellent performance!")
    elif load_time < 3000:  # Less than 3 seconds
        print("⚠️  Good performance, but could be optimized")
    else:
        print("❌ Slow performance, optimization needed")
    
    # Test booking management data loading time
    start_time = time.time()
    booking_data = get_booking_management_data(page=1, page_size=20)
    end_time = time.time()
    
    booking_load_time = round((end_time - start_time) * 1000, 2)
    print(f"📅 Booking Management Load Time: {booking_load_time}ms")
    
    if booking_load_time < 500:
        print("✅ Excellent booking query performance!")
    elif booking_load_time < 1500:
        print("⚠️  Good booking query performance")
    else:
        print("❌ Slow booking queries, consider indexing")

def run_all_tests():
    """Run all dashboard tests"""
    
    print("🚀 Starting Admin Dashboard Tests")
    print("=" * 60)
    
    # Basic API tests
    test_admin_dashboard_apis()
    
    print("\n")
    
    # Performance tests
    test_dashboard_performance()
    
    print("\n")
    
    # Sample data check
    create_sample_data()
    
    print("\n" + "=" * 60)
    print("🏁 All tests completed!")
    print("📱 You can now access the admin dashboard at: /app/admin-dashboard")

# Run tests if executed directly
if __name__ == "__main__":
    run_all_tests()
