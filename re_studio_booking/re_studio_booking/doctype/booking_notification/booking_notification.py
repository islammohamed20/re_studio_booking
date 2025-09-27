# Copyright (c) 2025, Re Studio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime

class BookingNotification(Document):
	def validate(self):
		"""Validate notification"""
		if not self.user:
			self.user = frappe.session.user
		
		if not self.created_date:
			self.created_date = datetime.now()
	
	def on_update(self):
		"""Update read status when notification is read"""
		if self.read_status and not self.read_date:
			self.read_date = datetime.now()
			self.status = "Read"

@frappe.whitelist()
def create_notification(title, message, notification_type, booking=None, user=None, priority="Medium"):
	"""Create a new notification"""
	if not user:
		user = frappe.session.user
	
	notification = frappe.get_doc({
		"doctype": "Booking Notification",
		"title": title,
		"message": message,
		"notification_type": notification_type,
		"booking": booking,
		"user": user,
		"priority": priority,
		"status": "Unread",
		"read_status": 0
	})
	
	notification.flags.ignore_permissions = True
	notification.insert()
	
	return notification

@frappe.whitelist()
def get_user_notifications(user=None, limit=50):
	"""Get notifications for a user"""
	if not user:
		user = frappe.session.user
	
	notifications = frappe.get_all(
		"Booking Notification",
		filters={"user": user},
		fields=["name", "title", "message", "notification_type", "priority", "status", "created_date", "booking", "read_status"],
		order_by="created_date desc",
		limit=limit
	)
	
	return notifications

@frappe.whitelist()
def get_unread_count(user=None):
	"""Get count of unread notifications for a user"""
	if not user:
		user = frappe.session.user
	
	count = frappe.db.count(
		"Booking Notification",
		filters={"user": user, "read_status": 0}
	)
	
	return count

@frappe.whitelist()
def mark_as_read(notification_name):
	"""Mark notification as read"""
	notification = frappe.get_doc("Booking Notification", notification_name)
	notification.read_status = 1
	notification.read_date = datetime.now()
	notification.status = "Read"
	notification.flags.ignore_permissions = True
	notification.save()
	
	return notification

@frappe.whitelist()
def mark_all_as_read(user=None):
	"""Mark all notifications as read for a user"""
	if not user:
		user = frappe.session.user
	
	frappe.db.sql("""
		UPDATE `tabBooking Notification`
		SET read_status = 1, read_date = %s, status = 'Read'
		WHERE user = %s AND read_status = 0
	""", (datetime.now(), user))
	
	frappe.db.commit()
	
	return {"message": "All notifications marked as read"}

@frappe.whitelist()
def delete_notification(notification_name):
	"""Delete a notification"""
	notification = frappe.get_doc("Booking Notification", notification_name)
	notification.flags.ignore_permissions = True
	notification.delete()
	
	return {"message": "Notification deleted"}

# Hooks for automatic notification creation
def create_booking_notification(doc, method):
	"""Create notification when booking is created/updated"""
	if method == "on_submit" or method == "after_insert":
		title = _("New Booking Created")
		message = _("Booking {0} has been created for client {1}").format(doc.name, doc.client)
		notification_type = "New Booking"
		priority = "High"
	
	elif method == "on_update":
		if doc.status == "Confirmed":
			title = _("Booking Confirmed")
			message = _("Booking {0} has been confirmed").format(doc.name)
			notification_type = "Booking Confirmed"
			priority = "Medium"
		elif doc.status == "Cancelled":
			title = _("Booking Cancelled")
			message = _("Booking {0} has been cancelled").format(doc.name)
			notification_type = "Booking Cancelled"
			priority = "High"
		else:
			return
	
	# Create notification for all Re Studio Managers
	managers = frappe.get_all("User", filters={"role_profile_name": "Re Studio Manager"}, fields=["name"])
	for manager in managers:
		create_notification(
			title=title,
			message=message,
			notification_type=notification_type,
			booking=doc.name,
			user=manager.name,
			priority=priority
		)

def create_payment_notification(doc, method):
	"""Create notification when payment is received"""
	if method == "on_submit":
		title = _("Payment Received")
		message = _("Payment of {0} received for booking {1}").format(doc.amount, doc.booking)
		notification_type = "Payment Received"
		priority = "Medium"
		
		# Create notification for all Re Studio Managers
		managers = frappe.get_all("User", filters={"role_profile_name": "Re Studio Manager"}, fields=["name"])
		for manager in managers:
			create_notification(
				title=title,
				message=message,
				notification_type=notification_type,
				booking=doc.booking,
				user=manager.name,
				priority=priority
			)