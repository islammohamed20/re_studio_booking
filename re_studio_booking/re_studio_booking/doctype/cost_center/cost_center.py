# -*- coding: utf-8 -*-
# Copyright (c) 2025, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, nowdate, now_datetime

class CostCenter(Document):
	def validate(self):
		"""Validate Cost Center before saving"""
		self.validate_default_account()
		self.calculate_balances()
	
	def validate_default_account(self):
		"""Ensure default account is valid"""
		if self.default_account:
			account = frappe.get_doc("Account", self.default_account)
			# Some installations may use a simplified Account DocType without 'is_group'
			is_group = getattr(account, "is_group", 0)
			if is_group:
				frappe.throw(f"الحساب المحاسبي {self.default_account} هو حساب مجموعة ولا يمكن استخدامه")
	
	def calculate_balances(self):
		"""Calculate current balances from all shifts"""
		# Get all closed shifts
		shifts = frappe.get_all(
			"Shift",
			filters={
				"cost_center": self.name,
				"status": ["in", ["Closed", "Handed Over"]]
			},
			fields=["name", "actual_closing_balance"]
		)
		
		if shifts:
			# Get the last shift
			last_shift = frappe.get_doc("Shift", shifts[-1].name)
			self.current_balance = flt(last_shift.actual_closing_balance)
			self.last_shift = last_shift.name
		
		# Calculate total in/out from all shift transactions
		total_in = frappe.db.sql("""
			SELECT SUM(st.amount)
			FROM `tabShift Transaction` st
			INNER JOIN `tabShift` s ON s.name = st.parent
			WHERE s.cost_center = %s
			AND st.trx_type IN ('Payment', 'Deposit', 'OpeningBalance')
		""", (self.name,))[0][0] or 0
		
		total_out = frappe.db.sql("""
			SELECT SUM(st.amount)
			FROM `tabShift Transaction` st
			INNER JOIN `tabShift` s ON s.name = st.parent
			WHERE s.cost_center = %s
			AND st.trx_type IN ('Refund', 'Expense', 'Withdrawal')
		""", (self.name,))[0][0] or 0
		
		self.total_in = flt(total_in)
		self.total_out = flt(total_out)
	
	def get_open_shift(self):
		"""Get currently open shift for this cost center"""
		open_shifts = frappe.get_all(
			"Shift",
			filters={
				"cost_center": self.name,
				"status": "Open"
			},
			limit=1
		)
		
		if open_shifts:
			return frappe.get_doc("Shift", open_shifts[0].name)
		return None
	
	def can_open_shift(self, user=None):
		"""Check if user can open a shift for this cost center"""
		if not user:
			user = frappe.session.user
		
		# Check if cost center is active
		if not self.is_active:
			return False, "الخزنة غير نشطة"
		
		# Check if there's already an open shift
		if self.get_open_shift():
			return False, "يوجد وردية مفتوحة بالفعل لهذه الخزنة"
		
		# Check user permission
		if self.user_account and self.user_account != user:
			if not frappe.has_permission("Shift", "create", user=user):
				return False, "ليس لديك صلاحية فتح وردية لهذه الخزنة"
		
		return True, "OK"
