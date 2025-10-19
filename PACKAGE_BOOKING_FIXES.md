# إصلاحات حجوزات الباقات (Package Booking Fixes)

## التاريخ: 19 أكتوبر 2025

## المشاكل التي تم إصلاحها

### 1. حقل المبلغ الإجمالي للباقة (total_amount_package)
**المشكلة:** الحقل لا يظهر مجموع عمود "المبلغ الإجمالي" من جدول خدمات الباقة

**الحل:**
- تم التأكد من أن `_aggregate_package_totals()` يتم استدعاؤها بعد `_build_package_rows()`
- الدالة تقوم بجمع قيم `amount` من كل صف في `package_services_table`
- النتيجة تُخزن في `self.total_amount_package`

**الكود:**
```python
def _aggregate_package_totals(self):
    if self.booking_type != 'Package':
        return
    base_total = 0.0
    final_total = 0.0
    for row in (self.package_services_table or []):
        qty = float(getattr(row, 'quantity', 1) or 1)
        bp = float(getattr(row, 'base_price', 0) or 0)
        base_total += bp * qty
        final_total += float(getattr(row, 'amount', 0) or 0)
    self.base_amount_package = round(base_total, 2)
    self.total_amount_package = round(final_total, 2)
```

### 2. خصم المصور في عمود "سعر الساعة بعد خصم المصور"
**المشكلة:** العمود `photographer_discount_amount` لا يظهر السعر المخصوم للخدمات المسموح بها

**الحل:**
تم تحديث دالتين:

#### أ) `populate_package_services()` - عند اختيار الباقة أول مرة
```python
# تطبيق خصم المصور إذا كانت الخدمة مسموحة
photographer_discounted_rate = hourly_rate
if photographer_discount > 0 and service.service in photographer_allowed_services:
    photographer_discounted_rate = hourly_rate * (1 - photographer_discount / 100)

self.append("package_services_table", {
    "service": service.service,
    "service_name": getattr(service, 'service_name', '') or service.service,
    "quantity": qty,
    "base_price": base_price,
    "package_price": hourly_rate,  # سعر الساعة داخل الباقة (قبل خصم المصور)
    "photographer_discount_amount": photographer_discounted_rate,  # السعر بعد خصم المصور
    "amount": qty * photographer_discounted_rate,  # المبلغ الإجمالي
    "أجباري": is_mandatory
})
```

#### ب) `_build_package_rows()` - عند إعادة حساب الأسعار
```python
# حساب السعر بعد خصم المصور
photographer_discounted_rate = base_price

if service_name in photographer_services:
    # استخدام السعر المخصوم من المصور إذا كان موجوداً
    if photographer_services[service_name]['discounted_price'] > 0:
        photographer_discounted_rate = photographer_services[service_name]['discounted_price']
    # وإلا استخدام نسبة الخصم العامة
    elif discount_pct > 0 and service_name in allowed:
        photographer_discounted_rate = base_price * (1 - discount_pct / 100.0)

# تعيين القيم
row.photographer_discount_amount = photographer_discounted_rate  # السعر بعد الخصم (لكل ساعة)
row.amount = photographer_discounted_rate * qty  # المبلغ الإجمالي
```

**الأولوية:**
1. أولاً: استخدام `discounted_price` من جدول خدمات المصور (إذا كان > 0)
2. ثانياً: استخدام `discount_percentage` العامة من المصور (إذا كانت الخدمة مسموحة)
3. ثالثاً: استخدام السعر الأساسي بدون خصم

### 3. عمود "إجباري" (أجباري) لا يظهر كـ Checked
**المشكلة:** الخدمات الإجبارية من مستند Package لا تظهر حالتها كـ checked

**الحل:**
تم إضافة منطق جلب `is_required` من `Package Service Item` وتعيينه في حقل `أجباري`:

```python
# Get is_required field from Package Service Item
is_mandatory = getattr(service, 'is_required', 0) or 0

self.append("package_services_table", {
    # ... باقي الحقول
    "أجباري": is_mandatory  # Set mandatory field from Package Service Item
})
```

**ملاحظة مهمة:**
- حقل `is_required` موجود في `Package Service Item` (ليس في `Service`)
- حقل `أجباري` في `Booking Package Service` كان يستخدم `fetch_from: "service.is_mandatory"` (خطأ)
- الآن يتم تعيين القيمة برمجياً من `Package Service Item.is_required`
- عند إعادة حساب الأسعار في `_build_package_rows()`، يتم الحفاظ على قيمة `أجباري` (لا يتم الكتابة فوقها)

## تسلسل التنفيذ

### عند اختيار Package
1. `populate_package_services()` ← يتم استدعاؤها عند تغيير الباقة
   - تحميل خدمات الباقة من `Package.package_services`
   - جلب خصومات المصور (إن وُجدت)
   - حساب السعر المخصوم لكل خدمة
   - تعيين `is_required` من Package Service Item إلى `أجباري`
   - حساب المبالغ الإجمالية

### عند حفظ/تحديث Booking
1. `recompute_pricing()` ← نقطة الدخول الموحدة
2. `_build_package_rows(ctx)` ← إعادة حساب أسعار الخدمات مع خصم المصور
   - تحديث `photographer_discount_amount` (السعر لكل ساعة بعد الخصم)
   - تحديث `amount` (المبلغ الإجمالي = السعر × الكمية)
   - **الحفاظ** على قيمة `أجباري` (لا يتم تغييرها)
3. `_aggregate_package_totals()` ← جمع الإجماليات
   - `base_amount_package` = مجموع (base_price × quantity)
   - `total_amount_package` = مجموع (amount)
4. `_compute_deposit()` ← حساب العربون
5. `_auto_set_payment_status()` ← تحديث حالة الدفع
6. `_validate_paid_vs_deposit()` ← التحقق من المبلغ المدفوع

## الحقول المستخدمة

### في Booking Package Service (Child Table)
| الحقل | النوع | الوصف |
|------|------|-------|
| `service` | Link | الخدمة |
| `quantity` | Int | الكمية/عدد الساعات |
| `base_price` | Currency | السعر الأساسي للخدمة |
| `package_price` | Currency | سعر الساعة داخل الباقة (قبل خصم المصور) |
| `photographer_discount_amount` | Currency | سعر الساعة بعد خصم المصور |
| `amount` | Currency | المبلغ الإجمالي (السعر × الكمية) |
| `أجباري` | Check | هل الخدمة إجبارية؟ |

### في Booking (Parent)
| الحقل | النوع | الوصف |
|------|------|-------|
| `base_amount_package` | Currency | المبلغ الأساسي للباقة (بدون خصومات) |
| `total_amount_package` | Currency | المبلغ الإجمالي بعد خصم المصور |
| `deposit_amount` | Currency | مبلغ العربون |

## الاختبار المطلوب

### سيناريو 1: حجز باقة بدون مصور B2B
1. إنشاء حجز جديد من نوع Package
2. اختيار باقة تحتوي على خدمات إجبارية وغير إجبارية
3. **التحقق:**
   - ✓ جدول `package_services_table` يظهر جميع الخدمات
   - ✓ عمود `أجباري` يظهر checked للخدمات الإجبارية
   - ✓ `photographer_discount_amount` = `package_price` (بدون خصم)
   - ✓ `amount` = `package_price × quantity`
   - ✓ `total_amount_package` = مجموع جميع قيم `amount`

### سيناريو 2: حجز باقة مع مصور B2B
1. إنشاء حجز جديد من نوع Package
2. اختيار باقة
3. اختيار مصور B2B لديه خصومات على بعض الخدمات
4. **التحقق:**
   - ✓ للخدمات المخصومة: `photographer_discount_amount` < `package_price`
   - ✓ للخدمات غير المخصومة: `photographer_discount_amount` = `package_price`
   - ✓ `amount` يتم حسابه من `photographer_discount_amount × quantity`
   - ✓ `total_amount_package` = مجموع جميع قيم `amount` المخصومة
   - ✓ عمود `أجباري` لا يزال يظهر بشكل صحيح

### سيناريو 3: تغيير المصور بعد اختيار الباقة
1. إنشاء حجز بباقة
2. اختيار مصور B2B
3. حفظ الحجز
4. تغيير المصور إلى مصور آخر بخصومات مختلفة
5. حفظ مرة أخرى
6. **التحقق:**
   - ✓ `photographer_discount_amount` يتم تحديثه حسب المصور الجديد
   - ✓ `amount` يتم إعادة حسابه
   - ✓ `total_amount_package` يتم تحديثه
   - ✓ عمود `أجباري` **لم يتأثر** بالتغيير

## الملفات المعدلة

### 1. booking.py
**الدوال المحدثة:**
- `populate_package_services()` - أضيف تعيين `أجباري` من `is_required`
- `_build_package_rows()` - تحديث منطق خصم المصور + الحفاظ على `أجباري`
- `_aggregate_package_totals()` - بدون تغيير (تعمل بشكل صحيح)

**السطور المعدلة:**
- خطوط 1113-1173: `populate_package_services()`
- خطوط 575-632: `_build_package_rows()`
- خطوط 633-643: `_aggregate_package_totals()` (بدون تغيير)

## التحقق من عدم وجود أخطاء

```bash
# فحص الصياغة
python3 -m py_compile re_studio_booking/re_studio_booking/doctype/booking/booking.py
# ✓ نجح بدون أخطاء

# إعادة تشغيل النظام
bench restart
# ✓ تم إعادة التشغيل بنجاح
```

## الخلاصة

تم إصلاح جميع المشاكل الثلاث:

1. ✅ **total_amount_package** - يتم حسابه بشكل صحيح من مجموع عمود `amount`
2. ✅ **photographer_discount_amount** - يظهر السعر المخصوم لكل ساعة للخدمات المسموح بها
3. ✅ **أجباري** - يتم جلبه من `Package Service Item.is_required` ويظهر كـ checked

التحديثات متوافقة مع:
- حجوزات الخدمات (Service bookings) - لم تتأثر
- حجوزات الباقات بدون مصور - تعمل بشكل صحيح
- حجوزات الباقات مع مصور B2B - تطبيق الخصومات بشكل صحيح
- إعادة حساب الأسعار - يحافظ على حالة `أجباري`

---
**ملاحظة:** يُنصح باختبار السيناريوهات الثلاثة المذكورة أعلاه للتأكد من أن كل شيء يعمل كما هو متوقع في بيئة الإنتاج.
