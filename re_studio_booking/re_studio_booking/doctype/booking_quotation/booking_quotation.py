# Copyright (c) 2025, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, add_days

class BookingQuotation(Document):
	def validate(self):
		self.calculate_amounts()
		self.set_valid_till()
	
	def after_insert(self):
		"""تحديث حالة Lead بعد إنشاء عرض السعر"""
		self.update_lead_status("Quotation")
		
	def calculate_amounts(self):
		"""Calculate discount, tax and total amounts"""
		base_amount = flt(self.base_amount)
		discount_percentage = flt(self.discount_percentage)
		tax_percentage = flt(self.tax_percentage)
		
		# Calculate discount amount
		self.discount_amount = base_amount * discount_percentage / 100
		
		# Calculate amount after discount
		amount_after_discount = base_amount - flt(self.discount_amount)
		
		# Calculate tax amount
		self.tax_amount = amount_after_discount * tax_percentage / 100
		
		# Calculate total amount
		self.total_amount = amount_after_discount + flt(self.tax_amount)
		
	def set_valid_till(self):
		"""Set valid till date if not provided"""
		if not self.valid_till and self.quotation_date:
			# Default validity: 30 days from quotation date
			self.valid_till = add_days(getdate(self.quotation_date), 30)
			
	def before_submit(self):
		"""Validate before submission"""
		if self.status == "Draft":
			self.status = "Sent"
			
	def on_submit(self):
		"""Actions on submission"""
		self.status = "Sent"
		
	def accept_quotation(self):
		"""Accept the quotation"""
		self.status = "Accepted"
		self.save()
		
		# Update booking with quotation reference
		if self.booking:
			booking_doc = frappe.get_doc("Booking", self.booking)
			booking_doc.quotation = self.name
			booking_doc.save()
			
		# Set client info from booking if not provided
		if self.booking and not self.client:
			booking_doc = frappe.get_doc("Booking", self.booking)
			self.client = getattr(booking_doc, 'client', None)
			if self.client:
				client_doc = frappe.get_doc("Client", self.client)
				self.customer_name = client_doc.client_name
				self.customer_email = client_doc.email_id
				self.customer_phone = client_doc.mobile_no
			
	def reject_quotation(self):
		"""Reject the quotation"""
		self.status = "Rejected"
		self.save()
	
	def update_lead_status(self, status):
		"""تحديث حالة Lead"""
		if self.quotation_to == "Lead" and self.lead:
			frappe.db.set_value("Lead", self.lead, "status", status)
			frappe.db.commit()
		
	@frappe.whitelist()
	def create_booking(self):
		"""Create booking from quotation"""
		if self.status != "Accepted":
			frappe.throw("يجب قبول العرض أولاً لإنشاء الحجز")
			
		if self.booking:
			frappe.throw("تم إنشاء حجز مرتبط بهذا العرض مسبقاً")
			
		# Create new booking
		booking_doc = frappe.get_doc({
			"doctype": "Booking",
			"customer": self.customer,
			"customer_name": self.customer_name,
			"customer_email": self.customer_email,
			"customer_phone": self.customer_phone,
			"booking_type": self.booking_type,
			"service": self.service,
			"package": self.package,
			"photographer": self.photographer,
			"booking_date": self.booking_date,
			"start_time": self.start_time,
			"end_time": self.end_time,
			"status": "Confirmed",
			"notes": f"تم إنشاؤه من العرض: {self.name}"
		})
		
		booking_doc.insert()
		
		# Link booking to quotation
		self.booking = booking_doc.name
		self.save()
		
		return booking_doc.name

@frappe.whitelist()
def get_service_price(service):
	"""Get service price for quotation"""
	if not service:
		return 0
		
	service_doc = frappe.get_doc("Service", service)
	return service_doc.price or 0

@frappe.whitelist()
def get_package_price(package):
	"""Get package price for quotation"""
	if not package:
		return 0
		
	package_doc = frappe.get_doc("Service Package", package)
	return package_doc.total_price or 0

@frappe.whitelist()
def create_quotation_from_booking(booking):
	"""Create quotation from booking"""
	booking_doc = frappe.get_doc("Booking", booking)
	
	# Check if quotation already exists
	existing_quotation = frappe.db.exists("Booking Quotation", {"booking": booking})
	if existing_quotation:
		frappe.throw(f"يوجد عرض مرتبط بهذا الحجز: {existing_quotation}")
	
	# Get base amount based on booking type
	base_amount = 0
	if booking_doc.booking_type == "Service" and booking_doc.service:
		service_doc = frappe.get_doc("Service", booking_doc.service)
		base_amount = service_doc.price or 0
	elif booking_doc.booking_type == "Package" and booking_doc.package:
		package_doc = frappe.get_doc("Service Package", booking_doc.package)
		base_amount = package_doc.total_price or 0
	
	# Create quotation
	quotation_doc = frappe.get_doc({
		"doctype": "Booking Quotation",
		"client": booking_doc.client,
		"customer_name": booking_doc.customer_name,
		"customer_email": booking_doc.customer_email,
		"customer_phone": booking_doc.customer_phone,
		"booking": booking_doc.name,
		"booking_type": booking_doc.booking_type,
		"service": booking_doc.service,
		"package": booking_doc.package,
		"photographer": booking_doc.photographer,
		"booking_date": booking_doc.booking_date,
		"start_time": booking_doc.start_time,
		"end_time": booking_doc.end_time,
		"base_amount": base_amount,
		"status": "Draft"
	})
	
	quotation_doc.insert()
	return quotation_doc.name

@frappe.whitelist()
def get_quotation_summary():
	"""Get quotation summary for dashboard"""
	summary = frappe.db.sql("""
		SELECT 
			status,
			COUNT(*) as count,
			SUM(total_amount) as total_amount
		FROM `tabBooking Quotation`
		WHERE docstatus != 2
		GROUP BY status
	""", as_dict=True)
	
	return summary