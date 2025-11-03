# -*- coding: utf-8 -*-
# Copyright (c) 2025, Masar Digital Group and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class OperationOrder(Document):
	def validate(self):
		"""التحقق من البيانات قبل الحفظ"""
		if not self.execution_times:
			frappe.throw(_("يجب إضافة مواعيد التنفيذ"))
		
		# تحديث تاريخ التنفيذ من أول تاريخ غير مكتمل
		self.update_execution_date()
	
	def on_update(self):
		"""تحديث تاريخ التنفيذ عند التحديث"""
		self.update_execution_date()
	
	def update_execution_date(self):
		"""تحديث تاريخ التنفيذ من أول تاريخ غير مكتمل"""
		if not self.execution_times:
			return
		
		# البحث عن أول تاريخ غير مكتمل
		for row in self.execution_times:
			if row.status != "مكتمل":
				self.execution_date = row.booking_date
				return
		
		# إذا كانت جميع التواريخ مكتملة، استخدم آخر تاريخ
		if self.execution_times:
			self.execution_date = self.execution_times[-1].booking_date
	
	def on_update_after_submit(self):
		"""تحديث حالة الحجز عند تغيير الحالة"""
		if self.status == "مكتمل":
			# يمكن إضافة منطق لتحديث حالة الحجز
			pass
	
	@frappe.whitelist()
	def load_booking_data(self):
		"""تحميل بيانات الحجز تلقائياً"""
		if not self.booking:
			return
		
		booking = frappe.get_doc("Booking", self.booking)
		
		# نسخ تواريخ الحجز
		self.execution_times = []
		if hasattr(booking, 'package_booking_dates') and booking.package_booking_dates:
			for date_row in booking.package_booking_dates:
				# حساب اسم اليوم من التاريخ
				day_name = ""
				if date_row.booking_date:
					from datetime import datetime
					date_obj = date_row.booking_date
					if isinstance(date_obj, str):
						date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
					day_name = date_obj.strftime('%A')  # اسم اليوم بالإنجليزية
				
				self.append("execution_times", {
					"booking_date": date_row.booking_date,
					"start_time": date_row.start_time,
					"end_time": date_row.end_time,
					"day_name": day_name,
					"status": "مجدول"
				})
		elif hasattr(booking, 'booking_date') and booking.booking_date:
			# في حالة Service booking
			# حساب اسم اليوم
			day_name = ""
			if booking.booking_date:
				from datetime import datetime
				date_obj = booking.booking_date
				if isinstance(date_obj, str):
					date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
				day_name = date_obj.strftime('%A')
			
			self.append("execution_times", {
				"booking_date": booking.booking_date,
				"start_time": booking.start_time if hasattr(booking, 'start_time') else None,
				"end_time": booking.end_time if hasattr(booking, 'end_time') else None,
				"day_name": day_name,
				"status": "مجدول"
			})
		
		# تحديث تاريخ التنفيذ
		if self.execution_times:
			self.execution_date = self.execution_times[0].booking_date
		
		# جلب أعضاء فريق التصوير
		self.team_members = []
		photographer_team = frappe.db.get_value("Booking", self.booking, "photographer_team")
		if photographer_team:
			team = frappe.get_doc("Photographer Team", photographer_team)
			if team.get('table_photographer'):
				for member in team.table_photographer:
					self.append("team_members", {
						"employee": member.get('employee'),
						"photographer": member.get('photographer', 0),
						"videographer": member.get('videographer', 0),
						"editor": member.get('editor', 0),
						"montage": member.get('montage', 0)
					})


@frappe.whitelist()
def make_operation_order(source_name, target_doc=None):
	"""إنشاء أمر تشغيل من الحجز"""
	from frappe.model.mapper import get_mapped_doc
	
	def set_missing_values(source, target):
		target.load_booking_data()
	
	doclist = get_mapped_doc("Booking", source_name, {
		"Booking": {
			"doctype": "Operation Order",
			"field_map": {
				"name": "booking",
				"client": "client",
				"client_name": "client_name",
				"booking_type": "booking_type",
				"package": "package"
			}
		}
	}, target_doc, set_missing_values, ignore_permissions=True)
	
	return doclist


@frappe.whitelist()
def get_booking_dates(booking):
	"""جلب تواريخ الحجز"""
	if not booking:
		return []
	
	dates = frappe.get_all("Booking Dates", 
		filters={"parent": booking},
		fields=["booking_date", "start_time", "end_time", "day_name"],
		order_by="booking_date")
	
	return dates
