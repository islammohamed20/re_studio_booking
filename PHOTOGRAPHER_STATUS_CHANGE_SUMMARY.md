# ✅ تم إزالة التكرار من Photographer

## 🎯 التغيير
**الاكتفاء بحقل "status" فقط** بدلاً من وجود "is_active" و "status" معاً

---

## 📝 ما تم:

### ✅ تم الحذف:
- ❌ Custom Field "is_active" من Photographer DocType
- ❌ ملف patch: `add_is_active_to_photographer.py`
- ❌ جميع الإشارات لـ is_active في Photographer

### ✅ تم التحديث:
- 📄 `photographer.js` - استخدام status بدلاً من is_active
- 📄 `performance.py` - get_active_photographers_count يستخدم status
- 📄 `performance.py` - index على status بدلاً من is_active
- 📄 `fix_issues.py` - إنشاء مصور افتراضي بـ status

### ✅ تم الاحتفاظ بـ is_active في:
- ✔️ **Photographer Service** (child table)
- ✔️ **Photographer Studios**
- ✔️ **Service**

---

## 🔄 الاستخدام الجديد

### حالات المصور (status):
```
Active     → نشط ومتاح
On Leave   → في إجازة
Inactive   → غير نشط
```

### مثال Python:
```python
# المصورين النشطين
frappe.db.count('Photographer', {'status': 'Active'})

# التحقق من الحالة
if photographer.status == "Active":
    # متاح للحجز
```

### مثال JavaScript:
```javascript
if (frm.doc.status === 'Active') {
    frm.page.set_indicator(__('نشط'), 'green');
}
```

---

## ✅ النتيجة
- لا تكرار
- أكثر وضوحاً
- أسهل في الصيانة

**التاريخ:** 2025-10-18  
**الحالة:** ✅ مكتمل
