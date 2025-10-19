import frappe

def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": "Bank Account", "fieldname": "bank_account", "fieldtype": "Data", "width": 200},
        {"label": "Debit", "fieldname": "debit", "fieldtype": "Currency", "width": 120},
        {"label": "Credit", "fieldname": "credit", "fieldtype": "Currency", "width": 120},
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
    if filters.get("bank_account"):
        conditions.append("bank_account = %(bank_account)s")
        values["bank_account"] = filters["bank_account"]

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    data = frappe.db.sql(
        f"""
        SELECT posting_date, bank_account, debit, credit, remarks
        FROM `tabGL Entry`
        {where_clause}
        ORDER BY posting_date ASC, name ASC
        """,
        values,
        as_dict=True,
    )

    return columns, data