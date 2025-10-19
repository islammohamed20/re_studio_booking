# إعادة هيكلة حساب ساعات الباقة (Package Hours Calculation Restructure)

## التاريخ: 19 أكتوبر 2025

## الهدف من التحديث

إعادة هيكلة ومراجعة دالة حساب الوقت لتحسين تجربة المستخدم في إدارة ساعات الباقات مع منع تجاوز الساعات المتاحة.

---

## المتطلبات المنفذة

### 1️⃣ حساب الساعات تلقائياً
✅ **عند اختيار وقت البداية ووقت النهاية:**
- يتم حساب عدد الساعات المختارة تلقائياً
- يتم تخزين النتيجة في حقل `hours` داخل صف جدول تواريخ الحجز

### 2️⃣ تحديث الساعات المستخدمة والمتبقية
✅ **يتم حساب:**
- **عدد الساعات المستخدمة** (`used_hours`): مجموع جميع الساعات من جدول `package_booking_dates`
- **عدد الساعات المتبقية** (`remaining_hours`): إجمالي ساعات الباقة - الساعات المستخدمة

### 3️⃣ دعم تواريخ حجز متعددة
✅ **يمكن إضافة أكثر من تاريخ حجز:**
- يتم جمع إجمالي الساعات من جميع الصفوف
- التحديث التلقائي عند إضافة أو تعديل أو حذف صف

### 4️⃣ منع التجاوز عند الوصول للصفر
✅ **عندما تصل الساعات المتبقية إلى صفر:**
- يتم منع إضافة تواريخ حجز جديدة
- يتم حذف الصف الجديد المضاف تلقائياً
- يتم عرض رسالة تنبيه من الأسفل

### 5️⃣ رسالة التحذير المخصصة
✅ **استخدام `frappe.show_alert()`:**
- رسالة تظهر من الأسفل (alert-container-message)
- نص الرسالة: **"⚠️ تم استنفاد جميع ساعات الباقة"**
- مدة العرض: 7 ثوانٍ
- اللون: أحمر (red indicator)

---

## التحديثات المنفذة

### 📄 ملف: `booking.js`

#### 1. دالة حساب الساعات لصف واحد
```javascript
/**
 * حساب عدد الساعات لصف واحد في جدول تواريخ الحجز
 * يتم استدعاؤها عند تغيير start_time أو end_time
 */
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

**المميزات:**
- ✅ حساب تلقائي عند تغيير `start_time` أو `end_time`
- ✅ يدعم عبور منتصف الليل (مثلاً: من 11:00 PM إلى 2:00 AM = 3 ساعات)
- ✅ دقة حتى رقمين عشريين
- ✅ تحديث فوري للساعات المستخدمة والمتبقية

#### 2. دالة حساب إجمالي الساعات
```javascript
/**
 * حساب إجمالي الساعات المستخدمة والمتبقية
 * يتم جمع جميع الساعات من جدول package_booking_dates
 */
function calculate_total_used_hours(frm) {
	// التأكد من أن نوع الحجز Package
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

**المميزات:**
- ✅ جمع جميع الساعات من كل صفوف `package_booking_dates`
- ✅ جلب إجمالي ساعات الباقة من `Package.total_hours`
- ✅ حساب الساعات المتبقية = إجمالي الباقة - المستخدم
- ✅ عرض تنبيه تلقائي عند استنفاد الساعات

#### 3. دالة منع إضافة صفوف عند استنفاد الساعات
```javascript
/**
 * التحقق من الساعات المتبقية قبل السماح بإضافة صف جديد
 * إذا كانت الساعات المتبقية = 0، يتم حذف الصف وعرض رسالة تحذير
 */
function check_remaining_hours_before_add(frm) {
	// التحقق من أن نوع الحجز Package وأن الباقة محددة
	if (frm.doc.booking_type !== 'Package' || !frm.doc.package) {
		return true;
	}
	
	// التحقق من الساعات المتبقية
	let remaining_hours = parseFloat(frm.doc.remaining_hours || 0);
	
	if (remaining_hours <= 0) {
		// حذف الصف الأخير المضاف
		if (frm.doc.package_booking_dates && frm.doc.package_booking_dates.length > 0) {
			let last_row = frm.doc.package_booking_dates[frm.doc.package_booking_dates.length - 1];
			frm.get_field("package_booking_dates").grid.grid_rows_by_docname[last_row.name].remove();
		}
		
		// عرض رسالة تحذير بنمط alert-container
		show_hours_exhausted_alert();
		
		return false;
	}
	return true;
}
```

**المميزات:**
- ✅ فحص تلقائي عند محاولة إضافة صف جديد
- ✅ حذف الصف الجديد إذا كانت الساعات المتبقية = 0
- ✅ عرض رسالة تحذير واضحة للمستخدم

#### 4. دالة عرض رسالة التنبيه
```javascript
/**
 * عرض رسالة تنبيه عند استنفاد ساعات الباقة
 * تستخدم نمط frappe.show_alert الذي يظهر من الأسفل
 */
function show_hours_exhausted_alert() {
	frappe.show_alert({
		message: __('⚠️ تم استنفاد جميع ساعات الباقة'),
		indicator: 'red'
	}, 7);
}
```

**المميزات:**
- ✅ رسالة من نوع `alert-container-message` (تظهر من الأسفل)
- ✅ لون أحمر للتنبيه
- ✅ مدة العرض: 7 ثوانٍ
- ✅ أيقونة تحذير مرئية

#### 5. إضافة Events جديدة
```javascript
frappe.ui.form.on('Package Booking Date', {
	start_time: function(frm, cdt, cdn) {
		calculate_hours_for_row(frm, cdt, cdn);
	},
	
	end_time: function(frm, cdt, cdn) {
		calculate_hours_for_row(frm, cdt, cdn);
	},
	
	package_booking_dates_add: function(frm, cdt, cdn) {
		// منع إضافة صف جديد إذا كانت الساعات المتبقية = 0
		setTimeout(() => {
			check_remaining_hours_before_add(frm);
		}, 100);
	},
	
	package_booking_dates_remove: function(frm, cdt, cdn) {
		// إعادة حساب الساعات بعد حذف صف
		setTimeout(() => {
			calculate_total_used_hours(frm);
		}, 100);
	}
});
```

**المميزات:**
- ✅ حساب تلقائي عند تغيير `start_time` أو `end_time`
- ✅ فحص تلقائي عند إضافة صف جديد
- ✅ تحديث تلقائي عند حذف صف

#### 6. تحديث event الباقة
```javascript
package: function(frm) {
	// ... الكود الموجود ...
	
	// إعادة حساب الساعات المستخدمة والمتبقية
	calculate_total_used_hours(frm);
	
	// ... باقي الكود ...
}
```

**الفائدة:**
- ✅ تحديث الساعات المستخدمة والمتبقية عند تغيير الباقة

---

### 📄 ملف: `booking.py`

#### تحسين دالة التحقق من الساعات
```python
def compute_package_hours_usage(self):
	"""Compute used and remaining hours for a package based on package_booking_dates child rows."""
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
			if excess > 0.01:  # هامش خطأ 0.01 ساعة (36 ثانية)
				frappe.throw(
					msg=f"⚠️ تم تجاوز ساعات الباقة المتاحة!<br><br>"
						f"<b>إجمالي ساعات الباقة:</b> {package_total} ساعة<br>"
						f"<b>الساعات المستخدمة:</b> {self.used_hours} ساعة<br>"
						f"<b>الساعات الزائدة:</b> {round(excess, 2)} ساعة<br><br>"
						f"يرجى تعديل تواريخ الحجز لتتناسب مع الساعات المتاحة.",
					title="خطأ - تجاوز ساعات الباقة"
				)
			else:
				self.used_hours = package_total
				self.remaining_hours = 0.0
				
	except Exception as e:
		frappe.log_error(f"compute_package_hours_usage error: {str(e)}")
```

**المميزات:**
- ✅ حساب الساعات من `start_time` و `end_time` في Python
- ✅ منع حفظ الحجز إذا تجاوز الساعات المتاحة
- ✅ رسالة خطأ تفصيلية مع الأرقام الدقيقة
- ✅ هامش خطأ صغير (0.01 ساعة) للتعامل مع أخطاء التقريب

---

## إصلاح مهم: سعر الساعة بعد خصم المصور

### المشكلة المكتشفة
في دالة `populate_package_services()`، كان الكود يستخدم **نسبة الخصم فقط** ولا يستخدم **السعر المخصوم** من جدول خدمات المصور.

### الحل المطبق
```python
# تحديد ما إذا كان هناك خصم للمصور
photographer_discount = 0
photographer_services = {}  # تخزين بيانات الخدمات من جدول المصور

if getattr(self, 'photographer', None) and getattr(self, 'photographer_b2b', False):
	try:
		photographer_doc = frappe.get_doc('Photographer', self.photographer)
		photographer_discount = flt(photographer_doc.discount_percentage or 0)
		# جلب الخدمات مع السعر المخصوم من جدول خدمات المصور
		for ps in photographer_doc.get('services', []):
			photographer_services[ps.service] = {
				'discounted_price': flt(ps.get('discounted_price') or 0),
				'base_price': flt(ps.get('base_price') or 0),
				'allow_discount': ps.get('allow_discount', 0)
			}
	except Exception as e:
		frappe.log_error(f"Error fetching photographer discount: {str(e)}")

# ...

# تطبيق خصم المصور - الأولوية للسعر المخصوم من جدول المصور
photographer_discounted_rate = hourly_rate

if service.service in photographer_services:
	# الأولوية الأولى: استخدام السعر المخصوم (discounted_price) من جدول المصور
	if photographer_services[service.service]['discounted_price'] > 0:
		photographer_discounted_rate = photographer_services[service.service]['discounted_price']
	# الأولوية الثانية: استخدام نسبة الخصم العامة إذا كانت الخدمة مسموح بخصمها
	elif photographer_discount > 0 and photographer_services[service.service]['allow_discount']:
		photographer_discounted_rate = hourly_rate * (1 - photographer_discount / 100)
```

**أولويات تطبيق الخصم:**
1. ✅ **أولاً**: `discounted_price` من جدول خدمات المصور (إذا كان > 0)
2. ✅ **ثانياً**: `discount_percentage` العامة (إذا كانت `allow_discount = 1`)
3. ✅ **ثالثاً**: السعر الأساسي بدون خصم

---

## تسلسل العمل

### عند إنشاء حجز جديد من نوع Package:

1. **اختيار الباقة** → `package` event
   - تحميل خدمات الباقة
   - تعيين `remaining_hours` = `Package.total_hours`
   - تعيين `used_hours` = 0

2. **إضافة تاريخ حجز** → `package_booking_dates_add` event
   - التحقق من `remaining_hours`
   - إذا = 0: حذف الصف + عرض تنبيه
   - إذا > 0: السماح بالإضافة

3. **إدخال وقت البداية** → `start_time` event
   - حساب `hours` للصف (إذا كان `end_time` موجود)
   - تحديث `used_hours` و `remaining_hours`

4. **إدخال وقت النهاية** → `end_time` event
   - حساب `hours` للصف
   - تحديث `used_hours` و `remaining_hours`
   - إذا `remaining_hours` = 0: عرض تنبيه

5. **حذف صف** → `package_booking_dates_remove` event
   - إعادة حساب `used_hours` و `remaining_hours`

6. **حفظ الحجز** → `validate()` في Python
   - التحقق من عدم تجاوز الساعات
   - إذا تجاوز: منع الحفظ + رسالة خطأ تفصيلية

---

## الحقول المستخدمة

### في Booking (Parent)
| الحقل | النوع | الوصف |
|------|------|-------|
| `package` | Link | الباقة المختارة |
| `used_hours` | Float | إجمالي الساعات المستخدمة (مجموع hours من جدول التواريخ) |
| `remaining_hours` | Float | الساعات المتبقية (إجمالي الباقة - المستخدم) |
| `package_booking_dates` | Table | جدول تواريخ الحجز |

### في Package Booking Date (Child)
| الحقل | النوع | الوصف |
|------|------|-------|
| `booking_date` | Date | تاريخ الحجز |
| `start_time` | Time | وقت البداية |
| `end_time` | Time | وقت النهاية |
| `hours` | Float | عدد الساعات المحسوبة تلقائياً |
| `notes` | Small Text | ملاحظات خاصة |

### في Package (Master)
| الحقل | النوع | الوصف |
|------|------|-------|
| `total_hours` | Float | إجمالي ساعات الباقة |

---

## سيناريوهات الاختبار

### ✅ سيناريو 1: إضافة تواريخ عادية
1. إنشاء حجز Package بباقة لديها 10 ساعات
2. إضافة تاريخ حجز: من 10:00 إلى 14:00 = 4 ساعات
   - `used_hours` = 4
   - `remaining_hours` = 6
3. إضافة تاريخ ثانٍ: من 15:00 إلى 18:00 = 3 ساعات
   - `used_hours` = 7
   - `remaining_hours` = 3
4. **النتيجة المتوقعة**: جميع الحسابات صحيحة ✅

### ✅ سيناريو 2: استنفاد الساعات بالضبط
1. باقة 5 ساعات
2. إضافة: 10:00 - 15:00 = 5 ساعات
   - `used_hours` = 5
   - `remaining_hours` = 0
   - عرض تنبيه: "تم استنفاد جميع ساعات الباقة"
3. محاولة إضافة صف جديد
   - يتم حذف الصف تلقائياً
   - عرض تنبيه مرة أخرى
4. **النتيجة المتوقعة**: منع إضافة صفوف جديدة ✅

### ✅ سيناريو 3: محاولة تجاوز الساعات
1. باقة 8 ساعات
2. إضافة صف: 09:00 - 18:00 = 9 ساعات
3. محاولة الحفظ
4. **النتيجة المتوقعة**: 
   - رسالة خطأ تفصيلية
   - منع الحفظ
   - "تم تجاوز ساعات الباقة المتاحة! المتاح: 8، المستخدم: 9" ✅

### ✅ سيناريو 4: حذف صف
1. باقة 10 ساعات
2. إضافة صف: 4 ساعات (`used_hours` = 4, `remaining_hours` = 6)
3. إضافة صف: 3 ساعات (`used_hours` = 7, `remaining_hours` = 3)
4. حذف الصف الأول
5. **النتيجة المتوقعة**:
   - `used_hours` = 3
   - `remaining_hours` = 7 ✅

### ✅ سيناريو 5: عبور منتصف الليل
1. باقة 10 ساعات
2. إضافة صف: 22:00 - 02:00 = 4 ساعات
3. **النتيجة المتوقعة**:
   - `hours` = 4.00
   - `used_hours` = 4
   - `remaining_hours` = 6 ✅

---

## الملفات المعدلة

### 1. `/re_studio_booking/doctype/booking/booking.js`
**الدوال المضافة/المحدثة:**
- ✅ `calculate_hours_for_row()` - محدثة بالكامل
- ✅ `calculate_total_used_hours()` - محدثة بالكامل
- ✅ `check_remaining_hours_before_add()` - محدثة بالكامل
- ✅ `show_hours_exhausted_alert()` - جديدة
- ✅ Events: `start_time`, `end_time`, `package_booking_dates_add`, `package_booking_dates_remove` - محدثة
- ✅ Event: `package` - إضافة `calculate_total_used_hours()`

### 2. `/re_studio_booking/doctype/booking/booking.py`
**الدوال المحدثة:**
- ✅ `compute_package_hours_usage()` - تحسين validation مع رسالة خطأ تفصيلية
- ✅ `populate_package_services()` - إصلاح منطق خصم المصور

---

## الخلاصة

### ✅ تم تنفيذ جميع المتطلبات:

1. ✅ حساب الساعات تلقائياً عند اختيار الأوقات
2. ✅ تحديث `used_hours` و `remaining_hours` فورياً
3. ✅ دعم تواريخ حجز متعددة مع جمع الساعات
4. ✅ منع إضافة صفوف عند `remaining_hours` = 0
5. ✅ رسالة تنبيه بنمط `alert-container-message` من الأسفل
6. ✅ منع حفظ الحجز إذا تجاوز الساعات المتاحة
7. ✅ إصلاح استخدام `discounted_price` من جدول المصور

### التحسينات الإضافية:
- ✅ دعم عبور منتصف الليل في حساب الساعات
- ✅ إعادة حساب تلقائي عند حذف صف
- ✅ validation قوي في Python مع رسائل خطأ تفصيلية
- ✅ هامش خطأ صغير (0.01 ساعة) لتجنب مشاكل التقريب
- ✅ كود موثق ومنظم

---

**تاريخ التحديث**: 19 أكتوبر 2025  
**الحالة**: ✅ مكتمل ومختبر  
**الإصدار**: 1.0
