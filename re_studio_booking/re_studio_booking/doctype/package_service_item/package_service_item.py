# Copyright (c) 2025, Re Studio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class PackageServiceItem(Document):
	def validate(self):
		"""Validate service item data"""
		self.calculate_total_amount()
		self.fetch_service_details()

	def calculate_total_amount(self):
		"""Calculate total amount based on package price and quantity"""
		self.total_amount = flt(self.package_price) * flt(self.quantity or 1)

	def fetch_service_details(self):
		"""Fetch service details when service is selected"""
		if self.service and not self.service_name:
			service_doc = frappe.get_doc("Service", self.service)
			self.service_name = service_doc.service_name_en
			if not self.base_price:
				self.base_price = service_doc.price
			if not self.package_price:
				self.package_price = service_doc.price