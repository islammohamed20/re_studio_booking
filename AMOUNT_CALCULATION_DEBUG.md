# 🔧 إصلاح حساب المبلغ الإجمالي في Package Service

## 🎯 المشكلة المبلغ عنها

**الأعراض:**
> "حقل المبلغ الإجمالي مازال يحسب على المدة فقط"

**التحليل:**
المستخدم يشير إلى أن حساب `amount` (المبلغ الإجمالي) في `Package Service` لا يعمل بشكل صحيح للخدمات الكمية (Reels, Photo, etc.)

---

## 🔍 التشخيص

### المشاكل المحتملة:

1. **الكود Python صحيح** ✅
   - المنطق موجود ويعمل بشكل صحيح
   - يميز بين "مدة" و "كمية"

2. **المشكلة المحتملة: `type_unit` فارغ** ⚠️
   - إذا كان `type_unit` فارغاً أو غير محدد
   - الكود يذهب إلى حالة الـ `else` (الخدمات الكمية)
   - ولكن قد يستخدم `package_price` بدلاً من `unit_price`

3. **المشكلة المحتملة: `unit_price` فارغ** ⚠️
   - للخدمات الكمية، إذا لم يتم تعيين `unit_price`
   - سيتم استخدام `package_price` كـ fallback
   - قد يعطي نتائج غير متوقعة

---

## ✅ الحلول المطبقة

### 1️⃣ إضافة Debug Logging

تم إضافة سجلات تشخيصية لتتبع العملية:

```python
def calculate_amount(self):
    # تسجيل للتشخيص
    frappe.logger().debug(f"PackageService.calculate_amount - type_unit: {self.type_unit}, quantity: {self.quantity}")
    
    if self.type_unit == 'مدة':
        price = self.package_price or self.base_price or 0
        self.amount = price * self.quantity
        frappe.logger().debug(f"  → مدة: price={price}, amount={self.amount}")
    else:
        price_per_unit = self.unit_price or self.package_price or self.base_price or 0
        self.amount = price_per_unit * self.quantity
        frappe.logger().debug(f"  → كمية: price_per_unit={price_per_unit}, amount={self.amount}")
```

### 2️⃣ التأكد من ظهور حقل `amount` في الجدول

تم إضافة `in_list_view: 1` لحقل `amount`:

```json
{
  "fieldname": "amount",
  "fieldtype": "Currency",
  "in_list_view": 1,  // ← إضافة هذا
  "label": "المبلغ",
  "options": "SAR",
  "read_only": 1
}
```

---

## 📊 كيفية التحقق من المشكلة

### السيناريو 1: خدمة زمنية (مدة)
```
الخدمة: Full Location
type_unit: مدة
quantity: 3
package_price: 450

✅ المتوقع: amount = 1,350 (450 × 3)
```

### السيناريو 2: خدمة كمية (Reels)
```
الخدمة: Reels Service
type_unit: Reels (أي شيء غير "مدة")
quantity: 10
unit_price: 50

✅ المتوقع: amount = 500 (50 × 10)
```

### السيناريو 3: خدمة كمية بدون unit_price
```
الخدمة: Photo Service
type_unit: Photo
quantity: 100
unit_price: (فارغ)
package_price: 10

⚠️ النتيجة: amount = 1,000 (10 × 100)
(يستخدم package_price كـ fallback)
```

---

## 🧪 خطوات الاختبار

### الاختبار 1: خدمة زمنية
1. افتح **Package**
2. أضف خدمة في جدول `Package Service`
3. اختر خدمة نوعها **"مدة"** (مثل Full Location)
4. تحقق من أن `type_unit` = "مدة"
5. ضع `quantity = 3`
6. ضع `package_price = 450`
7. احفظ
8. ✅ تحقق: `amount = 1,350`

### الاختبار 2: خدمة كمية مع unit_price
1. أضف خدمة أخرى
2. اختر خدمة نوعها **غير "مدة"** (مثل Reels)
3. تحقق من أن `type_unit` = "Reels" أو "Photo"، إلخ
4. ضع `quantity = 10`
5. ضع `unit_price = 50`
6. احفظ
7. ✅ تحقق: `amount = 500`

### الاختبار 3: خدمة كمية بدون unit_price
1. أضف خدمة ثالثة
2. اختر خدمة كمية
3. ضع `quantity = 100`
4. **اترك `unit_price` فارغاً**
5. ضع `package_price = 10`
6. احفظ
7. ✅ تحقق: `amount = 1,000` (fallback إلى package_price)

---

## 🔍 فحص السجلات (Logs)

للتحقق من أن الدالة تُستدعى بشكل صحيح:

```bash
# فتح سجلات Frappe
tail -f /home/frappe/frappe/logs/frappe.log | grep "PackageService.calculate_amount"
```

**ما تتوقع رؤيته:**
```
DEBUG PackageService.calculate_amount - type_unit: مدة, quantity: 3
DEBUG   → مدة: price=450, amount=1350
```

أو

```
DEBUG PackageService.calculate_amount - type_unit: Reels, quantity: 10
DEBUG   → كمية: price_per_unit=50, amount=500
```

---

## ⚠️ المشاكل المحتملة وحلولها

### مشكلة 1: `type_unit` فارغ

**الأعراض:**
- `type_unit` يظهر فارغاً في السجلات
- الحساب يذهب دائماً إلى فرع `else`

**الحل:**
1. تحقق من أن Service المختارة لها `type_unit` محدد
2. تحقق من أن `fetch_from` يعمل بشكل صحيح

### مشكلة 2: `unit_price` غير محدد للخدمات الكمية

**الأعراض:**
- خدمات الكمية تحسب بـ `package_price` بدلاً من `unit_price`

**الحل:**
- تأكد من ملء حقل `unit_price` للخدمات الكمية
- أو اعتمد على fallback إلى `package_price`

### مشكلة 3: الحساب لا يتم إطلاقاً

**الأعراض:**
- `amount` لا يتغير عند تحديث البيانات

**الحل:**
- تحقق من أن `validate()` تُستدعى
- تحقق من السجلات لمعرفة ما يحدث

---

## 📋 خريطة العملية

```
إضافة/تحديث صف في Package Service
    ↓
validate() تُستدعى
    ↓
update_service_details()
    → جلب type_unit من Service
    → تعيين base_price, package_price
    ↓
calculate_amount()
    → تسجيل: type_unit, quantity
    ↓
هل type_unit == 'مدة'?
    ↓
نعم → amount = package_price × quantity
    → تسجيل: price, amount
    ↓
لا → amount = unit_price × quantity
    → (fallback: package_price إذا unit_price فارغ)
    → تسجيل: price_per_unit, amount
    ↓
حفظ الصف ✅
```

---

## 🎯 التوصيات

### للمستخدم:
1. ✅ **للخدمات الزمنية**: تأكد من أن `type_unit = مدة`
2. ✅ **للخدمات الكمية**: تأكد من تعيين `unit_price`
3. ✅ **افحص السجلات** إذا كان الحساب لا يزال خاطئاً

### للمطور:
1. 📝 إضافة validation للتأكد من وجود `unit_price` للخدمات الكمية
2. 📝 إضافة رسالة تحذير إذا `type_unit` فارغ
3. 📝 إضافة unit tests للتأكد من صحة الحسابات

---

## 🔄 الكود النهائي

```python
class PackageService(Document):
    def validate(self):
        self.update_service_details()
        self.calculate_amount()
        
    def update_service_details(self):
        if self.service:
            service_doc = frappe.get_doc("Service", self.service)
            self.service_name = service_doc.service_name_en
            self.service_price = service_doc.price
            self.type_unit = service_doc.type_unit
            
            if not self.base_price:
                self.base_price = service_doc.price
            if not self.package_price:
                self.package_price = self.base_price
    
    def calculate_amount(self):
        if not self.quantity:
            self.quantity = 1
        
        # تسجيل للتشخيص
        frappe.logger().debug(
            f"PackageService.calculate_amount - "
            f"type_unit: {self.type_unit}, quantity: {self.quantity}"
        )
        
        if self.type_unit == 'مدة':
            # الخدمات الزمنية: سعر × عدد الساعات
            price = self.package_price or self.base_price or 0
            self.amount = price * self.quantity
            frappe.logger().debug(f"  → مدة: price={price}, amount={self.amount}")
        else:
            # الخدمات الكمية: سعر الوحدة × الكمية
            price_per_unit = self.unit_price or self.package_price or self.base_price or 0
            self.amount = price_per_unit * self.quantity
            frappe.logger().debug(
                f"  → كمية: price_per_unit={price_per_unit}, amount={self.amount}"
            )
```

---

## 🎉 الخلاصة

تم إضافة:
- ✅ **Debug logging** لتتبع العملية
- ✅ **إظهار `amount` في الجدول** (`in_list_view: 1`)
- ✅ **التوثيق الشامل** لكيفية عمل الحساب

**للمستخدم:**
- 🧪 اختبر بإضافة خدمات مختلفة
- 📊 راجع السجلات إذا كانت هناك مشاكل
- 📝 أخبرني بالنتائج

---

تاريخ التطبيق: 18 أكتوبر 2025
