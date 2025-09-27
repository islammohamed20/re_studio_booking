# Copyright (c) 2023, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate, format_date, format_time

class ServicePackage(Document):
	def validate(self):
		self.calculate_total_price()
		self.validate_discount()
		self.calculate_final_price()
		
	def calculate_total_price(self):
		"""Calculate the total price based on included services"""
		total = 0
		for service in self.package_services:
			service_doc = frappe.get_doc("Service", service.service)
			service_price = service_doc.price * service.quantity
			service.amount = service_price
			total += service_price
		
		self.total_price = total
		
	def validate_discount(self):
		"""Ensure discount percentage is between 0 and 100"""
		if self.discount_percentage is None:
			self.discount_percentage = 0
		
		if self.discount_percentage < 0 or self.discount_percentage > 100:
			frappe.throw("نسبة الخصم يجب أن تكون بين 0 و 100")
		
	def calculate_final_price(self):
		"""Calculate final price after applying discount"""
		if not self.total_price:
			self.calculate_total_price()
			
		discount_amount = flt(self.total_price) * flt(self.discount_percentage) / 100
		self.final_price = flt(self.total_price) - discount_amount
		
	def on_update(self):
		"""Update all linked bookings if package is deactivated"""
		if not self.is_active:
			# Find all bookings with this package that are not completed or cancelled
			bookings = frappe.get_all(
				"Booking",
				filters={
					"package": self.name,
					"status": ["not in", ["Completed", "Cancelled"]]
				},
				fields=["name"]
			)
			
			for booking in bookings:
				frappe.msgprint(f"تم تعطيل الباقة المرتبطة بالحجز {booking.name}")

@frappe.whitelist()
def get_booking_stats(package):
	"""Get booking statistics for a service package
	
	Args:
		package: The name of the service package
	
	Returns:
		dict: A dictionary containing booking statistics
	"""
	if not package:
		return {}
	
	# Get total bookings count
	total_bookings = frappe.db.count("Booking", {"package": package})
	
	# Get completed bookings count
	completed_bookings = frappe.db.count("Booking", {"package": package, "status": "Completed"})
	
	# Get upcoming bookings count (confirmed bookings with future dates)
	today = nowdate()
	upcoming_filters = {
		"package": package,
		"status": ["in", ["Confirmed", "Pending"]],
		"booking_date": [">=", today]
	}
	upcoming_bookings = frappe.db.count("Booking", upcoming_filters)
	
	# Get list of upcoming bookings for display
	upcoming_list = frappe.get_all(
		"Booking",
		filters=upcoming_filters,
		fields=[
			"name", "booking_date", "booking_time", "photographer", 
			"photographer_name", "customer_name", "status"
		],
		order_by="booking_date asc, booking_time asc",
		limit=5
	)
	
	# Format dates and times for display
	for booking in upcoming_list:
		booking.booking_date = format_date(booking.booking_date)
		booking.booking_time = format_time(booking.booking_time)
	
	return {
		"total_bookings": total_bookings,
		"completed_bookings": completed_bookings,
		"upcoming_bookings": upcoming_bookings,
		"upcoming_list": upcoming_list
	}