// Copyright (c) 2025, Masar Digital Group and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payment Method", {
	refresh(frm) {
		// إظهار حقول ذات صلة بحسب الفئة
		frm.toggle_display(["supported_networks", "requires_3ds"], frm.doc.method_category === "Card");
		frm.toggle_display(["wallet_provider"], frm.doc.method_category === "Wallet");
	},
	method_category(frm) {
		frm.trigger("refresh");
	},
	percentage_fee(frm) {
		if (frm.doc.percentage_fee < 0) {
			frappe.msgprint({ message: __("نسبة الرسوم لا يجب أن تكون سالبة"), indicator: "red" });
			frm.set_value("percentage_fee", 0);
		}
	},
	fixed_fee(frm) {
		if (frm.doc.fixed_fee < 0) {
			frappe.msgprint({ message: __("الرسوم الثابتة لا يجب أن تكون سالبة"), indicator: "red" });
			frm.set_value("fixed_fee", 0);
		}
	}
});
