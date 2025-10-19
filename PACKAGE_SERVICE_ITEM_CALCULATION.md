# 💰 تحديث حساب المبلغ الإجمالي في Package Service Item

## 🎯 المتطلب

تحديث حساب **المبلغ الإجمالي** (`total_amount`) في `Package Service Item` ليعتمد على **نوع الوحدة**:

### الحالتان:

#### 1️⃣ نوع الوحدة = **"مدة"** (خدمات زمنية)
```
المبلغ الإجمالي = سعر الساعة بالباقة × عدد الساعات
total_amount = package_price × quantity
```

**مثال:**
- خدمة: Full Location
- نوع الوحدة: مدة
- سعر الساعة بالباقة: 450 ريال
- عدد الساعات: 3
- **المبلغ الإجمالي = 450 × 3 = 1,350 ريال** ✅

---

#### 2️⃣ نوع الوحدة = **"كمية"** (خدمات كمية)
```
المبلغ الإجمالي = سعر الكمية × الكمية
total_amount = qty_price × qty
```

**مثال:**
- خدمة: Reels
- نوع الوحدة: كمية
- سعر الكمية: 50 ريال (لكل ريل)
- الكمية: 10 ريلز
- **المبلغ الإجمالي = 50 × 10 = 500 ريال** ✅

---

## ✅ التعديلات المطبقة

### في `package_service_item.py`:

#### 1️⃣ تحديث `calculate_total_amount()`

**قبل التعديل:**
```python
def calculate_total_amount(self):
    """Calculate total amount based on package price and quantity"""
    self.total_amount = flt(self.package_price) * flt(self.quantity or 1)
```

**بعد التعديل:**
```python
def calculate_total_amount(self):
    """
    Calculate total amount based on unit type:
    - If unit_type = 'مدة' (Duration): total = package_price × quantity (hours)
    - If unit_type = 'كمية' (Quantity): total = qty_price × qty
    """
    if self.unit_type == 'مدة':
        # للخدمات الزمنية: سعر الساعة × عدد الساعات
        self.total_amount = flt(self.package_price) * flt(self.quantity or 1)
    elif self.unit_type == 'كمية':
        # للخدمات الكمية: سعر الكمية × الكمية
        self.total_amount = flt(self.qty_price) * flt(self.qty or 1)
    else:
        # fallback: استخدام package_price × quantity
        self.total_amount = flt(self.package_price) * flt(self.quantity or 1)
```

---

#### 2️⃣ تحديث `fetch_service_details()`

تم إضافة منطق لتحديد `unit_type` تلقائياً بناءً على `Service.type_unit`:

```python
def fetch_service_details(self):
    """Fetch service details when service is selected"""
    if self.service:
        service_doc = frappe.get_doc("Service", self.service)
        
        # جلب اسم الخدمة
        if not self.service_name:
            self.service_name = service_doc.service_name_en
        
        # تحديد نوع الوحدة بناءً على Service
        if service_doc.type_unit:
            if service_doc.type_unit == 'مدة':
                self.unit_type = 'مدة'
            else:
                # أي نوع آخر (Reels, Photo, etc.) يعتبر كمية
                self.unit_type = 'كمية'
        
        # تعيين الأسعار الافتراضية
        if not self.base_price:
            self.base_price = service_doc.price
        if not self.package_price:
            self.package_price = service_doc.price
```

---

## 📊 أمثلة عملية

### مثال 1: خدمة زمنية (Full Location)

```
نوع الوحدة: مدة ⏱️
عدد الساعات: 4
سعر الساعة بالباقة: 400 ريال
المبلغ الإجمالي = 400 × 4 = 1,600 ريال ✅
```

---

### مثال 2: خدمة كمية (Reels)

```
نوع الوحدة: كمية 📦
الكمية: 15 ريل
سعر الكمية: 40 ريال/ريل
المبلغ الإجمالي = 40 × 15 = 600 ريال ✅
```

---

### مثال 3: خدمة كمية (Photo)

```
نوع الوحدة: كمية 📸
الكمية: 100 صورة
سعر الكمية: 5 ريال/صورة
المبلغ الإجمالي = 5 × 100 = 500 ريال ✅
```

---

## 🔄 التدفق الكامل

```
إضافة خدمة إلى Package Service Item
    ↓
جلب تفاصيل الخدمة (fetch_service_details)
    ↓
تحديد unit_type بناءً على Service.type_unit
    ↓
هل unit_type = "مدة"؟
    ↓
نعم → total_amount = package_price × quantity
    ↓
لا (unit_type = "كمية") → total_amount = qty_price × qty
    ↓
حفظ المبلغ الإجمالي ✅
```

---

## 📋 الحقول المستخدمة

### للخدمات الزمنية (مدة):
- `unit_type` = "مدة"
- `quantity` - عدد الساعات
- `package_price` - سعر الساعة بالباقة
- `total_amount` = `package_price × quantity`

### للخدمات الكمية:
- `unit_type` = "كمية"
- `qty` - الكمية (عدد الريلز، الصور، إلخ)
- `qty_price` - سعر الكمية الواحدة
- `total_amount` = `qty_price × qty`

---

## 🧪 الاختبار

### خطوات الاختبار:

#### اختبار 1: خدمة زمنية
1. افتح **Package**
2. أضف خدمة في `Package Service Item`
3. اختر خدمة نوعها **"مدة"** (مثل Full Location)
4. ✅ تحقق من `unit_type = مدة`
5. أدخل `quantity = 3` (عدد الساعات)
6. أدخل `package_price = 450`
7. ✅ تحقق من `total_amount = 1,350` (450 × 3)

#### اختبار 2: خدمة كمية
1. أضف خدمة أخرى
2. اختر خدمة نوعها **"Reels"** أو **"Photo"**
3. ✅ تحقق من `unit_type = كمية`
4. أدخل `qty = 10` (عدد الريلز)
5. أدخل `qty_price = 50`
6. ✅ تحقق من `total_amount = 500` (50 × 10)

---

## 🎨 عرض الحقول في الواجهة

### عند اختيار unit_type = "مدة":
```
┌─────────────────────────────────────────┐
│ الخدمة: Full Location                  │
│ نوع الوحدة: مدة ⏱️                     │
│                                         │
│ عدد الساعات: 3                         │
│ سعر الساعة بالباقة: 450 ريال           │
│                                         │
│ المبلغ الإجمالي: 1,350 ريال ✅         │
└─────────────────────────────────────────┘
```

### عند اختيار unit_type = "كمية":
```
┌─────────────────────────────────────────┐
│ الخدمة: Reels Service                  │
│ نوع الوحدة: كمية 📦                    │
│                                         │
│ الكمية: 10 ريل                         │
│ سعر الكمية: 50 ريال/ريل                │
│                                         │
│ المبلغ الإجمالي: 500 ريال ✅           │
└─────────────────────────────────────────┘
```

---

## 📊 جدول مقارنة شامل

| الخدمة | نوع الوحدة | الكمية/الساعات | السعر | المبلغ الإجمالي | الصيغة |
|--------|------------|----------------|-------|-----------------|--------|
| Full Location | مدة | 3 ساعات | 450 ريال/ساعة | 1,350 | 450 × 3 |
| Half Location | مدة | 2 ساعات | 300 ريال/ساعة | 600 | 300 × 2 |
| Reels | كمية | 10 ريل | 50 ريال/ريل | 500 | 50 × 10 |
| Photo | كمية | 100 صورة | 5 ريال/صورة | 500 | 5 × 100 |
| Promo | كمية | 3 فيديو | 200 ريال/فيديو | 600 | 200 × 3 |

---

## ✅ الفوائد

1. **دقة الحسابات** ✅
   - حساب صحيح بناءً على نوع الخدمة

2. **مرونة التسعير** ✅
   - خدمات زمنية: سعر بالساعة
   - خدمات كمية: سعر بالوحدة

3. **وضوح للعميل** ✅
   - يعرف بالضبط كيف يتم حساب المبلغ

4. **سهولة الإدارة** ✅
   - حقول واضحة حسب نوع الخدمة

---

## 🎯 ملخص التغييرات

### ملف واحد معدل:
- **`package_service_item.py`**

### دالتان محدثتان:
1. **`calculate_total_amount()`** - منطق الحساب الجديد
2. **`fetch_service_details()`** - تحديد unit_type تلقائياً

### المنطق:
```python
if unit_type == 'مدة':
    total_amount = package_price × quantity
elif unit_type == 'كمية':
    total_amount = qty_price × qty
```

---

## 🚀 الخطوات التالية

1. ✅ مسح الذاكرة المؤقتة: `bench clear-cache`
2. ✅ إعادة تشغيل النظام: `bench restart`
3. 🧪 اختبار من الواجهة
4. 📝 توثيق الاختبارات

---

تم التطبيق بنجاح! 🎉

تاريخ التطبيق: 18 أكتوبر 2025
