# -*- coding: utf-8 -*-
# Copyright (c) 2025, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class ShiftHandover(Document):
	def validate(self):
		"""Validate handover before saving"""
		if not self.handover_on:
			self.handover_on = now_datetime()
		
		# Validate shift status
		shift = frappe.get_doc("Shift", self.shift)
		if shift.status == "Closed":
			frappe.throw("لا يمكن تسليم وردية مغلقة")
		
		# Validate from_user is shift opener
		if shift.opened_by != self.from_user:
			frappe.throw("المسلم يجب أن يكون من فتح الوردية")
	
	def on_update(self):
		"""Update shift status when accepted"""
		if self.accepted and self.has_value_changed("accepted"):
			if not self.accepted_on:
				self.accepted_on = now_datetime()
			self.update_shift_status()
	
	def update_shift_status(self):
		"""Mark shift as Handed Over"""
		shift = frappe.get_doc("Shift", self.shift)
		shift.status = "Handed Over"
		shift.save(ignore_permissions=True)
