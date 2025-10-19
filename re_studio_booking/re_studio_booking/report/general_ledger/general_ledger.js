frappe.query_reports["General Ledger"] = {
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
            fieldname: "account",
            label: "Account",
            fieldtype: "Link",
            options: "Account",
        },
    ],
};