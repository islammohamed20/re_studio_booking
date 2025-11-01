# Copyright (c) 2025, Re Studio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint

class Package(Document):
	def validate(self):
		"""Validate package data before saving"""
		self.validate_minimum_booking_hours()
		self.calculate_total_price()
		self.calculate_final_price()
		self.calculate_remaining_hours()

	def validate_minimum_booking_hours(self):
		"""Ensure minimum booking hours is valid"""
		if self.minimum_booking_hours and self.minimum_booking_hours <= 0:
			frappe.throw("الحد الأدنى لساعات الحجز يجب أن يكون أكبر من صفر")
		
		if self.minimum_booking_hours and self.total_hours and self.minimum_booking_hours > self.total_hours:
			frappe.throw("الحد الأدنى لساعات الحجز لا يمكن أن يكون أكبر من إجمالي ساعات الباقة")

	def calculate_total_price(self):
		"""Calculate total price from all services"""
		total = 0
		for service in self.package_services:
			# الحساب: package_price × quantity
			service_total = flt(service.package_price or 0) * flt(service.quantity or 0)
			
			# تحديث total_amount في الصف
			service.total_amount = service_total
			
			# إضافة إلى المجموع الكلي
			total += service_total
		
		self.total_price = total
		
		# تسجيل للتشخيص
		frappe.logger().debug(
			f"Package.calculate_total_price: total_price={total} "
			f"from {len(self.package_services)} services"
		)

	def calculate_final_price(self):
		"""Calculate final price after discount"""
		discount_amount = flt(self.total_price) * flt(self.discount_percentage or 0) / 100
		self.final_price = flt(self.total_price) - discount_amount

	def calculate_remaining_hours(self):
		"""Calculate remaining hours from total and used hours"""
		self.remaining_hours = flt(self.total_hours) - flt(self.used_hours or 0)



	@frappe.whitelist()
	def get_remaining_hours_message(self):
		"""Get formatted message for remaining hours"""
		remaining = flt(self.total_hours) - flt(self.used_hours or 0)
		if remaining > 0:
			return f"متبقي {remaining:.1f} ساعة للحجز"
		else:
			return "تم استخدام جميع ساعات الباقة"

	@frappe.whitelist()
	def can_add_more_bookings(self):
		"""Check if more bookings can be added"""
		remaining = flt(self.total_hours) - flt(self.used_hours or 0)
		return remaining > 0

	@frappe.whitelist()
	def get_services_for_booking(self):
		"""Get services list for booking integration"""
		services = []
		for service in self.package_services:
			services.append({
				'service': service.service,
				'service_name': service.service_name,
				'quantity': service.quantity,
				'package_price': service.package_price,
				'is_required': service.is_required
			})
		return services

	def on_update(self):
		"""Actions to perform after updating the document"""
		# Update any related bookings if needed
		pass

	def before_save(self):
		"""Actions to perform before saving"""
		# Ensure package services are properly linked
		for service in self.package_services:
			if service.service and not service.service_name:
				service_doc = frappe.get_doc("Service", service.service)
				service.service_name = service_doc.service_name_en
				if not service.base_price:
					service.base_price = service_doc.price
				if not service.package_price:
					service.package_price = service_doc.price

@frappe.whitelist()
def get_service_details(service):
	"""Get service details for package service table"""
	service_doc = frappe.get_doc("Service", service)
	
	# تحديد نوع الخدمة بناءً على type_unit و duration_unit
	if service_doc.type_unit == 'مدة':
		# خدمة زمنية: استخدام duration_unit (دقيقة/ساعة/يوم)
		service_type = getattr(service_doc, 'duration_unit', 'ساعة')
	else:
		# خدمة كمية
		service_type = 'كمية'
	
	return {
		'service_name': service_doc.service_name_en,
		'base_price': service_doc.price,
		'package_price': service_doc.price,
		'service_type': service_type,
		'duration': service_doc.duration
	}

@frappe.whitelist()
def validate_booking_hours(package, new_hours):
	"""Validate if new booking hours can be added to package"""
	package_doc = frappe.get_doc("Package", package)
	total_with_new = flt(package_doc.used_hours) + flt(new_hours)
	
	if total_with_new > flt(package_doc.total_hours):
		return {
			'valid': False,
			'message': f"لا يمكن إضافة {new_hours} ساعة. متبقي {package_doc.remaining_hours} ساعة فقط"
		}
	
	if package_doc.minimum_booking_hours and new_hours < package_doc.minimum_booking_hours:
		return {
			'valid': False,
			'message': f"الحد الأدنى للحجز هو {package_doc.minimum_booking_hours} ساعة"
		}
	
	return {'valid': True, 'message': 'يمكن إضافة الحجز'}