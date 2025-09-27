# Copyright (c) 2023, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
	"""Run after installation"""
	create_roles()
	create_booking_settings()
	add_to_erpnext_modules()


def has_app_permission():
	"""Check if user has permission to access the app"""
	user = frappe.session.user
	
	if user == "Administrator" or frappe.db.exists("Has Role", {"parent": user, "role": "System Manager"}):
		return True
		
	allowed_roles = ["Re Studio Manager", "Re Studio Agent"]
	for role in allowed_roles:
		if frappe.db.exists("Has Role", {"parent": user, "role": role}):
			return True
			
	return False


def create_roles():
	"""Create required roles for Re Studio Booking"""
	roles = [
		"Re Studio Manager",
		"Re Studio Agent",
		"Re Studio Customer"
	]
	
	for role in roles:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({
				"doctype": "Role",
				"role_name": role,
				"desk_access": 1,
				"is_custom": 1,
				"disabled": 0
			}).insert(ignore_permissions=True)
			
			frappe.db.commit()


def create_booking_settings():
	"""Create default booking settings"""
	if not frappe.db.exists("Booking Settings", "Booking Settings"):
		settings = frappe.get_doc({
			"doctype": "Booking Settings",
			"business_start_time": "09:00:00",
			"business_end_time": "18:00:00",
			"first_day_of_week": "Sunday",
			"sunday": 0,
			"monday": 1,
			"tuesday": 1,
			"wednesday": 1,
			"thursday": 1,
			"friday": 0,
			"saturday": 0,
			"time_slot_duration": 30,
			"advance_booking_days": 1,
			"max_days_in_advance": 30,
			"allow_cancellation": 1,
			"cancellation_hours": 24,
			"default_currency": "EGP",
			"currency_symbol": "ج.م",
			"currency_position": "Before",
			"decimal_places": 2,
			"thousands_separator": ",",
			"decimal_separator": ".",
			"enable_service_selection": 1,
			"enable_agent_selection": 1,
			"enable_date_time_selection": 1,
			"enable_customer_info": 1,
			"enable_payment_step": 0,
			"enable_tax": 0,
			"tax_rate": 14,
			"include_tax_in_price": 0,
			"tax_label": "ضريبة القيمة المضافة",
			"enable_online_payments": 0,
			"payment_methods": "Cash",
			"deposit_percentage": 0,
			"minimum_booking_amount": 0,
			"auto_confirm_bookings": 1,
			"booking_buffer_time": 0,
			"enable_customer_dashboard": 1,
			"enable_agent_dashboard": 1,
			"send_confirmation_email": 1,
			"send_reminder_email": 1,
			"reminder_hours": 24,
			"default_status": "Pending Approval",
			"statuses_that_block_timeslot": "Approved",
			"statuses_that_appear_on_pending_page": "Pending Approval",
			"statuses_hidden_on_calendar": "Cancelled",
			"additional_statuses": "",
			"time_system": "12-hour clock",
			"date_format": "DD/MM/YYYY",
			"selectable_intervals": "15 minutes",
			"show_appointment_end_time": 1,
			"disable_verbose_date_output": 0
		})
		
		settings.insert(ignore_permissions=True)
		frappe.db.commit()


def add_to_erpnext_modules():
	"""Add Re Studio Booking to ERPNext modules"""
	try:
		# Check if ERPNext is installed
		if "erpnext" in frappe.get_installed_apps():
			# Add to modules.txt if not already there
			modules_path = frappe.get_app_path("erpnext", "modules.txt")
			with open(modules_path, "r") as f:
				modules = f.read().splitlines()
			
			if "Re Studio Booking" not in modules:
				with open(modules_path, "a") as f:
					f.write("\nRe Studio Booking")
			
			# Add module def if not exists
			if not frappe.db.exists("Module Def", "Re Studio Booking"):
				module = frappe.get_doc({
					"doctype": "Module Def",
					"module_name": "Re Studio Booking",
					"app_name": "re_studio_booking"
				})
				module.insert(ignore_permissions=True)
				frappe.db.commit()
			
			# Update navbar settings to ensure Apps link is visible
			if not frappe.db.exists("Navbar Item", {"item_label": "Apps"}):
				navbar_settings = frappe.get_single("Navbar Settings")
				settings_items = navbar_settings.settings_dropdown
				
				# Find position to insert Apps link
				view_website_item_idx = -1
				for i, item in enumerate(navbar_settings.settings_dropdown):
					if item.get("item_label") == "View Website":
						view_website_item_idx = i
						break
				
				# Add Apps link if position found
				if view_website_item_idx >= 0:
					settings_items.insert(
						view_website_item_idx + 1,
						{
							"item_label": "Apps",
							"item_type": "Route",
							"route": "/apps",
							"is_standard": 1,
						},
					)
					
					navbar_settings.set("settings_dropdown", settings_items)
					navbar_settings.save()
					frappe.db.commit()
	except Exception as e:
		frappe.log_error(f"Error adding Re Studio Booking to ERPNext modules: {str(e)}")