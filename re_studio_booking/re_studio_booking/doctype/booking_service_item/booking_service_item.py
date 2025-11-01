# Copyright (c) 2025, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class BookingServiceItem(Document):
	def validate(self):
		"""حساب الأسعار قبل الحفظ بناءً على خصم المصور (إن وجد)."""
		self.set_service_name()
		self.apply_photographer_discount()
		self.calculate_total_amount()

	def set_service_name(self):
		if getattr(self, 'service', None) and not getattr(self, 'service_name', None):
			try:
				service_doc = frappe.get_doc("Service", self.service)
				# استخدم الحقل المتوفر في Service DocType
				self.service_name = getattr(service_doc, 'service_name_en', None) or service_doc.name
			except Exception:
				self.service_name = self.service

	def apply_photographer_discount(self):
		# سعر أساسي
		base_price = flt(self.service_price)
		self.discounted_price = base_price
		if not self.parent or not getattr(self, 'service', None):
			return
		try:
			booking = frappe.get_doc("Booking", self.parent)
			# التحقق من تفعيل B2B للمصور
			if getattr(booking, 'photographer_b2b', False) and getattr(booking, 'photographer', None):
				photographer_doc = frappe.get_doc("Photographer", booking.photographer)
				# التحقق من أن المصور لديه B2B مفعل
				if getattr(photographer_doc, 'b2b', False):
					# البحث عن الخدمة في جدول خدمات المصور
					for photographer_service in photographer_doc.get('services', []):
						if photographer_service.service == self.service:
							# استخدام السعر المخصوم من جدول المصور إذا كان موجوداً
							photographer_discounted_price = flt(photographer_service.get('discounted_price') or 0)
							
							if photographer_discounted_price > 0:
								# استخدام السعر المخصوم من المصور
								self.discounted_price = photographer_discounted_price
								frappe.logger().debug(
									f"✅ تطبيق السعر المخصوم من المصور للخدمة {self.service}: "
									f"{base_price} → {self.discounted_price}"
								)
							elif photographer_doc.discount_percentage:
								# استخدام نسبة الخصم العامة إذا لم يكن هناك سعر مخصوم محدد
								discount_pct = flt(photographer_doc.discount_percentage or 0)
								if discount_pct > 0 and base_price > 0:
									self.discounted_price = base_price * (1 - discount_pct / 100.0)
									frappe.logger().debug(
										f"✅ تطبيق خصم {discount_pct}% على الخدمة {self.service}: "
										f"{base_price} → {self.discounted_price}"
									)
							break
					else:
						# الخدمة غير موجودة في جدول المصور
						frappe.logger().debug(
							f"⚠️ الخدمة {self.service} غير موجودة في جدول خدمات المصور {booking.photographer}"
						)
		except Exception as e:
			frappe.log_error(f"Photographer discount error: {str(e)}", "BookingServiceItem")

	def calculate_total_amount(self):
		"""
		حساب الإجمالي بناءً على نوع الوحدة:
		- مدة + ساعة → استخدام الحقل quantity (عدد الساعات)
		- مدة + دقيقة → استخدام الحقل min_duration (عدد الدقائق)
		- غير مدة → استخدام الحقل mount (عدد/كمية)
		واختيار السعر المخصوم إن وُجد ومختلف عن الأساسي.
		"""
		unit_type = getattr(self, 'service_unit_type', '') or ''
		duration_unit = getattr(self, 'service_duration_unit', '') or ''

		unit_qty = 0.0
		try:
			if unit_type == 'مدة':
				if duration_unit == 'ساعة':
					unit_qty = flt(getattr(self, 'quantity', 0) or 0)
				elif duration_unit == 'دقيقة':
					unit_qty = flt(getattr(self, 'min_duration', 0) or 0)
				else:
					unit_qty = 0.0
			else:
				unit_qty = flt(getattr(self, 'mount', 0) or 0)
		except Exception:
			unit_qty = 0.0

		base_price = flt(getattr(self, 'service_price', 0) or 0)
		discount_price = flt(getattr(self, 'discounted_price', 0) or 0)
		price_to_use = base_price
		if discount_price > 0 and discount_price != base_price:
			price_to_use = discount_price

		self.total_amount = unit_qty * price_to_use