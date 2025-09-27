# Copyright (c) 2023, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime, timedelta

class Photographer(Document):
	def validate(self):
		self.set_full_name()
		self.validate_services()
		self.calculate_discounted_prices()
	
	def before_insert(self):
		# منع إضافة ساعات العمل تلقائياً
		# إذا كانت ساعات العمل فارغة أو تحتوي على صفوف فارغة، امسحها
		if hasattr(self, 'working_hours') and self.working_hours:
			# تحقق إذا كانت جميع الصفوف فارغة (صفوف تلقائية)
			empty_rows = []
			for row in self.working_hours:
				if not row.start_time and not row.end_time and row.day:
					empty_rows.append(row)
			
			# إذا كانت جميع الصفوف فارغة، احذفها
			if len(empty_rows) == len(self.working_hours):
				self.working_hours = []
	
	def before_save(self):
		# منع حفظ صفوف فارغة في ساعات العمل
		if hasattr(self, 'working_hours') and self.working_hours:
			valid_rows = []
			for row in self.working_hours:
				# احتفظ فقط بالصفوف التي تحتوي على بيانات صحيحة
				if row.start_time and row.end_time and row.day:
					valid_rows.append(row)
			self.working_hours = valid_rows
		
	def set_full_name(self):
		# Set the full name based on first and last name
		self.full_name = f"{self.first_name} {self.last_name or ''}".strip()
		
	def validate_services(self):
		# Ensure photographer has at least one active service
		has_active_service = False
		if hasattr(self, 'services') and self.services:
			for service in self.services:
				if hasattr(service, 'is_active') and service.is_active:
					has_active_service = True
					break
		
		if not has_active_service and self.status == "Active":
			frappe.throw("يجب أن يكون لدى المصور خدمة نشطة واحدة على الأقل")
			
	def calculate_discounted_prices(self):
		"""حساب الأسعار المخفضة لجميع الخدمات في جدول الخدمات حسب نسبة الخصم"""
		if not hasattr(self, 'services') or not self.services:
			return
			
		# احصل على نسبة الخصم
		discount_percentage = 0
		if self.b2b and hasattr(self, 'discount_percentage') and self.discount_percentage:
			try:
				discount_percentage = float(self.discount_percentage)
			except (ValueError, TypeError):
				discount_percentage = 0
				
		# حساب السعر المخفض لكل خدمة
		for service_row in self.services:
			if not service_row.service:
				continue
				
			try:
				# احصل على السعر الأساسي من Service DocType
				base_price = frappe.db.get_value("Service", service_row.service, "price") or 0
				service_row.base_price = float(base_price)
				
				# حساب السعر المخفض
				if discount_percentage > 0 and base_price > 0:
					discounted_price = base_price * (1 - discount_percentage / 100.0)
					service_row.discounted_price = round(discounted_price, 2)
				else:
					service_row.discounted_price = base_price
					
			except Exception as e:
				frappe.log_error(f"خطأ في حساب السعر المخفض للخدمة {service_row.service}: {str(e)}")
				service_row.discounted_price = service_row.base_price or 0
			
	def get_availability(self, date):
		# Get photographer's availability for a specific date
		# First check if the date is a holiday or day off
		if self.is_holiday(date):
			return []
		
		# Get working hours for the day
		working_hours = self.get_working_hours(date)
		if not working_hours:
			return []
		
		# Get existing bookings for the date
		existing_bookings = frappe.get_all(
			"Booking",
			filters={
				"booking_date": date,
				"photographer": self.name,
				"status": ["not in", ["Cancelled"]]
			},
			fields=["start_time", "end_time"]
		)
		
		# Calculate available time slots
		available_slots = self.calculate_available_slots(working_hours, existing_bookings)
		return available_slots
		
	def is_holiday(self, date):
		# Check if the date is a holiday or day off
		# Implementation depends on holiday management system
		return False
		
	def get_working_hours(self, date):
		# Get working hours for the specific day of the week
		# Implementation depends on schedule management
		# For now, return default working hours
		return {"start": "09:00:00", "end": "17:00:00"}
		
	def calculate_available_slots(self, working_hours, existing_bookings):
		# Calculate available time slots based on working hours and existing bookings
		# This is a simplified implementation
		# A more complex implementation would consider slot duration, breaks, etc.
		return [{"start": "09:00:00", "end": "10:00:00"}, {"start": "10:00:00", "end": "11:00:00"}]


@frappe.whitelist()
def get_booking_stats(photographer):
	"""إرجاع إحصائيات الحجوزات الخاصة بالمصور للاستخدام في واجهة Photographer.

	النتيجة تتضمن:
	- total_bookings: إجمالي الحجوزات غير الملغاة
	- completed_bookings: عدد الحجوزات المكتملة
	- upcoming_bookings: عدد الحجوزات القادمة (التاريخ >= اليوم)
	- upcoming_bookings_list: أول 10 حجوزات قادمة للتفاصيل
	"""
	stats = {
		"total_bookings": 0,
		"completed_bookings": 0,
		"upcoming_bookings": 0,
		"upcoming_bookings_list": []
	}
	try:
		if not photographer or not frappe.db.exists("Photographer", photographer):
			return stats

		# إجمالي الحجوزات (استبعاد الملغاة فقط)
		stats["total_bookings"] = frappe.db.count("Booking", {
			"photographer": photographer,
			"status": ["not in", ["Cancelled"]]
		})

		# المكتملة
		stats["completed_bookings"] = frappe.db.count("Booking", {
			"photographer": photographer,
			"status": "Completed"
		})

		# القادمة (تاريخ اليوم أو بعده)
		today = frappe.utils.today()
		stats["upcoming_bookings"] = frappe.db.count("Booking", {
			"photographer": photographer,
			"status": ["in", ["Pending", "Confirmed"]],
			"booking_date": [">=", today]
		})

		# قائمة أول 10 حجوزات قادمة
		stats["upcoming_bookings_list"] = frappe.db.get_all(
			"Booking",
			filters={
				"photographer": photographer,
				"status": ["in", ["Pending", "Confirmed"]],
				"booking_date": [">=", today]
			},
			fields=["name", "booking_date", "booking_datetime", "customer_name", "service_name"],
			order_by="booking_date asc, booking_datetime asc",
			limit=10
		)
	except Exception as e:
		frappe.log_error(f"Error in get_booking_stats for photographer {photographer}: {str(e)}")
	return stats