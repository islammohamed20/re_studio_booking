# اختبار حساب المبلغ الإجمالي للباقة بعد الخصم

## المشكلة المبلغ عنها
"في مشكلة داخل حقل حساب المبلغ الاجمالي للباقة بعد الخصم"

## السبب الجذري
كان هناك استخدام خاطئ لأسماء الحقول في حسابات الباقة:

### الحقول المستخدمة خطأً ❌
1. `hourly_rate` - **غير موجود** في DocType (Package Service Item)
2. `photographer_discounted_rate` - **غير موجود** في DocType
3. `photographer_discount_amount` - **غير موجود** في DocType
4. `total_amount` - **غير موجود** (الاسم الصحيح: `amount`)

### الحقول الصحيحة من DocType ✅
1. `base_price` - السعر الأساسي من Service master
2. `package_price` - سعر الساعة في الباقة (قابل للتعديل)
3. `quantity` - عدد الساعات
4. `amount` - المبلغ الإجمالي للصف (package_price × quantity)

## التعديلات المطبقة

### 1. في `booking_calculations.py::calculate_package_totals()`
**قبل:**
```python
hourly_rate = flt(getattr(service_row, 'hourly_rate', 0))
photographer_discounted_rate = flt(getattr(service_row, 'photographer_discounted_rate', 0))
if photographer_discounted_rate > 0 and photographer_discounted_rate != hourly_rate:
    discounted_amount_row = quantity * photographer_discounted_rate
```

**بعد:**
```python
base_price = flt(getattr(service_row, 'base_price', 0))
package_price = flt(getattr(service_row, 'package_price', 0))
if not base_price and package_price:
    base_price = package_price

base_amount_row = quantity * base_price
final_amount_row = quantity * package_price
service_row.amount = final_amount_row
```

### 2. في `booking_calculations.py::_build_package_rows()`
**قبل:**
```python
booking_doc.append('package_services_table', {
    'service': service.service,
    'quantity': qty,
    'hourly_rate': hourly_rate,
    'photographer_discounted_rate': photographer_discounted_rate,
    'total_amount': total_amount
})
```

**بعد:**
```python
booking_doc.append('package_services_table', {
    'service': service.service,
    'quantity': qty,
    'base_price': base_price,
    'package_price': final_package_price,
    'amount': amount,
    'is_required': service.is_required if hasattr(service, 'is_required') else 0
})
```

### 3. في `booking.py::_build_package_rows()`
**قبل:**
```python
photographer_discounted_rate = base_price
row.photographer_discount_amount = photographer_discounted_rate
row.amount = photographer_discounted_rate * qty
```

**بعد:**
```python
final_price_per_unit = package_price
if service_name in photographer_services:
    if photographer_services[service_name]['discounted_price'] > 0:
        final_price_per_unit = photographer_services[service_name]['discounted_price']
    elif discount_pct > 0 and service_name in allowed:
        final_price_per_unit = package_price * (1 - discount_pct / 100.0)

row.package_price = final_price_per_unit
row.amount = final_price_per_unit * qty
```

## طريقة الاختبار

### 1. إنشاء حجز باقة جديد
```
1. فتح Booking DocType
2. اختيار booking_type = "Package"
3. اختيار باقة (Package) تحتوي على خدمات متعددة
4. اختيار مصور (Photographer) مع خصم B2B
5. حفظ الحجز
```

### 2. التحقق من الحسابات
```
المتوقع:
- base_amount_package = مجموع (base_price × quantity) لكل خدمة
- total_amount_package = مجموع (package_price × quantity) لكل خدمة بعد خصم المصور
- amount (لكل صف) = package_price × quantity
```

### 3. مثال حسابي

**باقة تحتوي على:**
- خدمة 1: base_price = 100 ج.م، quantity = 2 ساعات
- خدمة 2: base_price = 150 ج.م، quantity = 3 ساعات

**خصم المصور: 10%**

**النتيجة المتوقعة:**
```
base_amount_package = (100 × 2) + (150 × 3) = 200 + 450 = 650 ج.م

بعد خصم 10%:
- خدمة 1: package_price = 90 ج.م، amount = 90 × 2 = 180 ج.م
- خدمة 2: package_price = 135 ج.م، amount = 135 × 3 = 405 ج.م

total_amount_package = 180 + 405 = 585 ج.م
```

## الحالة الحالية
✅ **تم إصلاح جميع الحقول لتستخدم أسماء DocType الصحيحة**
✅ **تم توحيد منطق الحساب في جميع الدوال**
✅ **تم إزالة الحقول الوهمية غير الموجودة في DocType**

## الخطوات التالية
1. ✅ مسح الذاكرة المؤقتة (clear-cache)
2. ⏳ اختبار إنشاء حجز باقة جديد
3. ⏳ التحقق من أن total_amount_package يحسب بشكل صحيح
4. ⏳ اختبار مع خصومات المصور المختلفة
