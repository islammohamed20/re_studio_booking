# 📋 تعديلات Booking - قائمة المهام

## ✅ تم إنجازه

### 1. التحقق من المبلغ المدفوع قبل الحفظ
- ✅ تحديث `validate_paid_amount()` في booking_utils.py
- ✅ المبلغ المدفوع >= العربون OR = المبلغ الإجمالي
- ✅ رسائل خطأ واضحة بالعربية

---

## 🔄 قيد التنفيذ

### 2. إظهار سعر الساعة بعد الخصم في جدول الخدمات
**المشكلة الحالية:**
- عند تفعيل Photographer B2B، يتم إخفاء عمود "سعر الساعة بعد الخصم"
- السعر بعد الخصم = السعر قبل الخصم (لا يطبق الخصم)

**الحل المطلوب:**
- إظهار العمود دائماً (عدم إخفائه)
- حساب السعر المخفض بشكل صحيح عند:
  1. اختيار المصور
  2. تفعيل Photographer B2B
  
**الملفات المتأثرة:**
- `booking.js` - إزالة منطق الإخفاء
- `booking.py` - تحديث حساب السعر المخفض

---

## 📝 المتبقي

### 3. رسالة تحذير نفاد الباقة
**المطلوب:**
- تغيير رسالة "تم استنفاد جميع ساعات الباقة" من `frappe.throw()` إلى `frappe.msgprint()`
- نوع الرسالة: indicator='orange' أو 'red'
- الموضع: من الأسفل (alert-container-message)

**الملفات:**
- `booking.py` - تحديث validation

---

### 4. حساب الساعات المتبقية تلقائياً
**المطلوب:**
عند اختيار الباقة:
1. ملء `remaining_hours` بقيمة إجمالي ساعات الباقة (`package.total_hours`)
2. عند إضافة تاريخ حجز:
   - حساب عدد الساعات من `start_time` و `end_time`
   - وضع العدد في حقل `hours` داخل `package_booking_dates`
3. جمع كل الساعات المختارة ووضعها في `used_hours`
4. طرح `used_hours` من إجمالي ساعات الباقة = `remaining_hours`
5. عند `remaining_hours = 0`، منع إضافة تواريخ جديدة

**الملفات:**
- `booking.py` - دالة `compute_package_hours_usage()`
- `booking.js` - حساب الساعات عند تغيير start_time/end_time

---

### 5. حساب المبلغ الإجمالي في جدول خدمات الباقة
**المطلوب:**
- المبلغ الإجمالي لكل صف = `quantity × hourly_rate`
- عند تفعيل B2B:
  - للخدمات الموجودة في المصور والمسموح بخصمها:
    - المبلغ الإجمالي = `quantity × discounted_hourly_rate`
  - للخدمات الأخرى:
    - المبلغ الإجمالي = `quantity × hourly_rate`

**الملفات:**
- `booking_utils.py` - دالة `calculate_services_with_photographer_discount()`
- `booking.py` - استدعاء الدالة عند التغيير

---

## 🔍 التفاصيل الفنية

### حقول Booking المتأثرة:
```
- booking_type (Service/Package)
- photographer
- photographer_b2b (Check)
- package
- remaining_hours (Float)
- used_hours (Float)  
- total_booked_hours (Float)
- package_booking_dates (Table)
- package_services_table (Table)
- deposit_amount
- paid_amount
- total_amount (Service)
- total_amount_package (Package)
```

### جدول package_booking_dates:
```
- booking_date
- start_time
- end_time
- hours (حساب تلقائي)
```

### جدول package_services_table:
```
- service
- quantity
- hourly_rate
- discounted_hourly_rate (جديد أو موجود)
- total_amount (حساب تلقائي)
```

---

## 📌 ملاحظات مهمة

1. **ترتيب العمليات:**
   - اختيار الباقة → ملء remaining_hours
   - اختيار المصور → جلب الخدمات المسموح بها
   - تفعيل B2B → حساب الأسعار المخفضة
   - إضافة تواريخ → حساب الساعات → تحديث remaining_hours

2. **Validation:**
   - قبل الحفظ: التحقق من paid_amount
   - عند إضافة تاريخ: التحقق من remaining_hours > 0
   - عند الحفظ: التحقق من عدم تجاوز ساعات الباقة

3. **UI/UX:**
   - إظهار remaining_hours بشكل واضح
   - رسائل تحذير واضحة عند نفاد الساعات
   - تعطيل إضافة تواريخ عند remaining_hours = 0

---

**التاريخ:** 2025-10-18  
**الحالة:** قيد التنفيذ  
**الأولوية:** عالية
