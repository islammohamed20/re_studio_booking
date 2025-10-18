# ملخص التعديلات المطبقة على Re Studio Booking

## التاريخ: 18 أكتوبر 2025

---

## 1. إنشاء ملف booking_utils.py

### الموقع
`/home/frappe/frappe/apps/re_studio_booking/re_studio_booking/re_studio_booking/doctype/booking/booking_utils.py`

### الوظائف المضافة

#### 1.1 `calculate_package_service_total(service_item)`
- **الغرض**: حساب المبلغ الإجمالي لخدمة داخل الباقة
- **الحساب**: `المبلغ الإجمالي = الكمية × سعر الساعة`

#### 1.2 `calculate_photographer_discounted_rate(service_item, photographer, package_doc)`
- **الغرض**: حساب سعر الساعة بعد خصم المصور للخدمات المسموح بها فقط
- **المنطق**:
  - التحقق من تفعيل B2B للمصور
  - التحقق من أن الخدمة موجودة في خدمات المصور
  - التحقق من السماح بالخصم على الخدمة (`allow_discount`)
  - تطبيق نسبة الخصم إذا كانت الشروط متحققة

#### 1.3 `validate_paid_amount(booking_doc)`
- **الغرض**: التحقق من صحة المبلغ المدفوع قبل الحفظ
- **الشروط**:
  - المبلغ المدفوع >= مبلغ العربون
  - المبلغ المدفوع <= المبلغ الإجمالي بعد الخصم
- **رسالة الخطأ**: يتم رفع استثناء إذا لم تتحقق الشروط

#### 1.4 `calculate_services_with_photographer_discount(booking_doc)`
- **الغرض**: حساب سعر الساعة بعد خصم المصور لجميع الخدمات في جدول خدمات الباقة
- **الآلية**:
  - المرور على جميع الخدمات في `booking_service_item`
  - تطبيق خصم المصور على الخدمات المسموح بها
  - تحديث حقل `photographer_discounted_rate`
  - إعادة حساب `total_amount`

#### 1.5 دوال مساعدة أخرى
- `recalculate_package_services_on_package_change`: إعادة حساب الخدمات عند تغيير الباقة
- `get_service_unit_type_fields`: الحصول على الحقول حسب نوع الوحدة
- `validate_flexible_service_timing`: التحقق من توقيت الخدمة المرنة
- `format_currency_arabic`: تنسيق المبلغ بالعربية

---

## 2. تعديلات على booking.py

### 2.1 إضافة الاستيراد
```python
from .booking_utils import (
    validate_paid_amount,
    calculate_services_with_photographer_discount,
    recalculate_package_services_on_package_change
)
```

### 2.2 تحديث دالة `before_save()`
**إضافة**: التحقق من صحة المبلغ المدفوع
```python
# 4. التحقق من صحة المبلغ المدفوع
validate_paid_amount(self)
```

### 2.3 تحديث دالة `populate_package_services()`
**التحسينات**:
1. **جلب خصم المصور بشكل صحيح**:
   - التحقق من تفعيل `photographer_b2b`
   - جلب نسبة الخصم من المصور
   - جلب الخدمات المسموح بخصمها فقط

2. **حساب سعر الساعة بعد الخصم**:
   - حساب `hourly_rate` من سعر الباقة أو السعر الأساسي
   - تطبيق خصم المصور: `photographer_discounted_rate = hourly_rate * (1 - discount / 100)`
   - حفظ كلا السعرين في الجدول

3. **حساب المبلغ الإجمالي**:
   - `amount = quantity × photographer_discounted_rate`
   - استخدام السعر بعد الخصم إذا كان هناك خصم
   - استخدام السعر الأصلي إذا لم يكن هناك خصم

---

## 3. تعديلات على Service DocType

### 3.1 تحديث service.json

#### الحقول المضافة/المحدثة:

##### 3.1.1 حقل "خدمة مرنة" (`is_flexible_service`)
```json
{
  "default": "0",
  "description": "تحديد أن هذه الخدمة لها توقيت محدد غير مرتبط بعدد ساعات الحجز",
  "fieldname": "is_flexible_service",
  "fieldtype": "Check",
  "label": "خدمة مرنة"
}
```

##### 3.1.2 حقل "نوع الوحدة" (`type_unit`)
```json
{
  "fieldname": "type_unit",
  "fieldtype": "Select",
  "label": "نوع الوحدة",
  "options": "\nReels\nمدة\nPromo\nPhoto Session\nSeries\nPodcast Ep"
}
```

##### 3.1.3 حقل "عدد / الكمية" (`mount`)
```json
{
  "depends_on": "eval:doc.type_unit && doc.type_unit != 'مدة'",
  "fieldname": "mount",
  "fieldtype": "Int",
  "label": "عدد / الكمية"
}
```
**ملاحظة**: يظهر فقط عند اختيار نوع الوحدة غير "مدة"

##### 3.1.4 حقول المدة (تظهر فقط عند اختيار "مدة")

**المدة الافتراضية** (`duration`):
```json
{
  "depends_on": "eval:doc.type_unit == 'مدة'",
  "fieldname": "duration",
  "fieldtype": "Int",
  "label": "المدة الافتراضية (ساعة)"
}
```

**الحد الأدنى للمدة** (`min_duration`):
```json
{
  "depends_on": "eval:doc.type_unit == 'مدة'",
  "fieldname": "min_duration",
  "fieldtype": "Int",
  "label": "الحد الأدنى للمدة (دقائق)"
}
```

**الحد الأقصى للمدة** (`max_duration`):
```json
{
  "depends_on": "eval:doc.type_unit == 'مدة'",
  "fieldname": "max_duration",
  "fieldtype": "Int",
  "label": "الحد الأقصى للمدة (دقائق)"
}
```

**وحدة المدة** (`duration_unit`):
```json
{
  "default": "دقيقة",
  "depends_on": "eval:doc.type_unit == 'مدة'",
  "fieldname": "duration_unit",
  "fieldtype": "Select",
  "label": "وحدة المدة",
  "options": "دقيقة\nساعة\nيوم"
}
```

### 3.2 تحديث service.js

#### إضافة event handler للحقل `type_unit`
```javascript
type_unit: function(frm) {
    // تحديث عرض الحقول عند تغيير نوع الوحدة
    toggle_unit_type_fields(frm);
}
```

#### إضافة دالة `toggle_unit_type_fields(frm)`
**الوظيفة**: إظهار/إخفاء الحقول بناءً على نوع الوحدة المختار

**المنطق**:
1. إذا كان `type_unit == 'مدة'`:
   - إظهار: `duration`, `min_duration`, `max_duration`, `duration_unit`
   - إخفاء: `mount`
   
2. إذا كان `type_unit` غير "مدة":
   - إظهار: `mount`
   - إخفاء: حقول المدة

3. تحديث مطلوبية الحقول (`reqd`) تلقائياً

---

## 4. آلية العمل الكاملة

### 4.1 عند اختيار الباقة في Booking
1. يتم استدعاء `populate_package_services()`
2. يتم جلب خدمات الباقة من جدول `Package Services`
3. لكل خدمة:
   - حساب `hourly_rate` من الباقة أو الخدمة الأصلية
   - إذا كان هناك مصور وتم تفعيل B2B:
     - التحقق من السماح بالخصم على الخدمة
     - حساب `photographer_discounted_rate`
   - حساب `amount = quantity × السعر النهائي`
4. حفظ الإجماليات في `base_amount_package` و `total_amount_package`

### 4.2 عند اختيار المصور وتفعيل B2B
1. يتم إعادة حساب جميع الخدمات في `booking_service_item`
2. فقط الخدمات المسموح بخصمها تحصل على السعر المخفض
3. باقي الخدمات تبقى بالسعر الأصلي

### 4.3 قبل حفظ الحجز
1. يتم استدعاء `validate_paid_amount()`
2. التحقق من:
   - `paid_amount >= deposit_amount`
   - `paid_amount <= total_after_discount`
3. رفع خطأ إذا لم تتحقق الشروط

### 4.4 في نموذج Service
1. عند اختيار "نوع الوحدة":
   - إذا كان "Reels, Promo, Photo Session, Series, Podcast Ep": يظهر حقل "عدد / الكمية"
   - إذا كان "مدة": تظهر حقول المدة (المدة الافتراضية، الحد الأدنى، الحد الأقصى، وحدة المدة)
2. يتم تحديث عرض الحقول تلقائياً عند التغيير

---

## 5. الحقول الجديدة في جدول خدمات الباقة

| اسم الحقل | النوع | الوصف |
|-----------|------|-------|
| `hourly_rate` | Currency | سعر الساعة الأصلي من الباقة |
| `photographer_discounted_rate` | Currency | سعر الساعة بعد خصم المصور |
| `service_price` | Currency | السعر النهائي المستخدم في الحساب |
| `amount` | Currency | المبلغ الإجمالي = الكمية × السعر النهائي |

---

## 6. ملاحظات مهمة

### 6.1 الفرق بين الحقول
- **`base_price`**: السعر الأساسي من جدول Service
- **`hourly_rate`**: سعر الساعة في الباقة (قد يختلف عن السعر الأساسي)
- **`photographer_discounted_rate`**: سعر الساعة بعد خصم المصور (للخدمات المسموح بها)
- **`service_price`**: السعر النهائي المستخدم (مع أو بدون خصم)

### 6.2 شروط تطبيق خصم المصور
1. وجود مصور محدد في الحجز
2. تفعيل `photographer_b2b` = True
3. الخدمة موجودة في جدول خدمات المصور
4. `allow_discount` = True للخدمة في جدول المصور

### 6.3 الخدمة المرنة
- الخدمة المرنة لها توقيت محدد خاص بها
- غير مرتبطة بعدد ساعات الباقة المحجوزة
- يتم تحديد توقيت البداية والنهاية بشكل منفصل

---

## 7. الملفات المعدلة

1. **ملفات جديدة**:
   - `/re_studio_booking/doctype/booking/booking_utils.py`

2. **ملفات محدثة**:
   - `/re_studio_booking/doctype/booking/booking.py`
   - `/re_studio_booking/doctype/service/service.json`
   - `/re_studio_booking/doctype/service/service.js`

---

## 8. الأوامر المطبقة

```bash
# تطبيق التغييرات على قاعدة البيانات
bench --site site1.local migrate

# مسح الكاش
bench --site site1.local clear-cache

# إعادة تشغيل الخدمات
bench restart
```

---

## 9. الخطوات التالية (إذا لزم الأمر)

1. إضافة unit tests لدوال booking_utils
2. إضافة validation إضافية للخدمة المرنة
3. إضافة تقارير لمتابعة خصومات المصورين
4. تحسين واجهة المستخدم لعرض الأسعار قبل وبعد الخصم

---

**ملاحظة**: جميع التعديلات تم تطبيقها واختبارها بنجاح ✅
