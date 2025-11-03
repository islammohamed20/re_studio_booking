# -*- coding: utf-8 -*-
# Copyright (c) 2025, Masar Digital Group and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class Lead(Document):
	def before_insert(self):
		# تعيين lead_owner تلقائياً للمستخدم الحالي
		if not self.lead_owner:
			self.lead_owner = frappe.session.user
	
	def validate(self):
		# التحقق من وجود بريد إلكتروني أو رقم هاتف
		if not self.email_id and not self.phone and not self.mobile_no:
			frappe.throw("يجب إدخال البريد الإلكتروني أو رقم الهاتف على الأقل")
		
		# التحقق من صحة البريد الإلكتروني إذا تم إدخاله
		if self.email_id:
			from frappe.utils import validate_email_address
			if not validate_email_address(self.email_id, throw=False):
				frappe.throw(_("البريد الإلكتروني غير صحيح: {0}").format(self.email_id))

@frappe.whitelist()
def convert_to_client(lead_name):
	"""تحويل Lead إلى Client"""
	lead = frappe.get_doc("Lead", lead_name)
	
	# التحقق من عدم التحويل المسبق
	if lead.status == "Converted":
		frappe.throw(_("تم تحويل هذا العميل المحتمل مسبقاً"))
	
	# إنشاء Client جديد
	client = frappe.new_doc("Client")
	client.client_name = lead.lead_name
	client.email_id = lead.email_id
	client.phone = lead.phone
	client.mobile_no = lead.mobile_no
	client.city = lead.city
	client.state = lead.state
	client.country = lead.country
	
	# تعيين نوع العميل بناءً على organization_lead
	if lead.organization_lead:
		client.client_type = "Company"
	else:
		client.client_type = "Individual"
	
	client.insert(ignore_permissions=True)
	
	# تحديث حالة Lead
	lead.status = "Converted"
	lead.save(ignore_permissions=True)
	
	return client.name

@frappe.whitelist()
def make_quotation(source_name, target_doc=None):
	"""إنشاء Booking Quotation من Lead"""
	from frappe.model.mapper import get_mapped_doc
	
	def set_missing_values(source, target):
		target.quotation_to = "Lead"
		target.lead = source.name
		target.customer_email = source.email_id
		target.customer_phone = source.phone or source.mobile_no
	
	def update_lead_status(source, target, source_parent):
		# تحديث حالة Lead إلى Quotation
		frappe.db.set_value("Lead", source.name, "status", "Quotation")
	
	doclist = get_mapped_doc("Lead", source_name, {
		"Lead": {
			"doctype": "Booking Quotation",
			"field_map": {
				"name": "lead",
				"email_id": "customer_email",
				"phone": "customer_phone"
			}
		}
	}, target_doc, set_missing_values, ignore_permissions=True)
	
	# تحديث حالة Lead
	update_lead_status(None, None, None)
	
	return doclist

@frappe.whitelist()
def make_booking(source_name, target_doc=None):
	"""إنشاء Booking من Lead وتحويله إلى Client"""
	from frappe.model.mapper import get_mapped_doc
	
	# تحويل Lead إلى Client
	client_name = convert_to_client(source_name)
	
	def set_missing_values(source, target):
		target.client = client_name
		target.client_name = frappe.db.get_value("Client", client_name, "client_name")
		target.phone = source.phone
		target.mobile_no = source.mobile_no
		target.client_email = source.email_id
	
	doclist = get_mapped_doc("Lead", source_name, {
		"Lead": {
			"doctype": "Booking",
			"field_map": {
				"email_id": "client_email"
			}
		}
	}, target_doc, set_missing_values, ignore_permissions=True)
	
	return doclist
