# -*- coding: utf-8 -*-
# Copyright (c) 2025, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, now_datetime, get_datetime
from frappe import _

class Shift(Document):
	def before_insert(self):
		"""Set default values before inserting"""
		if not self.opened_on:
			self.opened_on = now_datetime()
		if not self.opened_by:
			self.opened_by = frappe.session.user
	
	def validate(self):
		"""Validate shift before saving"""
		self.validate_single_open_shift()
		self.calculate_totals()
		self.calculate_theoretical_closing()
		self.calculate_difference()
		self.validate_closing()
	
	def validate_single_open_shift(self):
		"""Ensure only one open shift per cost center"""
		if self.status == "Open" and not self.is_new():
			existing = frappe.db.exists("Shift", {
				"cost_center": self.cost_center,
				"status": "Open",
				"name": ["!=", self.name]
			})
			if existing:
				frappe.throw(_("يوجد وردية مفتوحة بالفعل لهذه الخزنة"))
	
	def calculate_totals(self):
		"""Calculate transaction totals"""
		self.total_payments = 0
		self.total_refunds = 0
		self.total_expenses = 0
		self.total_deposits = 0
		self.total_withdrawals = 0
		
		for trx in self.shift_transactions:
			amount = flt(trx.amount)
			
			if trx.trx_type == "Payment":
				self.total_payments += amount
			elif trx.trx_type == "Refund":
				self.total_refunds += amount
			elif trx.trx_type == "Expense":
				self.total_expenses += amount
			elif trx.trx_type == "Deposit":
				self.total_deposits += amount
			elif trx.trx_type == "Withdrawal":
				self.total_withdrawals += amount
		
		# Calculate net total (in minus out)
		total_in = self.total_payments + self.total_deposits
		total_out = self.total_refunds + self.total_expenses + self.total_withdrawals
		self.net_total = flt(total_in - total_out)
	
	def calculate_theoretical_closing(self):
		"""Calculate theoretical closing balance"""
		opening = flt(self.expected_opening_balance)
		net = flt(self.net_total)
		self.theoretical_closing_balance = flt(opening + net)
	
	def calculate_difference(self):
		"""Calculate difference between actual and theoretical"""
		if self.status in ["Closed", "Handed Over"]:
			actual = flt(self.actual_closing_balance)
			theoretical = flt(self.theoretical_closing_balance)
			self.difference = flt(actual - theoretical)
	
	def validate_closing(self):
		"""Validate shift closing"""
		if self.status in ["Closed", "Handed Over"]:
			# Ensure actual closing balance is entered
			if self.actual_closing_balance is None:
				frappe.throw(_("يجب إدخال الرصيد الختامي الفعلي قبل إغلاق الوردية"))
			
			# Ensure closed_by and closed_on are set
			if not self.closed_by:
				self.closed_by = frappe.session.user
			if not self.closed_on:
				self.closed_on = now_datetime()
	
	def on_update(self):
		"""Update cost center balance after closing"""
		if self.status == "Closed" and self.has_value_changed("status"):
			self.update_cost_center_balance()
	
	def update_cost_center_balance(self):
		"""Update cost center current balance"""
		cost_center = frappe.get_doc("Cost Center", self.cost_center)
		cost_center.current_balance = flt(self.actual_closing_balance)
		cost_center.last_shift = self.name
		cost_center.save(ignore_permissions=True)
	
	def can_add_transaction(self):
		"""Check if transactions can be added"""
		if self.status != "Open":
			return False, f"لا يمكن إضافة معاملات لوردية بحالة {self.status}"
		return True, "OK"
	
	def add_transaction(self, trx_type, payment_method, amount, **kwargs):
		"""Add a transaction to the shift"""
		can_add, message = self.can_add_transaction()
		if not can_add:
			frappe.throw(_(message))
		
		row = self.append("shift_transactions", {
			"trx_type": trx_type,
			"payment_method": payment_method,
			"amount": amount,
			"reference_doctype": kwargs.get("reference_doctype"),
			"reference_name": kwargs.get("reference_name"),
			"party": kwargs.get("party"),
			"description": kwargs.get("description"),
			"created_by": frappe.session.user,
			"created_on": now_datetime()
		})
		
		self.save()
		return row
