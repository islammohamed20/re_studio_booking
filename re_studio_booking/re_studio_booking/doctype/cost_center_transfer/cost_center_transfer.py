# -*- coding: utf-8 -*-
# Copyright (c) 2025, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, now_datetime

class CostCenterTransfer(Document):
	def validate(self):
		"""Validate transfer before saving"""
		self.validate_different_cost_centers()
		self.validate_sufficient_balance()
		
		if not self.transfer_date:
			self.transfer_date = now_datetime()
	
	def validate_different_cost_centers(self):
		"""Ensure from and to are different"""
		if self.from_cost_center == self.to_cost_center:
			frappe.throw("لا يمكن التحويل من وإلى نفس الخزنة")
	
	def validate_sufficient_balance(self):
		"""Check if from_cost_center has sufficient balance"""
		if self.status == "Completed":
			from_cc = frappe.get_doc("Cost Center", self.from_cost_center)
			if flt(from_cc.current_balance) < flt(self.amount):
				frappe.throw(f"رصيد الخزنة {self.from_cost_center} غير كافٍ للتحويل")
	
	def on_submit(self):
		"""Mark as completed and create journal entry"""
		self.status = "Completed"
		self.create_journal_entry()
	
	def create_journal_entry(self):
		"""Create journal entry for the transfer"""
		from_cc = frappe.get_doc("Cost Center", self.from_cost_center)
		to_cc = frappe.get_doc("Cost Center", self.to_cost_center)
		
		if not from_cc.default_account or not to_cc.default_account:
			frappe.msgprint("لم يتم تحديد حسابات محاسبية للخزن. لن يتم إنشاء قيد محاسبي.")
			return
		
		je = frappe.get_doc({
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"posting_date": self.transfer_date,
			"company": from_cc.company,
			"user_remark": f"تحويل من {self.from_cost_center} إلى {self.to_cost_center} - {self.name}",
			"accounts": [
				{
					"account": from_cc.default_account,
					"credit_in_account_currency": flt(self.amount)
				},
				{
					"account": to_cc.default_account,
					"debit_in_account_currency": flt(self.amount)
				}
			]
		})
		
		je.insert()
		self.journal_entry = je.name
		self.save()
