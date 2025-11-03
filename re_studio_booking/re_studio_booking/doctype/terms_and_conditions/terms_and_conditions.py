# Copyright (c) 2025, Re Studio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TermsandConditions(Document):
	def validate(self):
		"""التحقق من وجود شروط افتراضية واحدة فقط"""
		if self.default:
			# إلغاء تفعيل default من جميع الشروط الأخرى
			frappe.db.sql("""
				UPDATE `tabTerms and Conditions`
				SET `default` = 0
				WHERE name != %s AND `default` = 1
			""", (self.name,))
			frappe.db.commit()


def enforce_single_default(doc, method):
	"""التأكد من وجود شروط افتراضية واحدة فقط"""
	if hasattr(doc, 'default') and doc.default:
		frappe.db.sql("""
			UPDATE `tabTerms and Conditions`
			SET `default` = 0
			WHERE name != %s AND `default` = 1
		""", (doc.name,))


def apply_default_tc(doc, method):
	"""تطبيق الشروط الافتراضية على المستندات الجديدة"""
	# تحقق من وجود حقل tc_name في المستند
	if hasattr(doc, 'tc_name') and not doc.tc_name:
		# جلب الشروط الافتراضية
		default_terms = frappe.db.get_value(
			"Terms and Conditions",
			{"default": 1, "disabled": 0},
			["name", "terms"],
			as_dict=1
		)
		
		if default_terms:
			doc.tc_name = default_terms.name
			if hasattr(doc, 'terms'):
				doc.terms = default_terms.terms


@frappe.whitelist()
def get_default_terms():
	"""الحصول على الشروط الافتراضية"""
	default_terms = frappe.db.get_value(
		"Terms and Conditions",
		{"default": 1, "disabled": 0},
		["name", "terms"],
		as_dict=1
	)
	
	if default_terms:
		return default_terms
	
	return None
