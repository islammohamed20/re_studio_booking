# Unit Tests for Re Studio Booking

import unittest
import frappe
from frappe.test_runner import make_test_records
from datetime import datetime, timedelta
import json

class TestReStudioBooking(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        cls.create_test_data()
    
    @classmethod
    def create_test_data(cls):
        """Create test records for testing"""
        
        # Create test category
        if not frappe.db.exists("Category", "Portrait"):
            frappe.get_doc({
                "doctype": "Category",
                "category_name_en": "Portrait",
                "category_name_ar": "تصوير شخصي",
                "description": "Portrait photography services",
                "icon": "camera",
                "color": "#3498db",
                "sort_order": 1,
                "is_active": 1
            }).insert()
        
        # Create test service
        if not frappe.db.exists("Service", "Portrait Basic"):
            frappe.get_doc({
                "doctype": "Service",
                "service_name_en": "Portrait Basic",
                "service_name_ar": "تصوير شخصي أساسي",
                "category": "Portrait",
                "description_en": "Basic portrait photography session",
                "price": 150.00,
                "duration": 60,
                "duration_unit": "Minutes",
                "is_active": 1
            }).insert()
        
        # Create test photographer
        if not frappe.db.exists("Photographer", "Ahmed Ali"):
            frappe.get_doc({
                "doctype": "Photographer",
                "first_name": "Ahmed",
                "last_name": "Ali", 
                "full_name": "Ahmed Ali",
                "phone": "966501234567",
                "email": "ahmed@test.com",
                "specialization": "Portrait",
                "years_of_experience": 5,
                "is_active": 1,
                "status": "Active"
            }).insert()
        
        # Create test client
        if not frappe.db.exists("Client", "Mohammed Hassan"):
            frappe.get_doc({
                "doctype": "Client",
                "client_name": "Mohammed Hassan",
                "mobile_no": "966505555555",
                "email_id": "mohammed@test.com"
            }).insert()
    
    def test_booking_creation(self):
        """Test booking creation with valid data"""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        booking_data = {
            "doctype": "Booking",
            "client": "Mohammed Hassan",
            "service": "Portrait Basic",
            "photographer": "Ahmed Ali",
            "booking_date": tomorrow,
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "status": "Pending",
            "total_amount": 150.00
        }
        
        booking_doc = frappe.get_doc(booking_data)
        booking_doc.insert()
        
        self.assertTrue(booking_doc.name)
        self.assertEqual(booking_doc.status, "Pending")
        self.assertEqual(booking_doc.client, "Mohammed Hassan")
        
        # Cleanup
        frappe.delete_doc("Booking", booking_doc.name)
    
    def test_booking_past_date_validation(self):
        """Test that booking cannot be created for past dates"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        booking_data = {
            "doctype": "Booking",
            "client": "Mohammed Hassan",
            "service": "Portrait Basic", 
            "photographer": "Ahmed Ali",
            "booking_date": yesterday,
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "status": "Pending",
            "total_amount": 150.00
        }
        
        booking_doc = frappe.get_doc(booking_data)
        
        with self.assertRaises(frappe.ValidationError):
            booking_doc.insert()
    
    def test_booking_duplicate_time_slot(self):
        """Test that duplicate booking cannot be created for same time slot"""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Create first booking
        booking_data_1 = {
            "doctype": "Booking",
            "client": "Mohammed Hassan",
            "service": "Portrait Basic",
            "photographer": "Ahmed Ali", 
            "booking_date": tomorrow,
            "start_time": "14:00:00",
            "end_time": "15:00:00",
            "status": "Confirmed",
            "total_amount": 150.00
        }
        
        booking_doc_1 = frappe.get_doc(booking_data_1)
        booking_doc_1.insert()
        
        # Try to create overlapping booking
        booking_data_2 = {
            "doctype": "Booking", 
            "client": "Mohammed Hassan",
            "service": "Portrait Basic",
            "photographer": "Ahmed Ali",
            "booking_date": tomorrow,
            "start_time": "14:30:00",
            "end_time": "15:30:00", 
            "status": "Pending",
            "total_amount": 150.00
        }
        
        booking_doc_2 = frappe.get_doc(booking_data_2)
        
        with self.assertRaises(frappe.ValidationError):
            booking_doc_2.insert()
        
        # Cleanup
        frappe.delete_doc("Booking", booking_doc_1.name)
    
    def test_service_creation(self):
        """Test service creation with valid data"""
        service_data = {
            "doctype": "Service",
            "service_name_en": "Wedding Photography",
            "service_name_ar": "تصوير حفلات الزفاف",
            "category": "Portrait",
            "description_en": "Complete wedding photography package",
            "price": 500.00,
            "duration": 480,
            "duration_unit": "Minutes",
            "is_active": 1
        }
        
        service_doc = frappe.get_doc(service_data)
        service_doc.insert()
        
        self.assertTrue(service_doc.name)
        self.assertEqual(service_doc.service_name_en, "Wedding Photography")
        self.assertEqual(service_doc.price, 500.00)
        
        # Cleanup
        frappe.delete_doc("Service", service_doc.name)
    
    def test_photographer_creation(self):
        """Test photographer creation with valid data"""
        photographer_data = {
            "doctype": "Photographer",
            "first_name": "Sarah",
            "last_name": "Ahmed",
            "full_name": "Sarah Ahmed",
            "phone": "966501111111", 
            "email": "sarah@test.com",
            "specialization": "Wedding",
            "years_of_experience": 3,
            "is_active": 1,
            "status": "Active"
        }
        
        photographer_doc = frappe.get_doc(photographer_data)
        photographer_doc.insert()
        
        self.assertTrue(photographer_doc.name)
        self.assertEqual(photographer_doc.full_name, "Sarah Ahmed")
        self.assertEqual(photographer_doc.specialization, "Wedding")
        
        # Cleanup
        frappe.delete_doc("Photographer", photographer_doc.name)
    
    def test_client_creation(self):
        """Test client creation with valid data"""
        client_data = {
            "doctype": "Client",
            "client_name": "Fatima Ali",
            "mobile_no": "966502222222",
            "email_id": "fatima@test.com"
        }
        
        client_doc = frappe.get_doc(client_data)
        client_doc.insert()
        
        self.assertTrue(client_doc.name)
        self.assertEqual(client_doc.client_name, "Fatima Ali")
        self.assertEqual(client_doc.mobile_no, "966502222222")
        
        # Cleanup
        frappe.delete_doc("Client", client_doc.name)
    
    def test_api_create_booking(self):
        """Test API booking creation"""
        from re_studio_booking.re_studio_booking.api import create_booking
        
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        result = create_booking(
            date=tomorrow,
            time="16:00",
            service_type="service",
            service_id="Portrait Basic",
            customer_name="API Test Customer",
            customer_phone="966503333333",
            customer_email="apitest@test.com"
        )
        
        self.assertTrue(result['success'])
        self.assertTrue(result['booking_id'])
        
        # Cleanup
        if result.get('booking_id'):
            frappe.delete_doc("Booking", result['booking_id'])
            # Also cleanup the created client
            clients = frappe.get_all("Client", filters={"mobile_no": "966503333333"})
            for client in clients:
                frappe.delete_doc("Client", client.name)
    
    def test_api_validation_missing_fields(self):
        """Test API validation for missing required fields"""
        from re_studio_booking.re_studio_booking.api import create_booking
        
        with self.assertRaises(frappe.ValidationError):
            create_booking(
                date="",  # Missing required field
                time="16:00",
                service_type="service",
                service_id="Portrait Basic",
                customer_name="API Test Customer",
                customer_phone="966503333333"
            )
    
    def test_dashboard_stats(self):
        """Test dashboard statistics calculation"""
        from re_studio_booking.re_studio_booking.utils.performance import get_dashboard_stats_cached
        
        stats = get_dashboard_stats_cached()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_bookings', stats)
        self.assertIn('pending_bookings', stats)
        self.assertIn('confirmed_bookings', stats)
        self.assertIn('today_bookings', stats)
        self.assertIsInstance(stats['total_bookings'], (int, float))
    
    def test_service_availability(self):
        """Test service availability checking"""
        from re_studio_booking.re_studio_booking.doctype.booking.booking import get_available_time_slots
        
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # This should return available time slots
        slots = get_available_time_slots(
            date=tomorrow,
            service="Portrait Basic",
            photographer="Ahmed Ali"
        )
        
        self.assertIsInstance(slots, list)
        # Should have some available slots
        if slots:
            self.assertIn('time', slots[0])
            self.assertIn('available', slots[0])
    
    def test_performance_cache(self):
        """Test performance caching functionality"""
        from re_studio_booking.re_studio_booking.utils.performance import get_monthly_bookings_chart
        
        # First call should create cache
        chart_data_1 = get_monthly_bookings_chart()
        
        # Second call should use cache
        chart_data_2 = get_monthly_bookings_chart()
        
        self.assertEqual(chart_data_1, chart_data_2)
        self.assertIsInstance(chart_data_1, dict)
        self.assertIn('labels', chart_data_1)
        self.assertIn('datasets', chart_data_1)
    
    def test_security_permissions(self):
        """Test security and permission functions"""
        from re_studio_booking.re_studio_booking.utils.security import validate_user_access
        
        # Test with Administrator (should have access)
        has_access = validate_user_access("Booking", user="Administrator")
        self.assertTrue(has_access)
        
        # Test with non-existent doctype
        has_access = validate_user_access("NonExistentDoctype", user="Administrator")
        self.assertFalse(has_access)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        # Clean up test records
        test_records = [
            ("Category", "Portrait"),
            ("Service", "Portrait Basic"),
            ("Photographer", "Ahmed Ali"),
            ("Client", "Mohammed Hassan")
        ]
        
        for doctype, name in test_records:
            if frappe.db.exists(doctype, name):
                frappe.delete_doc(doctype, name)


class TestBookingValidation(unittest.TestCase):
    """Specific tests for booking validation logic"""
    
    def setUp(self):
        """Set up for each test"""
        self.booking_data = {
            "doctype": "Booking",
            "client": "Mohammed Hassan",
            "service": "Portrait Basic",
            "photographer": "Ahmed Ali"
        }
    
    def test_validate_booking_date_future(self):
        """Test booking date must be in future"""
        future_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        self.booking_data.update({
            "booking_date": future_date,
            "start_time": "10:00:00",
            "end_time": "11:00:00"
        })
        
        booking_doc = frappe.get_doc(self.booking_data)
        # Should not raise exception
        booking_doc.validate_booking_date_enhanced()
    
    def test_validate_booking_minimum_advance(self):
        """Test minimum advance booking time"""
        # Booking for 1 hour from now (should fail if min advance is 24 hours)
        near_future = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d')
        
        self.booking_data.update({
            "booking_date": near_future,
            "start_time": "10:00:00"
        })
        
        booking_doc = frappe.get_doc(self.booking_data)
        
        with self.assertRaises(frappe.ValidationError):
            booking_doc.validate_booking_date_enhanced()


class TestAPIFunctionality(unittest.TestCase):
    """Test API functionality"""
    
    def test_api_error_handling(self):
        """Test API error handling for invalid data"""
        from re_studio_booking.re_studio_booking.api import create_booking
        
        # Test with invalid service type
        with self.assertRaises(frappe.ValidationError):
            create_booking(
                date="2024-12-31",
                time="10:00",
                service_type="invalid_type",  # Should be 'service' or 'package'
                service_id="Portrait Basic",
                customer_name="Test Customer",
                customer_phone="966501234567"
            )
    
    def test_api_permission_check(self):
        """Test API permission checking"""
        # This would require setting up test user with limited permissions
        # For now, just verify the function exists and can be called
        from re_studio_booking.re_studio_booking.utils.security import has_app_permission
        
        # Should work for Administrator
        result = has_app_permission()
        self.assertIsInstance(result, bool)


def run_tests():
    """Run all tests and return results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestReStudioBooking))
    suite.addTests(loader.loadTestsFromTestCase(TestBookingValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIFunctionality))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return {
        'tests_run': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100 if result.testsRun > 0 else 0
    }

if __name__ == '__main__':
    # Create test environment
    frappe.init()
    frappe.connect()
    
    # Run tests
    results = run_tests()
    
    print(f"\n{'='*50}")
    print(f"TEST RESULTS:")
    print(f"Tests Run: {results['tests_run']}")
    print(f"Failures: {results['failures']}")  
    print(f"Errors: {results['errors']}")
    print(f"Success Rate: {results['success_rate']:.2f}%")
    print(f"{'='*50}")
    
    frappe.destroy()
