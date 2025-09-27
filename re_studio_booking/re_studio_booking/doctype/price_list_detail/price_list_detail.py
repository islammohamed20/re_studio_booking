# Copyright (c) 2024, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class PriceListDetail(Document):
	def validate(self):
		self.validate_item_selection()
		self.calculate_final_price()

	def validate_item_selection(self):
		"""التحقق من اختيار العنصر الصحيح"""
		if self.item_type == "Service" and not self.service:
			frappe.throw("يجب اختيار خدمة عند تحديد نوع العنصر كخدمة")
			
		if self.item_type == "Service Package" and not self.service_package:
			frappe.throw("يجب اختيار باقة خدمة عند تحديد نوع العنصر كباقة")
			
		# مسح الحقل غير المطلوب
		if self.item_type == "Service":
			self.service_package = None
		else:
			self.service = None

	def calculate_final_price(self):
		"""حساب السعر النهائي بعد الخصم"""
		if self.discount_percentage:
			discount_amount = flt(self.price) * flt(self.discount_percentage) / 100
			self.final_price = flt(self.price) - discount_amount
		else:
			self.final_price = flt(self.price)