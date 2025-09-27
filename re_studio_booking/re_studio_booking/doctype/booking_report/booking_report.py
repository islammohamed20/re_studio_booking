# Copyright (c) 2023, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_to_date, get_first_day, get_last_day
import json

class BookingReport(Document):
	def validate(self):
		self.validate_dates()
		
	def validate_dates(self):
		"""Ensure end date is after or equal to start date"""
		if getdate(self.end_date) < getdate(self.start_date):
			frappe.throw("يجب أن يكون تاريخ الانتهاء بعد أو يساوي تاريخ البدء")
			
	def before_save(self):
		"""Generate report data before saving"""
		self.generate_report()
		
	def generate_report(self):
		"""Generate report based on selected criteria"""
		if self.report_type == "Booking Summary":
			self.generate_booking_summary()
		elif self.report_type == "Photographer Performance":
			self.generate_photographer_performance()
		elif self.report_type == "Service Popularity":
			self.generate_service_popularity()
		elif self.report_type == "Revenue Report":
			self.generate_revenue_report()
			
	def generate_booking_summary(self):
		"""Generate booking summary report"""
		# Get bookings within date range
		filters = self.get_date_filters()
		
		# Add status filter if specified
		if self.status and self.status != "All":
			filters["status"] = self.status
			
		# Get bookings
		bookings = frappe.get_all(
			"Booking",
			filters=filters,
			fields=[
				"name", "customer_name", "booking_date", "start_time", 
				"end_time", "service", "photographer", "status"
			],
			order_by="booking_date, start_time"
		)
		
		# Calculate summary statistics
		total_bookings = len(bookings)
		status_counts = {}
		
		for booking in bookings:
			status = booking.status
			status_counts[status] = status_counts.get(status, 0) + 1
			
		# Save report data
		self.report_data = json.dumps({
			"bookings": bookings,
			"total_bookings": total_bookings,
			"status_counts": status_counts
		})
		
		# Set summary
		self.summary = f"إجمالي الحجوزات: {total_bookings}\n"
		for status, count in status_counts.items():
			self.summary += f"{status}: {count}\n"
		
	def generate_photographer_performance(self):
		"""Generate photographer performance report"""
		# Get bookings within date range
		filters = self.get_date_filters()
		
		# Only include completed bookings
		filters["status"] = "Completed"
		
		# Get bookings grouped by photographer
		photographer_bookings = frappe.db.sql("""
			SELECT 
				photographer, 
				COUNT(*) as total_bookings,
				SUM(TIMESTAMPDIFF(MINUTE, start_time, end_time)) as total_minutes
			FROM `tabBooking`
			WHERE booking_date BETWEEN %s AND %s
			AND status = 'Completed'
			GROUP BY photographer
			ORDER BY total_bookings DESC
		""", (self.start_date, self.end_date), as_dict=True)
		
		# Save report data
		self.report_data = json.dumps({
			"photographer_performance": photographer_bookings
		})
		
		# Set summary
		self.summary = "أداء المصورين:\n"
		for data in photographer_bookings:
			hours = data.total_minutes / 60
			self.summary += f"{data.photographer}: {data.total_bookings} حجز, {hours:.1f} ساعة\n"
		
	def generate_service_popularity(self):
		"""Generate service popularity report"""
		# Get bookings within date range
		filters = self.get_date_filters()
		
		# Get services grouped by popularity
		service_popularity = frappe.db.sql("""
			SELECT 
				service, 
				COUNT(*) as booking_count
			FROM `tabBooking`
			WHERE booking_date BETWEEN %s AND %s
			GROUP BY service
			ORDER BY booking_count DESC
		""", (self.start_date, self.end_date), as_dict=True)
		
		# Get service details
		for service in service_popularity:
			service_doc = frappe.get_doc("Service", service.service)
			service["service_name"] = service_doc.service_name_ar
			service["category"] = service_doc.category
			
		# Save report data
		self.report_data = json.dumps({
			"service_popularity": service_popularity
		})
		
		# Set summary
		self.summary = "شعبية الخدمات:\n"
		for data in service_popularity:
			self.summary += f"{data.service_name}: {data.booking_count} حجز\n"
		
	def generate_revenue_report(self):
		"""Generate revenue report"""
		# Get bookings within date range
		filters = self.get_date_filters()
		
		# Only include completed bookings
		filters["status"] = "Completed"
		
		# Get revenue by service
		revenue_by_service = frappe.db.sql("""
			SELECT 
				service, 
				COUNT(*) as booking_count,
				SUM(price) as total_revenue
			FROM `tabBooking`
			WHERE booking_date BETWEEN %s AND %s
			AND status = 'Completed'
			GROUP BY service
			ORDER BY total_revenue DESC
		""", (self.start_date, self.end_date), as_dict=True)
		
		# Calculate total revenue
		total_revenue = sum(item.total_revenue for item in revenue_by_service)
		
		# Save report data
		self.report_data = json.dumps({
			"revenue_by_service": revenue_by_service,
			"total_revenue": total_revenue
		})
		
		# Set summary
		self.summary = f"إجمالي الإيرادات: {total_revenue} ريال\n\n"
		self.summary += "الإيرادات حسب الخدمة:\n"
		for data in revenue_by_service:
			self.summary += f"{data.service}: {data.total_revenue} ريال ({data.booking_count} حجز)\n"
		
	def get_date_filters(self):
		"""Get date filters based on date range"""
		if self.date_range == "Custom":
			return {
				"booking_date": ["between", [self.start_date, self.end_date]]
			}
		elif self.date_range == "Today":
			today = getdate()
			return {"booking_date": today}
		elif self.date_range == "This Week":
			today = getdate()
			start_date = add_to_date(today, days=-(today.weekday()), hours=0, minutes=0, seconds=0)
			end_date = add_to_date(start_date, days=6, hours=0, minutes=0, seconds=0)
			return {"booking_date": ["between", [start_date, end_date]]}
		elif self.date_range == "This Month":
			today = getdate()
			start_date = get_first_day(today)
			end_date = get_last_day(today)
			return {"booking_date": ["between", [start_date, end_date]]}
		elif self.date_range == "Last Month":
			today = getdate()
			last_month = add_to_date(today, months=-1)
			start_date = get_first_day(last_month)
			end_date = get_last_day(last_month)
			return {"booking_date": ["between", [start_date, end_date]]}
		elif self.date_range == "This Year":
			today = getdate()
			start_date = getdate(f"{today.year}-01-01")
			end_date = getdate(f"{today.year}-12-31")
			return {"booking_date": ["between", [start_date, end_date]]}
		else:
			return {}
		
	@frappe.whitelist()
	def get_report_data(self):
		"""Return report data as JSON"""
		return self.report_data