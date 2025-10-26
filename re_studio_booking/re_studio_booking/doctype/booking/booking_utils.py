# Copyright (c) 2023, MASAR TEAM and contributors
# For license information, please see license.txt

"""
ملف مساعد للحسابات والدوال المتعلقة بـ Booking
لتخفيف الحمل عن booking.py وجعل الكود أكثر تنظيماً
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate
from datetime import datetime, timedelta


def calculate_package_service_total(service_item):
	"""
	حساب المبلغ الإجمالي لخدمة داخل الباقة
	المبلغ الإجمالي = الكمية × سعر الساعة
	"""
	quantity = flt(service_item.get('quantity', 0))
	hourly_rate = flt(service_item.get('hourly_rate', 0))
	return quantity * hourly_rate


def calculate_photographer_discounted_rate(service_item, photographer, package_doc):
	"""
	حساب سعر الساعة بعد خصم المصور للخدمات
	
	Args:
		service_item: صف الخدمة في جدول خدمات الباقة
		photographer: اسم المصور
		package_doc: مستند الباقة
	
	Returns:
		float: سعر الساعة بعد الخصم أو السعر الأصلي
	"""
	if not photographer:
		return flt(service_item.get('hourly_rate', 0))
	
	# جلب بيانات المصور
	photographer_doc = frappe.get_doc('Photographer', photographer)
	
	# التحقق من تفعيل B2B
	if not photographer_doc.get('b2b'):
		return flt(service_item.get('hourly_rate', 0))
	
	# البحث عن الخدمة في جدول خدمات المصور
	service_name = service_item.get('service')
	photographer_services = photographer_doc.get('services', [])
	
	for ps in photographer_services:
		if ps.service == service_name:
			# استخدام السعر المخصوم من المصور إذا كان موجوداً
			photographer_discounted_price = flt(ps.get('discounted_price') or 0)
			
			if photographer_discounted_price > 0:
				return photographer_discounted_price
			
			# وإلا استخدام نسبة الخصم العامة
			discount_percentage = flt(photographer_doc.get('discount_percentage', 0))
			if discount_percentage > 0:
				hourly_rate = flt(service_item.get('hourly_rate', 0))
				discounted_rate = hourly_rate * (1 - discount_percentage / 100)
				return discounted_rate
			
			# وإلا السعر الأصلي
			return flt(service_item.get('hourly_rate', 0))
	
	# الخدمة غير موجودة في جدول المصور
	return flt(service_item.get('hourly_rate', 0))


def validate_paid_amount(booking_doc):
	"""
	التحقق من صحة المبلغ المدفوع قبل الحفظ
	يجب أن يكون المبلغ المدفوع:
	- إجبارياً وأكبر من صفر
	- مساوياً أو أكبر من مبلغ العربون
	- ولا يتجاوز المبلغ الإجمالي الكامل بعد الخصم
	
	Args:
		booking_doc: مستند الحجز
	
	Raises:
		frappe.ValidationError: إذا كان المبلغ المدفوع غير صحيح
	"""
	paid_amount = flt(booking_doc.get('paid_amount', 0))
	deposit_amount = flt(booking_doc.get('deposit_amount', 0))
	
	# تحديد المبلغ الإجمالي حسب نوع الحجز
	if booking_doc.booking_type == 'Service':
		total_amount = flt(booking_doc.get('total_amount', 0))
		amount_label = "المبلغ الإجمالي بعد الخصم"
	elif booking_doc.booking_type == 'Package':
		total_amount = flt(booking_doc.get('total_amount_package', 0))
		amount_label = "المبلغ الإجمالي للباقة بعد الخصم"
	else:
		total_amount = 0
		amount_label = "المبلغ الإجمالي"
	
	# التحقق الإجباري: المبلغ المدفوع يجب أن يكون أكبر من صفر
	if paid_amount <= 0:
		frappe.throw(_(
			f"❌ المبلغ المدفوع مطلوب ويجب أن يكون أكبر من صفر!\n\n"
			f"📌 مبلغ العربون المطلوب: {deposit_amount:,.2f} ج.م\n"
			f"💰 {amount_label}: {total_amount:,.2f} ج.م\n\n"
			f"⚠️ يجب دفع مبلغ العربون على الأقل ({deposit_amount:,.2f} ج.م) لتأكيد الحجز"
		), title="المبلغ المدفوع مطلوب")
	
	# التحقق: المبلغ المدفوع >= العربون
	if paid_amount < deposit_amount:
		frappe.throw(_(
			f"❌ المبلغ المدفوع ({paid_amount:,.2f} ج.م) أقل من مبلغ العربون المطلوب!\n\n"
			f"📌 مبلغ العربون لتأكيد الحجز: {deposit_amount:,.2f} ج.م\n"
			f"💰 {amount_label}: {total_amount:,.2f} ج.م\n\n"
			f"⚠️ يجب أن يكون المبلغ المدفوع:\n"
			f"   • مساوياً أو أكبر من العربون ({deposit_amount:,.2f} ج.م)\n"
			f"   • أو مساوياً للمبلغ الإجمالي ({total_amount:,.2f} ج.م)"
		), title="خطأ في المبلغ المدفوع")
	
	# التحقق: المبلغ المدفوع <= المبلغ الإجمالي
	if paid_amount > total_amount:
		frappe.throw(_(
			f"❌ المبلغ المدفوع ({paid_amount:,.2f} ج.م) أكبر من المبلغ الإجمالي!\n\n"
			f"💰 {amount_label}: {total_amount:,.2f} ج.م\n"
			f"📌 مبلغ العربون: {deposit_amount:,.2f} ج.م\n"
			f"💵 المبلغ المدفوع: {paid_amount:,.2f} ج.م\n\n"
			f"⚠️ المبلغ المدفوع يتجاوز المبلغ الإجمالي بمقدار: {(paid_amount - total_amount):,.2f} ج.م"
		), title="خطأ في المبلغ المدفوع")
	
	# رسالة نجاح إذا كان المبلغ صحيحاً
	if paid_amount == total_amount:
		frappe.msgprint(
			f"✅ تم دفع المبلغ الإجمالي كاملاً: {paid_amount:,.2f} ج.م",
			title="دفع كامل",
			indicator="green"
		)
	elif paid_amount == deposit_amount:
		remaining = total_amount - paid_amount
		frappe.msgprint(
			f"✅ تم دفع مبلغ العربون: {paid_amount:,.2f} ج.م\n"
			f"📌 المبلغ المتبقي: {remaining:,.2f} ج.م",
			title="دفع العربون",
			indicator="blue"
		)
	else:
		remaining = total_amount - paid_amount
		frappe.msgprint(
			f"✅ تم دفع: {paid_amount:,.2f} ج.م\n"
			f"📌 المبلغ المتبقي: {remaining:,.2f} ج.م من أصل {total_amount:,.2f} ج.م",
			title="دفع جزئي",
			indicator="orange"
		)


def calculate_services_with_photographer_discount(booking_doc):
	"""
	حساب سعر الساعة بعد خصم المصور لجميع الخدمات في جدول خدمات الباقة
	
	Args:
		booking_doc: مستند الحجز
	"""
	if not booking_doc.get('photographer'):
		return
	
	photographer = booking_doc.get('photographer')
	package_name = booking_doc.get('package')
	
	if not package_name:
		return
	
	# جلب الباقة
	package_doc = frappe.get_doc('Package', package_name)
	
	# المرور على جميع الخدمات في جدول خدمات الباقة
	for service_item in booking_doc.get('booking_service_item', []):
		# حساب سعر الساعة بعد خصم المصور
		discounted_rate = calculate_photographer_discounted_rate(
			service_item, 
			photographer, 
			package_doc
		)
		
		# تحديث سعر الساعة بعد الخصم
		service_item.photographer_discounted_rate = discounted_rate
		
		# إعادة حساب المبلغ الإجمالي
		if discounted_rate != flt(service_item.get('hourly_rate', 0)):
			# استخدام السعر بعد الخصم
			service_item.total_amount = flt(service_item.quantity) * discounted_rate
		else:
			# استخدام السعر الأصلي
			service_item.total_amount = calculate_package_service_total(service_item)


def recalculate_package_services_on_package_change(booking_doc):
	"""
	إعادة حساب خدمات الباقة عند تغيير الباقة
	يتم حساب المبلغ الإجمالي = الكمية × سعر الساعة
	
	Args:
		booking_doc: مستند الحجز
	"""
	if not booking_doc.get('package'):
		return
	
	# المرور على جميع الخدمات
	for service_item in booking_doc.get('booking_service_item', []):
		# حساب المبلغ الإجمالي
		service_item.total_amount = calculate_package_service_total(service_item)


def get_service_unit_type_fields(unit_type):
	"""
	الحصول على الحقول التي يجب إظهارها بناءً على نوع الوحدة
	
	Args:
		unit_type: نوع الوحدة (Reels, مدة, Promo, etc.)
	
	Returns:
		dict: قاموس بالحقول التي يجب إظهارها
	"""
	show_quantity = unit_type in ['Reels', 'Promo', 'Photo Session', 'Series', 'Podcast Ep']
	show_duration = unit_type == 'مدة'
	
	return {
		'show_quantity': show_quantity,
		'show_duration_fields': show_duration
	}


def validate_flexible_service_timing(service_doc, booking_doc):
	"""
	التحقق من صحة توقيت الخدمة المرنة
	الخدمة المرنة لها توقيت محدد غير مرتبط بعدد ساعات الحجز
	
	Args:
		service_doc: مستند الخدمة
		booking_doc: مستند الحجز
	"""
	if not service_doc.get('is_flexible'):
		return
	
	# التحقق من وجود توقيت محدد للخدمة المرنة
	if not service_doc.get('flexible_start_time') or not service_doc.get('flexible_end_time'):
		frappe.throw(_(
			f"الخدمة {service_doc.name} هي خدمة مرنة ويجب تحديد توقيت البداية والنهاية"
		))


def format_currency_arabic(amount):
	"""
	تنسيق المبلغ بالعملة العربية
	
	Args:
		amount: المبلغ
	
	Returns:
		str: المبلغ منسق بالعربية
	"""
	currency = frappe.defaults.get_defaults().get('currency', 'EGP')
	currency_symbol = {
		'EGP': 'ج.م',
		'SAR': 'ر.س',
		'USD': '$'
	}.get(currency, currency)
	
	return f"{flt(amount, 2):,.2f} {currency_symbol}"


def get_studio_working_days():
	"""
	جلب أيام العمل للاستديو من General Settings
	
	Returns:
		list: قائمة بأسماء أيام العمل (Sunday, Monday, etc.)
	"""
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
