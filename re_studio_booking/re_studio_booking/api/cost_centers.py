# -*- coding: utf-8 -*-
# Copyright (c) 2025, MASAR TEAM and contributors
# For license information, please see license.txt

"""
Cost Center API Methods
All methods for managing Cost Centers, Shifts, Transactions, Transfers, and Handovers
"""

import frappe
from frappe import _
from frappe.utils import flt, now_datetime, nowdate
from frappe.model.document import Document


@frappe.whitelist()
def open_shift(cost_center_name, expected_opening_balance=None):
	"""
	Open a new shift for a cost center
	
	Args:
		cost_center_name: Name of the cost center
		expected_opening_balance: Expected opening balance (optional)
	
	Returns:
		shift_name: Name of the created shift
	"""
	# Check permissions
	if not frappe.has_permission("Shift", "create"):
		frappe.throw(_("ليس لديك صلاحية إنشاء وردية"))
	
	# Get cost center
	cost_center = frappe.get_doc("Cost Center", cost_center_name)
	
	# Check if can open shift
	can_open, message = cost_center.can_open_shift()
	if not can_open:
		frappe.throw(_(message))
	
	# Create new shift
	shift = frappe.get_doc({
		"doctype": "Shift",
		"cost_center": cost_center_name,
		"opened_by": frappe.session.user,
		"opened_on": now_datetime(),
		"expected_opening_balance": flt(expected_opening_balance) or flt(cost_center.current_balance),
		"status": "Open"
	})
	
	# Add opening balance transaction if needed
	if flt(expected_opening_balance) > 0:
		shift.append("shift_transactions", {
			"trx_type": "OpeningBalance",
			"payment_method": "Cash",
			"amount": flt(expected_opening_balance),
			"description": "رصيد افتتاحي",
			"created_by": frappe.session.user,
			"created_on": now_datetime()
		})
	
	shift.insert()
	frappe.db.commit()
	
	return shift.name


@frappe.whitelist()
def add_shift_transaction(shift_name, trx_type, payment_method, amount, 
						  reference_doctype=None, reference_name=None, 
						  party=None, description=None):
	"""
	Add a transaction to an open shift
	
	Args:
		shift_name: Name of the shift
		trx_type: Type of transaction (Payment, Refund, Expense, etc.)
		payment_method: Payment method (Cash, Wallet, Bank, Card)
		amount: Transaction amount
		reference_doctype: Reference document type (optional)
		reference_name: Reference document name (optional)
		party: Customer/Party (optional)
		description: Transaction description (optional)
	
	Returns:
		row: The created transaction row
	"""
	# Check permissions
	if not frappe.has_permission("Shift", "write"):
		frappe.throw(_("ليس لديك صلاحية تعديل الوردية"))
	
	# Get shift
	shift = frappe.get_doc("Shift", shift_name)
	
	# Check if can add transaction
	can_add, message = shift.can_add_transaction()
	if not can_add:
		frappe.throw(_(message))
	
	# Add transaction
	row = shift.add_transaction(
		trx_type=trx_type,
		payment_method=payment_method,
		amount=flt(amount),
		reference_doctype=reference_doctype,
		reference_name=reference_name,
		party=party,
		description=description
	)
	
	frappe.db.commit()
	
	return row.as_dict()


@frappe.whitelist()
def close_shift(shift_name, actual_closing_balance, create_journal=True):
	"""
	Close a shift and optionally create journal entry
	
	Args:
		shift_name: Name of the shift
		actual_closing_balance: Actual closing balance counted
		create_journal: Whether to create journal entry (default: True)
	
	Returns:
		dict: {
			"shift_name": shift name,
			"difference": difference between actual and theoretical,
			"journal_entry": journal entry name (if created)
		}
	"""
	# Check permissions
	if not frappe.has_permission("Shift", "write"):
		frappe.throw(_("ليس لديك صلاحية إغلاق الوردية"))
	
	# Get shift
	shift = frappe.get_doc("Shift", shift_name)
	
	# Check if shift is open
	if shift.status != "Open":
		frappe.throw(_("لا يمكن إغلاق وردية بحالة ") + shift.status)
	
	# Set closing data
	shift.actual_closing_balance = flt(actual_closing_balance)
	shift.status = "Closed"
	shift.closed_by = frappe.session.user
	shift.closed_on = now_datetime()
	
	# Save shift (this will trigger validate and calculate difference)
	shift.save()
	
	result = {
		"shift_name": shift.name,
		"difference": flt(shift.difference),
		"theoretical_closing": flt(shift.theoretical_closing_balance),
		"actual_closing": flt(shift.actual_closing_balance)
	}
	
	# Create journal entry if requested
	if create_journal and flt(shift.difference) != 0:
		journal_entry = create_shift_closing_journal(shift)
		if journal_entry:
			result["journal_entry"] = journal_entry.name
	
	frappe.db.commit()
	
	return result


def create_shift_closing_journal(shift):
	"""
	Create journal entry for shift closing difference
	
	Args:
		shift: Shift document
	
	Returns:
		journal_entry: Created journal entry
	"""
	cost_center = frappe.get_doc("Cost Center", shift.cost_center)
	
	if not cost_center.default_account:
		frappe.msgprint(_("لم يتم تحديد حساب محاسبي للخزنة. لن يتم إنشاء قيد محاسبي."))
		return None
	
	difference = flt(shift.difference)
	
	# Determine difference account (Over/Short)
	# You can create a custom account for cash over/short
	difference_account = frappe.db.get_single_value("General Settings", "cash_difference_account")
	if not difference_account:
		difference_account = cost_center.default_account
	
	je = frappe.get_doc({
		"doctype": "Journal Entry",
		"voucher_type": "Journal Entry",
		"posting_date": nowdate(),
		"company": cost_center.company,
		"user_remark": f"فرق إغلاق الوردية {shift.name} - الفرق: {difference}",
		"accounts": []
	})
	
	if difference > 0:
		# Actual is more than theoretical (Cash Over)
		je.append("accounts", {
			"account": cost_center.default_account,
			"debit_in_account_currency": abs(difference)
		})
		je.append("accounts", {
			"account": difference_account,
			"credit_in_account_currency": abs(difference)
		})
	else:
		# Actual is less than theoretical (Cash Short)
		je.append("accounts", {
			"account": difference_account,
			"debit_in_account_currency": abs(difference)
		})
		je.append("accounts", {
			"account": cost_center.default_account,
			"credit_in_account_currency": abs(difference)
		})
	
	je.insert()
	return je


@frappe.whitelist()
def create_cost_center_transfer(from_cost_center, to_cost_center, amount, reference=None):
	"""
	Create a transfer between cost centers
	
	Args:
		from_cost_center: Source cost center
		to_cost_center: Destination cost center
		amount: Transfer amount
		reference: Reference (optional)
	
	Returns:
		transfer_name: Name of the created transfer
	"""
	# Check permissions
	if not frappe.has_permission("Cost Center Transfer", "create"):
		frappe.throw(_("ليس لديك صلاحية إنشاء تحويل"))
	
	# Create transfer
	transfer = frappe.get_doc({
		"doctype": "Cost Center Transfer",
		"from_cost_center": from_cost_center,
		"to_cost_center": to_cost_center,
		"amount": flt(amount),
		"transfer_date": now_datetime(),
		"status": "Draft",
		"reference": reference
	})
	
	transfer.insert()
	frappe.db.commit()
	
	return transfer.name


@frappe.whitelist()
def request_handover(shift_name, to_user, handed_amount, notes=None):
	"""
	Request a shift handover
	
	Args:
		shift_name: Name of the shift
		to_user: User to hand over to
		handed_amount: Amount being handed over
		notes: Handover notes (optional)
	
	Returns:
		handover_doc: Created handover document
	"""
	# Check permissions
	if not frappe.has_permission("Shift Handover", "create"):
		frappe.throw(_("ليس لديك صلاحية طلب تسليم"))
	
	# Get shift
	shift = frappe.get_doc("Shift", shift_name)
	
	# Check if shift is open
	if shift.status != "Open":
		frappe.throw(_("لا يمكن تسليم وردية غير مفتوحة"))
	
	# Create handover
	handover = frappe.get_doc({
		"doctype": "Shift Handover",
		"shift": shift_name,
		"from_user": frappe.session.user,
		"to_user": to_user,
		"handed_amount": flt(handed_amount),
		"handover_on": now_datetime(),
		"notes": notes,
		"accepted": 0
	})
	
	handover.insert()
	frappe.db.commit()
	
	return handover.as_dict()


@frappe.whitelist()
def accept_handover(handover_name):
	"""
	Accept a shift handover
	
	Args:
		handover_name: Name of the handover
	
	Returns:
		success: True if successful
	"""
	# Get handover
	handover = frappe.get_doc("Shift Handover", handover_name)
	
	# Check if current user is the recipient
	if handover.to_user != frappe.session.user:
		frappe.throw(_("فقط المستلم يمكنه قبول التسليم"))
	
	# Check if already accepted
	if handover.accepted:
		frappe.throw(_("تم قبول التسليم بالفعل"))
	
	# Accept handover
	handover.accepted = 1
	handover.accepted_on = now_datetime()
	handover.save()
	
	frappe.db.commit()
	
	return {
		"success": True,
		"message": _("تم قبول التسليم بنجاح")
	}


@frappe.whitelist()
def get_cost_center_balance(cost_center_name):
	"""
	Get current balance of a cost center
	
	Args:
		cost_center_name: Name of the cost center
	
	Returns:
		dict: Balance information
	"""
	cost_center = frappe.get_doc("Cost Center", cost_center_name)
	
	return {
		"cost_center": cost_center_name,
		"current_balance": flt(cost_center.current_balance),
		"total_in": flt(cost_center.total_in),
		"total_out": flt(cost_center.total_out),
		"last_shift": cost_center.last_shift
	}


@frappe.whitelist()
def reconcile_incomplete_shifts():
	"""
	Reconcile incomplete/stale shifts
	This should be run periodically or after server crash
	
	Returns:
		dict: Reconciliation summary
	"""
	# Find shifts open for more than 24 hours
	from datetime import timedelta
	
	stale_threshold = now_datetime() - timedelta(hours=24)
	
	stale_shifts = frappe.get_all(
		"Shift",
		filters={
			"status": "Open",
			"opened_on": ["<", stale_threshold]
		},
		fields=["name", "cost_center", "opened_by", "opened_on"]
	)
	
	reconciled = []
	
	for shift_data in stale_shifts:
		shift = frappe.get_doc("Shift", shift_data.name)
		
		# Mark as cancelled or close automatically
		shift.status = "Cancelled"
		shift.save(ignore_permissions=True)
		
		reconciled.append(shift.name)
	
	frappe.db.commit()
	
	return {
		"reconciled_shifts": reconciled,
		"count": len(reconciled)
	}
