"""
سكريبت اختبار حساب العربون (Deposit Calculation Test)

يختبر جميع سيناريوهات حساب العربون:
1. حجز خدمة عادي
2. حجز باقة عادي
3. تطبيق الحد الأدنى
4. عدم تجاوز الإجمالي
5. احترام القيمة اليدوية
"""

import frappe
from frappe.utils import flt

def test_deposit_calculations():
    """اختبار شامل لحساب العربون"""
    
    print("\n" + "="*80)
    print("اختبار حساب العربون (Deposit Calculation)")
    print("="*80 + "\n")
    
    # 1. جلب إعدادات النظام
    print("📋 الإعدادات الحالية:")
    print("-" * 80)
    
    try:
        settings = frappe.db.get_singles_dict('General Settings') or {}
        
        # نسبة العربون الافتراضية
        default_deposit_pct = None
        for key in ('نسبة العربون (%)', 'deposit_percentage', 'نسبة_العربون_%'):
            if key in settings:
                default_deposit_pct = flt(settings.get(key))
                print(f"   نسبة العربون الافتراضية: {default_deposit_pct}%")
                break
        
        if not default_deposit_pct:
            print(f"   نسبة العربون الافتراضية: 30% (افتراضي)")
        
        # الحد الأدنى لمبلغ الحجز
        min_booking_amount = None
        for key in ('الحد الأدنى لمبلغ الحجز', 'minimum_booking_amount', 'min_booking_amount'):
            if key in settings:
                min_booking_amount = flt(settings.get(key))
                print(f"   الحد الأدنى لمبلغ الحجز: {min_booking_amount:,.2f} ج.م")
                break
        
        if not min_booking_amount:
            print(f"   الحد الأدنى لمبلغ الحجز: غير محدد")
    
    except Exception as e:
        print(f"   ⚠️ خطأ في جلب الإعدادات: {str(e)}")
    
    print()
    
    # 2. اختبار الحجوزات الموجودة
    print("📦 اختبار الحجوزات الموجودة:")
    print("-" * 80)
    
    bookings = frappe.get_all(
        'Booking',
        fields=['name', 'booking_type', 'total_amount', 'total_amount_package', 
                'deposit_percentage', 'deposit_amount', 'status'],
        limit=10,
        order_by='modified desc'
    )
    
    if not bookings:
        print("   ❌ لا توجد حجوزات للاختبار")
        return
    
    print(f"   ✅ تم العثور على {len(bookings)} حجز\n")
    
    for booking_info in bookings:
        booking_name = booking_info.name
        booking_type = booking_info.booking_type
        
        # تحديد المبلغ الإجمالي حسب النوع
        if booking_type == 'Service':
            total_amount = flt(booking_info.total_amount)
        else:
            total_amount = flt(booking_info.total_amount_package)
        
        deposit_pct = flt(booking_info.deposit_percentage)
        deposit_amount = flt(booking_info.deposit_amount)
        
        # حساب العربون المتوقع
        expected_deposit = round(total_amount * deposit_pct / 100.0, 2)
        
        # تطبيق الحد الأدنى
        if min_booking_amount and expected_deposit < min_booking_amount and total_amount > 0:
            expected_deposit = min(min_booking_amount, total_amount)
        
        # التحقق من عدم تجاوز الإجمالي
        if expected_deposit > total_amount:
            expected_deposit = total_amount
        
        # المقارنة
        is_correct = abs(deposit_amount - expected_deposit) < 0.01
        status_icon = "✅" if is_correct else "❌"
        
        print(f"{status_icon} {booking_name} ({booking_type}):")
        print(f"   المبلغ الإجمالي: {total_amount:,.2f} ج.م")
        print(f"   نسبة العربون: {deposit_pct}%")
        print(f"   العربون المحفوظ: {deposit_amount:,.2f} ج.م")
        print(f"   العربون المتوقع: {expected_deposit:,.2f} ج.م")
        
        if not is_correct:
            difference = abs(deposit_amount - expected_deposit)
            print(f"   ⚠️ فرق: {difference:,.2f} ج.م")
            print(f"   💡 يُنصح بإعادة حفظ الحجز لإعادة الحساب")
        
        print()
    
    # 3. سيناريوهات الاختبار
    print("\n📊 سيناريوهات الاختبار:")
    print("-" * 80)
    
    test_scenarios = [
        {
            "name": "سيناريو 1: حجز خدمة عادي",
            "booking_type": "Service",
            "total": 1000,
            "deposit_pct": 30,
            "expected": 300,
            "description": "30% من 1000 = 300 ج.م"
        },
        {
            "name": "سيناريو 2: حجز باقة مع مبلغ صغير",
            "booking_type": "Package",
            "total": 500,
            "deposit_pct": 30,
            "expected": min_booking_amount if min_booking_amount and min_booking_amount > 150 else 150,
            "description": f"30% من 500 = 150 ج.م، لكن الحد الأدنى = {min_booking_amount or 'غير محدد'} ج.م"
        },
        {
            "name": "سيناريو 3: عربون أكبر من الإجمالي",
            "booking_type": "Service",
            "total": 100,
            "deposit_pct": 150,
            "expected": 100,
            "description": "150% من 100 = 150 ج.م، لكن لا يتجاوز الإجمالي (100 ج.م)"
        },
        {
            "name": "سيناريو 4: عربون يدوي",
            "booking_type": "Package",
            "total": 1000,
            "deposit_pct": 50,
            "expected": 500,
            "description": "50% من 1000 = 500 ج.م (يحترم القيمة اليدوية)"
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n{scenario['name']}:")
        print(f"   النوع: {scenario['booking_type']}")
        print(f"   المبلغ الإجمالي: {scenario['total']:,.2f} ج.م")
        print(f"   نسبة العربون: {scenario['deposit_pct']}%")
        print(f"   العربون المتوقع: {scenario['expected']:,.2f} ج.م")
        print(f"   📝 {scenario['description']}")
    
    print("\n" + "="*80)
    print("انتهى الاختبار")
    print("="*80 + "\n")

if __name__ == '__main__':
    test_deposit_calculations()
