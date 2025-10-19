# Copyright (c) 2025, Masar Digital Group and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class PaymentMethod(Document):
	def validate(self):
		self._normalize_display_name()
		self._validate_category_specifics()
		self._validate_amount_limits()
		self._validate_fees()

	def _normalize_display_name(self):
		display_name = getattr(self, "display_name", None)
		if not display_name:
			parts = [self.method_name]
			if getattr(self, "method_category", None):
				parts.append(self.method_category)
			if getattr(self, "provider", None):
				parts.append(self.provider)
			self.display_name = " - ".join([p for p in parts if p])

	def _validate_category_specifics(self):
		if self.method_category == "Card":
			networks = self.get("supported_networks") or []
			if not networks:
				frappe.throw("برجاء تحديد شبكات البطاقات المدعومة (Visa/Mastercard/...).")
			if self.requires_3ds is None:
				self.requires_3ds = 1
		elif self.method_category == "Wallet":
			if not self.wallet_provider:
				frappe.throw("برجاء اختيار مزود المحفظة الإلكترونية.")

	def _validate_amount_limits(self):
		if self.min_amount and self.max_amount and flt(self.min_amount) > flt(self.max_amount):
			frappe.throw("الحد الأدنى لا يجب أن يتجاوز الحد الأقصى.")

	def _validate_fees(self):
		# تأكد من أن الرسوم ليست سالبة
		if self.percentage_fee is not None and flt(self.percentage_fee) < 0:
			frappe.throw("نسبة الرسوم يجب أن تكون 0 أو أكبر.")
		if self.fixed_fee is not None and flt(self.fixed_fee) < 0:
			frappe.throw("الرسوم الثابتة يجب أن تكون 0 أو أكبر.")

@frappe.whitelist()
def _test_create_payment_method():
	doc = frappe.get_doc({
		"doctype": "Payment Method",
		"method_name": "Dev Test Card",
		"method_category": "Card",
		"provider": "TestProvider",
		"supported_networks": [{"doctype": "Payment Method Network", "network": "Visa"}],
		"requires_3ds": 1,
		"is_active": 1
	})
	doc.insert()
	return doc.name
