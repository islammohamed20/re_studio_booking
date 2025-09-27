# Copyright (c) 2025, Re Studio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class UserSettings(Document):
	def validate(self):
		"""Validate user settings"""
		self.validate_user_exists()
		self.validate_unique_user()
		self.validate_session_timeout()
		self.validate_password_expiry()
	
	def validate_user_exists(self):
		"""Check if user exists"""
		if not frappe.db.exists("User", self.user):
			frappe.throw(_("User {0} does not exist").format(self.user))
	
	def validate_unique_user(self):
		"""Ensure one settings record per user"""
		if self.is_new():
			existing = frappe.db.exists("User Settings", {"user": self.user})
			if existing:
				frappe.throw(_("User Settings already exists for user {0}").format(self.user))
	
	def validate_session_timeout(self):
		"""Validate session timeout value"""
		if self.session_timeout and (self.session_timeout < 30 or self.session_timeout > 1440):
			frappe.throw(_("Session timeout must be between 30 and 1440 minutes"))
	
	def validate_password_expiry(self):
		"""Validate password expiry value"""
		if self.password_expiry_days and (self.password_expiry_days < 30 or self.password_expiry_days > 365):
			frappe.throw(_("Password expiry must be between 30 and 365 days"))
	
	def on_update(self):
		"""Update user preferences when settings are saved"""
		self.update_user_preferences()
	
	def update_user_preferences(self):
		"""Update user document with preferences"""
		user_doc = frappe.get_doc("User", self.user)
		
		# Update language preference
		if self.default_language:
			user_doc.language = self.default_language
		
		# Update time zone
		if self.timezone:
			user_doc.time_zone = self.timezone
		
		# Save user document
		user_doc.flags.ignore_permissions = True
		user_doc.save()

@frappe.whitelist()
def get_user_settings(user=None):
	"""Get user settings for a specific user"""
	if not user:
		user = frappe.session.user
	
	settings = frappe.db.get_value("User Settings", {"user": user}, "*", as_dict=True)
	if not settings:
		# Create default settings if not exists
		settings = create_default_user_settings(user)
	
	return settings

@frappe.whitelist()
def create_default_user_settings(user):
	"""Create default user settings"""
	user_info = frappe.get_doc("User", user)
	
	settings = frappe.get_doc({
		"doctype": "User Settings",
		"user": user,
		"full_name": user_info.full_name,
		"email": user_info.email,
		"enable_email_notifications": 1,
		"enable_booking_notifications": 1,
		"enable_payment_notifications": 1,
		"default_language": "ar",
		"timezone": "Asia/Riyadh",
		"date_format": "dd-mm-yyyy",
		"time_format": "HH:mm",
		"session_timeout": 480,
		"password_expiry_days": 90,
		"login_attempts": 5
	})
	
	settings.flags.ignore_permissions = True
	settings.insert()
	
	return settings.as_dict()

@frappe.whitelist()
def update_notification_settings(user, settings):
	"""Update notification settings for user"""
	user_settings = frappe.get_doc("User Settings", {"user": user})
	
	for key, value in settings.items():
		if hasattr(user_settings, key):
			setattr(user_settings, key, value)
	
	user_settings.flags.ignore_permissions = True
	user_settings.save()
	
	return user_settings.as_dict()