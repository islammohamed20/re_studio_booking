# 🔄 إزالة التكرار: من is_active إلى status

## 📋 الملخص
تم إزالة حقل **is_active** (Check) من Photographer واستبداله بالاعتماد الكامل على حقل **status** (Select) لتجنب التكرار والتعقيد.

---

## ❌ الوضع السابق (قبل التغيير)

### المشكلة:
كان لدينا **حقلان** للتحكم في حالة المصور:

1. **is_active** (Check): 
   - نوع: Custom Field
   - قيم: 1 أو 0
   - مضاف عبر patch

2. **status** (Select):
   - نوع: حقل أصلي في DocType
   - قيم: Active / On Leave / Inactive

### التكرار والمشاكل:
- ❌ ارتباك: أي حقل يُستخدم للتحقق من نشاط المصور؟
- ❌ تعقيد: إدارة حقلين بدلاً من واحد
- ❌ عدم توافق: is_active في photographer.js لكن غير موجود في DocType الأصلي

---

## ✅ الوضع الجديد (بعد التغيير)

### الحل:
الاعتماد على **حقل status فقط** مع 3 حالات واضحة:

```
status = "Active"     → المصور نشط ومتاح للحجوزات
status = "On Leave"   → المصور في إجازة
status = "Inactive"   → المصور غير نشط
```

### الفوائد:
- ✅ **لا تكرار**: حقل واحد فقط
- ✅ **أكثر وضوحاً**: 3 حالات مفصلة بدلاً من نعم/لا
- ✅ **تناسق**: جميع الاستعلامات تستخدم `status='Active'`
- ✅ **مرونة**: يمكن إضافة حالات جديدة مستقبلاً (مثل: "Training", "Suspended")

---

## 🔧 التغييرات المُطبقة

### 1. قاعدة البيانات
```python
# حذف Custom Field
frappe.delete_doc("Custom Field", "Photographer-is_active", force=1)
```

### 2. الملفات المُعدلة

#### **photographer.js** (تم التحديث مسبقاً)
```javascript
// القديم (خطأ - الحقل غير موجود):
if (frm.doc.is_active) {
    frm.page.set_indicator(__('نشط'), 'green');
}

// الجديد (صحيح):
if (frm.doc.status === 'Active') {
    frm.page.set_indicator(__('نشط'), 'green');
} else if (frm.doc.status === 'On Leave') {
    frm.page.set_indicator(__('في إجازة'), 'orange');
} else {
    frm.page.set_indicator(__('غير نشط'), 'red');
}
```

#### **performance.py**
```python
# القديم:
def get_active_photographers_count():
    return frappe.db.count('Photographer', {'is_active': 1})

# الجديد:
def get_active_photographers_count():
    """Get active photographers count based on status field"""
    return frappe.db.count('Photographer', {'status': 'Active'})
```

```python
# القديم:
("tabPhotographer", "is_active", "photographer_active_idx"),

# الجديد:
("tabPhotographer", "status", "photographer_status_idx"),
```

#### **fix_issues.py**
```python
# القديم:
if not frappe.db.exists("Photographer", {"is_active": 1}):
    photographer = frappe.get_doc({
        "doctype": "Photographer",
        "photographer_name": "أحمد محمد",
        "is_active": 1,
        ...
    })

# الجديد:
if not frappe.db.exists("Photographer", {"status": "Active"}):
    photographer = frappe.get_doc({
        "doctype": "Photographer",
        "first_name": "أحمد",
        "last_name": "محمد",
        "status": "Active",
        ...
    })
```

### 3. الملفات المحذوفة
```bash
# تم حذف patch file:
rm /apps/re_studio_booking/re_studio_booking/patches/add_is_active_to_photographer.py
```

---

## ⚠️ ملاحظات مهمة

### ✅ تم الاحتفاظ بـ is_active في:
- **Photographer Service** (child table) ← صحيح! لتفعيل/تعطيل خدمات معينة
- **Photographer Studios** ← صحيح! لتفعيل/تعطيل استوديوهات معينة
- **Service** ← صحيح! لتفعيل/تعطيل خدمات معينة

### ❌ تم إزالة is_active من:
- **Photographer** (DocType الرئيسي) ← استبدلناه بـ status

---

## 🧪 نتائج الاختبار

```
✅ Custom Field 'is_active': تم الحذف
✅ حقل 'status': موجود (نوع: Select)
   الخيارات: Active / On Leave / Inactive
✅ عدد المصورين النشطين (status='Active'): يعمل بشكل صحيح
✅ Photographer Service 'is_active': موجود (يجب أن يبقى)
✅ اختبار إنشاء مصور: validation يعمل بشكل صحيح
```

---

## 📊 الاستخدام الجديد

### في Python:
```python
# الحصول على المصورين النشطين
active_photographers = frappe.get_all(
    "Photographer",
    filters={"status": "Active"},
    fields=["name", "first_name", "last_name", "phone"]
)

# التحقق من حالة مصور
photographer = frappe.get_doc("Photographer", "أحمد")
if photographer.status == "Active":
    # المصور متاح
    pass
elif photographer.status == "On Leave":
    # المصور في إجازة
    pass
```

### في JavaScript:
```javascript
// عرض مؤشر الحالة
if (frm.doc.status === 'Active') {
    frm.page.set_indicator(__('نشط'), 'green');
} else if (frm.doc.status === 'On Leave') {
    frm.page.set_indicator(__('في إجازة'), 'orange');
} else {
    frm.page.set_indicator(__('غير نشط'), 'red');
}
```

### في الاستعلامات:
```python
# عد المصورين النشطين
frappe.db.count('Photographer', {'status': 'Active'})

# البحث عن مصورين متاحين (ليسوا في إجازة)
frappe.db.get_all('Photographer', {
    'status': ['in', ['Active']]
})
```

---

## 🎯 الخلاصة

| الجانب | قبل | بعد |
|--------|-----|-----|
| **عدد الحقول** | 2 (is_active + status) | 1 (status فقط) |
| **التعقيد** | مربك (أي حقل؟) | واضح |
| **الحالات** | 2 (نشط/غير نشط) | 3 (نشط/إجازة/غير نشط) |
| **الأداء** | نفس الأداء | نفس الأداء + index محسّن |
| **الصيانة** | صعبة (حقلان) | سهلة (حقل واحد) |

---

## ✅ التطبيق

```bash
# تم التنفيذ:
1. حذف Custom Field من قاعدة البيانات
2. تحديث 4 ملفات Python
3. تحديث 1 ملف JavaScript
4. حذف 1 ملف patch
5. تشغيل migrate
6. إعادة تشغيل النظام
7. اختبار شامل

# النتيجة: ✅ النظام يعمل بشكل صحيح
```

---

**التاريخ:** 18 أكتوبر 2025  
**الإصدار:** Re Studio Booking 0.0.1  
**الحالة:** ✅ تم التطبيق بنجاح
