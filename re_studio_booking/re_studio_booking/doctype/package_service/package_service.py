# Copyright (c) 2023, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PackageService(Document):
	def validate(self):
		self.update_service_details()
		
	def update_service_details(self):
		"""Fetch and update service details"""
		if self.service:
			service_doc = frappe.get_doc("Service", self.service)
			self.service_name = service_doc.service_name_ar
			self.service_price = service_doc.price
			self.amount = service_doc.price * self.quantity

@frappe.whitelist()
def get_service_details(service):
	"""Get service details for client-side use"""
	if not service:
		return {}
		
	service_doc = frappe.get_doc("Service", service)
	return {
		"service_name": service_doc.service_name_ar,
		"price": service_doc.price
	}