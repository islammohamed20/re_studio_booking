from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Re Studio Dashboard"),
			"items": [
				{
					"type": "page",
					"name": "admin-dashboard",
					"label": _("Admin Dashboard"),
					"description": _("Advanced admin dashboard with analytics")
				},
				{
					"type": "page",
					"name": "dashboard",
					"label": _("Main Dashboard"),
					"description": _("Main dashboard overview")
				},
				{
					"type": "page",
					"name": "booking-dashboard",
					"label": _("Booking Dashboard"),
					"description": _("Booking management dashboard")
				}
			]
		},
		{
			"label": _("Booking Management"),
			"items": [
				{
					"type": "doctype",
					"name": "Booking",
					"label": _("Bookings"),
					"description": _("Manage studio bookings")
				},
				{
					"type": "page",
					"name": "bookings",
					"label": _("Bookings List"),
					"description": _("View and manage all bookings")
				}
			]
		},
		{
			"label": _("Services & Categories"),
			"items": [
				{
					"type": "page",
					"name": "services",
					"label": _("Services Management"),
					"description": _("Manage studio services")
				},
				{
					"type": "doctype",
					"name": "Service",
					"label": _("Services"),
					"description": _("Studio services list")
				},
				{
					"type": "page",
					"name": "categories",
					"label": _("Categories Management"),
					"description": _("Manage service categories")
				},
				{
					"type": "doctype",
					"name": "Category",
					"label": _("Categories"),
					"description": _("Service categories list")
				}
			]
		},
		{
			"label": _("Packages"),
			"items": [
				{
					"type": "page",
					"name": "packages",
					"label": _("Packages Management"),
					"description": _("Manage service packages")
				},
				{
					"type": "doctype",
					"name": "Service Package",
					"label": _("Service Packages"),
					"description": _("Service packages list")
				},
				{
					"type": "doctype",
					"name": "Package Service",
					"label": _("Package Services"),
					"description": _("Package service relations")
				}
			]
		},
		{
			"label": _("Staff Management"),
			"items": [
				{
					"type": "page",
					"name": "photographers",
					"label": _("Photographers Management"),
					"description": _("Manage photographers")
				},
				{
					"type": "doctype",
					"name": "Photographer",
					"label": _("Photographers"),
					"description": _("Photographers list")
				},
				{
					"type": "doctype",
					"name": "Photographer Working Hours",
					"label": _("Working Hours"),
					"description": _("Photographer working hours")
				},
				{
					"type": "doctype",
					"name": "Photographer Holiday",
					"label": _("Holidays"),
					"description": _("Photographer holidays")
				},
				{
					"type": "doctype",
					"name": "Photographer Service",
					"label": _("Photographer Services"),
					"description": _("Photographer service relations")
				}
			]
		},
		{
			"label": _("User Management"),
			"items": [
				{
					"type": "page",
					"name": "users",
					"label": _("Users Management"),
					"description": _("Manage system users")
				},
				{
					"type": "doctype",
					"name": "User",
					"label": _("Users"),
					"description": _("System users")
				}
			]
		},
		{
			"label": _("Reports & Analytics"),
			"items": [
				{
					"type": "page",
					"name": "reports",
					"label": _("Reports Dashboard"),
					"description": _("View all reports and analytics")
				},
				{
					"type": "doctype",
					"name": "Booking Report",
					"label": _("Booking Reports"),
					"description": _("Detailed booking reports")
				},
				{
					"type": "page",
					"name": "booking-report-page",
					"label": _("Advanced Reports"),
					"description": _("Advanced booking reports")
				}
			]
		},
		{
			"label": _("System Settings"),
			"items": [
				{
					"type": "page",
					"name": "settings",
					"label": _("System Settings"),
					"description": _("Configure system settings")
				},
				{
					"type": "doctype",
					"name": "Booking Settings",
					"label": _("Booking Settings"),
					"description": _("Configure booking settings")
				}
			]
		}
	]
