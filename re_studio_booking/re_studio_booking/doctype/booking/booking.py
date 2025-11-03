# Copyright (c) 2023, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime, timedelta
from frappe.utils import flt
import json

# استيراد دوال المساعدة من booking_utils
from .booking_utils import (
	validate_paid_amount
)

# استيراد دوال التحقق من booking_validations
from .booking_validations import (
	validate_dates,
	validate_availability,
	validate_studio_working_day,
	check_deletion_permission,
	validate_package_hours
)

# استيراد دوال الحسابات من booking_calculations
from .booking_calculations import (
	calculate_deposit_amount,
	set_default_deposit_percentage,
	calculate_booking_datetime,
	calculate_time_usage,
	compute_package_hours_usage,
	calculate_service_totals as calculate_service_totals_logic,
	calculate_package_totals as calculate_package_totals_logic,
	recompute_pricing,
	calculate_booking_total
)

class Booking(Document):
	# ------------------------ Core Lifecycle ------------------------ #
	def before_save(self):
		"""تنفيذ العمليات قبل الحفظ"""
		if not self.current_employee:
			self.current_employee = frappe.session.user

		if self.status != 'Confirmed':
			self.status = 'Confirmed'

		validate_studio_working_day(self)
		calculate_deposit_amount(self)
		self._validate_cashback_usage()

	def after_insert(self):
		"""بعد إنشاء الحجز: معالجة الكاش باك وتحويل Lead"""
		# تحويل Lead إلى Client إذا كان الحجز من Lead
		self.convert_lead_to_client()
		# خصم الكاش باك المستخدم
		deduct_cashback_from_client(self)
		# إضافة نقاط جديدة من الباقة
		add_cashback_to_client(self)
	
	def convert_lead_to_client(self):
		"""تحويل Lead إلى Client عند إنشاء Booking"""
		if self.party_type == "Lead" and self.party_name:
			try:
				# استيراد دالة التحويل من lead.py
				from re_studio_booking.re_studio_booking.doctype.lead.lead import convert_to_client
				
				# تحويل Lead إلى Client
				client_name = convert_to_client(self.party_name)
				
				# تحديث الحجز بـ Client الجديد
				self.db_set("client", client_name, update_modified=False)
				self.db_set("party_type", "Client", update_modified=False)
				self.db_set("party_name", client_name, update_modified=False)
				
				# جلب معلومات Client
				client_doc = frappe.get_doc("Client", client_name)
				self.db_set("client_name", client_doc.client_name, update_modified=False)
				
				frappe.msgprint(_("تم تحويل العميل المحتمل إلى عميل بنجاح: {0}").format(client_name))
			except Exception as e:
				frappe.log_error(f"خطأ في تحويل Lead إلى Client: {str(e)}")


	def _validate_cashback_usage(self):
		"""التحقق من صحة استخدام الكاش باك"""
		if not self.cashback_used or flt(self.cashback_used) == 0:
			return
		
		if not self.client:
			frappe.throw(_("يجب تحديد العميل لاستخدام نقاط الكاش باك"))
		
		# جلب رصيد العميل
		client = frappe.get_doc("Client", self.client)
		available_cashback = flt(client.cashback_balance or 0)
		
		# التحقق من كفاية الرصيد
		if flt(self.cashback_used) > available_cashback:
			frappe.throw(_("رصيد الكاش باك غير كافي. الرصيد المتاح: {0}").format(available_cashback))
		
		# التحقق من عدم تجاوز قيمة الحجز
		total = flt(self.total_amount or 0)
		if flt(self.cashback_used) > total:
			frappe.throw(_("لا يمكن استخدام كاش باك أكثر من قيمة الحجز"))

	def validate(self):
		"""Validate booking data and calculate totals"""
		if not self.flags.get('ignore_version'):
			self.flags.ignore_version = True

		validate_dates(self)
		validate_availability(self)
		calculate_booking_datetime(self)
		calculate_time_usage(self)

		if self.booking_type == 'Package':
			compute_package_hours_usage(self)
			validate_package_hours(self)

		if self.booking_type == 'Service':
			self._deduplicate_selected_services()
		elif self.booking_type == 'Package':
			self._deduplicate_package_services()

		set_default_deposit_percentage(self)
		recompute_pricing(self)
		calculate_booking_total(self)
		calculate_deposit_amount(self)
		validate_paid_amount(self)

	def on_trash(self):
		"""منع حذف الحجز إذا كان مدفوعاً بالكامل (ما عدا Administrator)"""
		check_deletion_permission(self)

	def before_cancel(self):
		"""منع إلغاء الحجز إذا كان مدفوعاً بالكامل (ما عدا Administrator)"""
		check_deletion_permission(self)

	def on_update(self):
		"""إرسال تأكيد الحجز بعد التحويل إلى Confirmed مرة واحدة"""
		if getattr(self, 'status', None) == 'Confirmed' and not getattr(self, 'confirmation_sent', False):
			self.send_confirmation()
			self.confirmation_sent = 1

	def send_confirmation(self):
		"""إرسال بريد تأكيد الحجز للعميل"""
		if not getattr(self, 'client', None):
			return
		client_email = frappe.db.get_value("Client", self.client, "email_id")
		if not client_email:
			return
		
		# التحقق من وجود حساب بريد صادر قبل الإرسال
		try:
			frappe.sendmail(
				recipients=[client_email],
				subject=_("تأكيد الحجز - {0}").format(self.name),
				message=(
					"""<p>مرحباً،</p>
					<p>تم تأكيد حجزك رقم {0} في تاريخ {1} الساعة {2}.</p>
					<p>نشكرك على اختيار Re Studio.</p>
					""".format(self.name, getattr(self, 'booking_date', ''), getattr(self, 'start_time', ''))
				)
			)
		except Exception as e:
			# تسجيل الخطأ دون إيقاف عملية الحفظ
			frappe.log_error(
				message=f"فشل إرسال بريد تأكيد الحجز {self.name}: {str(e)}",
				title="خطأ في إرسال البريد الإلكتروني"
			)

	def _deduplicate_selected_services(self):
		"""دمج الصفوف المكررة لنفس الخدمة داخل selected_services_table."""
		try:
			if not hasattr(self, 'selected_services_table') or not self.selected_services_table:
				return
			service_map = {}
			order = []
			for row in list(self.selected_services_table):
				service = getattr(row, 'service', None)
				if not service:
					continue
				qty = 0.0
				try:
					qty = float(getattr(row, 'quantity', 0) or 0)
				except Exception:
					qty = 0.0
				if qty == 0:
					qty = 1.0
				if service not in service_map:
					service_map[service] = row
					order.append(service)
					row.quantity = qty
				else:
					existing = service_map[service]
					try:
						existing_qty = float(getattr(existing, 'quantity', 0) or 0)
					except Exception:
						existing_qty = 0.0
					existing.quantity = existing_qty + qty
			sorted_rows = [service_map[s] for s in order]
			self.set('selected_services_table', sorted_rows)
		except Exception as err:
			frappe.log_error(f"deduplicate_selected_services_failed: {str(err)}")

	def _deduplicate_package_services(self):
		"""دمج الصفوف المكررة لنفس الخدمة داخل package_services_table."""
		try:
			if self.booking_type != 'Package':
				return
			if not hasattr(self, 'package_services_table') or not self.package_services_table:
				return
			service_map = {}
			order = []
			for row in list(self.package_services_table):
				service = getattr(row, 'service', None)
				if not service:
					continue
				qty = 0.0
				try:
					qty = float(getattr(row, 'quantity', 0) or 0)
				except Exception:
					qty = 0.0
				if qty == 0:
					qty = 1.0
				base_price = float(getattr(row, 'base_price', 0) or getattr(row, 'service_price', 0) or 0)
				photographer_discount_amount = float(getattr(row, 'photographer_discount_amount', 0) or 0)
				if service not in service_map:
					service_map[service] = row
					order.append(service)
					row.quantity = qty
					row.base_price = base_price
					row.photographer_discount_amount = photographer_discount_amount
				else:
					existing = service_map[service]
					try:
						existing_qty = float(getattr(existing, 'quantity', 0) or 0)
					except Exception:
						existing_qty = 0.0
					existing.quantity = existing_qty + qty
					try:
						existing.photographer_discount_amount = float(getattr(existing, 'photographer_discount_amount', 0) or 0) + photographer_discount_amount
					except Exception:
						pass
			for service_code in order:
				row = service_map[service_code]
				bp = float(getattr(row, 'base_price', 0) or 0)
				q = float(getattr(row, 'quantity', 1) or 1)
				discount = float(getattr(row, 'photographer_discount_amount', 0) or 0)
				line_base = bp * q
				row.amount = max(line_base - discount, 0)
			sorted_rows = [service_map[s] for s in order]
			self.set('package_services_table', sorted_rows)
		except Exception as err:
			frappe.log_error(f"deduplicate_package_services_failed: {str(err)}")

	def populate_package_services(self):
		"""Populate package services with photographer discounts applied."""
		if self.booking_type != "Package" or not getattr(self, 'package', None):
			return

		self.package_services_table = []
		package_doc = frappe.get_doc("Package", self.package)
		package_services = package_doc.package_services or []
		base_sum = 0.0
		discounted_sum = 0.0

		photographer_discount = 0
		photographer_services = {}
		if getattr(self, 'photographer', None) and getattr(self, 'photographer_b2b', False):
			try:
				photographer_doc = frappe.get_doc('Photographer', self.photographer)
				photographer_discount = flt(photographer_doc.discount_percentage or 0)
				for ps in photographer_doc.get('services', []):
					photographer_services[ps.service] = {
						'discounted_price': flt(ps.get('discounted_price') or 0),
						'base_price': flt(ps.get('base_price') or 0),
						'allow_discount': ps.get('allow_discount', 0)
					}
			except Exception as err:
				frappe.log_error(f"Error fetching photographer discount: {str(err)}")

		for service in package_services:
			qty = float(service.quantity or 1)
			try:
				base_price = flt(frappe.db.get_value("Service", service.service, "price") or 0)
			except Exception:
				base_price = 0

			package_price = flt(getattr(service, 'package_price', 0) or 0)
			hourly_rate = package_price if package_price > 0 else base_price
			photographer_rate = hourly_rate

			if service.service in photographer_services:
				service_config = photographer_services[service.service]
				if service_config['discounted_price'] > 0:
					photographer_rate = service_config['discounted_price']
				elif photographer_discount > 0 and service_config['allow_discount']:
					photographer_rate = hourly_rate * (1 - photographer_discount / 100.0)

			amount = qty * photographer_rate
			is_mandatory = getattr(service, 'is_required', 0) or 0

			self.append("package_services_table", {
				"service": service.service,
				"service_name": getattr(service, 'service_name', '') or service.service,
				"quantity": qty,
				"base_price": base_price,
				"package_price": hourly_rate,
				"photographer_discount_amount": photographer_rate,
				"amount": amount,
				"أجباري": is_mandatory
			})
			base_sum += qty * base_price
			discounted_sum += amount

		self.base_amount_package = round(base_sum, 2)
		self.total_amount_package = round(discounted_sum, 2)

		# ------------------------ Calculations ------------------------ #
	def calculate_time_usage(self):
		"""حساب الوقت:
		- في حالة Service: إجمالي الساعات = الفرق بين start_time و end_time (بالساعات العشرية) يخزن في total_booked_hours.
		- في حالة Package: يجمع ساعات كل صف في package_booking_dates (end - start) ويضع الناتج في used_hours ويحسب remaining_hours = total_hours في الباقة - used_hours.
		- التحقق: لو نوع Package يجب إدخال صف واحد على الأقل في package_booking_dates وإلا خطأ.
		"""
		from frappe.utils import time_diff_in_seconds
		if self.booking_type == 'Service':
			if getattr(self, 'start_time', None) and getattr(self, 'end_time', None):
				try:
					seconds = time_diff_in_seconds(self.end_time, self.start_time)
					if seconds < 0:
						frappe.throw(_('وقت النهاية يجب أن يكون بعد وقت البداية'))
					self.total_booked_hours = round(seconds / 3600.0, 2)
					# ترحيل إجمالي الساعات إلى جدول الخدمات المختارة (quantity = عدد الساعات)
					if hasattr(self, 'selected_services_table') and self.selected_services_table:
						for row in self.selected_services_table:
							# دائماً نطابق عدد الساعات مع الجدولة (مصدر الحقيقة)
							row.quantity = self.total_booked_hours
				except Exception:
					pass
		elif self.booking_type == 'Package':
			# تحقق وجود صفوف
			rows = getattr(self, 'package_booking_dates', [])
			if not rows:
				frappe.throw(_('يجب إدخال تواريخ / أوقات الحجز في جدول الباقة'))
			used = 0.0
			for r in rows:
				if getattr(r, 'start_time', None) and getattr(r, 'end_time', None):
					try:
						sec = time_diff_in_seconds(r.end_time, r.start_time)
						if sec < 0:
							frappe.throw(_('وقت النهاية يجب أن يكون بعد وقت البداية في صف الحجز'))
						# ساعات الصف
						row_hours = round(sec / 3600.0, 2)
						# خزن الحقل hours لو موجود
						if hasattr(r, 'hours'):
							r.hours = row_hours
						used += row_hours
					except Exception:
						pass
			self.used_hours = round(used, 2)
			# جلب total_hours من الباقة لو لم يتم جلبه
			if getattr(self, 'package', None) and not getattr(self, 'remaining_hours', None):
				try:
					total_hours_pkg = frappe.db.get_value('Package', self.package, 'total_hours') or 0
					self.remaining_hours = round(float(total_hours_pkg) - self.used_hours, 2)
				except Exception:
					self.remaining_hours = 0
	def set_default_deposit_percentage(self):
		"""تعيين نسبة العربون الافتراضية دائماً من General Settings فقط (حقل عربي: 'نسبة العربون (%)').
		لا يتم أخذ أي نسبة من الباقة الآن بناءً على طلبك. إذا لم توجد قيمة في الإعدادات يتم fallback = 30.
		لا نعدل إن وُجدت قيمة حالية (قد تكون محقونة مسبقاً)."""
		if getattr(self, 'deposit_percentage', None) not in (None, ""):
			return
		try:
			settings = frappe.db.get_singles_dict('General Settings') if frappe.db.exists('DocType', 'General Settings') else {}
			val = None
			# الأولوية للحقل العربي المذكور
			for key in ('نسبة العربون (%)', 'deposit_percentage', 'نسبة_العربون_%'):
				if key in settings and settings.get(key) is not None:
					val = settings.get(key)
					break
			if val is not None:
				self.deposit_percentage = flt(val)
		except Exception:
			pass
		# fallback النهائي لو ظل فارغ
		if getattr(self, 'deposit_percentage', None) in (None, ""):
			self.deposit_percentage = 30

	def calculate_package_totals(self):
		"""Delegate package total computation to shared helper."""
		calculate_package_totals_logic(self)

	def calculate_service_totals(self):
		"""Delegate service total computation to shared helper."""
		calculate_service_totals_logic(self)

	def recalculate_service_pricing(self):
		"""Recalculate service pricing when photographer or B2B status changes"""
		if self.booking_type == "Service":
			self.calculate_booking_service_item_rows()
			self.calculate_service_totals()
		elif self.booking_type == "Package":
			self.populate_package_services()

	def calculate_booking_service_item_rows(self):
		"""حساب أسعار و إجمالي عناصر جدول Booking Service Item حسب خصم المصور.

		الشروط:
		- سعر الساعة قبل الخصم = السعر الأساسي من Service
		- السعر بعد الخصم من Photographer (لو photographer_b2b مفعّل و يوجد خصم للمصور)
		- المبلغ الإجمالي = عدد الساعات * سعر الساعة قبل الخصم
		  وإذا كان السعر بعد الخصم > 0 و مختلف عن الأساسي: المبلغ الإجمالي = عدد الساعات * السعر بعد الخصم
		تنفَّذ أثناء الإنشاء (validate).
		"""
		if self.booking_type != "Service":
			return
		if not hasattr(self, 'booking_service_items') or not self.booking_service_items:
			return

		photographer_discount_pct = 0
		allowed_services = set()
		if getattr(self, 'photographer_b2b', False) and getattr(self, 'photographer', None):
			try:
				photographer_discount_pct = flt(frappe.db.get_value("Photographer", self.photographer, "discount_percentage") or 0)
				photographer_services = frappe.get_all("Photographer Service", filters={"parent": self.photographer, "is_active": 1}, fields=["service"])
				allowed_services = {ps.service for ps in photographer_services}
			except Exception:
				photographer_discount_pct = 0

		total = 0
		base_total = 0
		discount_total = 0
		for row in self.booking_service_items:
			if not getattr(row, 'service', None):
				continue
			# احصل على السعر الأساسي من Service إذا لم يكن موجوداً أو صفر
			base_price = flt(row.service_price) if flt(getattr(row, 'service_price', 0)) else 0
			if base_price == 0:
				try:
					base_price = flt(frappe.db.get_value("Service", row.service, "price") or 0)
				except Exception:
					base_price = 0
			row.service_price = base_price

			# حساب السعر بعد خصم المصور
			discounted_price = base_price
			if photographer_discount_pct > 0 and base_price > 0 and row.service in allowed_services:
				discounted_price = base_price * (1 - photographer_discount_pct / 100.0)
			row.discounted_price = discounted_price

			qty = flt(getattr(row, 'quantity', 1) or 1)
			base_total += qty * base_price
			if discounted_price > 0 and discounted_price != base_price:
				row.total_amount = qty * discounted_price
				discount_total += qty * discounted_price
			else:
				row.total_amount = qty * base_price
				discount_total += qty * base_price
			total += flt(row.total_amount)

		# تخزين الإجماليات (قبل / بعد الخصم) للحجز (يُستخدم فقط إن لم نستعمل selected_services_table)
		if base_total and not getattr(self, 'base_amount', None):
			self.base_amount = base_total
		if discount_total and (not getattr(self, 'total_amount', None) or not self.total_amount):
			self.total_amount = discount_total

		# لا نكتب self.total_amount هنا مباشرة حتى لا نتعارض مع حسابات أخرى، سيجمعها calculate_booking_total

	def calculate_booking_total(self):
		"""Calculate total booking amount from service items (service table)"""
		total = 0
		if hasattr(self, 'booking_service_items') and self.booking_service_items:
			for item in self.booking_service_items:
				if hasattr(item, 'total_amount') and item.total_amount:
					total += flt(item.total_amount)
		# For service bookings rely on self.total_amount already set by calculate_service_totals if > 0
		if total and self.booking_type == "Service":
			self.total_amount = total
		# Deposit removed here; handled centrally in _compute_deposit

	# ------------------------ Validation Helpers ------------------------ #
			# تحديث العربون بناءً على هذه القيم لاحقاً في calculate_booking_total

@frappe.whitelist()
def recalc_booking_deposit(booking: str):
	"""Recompute pricing, totals, and deposit for an existing booking."""
	if not booking:
		frappe.throw(_('Booking required'))

	# احسب القيم وأعدها للواجهة بدون حفظ المستند لتجنب تعارض "modified"
	doc = frappe.get_doc('Booking', booking)
	recompute_pricing(doc)
	calculate_booking_total(doc)
	calculate_deposit_amount(doc)
	return {
		'booking': booking,
		'deposit_amount': doc.deposit_amount,
		'payment_status': getattr(doc, 'payment_status', None)
	}

@frappe.whitelist()
def debug_deposit_calculation(booking: str):
	"""Return a step-by-step breakdown of deposit calculation for debugging."""
	if not booking:
		frappe.throw(_('Booking required'))

	doc = frappe.get_doc('Booking', booking)

	settings = frappe.db.get_singles_dict('General Settings') if frappe.db.exists('DocType', 'General Settings') else {}
	deposit_pct = None
	for key in ('نسبة العربون (%)', 'deposit_percentage', 'نسبة_العربون_%'):
		if key in settings and settings.get(key) is not None:
			deposit_pct = float(settings.get(key))
			break
	if deposit_pct is None:
		deposit_pct = 30.0

	if doc.booking_type == 'Service':
		basis_amount = float(getattr(doc, 'total_amount', 0) or 0)
		basis_field = 'total_amount'
	else:
		basis_amount = float(getattr(doc, 'total_amount_package', 0) or 0)
		basis_field = 'total_amount_package'

	step1 = basis_amount * deposit_pct
	step2 = step1 / 100.0
	final_deposit = round(step2, 2)

	return {
		'booking': booking,
		'booking_type': doc.booking_type,
		'basis_field': basis_field,
		'basis_amount': basis_amount,
		'deposit_percentage': deposit_pct,
		'calculation_steps': {
			'step1_multiply': f"{basis_amount} × {deposit_pct} = {step1}",
			'step2_divide': f"{step1} ÷ 100 = {step2}",
			'step3_round': f"round({step2}, 2) = {final_deposit}"
		},
		'calculated_deposit': final_deposit,
		'current_deposit_amount': float(getattr(doc, 'deposit_amount', 0) or 0),
		'matches': final_deposit == float(getattr(doc, 'deposit_amount', 0) or 0)
	}

@frappe.whitelist()
def recalculate_booking_totals(booking_name):
	"""Recalculate pricing for an existing (already saved) booking."""
	# Avoid processing unsaved temp names
	if not booking_name or booking_name.startswith("new-"):
		return {"error": "unsaved", "message": _("يجب حفظ الحجز أولاً قبل إعادة الحساب")}
	booking = frappe.get_doc("Booking", booking_name)
	# احسب القيم على كائن الذاكرة فقط وأعدها للواجهة بدون حفظ
	booking.recalculate_service_pricing()
	booking.calculate_booking_total()
	return {
		"total_amount": booking.total_amount,
		"deposit_amount": getattr(booking, 'deposit_amount', 0),
		"package_discount_total": getattr(booking, 'total_amount_package', None)
	}

# API Methods
@frappe.whitelist()
def update_booking_status(booking, status):
	"""Update booking status"""
	try:
		booking_doc = frappe.get_doc("Booking", booking)
		booking_doc.status = status
		booking_doc.save()
		frappe.db.commit()
		
		# Add to status history if field exists
		if hasattr(booking_doc, 'status_history'):
			status_history = json.loads(booking_doc.status_history or '[]')
			status_history.append({
				'status': status,
				'timestamp': frappe.utils.now(),
				'user': frappe.session.user
			})
			booking_doc.status_history = json.dumps(status_history)
			booking_doc.save()
		
		return {"success": True, "message": _("تم تحديث حالة الحجز")}
	except Exception as e:
		frappe.log_error(f"Error updating booking status: {str(e)}")
		frappe.throw(_("خطأ في تحديث حالة الحجز: {0}").format(str(e)))

@frappe.whitelist()
def get_available_photographers(booking_date, booking_time, service, duration=60):
	"""Get available photographers for a specific date and time"""
	try:
		# Get all active photographers
		photographers = frappe.get_all(
			"Photographer",
			filters={"is_active": 1},
			fields=["name", "photographer_name"]
		)
		
		# Check availability for each photographer
		available_photographers = []
		for photographer in photographers:
			# Check if photographer has any conflicting bookings
			conflicting_bookings = frappe.get_all(
				"Booking",
				filters={
					"booking_date": booking_date,
					"booking_time": booking_time,
					"photographer": photographer.name,
					"status": ["not in", ["Cancelled"]]
				}
			)
			
			if not conflicting_bookings:
				available_photographers.append(photographer.name)
		
		return available_photographers
	except Exception as e:
		frappe.log_error(f"Error getting available photographers: {str(e)}")
		return []

@frappe.whitelist()
def get_service_details(service):
	"""Get service details"""
	try:
		service_doc = frappe.get_doc("Service", service)
		return {
			"service_name": service_doc.service_name_en,
			"service_name_ar": service_doc.service_name_en,  # استخدم نفس الحقل لكلا اللغتين
			"duration": service_doc.get("duration", 60),
			"price": service_doc.get("price", 0),
			"description": service_doc.get("description", "")
		}
	except Exception as e:
		frappe.log_error(f"Error getting service details: {str(e)}")
		return {}

@frappe.whitelist()
def create_booking_invoice(booking):
	"""Create booking invoice for booking"""
	try:
		booking_doc = frappe.get_doc("Booking", booking)
		
		# Check if invoice already exists
		if hasattr(booking_doc, 'invoice') and booking_doc.invoice:
			return {"success": False, "message": _("الفاتورة موجودة بالفعل")}
		
		# Import the function from booking_invoice module
		from re_studio_booking.re_studio_booking.doctype.booking_invoice.booking_invoice import create_invoice_from_booking
		
		# Create booking invoice
		invoice_name = create_invoice_from_booking(booking)
		
		return {"success": True, "invoice": invoice_name, "message": _("تم إنشاء الفاتورة بنجاح")}
	except Exception as e:
		frappe.log_error(f"Error creating booking invoice: {str(e)}")
		return {"success": False, "message": _("خطأ في إنشاء الفاتورة: {0}").format(str(e))}

@frappe.whitelist()
def create_booking_quotation(booking):
	"""Create booking quotation for booking"""
	try:
		booking_doc = frappe.get_doc("Booking", booking)
		
		# Check if quotation already exists
		if hasattr(booking_doc, 'quotation') and booking_doc.quotation:
			return {"success": False, "message": _("العرض موجود بالفعل")}
		
		# Import the function from booking_quotation module
		from re_studio_booking.re_studio_booking.doctype.booking_quotation.booking_quotation import create_quotation_from_booking
		
		# Create booking quotation
		quotation_name = create_quotation_from_booking(booking)
		
		return {"success": True, "quotation": quotation_name, "message": _("تم إنشاء العرض بنجاح")}
	except Exception as e:
		frappe.log_error(f"Error creating booking quotation: {str(e)}")
		return {"success": False, "message": _("خطأ في إنشاء العرض: {0}").format(str(e))}

@frappe.whitelist()
def send_booking_confirmation(booking):
	"""Send booking confirmation"""
	try:
		booking_doc = frappe.get_doc("Booking", booking)
		booking_doc.send_confirmation()
		return {"success": True, "message": _("تم إرسال تأكيد الحجز بنجاح")}
	except Exception as e:
		frappe.log_error(f"Error sending booking confirmation: {str(e)}")
		return {"success": False, "message": _("خطأ في إرسال تأكيد الحجز: {0}").format(str(e))}

@frappe.whitelist()
def bulk_update_status(names, status):
	"""Bulk update booking status"""
	try:
		updated_count = 0
		for name in names:
			booking_doc = frappe.get_doc("Booking", name)
			booking_doc.status = status
			booking_doc.save()
			updated_count += 1
		
		frappe.db.commit()
		return {"success": True, "message": _("تم تحديث {0} حجز").format(updated_count)}
	except Exception as e:
		frappe.log_error(f"Error bulk updating status: {str(e)}")
		return {"success": False, "message": _("خطأ في التحديث المجمع: {0}").format(str(e))}

@frappe.whitelist()
def get_events(start, end, filters=None):
	"""Get calendar events"""
	try:
		conditions = []
		values = []
		
		# Date range filter
		conditions.append("booking_date BETWEEN %s AND %s")
		values.extend([start, end])
		
		# Apply additional filters
		if filters:
			filter_dict = json.loads(filters) if isinstance(filters, str) else filters
			for key, value in filter_dict.items():
				if value and key in ['photographer', 'service', 'status']:
					conditions.append(f"{key} = %s")
					values.append(value)
		
		# Build query
		where_clause = " AND ".join(conditions) if conditions else "1=1"
		
		# لم يعد هناك حقل service مباشر بعد إزالة الحقول، نجلب أول عنصر خدمة (إن وجد) من جدول booking_service_items
		events = frappe.db.sql(f"""
			SELECT 
				b.name,
				b.customer_name,
				b.booking_date,
				b.booking_datetime,
				b.booking_end_datetime,
				b.photographer,
				b.photographer_name,
				b.status,
				b.customer_phone,
				(
					SELECT bi.service_name FROM `tabBooking Service Item` bi
					WHERE bi.parent = b.name
					ORDER BY bi.idx ASC LIMIT 1
				) as service_name
			FROM `tabBooking` b
			WHERE {where_clause}
			ORDER BY b.booking_date, b.booking_datetime
		""", values, as_dict=True)
		
		# Format events for calendar
		calendar_events = []
		for event in events:
			calendar_events.append({
				"name": event.name,
				"title": event.customer_name or event.name,
				"start": event.booking_datetime or f"{event.booking_date} 09:00:00",
				"end": event.booking_end_datetime or f"{event.booking_date} 10:00:00",
				"allDay": False,
				"color": get_status_color(event.status),
				"status": event.status,
				"customer_name": event.customer_name,
				"photographer_name": event.photographer_name,
				"service_name": event.service_name,
				"customer_phone": event.customer_phone,
				"booking_date": event.booking_date
			})
		
		return calendar_events
	except Exception as e:
		frappe.log_error(f"Error getting calendar events: {str(e)}")
		return []

@frappe.whitelist()
def get_invoice(booking):
	"""Get booking invoice for booking"""
	try:
		booking_doc = frappe.get_doc("Booking", booking)
		return getattr(booking_doc, 'invoice', None)
	except Exception as e:
		frappe.log_error(f"Error getting invoice: {str(e)}")
		return None

@frappe.whitelist()
def get_quotation(booking):
	"""Get booking quotation for booking"""
	try:
		booking_doc = frappe.get_doc("Booking", booking)
		return getattr(booking_doc, 'quotation', None)
	except Exception as e:
		frappe.log_error(f"Error getting quotation: {str(e)}")
		return None

@frappe.whitelist()
def validate_booking_date(booking_date):
	"""Validate booking date"""
	try:
		# Check if date is in the past
		if booking_date < frappe.utils.today():
			return {
				"valid": False,
				"message": _("لا يمكن الحجز في تاريخ سابق"),
				"next_available_date": frappe.utils.today()
			}
		
		# Check if date is a holiday (implement your holiday logic here)
		# For now, just check if it's a Friday (example)
		date_obj = frappe.utils.getdate(booking_date)
		if date_obj.weekday() == 4:  # Friday
			next_date = frappe.utils.add_days(booking_date, 1)
			return {
				"valid": False,
				"message": _("يوم الجمعة عطلة رسمية"),
				"next_available_date": next_date
			}
		
		return {"valid": True}
	except Exception as e:
		frappe.log_error(f"Error validating booking date: {str(e)}")
		return {"valid": False, "message": _("خطأ في التحقق من التاريخ")}

@frappe.whitelist()
def get_available_time_slots(booking_date, service=None, photographer=None):
	"""
	Get available time slots for a specific date
	Considers existing bookings and their durations to prevent overlaps
	"""
	try:
		from datetime import datetime, timedelta
		
		# Get existing bookings for the date
		filters = {
			"booking_date": booking_date,
			"status": ["not in", ["Cancelled", "Rejected"]]
		}
		
		# If photographer is specified, filter by photographer
		if photographer:
			filters["photographer"] = photographer
		
		existing_bookings = frappe.get_all(
			"Booking",
			filters=filters,
			fields=["start_time", "end_time", "duration"]
		)
		
		# Generate all possible time slots (9 AM to 9 PM, every 30 minutes)
		all_slots = []
		for hour in range(9, 21):  # 9 AM to 9 PM
			all_slots.append(f"{hour:02d}:00:00")
			all_slots.append(f"{hour:02d}:30:00")
		
		# Create set of blocked time slots
		blocked_slots = set()
		
		for booking in existing_bookings:
			if booking.start_time and booking.end_time:
				# Convert to datetime for comparison
				start = datetime.strptime(str(booking.start_time), "%H:%M:%S")
				end = datetime.strptime(str(booking.end_time), "%H:%M:%S")
				
				# Block all slots that overlap with this booking
				for slot in all_slots:
					slot_time = datetime.strptime(slot, "%H:%M:%S")
					# Slot is blocked if it falls within the booking period
					if start <= slot_time < end:
						blocked_slots.add(slot)
		
		# Return available slots
		available_slots = [slot for slot in all_slots if slot not in blocked_slots]
		
		return available_slots
		
	except Exception as e:
		frappe.log_error(f"Error getting available time slots: {str(e)}", "Booking Time Slots Error")
		# Return default slots on error
		return [f"{hour:02d}:00:00" for hour in range(9, 21)]

@frappe.whitelist()
def get_photographer_details(photographer):
	"""Get photographer details"""
	try:
		photographer_doc = frappe.get_doc("Photographer", photographer)
		return {
			"photographer_name": photographer_doc.photographer_name,
			"phone": photographer_doc.get("phone", ""),
			"email": photographer_doc.get("email", "")
		}
	except Exception as e:
		frappe.log_error(f"Error getting photographer details: {str(e)}")
		return {}

@frappe.whitelist()
def get_client_details(client):
	"""Get client details"""
	try:
		client_doc = frappe.get_doc("Client", client)
		return {
			"client_name": client_doc.client_name,
			"phone": client_doc.get("mobile_no", ""),
			"email": client_doc.get("email_id", "")
		}
	except Exception as e:
		frappe.log_error(f"Error getting client details: {str(e)}")
		return {}

def get_status_color(status):
	"""Get color for booking status"""
	colors = {
		'Pending': '#ff9800',
		'Confirmed': '#2196f3', 
		'Completed': '#4caf50',
		'Cancelled': '#f44336'
	}
	return colors.get(status, '#9e9e9e')

# ملاحظة: تم حذف الدالة المكررة fetch_package_services_for_booking من هنا (السطر 1613-1688)
# الدالة الصحيحة والمحدثة موجودة في السطر 1870 تقريباً
# تم الحذف لتجنب التعارض والنتائج غير المتوقعة

@frappe.whitelist()
def delete_booking(booking_id):
	"""Delete a booking"""
	try:
		if frappe.db.exists("Booking", booking_id):
			frappe.delete_doc("Booking", booking_id)
			frappe.db.commit()
			return {"success": True, "message": "Booking deleted successfully"}
		else:
			return {"success": False, "message": "Booking not found"}
	except Exception as e:
		frappe.log_error(f"Error deleting booking: {str(e)}")
		return {"success": False, "message": f"Error: {str(e)}"}

@frappe.whitelist()
def get_photographer_availability(photographer, date):
	"""Get photographer availability for a specific date"""
	try:
		# Get existing availability records
		availability_records = frappe.get_all(
			"Photographer Availability",
			filters={
				"photographer": photographer,
				"date": date
			},
			fields=["start_time", "end_time", "status"]
		)
		
		# Create default time slots if no records exist
		if not availability_records:
			default_slots = []
			for hour in range(9, 21):  # 9 AM to 8 PM
				default_slots.append({
					"start_time": f"{hour:02d}:00:00",
					"end_time": f"{hour+1:02d}:00:00",
					"status": "Available"
				})
			return default_slots
		
		return availability_records
		
	except Exception as e:
		frappe.log_error(f"Error getting photographer availability: {str(e)}")
		return []

@frappe.whitelist()
def update_photographer_availability(photographer, date, start_time, end_time, status):
	"""Update or create photographer availability"""
	try:
		# Check if record exists
		existing = frappe.db.exists("Photographer Availability", {
			"photographer": photographer,
			"date": date,
			"start_time": start_time
		})
		
		if existing:
			# Update existing record
			doc = frappe.get_doc("Photographer Availability", existing)
			doc.status = status
			doc.save()
		else:
			# Create new record
			doc = frappe.get_doc({
				"doctype": "Photographer Availability",
				"photographer": photographer,
				"date": date,
				"start_time": start_time,
				"end_time": end_time,
				"status": status
			})
			doc.insert()
		
		frappe.db.commit()
		return {"success": True, "message": "Availability updated successfully"}
		
	except Exception as e:
		frappe.log_error(f"Error updating photographer availability: {str(e)}")
		return {"success": False, "message": f"Error: {str(e)}"}

@frappe.whitelist()
def get_photographer_schedule(photographer=None, week_start=None):
	"""Get photographer schedule for a week"""
	try:
		filters = {}
		if photographer:
			filters["photographer"] = photographer
		if week_start:
			filters["week_start_date"] = week_start
		
		schedules = frappe.get_all(
			"Photographer Schedule",
			filters=filters,
			fields=[
				"name", "photographer", "week_start_date", 
				"monday_start", "monday_end", "monday_available",
				"tuesday_start", "tuesday_end", "tuesday_available",
				"wednesday_start", "wednesday_end", "wednesday_available",
				"thursday_start", "thursday_end", "thursday_available",
				"friday_start", "friday_end", "friday_available",
				"saturday_start", "saturday_end", "saturday_available",
				"sunday_start", "sunday_end", "sunday_available",
				"status"
			],
			order_by="week_start_date desc"
		)
		
		return schedules
		
	except Exception as e:
		frappe.log_error(f"Error getting photographer schedule: {str(e)}")
		return []

@frappe.whitelist()
def create_photographer_leave(photographer, leave_type, from_date, to_date, reason=None):
	"""Create photographer leave request"""
	try:
		doc = frappe.get_doc({
			"doctype": "Photographer Leave",
			"photographer": photographer,
			"leave_type": leave_type,
			"from_date": from_date,
			"to_date": to_date,
			"reason": reason,
			"status": "Pending"
		})
		doc.insert()
		frappe.db.commit()
		
		return {"success": True, "message": "Leave request created successfully", "name": doc.name}
		
	except Exception as e:
		frappe.log_error(f"Error creating photographer leave: {str(e)}")
		return {"success": False, "message": f"Error: {str(e)}"}

@frappe.whitelist()
def approve_photographer_leave(leave_name):
	"""Approve photographer leave request"""
	try:
		doc = frappe.get_doc("Photographer Leave", leave_name)
		doc.status = "Approved"
		doc.save()
		frappe.db.commit()
		
		return {"success": True, "message": "Leave request approved successfully"}
		
	except Exception as e:
		frappe.log_error(f"Error approving photographer leave: {str(e)}")
		return {"success": False, "message": f"Error: {str(e)}"}

@frappe.whitelist()
def get_photographer_stats():
	"""Get photographer statistics"""
	try:
		stats = {}
		
		# Total photographers
		stats["total_photographers"] = frappe.db.count("Photographer")
		
		# Active photographers
		stats["active_photographers"] = frappe.db.count("Photographer", {"status": "Active"})
		
		# Today's bookings
		today = frappe.utils.today()
		stats["today_bookings"] = frappe.db.count("Booking", {"booking_date": today})
		
		# Photographers on leave today
		stats["on_leave"] = frappe.db.sql("""
			SELECT COUNT(DISTINCT photographer) 
			FROM `tabPhotographer Leave` 
			WHERE status = 'Approved' 
			AND %s BETWEEN from_date AND to_date
		""", (today,))[0][0] or 0
		
		return stats
	except Exception as e:
		frappe.log_error(f"Error getting photographer stats: {str(e)}")
		return {}

@frappe.whitelist()
def fetch_package_services_for_booking(package, photographer=None, photographer_b2b=0):
	"""Fetch package services for booking with pricing calculations"""
	try:
		if not package:
			return {"error": "Package is required"}
		
		# Get package services
		package_services = frappe.get_all(
			"Package Service Item",
			filters={"parent": package},
			fields=["service", "service_name", "quantity", "base_price", "package_price", "total_amount"]
		)
		
		if not package_services:
			return {"error": "No services found for this package"}
		
		# Process each service
		processed_services = []
		
		# جلب بيانات المصور وخدماته (إذا كان B2B مفعل)
		photographer_services = {}
		discount_percentage = 0
		
		if photographer and photographer_b2b:
			try:
				# جلب نسبة الخصم العامة للمصور
				discount_percentage = flt(frappe.db.get_value("Photographer", photographer, "discount_percentage") or 0)
				
				# جلب الخدمات المسموحة مع الأسعار المخصومة
				services_data = frappe.get_all(
					"Photographer Service",
					filters={"parent": photographer, "is_active": 1},
					fields=["service", "discounted_price", "base_price", "allow_discount"]
				)
				
				for ps in services_data:
					photographer_services[ps.service] = {
						'discounted_price': flt(ps.get('discounted_price') or 0),
						'base_price': flt(ps.get('base_price') or 0),
						'allow_discount': ps.get('allow_discount', 0)
					}
			except Exception as e:
				frappe.log_error(f"Error fetching photographer services: {str(e)}")
				photographer_services = {}
				discount_percentage = 0

		for service in package_services:
			qty = flt(service.quantity or 1)
			
			# السعر الأساسي (من Service master)
			base_price = flt(service.base_price or 0)
			
			# سعر الباقة الأولي (قبل خصم المصور)
			initial_package_price = flt(service.package_price or base_price or 0)
			
			# تطبيق خصم المصور على سعر الوحدة (لو B2B مفعل)
			final_package_price = initial_package_price
			
			if photographer and photographer_b2b and service.service in photographer_services:
				# الأولوية الأولى: استخدام السعر المخصوم من جدول المصور
				if photographer_services[service.service]['discounted_price'] > 0:
					final_package_price = photographer_services[service.service]['discounted_price']
				# الأولوية الثانية: استخدام نسبة الخصم العامة (لو allow_discount مفعل)
				elif discount_percentage > 0 and photographer_services[service.service]['allow_discount']:
					final_package_price = initial_package_price * (1 - discount_percentage / 100.0)
					if final_package_price < 0:
						final_package_price = 0
			
			# حساب المبلغ الإجمالي
			final_amount = final_package_price * qty

			processed_services.append({
				"service": service.service,
				"service_name": service.service_name,
				"quantity": qty,
				"base_price": base_price,
				"package_price": final_package_price,  # السعر بعد خصم المصور
				"amount": final_amount,  # المبلغ الإجمالي (package_price × quantity)
				"is_required": getattr(service, 'is_required', 0)
			})

		return {"rows": processed_services}
		
	except Exception as e:
		frappe.log_error(f"Error fetching package services: {str(e)}")
		return {"error": f"Error fetching package services: {str(e)}"}

@frappe.whitelist()
def handle_photographer_b2b_change(booking_name=None, photographer=None, is_b2b=None):
	"""Handle photographer B2B status change and recalculate pricing"""
	try:
		# If booking_name is provided and it's not a temporary name, get photographer from booking
		if booking_name and not photographer and not booking_name.startswith("new-booking-"):
			if frappe.db.exists("Booking", booking_name):
				booking_doc = frappe.get_doc("Booking", booking_name)
				photographer = booking_doc.get("photographer")
				is_b2b = booking_doc.get("photographer_b2b", 0)
				
				# Recalculate package services with photographer discount
				if booking_doc.booking_type == "Package" and booking_doc.package:
					package_services_result = fetch_package_services_for_booking(
						booking_doc.package, 
						photographer, 
						is_b2b
					)
					
					if package_services_result.get("rows"):
						# Clear existing package services
						booking_doc.package_services_table = []
						
						# Add updated services with photographer discount
						for service_data in package_services_result["rows"]:
							booking_doc.append("package_services_table", {
								"service": service_data["service"],
								"service_name": service_data.get("service_name"),
								"quantity": service_data["quantity"],
								"base_price": service_data["base_price"],
								"package_price": service_data["package_price"],
								"amount": service_data["amount"],
								"is_required": service_data.get("is_required", 0)
							})
						
						# Save the booking with updated services
						# validate() will automatically call recompute_pricing() and calculate_package_totals()
						booking_doc.save()
		
		if not photographer:
			# Return default values for new bookings
			return {
				"discount_percentage": 0,
				"is_b2b": 0,
				"photographer_name": "",
				"success": True
			}
		
		# Check if photographer exists
		if not frappe.db.exists("Photographer", photographer):
			return {
				"discount_percentage": 0,
				"is_b2b": 0,
				"photographer_name": photographer,
				"success": True
			}
		
		# Get photographer details
		photographer_doc = frappe.get_doc("Photographer", photographer)
		
		# Get B2B status from photographer if not provided
		if is_b2b is None:
			is_b2b = getattr(photographer_doc, 'b2b', 0)
		
		discount_percentage = getattr(photographer_doc, 'discount_percentage', 0) if is_b2b else 0
		
		return {
			"discount_percentage": discount_percentage,
			"is_b2b": is_b2b,
			"photographer_name": getattr(photographer_doc, 'photographer_name', photographer),
			"success": True
		}
		
	except Exception as e:
		frappe.log_error(f"Error handling photographer B2B change: {str(e)}")
		return {
			"discount_percentage": 0,
			"is_b2b": 0,
			"photographer_name": "",
			"error": f"Error handling photographer B2B change: {str(e)}",
			"success": False
		}

# ================ General Settings Integration ================

@frappe.whitelist()
def get_studio_working_days():
	"""جلب أيام العمل للاستديو من General Settings"""
	try:
		if not frappe.db.exists('DocType', 'General Settings'):
			return get_default_studio_working_days()
		
		settings = frappe.get_single('General Settings')
		working_days = []
		
		# خريطة أيام العمل
		days_mapping = {
			'sunday_working': 'Sunday',
			'monday_working': 'Monday', 
			'tuesday_working': 'Tuesday',
			'wednesday_working': 'Wednesday',
			'thursday_working': 'Thursday',
			'friday_working': 'Friday',
			'saturday_working': 'Saturday'
		}
		
		for field_name, day_name in days_mapping.items():
			if hasattr(settings, field_name) and getattr(settings, field_name):
				working_days.append(day_name)
		
		# إذا لم توجد إعدادات، استخدم الافتراضي
		if not working_days:
			working_days = get_default_studio_working_days()
		
		return working_days
		
	except Exception as e:
		frappe.logger().error(f"Error getting studio working days: {str(e)}")
		return get_default_studio_working_days()

def get_default_studio_working_days():
	"""أيام العمل الافتراضية للاستديو (كل الأيام عدا الجمعة)"""
	return ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Saturday']

@frappe.whitelist()
def get_studio_business_hours():
	"""جلب ساعات العمل للاستديو من General Settings"""
	try:
		if not frappe.db.exists('DocType', 'General Settings'):
			return get_default_studio_business_hours()
		
		settings = frappe.get_single('General Settings')
		
		business_hours = {
			'opening_time': getattr(settings, 'opening_time', None) or '09:00:00',
			'closing_time': getattr(settings, 'closing_time', None) or '17:00:00'
		}
		
		return business_hours
		
	except Exception as e:
		frappe.logger().error(f"Error getting studio business hours: {str(e)}")
		return get_default_studio_business_hours()

def get_default_studio_business_hours():
	"""ساعات العمل الافتراضية للاستديو"""
	return {
		'opening_time': '09:00:00',
		'closing_time': '17:00:00'
	}

@frappe.whitelist()
def is_studio_working_day(date_str):
	"""فحص إذا كان اليوم المحدد يوم عمل للاستديو حسب General Settings"""
	try:
		from datetime import datetime
		date_obj = datetime.strptime(date_str, '%Y-%m-%d')
		day_name = date_obj.strftime('%A')  # Sunday, Monday, etc.
		
		working_days = get_studio_working_days()
		return day_name in working_days
		
	except Exception as e:
		frappe.logger().error(f"Error checking studio working day: {str(e)}")
		return True  # افتراضي: يوم عمل

@frappe.whitelist()
def get_studio_settings():
	"""جلب جميع إعدادات الاستديو من General Settings"""
	working_days = get_studio_working_days()
	business_hours = get_studio_business_hours()
	
	return {
		'working_days': working_days,
		'business_hours': business_hours,
		'is_friday_working': 'Friday' in working_days,
		'studio_status': 'open' if working_days else 'closed'
	}

@frappe.whitelist()
def get_booking_events(start, end, filters=None):
	"""جلب أحداث الحجوزات لعرض Calendar محسن"""
	try:
		conditions = ["1=1"]
		values = []
		
		# تصفية حسب التاريخ
		if start:
			conditions.append("booking_date >= %s")
			values.append(start)
		if end:
			conditions.append("booking_date <= %s") 
			values.append(end)
		
		# تصفية إضافية
		if filters:
			for key, value in filters.items():
				if value:
					conditions.append(f"`{key}` = %s")
					values.append(value)
		
		# استعلام محسن للحجوزات
		bookings = frappe.db.sql(f"""
			SELECT 
				name,
				client_name,
				booking_date,
				start_time,
				end_time,
				status,
				booking_type,
				photographer,
				service_name,
				package_name
			FROM `tabBooking`
			WHERE {' AND '.join(conditions)}
			AND status != 'Cancelled'
			ORDER BY booking_date, start_time
		""", values, as_dict=True)
		
		# تحويل إلى تنسيق Calendar
		events = []
		for booking in bookings:
			# تحديد العنوان
			title = f"📅 {booking.client_name}"
			if booking.service_name:
				title += f" - {booking.service_name}"
			elif booking.package_name:
				title += f" - {booking.package_name}"
			
			# تحديد اللون حسب نوع الحجز
			color = "#4CAF50"  # أخضر للخدمات
			if booking.booking_type == "Package":
				color = "#9C27B0"  # بنفسجي للباقات
			elif booking.status == "Pending":
				color = "#FF9800"  # برتقالي للمعلق
			
			# تحديد التوقيت
			start_datetime = str(booking.booking_date)
			end_datetime = str(booking.booking_date)
			
			if booking.start_time:
				start_datetime += f"T{booking.start_time}"
			if booking.end_time:
				end_datetime += f"T{booking.end_time}"
			
			event = {
				"id": booking.name,
				"title": title,
				"start": start_datetime,
				"end": end_datetime,
				"allDay": not (booking.start_time and booking.end_time),
				"color": color,
				"booking_type": booking.booking_type,
				"status": booking.status,
				"photographer": booking.photographer,
				"url": f"/app/booking/{booking.name}"
			}
			
			events.append(event)
		
		return events
		
	except Exception as e:
		frappe.logger().error(f"Error getting booking events: {str(e)}")
		return []

@frappe.whitelist()
def get_package_services(package_name):
	"""
	الحصول على خدمات الباقة مع تجاوز فحص الصلاحيات
	
	Args:
		package_name: اسم الباقة
		
	Returns:
		list: قائمة خدمات الباقة
	"""
	try:
		# جلب مستند الباقة
		package_doc = frappe.get_doc("Package", package_name)
		
		# التحقق من وجود خدمات
		if not package_doc.get("package_services"):
			frappe.throw(_("لا توجد خدمات في هذه الباقة. يرجى إضافة خدمات أولاً."))
		
		services = []
		# اسم الحقل الصحيح هو "package_services" وليس "services"
		for service_row in package_doc.get("package_services", []):
			services.append({
				"service": service_row.service,
				"service_name": service_row.get("service_name", ""),
				"quantity": service_row.get("quantity", 1),
				"service_price": service_row.get("service_price", 0),
				"base_price": service_row.get("base_price", 0),
				"package_price": service_row.get("package_price", 0),
				"amount": service_row.get("amount", 0),
				"is_mandatory": 1  # جميع خدمات الباقة إجبارية افتراضياً
			})
		
		# جلب معلومات الباقة أيضاً
		return {
			"services": services,
			"package_name": package_doc.package_name,
			"package_name_ar": package_doc.get("package_name_ar", ""),
			"total_hours": package_doc.get("total_hours", 0),
			"minimum_booking_hours": package_doc.get("minimum_booking_hours", 1),
			"total_price": package_doc.get("total_price", 0),
			"final_price": package_doc.get("final_price", 0),
			"discount_percentage": package_doc.get("discount_percentage", 0)
		}
		
	except Exception as e:
		error_msg = f"خطأ في جلب خدمات الباقة: {str(e)}"
		frappe.log_error(error_msg, "Get Package Services")
		frappe.throw(_(error_msg))

@frappe.whitelist()
def get_package_services_with_photographer(package_name, photographer=None, photographer_b2b=0):
	"""
	الحصول على خدمات الباقة مع تطبيق خصم المصور إذا كان موجوداً
	
	Args:
		package_name: اسم الباقة
		photographer: اسم المصور (اختياري)
		photographer_b2b: هل المصور B2B (0 أو 1)
		
	Returns:
		dict: معلومات الباقة مع الخدمات والأسعار بعد الخصم
	"""
	try:
		# جلب مستند الباقة
		package_doc = frappe.get_doc("Package", package_name)
		
		# التحقق من وجود خدمات
		if not package_doc.get("package_services"):
			frappe.throw(_("لا توجد خدمات في هذه الباقة. يرجى إضافة خدمات أولاً."))
		
		# جلب بيانات المصور وخدماته إذا كان موجوداً ومفعل B2B
		photographer_services = {}
		photographer_discount_pct = 0
		
		if photographer and int(photographer_b2b or 0) == 1:
			try:
				photographer_doc = frappe.get_doc('Photographer', photographer)
				if photographer_doc.get('b2b'):
					photographer_discount_pct = flt(photographer_doc.get('discount_percentage') or 0)
					# جلب الخدمات مع السعر المخصوم من جدول خدمات المصور
					for ps in photographer_doc.get('services', []):
						photographer_services[ps.service] = {
							'discounted_price': flt(ps.get('discounted_price') or 0),
							'base_price': flt(ps.get('base_price') or 0),
							'allow_discount': ps.get('allow_discount', 0)
						}
			except Exception as e:
				frappe.log_error(f"Error fetching photographer services: {str(e)}")
		
		services = []
		# معالجة خدمات الباقة مع تطبيق خصم المصور
		for service_row in package_doc.get("package_services", []):
			service_name = service_row.service
			quantity = flt(service_row.get("quantity", 1))
			
			# Get base price from Service table
			base_price = 0
			try:
				base_price = flt(frappe.db.get_value("Service", service_name, "price") or 0)
			except Exception:
				base_price = 0
			
			# Use package price as default, or base price if package price is 0
			package_price = flt(service_row.get('package_price', 0) or 0)
			hourly_rate = package_price if package_price > 0 else base_price
			
			# تطبيق خصم المصور - الأولوية للسعر المخصوم من جدول المصور
			final_package_price = hourly_rate
			
			if service_name in photographer_services:
				# الأولوية الأولى: استخدام السعر المخصوم (discounted_price) من جدول المصور
				if photographer_services[service_name]['discounted_price'] > 0:
					final_package_price = photographer_services[service_name]['discounted_price']
				# الأولوية الثانية: استخدام نسبة الخصم العامة إذا كانت الخدمة مسموح بخصمها
				elif photographer_discount_pct > 0 and photographer_services[service_name]['allow_discount']:
					final_package_price = hourly_rate * (1 - photographer_discount_pct / 100)
			
			# حساب المبلغ الإجمالي
			amount = quantity * final_package_price
			
			# Get is_required field from Package Service Item
			is_mandatory = service_row.get('is_required', 0) or 0
			
			services.append({
				"service": service_name,
				"service_name": service_row.get("service_name", ""),
				"quantity": quantity,
				"base_price": base_price,
				"package_price": final_package_price,  # السعر النهائي بعد خصم المصور
				"amount": amount,  # المبلغ الإجمالي (package_price × quantity)
				"is_mandatory": is_mandatory
			})
		
		# جلب معلومات الباقة
		return {
			"services": services,
			"package_name": package_doc.package_name,
			"package_name_ar": package_doc.get("package_name_ar", ""),
			"total_hours": package_doc.get("total_hours", 0),
			"minimum_booking_hours": package_doc.get("minimum_booking_hours", 1),
			"total_price": package_doc.get("total_price", 0),
			"final_price": package_doc.get("final_price", 0),
			"discount_percentage": package_doc.get("discount_percentage", 0)
		}
		
	except Exception as e:
		error_msg = f"خطأ في جلب خدمات الباقة مع خصم المصور: {str(e)}"
		frappe.log_error(error_msg, "Get Package Services With Photographer")
		frappe.throw(_(error_msg))


# ------------------------ Calendar View Methods ------------------------ #

@frappe.whitelist()
def get_events(start, end, filters=None):
	"""Get events for Calendar view - shows both Service and Package bookings"""
	from frappe.desk.calendar import get_event_conditions
	
	conditions = get_event_conditions("Booking", filters)
	
	# Get Service bookings
	service_events = frappe.db.sql(f"""
		SELECT 
			name,
			client_name as title,
			booking_date as start,
			booking_date as end,
			status,
			booking_type,
			service_name,
			start_time,
			end_time
		FROM `tabBooking`
		WHERE booking_date IS NOT NULL
		AND booking_type = 'Service'
		AND (booking_date BETWEEN %(start)s AND %(end)s)
		{conditions}
	""", {
		"start": start,
		"end": end
	}, as_dict=True)
	
	# Get Package bookings from Package Booking Date child table
	package_events = frappe.db.sql(f"""
		SELECT 
			b.name,
			b.client_name as title,
			pbd.booking_date as start,
			pbd.booking_date as end,
			b.status,
			'Package' as booking_type,
			b.package_name as service_name,
			pbd.start_time,
			pbd.end_time,
			pbd.name as child_name
		FROM `tabBooking` b
		INNER JOIN `tabPackage Booking Date` pbd ON pbd.parent = b.name
		WHERE pbd.booking_date IS NOT NULL
		AND b.booking_type = 'Package'
		AND (pbd.booking_date BETWEEN %(start)s AND %(end)s)
		{conditions.replace('`tabBooking`', 'b') if conditions else ''}
	""", {
		"start": start,
		"end": end
	}, as_dict=True)
	
	# Combine both lists
	all_events = service_events + package_events
	
	# Format events for calendar
	for event in all_events:
		# Set color based on status
		if event.status == "Confirmed":
			event.color = "#4CAF50"  # Green
		elif event.status == "Completed":
			event.color = "#2196F3"  # Blue
		elif event.status == "Cancelled":
			event.color = "#F44336"  # Red
		else:
			event.color = "#9E9E9E"  # Grey
		
		# Build proper datetime if times exist
		if event.start_time:
			event.start = f"{event.start} {event.start_time}"
			event.allDay = 0
		else:
			event.allDay = 1
			
		if event.end_time:
			event.end = f"{event.end} {event.end_time}"
		
		# Add service/package name to title with emoji indicator
		if event.service_name:
			badge = "📦" if event.booking_type == "Package" else "🎯"
			event.title = f"{badge} {event.title} - {event.service_name}"
		else:
			badge = "📦" if event.booking_type == "Package" else "🎯"
			event.title = f"{badge} {event.title}"
	
	return all_events
	
# ------------------------ Cashback Management ------------------------ #
def add_cashback_to_client(booking_doc):
	"""إضافة نقاط الكاش باك للعميل من الباقة"""
	if not booking_doc.client or booking_doc.booking_type != "Package" or not booking_doc.package:
		return
	
	package = frappe.get_doc("Package", booking_doc.package)
	cashback_points = flt(package.cashback_points or 0)
	
	if cashback_points > 0:
		client = frappe.get_doc("Client", booking_doc.client)
		client.cashback_balance = flt(client.cashback_balance or 0) + cashback_points
		client.total_cashback_earned = flt(client.total_cashback_earned or 0) + cashback_points
		
		client.add_comment(
			"Comment",
			_("تم إضافة {0} نقطة كاش باك من باقة {1} - الحجز {2}").format(
				cashback_points, booking_doc.package, booking_doc.name
			)
		)
		client.save(ignore_permissions=True)

def deduct_cashback_from_client(booking_doc):
	"""خصم الكاش باك المستخدم من رصيد العميل"""
	if not booking_doc.client or not booking_doc.cashback_used or flt(booking_doc.cashback_used) == 0:
		return
	
	client = frappe.get_doc("Client", booking_doc.client)
	client.cashback_balance = flt(client.cashback_balance or 0) - flt(booking_doc.cashback_used)
	client.total_cashback_used = flt(client.total_cashback_used or 0) + flt(booking_doc.cashback_used)
	client.save(ignore_permissions=True)


# ------------------------ User Permissions ------------------------ #
def has_permission(doc, ptype, user):
	"""
	التحكم في صلاحيات عرض الحجوزات
	- Administrator: يرى كل شيء
	- Re Studio Manager: يرى كل شيء
	- الموظف العادي: يرى حجوزاته فقط (سواء كان current_employee أو owner)
	"""
	if user == "Administrator":
		return True
	
	# الأدوار المسموح لها برؤية كل الحجوزات
	allowed_roles = ["Re Studio Manager", "System Manager"]
	user_roles = frappe.get_roles(user)
	
	if any(role in user_roles for role in allowed_roles):
		return True
	
	# الموظف العادي يرى حجوزاته فقط (current_employee أو owner)
	if doc.current_employee == user or doc.owner == user:
		return True
	
	return False

