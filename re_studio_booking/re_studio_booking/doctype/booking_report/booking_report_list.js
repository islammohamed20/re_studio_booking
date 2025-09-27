// Copyright (c) 2023, MASAR TEAM and contributors
// For license information, please see license.txt

frappe.listview_settings['Booking Report'] = {
	refresh: function(listview) {
		// Add custom buttons for quick reports
		listview.page.add_inner_button(__('تقرير اليوم'), function() {
			frappe.new_doc('Booking Report', {
				report_type: 'Booking Summary',
				date_range: 'Today'
			});
		}, __('تقرير سريع'));
		
		listview.page.add_inner_button(__('تقرير هذا الأسبوع'), function() {
			frappe.new_doc('Booking Report', {
				report_type: 'Booking Summary',
				date_range: 'This Week'
			});
		}, __('تقرير سريع'));
		
		listview.page.add_inner_button(__('تقرير هذا الشهر'), function() {
			frappe.new_doc('Booking Report', {
				report_type: 'Booking Summary',
				date_range: 'This Month'
			});
		}, __('تقرير سريع'));
		
		// Add buttons for different report types
		listview.page.add_inner_button(__('ملخص الحجوزات'), function() {
			frappe.new_doc('Booking Report', {
				report_type: 'Booking Summary',
				date_range: 'This Month'
			});
		}, __('نوع التقرير'));
		
		listview.page.add_inner_button(__('أداء المصورين'), function() {
			frappe.new_doc('Booking Report', {
				report_type: 'Photographer Performance',
				date_range: 'This Month'
			});
		}, __('نوع التقرير'));
		
		listview.page.add_inner_button(__('شعبية الخدمات'), function() {
			frappe.new_doc('Booking Report', {
				report_type: 'Service Popularity',
				date_range: 'This Month'
			});
		}, __('نوع التقرير'));
		
		listview.page.add_inner_button(__('تقرير الإيرادات'), function() {
			frappe.new_doc('Booking Report', {
				report_type: 'Revenue Report',
				date_range: 'This Month'
			});
		}, __('نوع التقرير'));
	},
	
	get_indicator: function(doc) {
		// Set indicators based on report type
		if (doc.report_type === 'Booking Summary') {
			return [__("ملخص الحجوزات"), "blue"];
		} else if (doc.report_type === 'Photographer Performance') {
			return [__("أداء المصورين"), "green"];
		} else if (doc.report_type === 'Service Popularity') {
			return [__("شعبية الخدمات"), "orange"];
		} else if (doc.report_type === 'Revenue Report') {
			return [__("تقرير الإيرادات"), "purple"];
		}
		return ["", "gray"];
	},
	
	formatters: {
		// Format date range for display in list
		date_range: function(value, df, doc) {
			if (value === 'Custom') {
				return __('مخصص') + ': ' + 
					frappe.datetime.str_to_user(doc.start_date) + ' - ' + 
					frappe.datetime.str_to_user(doc.end_date);
			} else if (value === 'Today') {
				return __('اليوم');
			} else if (value === 'This Week') {
				return __('هذا الأسبوع');
			} else if (value === 'This Month') {
				return __('هذا الشهر');
			} else if (value === 'Last Month') {
				return __('الشهر الماضي');
			} else if (value === 'This Year') {
				return __('هذا العام');
			}
			return value;
		}
	},
	
	onload: function(listview) {
		// Add custom filters
		listview.page.add_field({
			fieldname: 'report_type_filter',
			label: __('نوع التقرير'),
			fieldtype: 'Select',
			options: '\nBooking Summary\nPhotographer Performance\nService Popularity\nRevenue Report',
			onchange: function() {
				listview.refresh();
			}
		});
		
		listview.page.add_field({
			fieldname: 'date_range_filter',
			label: __('النطاق الزمني'),
			fieldtype: 'Select',
			options: '\nToday\nThis Week\nThis Month\nLast Month\nThis Year\nCustom',
			onchange: function() {
				listview.refresh();
			}
		});
	},
	
	get_filters_for_args: function() {
		// Apply custom filters
		let filters = {};
		
		let report_type_filter = frappe.listview_settings['Booking Report'].report_type_filter;
		if (report_type_filter) {
			filters['report_type'] = report_type_filter;
		}
		
		let date_range_filter = frappe.listview_settings['Booking Report'].date_range_filter;
		if (date_range_filter) {
			filters['date_range'] = date_range_filter;
		}
		
		return filters;
	}
};