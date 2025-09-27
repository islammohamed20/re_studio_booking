# Copyright (c) 2023, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PhotographerService(Document):
	def validate(self):
		self.update_service_details()
		self.calculate_discounted_price()
	
	def update_service_details(self):
		"""Update service details from the linked service"""
		if self.service:
			service_doc = frappe.get_doc("Service", self.service)
			self.service_name = service_doc.service_name_ar
			
			# Set base price from service price automatically
			self.base_price = service_doc.price
	
	def calculate_discounted_price(self):
		"""Calculate discounted price based on photographer's discount percentage"""
		if self.base_price and self.parent:
			# Get photographer document
			photographer_doc = frappe.get_doc("Photographer", self.parent)
			
			# Apply discount if photographer has B2B enabled and discount percentage
			if photographer_doc.b2b and photographer_doc.discount_percentage:
				discount_amount = self.base_price * (photographer_doc.discount_percentage / 100)
				self.discounted_price = self.base_price - discount_amount
			else:
				self.discounted_price = self.base_price

@frappe.whitelist()
def get_service_details(service):
	"""Get service details for client-side use"""
	if not service:
		return {}
		
	service_doc = frappe.get_doc("Service", service)
	return {
		"service_name": service_doc.service_name_ar,
		"base_price": service_doc.price
	}

@frappe.whitelist()
def calculate_discount(base_price, photographer_name):
	"""Calculate discounted price for client-side use"""
	if not base_price or not photographer_name:
		return base_price
		
	try:
		photographer_doc = frappe.get_doc("Photographer", photographer_name)
		base_price = float(base_price)
		
		# Apply discount if photographer has B2B enabled and discount percentage
		if photographer_doc.b2b and photographer_doc.discount_percentage:
			discount_amount = base_price * (photographer_doc.discount_percentage / 100)
			return base_price - discount_amount
		else:
			return base_price
	except:
		return base_price