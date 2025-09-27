# Copyright (c) 2025, Re Studio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, flt
from datetime import datetime, timedelta

class PackageBookingDate(Document):
	def validate(self):
		"""Validate booking date data"""
		self.validate_times()
		self.calculate_hours()
		self.validate_date()

	def validate_times(self):
		"""Validate start and end times"""
		if self.start_time and self.end_time:
			# Convert times to datetime for comparison
			start_datetime = get_datetime(f"{self.booking_date} {self.start_time}")
			end_datetime = get_datetime(f"{self.booking_date} {self.end_time}")
			
			if end_datetime <= start_datetime:
				frappe.throw("وقت النهاية يجب أن يكون بعد وقت البداية")

	def calculate_hours(self):
		"""Calculate hours between start and end time"""
		if self.start_time and self.end_time:
			start_datetime = get_datetime(f"{self.booking_date} {self.start_time}")
			end_datetime = get_datetime(f"{self.booking_date} {self.end_time}")
			
			# Calculate difference in hours
			hours_diff = (end_datetime - start_datetime).total_seconds() / 3600
			self.hours = round(hours_diff, 2)

	def validate_date(self):
		"""Validate booking date is not in the past"""
		if self.booking_date:
			booking_datetime = get_datetime(self.booking_date)
			today = get_datetime(frappe.utils.today())
			
			if booking_datetime < today:
				frappe.throw("لا يمكن حجز تاريخ في الماضي")

	def before_save(self):
		"""Actions before saving"""
		# Check for overlapping bookings on the same date
		self.check_overlapping_bookings()

	def check_overlapping_bookings(self):
		"""Check if there are overlapping bookings on the same date"""
		if not self.parent:
			return
		
		# Get parent package document
		package_doc = frappe.get_doc("Package", self.parent)
		
		for booking in package_doc.booking_dates:
			# Skip current row
			if booking.name == self.name:
				continue
			
			# Check if same date
			if booking.booking_date == self.booking_date:
				# Check for time overlap
				if self.times_overlap(booking.start_time, booking.end_time, self.start_time, self.end_time):
					frappe.throw(f"يوجد تداخل في الأوقات مع حجز آخر في نفس التاريخ {self.booking_date}")

	def times_overlap(self, start1, end1, start2, end2):
		"""Check if two time ranges overlap"""
		if not all([start1, end1, start2, end2]):
			return False
		
		# Convert to datetime for comparison
		date_str = self.booking_date or frappe.utils.today()
		start1_dt = get_datetime(f"{date_str} {start1}")
		end1_dt = get_datetime(f"{date_str} {end1}")
		start2_dt = get_datetime(f"{date_str} {start2}")
		end2_dt = get_datetime(f"{date_str} {end2}")
		
		# Check for overlap
		return start1_dt < end2_dt and start2_dt < end1_dt