# Copyright (c) 2023, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, format_date, format_time

class Service(Document):
	def validate(self):
		self.validate_price()
		self.validate_duration()
	
	def validate_price(self):
		# Ensure price is positive
		if self.price <= 0:
			frappe.throw("يجب أن يكون سعر الخدمة أكبر من صفر")
			
	def validate_duration(self):
		# Ensure duration is positive
		if self.duration <= 0:
			frappe.throw("يجب أن تكون مدة الخدمة أكبر من صفر")
			
	def on_update(self):
		# Update linked photographers if needed
		if self.has_value_changed("is_active") and not self.is_active:
			# If service is deactivated, update any linked photographers
			self.update_linked_photographers()
			
	def update_linked_photographers(self):
		# Update any photographers linked to this service
		linked_photographers = frappe.get_all(
			"Photographer Service",
			filters={"service": self.name},
			fields=["parent"]
		)
		
		for photographer in linked_photographers:
			frappe.db.set_value(
				"Photographer Service",
				{"parent": photographer.parent, "service": self.name},
				"is_active", 0
			)

@frappe.whitelist()
def get_booking_stats(service):
	"""Get booking statistics for a service"""
	# Get total bookings count
	total_bookings = frappe.db.count("Booking", {"service": service})
	
	# Get completed bookings count
	completed_bookings = frappe.db.count("Booking", {"service": service, "status": "Completed"})
	
	# Get upcoming bookings count
	today = nowdate()
	upcoming_bookings = frappe.db.count(
		"Booking", 
		{
			"service": service, 
			"booking_date": [">", today],
			"status": ["in", ["Confirmed", "Pending"]]
		}
	)
	
	# Get list of upcoming bookings
	upcoming_list = frappe.get_all(
		"Booking",
		filters={
			"service": service,
			"booking_date": [">", today],
			"status": ["in", ["Confirmed", "Pending"]]
		},
		fields=[
			"name", "booking_date", "booking_time", "photographer", 
			"customer_name", "status"
		],
		order_by="booking_date asc, booking_time asc",
		limit=10
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