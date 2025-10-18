// Calendar polyfill for legacy scripts using frappe.views.calendar.extend
// Ensures custom calendar definitions don't crash on Form load

(function() {
    // Ensure namespace exists
    if (!frappe.views) frappe.views = {};
    if (!frappe.views.calendar) frappe.views.calendar = {};

    // Add extend helper if missing
    if (typeof frappe.views.calendar.extend !== 'function') {
        frappe.views.calendar.extend = function(arg1, arg2) {
            // Supports both signatures:
            // 1) extend({ ...options }) -> returns options
            // 2) extend('Doctype', { ...options }) -> assigns and returns merged options
            if (typeof arg1 === 'object' && !arg2) {
                return arg1; // simple pass-through
            }

            var doctype = arg1;
            var opts = arg2 || {};
            var base = frappe.views.calendar[doctype] || {};
            var merged = Object.assign({}, base, opts);
            frappe.views.calendar[doctype] = merged;
            return merged;
        };
    }
})();