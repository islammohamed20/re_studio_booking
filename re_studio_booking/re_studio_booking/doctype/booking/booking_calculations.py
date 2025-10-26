# Copyright (c) 2023, MASAR TEAM and contributors
# For license information, please see license.txt

"""
Booking Calculation Functions
جميع دوال الحسابات والمبالغ الخاصة بالحجوزات
"""

import frappe
from frappe import _
from frappe.utils import flt, time_diff_in_seconds
from datetime import datetime, timedelta


# ============ Deposit Calculations ============

def calculate_deposit_amount(booking_doc):
	"""
	حساب مبلغ العربون بشكل شامل
	
	القواعد:
	1. حساب العربون من deposit_percentage × المبلغ الإجمالي
	2. تطبيق الحد الأدنى (minimum_booking_amount) من General Settings
	3. عدم تجاوز المبلغ الإجمالي
	4. احترام القيمة المُدخلة يدوياً
	
	Args:
		booking_doc: مستند الحجز
	"""
	try:
		# 1. تحديد المبلغ الأساسي للحساب (basis)
		basis = 0.0
		if booking_doc.booking_type == 'Service':
			basis = float(getattr(booking_doc, 'total_amount', 0) or 0)
		elif booking_doc.booking_type == 'Package':
			basis = float(getattr(booking_doc, 'total_amount_package', 0) or 0)
		
		# إذا لم يكن هناك مبلغ، لا نحسب عربون
		if basis <= 0:
			booking_doc.deposit_amount = 0
			return
		
		# 2. الحصول على نسبة العربون (deposit_percentage)
		deposit_percentage = float(getattr(booking_doc, 'deposit_percentage', 0) or 0)
		
		# التأكد من أن النسبة بين 0-100
		deposit_percentage = max(0, min(deposit_percentage, 100))
		
		# إذا لم تكن النسبة محددة، استخدم القيمة الافتراضية
		if deposit_percentage <= 0:
			deposit_percentage = 30  # افتراضي 30%
			try:
				general_settings = frappe.get_single('General Settings')
				if hasattr(general_settings, 'default_deposit_percentage') and general_settings.default_deposit_percentage:
					deposit_percentage = float(general_settings.default_deposit_percentage)
			except:
				pass
		
		# 3. حساب العربون من النسبة
		computed_deposit = round(basis * deposit_percentage / 100.0, 2)
		
		# 4. التأكد من عدم تجاوز المبلغ الإجمالي
		if computed_deposit > basis:
			computed_deposit = basis
		
		# 5. جلب الحد الأدنى لمبلغ الحجز من General Settings
		min_deposit = 0.0
		try:
			if frappe.db.exists('DocType', 'General Settings'):
				settings = frappe.db.get_singles_dict('General Settings') or {}
				# البحث في أسماء مختلفة للحقل
				for key in ('الحد الأدنى لمبلغ الحجز', 'minimum_booking_amount', 'min_booking_amount'):
					if key in settings and settings.get(key) not in (None, ""):
						min_deposit = float(settings.get(key) or 0)
						break
		except Exception as e:
			frappe.logger().debug(f"خطأ في جلب الحد الأدنى: {str(e)}")
			min_deposit = 0.0
		
		# 6. تطبيق الحد الأدنى (إذا كان العربون المحسوب أقل)
		if min_deposit > 0:
			if computed_deposit < min_deposit:
				# رفع العربون للحد الأدنى (لكن بحد أقصى = المبلغ الإجمالي)
				computed_deposit = min(min_deposit, basis)
		
		# 7. تعيين مبلغ العربون النهائي
		booking_doc.deposit_amount = computed_deposit
		
		# 8. تسجيل معلومات التشخيص
		frappe.logger().info(
			f"حساب العربون للحجز {booking_doc.name}: "
			f"نوع={booking_doc.booking_type}, "
			f"المبلغ={basis}, "
			f"النسبة={deposit_percentage}%, "
			f"الحد_الأدنى={min_deposit}, "
			f"العربون={computed_deposit}"
		)
		
	except Exception as e:
		frappe.logger().error(f"خطأ في حساب العربون: {str(e)}")
		frappe.log_error(f"deposit_calculation_failed: {str(e)}")
		# قيمة افتراضية في حالة الخطأ (30% من الإجمالي)
		try:
			if booking_doc.booking_type == 'Service':
				booking_doc.deposit_amount = round(float(getattr(booking_doc, 'total_amount', 0) or 0) * 0.3, 2)
			else:
				booking_doc.deposit_amount = round(float(getattr(booking_doc, 'total_amount_package', 0) or 0) * 0.3, 2)
		except:
			booking_doc.deposit_amount = 0


def set_default_deposit_percentage(booking_doc):
	"""
	تعيين نسبة العربون الافتراضية
	
	Args:
		booking_doc: مستند الحجز
	"""
	if getattr(booking_doc, 'deposit_percentage', None) not in (None, ""):
		return
	try:
		settings = frappe.db.get_singles_dict('General Settings') if frappe.db.exists('DocType', 'General Settings') else {}
		val = None
		for key in ('نسبة العربون (%)', 'deposit_percentage', 'نسبة_العربون_%'):
			if key in settings and settings.get(key) is not None:
				val = settings.get(key)
				break
		if val is not None:
			booking_doc.deposit_percentage = flt(val)
	except Exception:
		pass
	# fallback النهائي
	if getattr(booking_doc, 'deposit_percentage', None) in (None, ""):
		booking_doc.deposit_percentage = 30


# ============ Time Calculations ============

def calculate_booking_datetime(booking_doc):
	"""
	حساب تاريخ ووقت الحجز - مطلوب لـ Gantt view
	
	Args:
		booking_doc: مستند الحجز
	"""
	# For Service bookings: combine booking_date + start_time
	if booking_doc.booking_type == 'Service' and getattr(booking_doc, 'booking_date', None) and getattr(booking_doc, 'start_time', None):
		try:
			booking_datetime = f"{booking_doc.booking_date} {booking_doc.start_time}"
			booking_doc.booking_datetime = booking_datetime
		except Exception:
			pass
	
	# For Package bookings: use booking_date only (as packages can have multiple dates)
	elif booking_doc.booking_type == 'Package' and getattr(booking_doc, 'booking_date', None):
		try:
			booking_datetime = f"{booking_doc.booking_date} 00:00:00"
			booking_doc.booking_datetime = booking_datetime
		except Exception:
			pass


def calculate_time_usage(booking_doc):
	"""
	حساب الوقت المستخدم
	
	Args:
		booking_doc: مستند الحجز
	"""
	if booking_doc.booking_type == 'Service':
		if getattr(booking_doc, 'start_time', None) and getattr(booking_doc, 'end_time', None):
			try:
				seconds = time_diff_in_seconds(booking_doc.end_time, booking_doc.start_time)
				if seconds < 0:
					seconds = 86400 + seconds  # Handle next-day booking
				hours = seconds / 3600.0
				booking_doc.total_booked_hours = round(hours, 2)
				
				# ترحيل إجمالي الساعات إلى جدول الخدمات المختارة
				# (فقط للخدمات الغير مرنة - الخدمات المرنة تحتفظ بكميتها الخاصة)
				if hasattr(booking_doc, 'selected_services_table') and booking_doc.selected_services_table:
					# جلب is_flexible_service لجميع الخدمات مرة واحدة لتحسين الأداء
					service_names = [getattr(row, 'service', None) for row in booking_doc.selected_services_table if getattr(row, 'service', None)]
					flexible_services = {}
					if service_names:
						flexible_data = frappe.get_all('Service', 
							filters={'name': ['in', service_names]},
							fields=['name', 'is_flexible_service']
						)
						flexible_services = {s.name: s.is_flexible_service for s in flexible_data}
					
					# تحديث الكميات
					for row in booking_doc.selected_services_table:
						service_name = getattr(row, 'service', None)
						if service_name:
							is_flexible = flexible_services.get(service_name, 0)
							# فقط تحديث الكمية للخدمات غير المرنة
							if not is_flexible:
								row.quantity = booking_doc.total_booked_hours
			except Exception:
				pass


def compute_package_hours_usage(booking_doc):
	"""
	حساب الساعات المستخدمة والمتبقية للباقة
	
	Args:
		booking_doc: مستند الحجز
	"""
	try:
		if booking_doc.booking_type != 'Package':
			return
		
		# Determine total hours allotted by package
		package_total = 0.0
		if getattr(booking_doc, 'package', None):
			package_total = float(frappe.db.get_value('Package', booking_doc.package, 'total_hours') or 0)
		
		used = 0.0
		for row in (booking_doc.package_booking_dates or []):
			# Derive row.hours if times present
			if getattr(row, 'start_time', None) and getattr(row, 'end_time', None):
				try:
					# استخدام التاريخ من الصف (أو تاريخ الحجز كاحتياط)
					booking_date = getattr(row, 'booking_date', None) or getattr(booking_doc, 'booking_date', None)
					
					if booking_date:
						# دمج التاريخ مع الوقت لإنشاء DateTime كامل
						start_str = str(booking_date) + ' ' + str(row.start_time)
						end_str = str(booking_date) + ' ' + str(row.end_time)
						
						fmt = '%Y-%m-%d %H:%M:%S'
						start_dt = datetime.strptime(start_str, fmt)
						end_dt = datetime.strptime(end_str, fmt)
						
						# إذا كان end_dt أصغر من start_dt، نضيف يوماً كاملاً
						if end_dt <= start_dt:
							end_dt += timedelta(days=1)
						
						diff = end_dt - start_dt
						row_hours = diff.total_seconds() / 3600.0
						row.hours = round(row_hours, 2)
					else:
						frappe.logger().warn(
							f"لم يتم تحديد تاريخ حجز للصف {row.idx} في {booking_doc.name}"
						)
				except Exception as e:
					frappe.logger().error(f"خطأ في تحليل الأوقات: {str(e)}")
			
			used += flt(getattr(row, 'hours', 0))
		
		booking_doc.used_hours = round(used, 2)
		booking_doc.remaining_hours = round(package_total - used, 2) if package_total > 0 else 0
		
	except Exception as e:
		frappe.logger().error(f"خطأ في compute_package_hours_usage: {str(e)}")
		import traceback
		frappe.logger().error(traceback.format_exc())


# ============ Service Totals Calculations ============

def calculate_service_totals(booking_doc):
	"""
	حساب إجماليات حجز الخدمات
	
	Args:
		booking_doc: مستند الحجز
	"""
	if booking_doc.booking_type != "Service" or not hasattr(booking_doc, 'selected_services_table'):
		return
	
	# اجلب خصم المصور فقط إن كان B2B
	photographer_discount_pct = 0
	allowed_services = set()
	if getattr(booking_doc, 'photographer_b2b', False) and getattr(booking_doc, 'photographer', None):
		try:
			photographer_discount_pct = float(frappe.db.get_value("Photographer", booking_doc.photographer, "discount_percentage") or 0)
			photographer_services = frappe.get_all("Photographer Service", filters={"parent": booking_doc.photographer, "is_active": 1}, fields=["service"])
			allowed_services = {ps.service for ps in photographer_services}
		except Exception:
			photographer_discount_pct = 0
	
	base_total = 0
	total_booking_amount = 0
	
	for service_item in booking_doc.selected_services_table:
		if not getattr(service_item, 'service', None):
			continue
		try:
			base_price = float(frappe.db.get_value("Service", service_item.service, "price") or 0)
		except Exception:
			base_price = 0
		
		# تخزين الأسعار قبل وبعد الخصم لتوفيرها في الواجهات الأخرى
		service_item.pre_discount_price = base_price
		service_item.service_price = base_price
		discounted_price = base_price
		
		# طبق الخصم فقط إذا كانت الخدمة ضمن خدمات المصور
		if photographer_discount_pct > 0 and service_item.service in allowed_services:
			discounted_price = base_price * (1 - photographer_discount_pct / 100.0)
		service_item.discounted_price = discounted_price
		
		quantity = float(getattr(service_item, 'quantity', 1) or 1)
		base_total += quantity * base_price
		
		if discounted_price > 0 and discounted_price != base_price:
			service_item.total_amount = quantity * discounted_price
		else:
			service_item.total_amount = quantity * base_price
		
		total_booking_amount += service_item.total_amount
	
	booking_doc.base_amount = base_total
	booking_doc.total_amount = total_booking_amount


# ============ Package Totals Calculations ============

def calculate_package_totals(booking_doc):
	"""
	حساب إجماليات حجز الباقة
	
	Args:
		booking_doc: مستند الحجز
	"""
	if booking_doc.booking_type != 'Package':
		return
	
	# حساب إجمالي المبلغ من جدول خدمات الباقة
	base_total_package = 0
	total_after_discount_package = 0
	
	has_package_rows = hasattr(booking_doc, 'package_services_table') and booking_doc.package_services_table
	if has_package_rows:
		for service_row in booking_doc.package_services_table:
			quantity = flt(getattr(service_row, 'quantity', 0))
			
			# استخدام الحقول الصحيحة من DocType
			base_price = flt(getattr(service_row, 'base_price', 0))
			package_price = flt(getattr(service_row, 'package_price', 0))
			
			# إذا لم يكن هناك base_price، استخدم package_price كأساس
			if not base_price and package_price:
				base_price = package_price
			
			# حساب المبلغ الأساسي = الكمية × السعر الأساسي
			base_amount_row = quantity * base_price
			base_total_package += base_amount_row
			
			# حساب المبلغ النهائي = الكمية × سعر الباقة (بعد الخصم)
			final_amount_row = quantity * package_price
			total_after_discount_package += final_amount_row
			
			# تحديث amount في الصف
			service_row.amount = final_amount_row
	else:
		# fallback: استخدم سعر الباقة مباشرة إن لم يكن هناك صفوف خدمات
		package_name = getattr(booking_doc, 'package', None)
		if package_name:
			try:
				package_doc = frappe.get_doc("Package", package_name)
				if getattr(package_doc, 'final_price', None):
					base_total_package = flt(package_doc.final_price)
					total_after_discount_package = base_total_package
			except Exception:
				pass
	
	booking_doc.base_amount_package = base_total_package
	booking_doc.total_amount_package = total_after_discount_package

	# fallback افتراضي للعربون إذا ظل فارغاً بعد الحسابات السابقة
	if getattr(booking_doc, 'deposit_percentage', None) in (None, ""):
		booking_doc.deposit_percentage = 30


# ============ Unified Pricing Recompute ============

def recompute_pricing(booking_doc):
	"""
	إعادة حساب التسعير الموحد (Consolidated Flow)
	
	Args:
		booking_doc: مستند الحجز
	"""
	if booking_doc.booking_type == 'Service':
		_build_service_rows(booking_doc)
		calculate_service_totals(booking_doc)
	elif booking_doc.booking_type == 'Package':
		_build_package_rows(booking_doc)
		calculate_package_totals(booking_doc)


def _build_service_rows(booking_doc):
	"""
	بناء صفوف الخدمات لحجز الخدمات
	
	Args:
		booking_doc: مستند الحجز
	"""
	# الكود الحالي يتعامل مع selected_services_table مباشرة
	# هذه الدالة موجودة للتوافق المستقبلي
	pass


def _build_package_rows(booking_doc):
	"""
	بناء صفوف خدمات الباقة لحجز الباقة
	
	Args:
		booking_doc: مستند الحجز
	"""
	if not getattr(booking_doc, 'package', None):
		return
	
	# Get package document and its services
	package_doc = frappe.get_doc("Package", booking_doc.package)
	package_services = package_doc.package_services or []
	
	# تحديد ما إذا كان هناك خصم للمصور
	photographer_discount = 0
	photographer_services = {}
	
	if getattr(booking_doc, 'photographer', None) and getattr(booking_doc, 'photographer_b2b', False):
		try:
			photographer_doc = frappe.get_doc('Photographer', booking_doc.photographer)
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
	
	# Clear and rebuild package services table
	booking_doc.package_services_table = []
	
	for service in package_services:
		qty = float(service.quantity or 1)
		# Get base price from Service master
		base_price = 0
		try:
			base_price = flt(frappe.db.get_value("Service", service.service, "price") or 0)
		except Exception:
			base_price = 0
		
		# Use package price from Package, or base price as fallback
		initial_package_price = flt(getattr(service, 'package_price', 0) or 0)
		if initial_package_price <= 0:
			initial_package_price = base_price
		
		# تطبيق خصم المصور على package_price
		final_package_price = initial_package_price
		
		if service.service in photographer_services:
			# الأولوية الأولى: استخدام السعر المخصوم من جدول المصور
			if photographer_services[service.service]['discounted_price'] > 0:
				final_package_price = photographer_services[service.service]['discounted_price']
			# الأولوية الثانية: استخدام نسبة الخصم العامة
			elif photographer_discount > 0 and photographer_services[service.service]['allow_discount']:
				final_package_price = initial_package_price * (1 - photographer_discount / 100.0)
		
		# حساب المبلغ الإجمالي
		amount = qty * final_package_price
		
		# إضافة الصف باستخدام الحقول الصحيحة من DocType
		booking_doc.append('package_services_table', {
			'service': service.service,
			'quantity': qty,
			'base_price': base_price,          # السعر الأساسي من Service
			'package_price': final_package_price,  # السعر النهائي بعد خصم المصور
			'amount': amount,                  # المبلغ الإجمالي (package_price × quantity)
			'is_required': service.is_required if hasattr(service, 'is_required') else 0
		})


# ============ Booking Total Calculation ============

def calculate_booking_total(booking_doc):
	"""
	حساب الإجمالي الكلي للحجز (Legacy - kept for compatibility)
	
	Args:
		booking_doc: مستند الحجز
	"""
	if booking_doc.booking_type == 'Service':
		calculate_service_totals(booking_doc)
	elif booking_doc.booking_type == 'Package':
		calculate_package_totals(booking_doc)


# ============ Service Item Row Calculations ============

def calculate_booking_service_item_rows(booking_doc):
	"""
	حساب صفوف عناصر الخدمات
	
	Args:
		booking_doc: مستند الحجز
	"""
	if not hasattr(booking_doc, 'booking_service_item'):
		return
	
	for item in booking_doc.booking_service_item:
		quantity = flt(getattr(item, 'quantity', 1))
		hourly_rate = flt(getattr(item, 'hourly_rate', 0))
		photographer_discounted_rate = flt(getattr(item, 'photographer_discounted_rate', 0))
		
		if photographer_discounted_rate > 0:
			item.total_amount = quantity * photographer_discounted_rate
		else:
			item.total_amount = quantity * hourly_rate
