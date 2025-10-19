# Copyright (c) 2023, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PackageService(Document):
	def validate(self):
		self.update_service_details()
		self.calculate_amount()
		
	def update_service_details(self):
		"""Fetch and update service details"""
		if self.service:
			service_doc = frappe.get_doc("Service", self.service)
			self.service_name = service_doc.service_name_en  # تم التصحيح من service_name_ar
			self.service_price = service_doc.price
			self.type_unit = service_doc.type_unit
			
			# تعيين base_price إذا لم يكن موجوداً
			if not self.base_price:
				self.base_price = service_doc.price
			
			# تعيين package_price إذا لم يكن موجوداً (افتراضياً نفس base_price)
			if not self.package_price:
				self.package_price = self.base_price
	
	def calculate_amount(self):
		"""
		حساب المبلغ الإجمالي بناءً على نوع الوحدة:
		- إذا كان نوع الوحدة = 'مدة' → amount = package_price × quantity (عدد الساعات)
		- إذا كان نوع الوحدة غير ذلك (Reels, Photo, etc.) → amount = unit_price × quantity
		"""
		if not self.quantity:
			self.quantity = 1
		
		# تسجيل للتشخيص
		frappe.logger().debug(f"PackageService.calculate_amount - type_unit: {self.type_unit}, quantity: {self.quantity}")
		
		# إذا كان نوع الوحدة = "مدة" (خدمة بالوقت)
		if self.type_unit == 'مدة':
			# الخدمات الزمنية: سعر الساعة × عدد الساعات
			price = self.package_price or self.base_price or 0
			self.amount = price * self.quantity
			frappe.logger().debug(f"  → مدة: price={price}, amount={self.amount}")
		else:
			# الخدمات الكمية (Reels, Photo, etc.)
			# استخدم unit_price إذا كان موجوداً، وإلا استخدم package_price
			price_per_unit = self.unit_price or self.package_price or self.base_price or 0
			self.amount = price_per_unit * self.quantity
			frappe.logger().debug(f"  → كمية: price_per_unit={price_per_unit}, amount={self.amount}")

@frappe.whitelist()
def get_service_details(service):
	"""Get service details for client-side use"""
	if not service:
		return {}
		
	service_doc = frappe.get_doc("Service", service)
	return {
		"service_name": service_doc.service_name_en,
		"price": service_doc.price,
		"type_unit": service_doc.type_unit or "",
		"base_price": service_doc.price,
		"package_price": service_doc.price
	}