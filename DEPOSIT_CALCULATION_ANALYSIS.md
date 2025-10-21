# 🔍 تحليل شامل لحساب العربون (Deposit Calculation)

## 📋 الوضع الحالي

### الدوال الموجودة

#### 1. `calculate_deposit_amount()` في `booking_calculations.py`
**الموقع:** Lines 17-58  
**الاستدعاء:** يتم استدعاؤها في `before_save()` (Line 53)

**المنطق:**
```python
def calculate_deposit_amount(booking_doc):
    # 1. تحديد المبلغ الأساسي
    if booking_doc.booking_type == 'Service':
        base_amount = booking_doc.total_amount or 0
    elif booking_doc.booking_type == 'Package':
        base_amount = booking_doc.total_amount_package or 0
    
    # 2. جلب نسبة العربون من General Settings (افتراضي 30%)
    deposit_percentage = 30
    try:
        general_settings = frappe.get_single('General Settings')
        if hasattr(general_settings, 'default_deposit_percentage'):
            deposit_percentage = general_settings.default_deposit_percentage
    except:
        pass
    
    # 3. حساب العربون
    if base_amount > 0:
        booking_doc.deposit_amount = round(base_amount * deposit_percentage / 100, 2)
```

**المميزات:**
- ✅ يتعامل مع نوع الحجز (Service/Package) بشكل صحيح
- ✅ يجلب النسبة من General Settings
- ✅ يسجل logs للتشخيص

**المشاكل:**
- ❌ **لا يطبق الحد الأدنى** (`minimum_booking_amount`)
- ❌ **لا يتحقق** إذا كان العربون أكبر من الإجمالي
- ❌ يستخدم `total_amount` بدلاً من `deposit_percentage` الموجود في الحجز

---

#### 2. `_compute_deposit()` في `booking.py`
**الموقع:** Lines 394-445  
**الاستدعاء:** ❌ **غير مستخدمة!**

**المنطق:**
```python
def _compute_deposit(self):
    # 1. حساب العربون من النسبة
    pct = float(getattr(self, 'deposit_percentage', 0) or 0)
    pct = max(0, min(pct, 100))  # تحديد النسبة بين 0-100
    
    if self.booking_type == 'Service':
        basis = float(getattr(self, 'total_amount', 0) or 0)
    else:
        basis = float(getattr(self, 'total_amount_package', 0) or 0)
    
    computed = round(basis * pct / 100.0, 2)
    
    # 2. التأكد من عدم تجاوز الإجمالي
    if computed > basis:
        computed = basis
    
    # 3. جلب الحد الأدنى من General Settings
    min_deposit = 0.0
    try:
        settings = frappe.db.get_singles_dict('General Settings') or {}
        for key in ('الحد الأدنى لمبلغ الحجز', 'minimum_booking_amount', 'min_booking_amount'):
            if key in settings:
                min_deposit = float(settings.get(key) or 0)
                break
    except:
        min_deposit = 0.0
    
    # 4. تطبيق الحد الأدنى
    if min_deposit > 0 and basis > 0:
        if computed < min_deposit:
            computed = min(min_deposit, basis)
    
    self.deposit_amount = computed
```

**المميزات:**
- ✅ **يطبق الحد الأدنى** من General Settings
- ✅ يتحقق من عدم تجاوز الإجمالي
- ✅ يستخدم `deposit_percentage` من الحجز نفسه
- ✅ يحدد النسبة بين 0-100

**المشاكل:**
- ❌ **غير مستخدمة!** لا يتم استدعاؤها في أي مكان

---

#### 3. `set_default_deposit_percentage()` في `booking_calculations.py`
**الموقع:** Lines 61-83  
**الاستدعاء:** يتم استدعاؤها في `validate()` (Line 89)

**المنطق:**
```python
def set_default_deposit_percentage(booking_doc):
    # إذا كانت النسبة موجودة مسبقاً، لا تفعل شيء
    if getattr(booking_doc, 'deposit_percentage', None) not in (None, ""):
        return
    
    # جلب النسبة من General Settings
    try:
        settings = frappe.db.get_singles_dict('General Settings')
        for key in ('نسبة العربون (%)', 'deposit_percentage', 'نسبة_العربون_%'):
            if key in settings:
                booking_doc.deposit_percentage = flt(settings.get(key))
                break
    except:
        pass
    
    # fallback: 30%
    if getattr(booking_doc, 'deposit_percentage', None) in (None, ""):
        booking_doc.deposit_percentage = 30
```

**المميزات:**
- ✅ يحترم القيمة المُدخلة يدوياً
- ✅ يجلب القيمة من General Settings
- ✅ له قيمة افتراضية (30%)

---

## 🐛 المشاكل الرئيسية

### 1. تضارب الدوال
- `calculate_deposit_amount()` يتم استدعاؤها في `before_save()`
- `_compute_deposit()` **غير مستخدمة** لكن لديها ميزات أفضل!

### 2. عدم تطبيق الحد الأدنى
- `calculate_deposit_amount()` **لا تطبق** `minimum_booking_amount`
- `_compute_deposit()` **تطبقه** لكنها غير مستخدمة

### 3. سيناريو الخطأ
```
المستخدم يُنشئ حجز:
  - booking_type: Package
  - total_amount_package: 500 ج.م
  - deposit_percentage: 30%

General Settings:
  - minimum_booking_amount: 200 ج.م

النتيجة الحالية:
  ❌ deposit_amount = 500 × 30% = 150 ج.م (أقل من الحد الأدنى!)

النتيجة المتوقعة:
  ✅ deposit_amount = 200 ج.م (الحد الأدنى)
```

---

## ✅ الحل المقترح

### الخيار 1: دمج الدالتين (مُفضّل)
استبدال `calculate_deposit_amount()` بمنطق `_compute_deposit()` الأكثر اكتمالاً.

### الخيار 2: استخدام `_compute_deposit()`
استدعاء `_compute_deposit()` بدلاً من `calculate_deposit_amount()` في `before_save()`.

### الخيار 3: تحسين `calculate_deposit_amount()`
إضافة منطق الحد الأدنى إلى `calculate_deposit_amount()`.

---

## 📝 التوصية

**استخدام `_compute_deposit()` لأنها:**
1. ✅ تطبق الحد الأدنى
2. ✅ تستخدم `deposit_percentage` من الحجز
3. ✅ تتحقق من عدم تجاوز الإجمالي
4. ✅ كود أكثر أماناً مع try/except

**التعديل المطلوب:**
```python
# في before_save()
# القديم ❌
calculate_deposit_amount(self)

# الجديد ✅
self._compute_deposit()
```

**أو دمج المنطقين في دالة واحدة محسّنة في `booking_calculations.py`.**

---

## 🧪 سيناريوهات الاختبار

### سيناريو 1: حجز خدمة عادي
```
booking_type: Service
total_amount: 1000 ج.م
deposit_percentage: 30%
minimum_booking_amount: 200 ج.م

المتوقع: deposit_amount = 300 ج.م (30% من 1000)
```

### سيناريو 2: حجز باقة مع مبلغ صغير
```
booking_type: Package
total_amount_package: 500 ج.م
deposit_percentage: 30%
minimum_booking_amount: 200 ج.م

الحالي: deposit_amount = 150 ج.م ❌
المتوقع: deposit_amount = 200 ج.م ✅ (الحد الأدنى)
```

### سيناريو 3: عربون أكبر من الإجمالي
```
booking_type: Service
total_amount: 100 ج.م
deposit_percentage: 150%
minimum_booking_amount: 50 ج.م

المتوقع: deposit_amount = 100 ج.م (لا يتجاوز الإجمالي)
```

### سيناريو 4: عربون يدوي
```
booking_type: Package
total_amount_package: 1000 ج.م
deposit_percentage: 50% (تم تعديله يدوياً)
minimum_booking_amount: 200 ج.م

المتوقع: deposit_amount = 500 ج.م (يحترم القيمة اليدوية)
```

---

## 🎯 الخلاصة

**المشكلة الرئيسية:**  
حساب العربون الحالي **لا يطبق الحد الأدنى** من General Settings، مما قد يؤدي إلى قبول عربون أقل من المطلوب.

**الحل:**  
استخدام `_compute_deposit()` أو تحسين `calculate_deposit_amount()` لتطبيق جميع القواعد:
1. حساب من النسبة
2. تطبيق الحد الأدنى
3. عدم تجاوز الإجمالي
4. احترام القيمة اليدوية

**الأولوية:** 🔴 **عالية** - يؤثر على عملية الدفع والحجز
