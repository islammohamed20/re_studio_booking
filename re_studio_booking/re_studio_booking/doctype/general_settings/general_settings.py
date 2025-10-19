# Copyright (c) 2024, Masar Digital Group and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class GeneralSettings(Document):
	"""General Settings DocType for Re Studio Booking"""
	
	def validate(self):
		"""Validate settings before saving"""
		self.validate_business_hours()
		self.validate_currency_settings()
		self.validate_booking_settings()
	
	def validate_business_hours(self):
		"""Validate business hours"""
		if self.business_start_time and self.business_end_time:
			if self.business_start_time >= self.business_end_time:
				frappe.throw(_("Business start time must be before end time"))
	
	def validate_currency_settings(self):
		"""Validate currency settings"""
		if self.tax_rate and (self.tax_rate < 0 or self.tax_rate > 100):
			frappe.throw(_("Tax rate must be between 0 and 100"))
		
		if self.deposit_percentage and (self.deposit_percentage < 0 or self.deposit_percentage > 100):
			frappe.throw(_("Deposit percentage must be between 0 and 100"))
	
	def validate_booking_settings(self):
		"""Validate booking settings"""
		if self.time_slot_duration and self.time_slot_duration <= 0:
			frappe.throw(_("Time slot duration must be greater than 0"))
		
		if self.advance_booking_days and self.advance_booking_days < 0:
			frappe.throw(_("Advance booking days cannot be negative"))
		
		if self.cancellation_hours and self.cancellation_hours < 0:
			frappe.throw(_("Cancellation hours cannot be negative"))
		
		if self.booking_buffer_time and self.booking_buffer_time < 0:
			frappe.throw(_("Booking buffer time cannot be negative"))

@frappe.whitelist()
def get_general_settings():
	"""Get General Settings"""
	try:
		settings = frappe.get_single("General Settings")
		return settings
	except Exception as e:
		frappe.log_error(f"Error getting general settings: {str(e)}")
		return None

@frappe.whitelist()
def get_company_settings():
	"""Get company settings from General Settings"""
	try:
		settings = frappe.get_single("General Settings")
		return {
			"company_name": settings.get("company_name"),
			"company_name_ar": settings.get("company_name_ar"),
			"company_logo": settings.get("company_logo"),
			"company_address": settings.get("company_address"),
			"company_phone": settings.get("company_phone"),
			"company_email": settings.get("company_email"),
			"company_website": settings.get("company_website")
		}
	except Exception as e:
		frappe.log_error(f"Error getting company settings: {str(e)}")
		return {}

@frappe.whitelist()
def get_currency_settings():
	"""Get currency settings from General Settings"""
	try:
		settings = frappe.get_single("General Settings")
		return {
			"default_currency": settings.get("default_currency", "SAR"),
			"currency_symbol": settings.get("currency_symbol", "ر.س"),
			"currency_position": settings.get("currency_position", "Right"),
			"decimal_places": settings.get("decimal_places", 2),
			"number_format": settings.get("number_format", "#,###.##"),
			"thousand_separator": settings.get("thousand_separator", ",")
		}
	except Exception as e:
		frappe.log_error(f"Error getting currency settings: {str(e)}")
		return {
			"default_currency": "SAR",
			"currency_symbol": "ر.س",
			"currency_position": "Right",
			"decimal_places": 2,
			"number_format": "#,###.##",
			"thousand_separator": ","
		}

@frappe.whitelist()
def get_pricing_settings():
	"""Get pricing settings from General Settings"""
	try:
		settings = frappe.get_single("General Settings")
		return {
			"tax_rate": settings.get("tax_rate", 15),
			"include_tax_in_price": settings.get("include_tax_in_price", 0),
			"tax_label": settings.get("tax_label", "ضريبة القيمة المضافة"),
			"minimum_booking_amount": settings.get("minimum_booking_amount", 100),
			"deposit_percentage": settings.get("deposit_percentage", 30),
			"payment_terms": settings.get("payment_terms", "يجب دفع 30% عربون عند الحجز والباقي عند التسليم")
		}
	except Exception as e:
		frappe.log_error(f"Error getting pricing settings: {str(e)}")
		return {
			"tax_rate": 15,
			"include_tax_in_price": 0,
			"tax_label": "ضريبة القيمة المضافة",
			"minimum_booking_amount": 100,
			"deposit_percentage": 30,
			"payment_terms": "يجب دفع 30% عربون عند الحجز والباقي عند التسليم"
		}

@frappe.whitelist()
def get_booking_settings():
	"""Get booking settings from General Settings"""
	try:
		settings = frappe.get_single("General Settings")
		return {
			"business_start_time": settings.get("business_start_time", "09:00:00"),
			"business_end_time": settings.get("business_end_time", "18:00:00"),
			"first_day_of_week": settings.get("first_day_of_week", "Sunday"),
			"time_slot_duration": settings.get("time_slot_duration", 60),
			"advance_booking_days": settings.get("advance_booking_days", 30),
			"max_days_in_advance": settings.get("max_days_in_advance", 90),
			"allow_cancellation": settings.get("allow_cancellation", 1),
			"cancellation_hours": settings.get("cancellation_hours", 24),
			"booking_buffer_time": settings.get("booking_buffer_time", 0),
			"auto_confirm_bookings": settings.get("auto_confirm_bookings", 1),
			"enable_service_selection": settings.get("enable_service_selection", 1),
			"enable_agent_selection": settings.get("enable_agent_selection", 1),
			"enable_date_time_selection": settings.get("enable_date_time_selection", 1),
			"enable_customer_info": settings.get("enable_customer_info", 1),
			"enable_customer_dashboard": settings.get("enable_customer_dashboard", 1),
			"enable_agent_dashboard": settings.get("enable_agent_dashboard", 1),
			"working_days": {
				"saturday": settings.get("saturday", 1),
				"sunday": settings.get("sunday", 1),
				"monday": settings.get("monday", 1),
				"tuesday": settings.get("tuesday", 1),
				"wednesday": settings.get("wednesday", 1),
				"thursday": settings.get("thursday", 1),
				"friday": settings.get("friday", 0)
			}
		}
	except Exception as e:
		frappe.log_error(f"Error getting booking settings: {str(e)}")
		return {
			"business_start_time": "09:00:00",
			"business_end_time": "18:00:00",
			"first_day_of_week": "Sunday",
			"time_slot_duration": 60,
			"advance_booking_days": 30,
			"max_days_in_advance": 90,
			"allow_cancellation": 1,
			"cancellation_hours": 24,
			"booking_buffer_time": 0,
			"auto_confirm_bookings": 1,
			"enable_service_selection": 1,
			"enable_agent_selection": 1,
			"enable_date_time_selection": 1,
			"enable_customer_info": 1,
			"enable_customer_dashboard": 1,
			"enable_agent_dashboard": 1,
			"working_days": {
				"saturday": 1,
				"sunday": 1,
				"monday": 1,
				"tuesday": 1,
				"wednesday": 1,
				"thursday": 1,
				"friday": 0
			}
		}

@frappe.whitelist()
def get_notification_settings():
	"""Get notification settings from General Settings"""
	try:
		settings = frappe.get_single("General Settings")
		return {
			"send_confirmation_email": settings.get("send_confirmation_email", 1),
			"send_reminder_email": settings.get("send_reminder_email", 1),
			"send_sms_notifications": settings.get("send_sms_notifications", 1),
			"send_email_notifications": settings.get("send_email_notifications", 1),
			"reminder_hours": settings.get("reminder_hours", 24),
			"admin_email": settings.get("admin_email"),
			"sms_api_key": settings.get("sms_api_key"),
			"email_template": settings.get("email_template")
		}
	except Exception as e:
		frappe.log_error(f"Error getting notification settings: {str(e)}")
		return {
			"send_confirmation_email": 1,
			"send_reminder_email": 1,
			"send_sms_notifications": 1,
			"send_email_notifications": 1,
			"reminder_hours": 24,
			"admin_email": None,
			"sms_api_key": None,
			"email_template": None
		}

@frappe.whitelist()
def get_print_settings():
	"""Get print settings from General Settings"""
	try:
		settings = frappe.get_single("General Settings")
		return {
			"show_company_logo": settings.get("show_company_logo", 1),
			"show_company_name": settings.get("show_company_name", 1),
			"show_print_date": settings.get("show_print_date", 1),
			"show_page_numbers": settings.get("show_page_numbers", 1),
			"booking_print_format": settings.get("booking_print_format", "Standard"),
			"include_customer_details": settings.get("include_customer_details", 1),
			"include_service_details": settings.get("include_service_details", 1),
			"include_photographer_details": settings.get("include_photographer_details", 1),
			"include_payment_details": settings.get("include_payment_details", 1),
			"include_notes": settings.get("include_notes", 0),
			"show_qr_code": settings.get("show_qr_code", 0),
			"custom_footer_text": settings.get("custom_footer_text"),
			"receipt_format": settings.get("receipt_format", "Thermal"),
			"receipt_paper_size": settings.get("receipt_paper_size", "80mm"),
			"receipt_font_size": settings.get("receipt_font_size", 12),
			"auto_print_receipt": settings.get("auto_print_receipt", 0),
			"receipt_copies": settings.get("receipt_copies", 1),
			"thermal_printer_settings": settings.get("thermal_printer_settings"),
			"pdf_page_size": settings.get("pdf_page_size", "A4"),
			"pdf_orientation": settings.get("pdf_orientation", "Portrait"),
			"pdf_margins": settings.get("pdf_margins", "20mm"),
			"pdf_font": settings.get("pdf_font", "Arial"),
			"pdf_font_size": settings.get("pdf_font_size", 12),
			"enable_watermark": settings.get("enable_watermark", 0),
			"watermark_text": settings.get("watermark_text")
		}
	except Exception as e:
		frappe.log_error(f"Error getting print settings: {str(e)}")
		return {
			"show_company_logo": 1,
			"show_company_name": 1,
			"show_print_date": 1,
			"show_page_numbers": 1,
			"booking_print_format": "Standard",
			"include_customer_details": 1,
			"include_service_details": 1,
			"include_photographer_details": 1,
			"include_payment_details": 1,
			"include_notes": 0,
			"show_qr_code": 0,
			"custom_footer_text": None,
			"receipt_format": "Thermal",
			"receipt_paper_size": "80mm",
			"receipt_font_size": 12,
			"auto_print_receipt": 0,
			"receipt_copies": 1,
			"thermal_printer_settings": None,
			"pdf_page_size": "A4",
			"pdf_orientation": "Portrait",
			"pdf_margins": "20mm",
			"pdf_font": "Arial",
			"pdf_font_size": 12,
			"enable_watermark": 0,
			"watermark_text": None
		}

@frappe.whitelist()
def format_currency(amount, currency_settings=None):
	"""Format currency amount according to settings"""
	try:
		if not currency_settings:
			currency_settings = get_currency_settings()
		
		if not amount:
			return "0"
		
		# Format the number
		decimal_places = currency_settings.get("decimal_places", 2)
		formatted_amount = f"{float(amount):.{decimal_places}f}"
		
		# Add thousand separator
		thousand_separator = currency_settings.get("thousand_separator", ",")
		if thousand_separator:
			parts = formatted_amount.split(".")
			integer_part = parts[0]
			decimal_part = parts[1] if len(parts) > 1 else ""
			
			# Add thousand separators
			integer_with_separators = ""
			for i, digit in enumerate(reversed(integer_part)):
				if i > 0 and i % 3 == 0:
					integer_with_separators = thousand_separator + integer_with_separators
				integer_with_separators = digit + integer_with_separators
			
			formatted_amount = integer_with_separators
			if decimal_part:
				formatted_amount += "." + decimal_part
		
		# Add currency symbol
		currency_symbol = currency_settings.get("currency_symbol", "ر.س")
		currency_position = currency_settings.get("currency_position", "Right")
		
		if currency_position == "Left":
			return f"{currency_symbol} {formatted_amount}"
		else:
			return f"{formatted_amount} {currency_symbol}"
		
	except Exception as e:
		frappe.log_error(f"Error formatting currency: {str(e)}")
		return f"{amount} ر.س"