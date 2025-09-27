# Copyright (c) 2024, Re Studio Booking and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.utils import cint, now


def get_setup_stages(args):
	"""Setup stages for Re Studio Booking"""
	stages = [
		{
			"status": _("Setting up Re Studio"),
			"fail_msg": _("Failed to setup Re Studio"),
			"tasks": [
				{
					"fn": setup_studio_settings,
					"args": args,
					"fail_msg": "Failed to setup studio settings",
					"app_name": "re_studio_booking",
				}
			],
		},
		{
			"status": _("Creating default services"),
			"fail_msg": _("Failed to create default services"),
			"tasks": [
				{
					"fn": create_default_services,
					"args": args,
					"fail_msg": "Failed to create default services",
					"app_name": "re_studio_booking",
				}
			],
		},
		{
			"status": _("Setting up default photographer"),
			"fail_msg": _("Failed to setup default photographer"),
			"tasks": [
				{
					"fn": create_default_photographer,
					"args": args,
					"fail_msg": "Failed to create default photographer",
					"app_name": "re_studio_booking",
				}
			],
		}
	]
	return stages


def setup_studio_settings(args):
	"""Setup studio settings from wizard data"""
	try:
		# Create or update Studio Settings
		if not frappe.db.exists("DocType", "Studio Settings"):
			create_studio_settings_doctype()
		
		# Create studio settings document
		studio_settings = frappe.get_doc({
			"doctype": "Studio Settings",
			"studio_name": args.get("studio_name", "Re Studio"),
			"studio_phone": args.get("studio_phone", ""),
			"studio_website": args.get("studio_website", ""),
			"studio_address": args.get("studio_address", ""),
			"default_currency": args.get("currency", "USD"),
			"default_timezone": args.get("timezone", "UTC"),
			"business_hours_start": "09:00",
			"business_hours_end": "18:00",
			"booking_advance_days": 30,
			"cancellation_hours": 24
		})
		studio_settings.insert(ignore_permissions=True)
		frappe.db.commit()
	except Exception as e:
		frappe.log_error(f"Error in setup_studio_settings: {str(e)}")
		raise


def create_studio_settings_doctype():
	"""Create Studio Settings DocType if it doesn't exist"""
	doctype_dict = {
		"doctype": "DocType",
		"name": "Studio Settings",
		"module": "Re Studio Booking",
		"custom": 0,
		"is_single": 1,
		"track_changes": 1,
		"fields": [
			{
				"fieldname": "studio_name",
				"label": "Studio Name",
				"fieldtype": "Data",
				"reqd": 1
			},
			{
				"fieldname": "studio_phone",
				"label": "Studio Phone",
				"fieldtype": "Data"
			},
			{
				"fieldname": "studio_website",
				"label": "Studio Website",
				"fieldtype": "Data"
			},
			{
				"fieldname": "studio_address",
				"label": "Studio Address",
				"fieldtype": "Text"
			},
			{
				"fieldname": "section_break_1",
				"fieldtype": "Section Break",
				"label": "Business Settings"
			},
			{
				"fieldname": "default_currency",
				"label": "Default Currency",
				"fieldtype": "Link",
				"options": "Currency"
			},
			{
				"fieldname": "default_timezone",
				"label": "Default Timezone",
				"fieldtype": "Data"
			},
			{
				"fieldname": "column_break_1",
				"fieldtype": "Column Break"
			},
			{
				"fieldname": "business_hours_start",
				"label": "Business Hours Start",
				"fieldtype": "Time"
			},
			{
				"fieldname": "business_hours_end",
				"label": "Business Hours End",
				"fieldtype": "Time"
			},
			{
				"fieldname": "section_break_2",
				"fieldtype": "Section Break",
				"label": "Booking Settings"
			},
			{
				"fieldname": "booking_advance_days",
				"label": "Booking Advance Days",
				"fieldtype": "Int",
				"default": 30
			},
			{
				"fieldname": "cancellation_hours",
				"label": "Cancellation Hours",
				"fieldtype": "Int",
				"default": 24
			}
		],
		"permissions": [
			{
				"role": "System Manager",
				"read": 1,
				"write": 1,
				"create": 1,
				"delete": 1
			}
		]
	}
	
	doc = frappe.get_doc(doctype_dict)
	doc.insert(ignore_permissions=True)
	frappe.db.commit()


def create_default_services(args):
	"""Create default photography services"""
	default_services = [
		{
			"service_name": "Portrait Photography",
			"description": "Professional portrait photography session",
			"duration": 60,
			"price": 100.0
		},
		{
			"service_name": "Wedding Photography",
			"description": "Complete wedding photography package",
			"duration": 480,
			"price": 1500.0
		},
		{
			"service_name": "Event Photography",
			"description": "Event and party photography",
			"duration": 240,
			"price": 500.0
		},
		{
			"service_name": "Product Photography",
			"description": "Professional product photography",
			"duration": 120,
			"price": 200.0
		}
	]
	
	for service_data in default_services:
		if not frappe.db.exists("Service", service_data["service_name"]):
			service = frappe.get_doc({
				"doctype": "Service",
				"service_name": service_data["service_name"],
				"description": service_data["description"],
				"duration": service_data["duration"],
				"price": service_data["price"],
				"is_active": 1
			})
			service.insert(ignore_permissions=True)
	
	frappe.db.commit()


def create_default_photographer(args):
	"""Create default photographer from user data"""
	user_name = args.get("photographer_name", args.get("full_name", "Default Photographer"))
	user_email = args.get("photographer_email", args.get("email", "photographer@restudio.com"))
	
	if not frappe.db.exists("Photographer", user_email):
		photographer = frappe.get_doc({
			"doctype": "Photographer",
			"photographer_name": user_name,
			"email": user_email,
			"phone": args.get("photographer_phone", args.get("phone", "")),
			"is_active": 1,
			"working_hours_start": args.get("photographer_hours_start", "09:00"),
			"working_hours_end": args.get("photographer_hours_end", "18:00"),
			"specializations": args.get("specializations", "")
		})
		photographer.insert(ignore_permissions=True)
	
	frappe.db.commit()


def setup_complete(args):
	"""Called after setup wizard is complete"""
	try:
		# Mark setup as complete
		frappe.db.set_single_value("System Settings", "setup_complete", 1)
		
		# Create welcome message
		studio_name = args.get("studio_name", "Re Studio")
		frappe.msgprint(
			f"Welcome to {studio_name}! Your photography studio management system is now ready.",
			title="Setup Complete",
			indicator="green"
		)
		
		frappe.db.commit()
	except Exception as e:
		frappe.log_error(f"Error in setup_complete: {str(e)}")
		raise