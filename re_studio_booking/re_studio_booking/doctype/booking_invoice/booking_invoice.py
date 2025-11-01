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
		- For Service bookings: if selected_services_table has rows use sum(row.total_amount or row.service_price * unit_qty).
		- For Package bookings: sum of package services + any additional selected services (unit-based).
		- If total_amount already set (e.g. copied from Booking) trust it unless child-row recomputation differs (then overwrite to keep consistency).
		"""
		original_total = flt(self.total_amount)
		computed = 0.0
		if getattr(self, 'booking_type', None) == 'Service':
			def _unit_qty(r):
				unit_type = getattr(r, 'service_unit_type', '') or ''
				duration_unit = getattr(r, 'service_duration_unit', '') or ''
				if unit_type == 'مدة':
					if duration_unit == 'ساعة':
						return flt(getattr(r, 'quantity', 0) or 0)
					elif duration_unit == 'دقيقة':
						return flt(getattr(r, 'min_duration', 0) or 0)
					return 0.0
				return flt(getattr(r, 'mount', 0) or 0)

			for row in (getattr(self, 'selected_services_table', []) or []):
				row_total = flt(getattr(row, 'total_amount', 0))
				if not row_total:
					price = flt(getattr(row, 'discounted_price', 0) or getattr(row, 'service_price', 0))
					row_total = price * _unit_qty(row)
				computed += row_total
		elif getattr(self, 'booking_type', None) == 'Package':
			# 1) إجمالي خدمات الباقة
			for row in (getattr(self, 'package_services_table', []) or []):
				qty = flt(getattr(row, 'quantity', 1) or 1)
				price = flt(getattr(row, 'package_price', 0) or getattr(row, 'service_price', 0) or getattr(row, 'base_price', 0))
				computed += price * qty
			# 2) إضافة الخدمات الفردية المختارة (إن وجدت)
			def _unit_qty_pkg(r):
				unit_type = getattr(r, 'service_unit_type', '') or ''
				duration_unit = getattr(r, 'service_duration_unit', '') or ''
				if unit_type == 'مدة':
					if duration_unit == 'ساعة':
						return flt(getattr(r, 'quantity', 0) or 0)
					elif duration_unit == 'دقيقة':
						return flt(getattr(r, 'min_duration', 0) or 0)
					return 0.0
				return flt(getattr(r, 'mount', 0) or 0)
			for row in (getattr(self, 'selected_services_table', []) or []):
				row_total = flt(getattr(row, 'total_amount', 0))
				if not row_total:
					price = flt(getattr(row, 'discounted_price', 0) or getattr(row, 'service_price', 0))
					row_total = price * _unit_qty_pkg(row)
				computed += row_total
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
	
	def create_journal_entry(self):
		"""إنشاء قيد محاسبي للمبالغ المدفوعة"""
		if not self.company:
			frappe.throw("يجب تحديد الشركة لإنشاء القيد المحاسبي")
		
		if not self.cost_center:
			frappe.throw("يجب تحديد مركز التكلفة لإنشاء القيد المحاسبي")
		
		if not self.debit_to or not self.income_account:
			frappe.throw("يجب تحديد حساب المدين وحساب الإيرادات لإنشاء القيد المحاسبي")
		
		if self.paid_amount <= 0:
			frappe.throw("لا يمكن إنشاء قيد محاسبي بدون مبالغ مدفوعة")
		
		# إنشاء القيد اليومي
		je = frappe.get_doc({
			'doctype': 'Journal Entry',
			'voucher_type': 'Journal Entry',
			'naming_series': 'ACC-JV-.YYYY.-',
			'company': self.company,
			'posting_date': self.invoice_date or today(),
			'user_remark': f'قيد محاسبي للفاتورة {self.name} - العميل: {self.client_name or "غير محدد"}',
			'accounts': [
				{
					# المدين: حساب الخزينة/البنك
					'account': self.debit_to,
					'debit_in_account_currency': self.paid_amount,
					'credit_in_account_currency': 0,
					'cost_center': self.cost_center,
					'reference_type': 'Booking Invoice',
					'reference_name': self.name,
					'user_remark': f'استلام مبلغ من الفاتورة {self.name}'
				},
				{
					# الدائن: حساب الإيرادات
					'account': self.income_account,
					'debit_in_account_currency': 0,
					'credit_in_account_currency': self.paid_amount,
					'cost_center': self.cost_center,
					'reference_type': 'Booking Invoice',
					'reference_name': self.name,
					'user_remark': f'إيرادات من الفاتورة {self.name}'
				}
			]
		})
		
		try:
			je.insert()
			je.submit()
			
			# حفظ رقم القيد في الفاتورة
			self.db_set('journal_entry', je.name)
			
			frappe.msgprint(f"✅ تم إنشاء القيد المحاسبي {je.name} بنجاح", indicator='green')
			return je.name
			
		except Exception as e:
			frappe.log_error(f"خطأ في إنشاء القيد المحاسبي: {str(e)}", "Booking Invoice JE Creation Error")
			frappe.throw(f"حدث خطأ أثناء إنشاء القيد المحاسبي: {str(e)}")
			
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
		
		# إنشاء القيد المحاسبي تلقائياً إذا كانت الإعدادات المحاسبية مفعلة
		if self.paid_amount > 0 and self.cost_center and self.debit_to and self.income_account:
			self.create_journal_entry()
			
	def on_cancel(self):
		"""Actions on cancellation"""
		# إلغاء القيد المحاسبي المرتبط
		if self.journal_entry:
			try:
				je = frappe.get_doc("Journal Entry", self.journal_entry)
				if je.docstatus == 1:  # Submitted
					je.cancel()
					frappe.msgprint(f"تم إلغاء القيد المحاسبي {self.journal_entry}")
			except Exception as e:
				frappe.log_error(f"خطأ في إلغاء القيد المحاسبي: {str(e)}")
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
		self.update_invoice_status()
		self.save()
		return {
			'paid_amount': self.paid_amount,
			'outstanding_amount': self.outstanding_amount,
			'status': self.status
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
    """Reaggregate payments for an invoice (utility) - بدون حفظ لتجنب خطأ التعديل المتزامن"""
    doc = frappe.get_doc('Booking Invoice', invoice)
    doc.update_payments_aggregation()
    doc.update_invoice_status()
    # لا نحفظ هنا - فقط نحسب ونرجع القيم
    # الحفظ سيتم من قبل المستخدم عند الضغط على Save
    return {
        'paid_amount': doc.paid_amount,
        'outstanding_amount': doc.outstanding_amount,
        'status': doc.status
    }

@frappe.whitelist()
def create_journal_entry_for_invoice(invoice: str):
	"""إنشاء قيد محاسبي للفاتورة (يدوياً من الزر)"""
	doc = frappe.get_doc('Booking Invoice', invoice)
	
	if doc.docstatus != 1:
		frappe.throw("يجب اعتماد الفاتورة أولاً لإنشاء القيد المحاسبي")
	
	if doc.journal_entry:
		frappe.throw(f"تم إنشاء قيد محاسبي مسبقاً: {doc.journal_entry}")
	
	return doc.create_journal_entry()

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
		"booking_creation_date": getattr(booking_doc, 'booking_creation_date', None),
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
	
	# نسخ جداول الخدمات من الحجز إلى الفاتورة (قبل insert)
	frappe.logger().info(f"🔍 نوع الحجز: {booking_doc.booking_type}")
	
	if booking_doc.booking_type == "Package":
		# نسخ جدول خدمات الباقة
		if hasattr(booking_doc, 'package_services_table') and booking_doc.package_services_table:
			frappe.logger().info(f"📦 نسخ {len(booking_doc.package_services_table)} خدمة من جدول الباقة")
			for service_row in booking_doc.package_services_table:
				service_name = getattr(service_row, 'service_name', None)
				service_link = getattr(service_row, 'service', None)
				frappe.logger().info(f"   - الخدمة: {service_link} | الاسم: {service_name}")
				
				invoice_doc.append('package_services_table', {
					'service': service_link,
					'service_name': service_name,
					'quantity': getattr(service_row, 'quantity', 0),
					'base_price': getattr(service_row, 'base_price', 0),
					'package_price': getattr(service_row, 'package_price', 0),
					'amount': getattr(service_row, 'amount', 0),
				})
			frappe.logger().info(f"✅ تم إضافة {len(invoice_doc.package_services_table)} صف لجدول الباقة في الفاتورة")
		
		# نسخ جدول الخدمات الإضافية (المختارة) إن وجدت
		frappe.logger().info(f"🔍 فحص selected_services_table في الحجز...")
		frappe.logger().info(f"🔍 hasattr = {hasattr(booking_doc, 'selected_services_table')}")
		if hasattr(booking_doc, 'selected_services_table'):
			frappe.logger().info(f"🔍 الجدول موجود، العدد = {len(booking_doc.selected_services_table) if booking_doc.selected_services_table else 0}")
		
		if hasattr(booking_doc, 'selected_services_table') and booking_doc.selected_services_table:
			frappe.logger().info(f"➕ بدء نسخ {len(booking_doc.selected_services_table)} خدمة إضافية إلى الفاتورة")
			
			# تفعيل علامة وجود خدمات إضافية
			invoice_doc.has_additional_services = 1
			
			for idx, service_row in enumerate(booking_doc.selected_services_table):
				service_link = getattr(service_row, 'service', None)
				mount = getattr(service_row, 'mount', 0)
				service_price = getattr(service_row, 'service_price', 0)
				
				frappe.logger().info(f"   [{idx+1}] الخدمة: {service_link} | الكمية: {mount} | السعر: {service_price}")
				
				invoice_doc.append('selected_services_table', {
					'service': service_link,
					'mount': mount,
					'service_price': service_price,
					'discounted_price': getattr(service_row, 'discounted_price', 0),
					'total_amount': getattr(service_row, 'total_amount', 0),
					'service_unit_type': getattr(service_row, 'service_unit_type', None),
					'service_duration_unit': getattr(service_row, 'service_duration_unit', None),
				})
			
			current_count = len(invoice_doc.selected_services_table) if hasattr(invoice_doc, 'selected_services_table') and invoice_doc.selected_services_table else 0
			frappe.logger().info(f"✅ تم نسخ الخدمات الإضافية - العدد في الفاتورة الآن: {current_count}")
		else:
			frappe.logger().warning("⚠️ لم يتم نسخ الخدمات الإضافية - الجدول فارغ أو غير موجود")
	
	elif booking_doc.booking_type == "Service":
		# نسخ جدول الخدمات المختارة
		if hasattr(booking_doc, 'selected_services_table') and booking_doc.selected_services_table:
			for service_row in booking_doc.selected_services_table:
				invoice_doc.append('selected_services_table', {
					'service': getattr(service_row, 'service', None),
					'mount': getattr(service_row, 'mount', 0),
					'service_price': getattr(service_row, 'service_price', 0),
					'discounted_price': getattr(service_row, 'discounted_price', 0),
					'total_amount': getattr(service_row, 'total_amount', 0),
					'service_unit_type': getattr(service_row, 'service_unit_type', None),
					'service_duration_unit': getattr(service_row, 'service_duration_unit', None),
				})
	
	invoice_doc.insert()
	
	# ملء جدول المدفوعات بناءً على نوع الحجز
	booking_creation_date = getattr(booking_doc, 'booking_creation_date', None) or today()
	
	# الصف الأول دائماً: تاريخ إنشاء الحجز + العربون
	invoice_doc.append('payment_table', {
		'date': booking_creation_date,
		'paid_amount': deposit_amount,
		'payment_method': getattr(booking_doc, 'payment_method', None) or 'Cash',
		'transaction_reference_number': f"عربون حجز {booking_doc.name}" if deposit_amount > 0 else ''
	})
	
	# الصفوف التالية تعتمد على نوع الحجز
	if booking_doc.booking_type == "Service":
		# Service: صف واحد إضافي = تاريخ الحجز
		if getattr(booking_doc, 'booking_date', None):
			invoice_doc.append('payment_table', {
				'date': booking_doc.booking_date,
				'paid_amount': 0,  # يُملأ لاحقاً
			})
	
	elif booking_doc.booking_type == "Package":
		# Package: صفوف من جدول package_booking_dates
		if hasattr(booking_doc, 'package_booking_dates'):
			for date_row in (booking_doc.package_booking_dates or []):
				invoice_doc.append('payment_table', {
					'date': getattr(date_row, 'booking_date', None),
					'paid_amount': 0,  # يُملأ لاحقاً
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