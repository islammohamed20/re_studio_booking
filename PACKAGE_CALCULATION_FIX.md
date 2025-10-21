# 🔧 إصلاح مشكلة حساب المبلغ الإجمالي للباقة بعد الخصم

## 📋 ملخص المشكلة
**البلاغ:** "في مشكلة داخل حقل حساب المبلغ الاجمالي للباقة بعد الخصم"

**السبب:** استخدام حقول **غير موجودة** في DocType (Package Service Item) أدى إلى حسابات خاطئة.

---

## 🔍 السبب الجذري

### الحقول المستخدمة خطأً ❌
```python
# في booking_calculations.py
hourly_rate = flt(getattr(service_row, 'hourly_rate', 0))  # ❌ غير موجود
photographer_discounted_rate = flt(getattr(service_row, 'photographer_discounted_rate', 0))  # ❌ غير موجود

# في booking.py
row.photographer_discount_amount = photographer_discounted_rate  # ❌ غير موجود
```

### الحقول الصحيحة من DocType ✅
```json
{
  "base_price": "السعر الأساسي من Service master",
  "package_price": "سعر الساعة في الباقة (قابل للتعديل + يطبق عليه خصم المصور)",
  "quantity": "عدد الساعات",
  "amount": "المبلغ الإجمالي (package_price × quantity)"
}
```

---

## 🛠️ التعديلات المطبقة

### 1. `booking_calculations.py::calculate_package_totals()` (Lines 247-284)

#### قبل التعديل ❌
```python
def calculate_package_totals(booking_doc):
    for service_row in booking_doc.package_services_table:
        quantity = flt(getattr(service_row, 'quantity', 0))
        hourly_rate = flt(getattr(service_row, 'hourly_rate', 0))  # ❌
        photographer_discounted_rate = flt(getattr(service_row, 'photographer_discounted_rate', 0))  # ❌
        
        if photographer_discounted_rate > 0:
            discounted_amount_row = quantity * photographer_discounted_rate
            service_row.total_amount = discounted_amount_row  # ❌ خطأ: total_amount
```

#### بعد التعديل ✅
```python
def calculate_package_totals(booking_doc):
    for service_row in booking_doc.package_services_table:
        quantity = flt(getattr(service_row, 'quantity', 0))
        base_price = flt(getattr(service_row, 'base_price', 0))  # ✅
        package_price = flt(getattr(service_row, 'package_price', 0))  # ✅
        
        if not base_price and package_price:
            base_price = package_price
        
        # حساب المبالغ
        base_amount_row = quantity * base_price
        final_amount_row = quantity * package_price
        service_row.amount = final_amount_row  # ✅ الحقل الصحيح
```

---

### 2. `booking_calculations.py::_build_package_rows()` (Lines 351-391)

#### قبل التعديل ❌
```python
def _build_package_rows(booking_doc):
    for service in package_services:
        # ... منطق الحساب ...
        
        booking_doc.append('package_services_table', {
            'service': service.service,
            'quantity': qty,
            'hourly_rate': hourly_rate,  # ❌ غير موجود
            'photographer_discounted_rate': photographer_discounted_rate,  # ❌ غير موجود
            'total_amount': total_amount  # ❌ خطأ في الاسم
        })
```

#### بعد التعديل ✅
```python
def _build_package_rows(booking_doc):
    for service in package_services:
        # استخدام package_price من الباقة أو base_price
        initial_package_price = flt(getattr(service, 'package_price', 0) or 0)
        if initial_package_price <= 0:
            initial_package_price = base_price
        
        # تطبيق خصم المصور
        final_package_price = initial_package_price
        if service.service in photographer_services:
            if photographer_services[service.service]['discounted_price'] > 0:
                final_package_price = photographer_services[service.service]['discounted_price']
            elif photographer_discount > 0:
                final_package_price = initial_package_price * (1 - photographer_discount / 100.0)
        
        amount = qty * final_package_price
        
        booking_doc.append('package_services_table', {
            'service': service.service,
            'quantity': qty,
            'base_price': base_price,  # ✅ السعر الأساسي
            'package_price': final_package_price,  # ✅ السعر بعد الخصم
            'amount': amount,  # ✅ المبلغ الإجمالي
            'is_required': service.is_required if hasattr(service, 'is_required') else 0
        })
```

---

### 3. `booking.py::_build_package_rows()` (Lines 320-377)

#### قبل التعديل ❌
```python
def _build_package_rows(self, ctx):
    for row in (self.package_services_table or []):
        base_price = float(getattr(row, 'base_price', 0) or getattr(row, 'package_price', 0) or 0)
        
        # حساب خاطئ
        photographer_discounted_rate = base_price
        # ... منطق الخصم ...
        
        row.photographer_discount_amount = photographer_discounted_rate  # ❌ غير موجود
        row.amount = photographer_discounted_rate * qty
```

#### بعد التعديل ✅
```python
def _build_package_rows(self, ctx):
    for row in (self.package_services_table or []):
        base_price = float(getattr(row, 'base_price', 0) or 0)
        package_price = float(getattr(row, 'package_price', 0) or base_price or 0)
        
        # حساب السعر النهائي بعد خصم المصور
        final_price_per_unit = package_price
        
        if service_name in photographer_services:
            if photographer_services[service_name]['discounted_price'] > 0:
                final_price_per_unit = photographer_services[service_name]['discounted_price']
            elif discount_pct > 0 and service_name in allowed:
                final_price_per_unit = package_price * (1 - discount_pct / 100.0)
        
        # تعيين القيم الصحيحة
        row.package_price = final_price_per_unit  # ✅ السعر بعد الخصم
        row.amount = final_price_per_unit * qty  # ✅ المبلغ الإجمالي
```

---

## ✅ النتائج

### اختبار على حجز فعلي (BOOK-0002)

#### قبل الإصلاح ❌
```
المبلغ الأساسي: 8,000.00 ج.م
المبلغ بعد الخصم: 7,400.00 ج.م  ← خطأ!
```

#### بعد الإصلاح ✅
```
المبلغ الأساسي: 8,000.00 ج.م
المبلغ بعد الخصم: 4,800.00 ج.م  ← صحيح!
```

### تفاصيل الخدمات

| الخدمة | الكمية | السعر الأساسي | سعر الباقة | المبلغ |
|--------|--------|---------------|------------|--------|
| Full Location | 3 ساعات | 800 ج.م | 600 ج.م | **1,800 ج.م** |
| 1 Camera | 3 ساعات | 1,000 ج.م | 600 ج.م | **1,800 ج.م** |
| Mics + Lights | 3 ساعات | 600 ج.م | 200 ج.م | **600 ج.م** |
| Montage | 1 ساعة | 800 ج.م | 600 ج.م | **600 ج.م** |

**الإجمالي:** 1,800 + 1,800 + 600 + 600 = **4,800 ج.م** ✅

**نسبة الخصم:** (8,000 - 4,800) / 8,000 = **40%** ✅

---

## 🔄 الخطوات المطلوبة للتطبيق

### 1. تطبيق التعديلات
```bash
cd /home/frappe/frappe
bench --site site1.local clear-cache
```

### 2. إعادة حساب الحجوزات القديمة
```bash
# تشغيل سكريبت إعادة الحساب
bench --site site1.local console < apps/re_studio_booking/recalculate_packages.py
```

### 3. التحقق من النتائج
```bash
# تشغيل سكريبت الاختبار
bench --site site1.local console < apps/re_studio_booking/test_package_calculation.py
```

---

## 📁 الملفات المعدلة

1. ✅ `/apps/re_studio_booking/re_studio_booking/re_studio_booking/doctype/booking/booking_calculations.py`
   - `calculate_package_totals()` (Lines 247-284)
   - `_build_package_rows()` (Lines 317-391)

2. ✅ `/apps/re_studio_booking/re_studio_booking/re_studio_booking/doctype/booking/booking.py`
   - `_build_package_rows()` (Lines 320-377)

---

## 📝 الملفات المساعدة

1. ✅ `test_package_calculation.py` - سكريبت اختبار الحسابات
2. ✅ `recalculate_packages.py` - سكريبت إعادة حساب الحجوزات القديمة
3. ✅ `inspect_booking.py` - سكريبت فحص تفاصيل حجز معين
4. ✅ `test_package_calculation.md` - توثيق الاختبار
5. ✅ `PACKAGE_CALCULATION_FIX.md` - هذا الملف

---

## 🎯 الخلاصة

**المشكلة:** استخدام حقول غير موجودة في DocType أدى إلى حسابات خاطئة.

**الحل:** توحيد استخدام الحقول الصحيحة:
- `base_price` - السعر الأساسي
- `package_price` - سعر الباقة (مع الخصم)
- `amount` - المبلغ الإجمالي

**النتيجة:** ✅ **تم إصلاح المشكلة بنجاح!**

---

## ⚠️ ملاحظات مهمة

1. **الحجوزات القديمة:** يجب إعادة حفظها لتطبيق الحسابات الجديدة
2. **الحقول القديمة:** لا تزال موجودة في قاعدة البيانات لكنها لم تعد مستخدمة
3. **التوافق:** النظام يعمل بشكل صحيح مع الحقول الجديدة

---

**تاريخ الإصلاح:** 2025-01-20  
**المطور:** GitHub Copilot  
**الحالة:** ✅ **مكتمل**
