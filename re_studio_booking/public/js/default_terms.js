/*
 * Auto-fill default Terms and Conditions on any form that has terms or tc_name.
 */

(() => {
  frappe.ui.form.on('*', {
    refresh(frm) {
      const tcField = frm.get_field('tc_name') || frm.get_field('terms');
      if (!tcField) return;

      const currentVal = frm.doc.tc_name || frm.doc.terms;
      if (currentVal) return;

      const company = frm.doc.company || frappe.boot?.company || null;

      frappe.call({
        method: 're_studio_booking.re_studio_booking.terms_conditions.get_default_terms',
        args: { company },
        callback: (r) => {
          const defaultName = r && r.message;
          if (!defaultName) return;

          if (frm.get_field('tc_name')) {
            frm.set_value('tc_name', defaultName);
          } else if (frm.get_field('terms')) {
            frappe.db.get_value('Terms and Conditions', defaultName, 'terms').then((res) => {
              const val = res.message && res.message.terms;
              if (val) frm.set_value('terms', val);
            });
          }
        },
      });
    },
  });
})();