# Copyright (c) 2024, MASAR TEAM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, today, getdate

class PriceList(Document):
	def validate(self):
		self.validate_dates()
		self.calculate_final_prices()
		self.validate_duplicate_items()

	def validate_dates(self):
		"""التحقق من صحة التواريخ"""
		if self.valid_from and self.valid_upto:
			if getdate(self.valid_from) > getdate(self.valid_upto):
				frappe.throw("تاريخ البداية يجب أن يكون قبل تاريخ النهاية")

	def calculate_final_prices(self):
		"""حساب الأسعار النهائية بعد الخصم"""
		for item in self.price_list_details:
			if item.discount_percentage:
				discount_amount = flt(item.price) * flt(item.discount_percentage) / 100
				item.final_price = flt(item.price) - discount_amount
			else:
				item.final_price = flt(item.price)

	def validate_duplicate_items(self):
		"""التحقق من عدم تكرار العناصر"""
		items = []
		for item in self.price_list_details:
			item_key = f"{item.item_type}:{item.service or item.service_package}"
			if item_key in items:
				frappe.throw(f"العنصر {item.service or item.service_package} مكرر في قائمة الأسعار")
			items.append(item_key)

	def is_valid(self):
		"""التحقق من صلاحية قائمة الأسعار"""
		if not self.enabled:
			return False
		
		today_date = getdate(today())
		
		if self.valid_from and getdate(self.valid_from) > today_date:
			return False
			
		if self.valid_upto and getdate(self.valid_upto) < today_date:
			return False
			
		return True

	def get_price(self, item_type, item_name):
		"""الحصول على سعر عنصر معين"""
		if not self.is_valid():
			return None
			
		for item in self.price_list_details:
			if item.item_type == item_type:
				if (item_type == "Service" and item.service == item_name) or \
				   (item_type == "Service Package" and item.service_package == item_name):
					return item.final_price
					
		return None

@frappe.whitelist()
def get_price_list_price(price_list, item_type, item_name):
	"""API للحصول على سعر من قائمة أسعار معينة"""
	price_list_doc = frappe.get_doc("Price List", price_list)
	return price_list_doc.get_price(item_type, item_name)

@frappe.whitelist()
def get_client_price_list(client):
	"""الحصول على قائمة أسعار العميل"""
	client_doc = frappe.get_doc("Client", client)
	return getattr(client_doc, 'price_list', None)

@frappe.whitelist()
def get_applicable_price(client, item_type, item_name):
	"""الحصول على السعر المطبق للعميل"""
	# محاولة الحصول على قائمة أسعار العميل
	client_price_list = get_client_price_list(client)
	
	if client_price_list:
		price = get_price_list_price(client_price_list, item_type, item_name)
		if price is not None:
			return {
				"price": price,
				"price_list": client_price_list,
				"source": "Client Price List"
			}
	
	# إذا لم توجد قائمة أسعار للعميل، استخدم السعر الافتراضي
	if item_type == "Service":
		service = frappe.get_doc("Service", item_name)
		return {
			"price": service.discount_price or service.price,
			"price_list": None,
			"source": "Default Service Price"
		}
	elif item_type == "Service Package":
		package = frappe.get_doc("Service Package", item_name)
		return {
			"price": package.discount_price or package.price,
			"price_list": None,
			"source": "Default Package Price"
		}
	
	return None