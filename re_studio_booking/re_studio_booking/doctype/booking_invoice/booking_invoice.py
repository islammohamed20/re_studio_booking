# Copyright (c) 2025, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, add_days

class BookingInvoice(Document):
	def validate(self):
		self.calculate_amounts()
		self.set_due_date()
		self.update_payments_aggregation()
		self.update_payment_status()
		
	def calculate_amounts(self):
		"""Compute total_amount from existing value or derive from child rows.

		Current simplified model:
		- No discount / tax fields maintained in this DocType.
		- For Service bookings: if selected_services_table has rows use sum(row.total_amount or row.service_price * qty).
		- For Package bookings: derive sum of (package_price * quantity) from package_services_table.
		- If total_amount already set (e.g. copied from Booking) trust it unless child-row recomputation differs (then overwrite to keep consistency).
		"""
		original_total = flt(self.total_amount)
		computed = 0.0
		if getattr(self, 'booking_type', None) == 'Service':
			for row in (getattr(self, 'selected_services_table', []) or []):
				qty = flt(getattr(row, 'quantity', 1) or 1)
				row_total = flt(getattr(row, 'total_amount', 0))
				if not row_total:
					price = flt(getattr(row, 'service_price', 0) or getattr(row, 'discounted_price', 0))
					row_total = price * qty
				computed += row_total
		elif getattr(self, 'booking_type', None) == 'Package':
			for row in (getattr(self, 'package_services_table', []) or []):
				qty = flt(getattr(row, 'quantity', 1) or 1)
				price = flt(getattr(row, 'package_price', 0) or getattr(row, 'service_price', 0) or getattr(row, 'base_price', 0))
				computed += price * qty
		# If we computed a positive amount and it differs from stored total, update
		if computed > 0 and abs(computed - original_total) > 0.0001:
			self.total_amount = computed
		# Outstanding will be recalculated after payments aggregation; keep provisional here
		self.outstanding_amount = flt(self.total_amount) - flt(self.paid_amount)
		
	def set_due_date(self):
		"""Set due date if not provided"""
		if not self.due_date and self.invoice_date:
			# Default due date: 30 days from invoice date
			self.due_date = add_days(getdate(self.invoice_date), 30)
			
	def update_payment_status(self):
		"""Update payment status derived from aggregated child payments"""
		total_amount = flt(self.total_amount)
		paid_amount = flt(self.paid_amount)
		if total_amount <= 0:
			self.payment_status = "Unpaid"
			return
		if paid_amount <= 0:
			self.payment_status = "Unpaid"
		elif paid_amount >= total_amount:
			self.payment_status = "Paid" if paid_amount == total_amount else "Overpaid"
		else:
			self.payment_status = "Partially Paid"
		# Invoice status mirror
		if self.payment_status == "Paid":
			self.status = "Paid"
		elif self.payment_status == "Partially Paid":
			self.status = "Partially Paid"
		elif self.status not in ["Draft", "Cancelled"] and self.due_date and getdate() > getdate(self.due_date):
			self.status = "Overdue"

	def update_payments_aggregation(self):
		"""Aggregate child payment_table rows to update paid_amount & outstanding_amount"""
		total_payments = 0.0
		for row in (getattr(self, 'payment_table', []) or []):
			amt = flt(getattr(row, 'paid_amount', 0) or 0)
			if amt > 0:
				total_payments += amt
		self.paid_amount = total_payments
		self.outstanding_amount = flt(self.total_amount) - total_payments if flt(self.total_amount) else 0
			
	def before_submit(self):
		"""Validate before submission"""
		if self.status == "Draft":
			self.status = "Submitted"
			
	def on_submit(self):
		"""Actions on submission"""
		self.status = "Submitted"
		
		# Update booking with invoice reference
		if self.booking:
			booking_doc = frappe.get_doc("Booking", self.booking)
			booking_doc.invoice = self.name
			booking_doc.save()
			
		# Set client info from booking if not provided
		if self.booking and not self.client:
			booking_doc = frappe.get_doc("Booking", self.booking)
			self.client = getattr(booking_doc, 'client', None)
			if self.client:
				client_doc = frappe.get_doc("Client", self.client)
				self.customer_name = client_doc.client_name
				self.customer_email = client_doc.email_id
				self.customer_phone = client_doc.mobile_no
			
	def on_cancel(self):
		"""Actions on cancellation"""
		self.status = "Cancelled"
		
		# Remove invoice link from booking
		if self.booking:
			booking_doc = frappe.get_doc("Booking", self.booking)
			booking_doc.invoice = None
			booking_doc.save()
			
	@frappe.whitelist()
	def add_payment(self, amount, payment_method=None, payment_reference=None, payment_date=None, transaction_reference_number=None):
		"""Add payment as a new child row instead of single fields"""
		amount = flt(amount)
		if amount <= 0:
			frappe.throw("مبلغ الدفع يجب أن يكون أكبر من صفر")
		row = self.append('payment_table', {})
		row.paid_amount = amount
		row.payment_method = payment_method
		row.transaction_reference_number = transaction_reference_number or payment_reference
		row.date = payment_date or getdate()
		self.update_payments_aggregation()
		self.update_payment_status()
		self.save()
		return {
			'paid_amount': self.paid_amount,
			'outstanding_amount': self.outstanding_amount,
			'payment_status': self.payment_status
		}
		
	@frappe.whitelist()
	def mark_as_paid(self, payment_method=None, payment_reference=None):
		"""Mark invoice as fully paid by creating payment row for outstanding"""
		outstanding = flt(self.outstanding_amount)
		if outstanding <= 0:
			frappe.throw("الفاتورة مدفوعة بالكامل")
		return self.add_payment(outstanding, payment_method=payment_method, payment_reference=payment_reference)

# -----------------------------
# Module-level wrappers (for direct method path calls from client scripts)
# -----------------------------

@frappe.whitelist()
def add_payment(name: str, amount, payment_method=None, payment_reference=None, payment_date=None, transaction_reference_number=None):
	"""Wrapper to add payment to Booking Invoice via module method path.

	Parameters mirror the class method; 'name' is the invoice docname.
	"""
	doc = frappe.get_doc('Booking Invoice', name)
	return doc.add_payment(amount, payment_method=payment_method, payment_reference=payment_reference, payment_date=payment_date, transaction_reference_number=transaction_reference_number)

@frappe.whitelist()
def mark_as_paid(name: str, payment_method=None, payment_reference=None):
	"""Wrapper to mark invoice as paid (module-level)."""
	doc = frappe.get_doc('Booking Invoice', name)
	return doc.mark_as_paid(payment_method=payment_method, payment_reference=payment_reference)

@frappe.whitelist()
def recalc_invoice_payments(invoice: str):
    """Reaggregate payments for an invoice (utility)"""
    doc = frappe.get_doc('Booking Invoice', invoice)
    doc.update_payments_aggregation()
    doc.update_payment_status()
    doc.save()
    return {
        'paid_amount': doc.paid_amount,
        'outstanding_amount': doc.outstanding_amount,
        'payment_status': doc.payment_status
    }

@frappe.whitelist()
def get_booking_child_rows(booking: str):
	"""Return booking child tables (service items & package services) for population in Booking Invoice.

	Returns structure:
	{
		"services": [ {service, service_name, quantity, service_price, discounted_price, total_amount} ... ],
		"package_services": [ {service, service_name, quantity, base_price, package_price, service_price, amount, photographer_discount_amount} ... ]
	}
	"""
	if not booking:
		frappe.throw("الحجز مطلوب")
	if not frappe.db.exists("Booking", booking):
		frappe.throw("الحجز غير موجود")

	booking_doc = frappe.get_doc("Booking", booking)

	# Permission check: ensure user can read booking
	if not frappe.has_permission("Booking", doc=booking_doc, ptype="read"):
		frappe.throw("ليست لديك صلاحية لعرض هذا الحجز", frappe.PermissionError)

	services = []
	package_services = []

	# Collect service booking items (selected_services_table preferred)
	table_attr_names = ["selected_services_table", "booking_service_items"]
	service_rows = None
	for attr in table_attr_names:
		if hasattr(booking_doc, attr) and getattr(booking_doc, attr):
			service_rows = getattr(booking_doc, attr)
			break
	if service_rows:
		for row in service_rows:
			services.append({
				"service": getattr(row, 'service', None),
				"service_name": getattr(row, 'service_name', None) or getattr(row, 'service', None),
				"quantity": getattr(row, 'quantity', None),
				"service_price": getattr(row, 'service_price', None),
				"discounted_price": getattr(row, 'discounted_price', None),
				"total_amount": getattr(row, 'total_amount', None)
			})

	# Collect package services if booking is a package
	if getattr(booking_doc, 'booking_type', None) == 'Package' and hasattr(booking_doc, 'package_services_table'):
		for row in (booking_doc.package_services_table or []):
			package_services.append({
				"service": getattr(row, 'service', None),
				"service_name": getattr(row, 'service_name', None) or getattr(row, 'service', None),
				"quantity": getattr(row, 'quantity', None),
				"base_price": getattr(row, 'base_price', None),
				"package_price": getattr(row, 'package_price', None),
				"service_price": getattr(row, 'service_price', None),
				"amount": getattr(row, 'amount', None),
				"photographer_discount_amount": getattr(row, 'photographer_discount_amount', None)
			})

	return {
		"services": services,
		"package_services": package_services
	}

@frappe.whitelist()
def create_invoice_from_booking(booking):
	"""Create invoice from booking"""
	booking_doc = frappe.get_doc("Booking", booking)
	
	# Check if invoice already exists
	existing_invoice = frappe.db.exists("Booking Invoice", {"booking": booking})
	if existing_invoice:
		frappe.throw(f"توجد فاتورة مرتبطة بهذا الحجز: {existing_invoice}")
	
	# Determine initial total from booking (prefer already computed booking totals)
	initial_total = 0
	if booking_doc.booking_type == "Service":
		initial_total = flt(getattr(booking_doc, 'total_amount', 0) or 0)
	else:
		initial_total = flt(getattr(booking_doc, 'total_amount_package', 0) or getattr(booking_doc, 'total_amount', 0) or 0)

	# Create invoice record (no base_amount field in current model)
	invoice_doc = frappe.get_doc({
		"doctype": "Booking Invoice",
		"client": getattr(booking_doc, 'client', None),
		"customer_name": booking_doc.customer_name,
		"customer_email": booking_doc.customer_email,
		"customer_phone": booking_doc.customer_phone,
		"booking": booking_doc.name,
		"booking_type": booking_doc.booking_type,
		"service": booking_doc.service,
		"package": booking_doc.package,
		"photographer": booking_doc.photographer,
		"booking_date": booking_doc.booking_date,
		"start_time": booking_doc.start_time,
		"end_time": booking_doc.end_time,
		"total_amount": initial_total,
		"status": "Draft"
	})
	
	invoice_doc.insert()
	return invoice_doc.name

@frappe.whitelist()
def create_invoice_from_quotation(quotation):
	"""Create invoice from accepted quotation"""
	quotation_doc = frappe.get_doc("Booking Quotation", quotation)
	
	if quotation_doc.status != "Accepted":
		frappe.throw("يجب قبول العرض أولاً لإنشاء الفاتورة")
	
	# Check if invoice already exists
	existing_invoice = frappe.db.exists("Booking Invoice", {"quotation": quotation})
	if existing_invoice:
		frappe.throw(f"توجد فاتورة مرتبطة بهذا العرض: {existing_invoice}")
	
	# Create invoice (simplified fields only)
	invoice_doc = frappe.get_doc({
		"doctype": "Booking Invoice",
		"customer": quotation_doc.customer,
		"customer_name": quotation_doc.customer_name,
		"customer_email": quotation_doc.customer_email,
		"customer_phone": quotation_doc.customer_phone,
		"booking": quotation_doc.booking,
		"quotation": quotation_doc.name,
		"booking_type": quotation_doc.booking_type,
		"service": quotation_doc.service,
		"package": quotation_doc.package,
		"photographer": quotation_doc.photographer,
		"booking_date": quotation_doc.booking_date,
		"start_time": quotation_doc.start_time,
		"end_time": quotation_doc.end_time,
		"total_amount": quotation_doc.base_amount,
		"status": "Draft"
	})
	
	invoice_doc.insert()
	return invoice_doc.name

@frappe.whitelist()
def get_invoice_summary():
	"""Get invoice summary for dashboard"""
	summary = frappe.db.sql("""
		SELECT 
			status,
			COUNT(*) as count,
			SUM(total_amount) as total_amount,
			SUM(paid_amount) as paid_amount,
			SUM(outstanding_amount) as outstanding_amount
		FROM `tabBooking Invoice`
		WHERE docstatus != 2
		GROUP BY status
	""", as_dict=True)
	
	return summary