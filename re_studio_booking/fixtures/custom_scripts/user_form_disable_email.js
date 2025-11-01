// تعطيل "Send Welcome Email" افتراضياً عند إنشاء مستخدم جديد
frappe.ui.form.on('User', {
    onload: function(frm) {
        if (frm.is_new()) {
            frm.set_value('send_welcome_email', 0);
        }
    }
});
