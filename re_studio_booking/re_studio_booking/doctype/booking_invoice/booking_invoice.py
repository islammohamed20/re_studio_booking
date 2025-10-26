# Copyright (c) 2025, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, add_days, today

class BookingInvoice(Document):
	def validate(self):
		self.calculate_amounts()
		self.set_due_date()
		self.update_payments_aggregation()
		self.update_invoice_status()
		
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

	def update_payments_aggregation(self):
		"""Aggregate child payment_table rows to update paid_amount & outstanding_amount"""
		total_payments = 0.0
		for row in (getattr(self, 'payment_table', []) or []):
			amt = flt(getattr(row, 'paid_amount', 0) or 0)
			if amt > 0:
				total_payments += amt
		self.paid_amount = total_payments
		self.outstanding_amount = flt(self.total_amount) - total_payments if flt(self.total_amount) else 0
	
	def update_invoice_status(self):
		"""تحديث حالة الفاتورة بناءً على حالة الدفع وآخر تاريخ دفع"""
		from frappe.utils import getdate, nowdate
		
		total_amount = flt(self.total_amount)
		paid_amount = flt(self.paid_amount)
		
		# لا نغير الحالة إذا كانت Cancelled أو Draft (للفواتير الجديدة)
		if self.status == "Cancelled":
			return
		
		# السماح بتحديث Draft إلى حالة أخرى فقط إذا كان هناك دفعات
		if self.status == "Draft" and paid_amount <= 0:
			return
		
		# إذا لم يوجد مبلغ إجمالي
		if total_amount <= 0:
			return
		
		# إذا تم الدفع بالكامل
		if paid_amount >= total_amount:
			self.status = "Paid"
			return
		
		# إذا تم دفع جزء من المبلغ
		if paid_amount > 0 and paid_amount < total_amount:
			# التحقق من آخر تاريخ دفع
			last_payment_date = self._get_last_payment_date()
			
			if last_payment_date:
				today = getdate(nowdate())
				days_since_last_payment = (today - getdate(last_payment_date)).days
				
				# إذا مر أكثر من يوم على آخر دفعة
				if days_since_last_payment > 1:
					self.status = "Overdue"
				else:
					self.status = "Partially Paid"
			else:
				self.status = "Partially Paid"
			return
		
		# إذا لم يتم الدفع أبداً
		# التحقق من تاريخ الاستحقاق
		if self.due_date and getdate(nowdate()) > getdate(self.due_date):
			self.status = "Overdue"
	
	def _get_last_payment_date(self):
		"""الحصول على آخر تاريخ دفع من جدول المدفوعات"""
		payment_dates = []
		for row in (getattr(self, 'payment_table', []) or []):
			if getattr(row, 'date', None) and flt(getattr(row, 'paid_amount', 0)) > 0:
				payment_dates.append(row.date)
		
		if payment_dates:
			return max(payment_dates)
		return None
			
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
				self.client_name = client_doc.client_name
				self.customer_email = client_doc.email_id
				self.phone = client_doc.mobile_no
			
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
    doc.update_invoice_status()
    doc.save()
    return {
        'paid_amount': doc.paid_amount,
        'outstanding_amount': doc.outstanding_amount,
        'status': doc.status
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
	
	# جلب تواريخ الحجز للباقات
	package_dates = []
	if getattr(booking_doc, 'booking_type', None) == 'Package' and hasattr(booking_doc, 'package_booking_dates'):
		for row in (booking_doc.package_booking_dates or []):
			package_dates.append({
				"booking_date": getattr(row, 'booking_date', None),
				"start_time": getattr(row, 'start_time', None),
				"end_time": getattr(row, 'end_time', None),
				"hours": getattr(row, 'hours', None)
			})

	return {
		"services": services,
		"package_services": package_services,
		"package_dates": package_dates
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

	# Get deposit amount from booking to initialize paid_amount
	deposit_amount = flt(getattr(booking_doc, 'deposit_amount', 0) or 0)
	outstanding = initial_total - deposit_amount if initial_total > 0 else 0

	# Create invoice record (no base_amount field in current model)
	invoice_doc = frappe.get_doc({
		"doctype": "Booking Invoice",
		"client": getattr(booking_doc, 'client', None),
		"client_name": getattr(booking_doc, 'client_name', None),
		"customer_email": getattr(booking_doc, 'client_email', None),  # Booking uses client_email
		"phone": getattr(booking_doc, 'phone', None),
		"mobile_no": getattr(booking_doc, 'mobile_no', None),
		"booking": booking_doc.name,
		"booking_type": getattr(booking_doc, 'booking_type', None),
		"service": getattr(booking_doc, 'service', None),
		"package": getattr(booking_doc, 'package', None),
		"photographer": getattr(booking_doc, 'photographer', None),
		"booking_date": getattr(booking_doc, 'booking_date', None),
		"start_time": getattr(booking_doc, 'start_time', None),
		"end_time": getattr(booking_doc, 'end_time', None),
		"total_amount": initial_total,
		"paid_amount": deposit_amount,
		"outstanding_amount": outstanding,
		"status": "Draft"
	})
	
	invoice_doc.insert()
	
	# إضافة مبلغ العربون كأول دفعة في جدول المدفوعات إذا كان موجوداً
	if deposit_amount > 0:
		invoice_doc.append('payment_table', {
			'paid_amount': deposit_amount,
			'payment_method': getattr(booking_doc, 'payment_method', None) or 'Cash',
			'date': getattr(booking_doc, 'booking_date', None) or today(),
			'transaction_reference_number': f"عربون حجز {booking_doc.name}"
		})
		invoice_doc.save()
	
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
		"client": getattr(quotation_doc, 'client', None),
		"client_name": getattr(quotation_doc, 'customer_name', None),
		"customer_email": getattr(quotation_doc, 'customer_email', None),
		"phone": getattr(quotation_doc, 'customer_phone', None),
		"booking": getattr(quotation_doc, 'booking', None),
		"quotation": quotation_doc.name,
		"booking_type": getattr(quotation_doc, 'booking_type', None),
		"service": getattr(quotation_doc, 'service', None),
		"package": getattr(quotation_doc, 'package', None),
		"photographer": getattr(quotation_doc, 'photographer', None),
		"booking_date": getattr(quotation_doc, 'booking_date', None),
		"start_time": getattr(quotation_doc, 'start_time', None),
		"end_time": getattr(quotation_doc, 'end_time', None),
		"total_amount": getattr(quotation_doc, 'base_amount', 0),
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