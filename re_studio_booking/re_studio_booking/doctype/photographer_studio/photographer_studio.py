# Copyright (c) 2025, Masar Digital Group and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PhotographerStudio(Document):
	"""DocType for Photographer Studio"""
	
	def validate(self):
		"""Validate studio settings before saving"""
		self.validate_business_hours()
		self.validate_logo()
	
	def validate_business_hours(self):
		"""Validate business hours"""
		if self.business_hours_start and self.business_hours_end:
			if self.business_hours_start >= self.business_hours_end:
				frappe.throw("Business start time must be before end time")
	
	def validate_logo(self):
		"""Validate studio logo"""
		if self.studio_logo:
			# Check if file exists and is an image
			if not frappe.db.exists("File", {"file_url": self.studio_logo}):
				frappe.throw("Invalid logo file selected")
			
			# Get file extension to ensure it's an image
			import os
			file_extension = os.path.splitext(self.studio_logo)[1].lower()
			allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
			
			if file_extension not in allowed_extensions:
				frappe.throw(f"Logo must be an image file. Allowed formats: {', '.join(allowed_extensions)}")
