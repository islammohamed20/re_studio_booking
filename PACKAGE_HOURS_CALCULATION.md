# 📋 توثيق حساب ساعات الباقة - Package Hours Calculation

## 🎯 الميزات المطبقة

### ✅ 1. اختيار الباقة
عند اختيار باقة في نموذج Booking:
- يتم ملء حقل **عدد الساعات المتبقية** (`remaining_hours`) تلقائياً من إجمالي ساعات الباقة (`total_hours`)
- يتم جلب جميع خدمات الباقة مع تحديد خانة "إجباري" افتراضياً

### ✅ 2. حساب الساعات تلقائياً
في جدول **تواريخ الحجز** (`package_booking_dates`):
- عند اختيار **وقت البداية** (`start_time`) و **وقت النهاية** (`end_time`):
  - يتم حساب عدد الساعات تلقائياً
  - يتم وضع النتيجة في حقل **عدد الساعات** (`hours`)
  - معالجة حالة عبور منتصف الليل (إذا كان وقت النهاية أصغر من البداية)

### ✅ 3. جمع إجمالي الساعات المستخدمة
- يتم جمع كل الساعات من جميع صفوف جدول **تواريخ الحجز**
- النتيجة توضع في حقل **عدد الساعات المستخدمة** (`used_hours`)
- يتم التحديث فوراً عند تغيير أي وقت في الجدول

### ✅ 4. حساب الساعات المتبقية
- الصيغة: `remaining_hours = total_hours - used_hours`
- يتم التحديث تلقائياً عند إضافة أو تعديل تواريخ الحجز
- الحد الأدنى = 0 (لا يمكن أن يكون سالباً)

### ✅ 5. منع إضافة حجوزات عند نفاد الساعات
- عندما `remaining_hours = 0`:
  - يتم منع إضافة صفوف جديدة في جدول تواريخ الحجز
  - يظهر تنبيه: **"⚠️ تم استنفاد جميع ساعات الباقة. لا يمكن إضافة تواريخ حجز إضافية"**
  - يتم حذف الصف الجديد تلقائياً

### ✅ 6. رسالة التحذير المحسنة
- تم تغيير رسالة التجاوز من `throw` (خطأ يوقف الحفظ) إلى `msgprint` (تنبيه فقط)
- الرسالة: **"⚠️ تم استنفاد جميع ساعات الباقة"**
- تظهر كـ alert من الأسفل (نوع: red indicator)
- لا توقف عملية الحفظ

---

## 🔧 التطبيق التقني

### في ملف `booking.js`:

```javascript
// Event handlers لجدول Package Booking Date
frappe.ui.form.on('Package Booking Date', {
    start_time: function(frm, cdt, cdn) {
        calculate_hours_for_row(frm, cdt, cdn);
    },
    
    end_time: function(frm, cdt, cdn) {
        calculate_hours_for_row(frm, cdt, cdn);
    },
    
    package_booking_dates_add: function(frm, cdt, cdn) {
        check_remaining_hours_before_add(frm);
    }
});

// وظيفة حساب الساعات للصف
function calculate_hours_for_row(frm, cdt, cdn) {
    // حساب الفرق بين start_time و end_time
    // تحديث حقل hours
    // استدعاء calculate_total_used_hours
}

// وظيفة جمع إجمالي الساعات
function calculate_total_used_hours(frm) {
    // جمع كل hours من package_booking_dates
    // تحديث used_hours
    // حساب remaining_hours
    // عرض تنبيه إذا وصلت لصفر
}

// وظيفة منع الإضافة عند النفاد
function check_remaining_hours_before_add(frm) {
    // التحقق من remaining_hours <= 0
    // حذف الصف الجديد إذا لزم الأمر
    // عرض تنبيه
}
```

### في ملف `booking.py`:

```python
def compute_package_hours_usage(self):
    """
    - حساب hours لكل صف من start_time & end_time
    - جمع used_hours
    - حساب remaining_hours
    - عرض msgprint (بدلاً من throw) عند التجاوز
    """
    if self.booking_type != 'Package':
        return
    
    # جلب total_hours من Package
    package_total = float(frappe.db.get_value('Package', self.package, 'total_hours') or 0)
    
    used = 0.0
    for row in (self.package_booking_dates or []):
        if row.start_time and row.end_time:
            # حساب الفرق بالساعات
            row.hours = calculate_time_difference(row.start_time, row.end_time)
        used += float(row.hours or 0)
    
    self.used_hours = round(used, 2)
    self.remaining_hours = max(package_total - used, 0.0)
    
    # رسالة تحذير (msgprint) بدلاً من throw
    if package_total and self.used_hours > package_total:
        frappe.msgprint(
            msg=f"⚠️ تم استنفاد جميع ساعات الباقة...",
            indicator="red"
        )
```

---

## 📝 سيناريو الاستخدام

### مثال عملي:

1. **اختيار الباقة "Startup 1"** التي تحتوي على **10 ساعات**
   - ✅ `remaining_hours = 10`
   - ✅ `used_hours = 0`

2. **إضافة تاريخ حجز أول:**
   - وقت البداية: `10:00`
   - وقت النهاية: `14:00`
   - ✅ يتم الحساب: `hours = 4`
   - ✅ `used_hours = 4`
   - ✅ `remaining_hours = 6`

3. **إضافة تاريخ حجز ثاني:**
   - وقت البداية: `15:00`
   - وقت النهاية: `21:00`
   - ✅ يتم الحساب: `hours = 6`
   - ✅ `used_hours = 10` (4 + 6)
   - ✅ `remaining_hours = 0`
   - ⚠️ يظهر تنبيه: "تم استنفاد جميع ساعات الباقة"

4. **محاولة إضافة تاريخ ثالث:**
   - ❌ يتم رفض الإضافة
   - ⚠️ يظهر تنبيه: "لا يمكن إضافة تواريخ حجز إضافية"
   - الصف الجديد يُحذف تلقائياً

---

## ✅ الحالات المعالجة

### 1. عبور منتصف الليل
```
start_time: 22:00
end_time: 02:00
Result: hours = 4 ساعات ✅
```

### 2. أوقات متطابقة
```
start_time: 10:00
end_time: 10:00
Result: hours = 0 ساعات ✅
```

### 3. عدة تواريخ حجز
```
Date 1: 3 ساعات
Date 2: 5 ساعات
Date 3: 2 ساعات
Total used_hours: 10 ساعات ✅
```

### 4. تجاوز الساعات
```
Total package hours: 10
Used hours: 12
Result: 
- remaining_hours = 0
- msgprint alert (لا يمنع الحفظ) ✅
```

---

## 🎨 واجهة المستخدم

### التنبيهات (Alerts):

1. **نجاح تحميل الباقة:**
   ```
   ✅ تم تحميل خدمات الباقة بنجاح
   (أخضر - 3 ثوان)
   ```

2. **تحذير نفاد الساعات:**
   ```
   ⚠️ تم استنفاد جميع ساعات الباقة
   (أحمر - 5 ثوان)
   ```

3. **منع الإضافة:**
   ```
   ⚠️ تم استنفاد جميع ساعات الباقة. 
   لا يمكن إضافة تواريخ حجز إضافية
   (أحمر - 7 ثوان)
   ```

---

## 🧪 الاختبار

### لاختبار الميزة:

1. افتح نموذج Booking جديد
2. اختر **Booking Type = Package**
3. اختر باقة (مثل "Startup 1")
4. تحقق من ملء `remaining_hours` تلقائياً
5. أضف تاريخ حجز في جدول **تواريخ الحجز**
6. اختر `start_time` و `end_time`
7. تحقق من حساب `hours` تلقائياً
8. أضف تواريخ أخرى حتى تصل لنفاد الساعات
9. حاول إضافة تاريخ جديد بعد النفاد
10. تحقق من ظهور التنبيه ومنع الإضافة

---

## 📊 ملخص الحقول

| الحقل | النوع | القراءة فقط | الحساب |
|------|------|------------|---------|
| `total_hours` | Float | ✅ | من Package |
| `used_hours` | Float | ✅ | مجموع hours من الجدول |
| `remaining_hours` | Float | ✅ | total - used |
| `hours` (في الجدول) | Float | ✅ | end_time - start_time |

---

## 🔄 التدفق الكامل

```
اختيار الباقة
    ↓
تعيين remaining_hours = total_hours
    ↓
إضافة تاريخ حجز
    ↓
اختيار start_time & end_time
    ↓
حساب hours تلقائياً [JavaScript]
    ↓
جمع used_hours من كل الصفوف [JavaScript]
    ↓
حساب remaining_hours [JavaScript]
    ↓
حفظ الوثيقة
    ↓
إعادة الحساب والتحقق [Python]
    ↓
msgprint إذا تجاوزت الساعات [Python]
```

---

## ⚠️ ملاحظات مهمة

1. **الحساب التلقائي يتم في JavaScript** (واجهة المستخدم)
2. **التحقق النهائي يتم في Python** (validate method)
3. **msgprint لا يمنع الحفظ** (على عكس throw)
4. **معالجة عبور منتصف الليل** تتم تلقائياً
5. **الصفوف لا يمكن إضافتها** عند `remaining_hours = 0`

---

## 🎉 الخلاصة

تم تطبيق **نظام حساب ساعات الباقة** بشكل كامل مع:
- ✅ حساب تلقائي للساعات
- ✅ جمع الساعات المستخدمة
- ✅ تحديث الساعات المتبقية
- ✅ منع الإضافة عند النفاد
- ✅ رسائل تحذير واضحة ومفيدة
- ✅ واجهة مستخدم محسنة

التطبيق جاهز للاختبار! 🚀
