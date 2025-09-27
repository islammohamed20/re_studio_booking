# Copyright (c) 2023, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Category(Document):
	def validate(self):
		# Ensure category has a valid icon
		if not self.icon:
			self.icon = "camera"
			
	def on_trash(self):
		# Check if category is being used by any services
		services = frappe.get_all("Service", filters={"category": self.name})
		if services:
			frappe.throw("لا يمكن حذف هذه الفئة لأنها مستخدمة في خدمات موجودة")