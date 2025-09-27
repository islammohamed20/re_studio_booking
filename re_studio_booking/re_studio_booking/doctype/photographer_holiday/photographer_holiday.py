# Copyright (c) 2023, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class PhotographerHoliday(Document):
	def validate(self):
		self.validate_dates()
		
	def validate_dates(self):
		# Ensure end date is after or equal to start date
		if getdate(self.end_date) < getdate(self.start_date):
			frappe.throw("يجب أن يكون تاريخ الانتهاء بعد أو يساوي تاريخ البدء")
		
		# Check for overlapping holidays for the same photographer
		overlapping = frappe.db.sql("""
			SELECT name FROM `tabPhotographer Holiday`
			WHERE photographer = %s AND name != %s
			AND (
				(start_date BETWEEN %s AND %s) OR
				(end_date BETWEEN %s AND %s) OR
				(%s BETWEEN start_date AND end_date) OR
				(%s BETWEEN start_date AND end_date)
			)
		""", (
			self.photographer, self.name, 
			self.start_date, self.end_date,
			self.start_date, self.end_date,
			self.start_date, self.end_date
		))
		
		if overlapping:
			frappe.throw("هناك إجازة أخرى مسجلة في نفس الفترة لهذا المصور")