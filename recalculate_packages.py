"""
سكريبت إعادة حساب جميع حجوزات الباقة

هذا السكريبت يعيد حفظ جميع حجوزات الباقة لإعادة حساب المبالغ بعد التعديلات.
"""

import frappe
from frappe.utils import flt

def recalculate_all_packages():
    """إعادة حساب جميع حجوزات الباقة"""
    
    print("\n" + "="*70)
    print("إعادة حساب جميع حجوزات الباقة")
    print("="*70 + "\n")
    
    # 1. البحث عن جميع حجوزات الباقة
    package_bookings = frappe.get_all(
        'Booking',
        filters={'booking_type': 'Package'},
        fields=['name'],
        order_by='modified desc'
    )
    
    if not package_bookings:
        print("❌ لا توجد حجوزات باقة")
        return
    
    print(f"✅ تم العثور على {len(package_bookings)} حجز باقة\n")
    
    # 2. إعادة حساب كل حجز
    success_count = 0
    error_count = 0
    
    for booking_info in package_bookings:
        booking_name = booking_info.name
        try:
            print(f"📦 معالجة الحجز: {booking_name}... ", end='')
            
            # جلب الحجز
            booking = frappe.get_doc('Booking', booking_name)
            
            # حفظ القيم القديمة للمقارنة
            old_base = flt(booking.base_amount_package)
            old_total = flt(booking.total_amount_package)
            
            # إعادة الحفظ لإعادة الحساب
            booking.save()
            frappe.db.commit()
            
            # جلب القيم الجديدة
            booking.reload()
            new_base = flt(booking.base_amount_package)
            new_total = flt(booking.total_amount_package)
            
            # التحقق من التغييرات
            base_changed = abs(new_base - old_base) > 0.01
            total_changed = abs(new_total - old_total) > 0.01
            
            if base_changed or total_changed:
                print(f"✅ تم التحديث")
                print(f"   المبلغ الأساسي: {old_base:,.2f} ← {new_base:,.2f} ج.م")
                print(f"   المبلغ الكلي: {old_total:,.2f} ← {new_total:,.2f} ج.م")
            else:
                print(f"✓ بدون تغيير")
            
            success_count += 1
            
        except Exception as e:
            print(f"❌ خطأ: {str(e)}")
            error_count += 1
            frappe.db.rollback()
    
    print("\n" + "="*70)
    print(f"✅ نجح: {success_count} حجز")
    print(f"❌ فشل: {error_count} حجز")
    print("="*70 + "\n")

if __name__ == '__main__':
    recalculate_all_packages()
