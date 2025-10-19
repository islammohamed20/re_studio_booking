import frappe

def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": "Account", "fieldname": "account", "fieldtype": "Data", "width": 180},
        {"label": "Party Type", "fieldname": "party_type", "fieldtype": "Data", "width": 120},
        {"label": "Party", "fieldname": "party", "fieldtype": "Data", "width": 180},
        {"label": "Debit", "fieldname": "debit", "fieldtype": "Currency", "width": 120},
        {"label": "Credit", "fieldname": "credit", "fieldtype": "Currency", "width": 120},
        {"label": "Against", "fieldname": "against", "fieldtype": "Data", "width": 180},
        {"label": "Reference Type", "fieldname": "reference_doctype", "fieldtype": "Data", "width": 140},
        {"label": "Reference", "fieldname": "reference_name", "fieldtype": "Data", "width": 140},
        {"label": "Remarks", "fieldname": "remarks", "fieldtype": "Text", "width": 200},
    ]

    conditions = []
    values = {}

    if filters.get("from_date"):
        conditions.append("posting_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions.append("posting_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]
    if filters.get("account"):
        conditions.append("account = %(account)s")
        values["account"] = filters["account"]

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    data = frappe.db.sql(
        f"""
        SELECT posting_date, account, party_type, party, debit, credit,
               against, reference_doctype, reference_name, remarks
        FROM `tabGL Entry`
        {where_clause}
        ORDER BY posting_date ASC, name ASC
        """,
        values,
        as_dict=True,
    )

    return columns, data