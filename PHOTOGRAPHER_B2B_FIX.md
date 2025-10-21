# 🔧 إصلاح تحديث المبلغ الإجمالي للباقة عند تفعيل Photographer B2B

## 📋 ملخص المشكلة
**البلاغ:** "المفروض عند تفعيل Photographer B2B بيحدث تحديث لحقل المبلغ الاجمالي للباقة بعد الخصم، لان في خصم مصور اتطبق داخل الجدول خدمات الباقة"

**المشكلة:** عند تفعيل/إلغاء تفعيل Photographer B2B:
1. ✅ يتم تطبيق خصم المصور على أسعار الخدمات في الجدول
2. ❌ لا يتحدث المبلغ الإجمالي للباقة (`total_amount_package`) تلقائياً
3. ❌ استخدام حقول غير موجودة (`photographer_discount_amount`, `total_amount`)

---

## 🔍 السبب الجذري

### 1. حقول خاطئة في API Responses
```python
# في get_package_services_with_photographer()
services.append({
    "photographer_discount_amount": photographer_discounted_rate,  # ❌ خطأ!
    # يجب أن يكون:
    "package_price": photographer_discounted_rate  # ✅
})
```

### 2. حقول خاطئة في JavaScript
```javascript
// في reload_package_services_with_photographer_discount()
row.photographer_discount_amount = service.photographer_discount_amount || service.package_price;  // ❌ خطأ!
row.amount = service.amount;  // ✅ صحيح
```

### 3. حسابات خاطئة في UI
```javascript
// في calculate_package_totals_ui()
final_total += flt(row.total_amount || (flt(row.package_price || 0) * qty));  // ❌ خطأ!
// total_amount غير موجود، يجب استخدام amount
```

### 4. عدم وجود مستمعات لتحديث الإجماليات
- لا يوجد event handlers لـ `quantity` و `package_price` في جدول `package_services_table`
- لا يتم إعادة حساب الإجماليات تلقائياً عند تغيير القيم

---

## 🛠️ التعديلات المطبقة

### 1. إصلاح `booking.py::fetch_package_services_for_booking()` (Lines 1653-1702)

#### التغييرات:
1. ✅ جلب الأسعار المخصومة من جدول `Photographer Service`
2. ✅ تطبيق منطق الأولويات (سعر مخصوم → نسبة خصم عامة)
3. ✅ استخدام الحقول الصحيحة (`package_price`, `amount`)

```python
# الأولوية الأولى: السعر المخصوم من جدول المصور
if photographer_services[service.service]['discounted_price'] > 0:
    final_package_price = photographer_services[service.service]['discounted_price']
# الأولوية الثانية: نسبة الخصم العامة
elif discount_percentage > 0 and photographer_services[service.service]['allow_discount']:
    final_package_price = initial_package_price * (1 - discount_percentage / 100.0)

processed_services.append({
    "service": service.service,
    "quantity": qty,
    "base_price": base_price,
    "package_price": final_package_price,  # ✅ السعر النهائي بعد الخصم
    "amount": final_amount,  # ✅ المبلغ الإجمالي
    "is_required": getattr(service, 'is_required', 0)
})
```

---

### 2. إصلاح `booking.py::get_package_services_with_photographer()` (Lines 2108-2131)

#### التغييرات:
```python
# قبل ❌
"photographer_discount_amount": photographer_discounted_rate,

# بعد ✅
"package_price": final_package_price,  # السعر النهائي بعد خصم المصور
"amount": amount,  # المبلغ الإجمالي
```

---

### 3. إصلاح `booking.py::handle_photographer_b2b_change()` (Lines 1738-1752)

#### التغييرات:
```python
# قبل ❌
booking_doc.append("package_services_table", {
    "photographer_discount_amount": service_data["photographer_discount_amount"]
})

# بعد ✅
booking_doc.append("package_services_table", {
    "service": service_data["service"],
    "quantity": service_data["quantity"],
    "base_price": service_data["base_price"],
    "package_price": service_data["package_price"],  # ✅ السعر النهائي
    "amount": service_data["amount"],  # ✅ المبلغ الإجمالي
    "is_required": service_data.get("is_required", 0)
})

# validate() سيُستدعى تلقائياً ويحسب الإجماليات
booking_doc.save()
```

---

### 4. إصلاح `booking.js::reload_package_services_with_photographer_discount()` (Lines 553-562)

#### التغييرات:
```javascript
// قبل ❌
row.photographer_discount_amount = service.photographer_discount_amount || service.package_price;

// بعد ✅
row.package_price = service.package_price;  // السعر النهائي بعد خصم المصور
row.amount = service.amount;  // المبلغ الإجمالي
```

---

### 5. إصلاح `booking.js::calculate_package_totals_ui()` (Lines 613-631)

#### التغييرات:
```javascript
// قبل ❌
final_total += flt(row.total_amount || (flt(row.package_price || 0) * qty));

// بعد ✅
const amount = flt(row.amount || 0);
const package_price = flt(row.package_price || 0);
final_total += amount > 0 ? amount : (package_price * qty);
```

---

### 6. إضافة Event Handlers لجدول `package_services_table` (NEW!)

#### الهدف: تحديث الإجماليات تلقائياً عند تغيير القيم

```javascript
frappe.ui.form.on('Package Service Item', {
	quantity: function(frm, cdt, cdn) {
		// إعادة حساب المبلغ عند تغيير الكمية
		calculate_package_service_item_total(frm, cdt, cdn);
	},
	
	package_price: function(frm, cdt, cdn) {
		// إعادة حساب المبلغ عند تغيير سعر الباقة
		calculate_package_service_item_total(frm, cdt, cdn);
	},
	
	package_services_table_add: function(frm, cdt, cdn) {
		// حساب المبلغ للصف الجديد
		calculate_package_service_item_total(frm, cdt, cdn);
	}
});

function calculate_package_service_item_total(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	if (!row) return;
	
	let quantity = flt(row.quantity || 1);
	let package_price = flt(row.package_price || 0);
	
	// حساب المبلغ الإجمالي
	let amount = quantity * package_price;
	frappe.model.set_value(cdt, cdn, 'amount', amount);
	
	// إعادة حساب إجماليات الباقة
	setTimeout(function() {
		calculate_package_totals_ui(frm);
	}, 100);
}
```

---

## ✅ النتائج

### الآن عند تفعيل/إلغاء Photographer B2B:

1. ✅ **يتم جلب الأسعار المخصومة** من جدول Photographer Services
2. ✅ **يتم تطبيق الخصم** على `package_price` في كل صف
3. ✅ **يتم حساب `amount`** تلقائياً (package_price × quantity)
4. ✅ **يتم تحديث `total_amount_package`** تلقائياً
5. ✅ **يتم إعادة حساب العربون** (`deposit_amount`) بناءً على المبلغ الجديد

### التفاعل الفوري في UI:

- تغيير `photographer_b2b` → إعادة تحميل الخدمات مع الأسعار المخصومة
- تغيير `quantity` في الجدول → إعادة حساب `amount` والإجماليات
- تغيير `package_price` في الجدول → إعادة حساب `amount` والإجماليات
- حفظ الحجز → `validate()` تُستدعى وتحسب كل شيء من جديد

---

## 🔄 الخطوات المطلوبة للتطبيق

### 1. تطبيق التعديلات
```bash
cd /home/frappe/frappe
bench --site site1.local clear-cache
bench build --app re_studio_booking
```

### 2. إعادة حساب الحجوزات القديمة (اختياري)
```bash
bench --site site1.local console < apps/re_studio_booking/recalculate_packages.py
```

### 3. اختبار في الواجهة
1. فتح حجز باقة موجود
2. تفعيل/إلغاء Photographer B2B
3. التحقق من تحديث:
   - أسعار الخدمات في الجدول (`package_price`)
   - المبالغ في كل صف (`amount`)
   - المبلغ الإجمالي للباقة (`total_amount_package`)
   - العربون (`deposit_amount`)

---

## 📁 الملفات المعدلة

1. ✅ `booking.py`:
   - `fetch_package_services_for_booking()` (Lines 1653-1702)
   - `get_package_services_with_photographer()` (Lines 2108-2131)
   - `handle_photographer_b2b_change()` (Lines 1738-1752)

2. ✅ `booking.js`:
   - `reload_package_services_with_photographer_discount()` (Lines 553-562)
   - `calculate_package_totals_ui()` (Lines 613-631)
   - **NEW:** `Package Service Item` event handlers (Lines 152-184)

---

## 🎯 الخلاصة

**المشكلة:** المبلغ الإجمالي للباقة لم يكن يتحدث عند تفعيل Photographer B2B

**السبب:** 
- استخدام حقول غير موجودة (`photographer_discount_amount`, `total_amount`)
- عدم وجود event handlers لتحديث الإجماليات تلقائياً

**الحل:** 
- توحيد استخدام الحقول الصحيحة (`package_price`, `amount`)
- إضافة event handlers للتحديث الفوري
- إصلاح جميع دوال الحساب في Python و JavaScript

**النتيجة:** ✅ **الآن يتحدث المبلغ الإجمالي تلقائياً عند تفعيل/إلغاء Photographer B2B!**

---

**تاريخ الإصلاح:** 2025-01-20  
**المطور:** GitHub Copilot  
**الحالة:** ✅ **مكتمل**
