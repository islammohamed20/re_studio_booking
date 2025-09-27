# -*- coding: utf-8 -*-
# Copyright (c) 2025, Re Studio and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint


class Package(Document):
	def validate(self):
		"""Validate package data before saving"""
		self.validate_hours()
		self.calculate_pricing()
		
	def validate_hours(self):
		"""Validate package hours"""
		if self.minimum_booking_hours and self.minimum_booking_hours <= 0:
			frappe.throw("الحد الأدنى لساعات الحجز يجب أن يكون أكبر من صفر")
		
		if self.minimum_booking_hours and self.total_hours and self.minimum_booking_hours > self.total_hours:
			frappe.throw("الحد الأدنى لساعات الحجز لا يمكن أن يكون أكبر من إجمالي ساعات الباقة")
		
		# Calculate remaining hours
		self.remaining_hours = flt(self.total_hours) - flt(self.used_hours or 0)

	def calculate_pricing(self):
		"""Calculate package pricing"""
		# Calculate total price from all services
		total = 0
		if self.package_services:
			for service in self.package_services:
				if service.package_price:
					total += flt(service.package_price) * flt(service.quantity or 1)
		self.total_price = total

		# Calculate final price after discount
		discount_amount = flt(self.total_price) * flt(self.discount_percentage or 0) / 100
		self.final_price = flt(self.total_price) - discount_amount

	def before_save(self):
		"""Actions to perform before saving"""
		# Ensure package services are properly linked
		if self.package_services:
			for service in self.package_services:
				if service.service and not service.service_name:
					try:
						service_doc = frappe.get_doc("Service", service.service)
						service.service_name = service_doc.service_name_en or service_doc.name
						if not service.base_price:
							service.base_price = service_doc.price
						if not service.package_price:
							service.package_price = service_doc.price
					except Exception:
						pass  # Skip if service not found

	@frappe.whitelist()
	def get_remaining_hours_message(self):
		"""Get formatted message for remaining hours"""
		remaining = flt(self.total_hours) - flt(self.used_hours or 0)
		if remaining > 0:
			return "متبقي {:.1f} ساعة للحجز".format(remaining)
		else:
			return "تم استخدام جميع ساعات الباقة"

	@frappe.whitelist()
	def can_add_more_bookings(self):
		"""Check if more bookings can be added"""
		remaining = flt(self.total_hours) - flt(self.used_hours or 0)
		return remaining > 0


@frappe.whitelist()
def get_service_details(service):
	"""Get service details for package service table"""
	try:
		service_doc = frappe.get_doc("Service", service)
		return {
			'service_name': service_doc.service_name_en or service_doc.name,
			'base_price': service_doc.price or 0,
			'package_price': service_doc.price or 0,
			'duration': getattr(service_doc, 'duration', 0)
		}
	except Exception:
		return {'service_name': '', 'base_price': 0, 'package_price': 0, 'duration': 0}


@frappe.whitelist()
def validate_booking_hours(package, new_hours):
	"""Validate if new booking hours can be added to package"""
	try:
		package_doc = frappe.get_doc("Package", package)
		total_with_new = flt(package_doc.used_hours or 0) + flt(new_hours)
		
		if total_with_new > flt(package_doc.total_hours):
			remaining = flt(package_doc.total_hours) - flt(package_doc.used_hours or 0)
			return {
				'valid': False,
				'message': "لا يمكن إضافة {} ساعة. متبقي {} ساعة فقط".format(new_hours, remaining)
			}
		
		if package_doc.minimum_booking_hours and new_hours < package_doc.minimum_booking_hours:
			return {
				'valid': False,
				'message': "الحد الأدنى للحجز هو {} ساعة".format(package_doc.minimum_booking_hours)
			}
		
		return {'valid': True, 'message': 'يمكن إضافة الحجز'}
	except Exception as e:
		return {'valid': False, 'message': str(e)}
