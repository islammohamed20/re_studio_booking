# إصلاح مشكلة عدم ظهور الحقول في Service

## المشكلة
عند فتح نموذج Service، لا تظهر بعض الحقول مثل:
- `type_unit` (نوع الوحدة)
- `mount` (عدد / الكمية)
- `duration` (المدة)
- وحقول أخرى

## السبب
1. كان هناك خطأ في JavaScript في ملف `service.js` - وجود `}}` بدلاً من `}` في نهاية دالة
2. لم يتم بناء assets بعد تحديث الملفات

## الحل المطبق

### 1. إصلاح JavaScript
تم إصلاح الخطأ في الدالة `toggle_unit_type_fields()` في ملف:
```
/apps/re_studio_booking/re_studio_booking/re_studio_booking/doctype/service/service.js
```

**قبل:**
```javascript
return status_colors[status] || 'gray';
}}  // ❌ قوسان معقوفان

// دالة لإظهار/إخفاء الحقول
function toggle_unit_type_fields(frm) {
const type_unit = frm.doc.type_unit;  // ❌ بدون مسافات
...
```

**بعد:**
```javascript
return status_colors[status] || 'gray';
}  // ✅ قوس واحد فقط

// دالة لإظهار/إخفاء الحقول
function toggle_unit_type_fields(frm) {
	const type_unit = frm.doc.type_unit;  // ✅ مع مسافات صحيحة
	...
```

### 2. الأوامر المنفذة
```bash
# 1. تطبيق التغييرات
bench --site site1.local migrate

# 2. إعادة تحميل DocType
bench --site site1.local reload-doctype Service

# 3. مسح الذاكرة المؤقتة
bench --site site1.local clear-cache

# 4. بناء Assets
bench build --app re_studio_booking

# 5. إعادة تشغيل النظام
bench restart
```

## التحقق من الحل

### الحقول المتوفرة الآن:
✅ **service_name_en** (Data): اسم الخدمة
✅ **category** (Link): الفئة
✅ **is_active** (Check): نشط
✅ **type_unit** (Select): نوع الوحدة
  - خيارات: فارغ, Reels, مدة, Promo, Photo Session, Series, Podcast Ep

✅ **mount** (Int): عدد / الكمية
  - يظهر عندما: `type_unit != 'مدة'`
  
✅ **duration** (Int): المدة الافتراضية
  - يظهر عندما: `type_unit == 'مدة'`
  
✅ **min_duration** (Int): الحد الأدنى للمدة
  - يظهر عندما: `type_unit == 'مدة'`
  
✅ **max_duration** (Int): الحد الأقصى للمدة
  - يظهر عندما: `type_unit == 'مدة'`
  
✅ **duration_unit** (Select): وحدة المدة
  - يظهر عندما: `type_unit == 'مدة'`
  - خيارات: دقيقة, ساعة, يوم

✅ **price** (Currency): السعر الأساسي
✅ **is_mandatory** (Check): إجباري

## كيفية الاستخدام

### سيناريو 1: خدمة بالمدة الزمنية
1. افتح Service جديد
2. اختر `type_unit` = **"مدة"**
3. ستظهر لك:
   - حقل المدة (duration)
   - الحد الأدنى والأقصى
   - وحدة المدة (دقيقة/ساعة/يوم)

### سيناريو 2: خدمة بالكمية
1. افتح Service جديد
2. اختر `type_unit` = **"Reels"** أو **"Photo Session"** أو غيرها
3. سيظهر لك:
   - حقل الكمية (mount)

### سيناريو 3: خدمة بدون تحديد
1. اترك `type_unit` فارغاً
2. لن تظهر حقول المدة أو الكمية

## الدالة الرئيسية

```javascript
function toggle_unit_type_fields(frm) {
	const type_unit = frm.doc.type_unit;
	
	// إظهار/إخفاء حقول المدة
	const show_duration_fields = (type_unit == 'مدة');
	frm.toggle_display('duration', show_duration_fields);
	frm.toggle_display('min_duration', show_duration_fields);
	frm.toggle_display('max_duration', show_duration_fields);
	frm.toggle_display('duration_unit', show_duration_fields);
	
	// إظهار/إخفاء حقل الكمية
	const show_quantity_field = type_unit && type_unit != 'مدة';
	frm.toggle_display('mount', show_quantity_field);
	
	// تحديث الحقول المطلوبة
	frm.toggle_reqd('duration', show_duration_fields);
	frm.toggle_reqd('mount', show_quantity_field);
}
```

## ملاحظات مهمة

1. **الحقول تظهر حسب الشرط (Conditional Display)**
   - إذا لم تختر `type_unit`، لن تظهر حقول المدة أو الكمية
   
2. **التحقق من البيانات**
   - إذا اخترت "مدة" يجب إدخال duration > 0
   - إذا اخترت نوع آخر يجب إدخال mount > 0

3. **التحديث التلقائي**
   - عند تغيير `type_unit`، تتحدث الحقول المعروضة تلقائياً
   - يتم استدعاء `toggle_unit_type_fields()` في:
     - `refresh` event
     - `type_unit` change event

## الاختبار

لاختبار الحل:
1. افتح: http://192.168.1.27:8090/app/service/new
2. جرب تغيير `type_unit` بين الخيارات المختلفة
3. تأكد من ظهور/اختفاء الحقول بشكل صحيح

---

**تاريخ الإصلاح:** 18 أكتوبر 2025
**الحالة:** ✅ تم الإصلاح بنجاح
