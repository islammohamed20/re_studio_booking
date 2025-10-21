"""فحص تفاصيل حجز باقة معين"""
import frappe
import json

booking = frappe.get_doc('Booking', 'BOOK-0002')

print("\n" + "="*70)
print(f"📦 فحص الحجز: {booking.name}")
print("="*70)

print(f"\nنوع الحجز: {booking.booking_type}")
print(f"الباقة: {booking.package if hasattr(booking, 'package') else 'غير محدد'}")
print(f"\n📊 الإجماليات:")
print(f"  المبلغ الأساسي: {booking.base_amount_package:,.2f} ج.م")
print(f"  المبلغ بعد الخصم: {booking.total_amount_package:,.2f} ج.م")

if hasattr(booking, 'package_services_table') and booking.package_services_table:
    print(f"\n📋 جدول الخدمات ({len(booking.package_services_table)} خدمة):")
    
    for idx, row in enumerate(booking.package_services_table, 1):
        print(f"\n  {idx}. الخدمة: {row.service}")
        print(f"     الكمية: {row.quantity}")
        print(f"     السعر الأساسي: {getattr(row, 'base_price', 0):,.2f} ج.م")
        print(f"     سعر الباقة: {getattr(row, 'package_price', 0):,.2f} ج.م")
        print(f"     المبلغ: {getattr(row, 'amount', 0):,.2f} ج.م")
        print(f"     إجباري: {'نعم' if getattr(row, 'is_required', 0) else 'لا'}")
        
        # عرض جميع الحقول
        print(f"     جميع الحقول:")
        for key in row.__dict__:
            if not key.startswith('_'):
                print(f"       - {key}: {row.__dict__[key]}")

print("\n" + "="*70)
