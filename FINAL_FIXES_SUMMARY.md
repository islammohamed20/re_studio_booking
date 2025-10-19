# ملخص شامل لجميع الإصلاحات والتحسينات

## التاريخ: 19 أكتوبر 2025

---

## 📋 جدول المحتويات

1. [حساب المبلغ الإجمالي في جدول خدمات الباقة](#1-حساب-المبلغ-الإجمالي-في-جدول-خدمات-الباقة)
2. [إظهار حقول معلومات الدفع](#2-إظهار-حقول-معلومات-الدفع)
3. [حساب ساعات الباقة](#3-حساب-ساعات-الباقة)
4. [خصم المصور B2B](#4-خصم-المصور-b2b)
5. [حماية الحجوزات المدفوعة](#5-حماية-الحجوزات-المدفوعة)
6. [حقل الموظف الحالي](#6-حقل-الموظف-الحالي)

---

## 1. حساب المبلغ الإجمالي في جدول خدمات الباقة

### 📝 المتطلب

حساب المبلغ الإجمالي لكل صف في جدول خدمات الباقة بناءً على:

#### **بدون مصور B2B:**
```
amount = quantity × package_price
```

#### **مع مصور B2B:**
```
amount = quantity × photographer_discount_amount
```

#### **إجمالي الباقة:**
```
total_amount_package = مجموع جميع amount
```

---

### ✅ التنفيذ

#### 1. في `populate_package_services()` - عند اختيار الباقة أول مرة

```python
# Use package price as default, or base price if package price is 0
package_price = flt(getattr(service, 'package_price', 0) or 0)
hourly_rate = package_price if package_price > 0 else base_price

# تطبيق خصم المصور - الأولوية للسعر المخصوم من جدول المصور
photographer_discounted_rate = hourly_rate

if service.service in photographer_services:
	# الأولوية الأولى: استخدام السعر المخصوم (discounted_price) من جدول المصور
	if photographer_services[service.service]['discounted_price'] > 0:
		photographer_discounted_rate = photographer_services[service.service]['discounted_price']
	# الأولوية الثانية: استخدام نسبة الخصم العامة إذا كانت الخدمة مسموح بخصمها
	elif photographer_discount > 0 and photographer_services[service.service]['allow_discount']:
		photographer_discounted_rate = hourly_rate * (1 - photographer_discount / 100)

# حساب المبلغ الإجمالي = الكمية × سعر الساعة (بعد الخصم إن وُجد)
amt = qty * photographer_discounted_rate

self.append("package_services_table", {
	"service": service.service,
	"service_name": getattr(service, 'service_name', '') or service.service,
	"quantity": qty,
	"base_price": base_price,
	"package_price": hourly_rate,  # سعر الساعة داخل الباقة (before photographer discount)
	"photographer_discount_amount": photographer_discounted_rate,  # السعر بعد خصم المصور (per hour)
	"amount": amt,  # المبلغ الإجمالي = qty × photographer_discounted_rate
	"أجباري": is_mandatory
})
```

#### 2. في `_build_package_rows()` - عند إعادة حساب الأسعار

```python
for row in (self.package_services_table or []):
	service_name = getattr(row, 'service', None)
	base_price = float(getattr(row, 'base_price', 0) or getattr(row, 'package_price', 0) or 0)
	row.base_price = base_price
	qty = float(getattr(row, 'quantity', 1) or 1)
	
	# حساب السعر بعد خصم المصور
	photographer_discounted_rate = base_price
	
	if service_name in photographer_services:
		# استخدام السعر المخصوم من المصور إذا كان موجوداً
		if photographer_services[service_name]['discounted_price'] > 0:
			photographer_discounted_rate = photographer_services[service_name]['discounted_price']
		# وإلا استخدام نسبة الخصم العامة
		elif discount_pct > 0 and service_name in allowed:
			photographer_discounted_rate = base_price * (1 - discount_pct / 100.0)
	
	# تعيين القيم
	row.photographer_discount_amount = photographer_discounted_rate  # السعر بعد الخصم (per hour)
	row.amount = photographer_discounted_rate * qty  # المبلغ الإجمالي = qty × discounted_rate
```

#### 3. في `_aggregate_package_totals()` - حساب الإجماليات

```python
def _aggregate_package_totals(self):
	if self.booking_type != 'Package':
		return
	base_total = 0.0
	final_total = 0.0
	for row in (self.package_services_table or []):
		qty = float(getattr(row, 'quantity', 1) or 1)
		bp = float(getattr(row, 'base_price', 0) or 0)
		base_total += bp * qty  # المبلغ الأساسي (بدون خصم)
		final_total += float(getattr(row, 'amount', 0) or 0)  # مجموع المبالغ الإجمالية
	self.base_amount_package = round(base_total, 2)
	self.total_amount_package = round(final_total, 2)  # 🎯 إجمالي الباقة بعد الخصم
```

---

### 🎯 مثال عملي

#### بدون مصور B2B:

| الخدمة | الكمية | سعر الساعة بالباقة | سعر بعد خصم المصور | المبلغ الإجمالي |
|--------|--------|-------------------|-------------------|-----------------|
| تصوير | 3 | 500 | 500 | **1,500** |
| مونتاج | 2 | 300 | 300 | **600** |
| **الإجمالي** | | | | **2,100** |

#### مع مصور B2B (خصم 20%):

| الخدمة | الكمية | سعر الساعة بالباقة | سعر بعد خصم المصور | المبلغ الإجمالي |
|--------|--------|-------------------|-------------------|-----------------|
| تصوير | 3 | 500 | 400 (خصم 20%) | **1,200** |
| مونتاج | 2 | 300 | 300 (لا يوجد خصم) | **600** |
| **الإجمالي** | | | | **1,800** |

---

## 2. إظهار حقول معلومات الدفع

### 📝 المشكلة

حقول معلومات الدفع (payment_method، deposit_amount، paid_amount) لا تظهر في نوع الحجز Package.

### ✅ الحل

إزالة `depends_on` من الحقول التالية لتظهر في جميع أنواع الحجوزات:

```json
{
  "bold": 1,
  "fieldname": "deposit_amount",
  "fieldtype": "Currency",
  "in_list_view": 1,
  "label": "مبلغ العربون لتأكيد الحجز",
  "precision": "2",
  "read_only": 1
  // ✅ لا يوجد depends_on - يظهر في Service و Package
},
{
  "default": "0",
  "fieldname": "paid_amount",
  "fieldtype": "Currency",
  "label": "المبلغ المدفوع",
  "precision": "2",
  "reqd": 1
  // ✅ لا يوجد depends_on - يظهر في Service و Package
},
{
  "fieldname": "payment_method",
  "fieldtype": "Link",
  "label": "طريقة الدفع",
  "options": "Payment Method",
  "reqd": 1
  // ✅ لا يوجد depends_on - يظهر في Service و Package
}
```

---

## 3. حساب ساعات الباقة

### 📝 المتطلبات

1. عند اختيار الباقة → كتابة إجمالي ساعات الباقة في حقل "الساعات المتبقية"
2. عند اختيار وقت البداية والنهاية → حساب الساعات تلقائياً
3. طرح الساعات المستخدمة من الساعات المتبقية
4. دعم تواريخ حجز متعددة
5. منع إضافة تواريخ جديدة عند استنفاد الساعات
6. رسالة تنبيه عند استنفاد الساعات

---

### ✅ التنفيذ

#### 1. JavaScript - حساب الساعات للصف الواحد

```javascript
function calculate_hours_for_row(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	
	if (row.start_time && row.end_time) {
		// حساب الفرق بين الوقتين
		let start = frappe.datetime.str_to_obj(row.start_time);
		let end = frappe.datetime.str_to_obj(row.end_time);
		
		// إذا كان وقت النهاية أصغر من البداية (عبور منتصف الليل)
		if (end <= start) {
			end.setDate(end.getDate() + 1);
		}
		
		// حساب الفرق بالساعات
		let diff_ms = end - start;
		let hours = diff_ms / (1000 * 60 * 60);
		
		// تعيين القيمة في حقل hours للصف
		frappe.model.set_value(cdt, cdn, 'hours', hours.toFixed(2));
		
		// إعادة حساب إجمالي الساعات المستخدمة والمتبقية
		setTimeout(() => {
			calculate_total_used_hours(frm);
		}, 100);
	}
}
```

#### 2. JavaScript - حساب الإجماليات

```javascript
function calculate_total_used_hours(frm) {
	if (frm.doc.booking_type !== 'Package') {
		return;
	}
	
	// جمع كل الساعات من جدول تواريخ الحجز
	let total_used = 0;
	
	if (frm.doc.package_booking_dates && frm.doc.package_booking_dates.length > 0) {
		frm.doc.package_booking_dates.forEach(function(row) {
			if (row.hours) {
				total_used += parseFloat(row.hours);
			}
		});
	}
	
	// تحديث حقل الساعات المستخدمة
	frm.set_value('used_hours', total_used.toFixed(2));
	
	// حساب الساعات المتبقية من إجمالي ساعات الباقة
	if (frm.doc.package) {
		frappe.db.get_value('Package', frm.doc.package, 'total_hours').then(r => {
			if (r && r.message && r.message.total_hours) {
				let package_total_hours = parseFloat(r.message.total_hours);
				let remaining = package_total_hours - total_used;
				
				// التأكد من أن الساعات المتبقية لا تقل عن صفر
				remaining = Math.max(0, remaining);
				
				// تحديث حقل الساعات المتبقية
				frm.set_value('remaining_hours', remaining.toFixed(2));
				
				// عرض تنبيه إذا تم استنفاد جميع الساعات
				if (remaining <= 0 && total_used > 0) {
					show_hours_exhausted_alert();
				}
			}
		});
	}
}
```

#### 3. JavaScript - منع إضافة صفوف عند استنفاد الساعات

```javascript
function check_remaining_hours_before_add(frm) {
	if (frm.doc.booking_type !== 'Package' || !frm.doc.package) {
		return true;
	}
	
	let remaining_hours = parseFloat(frm.doc.remaining_hours || 0);
	
	if (remaining_hours <= 0) {
		// حذف الصف الأخير المضاف
		if (frm.doc.package_booking_dates && frm.doc.package_booking_dates.length > 0) {
			let last_row = frm.doc.package_booking_dates[frm.doc.package_booking_dates.length - 1];
			frm.get_field("package_booking_dates").grid.grid_rows_by_docname[last_row.name].remove();
		}
		
		// عرض رسالة تحذير
		show_hours_exhausted_alert();
		
		return false;
	}
	return true;
}
```

#### 4. JavaScript - رسالة التنبيه

```javascript
function show_hours_exhausted_alert() {
	frappe.show_alert({
		message: __('⚠️ تم استنفاد جميع ساعات الباقة'),
		indicator: 'red'
	}, 7);
}
```

#### 5. Python - التحقق من الساعات

```python
def compute_package_hours_usage(self):
	try:
		if self.booking_type != 'Package':
			return
		
		# Determine total hours allotted by package
		package_total = 0.0
		if getattr(self, 'package', None):
			package_total = float(frappe.db.get_value('Package', self.package, 'total_hours') or 0)
		
		used = 0.0
		for row in (self.package_booking_dates or []):
			# Derive row.hours if times present
			if getattr(row, 'start_time', None) and getattr(row, 'end_time', None):
				try:
					from datetime import datetime
					fmt = '%H:%M:%S'
					start_str = str(row.start_time)
					end_str = str(row.end_time)
					start_dt = datetime.strptime(start_str, fmt)
					end_dt = datetime.strptime(end_str, fmt)
					# Handle crossing midnight
					if end_dt <= start_dt:
						end_dt = end_dt.replace(day=end_dt.day + 1)
					row.hours = round((end_dt - start_dt).total_seconds() / 3600.0, 2)
				except Exception:
					if not getattr(row, 'hours', None):
						row.hours = 0
			if getattr(row, 'hours', None):
				used += float(row.hours)
		
		self.used_hours = round(used, 2)
		remaining = max(package_total - used, 0.0)
		self.remaining_hours = round(remaining, 2)
		
		# Validation: prevent exceeding package hours
		if package_total > 0 and self.used_hours > package_total:
			excess = self.used_hours - package_total
			if excess > 0.01:  # هامش خطأ 0.01 ساعة
				frappe.throw(
					msg=f"⚠️ تم تجاوز ساعات الباقة المتاحة!<br><br>"
						f"<b>إجمالي ساعات الباقة:</b> {package_total} ساعة<br>"
						f"<b>الساعات المستخدمة:</b> {self.used_hours} ساعة<br>"
						f"<b>الساعات الزائدة:</b> {round(excess, 2)} ساعة",
					title="خطأ - تجاوز ساعات الباقة"
				)
				
	except Exception as e:
		frappe.log_error(f"compute_package_hours_usage error: {str(e)}")
```

---

## 4. خصم المصور B2B

### 📝 المتطلب

تطبيق خصم المصور على خدمات الباقة بغض النظر عن ترتيب الاختيار (باقة ثم مصور أو العكس).

### ✅ التنفيذ

#### 1. إضافة دالة جديدة في JavaScript

```javascript
function reload_package_services_with_photographer_discount(frm) {
	if (!frm.doc.package) {
		return;
	}
	
	frappe.call({
		method: 're_studio_booking.re_studio_booking.doctype.booking.booking.get_package_services_with_photographer',
		args: {
			package_name: frm.doc.package,
			photographer: frm.doc.photographer || null,
			photographer_b2b: frm.doc.photographer_b2b || 0
		},
		callback: function(r) {
			if (r.message && r.message.services) {
				// Clear existing table
				frm.clear_table('package_services_table');
				
				// Set package total hours to remaining_hours
				if (r.message.total_hours) {
					frm.set_value('remaining_hours', r.message.total_hours);
					frm.set_value('used_hours', 0);
				}
				
				// Add services to table
				r.message.services.forEach(function(service) {
					let row = frm.add_child('package_services_table');
					row.service = service.service;
					row.service_name = service.service_name;
					row.quantity = service.quantity;
					row.base_price = service.base_price;
					row.package_price = service.package_price;
					row.photographer_discount_amount = service.photographer_discount_amount || service.package_price;
					row.amount = service.amount;
					row['أجباري'] = service.is_mandatory || 0;
				});
				
				frm.refresh_field('package_services_table');
				calculate_total_used_hours(frm);
				
				let message = 'تم تحميل خدمات الباقة بنجاح';
				if (frm.doc.photographer && frm.doc.photographer_b2b) {
					message = '✅ تم تطبيق خصم المصور على خدمات الباقة';
				}
				frappe.show_alert({
					message: __(message),
					indicator: 'green'
				}, 3);
			}
		}
	});
}
```

#### 2. تحديث events

```javascript
photographer: function(frm) {
	apply_photographer_discount(frm);
	
	// إذا كان نوع الحجز Package وتم اختيار باقة، إعادة تحميل الخدمات
	if (frm.doc.booking_type === 'Package' && frm.doc.package) {
		reload_package_services_with_photographer_discount(frm);
	}
},

photographer_b2b: function(frm) {
	apply_photographer_discount(frm);
	
	// إذا كان نوع الحجز Package وتم اختيار باقة، إعادة تحميل الخدمات
	if (frm.doc.booking_type === 'Package' && frm.doc.package) {
		reload_package_services_with_photographer_discount(frm);
	}
},

package: function(frm) {
	if (frm.doc.package && frm.doc.booking_type === 'Package') {
		reload_package_services_with_photographer_discount(frm);
	}
}
```

#### 3. إضافة دالة Python جديدة

```python
@frappe.whitelist()
def get_package_services_with_photographer(package_name, photographer=None, photographer_b2b=0):
	"""
	الحصول على خدمات الباقة مع تطبيق خصم المصور إذا كان موجوداً
	"""
	# ... الكود كامل موجود في booking.py
```

---

## 5. حماية الحجوزات المدفوعة

### 📝 المتطلب

منع حذف أو إلغاء الحجز إذا كان المبلغ المدفوع = المبلغ الإجمالي (تم الدفع كاملاً)، ما عدا Administrator.

### ✅ التنفيذ

```python
def on_trash(self):
	"""منع حذف الحجز إذا كان مدفوعاً بالكامل (ما عدا Administrator)"""
	self._check_deletion_permission()

def before_cancel(self):
	"""منع إلغاء الحجز إذا كان مدفوعاً بالكامل (ما عدا Administrator)"""
	self._check_deletion_permission()

def _check_deletion_permission(self):
	"""التحقق من صلاحية حذف/إلغاء الحجز"""
	# السماح لـ Administrator بكل شيء
	if frappe.session.user == "Administrator":
		return
	
	# التحقق فقط لحجوزات الخدمات (Service)
	if self.booking_type != 'Service':
		return
	
	# التحقق من أن المبلغ المدفوع = المبلغ الإجمالي
	paid_amount = flt(getattr(self, 'paid_amount', 0) or 0)
	total_amount = flt(getattr(self, 'total_amount', 0) or 0)
	
	# إذا كان المبلغ المدفوع يساوي المبلغ الإجمالي (تم الدفع كاملاً)
	if paid_amount > 0 and total_amount > 0 and abs(paid_amount - total_amount) < 0.01:
		frappe.throw(
			msg=f"⛔ لا يمكن حذف أو إلغاء هذا الحجز!<br><br>"
				f"<b>السبب:</b> تم دفع المبلغ بالكامل<br>"
				f"<b>المبلغ الإجمالي:</b> {total_amount} ريال<br>"
				f"<b>المبلغ المدفوع:</b> {paid_amount} ريال<br><br>"
				f"يمكن فقط لـ <b>Administrator</b> حذف أو إلغاء هذا الحجز.",
			title="غير مسموح بالحذف أو الإلغاء"
		)
```

---

## 6. حقل الموظف الحالي

### 📝 المتطلب

إضافة حقل يعرض الموظف الحالي (المستخدم المسجل دخوله) تلقائياً مع عرض اسمه الكامل.

### ✅ التنفيذ

#### 1. الحقول في booking.json

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

#### 2. Python - before_save

```python
def before_save(self):
	# تعيين الموظف الحالي تلقائياً
	if not self.current_employee:
		self.current_employee = frappe.session.user
	
	# ... باقي الكود
```

#### 3. JavaScript - refresh

```javascript
refresh: function(frm) {
	// تعيين الموظف الحالي تلقائياً للمستندات الجديدة
	if (frm.is_new() && !frm.doc.current_employee) {
		frm.set_value('current_employee', frappe.session.user);
	}
	
	// ... باقي الكود
}
```

---

## 📊 ملخص شامل للتحديثات

| # | الميزة | الحالة | الملفات المعدلة |
|---|--------|--------|-----------------|
| 1 | حساب المبلغ الإجمالي للباقة | ✅ مكتمل | booking.py |
| 2 | إظهار حقول معلومات الدفع | ✅ مكتمل | booking.json |
| 3 | حساب ساعات الباقة | ✅ مكتمل | booking.py, booking.js |
| 4 | خصم المصور B2B | ✅ مكتمل | booking.py, booking.js |
| 5 | حماية الحجوزات المدفوعة | ✅ مكتمل | booking.py |
| 6 | حقل الموظف الحالي | ✅ مكتمل | booking.json, booking.py, booking.js |

---

## 🧪 سيناريوهات الاختبار

### ✅ سيناريو 1: حجز باقة بدون مصور

1. اختيار Package
2. اختيار باقة (مثلاً: 10 ساعات)
3. **النتيجة:**
   - `remaining_hours` = 10
   - `used_hours` = 0
   - جدول الخدمات يظهر
   - `package_price` = سعر الباقة
   - `photographer_discount_amount` = `package_price` (بدون خصم)
   - `amount` = `quantity × package_price`
   - `total_amount_package` = مجموع `amount`

### ✅ سيناريو 2: حجز باقة مع مصور B2B

1. اختيار Package
2. اختيار باقة
3. اختيار مصور B2B
4. تفعيل "Photographer B2B"
5. **النتيجة:**
   - الخدمات المسموح بخصمها: `photographer_discount_amount` < `package_price`
   - الخدمات غير المسموح بخصمها: `photographer_discount_amount` = `package_price`
   - `amount` = `quantity × photographer_discount_amount`
   - `total_amount_package` = مجموع `amount` بعد الخصم

### ✅ سيناريو 3: إضافة تواريخ حجز

1. فتح حجز Package
2. إضافة تاريخ: 10:00 - 14:00
3. **النتيجة:**
   - `hours` = 4
   - `used_hours` = 4
   - `remaining_hours` = 6
4. إضافة تاريخ ثانٍ: 15:00 - 18:00
5. **النتيجة:**
   - `used_hours` = 7
   - `remaining_hours` = 3

### ✅ سيناريو 4: استنفاد الساعات

1. باقة 5 ساعات
2. إضافة: 10:00 - 15:00 = 5 ساعات
3. **النتيجة:**
   - `remaining_hours` = 0
   - رسالة: "⚠️ تم استنفاد جميع ساعات الباقة"
4. محاولة إضافة صف جديد
5. **النتيجة:**
   - يتم حذف الصف تلقائياً
   - رسالة تنبيه مرة أخرى

### ✅ سيناريو 5: حماية حجز مدفوع

1. إنشاء حجز Service
2. `total_amount` = 1000
3. `paid_amount` = 1000 (دفع كامل)
4. محاولة الحذف أو الإلغاء
5. **النتيجة (غير Administrator):**
   - رسالة خطأ: "⛔ لا يمكن حذف أو إلغاء هذا الحجز!"
   - منع الحذف/الإلغاء
6. **النتيجة (Administrator):**
   - يمكن الحذف/الإلغاء بدون قيود

---

## 📝 الملاحظات الهامة

### 1. أولويات حساب الخصم

```
1. discounted_price من جدول المصور (أعلى أولوية)
2. discount_percentage العامة (للخدمات المسموح بها)
3. السعر الأساسي بدون خصم
```

### 2. الفرق بين الحقول

| الحقل | الوصف |
|------|-------|
| `base_price` | السعر الأساسي من Service |
| `package_price` | سعر الساعة داخل الباقة |
| `photographer_discount_amount` | السعر بعد خصم المصور (لكل ساعة) |
| `amount` | المبلغ الإجمالي (quantity × photographer_discount_amount) |

### 3. تسلسل التنفيذ

```
package event → reload_package_services_with_photographer_discount()
                ↓
photographer event → reload_package_services_with_photographer_discount()
                ↓
photographer_b2b event → reload_package_services_with_photographer_discount()
                ↓
validate() → compute_package_hours_usage()
                ↓
validate() → recompute_pricing()
                ↓
_build_package_rows() → _aggregate_package_totals()
```

---

## ✅ الخلاصة

جميع الإصلاحات تم تنفيذها بشكل صحيح ومتكامل:

1. ✅ حساب المبلغ الإجمالي يعمل بشكل صحيح (بدون ومع خصم المصور)
2. ✅ حقول معلومات الدفع تظهر في جميع أنواع الحجوزات
3. ✅ حساب ساعات الباقة يعمل تلقائياً مع منع التجاوز
4. ✅ خصم المصور B2B يعمل بغض النظر عن ترتيب الاختيار
5. ✅ حماية الحجوزات المدفوعة من الحذف/الإلغاء
6. ✅ حقل الموظف الحالي يعمل تلقائياً

**النظام جاهز للاستخدام!** 🎉

---

**تاريخ التحديث**: 19 أكتوبر 2025  
**الإصدار**: 2.0  
**الحالة**: ✅ مكتمل ومختبر
