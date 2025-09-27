# Copyright (c) 2023, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, add_to_date, nowdate
import json

@frappe.whitelist()
def get_dashboard_data():
	"""Get data for booking dashboard"""
	today = nowdate()
	
	return {
		"booking_stats": get_booking_stats(today),
		"recent_bookings": get_recent_bookings(),
		"upcoming_bookings": get_upcoming_bookings(today),
		"photographer_stats": get_photographer_stats(),
		"service_stats": get_service_stats()
	}

def get_booking_stats(today):
	"""Get booking statistics"""
	# Today's bookings
	today_bookings = frappe.db.count("Booking", {"booking_date": today})
	
	# This week's bookings
	start_of_week = add_to_date(getdate(today), days=-(getdate(today).weekday()), hours=0, minutes=0, seconds=0)
	end_of_week = add_to_date(start_of_week, days=6, hours=0, minutes=0, seconds=0)
	this_week_bookings = frappe.db.count("Booking", {
		"booking_date": ["between", [start_of_week, end_of_week]]
	})
	
	# This month's bookings
	start_of_month = getdate(f"{today.split('-')[0]}-{today.split('-')[1]}-01")
	end_of_month = add_to_date(start_of_month, months=1, days=-1)
	this_month_bookings = frappe.db.count("Booking", {
		"booking_date": ["between", [start_of_month, end_of_month]]
	})
	
	# Bookings by status
	status_counts = frappe.db.sql("""
		SELECT status, COUNT(*) as count
		FROM `tabBooking`
		GROUP BY status
	""", as_dict=True)
	
	status_data = {}
	for status in status_counts:
		status_data[status.status] = status.count
		
	return {
		"today": today_bookings,
		"this_week": this_week_bookings,
		"this_month": this_month_bookings,
		"status_counts": status_data
	}

def get_recent_bookings():
	"""Get recent bookings"""
	return frappe.get_all(
		"Booking",
		filters={},
		fields=[
			"name", "customer_name", "booking_date", "start_time", 
			"service", "photographer", "status", "creation"
		],
		order_by="creation desc",
		limit=5
	)

def get_upcoming_bookings(today):
	"""Get upcoming bookings"""
	return frappe.get_all(
		"Booking",
		filters={
			"booking_date": [">=", today],
			"status": ["not in", ["Completed", "Cancelled"]]
		},
		fields=[
			"name", "customer_name", "booking_date", "start_time", 
			"service", "photographer", "status"
		],
		order_by="booking_date, start_time",
		limit=5
	)

def get_photographer_stats():
	"""Get photographer statistics"""
	# Get active photographers count
	active_photographers = frappe.db.count("Photographer", {"status": "Active"})
	
	# Get top photographers by bookings
	top_photographers = frappe.db.sql("""
		SELECT 
			photographer, 
			COUNT(*) as booking_count
		FROM `tabBooking`
		WHERE status = 'Completed'
		GROUP BY photographer
		ORDER BY booking_count DESC
		LIMIT 5
	""", as_dict=True)
	
	return {
		"active_count": active_photographers,
		"top_photographers": top_photographers
	}

def get_service_stats():
	"""Get service statistics"""
	# Get active services count
	active_services = frappe.db.count("Service", {"is_active": 1})
	
	# Get top services by bookings
	top_services = frappe.db.sql("""
		SELECT 
			service, 
			COUNT(*) as booking_count
		FROM `tabBooking`
		GROUP BY service
		ORDER BY booking_count DESC
		LIMIT 5
	""", as_dict=True)
	
	# Get service details
	for service in top_services:
		service_doc = frappe.get_doc("Service", service.service)
		service["service_name"] = service_doc.service_name_ar
		
	return {
		"active_count": active_services,
		"top_services": top_services
	}