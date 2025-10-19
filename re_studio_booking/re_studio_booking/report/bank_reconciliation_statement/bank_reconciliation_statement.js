frappe.query_reports["Bank Reconciliation Statement"] = {
    filters: [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 1,
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 1,
        },
        {
            fieldname: "bank_account",
            label: "Bank Account",
            fieldtype: "Link",
            options: "Bank Account",
        },
    ],
};