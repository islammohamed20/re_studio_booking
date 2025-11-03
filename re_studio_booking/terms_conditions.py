import frappe
from frappe import _


@frappe.whitelist()
def get_default_terms(company: str | None = None) -> str | None:
    """
    Return the name of the default Terms and Conditions.
    If `company` is provided, prefer a default for that company; otherwise fallback to global default.
    """
    filters = {"default": 1}
    if company:
        filters["company"] = company

    name = frappe.db.get_value("Terms and Conditions", filters, "name")
    if name:
        return name

    return frappe.db.get_value("Terms and Conditions", {"default": 1}, "name")


def enforce_single_default(doc, method=None):
    """
    Ensure only one Terms and Conditions is marked as default per company (or globally).
    Unset `default` on other records when current doc is set as default.
    """
    if not hasattr(doc, "default"):
        return
    if not doc.default:
        return

    filters = {"name": ("!=", doc.name), "default": 1}
    if getattr(doc, "company", None):
        filters["company"] = doc.company

    others = frappe.get_all("Terms and Conditions", filters=filters, pluck="name")
    for other in others:
        frappe.db.set_value("Terms and Conditions", other, "default", 0)


def apply_default_tc(doc, method=None):
    """
    Apply default Terms and Conditions on any document that has `tc_name` or `terms` field
    when value is empty. Prefer company-specific default.
    """
    # Try to read company from doc, defaults, or None
    company = getattr(doc, "company", None) or frappe.defaults.get_user_default("Company")

    default_tc = get_default_terms(company)
    if not default_tc:
        return

    # Populate link field if present
    if hasattr(doc, "tc_name") and not getattr(doc, "tc_name"):
        doc.tc_name = default_tc

    # Populate text field if present
    if hasattr(doc, "terms") and not getattr(doc, "terms"):
        terms_text = frappe.db.get_value("Terms and Conditions", default_tc, "terms")
        if terms_text:
            doc.terms = terms_text