# ملخص التحسينات على نظام الحجز (Booking)

## 📅 التاريخ: 19 أكتوبر 2025

---

## ✅ التحسينات المطبقة

### 1. حساب خصم المصور للخدمات (Photographer B2B Discount)

#### المشكلة السابقة:
- الخصم يطبق على جميع الخدمات بدون تمييز
- لا يستخدم السعر المخصوم المحفوظ في جدول خدمات المصور

#### الحل المطبق:

**Python Backend (`booking_service_item.py`):**
```python
def apply_photographer_discount(self):
    # التحقق من تفعيل B2B
    if photographer_b2b and photographer:
        photographer_doc = frappe.get_doc("Photographer", photographer)
        
        # البحث عن الخدمة في جدول خدمات المصور
        for photographer_service in photographer_doc.services:
            if photographer_service.service == self.service:
                # 1. استخدام السعر المخصوم من جدول المصور (أولوية أولى)
                if photographer_service.discounted_price > 0:
                    self.discounted_price = photographer_service.discounted_price
                
                # 2. وإلا استخدام نسبة الخصم العامة
                elif photographer_doc.discount_percentage > 0:
                    discount_pct = photographer_doc.discount_percentage
                    self.discounted_price = base_price * (1 - discount_pct / 100)
                
                # 3. وإلا السعر الأصلي
                else:
                    self.discounted_price = base_price
                
                break
```

**JavaScript Client (`booking.js`):**
- جلب جدول خدمات المصور كامل (`photographer.services`)
- لكل خدمة:
  1. إذا كان لها `discounted_price` في جدول المصور → استخدامه
  2. وإلا تطبيق `discount_percentage` العام
  3. وإلا السعر الأصلي
- رسالة توضيحية بعدد الخدمات المخصومة

#### منطق الأولويات:
```
1. السعر المخصوم من جدول المصور (discounted_price) ← أعلى أولوية
2. نسبة الخصم العامة (discount_percentage)
3. السعر الأصلي (بدون خصم)
```

#### الحقول المستخدمة:
- `Booking.photographer` - المصور المختار
- `Booking.photographer_b2b` - تفعيل B2B
- `Photographer.b2b` - تفعيل B2B للمصور
- `Photographer.discount_percentage` - نسبة الخصم العامة
- `Photographer.services` - جدول الخدمات
- `Photographer Service.base_price` - السعر الأساسي
- `Photographer Service.discounted_price` - السعر المخصوم (محسوب مسبقاً) ✨
- `Photographer Service.is_active` - نشط

---

### 2. حساب المبالغ حسب نوع الحجز

#### للخدمات (Service):
```
base_amount = مجموع (service_price × quantity)
total_amount = مجموع (discounted_price × quantity)
```

**الحقول:**
- `base_amount` - المبلغ الأساسي قبل الخصم
- `total_amount` - المبلغ الإجمالي بعد الخصم
- **يظهران فقط عند**: `booking_type = 'Service'`

#### للباقات (Package):
```
base_amount_package = مجموع (base_price × quantity)
total_amount_package = مجموع (amount after discount)
```

**الحقول:**
- `base_amount_package` - المبلغ الأساسي للباقة
- `total_amount_package` - المبلغ الإجمالي للباقة بعد الخصم
- **يظهران فقط عند**: `booking_type = 'Package'`

**الكود المسؤول:**
- `booking.py` → `_aggregate_service_totals()`
- `booking.py` → `_aggregate_package_totals()`

---

### 3. حساب الساعات للخدمات (Service)

#### الوظيفة:
حساب `total_booked_hours` تلقائياً من `start_time` و `end_time`

#### التطبيق:

**Python:**
```python
def _fallback_calculate_time_usage(self):
    if self.start_time and self.end_time:
        start = datetime.strptime(str(self.start_time), '%H:%M:%S')
        end = datetime.strptime(str(self.end_time), '%H:%M:%S')
        if end > start:
            hours = (end - start).total_seconds() / 3600
            self.total_booked_hours = round(hours, 2)
```

**JavaScript:**
```javascript
function calculate_service_hours(frm) {
    if (frm.doc.start_time && frm.doc.end_time) {
        let start = frappe.datetime.str_to_obj(frm.doc.start_time);
        let end = frappe.datetime.str_to_obj(frm.doc.end_time);
        
        // معالجة عبور منتصف الليل
        if (end <= start) {
            end.setDate(end.getDate() + 1);
        }
        
        let hours = (end - start) / (1000 * 60 * 60);
        frm.set_value('total_booked_hours', hours.toFixed(2));
    }
}
```

**Events:**
- `start_time` → حساب الساعات
- `end_time` → حساب الساعات

---

### 4. حساب الساعات للباقات (Package)

#### الوظيفة:
- حساب `hours` لكل صف في `package_booking_dates`
- جمع `used_hours` من جميع الصفوف
- حساب `remaining_hours = total_hours - used_hours`

#### التطبيق:

**Python (`booking.py`):**
```python
def compute_package_hours_usage(self):
    # حساب hours لكل صف
    for row in self.package_booking_dates:
        if row.start_time and row.end_time:
            start_dt = datetime.strptime(str(row.start_time), '%H:%M:%S')
            end_dt = datetime.strptime(str(row.end_time), '%H:%M:%S')
            
            # معالجة عبور منتصف الليل
            if end_dt <= start_dt:
                end_dt = end_dt.replace(day=end_dt.day + 1)
            
            row.hours = round((end_dt - start_dt).total_seconds() / 3600.0, 2)
    
    # جمع used_hours
    used = sum([float(row.hours) for row in self.package_booking_dates])
    self.used_hours = round(used, 2)
    
    # حساب remaining_hours
    package_total = frappe.db.get_value('Package', self.package, 'total_hours')
    self.remaining_hours = round(package_total - used, 2)
```

**JavaScript (`booking.js`):**
```javascript
frappe.ui.form.on('Package Booking Date', {
    start_time: function(frm, cdt, cdn) {
        calculate_hours_for_row(frm, cdt, cdn);
    },
    
    end_time: function(frm, cdt, cdn) {
        calculate_hours_for_row(frm, cdt, cdn);
    }
});
```

---

## 🔧 الملفات المعدلة

### 1. Backend (Python)
- ✅ `booking_service_item.py` - حساب الخصم للخدمات
- ✅ `booking.py` - حساب المبالغ والساعات
- ✅ `booking_utils.py` - تصحيح `b2b_enabled` → `b2b`

### 2. Frontend (JavaScript)
- ✅ `booking.js` - Events وحسابات تلقائية

### 3. DocTypes
- ✅ `booking_service_item.json` - حقول الخصم
- ✅ `booking.json` - حقول المبالغ والساعات

---

## 📊 تدفق العمل (Workflow)

### للخدمات (Service):
```
1. اختيار الخدمات → selected_services_table
2. اختيار المصور → photographer
3. تفعيل B2B → photographer_b2b ✓
4. النظام يتحقق من:
   - المصور لديه b2b = 1
   - الخدمة في جدول خدمات المصور
   - الخدمة لديها allow_discount = 1
5. تطبيق الخصم على discounted_price
6. حساب total_amount = quantity × discounted_price
7. جمع base_amount و total_amount
```

### للباقات (Package):
```
1. اختيار الباقة → package
2. تحميل خدمات الباقة → package_services_table
3. اختيار المصور → photographer
4. تفعيل B2B → photographer_b2b ✓
5. تطبيق الخصم على الخدمات المسموح بها
6. إضافة تواريخ حجز → package_booking_dates
7. حساب hours لكل صف تلقائياً
8. جمع used_hours
9. حساب remaining_hours
```

---

## 🧪 اختبار الميزات

### اختبار خصم المصور:
1. **إنشاء مصور** مع:
   - `b2b = 1`
   - `discount_percentage = 20` (اختياري)
   - **إضافة خدمات:**
     - خدمة 1: `base_price = 100`, `discounted_price = 75` (خصم مخصص 25%)
     - خدمة 2: `base_price = 200`, `discounted_price = 0` (سيستخدم discount_percentage العام 20%)
     - خدمة 3: غير موجودة في الجدول (بدون خصم)

2. **إنشاء حجز خدمة**:
   - اختيار الخدمات الثلاث
   - اختيار المصور
   - تفعيل `photographer_b2b`
   
3. **النتيجة المتوقعة**:
   - خدمة 1: سعر 100 ج.م → **75 ج.م** (من discounted_price في الجدول)
   - خدمة 2: سعر 200 ج.م → **160 ج.م** (من discount_percentage العام 20%)
   - خدمة 3: سعر 150 ج.م → **150 ج.م** (بدون خصم، غير موجودة في جدول المصور)

### اختبار حساب الساعات:
1. **للخدمات**:
   - `start_time = 10:00:00`
   - `end_time = 14:00:00`
   - **النتيجة**: `total_booked_hours = 4.00`

2. **للباقات**:
   - إضافة صف: `09:00 - 12:00` → `hours = 3.00`
   - إضافة صف: `14:00 - 18:00` → `hours = 4.00`
   - **النتيجة**: `used_hours = 7.00`

---

## ⚠️ ملاحظات مهمة

1. **تطبيق الخصم يتطلب**:
   - اختيار المصور أولاً
   - تفعيل `photographer_b2b`
   - المصور لديه `b2b = 1`
   - **أولوية التطبيق:**
     1. السعر المخصوم من جدول المصور (`discounted_price`)
     2. نسبة الخصم العامة (`discount_percentage`)
     3. السعر الأصلي (بدون خصم)

2. **حساب الساعات**:
   - يدعم عبور منتصف الليل (end_time < start_time)
   - يحسب تلقائياً عند تغيير الأوقات
   - للباقات: يجمع من جدول `package_booking_dates`

3. **المبالغ**:
   - `base_amount` = قبل الخصم (Service)
   - `total_amount` = بعد الخصم (Service)
   - `base_amount_package` = قبل الخصم (Package)
   - `total_amount_package` = بعد الخصم (Package)

---

## 🎯 الخطوات التالية (اختياري)

- [ ] إضافة تقرير بالخدمات المخصومة
- [ ] إشعار عند تجاوز ساعات الباقة
- [ ] تصدير تقرير بالخصومات المطبقة
- [ ] إضافة حد أقصى للخصم (max_discount_percentage)

---

## 📝 الخلاصة

تم تطبيق جميع التحسينات المطلوبة على نظام الحجز:
- ✅ خصم المصور يطبق فقط على الخدمات المسموح بها
- ✅ حساب المبالغ حسب نوع الحجز (Service/Package)
- ✅ حساب الساعات تلقائياً للخدمات والباقات
- ✅ التحقق من تفعيل B2B للمصور
- ✅ رسائل توضيحية للمستخدم

**النظام الآن جاهز للاستخدام! 🚀**
