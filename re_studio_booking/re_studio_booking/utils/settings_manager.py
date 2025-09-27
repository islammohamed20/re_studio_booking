# Copyright (c) 2024, Masar Digital Group and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from typing import Dict, Any, Optional

class SettingsManager:
    """
    Unified Settings Manager for Re Studio Booking
    Provides centralized access to all settings from General Settings DocType
    """
    
    _instance = None
    _settings_cache = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._settings_cache = None
    
    def get_settings(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get all settings from General Settings with caching
        
        Args:
            force_refresh: Force refresh cache
            
        Returns:
            Dict containing all settings
        """
        if self._settings_cache is None or force_refresh:
            try:
                settings_doc = frappe.get_single("General Settings")
                self._settings_cache = settings_doc.as_dict()
            except Exception as e:
                frappe.log_error(f"Error loading settings: {str(e)}")
                self._settings_cache = self._get_default_settings()
        
        return self._settings_cache
    
    def get_currency_settings(self) -> Dict[str, Any]:
        """
        Get currency-related settings
        """
        settings = self.get_settings()
        return {
            "default_currency": settings.get("default_currency", "SAR"),
            "currency_symbol": settings.get("currency_symbol", "ر.س"),
            "currency_position": settings.get("currency_position", "Right"),
            "decimal_places": settings.get("decimal_places", 2),
            "number_format": settings.get("number_format", "#,###.##"),
            "thousand_separator": settings.get("thousand_separator", ",")
        }
    
    def get_company_settings(self) -> Dict[str, Any]:
        """
        Get company-related settings
        """
        settings = self.get_settings()
        return {
            "company_name": settings.get("company_name", ""),
            "company_name_ar": settings.get("company_name_ar", ""),
            "company_logo": settings.get("company_logo", ""),
            "company_email": settings.get("company_email", ""),
            "company_website": settings.get("company_website", "")
        }
    
    def get_localization_settings(self) -> Dict[str, Any]:
        """
        Get localization-related settings
        """
        settings = self.get_settings()
        return {
            "country": settings.get("country", "Saudi Arabia"),
            "timezone": settings.get("timezone", "Asia/Riyadh"),
            "date_format": settings.get("date_format", "dd/mm/yyyy"),
            "time_format": settings.get("time_format", "HH:mm"),
            "language": settings.get("language", "ar")
        }
    
    def get_pricing_settings(self) -> Dict[str, Any]:
        """
        Get pricing and tax-related settings
        """
        settings = self.get_settings()
        return {
            "tax_rate": settings.get("tax_rate", 15.0),
            "include_tax_in_price": settings.get("include_tax_in_price", 0),
            "minimum_booking_amount": settings.get("minimum_booking_amount", 100.0),
            "deposit_percentage": settings.get("deposit_percentage", 30.0),
            "payment_terms": settings.get("payment_terms", "يجب دفع 30% عربون عند الحجز والباقي عند التسليم")
        }
    
    def get_booking_settings(self) -> Dict[str, Any]:
        """
        Get booking-specific settings from Booking Settings DocType
        (These remain in Booking Settings as they are booking-specific)
        """
        try:
            booking_settings = frappe.get_single("Booking Settings")
            return {
                "business_start_time": booking_settings.get("business_start_time"),
                "business_end_time": booking_settings.get("business_end_time"),
                "time_slot_duration": booking_settings.get("time_slot_duration", 60),
                "advance_booking_days": booking_settings.get("advance_booking_days", 30),
                "cancellation_hours": booking_settings.get("cancellation_hours", 24),
                "auto_confirm_bookings": booking_settings.get("auto_confirm_bookings", 1),
                "booking_buffer_time": booking_settings.get("booking_buffer_time", 0)
            }
        except Exception as e:
            frappe.log_error(f"Error loading booking settings: {str(e)}")
            return self._get_default_booking_settings()
    
    def format_currency(self, amount: float, include_symbol: bool = True) -> str:
        """
        Format amount according to currency settings
        
        Args:
            amount: Amount to format
            include_symbol: Whether to include currency symbol
            
        Returns:
            Formatted currency string
        """
        currency_settings = self.get_currency_settings()
        
        # Format number according to settings
        decimal_places = currency_settings["decimal_places"]
        thousand_separator = currency_settings["thousand_separator"]
        
        # Format the number
        formatted_amount = f"{amount:,.{decimal_places}f}"
        
        # Replace comma with thousand separator if different
        if thousand_separator != ",":
            formatted_amount = formatted_amount.replace(",", thousand_separator)
        
        if include_symbol:
            symbol = currency_settings["currency_symbol"]
            position = currency_settings["currency_position"]
            
            if position == "Left":
                return f"{symbol} {formatted_amount}"
            else:
                return f"{formatted_amount} {symbol}"
        
        return formatted_amount
    
    def calculate_tax(self, amount: float) -> Dict[str, float]:
        """
        Calculate tax based on pricing settings
        
        Args:
            amount: Base amount
            
        Returns:
            Dict with tax_amount, total_amount, and tax_rate
        """
        pricing_settings = self.get_pricing_settings()
        tax_rate = pricing_settings["tax_rate"]
        include_tax = pricing_settings["include_tax_in_price"]
        
        if include_tax:
            # Tax is included in the price
            tax_amount = amount * (tax_rate / (100 + tax_rate))
            base_amount = amount - tax_amount
            total_amount = amount
        else:
            # Tax is added to the price
            tax_amount = amount * (tax_rate / 100)
            base_amount = amount
            total_amount = amount + tax_amount
        
        return {
            "base_amount": base_amount,
            "tax_amount": tax_amount,
            "total_amount": total_amount,
            "tax_rate": tax_rate
        }
    
    def calculate_deposit(self, total_amount: float) -> Dict[str, float]:
        """
        Calculate deposit amount based on settings
        
        Args:
            total_amount: Total booking amount
            
        Returns:
            Dict with deposit_amount and remaining_amount
        """
        pricing_settings = self.get_pricing_settings()
        deposit_percentage = pricing_settings["deposit_percentage"]
        
        deposit_amount = total_amount * (deposit_percentage / 100)
        remaining_amount = total_amount - deposit_amount
        
        return {
            "deposit_amount": deposit_amount,
            "remaining_amount": remaining_amount,
            "deposit_percentage": deposit_percentage
        }
    
    def refresh_cache(self):
        """
        Force refresh settings cache
        """
        self._settings_cache = None
        self.get_settings(force_refresh=True)
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """
        Get default settings if General Settings doesn't exist
        """
        return {
            "default_currency": "SAR",
            "currency_symbol": "ر.س",
            "currency_position": "Right",
            "decimal_places": 2,
            "number_format": "#,###.##",
            "thousand_separator": ",",
            "country": "Saudi Arabia",
            "timezone": "Asia/Riyadh",
            "date_format": "dd/mm/yyyy",
            "time_format": "HH:mm",
            "language": "ar",
            "tax_rate": 15.0,
            "include_tax_in_price": 0,
            "minimum_booking_amount": 100.0,
            "deposit_percentage": 30.0,
            "payment_terms": "يجب دفع 30% عربون عند الحجز والباقي عند التسليم",
            "company_name": "",
            "company_name_ar": "",
            "company_logo": "",
            "company_email": "",
            "company_website": ""
        }
    
    def _get_default_booking_settings(self) -> Dict[str, Any]:
        """
        Get default booking settings
        """
        return {
            "business_start_time": "09:00:00",
            "business_end_time": "18:00:00",
            "time_slot_duration": 60,
            "advance_booking_days": 30,
            "cancellation_hours": 24,
            "auto_confirm_bookings": 1,
            "booking_buffer_time": 0
        }

# Global instance
settings_manager = SettingsManager()

# Convenience functions for backward compatibility
def get_currency_settings():
    """Get currency settings - backward compatibility function"""
    return settings_manager.get_currency_settings()

def get_company_settings():
    """Get company settings - backward compatibility function"""
    return settings_manager.get_company_settings()

def get_pricing_settings():
    """Get pricing settings - backward compatibility function"""
    return settings_manager.get_pricing_settings()

def format_currency(amount, include_symbol=True):
    """Format currency - backward compatibility function"""
    return settings_manager.format_currency(amount, include_symbol)

def calculate_tax(amount):
    """Calculate tax - backward compatibility function"""
    return settings_manager.calculate_tax(amount)

def calculate_deposit(total_amount):
    """Calculate deposit - backward compatibility function"""
    return settings_manager.calculate_deposit(total_amount)

# Migration function
def migrate_settings():
	"""Migrate settings from other DocTypes to Currency Settings (renamed to General Settings)"""
	print("Starting settings migration...")
	
	try:
		# Get Currency Settings (which is our General Settings)
		general_settings = frappe.get_single("Currency Settings")
		
		# Try to get Booking Settings and migrate currency settings
		try:
			booking_settings = frappe.get_single("Booking Settings")
			if hasattr(booking_settings, 'default_currency') and booking_settings.default_currency:
				general_settings.default_currency = booking_settings.default_currency
			if hasattr(booking_settings, 'currency_symbol') and booking_settings.currency_symbol:
				general_settings.currency_symbol = booking_settings.currency_symbol
			if hasattr(booking_settings, 'tax_rate') and booking_settings.tax_rate:
				general_settings.tax_rate = booking_settings.tax_rate
			print("✓ Migrated currency settings from Booking Settings")
		except Exception as e:
			print(f"⚠ Could not migrate from Booking Settings: {str(e)}")
		
		# Try to get Print Settings and migrate company settings
		try:
			print_settings = frappe.get_single("Print Settings")
			if hasattr(print_settings, 'company_name') and print_settings.company_name:
				general_settings.company_name = print_settings.company_name
			if hasattr(print_settings, 'company_logo') and print_settings.company_logo:
				general_settings.company_logo = print_settings.company_logo
			print("✓ Migrated company settings from Print Settings")
		except Exception as e:
			print(f"⚠ Could not migrate from Print Settings: {str(e)}")
		
		# Save General Settings
		general_settings.save()
		frappe.db.commit()
		
		print("✓ Settings migration completed successfully!")
		return "Migration completed successfully"
		
	except Exception as e:
		print(f"✗ Migration failed: {str(e)}")
		frappe.db.rollback()
		return f"Migration failed: {str(e)}"