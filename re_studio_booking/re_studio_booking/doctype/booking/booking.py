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
	validate_paid_amount,
	calculate_services_with_photographer_discount,
	recalculate_package_services_on_package_change
)

class Booking(Document):
	# ------------------------ Core Lifecycle ------------------------ #
	def before_save(self):
		"""تنفيذ العمليات قبل الحفظ"""
		# 0. تعيين الموظف الحالي تلقائياً
		if not self.current_employee:
			self.current_employee = frappe.session.user
		
		# 1. تغيير الحالة إلى Confirmed عند الحفظ
		if self.status != 'Confirmed':
			self.status = 'Confirmed'
		
		# 2. حساب مبلغ العربون تلقائياً
		self.calculate_deposit_amount()
		
		# 3. التحقق من أيام العمل حسب General Settings
		self.validate_studio_working_day()
		
		# 4. التحقق من صحة المبلغ المدفوع
		validate_paid_amount(self)
	
	def validate_studio_working_day(self):
		"""التحقق من أن تاريخ الحجز في يوم عمل حسب إعدادات General Settings"""
		if not self.booking_date:
			return
			
		try:
			from datetime import datetime
			booking_date = datetime.strptime(str(self.booking_date), '%Y-%m-%d')
			day_name = booking_date.strftime('%A')  # Sunday, Monday, etc.
			
			# جلب أيام العمل من General Settings
			working_days = self.get_studio_working_days()
			
			if day_name not in working_days:
				day_arabic = {
					'Sunday': 'الأحد',
					'Monday': 'الاثنين', 
					'Tuesday': 'الثلاثاء',
					'Wednesday': 'الأربعاء',
					'Thursday': 'الخميس',
					'Friday': 'الجمعة',
					'Saturday': 'السبت'
				}.get(day_name, day_name)
				
				frappe.throw(_(f"لا يمكن الحجز في يوم {day_arabic} - هذا اليوم عطلة رسمية حسب إعدادات الاستديو"))
				
		except Exception as e:
			frappe.logger().error(f"Error validating studio working day: {str(e)}")
	
	def get_studio_working_days(self):
		"""جلب أيام العمل للاستديو من General Settings"""
		try:
			if frappe.db.exists('DocType', 'General Settings'):
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
				
				# إذا لم توجد إعدادات، استخدم الافتراضي (كل الأيام عدا الجمعة)
				if not working_days:
					working_days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Saturday']
				
				return working_days
			else:
				# افتراضي: كل الأيام عدا الجمعة
				return ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Saturday']
		
		except Exception as e:
			frappe.logger().error(f"Error getting studio working days: {str(e)}")
			return ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Saturday']
	
	def calculate_deposit_amount(self):
		"""حساب مبلغ العربون تلقائياً بناءً على نوع الحجز"""
		try:
			# تحديد المبلغ الأساسي للحساب
			base_amount = 0
			
			if self.booking_type == 'Service':
				base_amount = self.total_amount or 0
			elif self.booking_type == 'Package':
				base_amount = self.total_amount_package or 0
			
			# الحصول على نسبة العربون من الإعدادات العامة
			deposit_percentage = 30  # افتراضي 30%
			try:
				general_settings = frappe.get_single('General Settings')
				if hasattr(general_settings, 'default_deposit_percentage') and general_settings.default_deposit_percentage:
					deposit_percentage = general_settings.default_deposit_percentage
			except:
				pass
			
			# حساب مبلغ العربون
			if base_amount > 0:
				self.deposit_amount = round(base_amount * deposit_percentage / 100, 2)
				
			# إضافة تشخيص لحساب العربون
			diagnosis = f"نوع الحجز: {self.booking_type}\n"
			diagnosis += f"المبلغ الأساسي: {base_amount}\n"
			diagnosis += f"نسبة العربون: {deposit_percentage}%\n"
			diagnosis += f"مبلغ العربون: {self.deposit_amount}"
			
			# يمكن عرض التشخيص في الـ log أو كرسالة
			frappe.logger().info(f"تشخيص حساب العربون للحجز {self.name}: {diagnosis}")
			
		except Exception as e:
			frappe.logger().error(f"خطأ في حساب العربون: {str(e)}")
			# قيمة افتراضية في حالة الخطأ
			if self.total_amount:
				self.deposit_amount = round(self.total_amount * 0.3, 2)
	
	def validate(self):
		# Validation & temporal logic (defensive: handle potential stale class load where validate_dates missing)
		if hasattr(self, 'validate_dates') and callable(getattr(self, 'validate_dates')):
			self.validate_dates()
		else:
			# Log once per process; fallback does minimal date check
			frappe.log_error("validate_dates missing on Booking instance - using fallback", "Booking.validate fallback")
			self._fallback_validate_dates()
		# Availability check with fallback
		if hasattr(self, 'validate_availability') and callable(getattr(self, 'validate_availability')):
			self.validate_availability()
		else:
			frappe.log_error("validate_availability missing on Booking instance - using fallback", "Booking.validate fallback")
			self._fallback_validate_availability()
		# Calculate booking datetime with fallback
		if hasattr(self, 'calculate_booking_datetime') and callable(getattr(self, 'calculate_booking_datetime')):
			self.calculate_booking_datetime()
		else:
			frappe.log_error("calculate_booking_datetime missing on Booking instance - using fallback", "Booking.validate fallback")
			self._fallback_calculate_booking_datetime()
		# Calculate time usage with fallback
		if hasattr(self, 'calculate_time_usage') and callable(getattr(self, 'calculate_time_usage')):
			self.calculate_time_usage()
		else:
			frappe.log_error("calculate_time_usage missing on Booking instance - using fallback", "Booking.validate fallback")
			self._fallback_calculate_time_usage()
		# Package hours usage (before pricing so quantities can reference remaining hours)
		if self.booking_type == 'Package':
			self.compute_package_hours_usage()
		# دمج تكرار نفس الخدمة في جدول الخدمات المختارة (جمع الساعات بدلاً من تكرار الصفوف)
		if self.booking_type == 'Service':
			self._deduplicate_selected_services()
		elif self.booking_type == 'Package':
			self._deduplicate_package_services()
		# Set default deposit percentage with fallback
		if hasattr(self, 'set_default_deposit_percentage') and callable(getattr(self, 'set_default_deposit_percentage')):
			self.set_default_deposit_percentage()
		else:
			frappe.log_error("set_default_deposit_percentage missing on Booking instance - using fallback", "Booking.validate fallback")
			self._fallback_set_default_deposit_percentage()
		# Unified pricing recompute (new consolidated flow)
		if hasattr(self, 'recompute_pricing') and callable(getattr(self, 'recompute_pricing')):
			self.recompute_pricing()
		else:
			frappe.log_error("recompute_pricing missing on Booking instance - using fallback", "Booking.validate fallback")
			self._fallback_recompute_pricing()
		# Legacy fallback (kept temporarily for safety) – can remove after verification
		if hasattr(self, 'calculate_booking_total') and callable(getattr(self, 'calculate_booking_total')):
			self.calculate_booking_total()
		else:
			frappe.log_error("calculate_booking_total missing on Booking instance - using fallback", "Booking.validate fallback")
			self._fallback_calculate_booking_total()

	def on_trash(self):
		"""منع حذف الحجز إذا كان مدفوعاً بالكامل (ما عدا Administrator)"""
		self._check_deletion_permission()
	
	def before_cancel(self):
		"""منع إلغاء الحجز إذا كان مدفوعاً بالكامل (ما عدا Administrator)"""
		self._check_deletion_permission()
	
	def _check_deletion_permission(self):
		"""التحقق من صلاحية حذف/إلغاء الحجز"""
		# السماح لـ Administrator بكل شيء
		if frappe.session.user == "Administrator":
			return
		
		# التحقق فقط لحجوزات الخدمات (Service)
		if self.booking_type != 'Service':
			return
		
		# التحقق من أن المبلغ المدفوع = المبلغ الإجمالي
		paid_amount = flt(getattr(self, 'paid_amount', 0) or 0)
		total_amount = flt(getattr(self, 'total_amount', 0) or 0)
		
		# إذا كان المبلغ المدفوع يساوي المبلغ الإجمالي (تم الدفع كاملاً)
		if paid_amount > 0 and total_amount > 0 and abs(paid_amount - total_amount) < 0.01:
			frappe.throw(
				msg=f"⛔ لا يمكن حذف أو إلغاء هذا الحجز!<br><br>"
					f"<b>السبب:</b> تم دفع المبلغ بالكامل<br>"
					f"<b>المبلغ الإجمالي:</b> {total_amount} ريال<br>"
					f"<b>المبلغ المدفوع:</b> {paid_amount} ريال<br><br>"
					f"يمكن فقط لـ <b>Administrator</b> حذف أو إلغاء هذا الحجز.<br>"
					f"يرجى التواصل مع مدير النظام.",
				title="غير مسموح بالحذف أو الإلغاء"
			)

	def compute_package_hours_usage(self):
		"""Compute used and remaining hours for a package based on package_booking_dates child rows.
		- Calculates each row.hours from start_time & end_time if both present.
		- Sums used_hours, fetches total allowed from Package.total_hours (fallback to duration).
		- Sets remaining_hours and validates not exceeding.
		- Prevent adding new rows if remaining becomes zero (validation error if extra time).
		"""
		try:
			if self.booking_type != 'Package':
				return
			
			# Determine total hours allotted by package
			package_total = 0.0
			if getattr(self, 'package', None):
				package_total = float(frappe.db.get_value('Package', self.package, 'total_hours') or 0)
			
			used = 0.0
			for row in (self.package_booking_dates or []):
				# Derive row.hours if times present
				if getattr(row, 'start_time', None) and getattr(row, 'end_time', None):
					try:
						# Convert to datetime for diff (assume arbitrary same date)
						from datetime import datetime
						fmt = '%H:%M:%S'
						start_str = str(row.start_time)
						end_str = str(row.end_time)
						start_dt = datetime.strptime(start_str, fmt)
						end_dt = datetime.strptime(end_str, fmt)
						# Handle crossing midnight: if end < start add 24h
						if end_dt <= start_dt:
							end_dt = end_dt.replace(day=end_dt.day + 1)
						row.hours = round((end_dt - start_dt).total_seconds() / 3600.0, 2)
					except Exception:
						# fallback: do nothing; ensure hours numeric
						if not getattr(row, 'hours', None):
							row.hours = 0
				if getattr(row, 'hours', None):
					used += float(row.hours)
			
			self.used_hours = round(used, 2)
			remaining = max(package_total - used, 0.0)
			self.remaining_hours = round(remaining, 2)
			
			# Validation: prevent exceeding package hours
			if package_total > 0 and self.used_hours > package_total:
				# التحقق من تجاوز الساعات بهامش خطأ صغير
				excess = self.used_hours - package_total
				if excess > 0.01:  # هامش خطأ 0.01 ساعة (36 ثانية)
					frappe.throw(
						msg=f"⚠️ تم تجاوز ساعات الباقة المتاحة!<br><br>"
							f"<b>إجمالي ساعات الباقة:</b> {package_total} ساعة<br>"
							f"<b>الساعات المستخدمة:</b> {self.used_hours} ساعة<br>"
							f"<b>الساعات الزائدة:</b> {round(excess, 2)} ساعة<br><br>"
							f"يرجى تعديل تواريخ الحجز لتتناسب مع الساعات المتاحة.",
						title="خطأ - تجاوز ساعات الباقة"
					)
				else:
					# إذا كان الفرق بسيط جداً، نعتبره مساوياً
					self.used_hours = package_total
					self.remaining_hours = 0.0
					
		except Exception as e:
			frappe.log_error(f"compute_package_hours_usage error: {str(e)}")

	def recompute_pricing(self):
		"""Unified pricing entry point. Computes service/package rows, applies photographer discounts
		(allowed services only), aggregates totals, and sets deposit.
		Keeps legacy functions for now but uses internal helpers to avoid duplication."""
		try:
			ctx = self._load_photographer_context()
			if self.booking_type == 'Package':
				self._build_package_rows(ctx)
				self._aggregate_package_totals()
			elif self.booking_type == 'Service':
				self._sync_selected_services_quantity_from_time()
				self._build_service_rows(ctx)
				self._aggregate_service_totals()
			self._compute_deposit()
			self._auto_set_payment_status()
			self._validate_paid_vs_deposit()
		except Exception as e:
			frappe.log_error(f"recompute_pricing error: {str(e)}")

	def _fallback_validate_dates(self):
		"""Fallback lightweight date validation used only if validate_dates mysteriously missing at runtime.
		Avoids hard failure; enforces basic rule: service booking date not in past.
		"""
		try:
			from frappe.utils import getdate, nowdate
			if getattr(self, 'booking_type', None) == 'Service' and getattr(self, 'booking_date', None):
				if getdate(self.booking_date) < getdate(nowdate()):
					frappe.throw("لا يمكن إنشاء حجز في تاريخ سابق (fallback)")
		except Exception:
			pass

	def _fallback_validate_availability(self):
		"""Minimal overlap check used only if validate_availability is missing (stale controller)."""
		try:
			if not (getattr(self, 'booking_date', None) and getattr(self, 'start_time', None) and getattr(self, 'end_time', None) and getattr(self, 'photographer', None)):
				return
			existing = frappe.get_all(
				"Booking",
				filters={
					"booking_date": self.booking_date,
					"photographer": self.photographer,
					"status": ["not in", ["Cancelled"]],
					"name": ["!=", self.name or "new"]
				},
				fields=["name", "start_time", "end_time"]
			)
			for b in existing:
				try:
					if b.start_time < self.end_time and b.end_time > self.start_time:
						frappe.throw("هذا الوقت محجوز بالفعل (fallback)")
				except Exception:
					continue
		except Exception:
			pass

	def _fallback_calculate_booking_datetime(self):
		"""Minimal booking datetime calculation fallback."""
		try:
			if getattr(self, 'booking_date', None) and getattr(self, 'start_time', None):
				from frappe.utils import get_datetime
				self.booking_datetime = get_datetime(f"{self.booking_date} {self.start_time}")
			if getattr(self, 'booking_date', None) and getattr(self, 'end_time', None):
				from frappe.utils import get_datetime
				self.booking_end_datetime = get_datetime(f"{self.booking_date} {self.end_time}")
		except Exception:
			pass

	def _fallback_calculate_time_usage(self):
		"""Minimal time usage calculation fallback."""
		try:
			if getattr(self, 'start_time', None) and getattr(self, 'end_time', None):
				from datetime import datetime
				start = datetime.strptime(str(self.start_time), '%H:%M:%S')
				end = datetime.strptime(str(self.end_time), '%H:%M:%S')
				if end > start:
					hours = (end - start).total_seconds() / 3600
					self.total_booked_hours = round(hours, 2)
		except Exception:
			pass

	def _fallback_set_default_deposit_percentage(self):
		"""Set default deposit percentage fallback."""
		try:
			if not getattr(self, 'deposit_percentage', None):
				self.deposit_percentage = 30  # Default 30%
		except Exception:
			pass

	def _fallback_calculate_booking_total(self):
		"""Calculate booking total fallback."""
		try:
			if self.booking_type == 'Service' and hasattr(self, 'selected_services_table'):
				total = 0
				for item in self.selected_services_table or []:
					if hasattr(item, 'total_amount') and item.total_amount:
						total += float(item.total_amount)
				if total > 0:
					self.total_amount = total
		except Exception:
			pass

	def _fallback_recompute_pricing(self):
		"""Basic pricing computation fallback."""
		try:
			if self.booking_type == 'Service' and hasattr(self, 'selected_services_table'):
				base_total = 0
				final_total = 0
				for row in self.selected_services_table or []:
					price = float(getattr(row, 'service_price', 0) or 0)
					qty = float(getattr(row, 'quantity', 1) or 1)
					base_total += price * qty
					final_total += float(getattr(row, 'total_amount', 0) or 0)
				self.base_amount = base_total
				self.total_amount = final_total
				# Basic deposit calculation (30% of total)
				if final_total > 0:
					self.deposit_amount = round(final_total * 0.3, 2)
		except Exception:
			pass

	def _load_photographer_context(self):
		"""Prepare discount percentage and allowed services list for the photographer."""
		ctx = {
			"discount_pct": 0.0,
			"allowed_services": set()
		}
		if getattr(self, 'photographer_b2b', False) and getattr(self, 'photographer', None):
			try:
				ctx["discount_pct"] = float(frappe.db.get_value("Photographer", self.photographer, "discount_percentage") or 0)
				photographer_services = frappe.get_all(
					"Photographer Service",
					filters={"parent": self.photographer, "is_active": 1},
					fields=["service"]
				)
				ctx["allowed_services"] = {ps.service for ps in photographer_services}
			except Exception:
				ctx["discount_pct"] = 0.0
		return ctx

	def _sync_selected_services_quantity_from_time(self):
		"""
		تحديث كمية الخدمات المختارة من إجمالي الساعات المحجوزة.
		ملاحظة: الخدمات المرنة لا يتم تحديث كميتها تلقائياً.
		"""
		if self.booking_type != 'Service':
			return
		if not getattr(self, 'total_booked_hours', None):
			return
		if not hasattr(self, 'selected_services_table') or not self.selected_services_table:
			return
		
		total_hours = flt(self.total_booked_hours)
		if total_hours <= 0:
			return
		
		# المرور على كل الخدمات المختارة
		for row in self.selected_services_table:
			try:
				service_name = getattr(row, 'service', None)
				if not service_name:
					continue
				
				# التحقق من أن الخدمة ليست مرنة
				is_flexible = frappe.db.get_value('Service', service_name, 'is_flexible_service')
				
				if not is_flexible:
					# تحديث الكمية = إجمالي الساعات (للخدمات غير المرنة فقط)
					row.quantity = total_hours
					frappe.logger().debug(
						f"📊 تحديث كمية الخدمة {service_name}: {total_hours} ساعة"
					)
				else:
					frappe.logger().debug(
						f"⚙️ الخدمة {service_name} مرنة - لا يتم تحديث الكمية"
					)
			except Exception as e:
				frappe.logger().error(f"خطأ في تحديث كمية الخدمة: {str(e)}")
				pass

	def _deduplicate_selected_services(self):
		"""دمج الصفوف المكررة لنفس الخدمة داخل selected_services_table:
		- يتم جمع الحقل quantity (أو اعتباره 1 إذا فارغ)
		- الاحتفاظ بأول صف كصف رئيسي وتحديث كميته
		- تجاهل الصفوف المدموجة الأخرى (إزالتها)
		يُنفذ قبل إعادة الحساب لتنعكس القيم في التسعير.
		"""
		try:
			if not hasattr(self, 'selected_services_table') or not self.selected_services_table:
				return
			service_map = {}
			order = []  # للمحافظة على ترتيب الظهور الأول
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
					# لو لم تُحدد كمية اعتبرها 1 (اختيار خدمة يعني ساعة واحدة مبدئياً)
					qty = 1.0
				if service not in service_map:
					service_map[service] = row
					order.append(service)
					# مهيأة بالكمية الحالية (أول مرة)
					row.quantity = qty
				else:
					# دمج في الصف الأصلي
					existing = service_map[service]
					try:
						existing_qty = float(getattr(existing, 'quantity', 0) or 0)
					except Exception:
						existing_qty = 0.0
					existing.quantity = existing_qty + qty
			# إعادة بناء القائمة بالترتيب الأصلي بدون التكرارات
			merged_rows = [service_map[s] for s in order]
			# استبدال الجدول كاملاً
			self.set('selected_services_table', merged_rows)
		except Exception as e:
			frappe.log_error(f"deduplicate_selected_services_failed: {str(e)}")

	def _deduplicate_package_services(self):
		"""دمج الصفوف المكررة لنفس الخدمة داخل package_services_table (خدمات الباقة):
		- يجمع الكمية
		- يجمع الخصم photographer_discount_amount
		- يعيد حساب amount على أساس base_price * quantity - discount
		ينفذ قبل التجميع الكلي لأسعار الباقة لتفادي التكرار و تضخيم المجموع.
		"""
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
					# جمع الخصومات
					try:
						existing.photographer_discount_amount = float(getattr(existing, 'photographer_discount_amount', 0) or 0) + photographer_discount_amount
					except Exception:
						pass
			# إعادة حساب amount لكل صف مدموج
			for service_code in order:
				row = service_map[service_code]
				bp = float(getattr(row, 'base_price', 0) or 0)
				q = float(getattr(row, 'quantity', 1) or 1)
				discount = float(getattr(row, 'photographer_discount_amount', 0) or 0)
				line_base = bp * q
				row.amount = max(line_base - discount, 0)
			merged_rows = [service_map[s] for s in order]
			self.set('package_services_table', merged_rows)
		except Exception as e:
			frappe.log_error(f"deduplicate_package_services_failed: {str(e)}")

	def _build_service_rows(self, ctx):
		"""Populate pricing related fields on service rows (selected_services_table & booking_service_items)."""
		# Process selected_services_table (primary for pricing now)
		if self.booking_type != 'Service':
			return
		discount_pct = ctx["discount_pct"] if ctx["discount_pct"] > 0 else 0
		allowed = ctx["allowed_services"]
		if hasattr(self, 'selected_services_table') and self.selected_services_table:
			for row in self.selected_services_table:
				if not getattr(row, 'service', None):
					continue
				base_price = 0
				try:
					base_price = float(frappe.db.get_value("Service", row.service, "price") or 0)
				except Exception:
					base_price = 0
				row.service_price = base_price
				applied_pct = discount_pct if (discount_pct > 0 and row.service in allowed) else 0
				row.discounted_price = base_price * (1 - applied_pct/100.0) if applied_pct else base_price
				qty = float(getattr(row, 'quantity', 1) or 1)
				row.total_amount = qty * row.discounted_price

		# Keep legacy booking_service_items updated (mirror) if exists
		if hasattr(self, 'booking_service_items') and self.booking_service_items:
			for row in self.booking_service_items:
				if not getattr(row, 'service', None):
					continue
				base_price = 0
				try:
					base_price = float(frappe.db.get_value("Service", row.service, "price") or 0)
				except Exception:
					base_price = 0
				row.service_price = base_price
				applied_pct = discount_pct if (discount_pct > 0 and row.service in allowed) else 0
				row.discounted_price = base_price * (1 - applied_pct/100.0) if applied_pct else base_price
				qty = float(getattr(row, 'quantity', 1) or 1)
				row.total_amount = qty * row.discounted_price

	def _aggregate_service_totals(self):
		if self.booking_type != 'Service':
			return
		base_total = 0.0
		final_total = 0.0
		if hasattr(self, 'selected_services_table') and self.selected_services_table:
			for row in self.selected_services_table:
				price = float(getattr(row, 'service_price', 0) or 0)
				qty = float(getattr(row, 'quantity', 1) or 1)
				base_total += price * qty
				final_total += float(getattr(row, 'total_amount', 0) or 0)
		self.base_amount = round(base_total, 2)
		self.total_amount = round(final_total, 2)

	def _build_package_rows(self, ctx):
		if self.booking_type != 'Package' or not getattr(self, 'package', None):
			return
		# Reuse existing fetch if table empty; otherwise adjust discount only
		if not getattr(self, 'package_services_table', None):
			self.populate_package_services()
		
		discount_pct = ctx["discount_pct"] if ctx["discount_pct"] > 0 else 0
		allowed = ctx["allowed_services"]
		photographer = getattr(self, 'photographer', None)
		photographer_b2b = getattr(self, 'photographer_b2b', False)
		
		# جلب بيانات المصور إذا كان B2B مفعل
		photographer_services = {}
		if photographer and photographer_b2b and discount_pct > 0:
			try:
				photographer_doc = frappe.get_doc('Photographer', photographer)
				if photographer_doc.get('b2b'):
					for ps in photographer_doc.get('services', []):
						photographer_services[ps.service] = {
							'discounted_price': flt(ps.get('discounted_price') or 0),
							'base_price': flt(ps.get('base_price') or 0)
						}
			except Exception as e:
				frappe.logger().error(f"خطأ في جلب خدمات المصور: {str(e)}")
		
		for row in (self.package_services_table or []):
			service_name = getattr(row, 'service', None)
			base_price = float(getattr(row, 'base_price', 0) or getattr(row, 'package_price', 0) or 0)
			row.base_price = base_price
			qty = float(getattr(row, 'quantity', 1) or 1)
			
			# Preserve the mandatory flag (أجباري) - don't overwrite it
			# This field is set when package services are first populated from Package
			
			# حساب السعر بعد خصم المصور
			photographer_discounted_rate = base_price
			applied_discount_amount = 0
			
			if service_name in photographer_services:
				# استخدام السعر المخصوم من المصور إذا كان موجوداً
				if photographer_services[service_name]['discounted_price'] > 0:
					photographer_discounted_rate = photographer_services[service_name]['discounted_price']
					applied_discount_amount = (base_price - photographer_discounted_rate) * qty
				# وإلا استخدام نسبة الخصم العامة
				elif discount_pct > 0 and service_name in allowed:
					photographer_discounted_rate = base_price * (1 - discount_pct / 100.0)
					applied_discount_amount = (base_price - photographer_discounted_rate) * qty
			
			# تعيين القيم
			row.photographer_discount_amount = photographer_discounted_rate  # السعر بعد الخصم
			row.amount = photographer_discounted_rate * qty  # المبلغ الإجمالي
			
			frappe.logger().debug(
				f"📊 خدمة {service_name}: base={base_price}, "
				f"discounted={photographer_discounted_rate}, qty={qty}, amount={row.amount}"
			)

	def _aggregate_package_totals(self):
		if self.booking_type != 'Package':
			return
		base_total = 0.0
		final_total = 0.0
		for row in (self.package_services_table or []):
			qty = float(getattr(row, 'quantity', 1) or 1)
			bp = float(getattr(row, 'base_price', 0) or 0)
			base_total += bp * qty
			final_total += float(getattr(row, 'amount', 0) or 0)
		self.base_amount_package = round(base_total, 2)
		self.total_amount_package = round(final_total, 2)

	def _compute_deposit(self):
		"""Compute deposit based on percentage, then enforce minimum booking amount from General Settings.
		General Settings expected field names (first match wins):
		- 'الحد الأدنى لمبلغ الحجز'
		- 'minimum_booking_amount'
		- 'min_booking_amount'

		Rules:
		1. deposit_amount = round( basis * deposit_percentage / 100 )
		2. If a minimum booking amount setting exists and deposit_amount < minimum -> raise deposit to minimum (capped at basis)
		3. Never exceed basis (total)
		"""
		try:
			pct = float(getattr(self, 'deposit_percentage', 0) or 0)
			pct = max(0, min(pct, 100))
			if self.booking_type == 'Service':
				basis = float(getattr(self, 'total_amount', 0) or 0)
			else:
				basis = float(getattr(self, 'total_amount_package', 0) or 0)
			computed = round(basis * pct / 100.0, 2)
			# لا يتجاوز الإجمالي
			if computed > basis:
				computed = basis

			# جلب الحد الأدنى لمبلغ الحجز من General Settings (إن وجد)
			min_deposit = 0.0
			try:
				if frappe.db.exists('DocType', 'General Settings'):
					settings = frappe.db.get_singles_dict('General Settings') or {}
					for key in ('الحد الأدنى لمبلغ الحجز', 'minimum_booking_amount', 'min_booking_amount'):
						if key in settings and settings.get(key) not in (None, ""):
							min_deposit = float(settings.get(key) or 0)
							break
			except Exception:
				min_deposit = 0.0

			if min_deposit > 0 and basis > 0:
				# ارفع العربون للحد الأدنى إن كان أقل (مع سقف الإجمالي)
				if computed < min_deposit:
					computed = min(min_deposit, basis)

			self.deposit_amount = computed
		except Exception:
			frappe.log_error("deposit_compute_failed")

	def _validate_paid_vs_deposit(self):
		"""تحقق إلزامي قبل الحفظ:
		1. يجب أن يكون paid_amount >= deposit_amount (أو يساوي كامل المبلغ الإجمالي).
		2. لو يوجد حد أدنى (General Settings) للمبلغ (الحد الأدنى لمبلغ الحجز) وتجاوزناه في deposit_amount فسنلتزم به.
		3. في حال لم يتم احتساب الإجمالي بعد، نتجاوز التحقق.
		"""
		try:
			paid = float(getattr(self, 'paid_amount', 0) or 0)
			deposit = float(getattr(self, 'deposit_amount', 0) or 0)
			if self.booking_type == 'Service':
				full_total = float(getattr(self, 'total_amount', 0) or 0)
			else:
				full_total = float(getattr(self, 'total_amount_package', 0) or 0)
			if full_total <= 0:
				return
			if deposit > full_total:
				deposit = full_total
			# التحقق الأساسي
			if deposit > 0 and paid < deposit and paid < full_total:
				frappe.throw(_(f"المبلغ المدفوع ({paid}) أقل من العربون المطلوب ({deposit}). يجب دفع العربون أو المبلغ الكامل ({full_total})."))
		except Exception as e:
			frappe.log_error(f"validate_paid_vs_deposit_failed: {str(e)}")

	def _auto_set_payment_status(self):
		try:
			paid = float(getattr(self, 'paid_amount', 0) or 0)
			if self.booking_type == 'Service':
				full_total = float(getattr(self, 'total_amount', 0) or 0)
			else:
				full_total = float(getattr(self, 'total_amount_package', 0) or 0)
			if full_total <= 0:
				return
			if paid >= full_total and full_total > 0:
				self.payment_status = 'Paid'
			elif paid > 0:
				self.payment_status = 'Partially Paid'
			else:
				# keep existing or set default
				if not getattr(self, 'payment_status', None):
					self.payment_status = 'Confirmed'
		except Exception:
			pass

# -------------- Public API Helpers -------------- #

@frappe.whitelist()
def recalc_booking_deposit(booking: str):
	"""Recompute pricing & deposit & payment status for a booking and save it."""
	if not booking:
		frappe.throw('Booking required')
	doc = frappe.get_doc('Booking', booking)
	doc.recompute_pricing()
	doc.save()
	return {
		'booking': booking,
		'deposit_amount': doc.deposit_amount,
		'payment_status': doc.payment_status
	}

@frappe.whitelist()
def debug_deposit_calculation(booking: str):
	"""Debug deposit calculation showing step by step breakdown"""
	if not booking:
		frappe.throw('Booking required')
	
	doc = frappe.get_doc('Booking', booking)
	
	# Get deposit percentage from settings
	settings = frappe.db.get_singles_dict('General Settings') if frappe.db.exists('DocType', 'General Settings') else {}
	deposit_pct = None
	for key in ('نسبة العربون (%)', 'deposit_percentage', 'نسبة_العربون_%'):
		if key in settings and settings.get(key) is not None:
			deposit_pct = float(settings.get(key))
			break
	
	if deposit_pct is None:
		deposit_pct = 30.0  # fallback
	
	# Get the basis amount
	if doc.booking_type == 'Service':
		basis_amount = float(getattr(doc, 'total_amount', 0) or 0)
		basis_field = 'total_amount'
	else:
		basis_amount = float(getattr(doc, 'total_amount_package', 0) or 0)
		basis_field = 'total_amount_package'
	
	# Calculate deposit step by step
	step1 = basis_amount * deposit_pct  # المبلغ × النسبة
	step2 = step1 / 100.0  # القسمة على 100
	final_deposit = round(step2, 2)  # التقريب
	
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
		"""حساب إجماليات الباقة باستخدام الأسعار المحسوبة مسبقاً"""
		if self.booking_type != "Package":
			return
		
		try:
			# حساب الإجماليات من جدول خدمات الباقة
			base_total = 0
			final_total = 0
			
			if hasattr(self, 'package_services_table') and self.package_services_table:
				for row in self.package_services_table:
					# حساب السعر الأساسي
					base_amount = flt(getattr(row, 'base_price', 0) or 0) * flt(getattr(row, 'quantity', 1) or 1)
					base_total += base_amount
					
					# استخدام المبلغ المحسوب (الذي يتضمن خصم المصور إن وُجد)
					final_total += flt(getattr(row, 'amount', 0) or 0)
			else:
				# إذا لم توجد خدمات، احسب من سعر الباقة مباشرة
				if getattr(self, 'package', None):
					try:
						package_doc = frappe.get_doc("Package", self.package)
						if package_doc.final_price:
							base_total = flt(package_doc.final_price)
							final_total = base_total
					except Exception:
						pass
			
			# تحديث الحقول
			self.base_amount_package = base_total
			self.total_amount_package = final_total
			
		except Exception as e:
			frappe.log_error(f"Error calculating package totals: {str(e)}")
		
		# fallback افتراضي إن ظل فارغ
		if getattr(self, 'deposit_percentage', None) in (None, ""):
			self.deposit_percentage = 30
	def calculate_service_totals(self):
		"""Calculate totals for service booking items based on photographer discount"""
		if self.booking_type == "Service" and hasattr(self, 'selected_services_table'):
			# اجلب خصم المصور فقط إن كان B2B
			photographer_discount_pct = 0
			allowed_services = set()
			if getattr(self, 'photographer_b2b', False) and getattr(self, 'photographer', None):
				try:
					photographer_discount_pct = float(frappe.db.get_value("Photographer", self.photographer, "discount_percentage") or 0)
					# اجلب الخدمات المربوطة بالمصور (Photographer Service)
					photographer_services = frappe.get_all("Photographer Service", filters={"parent": self.photographer, "is_active": 1}, fields=["service"])
					allowed_services = {ps.service for ps in photographer_services}
				except Exception:
					photographer_discount_pct = 0
			else:
				photographer_discount_pct = 0
			# اجمالي قبل الخصم
			base_total = 0
			# اجمالي بعد الخصم
			total_booking_amount = 0
			for service_item in self.selected_services_table:
				if not getattr(service_item, 'service', None):
					continue
				try:
					base_price = float(frappe.db.get_value("Service", service_item.service, "price") or 0)
				except Exception:
					base_price = 0
				service_item.pre_discount_price = base_price
				service_item.service_price = base_price
				discounted_price = base_price
				# طبق الخصم فقط إذا كانت الخدمة ضمن خدمات المصور
				if photographer_discount_pct > 0 and service_item.service in allowed_services:
					discounted_price = base_price * (1 - photographer_discount_pct / 100.0)
				service_item.discounted_price = discounted_price
				quantity = float(getattr(service_item, 'quantity', 1) or 1)
				# اجمالي قبل الخصم
				base_total += quantity * base_price
				if discounted_price > 0 and discounted_price != base_price:
					service_item.total_amount = quantity * discounted_price
				else:
					service_item.total_amount = quantity * base_price
				total_booking_amount += service_item.total_amount
			self.base_amount = base_total
			self.total_amount = total_booking_amount

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
	def validate_dates(self):
		from frappe.utils import getdate, nowdate
		today = getdate(nowdate())
		# Service (single date) logic stays strict
		if self.booking_type == 'Service' and getattr(self, 'booking_date', None):
			if getdate(self.booking_date) < today:
				frappe.throw("لا يمكن إنشاء حجز في تاريخ سابق")
		# Package: evaluate child dates if present
		if self.booking_type == 'Package':
			future_exists = False
			past_rows = []
			for row in (getattr(self, 'package_booking_dates', None) or []):
				if getattr(row, 'booking_date', None):
					row_date = getdate(row.booking_date)
					if row_date >= today:
						future_exists = True
					else:
						past_rows.append(row.booking_date)
			# If no future dates at all -> block
			if (getattr(self, 'package_booking_dates', None) and not future_exists):
				frappe.throw("لا يمكن إنشاء حجز كل تواريخه في الماضي")
			# If mixture -> warn (non blocking)
			if past_rows and future_exists:
				frappe.msgprint(
					"تحذير: بعض التواريخ في الماضي ولن يتم اعتبارها: " + ", ".join(past_rows),
					indicator='orange'
				)

	def validate_availability(self):
		if hasattr(self, 'start_time') and hasattr(self, 'end_time') and getattr(self, 'booking_date', None) and getattr(self, 'photographer', None):
			# Check for overlapping bookings
			existing_bookings = frappe.get_all(
				"Booking",
				filters=[
					["booking_date", "=", self.booking_date],
					["photographer", "=", self.photographer],
					["status", "not in", ["Cancelled"]],
					["name", "!=", self.name or "new"],
					# Check for time overlap: existing start_time < our end_time AND existing end_time > our start_time
					["start_time", "<", self.end_time],
					["end_time", ">", self.start_time]
				]
			)
			if existing_bookings:
				frappe.throw("هذا الوقت محجوز بالفعل. الرجاء اختيار وقت آخر.")

	def calculate_booking_datetime(self):
		if getattr(self, 'booking_date', None) and hasattr(self, 'booking_time') and getattr(self, 'booking_time', None):
			booking_datetime = f"{self.booking_date} {self.booking_time}:00"
			self.booking_datetime = booking_datetime
			if hasattr(self, 'duration') and getattr(self, 'duration', None):
				end_datetime = frappe.utils.add_to_date(booking_datetime, minutes=self.duration)
				self.booking_end_datetime = end_datetime

	# ------------------------ Events ------------------------ #
	def on_update(self):
		if getattr(self, 'status', None) == "Confirmed" and not getattr(self, 'confirmation_sent', False):
			self.send_confirmation()
			self.confirmation_sent = 1

	# ------------------------ Communications ------------------------ #
	def send_confirmation(self):
		if hasattr(self, 'client') and getattr(self, 'client', None):
			client_email = frappe.db.get_value("Client", self.client, "email_id")
			if client_email:
				frappe.sendmail(
					recipients=[client_email],
					subject="تأكيد الحجز - {0}".format(self.name),
					message="""<p>مرحباً،</p>
					<p>تم تأكيد حجزك رقم {0} في تاريخ {1} الساعة {2}.</p>
					<p>نشكرك على اختيار Re Studio.</p>
					""".format(self.name, self.booking_date, getattr(self, 'start_time', ''))
				)

	# ------------------------ Package Services ------------------------ #
	def populate_package_services(self):
		"""Populate package services table when package is selected with photographer discount"""
		if self.booking_type == "Package" and getattr(self, 'package', None):
			self.package_services_table = []
			# Get package document and its services
			package_doc = frappe.get_doc("Package", self.package)
			package_services = package_doc.package_services or []
			base_sum = 0.0
			discounted_sum = 0.0
			
			# تحديد ما إذا كان هناك خصم للمصور
			photographer_discount = 0
			photographer_services = {}  # تخزين بيانات الخدمات من جدول المصور
			
			if getattr(self, 'photographer', None) and getattr(self, 'photographer_b2b', False):
				try:
					photographer_doc = frappe.get_doc('Photographer', self.photographer)
					photographer_discount = flt(photographer_doc.discount_percentage or 0)
					# جلب الخدمات مع السعر المخصوم من جدول خدمات المصور
					for ps in photographer_doc.get('services', []):
						photographer_services[ps.service] = {
							'discounted_price': flt(ps.get('discounted_price') or 0),
							'base_price': flt(ps.get('base_price') or 0),
							'allow_discount': ps.get('allow_discount', 0)
						}
				except Exception as e:
					frappe.log_error(f"Error fetching photographer discount: {str(e)}")
			
			for service in package_services:
				qty = float(service.quantity or 1)
				# Get base price from Service table
				base_price = 0
				try:
					base_price = flt(frappe.db.get_value("Service", service.service, "price") or 0)
				except Exception:
					base_price = 0
				
				# Use package price as default, or base price if package price is 0
				package_price = flt(getattr(service, 'package_price', 0) or 0)
				hourly_rate = package_price if package_price > 0 else base_price
				
				# تطبيق خصم المصور - الأولوية للسعر المخصوم من جدول المصور
				photographer_discounted_rate = hourly_rate
				
				if service.service in photographer_services:
					# الأولوية الأولى: استخدام السعر المخصوم (discounted_price) من جدول المصور
					if photographer_services[service.service]['discounted_price'] > 0:
						photographer_discounted_rate = photographer_services[service.service]['discounted_price']
					# الأولوية الثانية: استخدام نسبة الخصم العامة إذا كانت الخدمة مسموح بخصمها
					elif photographer_discount > 0 and photographer_services[service.service]['allow_discount']:
						photographer_discounted_rate = hourly_rate * (1 - photographer_discount / 100)
				
				# حساب المبلغ الإجمالي = الكمية × سعر الساعة (بعد الخصم إن وُجد)
				amt = qty * photographer_discounted_rate
				
				# Get is_required field from Package Service Item
				is_mandatory = getattr(service, 'is_required', 0) or 0
				
				self.append("package_services_table", {
					"service": service.service,
					"service_name": getattr(service, 'service_name', '') or service.service,
					"quantity": qty,
					"base_price": base_price,
					"package_price": hourly_rate,  # سعر الساعة داخل الباقة (before photographer discount)
					"photographer_discount_amount": photographer_discounted_rate,  # السعر بعد خصم المصور (per hour)
					"amount": amt,  # المبلغ الإجمالي
					"أجباري": is_mandatory  # Set mandatory field from Package Service Item
				})
				base_sum += qty * base_price
				discounted_sum += amt
			
			# تخزين الإجماليات في الحقلين الموحدين
			self.base_amount_package = round(base_sum, 2)
			self.total_amount_package = round(discounted_sum, 2)
			# تحديث العربون بناءً على هذه القيم لاحقاً في calculate_booking_total

@frappe.whitelist()
def recalculate_booking_totals(booking_name):
	"""Recalculate pricing for an existing (already saved) booking."""
	# Avoid processing unsaved temp names
	if not booking_name or booking_name.startswith("new-"):
		return {"error": "unsaved", "message": _("يجب حفظ الحجز أولاً قبل إعادة الحساب")}
	booking = frappe.get_doc("Booking", booking_name)
	booking.recalculate_service_pricing()
	booking.calculate_booking_total()
	booking.save()
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

@frappe.whitelist()
def fetch_package_services_for_booking(package, photographer=None, photographer_b2b=0):
	"""جلب خدمات الباقة مع حساب خصم المصور"""
	try:
		if not package:
			return {"error": "لم يتم تحديد الباقة"}
		
		# جلب معلومات الباقة
		package_doc = frappe.get_doc("Package", package)
		hourly_rate = 0
		if package_doc.total_hours and package_doc.final_price:
			hourly_rate = flt(package_doc.final_price) / flt(package_doc.total_hours)
		
		# جلب الخدمات المسموح بها للمصور (لو B2B مفعّل)
		allowed_services = set()
		if photographer_b2b and photographer:
			try:
				photographer_services = frappe.get_all(
					"Photographer Service",
					filters={"parent": photographer, "is_active": 1},
					fields=["service"]
				)
				allowed_services = {ps.service for ps in photographer_services}
			except Exception:
				allowed_services = set()

		# نسبة الخصم للمصور (مرة واحدة)
		photographer_discount_pct = 0
		if photographer_b2b and photographer:
			try:
				photographer_discount_pct = flt(frappe.db.get_value("Photographer", photographer, "discount_percentage") or 0)
			except Exception:
				photographer_discount_pct = 0
		
		# جلب خدمات الباقة
		package_services = frappe.get_all(
			"Package Service Item",
			filters={"parent": package},
			fields=["service", "quantity", "price"]
		)
		
		rows = []
		for svc in package_services:
			qty = flt(svc.quantity or 1)
			# تحديد السعر الوحدي المستخدم (سعر الساعة داخل الباقة أو السعر الأصلي)
			unit_price = hourly_rate if hourly_rate > 0 else flt(svc.price or 0)
			base_amount = unit_price * qty
			photographer_discount_amount = 0
			final_amount = base_amount
			if photographer_discount_pct > 0 and photographer_b2b and svc.service in allowed_services:
				photographer_discount_amount = base_amount * (photographer_discount_pct / 100.0)
				final_amount = base_amount - photographer_discount_amount
				if final_amount < 0:
					final_amount = 0
			# اسم الخدمة
			try:
				service_name = frappe.db.get_value("Service", svc.service, "service_name_en")
			except Exception:
				service_name = svc.service
			rows.append({
				"service": svc.service,
				"service_name": service_name or svc.service,
				"quantity": qty,
				"base_price": flt(svc.price or 0),
				"package_price": unit_price,
				"service_price": unit_price,
				"amount": final_amount,
				"photographer_discount_amount": photographer_discount_amount
			})
		
		return {"rows": rows}
		
	except Exception as e:
		frappe.log_error(f"Error fetching package services: {str(e)}")
		return {"error": str(e)}

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
		# Collect allowed services for the photographer (only if B2B enabled)
		allowed_services = set()
		if photographer and photographer_b2b:
			try:
				photographer_services = frappe.get_all(
					"Photographer Service",
					filters={"parent": photographer, "is_active": 1},
					fields=["service"]
				)
				allowed_services = {ps.service for ps in photographer_services}
			except Exception:
				allowed_services = set()

		# Pre-fetch photographer discount percentage once
		discount_percentage = 0
		if photographer_b2b and photographer:
			try:
				discount_percentage = flt(frappe.db.get_value("Photographer", photographer, "discount_percentage") or 0)
			except Exception:
				discount_percentage = 0

		for service in package_services:
			qty = flt(service.quantity or 1)
			# Decide the effective base line amount (use total_amount if present, else package_price*qty, else base_price*qty)
			line_base_single = flt(service.package_price or service.base_price or 0)
			if service.total_amount and service.total_amount > 0:
				line_base_total = flt(service.total_amount)
			else:
				line_base_total = line_base_single * qty

			photographer_discount_amount = 0
			final_amount = line_base_total

			# Apply discount only if: B2B enabled, service allowed for photographer, discount_percentage > 0
			if discount_percentage > 0 and photographer_b2b and photographer and service.service in allowed_services:
				photographer_discount_amount = (line_base_total * discount_percentage) / 100.0
				final_amount = line_base_total - photographer_discount_amount
				if final_amount < 0:
					final_amount = 0

			processed_services.append({
				"service": service.service,
				"service_name": service.service_name,
				"quantity": qty,
				"base_price": flt(service.base_price or 0),
				"package_price": flt(service.package_price or 0),
				"amount": final_amount,
				"photographer_discount_amount": photographer_discount_amount
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
								"service_name": service_data["service_name"],
								"quantity": service_data["quantity"],
								"base_price": service_data["base_price"],
								"package_price": service_data["package_price"],
								"amount": service_data["amount"],
								"photographer_discount_amount": service_data["photographer_discount_amount"]
							})
						
						# Save the booking with updated services
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
			photographer_discounted_rate = hourly_rate
			
			if service_name in photographer_services:
				# الأولوية الأولى: استخدام السعر المخصوم (discounted_price) من جدول المصور
				if photographer_services[service_name]['discounted_price'] > 0:
					photographer_discounted_rate = photographer_services[service_name]['discounted_price']
				# الأولوية الثانية: استخدام نسبة الخصم العامة إذا كانت الخدمة مسموح بخصمها
				elif photographer_discount_pct > 0 and photographer_services[service_name]['allow_discount']:
					photographer_discounted_rate = hourly_rate * (1 - photographer_discount_pct / 100)
			
			# حساب المبلغ الإجمالي
			amount = quantity * photographer_discounted_rate
			
			# Get is_required field from Package Service Item
			is_mandatory = service_row.get('is_required', 0) or 0
			
			services.append({
				"service": service_name,
				"service_name": service_row.get("service_name", ""),
				"quantity": quantity,
				"base_price": base_price,
				"package_price": hourly_rate,
				"photographer_discount_amount": photographer_discounted_rate,
				"amount": amount,
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

