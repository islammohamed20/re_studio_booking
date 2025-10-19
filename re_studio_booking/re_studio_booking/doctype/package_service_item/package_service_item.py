# Copyright (c) 2025, Re Studio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class PackageServiceItem(Document):
	def validate(self):
		"""Validate service item data"""
		self.fetch_service_details()  # يجب جلب التفاصيل أولاً
		self.calculate_total_amount()  # ثم حساب المبلغ

	def calculate_total_amount(self):
		"""
		Calculate total amount based on unit type:
		- If unit_type = 'مدة' (Duration): total = package_price × quantity (hours)
		- If unit_type = 'كمية' (Quantity): total = qty_price × qty
		"""
		# تسجيل للتشخيص
		frappe.logger().debug(
			f"PackageServiceItem.calculate_total_amount - "
			f"unit_type: {self.unit_type}, quantity: {self.quantity}, "
			f"qty: {self.qty}, package_price: {self.package_price}, "
			f"qty_price: {self.qty_price}"
		)
		
		if self.unit_type == 'مدة':
			# للخدمات الزمنية: سعر الساعة × عدد الساعات
			price = flt(self.package_price) or flt(self.base_price) or 0
			quantity = flt(self.quantity) or 1
			self.total_amount = price * quantity
			frappe.logger().debug(f"  → مدة: price={price}, quantity={quantity}, total={self.total_amount}")
		elif self.unit_type == 'كمية':
			# للخدمات الكمية: سعر الكمية × الكمية
			price = flt(self.qty_price) or 0
			qty = flt(self.qty) or 1
			
			# تحذير إذا qty_price فارغ
			if not price:
				frappe.msgprint(
					f"⚠️ تحذير: سعر الكمية (qty_price) غير محدد للخدمة. "
					f"يرجى تحديد سعر الكمية.",
					title="قيمة مفقودة",
					indicator="orange"
				)
			
			self.total_amount = price * qty
			frappe.logger().debug(f"  → كمية: price={price}, qty={qty}, total={self.total_amount}")
		else:
			# fallback: استخدام package_price × quantity
			price = flt(self.package_price) or flt(self.base_price) or 0
			quantity = flt(self.quantity) or 1
			self.total_amount = price * quantity
			frappe.logger().warning(
				f"PackageServiceItem: unit_type غير محدد أو قيمة غير متوقعة: {self.unit_type}, "
				f"استخدام fallback"
			)
			frappe.logger().debug(f"  → fallback: price={price}, quantity={quantity}, total={self.total_amount}")

	def fetch_service_details(self):
		"""Fetch service details when service is selected"""
		if self.service:
			service_doc = frappe.get_doc("Service", self.service)
			
			# جلب اسم الخدمة
			if not self.service_name:
				self.service_name = service_doc.service_name_en
			
			# تحديد نوع الوحدة بناءً على Service.type_unit
			# يتم التحديث دائماً (حتى لو كان موجوداً) لضمان التطابق
			if service_doc.type_unit:
				if service_doc.type_unit == 'مدة':
					self.unit_type = 'مدة'
				else:
					# أي نوع آخر (Reels, Photo, etc.) يعتبر كمية
					self.unit_type = 'كمية'
				
				frappe.logger().debug(
					f"PackageServiceItem.fetch_service_details - "
					f"Service: {self.service}, type_unit: {service_doc.type_unit}, "
					f"unit_type: {self.unit_type}"
				)
			else:
				# إذا لم يكن محدداً في Service، استخدم القيمة الموجودة أو افتراضي
				if not self.unit_type:
					self.unit_type = 'مدة'  # افتراضي
				frappe.logger().warning(
					f"PackageServiceItem: Service {self.service} has no type_unit, "
					f"using default: {self.unit_type}"
				)
			
			# تعيين الأسعار الافتراضية
			if not self.base_price:
				self.base_price = service_doc.price
			if not self.package_price:
				self.package_price = service_doc.price