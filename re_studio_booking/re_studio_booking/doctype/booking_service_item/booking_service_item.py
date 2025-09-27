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
			if getattr(booking, 'photographer_b2b', False) and getattr(booking, 'photographer', None):
				discount_pct = flt(frappe.db.get_value("Photographer", booking.photographer, "discount_percentage") or 0)
				if discount_pct > 0 and base_price > 0:
					self.discounted_price = base_price * (1 - discount_pct / 100.0)
		except Exception as e:
			frappe.log_error(f"Photographer discount error: {str(e)}", "BookingServiceItem")

	def calculate_total_amount(self):
		qty = flt(getattr(self, 'quantity', 1) or 1)
		# إذا كان السعر بعد الخصم مختلفاً و > 0 استخدمه
		if flt(self.discounted_price) > 0 and flt(self.discounted_price) != flt(self.service_price):
			self.total_amount = qty * flt(self.discounted_price)
		else:
			self.total_amount = qty * flt(self.service_price)