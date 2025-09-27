app_name = "re_studio_booking"
app_title = "Re Studio Booking"
app_publisher = "Masar Digital Group"
app_description = "Booking & Studio Management System"
app_email = "support@re-studio.app"
app_license = "MIT"
app_icon_url = "/assets/re_studio_booking/images/logo.svg"
app_icon_title = "Re Studio"

# Apps
# ------------------

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "re_studio_booking",
		"logo": "/assets/re_studio_booking/images/logo.svg",
		"title": "Re Studio Booking",
		"has_permission": "re_studio_booking.re_studio_booking.setup.install.has_app_permission"
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = [
    "/assets/re_studio_booking/css/re_studio_booking.css",
    "/assets/re_studio_booking/css/admin_dashboard.css",
    "/assets/re_studio_booking/css/sidebar.css",
    "/assets/re_studio_booking/css/dialogs.css",
    "/assets/re_studio_booking/css/modern-calendar.css"
]
app_include_js = [
    "/assets/re_studio_booking/js/re_studio_booking.js",
    "/assets/re_studio_booking/js/admin_dashboard_charts.js",
    "/assets/re_studio_booking/js/admin_dashboard_utils.js",
    "/assets/re_studio_booking/js/dialogs.js",
    "/assets/re_studio_booking/js/booking-form.js"
]

# Website Settings
# ------------------
home_page = ""

# Setup Wizard
# ------------------
setup_wizard_requires = "/assets/re_studio_booking/js/setup_wizard.js"
setup_wizard_stages = "re_studio_booking.setup_wizard.setup_wizard.get_setup_stages"
setup_wizard_complete = "re_studio_booking.setup_wizard.setup_wizard.setup_complete"

# include js, css files in header of web template
web_include_css = [
    "/assets/re_studio_booking/css/re_studio_booking.css",
    "/assets/re_studio_booking/css/sidebar.css",
    "/assets/re_studio_booking/css/dialogs.css",
    "/assets/re_studio_booking/css/modern-calendar.css"
]
web_include_js = [
    "/assets/re_studio_booking/js/re_studio_booking.js",
    "/assets/re_studio_booking/js/dialogs.js",
    "/assets/re_studio_booking/js/booking-form.js"
]

# Website route rules
website_route_rules = [
	{"from_route": "/re_studio_booking/dashboard", "to_route": "/dashboard"},
	{"from_route": "/re_studio_booking/booking-dashboard", "to_route": "/booking-dashboard"},
	{"from_route": "/re_studio_booking/services", "to_route": "/services"},
	{"from_route": "/re_studio_booking/photographers", "to_route": "/photographers"},
	{"from_route": "/re_studio_booking/bookings", "to_route": "/bookings"},
	{"from_route": "/re_studio_booking/categories", "to_route": "/categories"},
	{"from_route": "/re_studio_booking/packages", "to_route": "/packages"},
	{"from_route": "/re_studio_booking/users", "to_route": "/users"},
	{"from_route": "/re_studio_booking/settings", "to_route": "/settings"},
	{"from_route": "/re_studio_booking/reports", "to_route": "/reports"},
	{"from_route": "/re_studio_booking/service-analysis", "to_route": "/service-analysis"},
	{"from_route": "/re_studio_booking/photographer-performance", "to_route": "/photographer-performance"},
	{"from_route": "/re_studio_booking/revenue-report", "to_route": "/revenue-report"},
	{"from_route": "/re_studio_booking/payment-method", "to_route": "/payment-method"},
	{"from_route": "/re_studio_booking/booking-time-slot", "to_route": "/booking-time-slot"},
	{"from_route": "/re_studio_booking/currency-settings", "to_route": "/currency-settings"},
]

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "re_studio_booking/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
page_js = {
	"booking-dashboard": "public/js/booking_dashboard.js",
	"booking-report-page": "public/js/booking_report_page.js",
	"admin-dashboard": "public/js/admin_dashboard_charts.js"
}

# include js in doctype views
doctype_js = {
	"Booking" : ["public/js/booking.js", "public/js/booking_debug.js"],
	"Photographer" : "public/js/photographer.js"
}
doctype_list_js = {
	"Booking" : "public/js/booking_list.js"
}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
doctype_calendar_js = {"Booking" : "public/js/booking_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "re_studio_booking/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "dashboard"

# website user home page (by Role)
role_home_page = {
	"Re Studio Manager": "admin-dashboard",
	"Re Studio Agent": "booking-dashboard",
	"Re Studio Customer": "bookings"
}

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "re_studio_booking.utils.jinja_methods",
# 	"filters": "re_studio_booking.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "re_studio_booking.install.before_install"
after_install = "re_studio_booking.re_studio_booking.setup.install.after_install"

# Fixtures
# --------

fixtures = [
	{"dt": "Workspace", "filters": [["module", "in", ["Re Studio Booking"]]]}
]

# Uninstallation
# ------------

# before_uninstall = "re_studio_booking.uninstall.before_uninstall"
# after_uninstall = "re_studio_booking.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "re_studio_booking.utils.before_app_install"
# after_app_install = "re_studio_booking.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "re_studio_booking.utils.before_app_uninstall"
# after_app_uninstall = "re_studio_booking.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "re_studio_booking.notifications.get_notification_config"

# Desk Sidebar Items
# ------------------
# Specify which sidebar items should appear in the desk
desk_sidebar_items = {
    "Re Studio Booking": "re_studio_booking.re_studio_booking.config.re_studio_booking.get_data"
}

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"re_studio_booking.tasks.all"
# 	],
# 	"daily": [
# 		"re_studio_booking.tasks.daily"
# 	],
# 	"hourly": [
# 		"re_studio_booking.tasks.hourly"
# 	],
# 	"weekly": [
# 		"re_studio_booking.tasks.weekly"
# 	],
# 	"monthly": [
# 		"re_studio_booking.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "re_studio_booking.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "re_studio_booking.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "re_studio_booking.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["re_studio_booking.utils.before_request"]
# after_request = ["re_studio_booking.utils.after_request"]

# Job Events
# ----------
# before_job = ["re_studio_booking.utils.before_job"]
# after_job = ["re_studio_booking.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"re_studio_booking.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Document Events
# ---------------

doc_events = {
	"Service": {
		"after_insert": "re_studio_booking.re_studio_booking.hooks_realtime.on_service_update",
		"on_update": "re_studio_booking.re_studio_booking.hooks_realtime.on_service_update",
		"validate": "re_studio_booking.re_studio_booking.hooks_realtime.validate_service_deactivation"
	},
	"Service Package": {
		"after_insert": "re_studio_booking.re_studio_booking.hooks_realtime.on_service_package_update",
		"on_update": "re_studio_booking.re_studio_booking.hooks_realtime.on_service_package_update",
		"validate": "re_studio_booking.re_studio_booking.hooks_realtime.validate_package_deactivation"
	}
}

