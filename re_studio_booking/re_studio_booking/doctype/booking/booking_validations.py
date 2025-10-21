# Copyright (c) 2023, MASAR TEAM and contributors
# For license information, please see license.txt

"""
Booking Validation Functions
جميع دوال التحقق والـ Validation الخاصة بالحجوزات
"""

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, flt
from datetime import datetime


# ============ Date Validations ============

def validate_dates(booking_doc):
	"""
	التحقق من صحة التواريخ
	- Service: لا يمكن الحجز في الماضي
	- Package: يجب وجود تاريخ واحد على الأقل في المستقبل
	
	Args:
		booking_doc: مستند الحجز
	
	Raises:
		frappe.ValidationError: إذا كان التاريخ غير صحيح
	"""
	today = getdate(nowdate())
	
	# Service: تاريخ واحد
	if booking_doc.booking_type == 'Service' and getattr(booking_doc, 'booking_date', None):
		if getdate(booking_doc.booking_date) < today:
			frappe.throw(_("لا يمكن إنشاء حجز في تاريخ سابق"))
	
	# Package: تواريخ متعددة
	if booking_doc.booking_type == 'Package':
		_validate_package_dates(booking_doc, today)


def _validate_package_dates(booking_doc, today):
	"""
	التحقق من تواريخ الباقة
	
	Args:
		booking_doc: مستند الحجز
		today: تاريخ اليوم
	"""
	future_exists = False
	past_rows = []
	
	for row in (getattr(booking_doc, 'package_booking_dates', None) or []):
		if getattr(row, 'booking_date', None):
			row_date = getdate(row.booking_date)
			if row_date >= today:
				future_exists = True
			else:
				past_rows.append(str(row.booking_date))
	
	# إذا كل التواريخ في الماضي
	if (getattr(booking_doc, 'package_booking_dates', None) and not future_exists):
		frappe.throw(_("لا يمكن إنشاء حجز كل تواريخه في الماضي"))
	
	# تحذير للتواريخ الماضية
	if past_rows and future_exists:
		frappe.msgprint(
			_("تحذير: بعض التواريخ في الماضي ولن يتم اعتبارها: ") + ", ".join(past_rows),
			indicator='orange'
		)


def validate_studio_working_day(booking_doc):
	"""
	التحقق من أن تاريخ الحجز في يوم عمل حسب إعدادات الاستديو
	
	Args:
		booking_doc: مستند الحجز
	
	Raises:
		frappe.ValidationError: إذا كان اليوم عطلة
	"""
	if not getattr(booking_doc, 'booking_date', None):
		return
	
	try:
		booking_date = datetime.strptime(str(booking_doc.booking_date), '%Y-%m-%d')
		day_name = booking_date.strftime('%A')  # Sunday, Monday, etc.
		
		# جلب أيام العمل
		from .booking_utils import get_studio_working_days
		working_days = get_studio_working_days()
		
		if day_name not in working_days:
			day_arabic = _get_arabic_day_name(day_name)
			frappe.throw(_(
				f"لا يمكن الحجز في يوم {day_arabic} - "
				f"هذا اليوم عطلة رسمية حسب إعدادات الاستديو"
			))
	except Exception as e:
		frappe.log_error(f"خطأ في التحقق من يوم العمل: {str(e)}")


def _get_arabic_day_name(day_name):
	"""
	تحويل اسم اليوم للعربية
	
	Args:
		day_name: اسم اليوم بالإنجليزية
	
	Returns:
		str: اسم اليوم بالعربية
	"""
	days = {
		'Sunday': 'الأحد',
		'Monday': 'الاثنين',
		'Tuesday': 'الثلاثاء',
		'Wednesday': 'الأربعاء',
		'Thursday': 'الخميس',
		'Friday': 'الجمعة',
		'Saturday': 'السبت'
	}
	return days.get(day_name, day_name)


# ============ Availability Validation ============

def validate_availability(booking_doc):
	"""
	التحقق من توفر الوقت (عدم وجود حجوزات متداخلة)
	
	Args:
		booking_doc: مستند الحجز
	
	Raises:
		frappe.ValidationError: إذا كان الوقت محجوزاً
	"""
	if not (hasattr(booking_doc, 'start_time') and 
			hasattr(booking_doc, 'end_time') and 
			getattr(booking_doc, 'booking_date', None) and 
			getattr(booking_doc, 'photographer', None)):
		return
	
	# البحث عن حجوزات متداخلة
	existing_bookings = frappe.get_all(
		"Booking",
		filters=[
			["booking_date", "=", booking_doc.booking_date],
			["photographer", "=", booking_doc.photographer],
			["status", "not in", ["Cancelled"]],
			["name", "!=", booking_doc.name or "new"],
			# Check for time overlap
			["start_time", "<", booking_doc.end_time],
			["end_time", ">", booking_doc.start_time]
		]
	)
	
	if existing_bookings:
		frappe.throw(_("هذا الوقت محجوز بالفعل. الرجاء اختيار وقت آخر."))


# ============ Hours Validation ============

def validate_package_hours(booking_doc):
	"""
	التحقق من عدم تجاوز ساعات الباقة المتاحة
	
	Args:
		booking_doc: مستند الحجز
	
	Raises:
		frappe.ValidationError: إذا تم تجاوز الساعات
	"""
	if booking_doc.booking_type != 'Package':
		return
	
	if not getattr(booking_doc, 'package', None):
		return
	
	# حساب الساعات المستخدمة (تم حسابها مسبقاً في compute_package_hours_usage)
	package_total = flt(frappe.db.get_value('Package', booking_doc.package, 'total_hours') or 0)
	used = flt(getattr(booking_doc, 'used_hours', 0))
	
	if package_total > 0 and used > package_total:
		# التحقق من تجاوز الساعات بهامش خطأ صغير
		excess = used - package_total
		if excess > 0.01:  # هامش خطأ 0.01 ساعة (36 ثانية)
			frappe.throw(
				msg=_(
					f"⚠️ تم تجاوز ساعات الباقة المتاحة!<br><br>"
					f"<b>إجمالي ساعات الباقة:</b> {package_total} ساعة<br>"
					f"<b>الساعات المستخدمة:</b> {used} ساعة<br>"
					f"<b>الساعات الزائدة:</b> {round(excess, 2)} ساعة<br><br>"
					f"يرجى تعديل تواريخ الحجز لتتناسب مع الساعات المتاحة."
				),
				title=_("خطأ - تجاوز ساعات الباقة")
			)


# ============ Payment Validation ============

def validate_paid_vs_deposit(booking_doc):
	"""
	التحقق من أن المبلغ المدفوع منطقي مقارنة بالعربون والإجمالي
	هذه دالة إضافية للتحقق المزدوج (الدالة الأساسية في booking_utils.py)
	
	Args:
		booking_doc: مستند الحجز
	"""
	paid = flt(getattr(booking_doc, 'paid_amount', 0))
	deposit = flt(getattr(booking_doc, 'deposit_amount', 0))
	
	if paid == 0:
		return
	
	# التحقق الأساسي تم في booking_utils.validate_paid_amount()
	# هذه مجرد رسالة توضيحية إضافية
	if paid >= deposit:
		remaining = 0
		if booking_doc.booking_type == 'Service':
			total = flt(getattr(booking_doc, 'total_amount', 0))
			remaining = total - paid
		elif booking_doc.booking_type == 'Package':
			total = flt(getattr(booking_doc, 'total_amount_package', 0))
			remaining = total - paid
		
		if remaining > 0:
			frappe.logger().info(
				f"الحجز {booking_doc.name}: تم دفع {paid}, المتبقي {remaining}"
			)


# ============ Deletion Permission ============

def check_deletion_permission(booking_doc):
	"""
	منع حذف أو إلغاء الحجوزات المدفوعة بالكامل
	(ما عدا Administrator)
	
	Args:
		booking_doc: مستند الحجز
	
	Raises:
		frappe.PermissionError: إذا كان الحجز مدفوعاً بالكامل
	"""
	# السماح لـ Administrator بكل شيء
	if frappe.session.user == "Administrator":
		return
	
	# التحقق فقط لحجوزات الخدمات (Service)
	if booking_doc.booking_type != 'Service':
		return
	
	# التحقق من أن المبلغ المدفوع = المبلغ الإجمالي
	paid_amount = flt(getattr(booking_doc, 'paid_amount', 0) or 0)
	total_amount = flt(getattr(booking_doc, 'total_amount', 0) or 0)
	
	# إذا كان المبلغ المدفوع يساوي المبلغ الإجمالي (تم الدفع كاملاً)
	if paid_amount > 0 and total_amount > 0 and abs(paid_amount - total_amount) < 0.01:
		frappe.throw(
			msg=_(
				f"⛔ لا يمكن حذف أو إلغاء هذا الحجز!<br><br>"
				f"<b>السبب:</b> تم دفع المبلغ بالكامل<br>"
				f"<b>المبلغ الإجمالي:</b> {total_amount:,.2f} ريال<br>"
				f"<b>المبلغ المدفوع:</b> {paid_amount:,.2f} ريال<br><br>"
				f"يمكن فقط لـ <b>Administrator</b> حذف أو إلغاء هذا الحجز.<br>"
				f"يرجى التواصل مع مدير النظام."
			),
			title=_("غير مسموح بالحذف أو الإلغاء")
		)


# ============ Service Validation ============

def validate_flexible_service_timing(service_doc, booking_doc):
	"""
	التحقق من صحة توقيت الخدمة المرنة
	الخدمة المرنة لها توقيت محدد غير مرتبط بعدد ساعات الحجز
	
	Args:
		service_doc: مستند الخدمة
		booking_doc: مستند الحجز
	
	Raises:
		frappe.ValidationError: إذا لم يكن هناك توقيت محدد
	"""
	if not getattr(service_doc, 'is_flexible', False):
		return
	
	# التحقق من وجود توقيت محدد للخدمة المرنة
	if not getattr(service_doc, 'flexible_start_time', None) or not getattr(service_doc, 'flexible_end_time', None):
		frappe.throw(_(
			f"الخدمة {service_doc.name} هي خدمة مرنة ويجب تحديد توقيت البداية والنهاية"
		))


# ============ General Validation Utilities ============

def validate_required_fields_for_type(booking_doc):
	"""
	التحقق من الحقول المطلوبة حسب نوع الحجز
	
	Args:
		booking_doc: مستند الحجز
	"""
	if booking_doc.booking_type == 'Service':
		# Service bookings require service selection
		if not getattr(booking_doc, 'service', None):
			frappe.throw(_("يجب اختيار الخدمة لحجز الخدمة"))
	
	elif booking_doc.booking_type == 'Package':
		# Package bookings require package selection
		if not getattr(booking_doc, 'package', None):
			frappe.throw(_("يجب اختيار الباقة لحجز الباقة"))


def validate_booking_datetime_logic(booking_doc):
	"""
	التحقق من منطقية التاريخ والوقت
	
	Args:
		booking_doc: مستند الحجز
	"""
	if hasattr(booking_doc, 'start_time') and hasattr(booking_doc, 'end_time'):
		if booking_doc.get('start_time') and booking_doc.get('end_time'):
			if booking_doc.end_time <= booking_doc.start_time:
				frappe.throw(_("وقت النهاية يجب أن يكون بعد وقت البداية"))
