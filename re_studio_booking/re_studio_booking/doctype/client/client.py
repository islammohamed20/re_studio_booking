# Copyright (c) 2025, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import validate_email_address
from frappe import _

class Client(Document):
	def validate(self):
		self.validate_email()
		self.validate_mobile_no()
		self.set_full_name()
		
	def validate_email(self):
		"""Validate email address format"""
		if self.email_id:
			if not validate_email_address(self.email_id):
				frappe.throw(_("عنوان البريد الإلكتروني غير صحيح"))
				
			# Check for duplicate email
			existing_client = frappe.db.exists("Client", {
				"email_id": self.email_id,
				"name": ["!=", self.name]
			})
			if existing_client:
				frappe.throw(_("يوجد عميل آخر بنفس البريد الإلكتروني: {0}").format(existing_client))
				
	def validate_mobile_no(self):
		"""Validate mobile number"""
		if self.mobile_no:
			# Check for duplicate mobile number
			existing_client = frappe.db.exists("Client", {
				"mobile_no": self.mobile_no,
				"name": ["!=", self.name]
			})
			if existing_client:
				frappe.throw(_("يوجد عميل آخر بنفس رقم الجوال: {0}").format(existing_client))
				
	def set_full_name(self):
		"""Set full name for display"""
		if not hasattr(self, 'full_name'):
			self.full_name = self.client_name
			
	def before_save(self):
		"""Actions before saving"""
		# Clean up phone numbers
		if self.mobile_no:
			self.mobile_no = self.mobile_no.strip()
		if self.phone:
			self.phone = self.phone.strip()
			
		# Clean up email
		if self.email_id:
			self.email_id = self.email_id.strip().lower()
			
	def get_full_address(self):
		"""Get formatted full address"""
		address_parts = []
		
		if self.address_line1:
			address_parts.append(self.address_line1)
		if self.address_line2:
			address_parts.append(self.address_line2)
		if self.city:
			address_parts.append(self.city)
		if self.state:
			address_parts.append(self.state)
		if self.country:
			address_parts.append(self.country)
		if self.pincode:
			address_parts.append(self.pincode)
			
		return ", ".join(address_parts)
		
	@frappe.whitelist()
	def get_contact_info(self):
		"""Get client contact information"""
		return {
			"name": self.client_name,
			"email": self.email_id,
			"mobile": self.mobile_no,
			"phone": self.phone,
			"address": self.get_full_address()
		}

@frappe.whitelist()
def get_client_list(filters=None, limit=20):
	"""Get list of clients with optional filters"""
	filters = filters or {}
	
	# Add default filter for active clients
	if "status" not in filters:
		filters["status"] = "Active"
		
	clients = frappe.get_all("Client", 
		filters=filters,
		fields=["name", "client_name", "email_id", "mobile_no", "client_type", "status"],
		order_by="client_name asc",
		limit=limit
	)
	
	return clients

@frappe.whitelist()
def search_clients(query, limit=10):
	"""Search clients by name, email or mobile"""
	if not query:
		return []
		
	query = f"%{query}%"
	
	clients = frappe.db.sql("""
		SELECT name, client_name, email_id, mobile_no
		FROM `tabClient`
		WHERE status = 'Active'
			AND (client_name LIKE %(query)s 
				OR email_id LIKE %(query)s 
				OR mobile_no LIKE %(query)s)
		ORDER BY client_name
		LIMIT %(limit)s
	""", {
		"query": query,
		"limit": limit
	}, as_dict=True)
	
	return clients

@frappe.whitelist()
def create_client_from_booking_data(client_name, email_id=None, mobile_no=None):
	"""Create a new client from booking data"""
	if not client_name:
		frappe.throw(_("اسم العميل مطلوب"))
		
	# Check if client already exists
	existing_client = None
	if email_id:
		existing_client = frappe.db.exists("Client", {"email_id": email_id})
	if not existing_client and mobile_no:
		existing_client = frappe.db.exists("Client", {"mobile_no": mobile_no})
		
	if existing_client:
		return existing_client
		
	# Create new client
	client_doc = frappe.get_doc({
		"doctype": "Client",
		"client_name": client_name,
		"email_id": email_id,
		"mobile_no": mobile_no,
		"status": "Active"
	})
	
	client_doc.insert()
	return client_doc.name

@frappe.whitelist()
def get_client_bookings(client):
	"""Get all bookings for a client"""
	bookings = frappe.get_all("Booking",
		filters={"client": client},
		fields=["name", "booking_date", "start_time", "end_time", "service", "status"],
		order_by="booking_date desc"
	)
	
	return bookings

@frappe.whitelist()
def get_client_summary():
	"""Get client summary for dashboard"""
	summary = frappe.db.sql("""
		SELECT 
			status,
			client_type,
			COUNT(*) as count
		FROM `tabClient`
		GROUP BY status, client_type
		ORDER BY status, client_type
	""", as_dict=True)
	
	return summary