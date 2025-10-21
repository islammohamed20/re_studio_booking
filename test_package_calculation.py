"""
سكريبت اختبار حساب المبلغ الإجمالي للباقة بعد الخصم

هذا السكريبت يتحقق من صحة حسابات الباقة بعد التعديلات.
"""

import frappe
from frappe.utils import flt

def test_package_calculation():
    """اختبار حساب الباقة"""
    
    print("\n" + "="*70)
    print("اختبار حساب المبلغ الإجمالي للباقة بعد الخصم")
    print("="*70 + "\n")
    
    # 1. البحث عن حجز باقة موجود
    package_bookings = frappe.get_all(
        'Booking',
        filters={'booking_type': 'Package'},
        fields=['name', 'total_amount_package', 'base_amount_package'],
        limit=5,
        order_by='modified desc'
    )
    
    if not package_bookings:
        print("❌ لا توجد حجوزات باقة للاختبار")
        return
    
    print(f"✅ تم العثور على {len(package_bookings)} حجز باقة\n")
    
    # 2. فحص كل حجز
    for booking_info in package_bookings:
        booking_name = booking_info.name
        print(f"\n📦 فحص الحجز: {booking_name}")
        print("-" * 70)
        
        # جلب تفاصيل الحجز
        booking = frappe.get_doc('Booking', booking_name)
        
        # التحقق من الحقول الأساسية
        base_amount = flt(booking.base_amount_package)
        total_amount = flt(booking.total_amount_package)
        
        print(f"   المبلغ الأساسي: {base_amount:,.2f} ج.م")
        print(f"   المبلغ بعد الخصم: {total_amount:,.2f} ج.م")
        
        # حساب الخصم
        if base_amount > 0:
            discount_amount = base_amount - total_amount
            discount_percentage = (discount_amount / base_amount) * 100
            print(f"   مبلغ الخصم: {discount_amount:,.2f} ج.م ({discount_percentage:.1f}%)")
        
        # فحص جدول الخدمات
        if hasattr(booking, 'package_services_table') and booking.package_services_table:
            print(f"\n   📋 جدول الخدمات ({len(booking.package_services_table)} خدمة):")
            
            calculated_base = 0
            calculated_total = 0
            
            for idx, row in enumerate(booking.package_services_table, 1):
                service = getattr(row, 'service', 'غير محدد')
                quantity = flt(getattr(row, 'quantity', 0))
                base_price = flt(getattr(row, 'base_price', 0))
                package_price = flt(getattr(row, 'package_price', 0))
                amount = flt(getattr(row, 'amount', 0))
                
                # حساب المتوقع
                expected_base = base_price * quantity
                expected_amount = package_price * quantity
                
                calculated_base += expected_base
                calculated_total += expected_amount
                
                # التحقق من صحة الحساب
                is_correct = abs(amount - expected_amount) < 0.01
                status = "✅" if is_correct else "❌"
                
                print(f"\n   {status} خدمة {idx}: {service}")
                print(f"      الكمية: {quantity:.1f}")
                print(f"      السعر الأساسي: {base_price:,.2f} ج.م")
                print(f"      سعر الباقة: {package_price:,.2f} ج.م")
                print(f"      المبلغ المحفوظ: {amount:,.2f} ج.م")
                print(f"      المبلغ المتوقع: {expected_amount:,.2f} ج.م")
                
                if not is_correct:
                    print(f"      ⚠️ فرق: {abs(amount - expected_amount):,.2f} ج.م")
            
            # التحقق من الإجماليات
            print(f"\n   📊 التحقق من الإجماليات:")
            print(f"      المبلغ الأساسي المحسوب: {calculated_base:,.2f} ج.م")
            print(f"      المبلغ الأساسي المحفوظ: {base_amount:,.2f} ج.م")
            base_match = abs(calculated_base - base_amount) < 0.01
            print(f"      {'✅' if base_match else '❌'} المبلغ الأساسي {'صحيح' if base_match else 'خاطئ'}")
            
            print(f"\n      المبلغ الكلي المحسوب: {calculated_total:,.2f} ج.م")
            print(f"      المبلغ الكلي المحفوظ: {total_amount:,.2f} ج.م")
            total_match = abs(calculated_total - total_amount) < 0.01
            print(f"      {'✅' if total_match else '❌'} المبلغ الكلي {'صحيح' if total_match else 'خاطئ'}")
            
            if not base_match or not total_match:
                print(f"\n      ⚠️ يُنصح بإعادة حفظ الحجز لإعادة الحساب")
    
    print("\n" + "="*70)
    print("انتهى الاختبار")
    print("="*70 + "\n")

if __name__ == '__main__':
    test_package_calculation()
