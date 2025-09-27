// Re Studio Booking Setup Wizard

// Add custom slides for Re Studio setup
frappe.setup.on("before_load", function () {
	// Add Re Studio organization setup slide
	frappe.setup.add_slide({
		name: "studio_organization",
		title: __("Setup your Studio"),
		icon: "fa fa-camera",
		fields: [
			{
				fieldname: "studio_name",
				label: __("Studio Name"),
				fieldtype: "Data",
				reqd: 1,
				default: "Re Studio"
			},
			{
				fieldname: "studio_phone",
				label: __("Studio Phone"),
				fieldtype: "Data"
			},
			{
				fieldname: "studio_website",
				label: __("Studio Website"),
				fieldtype: "Data",
				placeholder: "https://www.yourstudio.com"
			},
			{
				fieldtype: "Section Break"
			},
			{
				fieldname: "studio_address",
				label: __("Studio Address"),
				fieldtype: "Text",
				placeholder: "Enter your studio's complete address"
			},
			{
				fieldtype: "Section Break",
				label: __("Studio Logo")
			},
			{
				fieldname: "studio_logo",
				label: __("Upload Studio Logo"),
				fieldtype: "Attach Image",
				description: __("Upload your studio logo (recommended size: 200x200px)")
			}
		],
		onload: function(slide) {
			// Set default studio name if not set
			if (!slide.get_value("studio_name")) {
				slide.get_field("studio_name").set_input("Re Studio");
			}
		}
	});

	// Add business settings slide
	frappe.setup.add_slide({
		name: "business_settings",
		title: __("Business Settings"),
		icon: "fa fa-cog",
		fields: [
			{
				fieldname: "business_hours_start",
				label: __("Business Hours Start"),
				fieldtype: "Time",
				default: "09:00",
				reqd: 1
			},
			{
				fieldname: "business_hours_end",
				label: __("Business Hours End"),
				fieldtype: "Time",
				default: "18:00",
				reqd: 1
			},
			{
				fieldtype: "Section Break",
				label: __("Booking Settings")
			},
			{
				fieldname: "booking_advance_days",
				label: __("Booking Advance Days"),
				fieldtype: "Int",
				default: 30,
				description: __("How many days in advance can customers book?")
			},
			{
				fieldname: "cancellation_hours",
				label: __("Cancellation Hours"),
				fieldtype: "Int",
				default: 24,
				description: __("Minimum hours before booking for cancellation")
			},
			{
				fieldtype: "Section Break",
				label: __("Default Services")
			},
			{
				fieldname: "create_default_services",
				label: __("Create Default Photography Services"),
				fieldtype: "Check",
				default: 1,
				description: __("Create basic photography services (Portrait, Wedding, Event, Product)")
			}
		]
	});

	// Add photographer setup slide
	frappe.setup.add_slide({
		name: "photographer_setup",
		title: __("Setup Main Photographer"),
		icon: "fa fa-user",
		fields: [
			{
				fieldname: "photographer_name",
				label: __("Photographer Name"),
				fieldtype: "Data",
				reqd: 1
			},
			{
				fieldname: "photographer_email",
				label: __("Photographer Email"),
				fieldtype: "Data",
				options: "Email"
			},
			{
				fieldname: "photographer_phone",
				label: __("Photographer Phone"),
				fieldtype: "Data"
			},
			{
				fieldtype: "Section Break",
				label: __("Working Hours")
			},
			{
				fieldname: "photographer_hours_start",
				label: __("Working Hours Start"),
				fieldtype: "Time",
				default: "09:00"
			},
			{
				fieldname: "photographer_hours_end",
				label: __("Working Hours End"),
				fieldtype: "Time",
				default: "18:00"
			},
			{
				fieldtype: "Section Break",
				label: __("Specializations")
			},
			{
				fieldname: "specializations",
				label: __("Photography Specializations"),
				fieldtype: "Text",
				placeholder: "e.g., Wedding, Portrait, Event, Product Photography"
			}
		],
		onload: function(slide) {
			// Auto-fill photographer name from user data
			if (frappe.wizard.values.full_name && !slide.get_value("photographer_name")) {
				slide.get_field("photographer_name").set_input(frappe.wizard.values.full_name);
			}
			// Auto-fill photographer email from user data
			if (frappe.wizard.values.email && !slide.get_value("photographer_email")) {
				slide.get_field("photographer_email").set_input(frappe.wizard.values.email);
			}
		}
	});
});

// Set welcome page for Re Studio
frappe.setup.welcome_page = "/app/re-studio";

// Custom setup completion message
frappe.setup.on("setup_complete", function() {
	frappe.msgprint({
		title: __("Welcome to Re Studio!"),
		message: __("Your photography studio is now set up and ready to use. You can start managing bookings, photographers, and services."),
		indicator: "green"
	});
});