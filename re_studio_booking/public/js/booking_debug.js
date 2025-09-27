// Debugging permission issues
frappe.ui.form.on('Booking', {
    after_save: function(frm) {
        console.log("Booking saved with name:", frm.doc.name);
    },
    
    package: function(frm) {
        console.log("Package selected:", frm.doc.package);
        
        // Add debug code to log the request
        if (frm.doc.package && frm.doc.booking_type === 'Package') {
            console.log("Calling fetch_package_services_for_booking with parameters:", {
                package: frm.doc.package,
                photographer: frm.doc.photographer || null,
                photographer_b2b: frm.doc.photographer_b2b ? 1 : 0
            });
            
            // Add try-catch and better error handling
            frappe.call({
                method: 're_studio_booking.re_studio_booking.doctype.booking.booking.fetch_package_services_for_booking',
                args: {
                    package: frm.doc.package,
                    photographer: frm.doc.photographer || null,
                    photographer_b2b: frm.doc.photographer_b2b ? 1 : 0
                },
                callback: function(r) {
                    console.log("Response received:", r);
                    if (r.message && r.message.rows) {
                        console.log("Processing rows:", r.message.rows);
                        frm.clear_table('package_services_table');
                        r.message.rows.forEach(function(svc){
                            let row = frm.add_child('package_services_table');
                            console.log("Creating row with service:", svc.service);
                            row.service = svc.service;
                            row.service_name = svc.service_name;
                            row.quantity = svc.quantity;
                            row.base_price = svc.base_price;
                            row.package_price = svc.package_price;
                            row.amount = svc.amount;
                            row.photographer_discount_amount = svc.photographer_discount_amount;
                            if (svc.service_price !== undefined) row.service_price = svc.service_price;
                        });
                        frm.refresh_field('package_services_table');
                        console.log("Table refreshed");
                    } else if (r.message && r.message.error) {
                        console.error("Error in API response:", r.message.error);
                        frappe.msgprint(__('خطأ في جلب خدمات الباقة: ') + r.message.error);
                    } else {
                        console.error("Unexpected response structure:", r);
                        frappe.msgprint(__('خطأ غير متوقع في الاستجابة من السيرفر'));
                    }
                },
                error: function(err) {
                    console.error("Call failed with error:", err);
                    frappe.msgprint(__('فشل الاتصال بالسيرفر. يرجى المحاولة مرة أخرى'));
                }
            });
        }
    }
});
