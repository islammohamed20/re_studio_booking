# Copyright (c) 2023, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PhotographerWorkingHours(Document):
	def validate(self):
		self.validate_times()
		
	def validate_times(self):
		# Ensure end time is after start time
		if self.end_time <= self.start_time:
			frappe.throw("يجب أن يكون وقت الانتهاء بعد وقت البدء")