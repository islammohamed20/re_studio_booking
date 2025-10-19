# إضافة حقل الموظف الحالي (Current Employee Field)

## التاريخ: 19 أكتوبر 2025

## الهدف من التحديث

إضافة حقل جديد لعرض **الموظف الحالي** (المستخدم المسجل دخوله) تلقائياً في مستند Booking، مع عرض **الاسم الكامل** للموظف.

---

## الحقول المضافة

### 1. حقل الموظف (current_employee)
- **الاسم**: `current_employee`
- **النوع**: Link (User)
- **العنوان**: "الموظف"
- **القيمة الافتراضية**: `__user` (المستخدم الحالي)
- **للقراءة فقط**: نعم (read_only: 1)

### 2. حقل اسم الموظف الكامل (current_employee_full_name)
- **الاسم**: `current_employee_full_name`
- **النوع**: Data
- **العنوان**: "اسم الموظف الكامل"
- **مصدر البيانات**: يتم جلبه تلقائياً من `current_employee.full_name`
- **يظهر في القائمة**: نعم (in_list_view: 1)
- **للقراءة فقط**: نعم (read_only: 1)

---

## آلية العمل

### في Frontend (JavaScript)

```javascript
// في حدث refresh
if (frm.is_new() && !frm.doc.current_employee) {
	frm.set_value('current_employee', frappe.session.user);
}
```

**الوظيفة:**
- عند إنشاء حجز جديد، يتم تعيين `current_employee` تلقائياً إلى المستخدم الحالي
- يتم استخدام `frappe.session.user` للحصول على معرف المستخدم الحالي

### في Backend (Python)

```python
def before_save(self):
	"""تنفيذ العمليات قبل الحفظ"""
	# 0. تعيين الموظف الحالي تلقائياً
	if not self.current_employee:
		self.current_employee = frappe.session.user
	
	# ... باقي الكود
```

**الوظيفة:**
- قبل حفظ المستند، يتم التحقق من وجود قيمة في `current_employee`
- إذا لم يكن موجوداً، يتم تعيينه تلقائياً إلى `frappe.session.user`
- هذا يضمن حفظ الموظف حتى لو تم الحفظ من الـ API أو Script

---

## موقع الحقول في النموذج

الحقول تظهر في قسم **"نوع الحجز"** (booking_type_section):

```
نوع الحجز (booking_type_section)
├── نوع الحجز (booking_type)
├── المصور (photographer)
├── Photographer B2B (photographer_b2b)
├── [Column Break]
├── ⭐ الموظف (current_employee) [جديد]
├── ⭐ اسم الموظف الكامل (current_employee_full_name) [جديد]
└── موظف (agent) - حقل قديم
```

---

## الفرق بين الحقلين

### 🆕 current_employee (الموظف الحالي)
- **تلقائي**: يتم تعيينه تلقائياً للمستخدم الحالي
- **للقراءة فقط**: لا يمكن تعديله
- **الغرض**: تتبع من قام بإنشاء الحجز فعلياً
- **يعرض**: Full Name من User

### 🔵 agent (موظف)
- **يدوي**: يمكن اختياره يدوياً
- **قابل للتعديل**: يمكن تغييره
- **الغرض**: تعيين موظف مسؤول عن الحجز (قد يكون مختلف عن المنشئ)
- **يعرض**: User ID

---

## تحديثات الملفات

### 1. booking.json
**التغييرات:**

#### أ) field_order (إضافة الحقول للترتيب)
```json
"field_order": [
  ...
  "booking_type",
  "photographer",
  "photographer_b2b",
  "column_break_zteg",
  "current_employee",              // ⭐ جديد
  "current_employee_full_name",    // ⭐ جديد
  "agent",
  ...
]
```

#### ب) fields (تعريف الحقول)
```json
{
  "default": "__user",
  "fieldname": "current_employee",
  "fieldtype": "Link",
  "label": "الموظف",
  "options": "User",
  "read_only": 1
},
{
  "fetch_from": "current_employee.full_name",
  "fieldname": "current_employee_full_name",
  "fieldtype": "Data",
  "in_list_view": 1,
  "label": "اسم الموظف الكامل",
  "read_only": 1
}
```

### 2. booking.py
**التغيير:**

```python
def before_save(self):
	"""تنفيذ العمليات قبل الحفظ"""
	# 0. تعيين الموظف الحالي تلقائياً
	if not self.current_employee:
		self.current_employee = frappe.session.user
	
	# 1. تغيير الحالة إلى Confirmed عند الحفظ
	if self.status != 'Confirmed':
		self.status = 'Confirmed'
	
	# ... باقي الكود
```

### 3. booking.js
**التغيير:**

```javascript
refresh: function(frm) {
	// Set default booking type if not set
	if (!frm.doc.booking_type) {
		frm.set_value('booking_type', 'Service');
	}
	
	// تعيين الموظف الحالي تلقائياً للمستندات الجديدة
	if (frm.is_new() && !frm.doc.current_employee) {
		frm.set_value('current_employee', frappe.session.user);
	}
	
	// ... باقي الكود
}
```

---

## خطوات التطبيق

### 1. تحديث ملف JSON
✅ إضافة `current_employee` و `current_employee_full_name` إلى `field_order`  
✅ إضافة تعريفات الحقول في قسم `fields`

### 2. تحديث ملف Python
✅ إضافة منطق تعيين `current_employee` في `before_save()`

### 3. تحديث ملف JavaScript
✅ إضافة منطق تعيين `current_employee` في `refresh` event

### 4. تطبيق التغييرات على قاعدة البيانات
```bash
bench --site site1.local migrate
```
✅ **تم التنفيذ بنجاح**

### 5. إعادة تشغيل النظام
```bash
bench restart
```
✅ **تم التنفيذ بنجاح**

---

## سيناريوهات الاختبار

### ✅ سيناريو 1: إنشاء حجز جديد
1. تسجيل الدخول كمستخدم (مثلاً: user@example.com)
2. إنشاء حجز جديد
3. **النتيجة المتوقعة**:
   - حقل "الموظف" = user@example.com
   - حقل "اسم الموظف الكامل" = "محمد أحمد" (Full Name من User)

### ✅ سيناريو 2: حفظ حجز موجود
1. فتح حجز موجود
2. تعديل بعض البيانات
3. حفظ
4. **النتيجة المتوقعة**:
   - حقل "الموظف" يبقى كما هو (المستخدم الذي أنشأ الحجز أصلاً)
   - لا يتغير إلى المستخدم الحالي

### ✅ سيناريو 3: عرض في القائمة
1. الذهاب إلى قائمة Bookings
2. **النتيجة المتوقعة**:
   - عمود "اسم الموظف الكامل" يظهر في القائمة
   - يعرض الاسم الكامل لكل موظف

### ✅ سيناريو 4: الحقل للقراءة فقط
1. فتح حجز جديد أو موجود
2. محاولة تعديل حقل "الموظف" أو "اسم الموظف الكامل"
3. **النتيجة المتوقعة**:
   - الحقلان غير قابلين للتعديل (read-only)
   - اللون رمادي فاتح

---

## الفوائد

### 1. التتبع التلقائي ✅
- معرفة من قام بإنشاء الحجز بدون الحاجة للبحث في السجلات
- عرض الاسم الكامل بدلاً من User ID

### 2. التمييز بين المنشئ والمسؤول ✅
- `current_employee`: من أنشأ الحجز فعلياً
- `agent`: من هو المسؤول عن متابعة الحجز (قد يكون شخص آخر)

### 3. التقارير والإحصائيات ✅
- إمكانية عمل تقارير حسب الموظف
- معرفة عدد الحجوزات لكل موظف
- تتبع الأداء

### 4. الأمان ✅
- الحقل للقراءة فقط، لا يمكن التلاعب به
- يتم التعيين تلقائياً من `frappe.session.user`

---

## ملاحظات مهمة

### ⚠️ الفرق بين `__user` و `frappe.session.user`

- **`__user`**: قيمة افتراضية في JSON، تعمل في Frontend فقط
- **`frappe.session.user`**: يعمل في Frontend و Backend
- **الحل**: استخدمنا كلاهما لضمان العمل في جميع الحالات

### ⚠️ fetch_from vs set_value

- **`fetch_from`**: يتم جلب القيمة تلقائياً من DocType آخر
- في حالتنا: `current_employee_full_name` يتم جلبه من `current_employee.full_name`
- لا حاجة لكود إضافي، Frappe يتعامل معه تلقائياً

### ⚠️ read_only vs disabled

- **`read_only: 1`**: الحقل يظهر بلون رمادي فاتح، لا يمكن تعديله
- **`disabled: 1`**: الحقل معطل بالكامل
- استخدمنا `read_only` لأنه أكثر وضوحاً للمستخدم

---

## الملخص

✅ **تم إضافة حقلين جديدين:**
1. **الموظف** (current_employee) - Link إلى User
2. **اسم الموظف الكامل** (current_employee_full_name) - اسم كامل

✅ **يتم التعيين تلقائياً:**
- عند إنشاء حجز جديد
- يتم حفظ المستخدم الحالي
- عرض الاسم الكامل

✅ **للقراءة فقط:**
- لا يمكن التعديل
- ضمان صحة البيانات

✅ **يظهر في القائمة:**
- سهولة التتبع
- معرفة من أنشأ كل حجز

---

**تاريخ التحديث**: 19 أكتوبر 2025  
**الحالة**: ✅ مكتمل ومطبق  
**الإصدار**: 1.0
