# 🎯 مثال عملي: كيف يجب أن يكون الكود

## الهدف: إظهار الفرق بين الوضع الحالي والمقترح

---

## ❌ الوضع الحالي (booking.py - 2381 سطر)

```python
# booking.py (ملف ضخم واحد)

import frappe
from frappe.model.document import Document
# ... 50 استيراد آخر

class Booking(Document):
    def before_save(self):
        # منطق معقد هنا مباشرة (50 سطر)
        if not self.current_employee:
            self.current_employee = frappe.session.user
        
        if self.status != 'Confirmed':
            self.status = 'Confirmed'
        
        # حساب العربون - منطق معقد 30 سطر
        base_amount = 0
        if self.booking_type == 'Service':
            base_amount = self.total_amount or 0
        elif self.booking_type == 'Package':
            base_amount = self.total_amount_package or 0
        
        deposit_percentage = 30
        try:
            general_settings = frappe.get_single('General Settings')
            if hasattr(general_settings, 'default_deposit_percentage'):
                deposit_percentage = general_settings.default_deposit_percentage
        except:
            pass
        
        if base_amount > 0:
            self.deposit_amount = round(base_amount * deposit_percentage / 100, 2)
        # ... 20 سطر إضافية
    
    def validate(self):
        # 200 سطر من المنطق المعقد
        self.validate_dates()
        self.validate_availability()
        self.calculate_time_usage()
        if self.booking_type == 'Package':
            self.compute_package_hours_usage()
        self._deduplicate_selected_services()
        self.recompute_pricing()
        self.calculate_booking_total()
    
    def validate_dates(self):
        # 50 سطر من التحقق
        pass
    
    def validate_availability(self):
        # 40 سطر من التحقق
        pass
    
    def calculate_time_usage(self):
        # 80 سطر من الحسابات
        pass
    
    def compute_package_hours_usage(self):
        # 90 سطر من الحسابات
        pass
    
    def recompute_pricing(self):
        # 100 سطر من الحسابات
        pass
    
    # ... 25 method أخرى

# بعد الكلاس، 40 دالة API
@frappe.whitelist()
def get_package_services(package_name):
    # 50 سطر
    pass

@frappe.whitelist()
def get_service_details(service):
    # 30 سطر
    pass

# ... 38 دالة API أخرى

# النتيجة: ملف 2381 سطر، صعب القراءة والصيانة
```

---

## ✅ الوضع المقترح (5 ملفات منظمة)

### 1️⃣ booking.py (Orchestration - 600 سطر)

```python
# booking.py - التنسيق فقط

import frappe
from frappe.model.document import Document

# استيراد منظم من الملفات المساعدة
from .booking_utils import (
    calculate_deposit_amount,
    get_studio_working_days,
    format_currency_arabic
)
from .booking_validations import (
    validate_dates,
    validate_availability,
    validate_package_hours,
    check_deletion_permission
)
from .booking_calculations import (
    calculate_time_usage,
    recompute_pricing,
    calculate_booking_datetime
)


class Booking(Document):
    """
    مستند الحجز - مسؤول عن تنسيق العمليات فقط
    المنطق الفعلي موجود في الملفات المساعدة
    """
    
    # ============ Lifecycle Methods ============
    
    def before_save(self):
        """تنفيذ العمليات قبل الحفظ"""
        # تعيين الموظف الحالي
        if not self.current_employee:
            self.current_employee = frappe.session.user
        
        # تغيير الحالة
        if self.status != 'Confirmed':
            self.status = 'Confirmed'
        
        # حساب العربون (المنطق في booking_utils)
        calculate_deposit_amount(self)
        
        # التحقق من أيام العمل (المنطق في booking_validations)
        from .booking_validations import validate_studio_working_day
        validate_studio_working_day(self)
        
        # التحقق من المبلغ المدفوع
        from .booking_utils import validate_paid_amount
        validate_paid_amount(self)
    
    def validate(self):
        """التحقق من صحة البيانات"""
        # التحقق من التواريخ
        validate_dates(self)
        
        # التحقق من التوفر
        validate_availability(self)
        
        # حساب تاريخ ووقت الحجز
        calculate_booking_datetime(self)
        
        # حساب الوقت المستخدم
        calculate_time_usage(self)
        
        # التحقق من ساعات الباقة
        if self.booking_type == 'Package':
            validate_package_hours(self)
        
        # دمج الخدمات المكررة
        if self.booking_type == 'Service':
            self._deduplicate_selected_services()
        elif self.booking_type == 'Package':
            self._deduplicate_package_services()
        
        # إعادة حساب الأسعار
        recompute_pricing(self)
        
        # حساب الإجمالي
        from .booking_calculations import calculate_booking_total
        calculate_booking_total(self)
    
    def on_trash(self):
        """منع حذف الحجز إذا كان مدفوعاً بالكامل"""
        check_deletion_permission(self)
    
    def before_cancel(self):
        """منع إلغاء الحجز إذا كان مدفوعاً بالكامل"""
        check_deletion_permission(self)
    
    # ============ Helper Methods (Light) ============
    
    def _deduplicate_selected_services(self):
        """دمج الخدمات المكررة - منطق بسيط"""
        # منطق بسيط جداً هنا فقط
        pass
    
    def _deduplicate_package_services(self):
        """دمج خدمات الباقة المكررة - منطق بسيط"""
        # منطق بسيط جداً هنا فقط
        pass


# النتيجة: ملف 600 سطر فقط، واضح ومنظم
```

---

### 2️⃣ booking_utils.py (Business Logic - 1200 سطر)

```python
# booking_utils.py - المنطق الأساسي

import frappe
from frappe import _
from frappe.utils import flt, getdate, time_diff_in_seconds


# ============ Deposit Calculation ============

def calculate_deposit_amount(booking_doc):
    """
    حساب مبلغ العربون تلقائياً بناءً على نوع الحجز
    
    Args:
        booking_doc: مستند الحجز
    
    Returns:
        None (يحدث حقل deposit_amount مباشرة)
    """
    try:
        # تحديد المبلغ الأساسي للحساب
        base_amount = 0
        
        if booking_doc.booking_type == 'Service':
            base_amount = booking_doc.total_amount or 0
        elif booking_doc.booking_type == 'Package':
            base_amount = booking_doc.total_amount_package or 0
        
        # الحصول على نسبة العربون من الإعدادات
        deposit_percentage = get_deposit_percentage()
        
        # حساب مبلغ العربون
        if base_amount > 0:
            booking_doc.deposit_amount = round(base_amount * deposit_percentage / 100, 2)
            
        # logging للتشخيص
        frappe.logger().info(
            f"تم حساب العربون للحجز {booking_doc.name}: "
            f"{booking_doc.deposit_amount} ({deposit_percentage}% من {base_amount})"
        )
        
    except Exception as e:
        frappe.log_error(f"خطأ في حساب العربون: {str(e)}")
        # قيمة افتراضية
        if booking_doc.total_amount:
            booking_doc.deposit_amount = round(booking_doc.total_amount * 0.3, 2)


def get_deposit_percentage():
    """
    الحصول على نسبة العربون من الإعدادات العامة
    
    Returns:
        float: نسبة العربون (افتراضي: 30)
    """
    try:
        settings = frappe.get_single('General Settings')
        if hasattr(settings, 'default_deposit_percentage') and settings.default_deposit_percentage:
            return flt(settings.default_deposit_percentage)
    except Exception:
        pass
    
    return 30.0  # الافتراضي


# ============ Payment Validation ============

def validate_paid_amount(booking_doc):
    """
    التحقق من صحة المبلغ المدفوع
    
    Args:
        booking_doc: مستند الحجز
    
    Raises:
        frappe.ValidationError: إذا كان المبلغ غير صحيح
    """
    paid_amount = flt(booking_doc.get('paid_amount', 0))
    deposit_amount = flt(booking_doc.get('deposit_amount', 0))
    
    # تحديد المبلغ الإجمالي حسب النوع
    if booking_doc.booking_type == 'Service':
        total_amount = flt(booking_doc.get('total_amount', 0))
    elif booking_doc.booking_type == 'Package':
        total_amount = flt(booking_doc.get('total_amount_package', 0))
    else:
        return
    
    # لا تحقق إذا لم يدفع شيء
    if paid_amount == 0:
        return
    
    # التحقق: المبلغ المدفوع >= العربون
    if paid_amount < deposit_amount:
        frappe.throw(_(
            f"❌ المبلغ المدفوع ({format_currency_arabic(paid_amount)}) "
            f"أقل من مبلغ العربون ({format_currency_arabic(deposit_amount)})!"
        ), title="خطأ في المبلغ المدفوع")
    
    # التحقق: المبلغ المدفوع <= المبلغ الإجمالي
    if paid_amount > total_amount:
        excess = paid_amount - total_amount
        frappe.throw(_(
            f"❌ المبلغ المدفوع ({format_currency_arabic(paid_amount)}) "
            f"يتجاوز المبلغ الإجمالي ({format_currency_arabic(total_amount)}) "
            f"بمقدار {format_currency_arabic(excess)}!"
        ), title="خطأ في المبلغ المدفوع")


# ============ Auto Payment Status ============

def auto_set_payment_status(booking_doc):
    """
    تحديث حالة الدفع تلقائياً بناءً على المبلغ المدفوع
    
    Args:
        booking_doc: مستند الحجز
    """
    try:
        paid = flt(booking_doc.get('paid_amount', 0))
        
        if booking_doc.booking_type == 'Service':
            total = flt(booking_doc.get('total_amount', 0))
        else:
            total = flt(booking_doc.get('total_amount_package', 0))
        
        if total <= 0:
            return
        
        if paid >= total:
            booking_doc.payment_status = 'Paid'
        elif paid > 0:
            booking_doc.payment_status = 'Partially Paid'
        else:
            if not booking_doc.get('payment_status'):
                booking_doc.payment_status = 'Confirmed'
                
    except Exception as e:
        frappe.log_error(f"خطأ في تحديث حالة الدفع: {str(e)}")


# ============ Photographer Discount ============

def calculate_photographer_discounted_rate(service_item, photographer, package_doc):
    """
    حساب سعر الساعة بعد خصم المصور
    
    Args:
        service_item: صف الخدمة
        photographer: اسم المصور
        package_doc: مستند الباقة
    
    Returns:
        float: السعر بعد الخصم
    """
    if not photographer:
        return flt(service_item.get('hourly_rate', 0))
    
    # جلب بيانات المصور
    photographer_doc = frappe.get_doc('Photographer', photographer)
    
    # التحقق من B2B
    if not photographer_doc.get('b2b'):
        return flt(service_item.get('hourly_rate', 0))
    
    # البحث عن الخدمة في جدول المصور
    service_name = service_item.get('service')
    for ps in photographer_doc.get('services', []):
        if ps.service == service_name:
            # أولوية 1: السعر المخصوم
            if flt(ps.get('discounted_price', 0)) > 0:
                return flt(ps.discounted_price)
            
            # أولوية 2: نسبة الخصم
            discount_pct = flt(photographer_doc.get('discount_percentage', 0))
            if discount_pct > 0:
                hourly_rate = flt(service_item.get('hourly_rate', 0))
                return hourly_rate * (1 - discount_pct / 100)
    
    # السعر الأصلي
    return flt(service_item.get('hourly_rate', 0))


# ============ Studio Settings ============

def get_studio_working_days():
    """
    جلب أيام العمل من الإعدادات
    
    Returns:
        list: قائمة بأسماء أيام العمل بالإنجليزية
    """
    try:
        if frappe.db.exists('DocType', 'General Settings'):
            settings = frappe.get_single('General Settings')
            working_days = []
            
            days_mapping = {
                'sunday_working': 'Sunday',
                'monday_working': 'Monday',
                'tuesday_working': 'Tuesday',
                'wednesday_working': 'Wednesday',
                'thursday_working': 'Thursday',
                'friday_working': 'Friday',
                'saturday_working': 'Saturday'
            }
            
            for field, day in days_mapping.items():
                if hasattr(settings, field) and getattr(settings, field):
                    working_days.append(day)
            
            return working_days or get_default_working_days()
    except Exception as e:
        frappe.log_error(f"خطأ في جلب أيام العمل: {str(e)}")
    
    return get_default_working_days()


def get_default_working_days():
    """الأيام الافتراضية"""
    return ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Saturday']


# ============ Utilities ============

def format_currency_arabic(amount):
    """
    تنسيق المبلغ بالعملة العربية
    
    Args:
        amount: المبلغ
    
    Returns:
        str: المبلغ منسق
    """
    currency = frappe.defaults.get_defaults().get('currency', 'EGP')
    currency_symbol = {
        'EGP': 'ج.م',
        'SAR': 'ر.س',
        'USD': '$'
    }.get(currency, currency)
    
    return f"{flt(amount, 2):,.2f} {currency_symbol}"


# ... باقي الدوال (40+ دالة أخرى)

# النتيجة: ملف 1200 سطر، منظم ومقسم لأقسام واضحة
```

---

### 3️⃣ booking_validations.py (Validation Logic - 400 سطر)

```python
# booking_validations.py - جميع التحققات

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, flt
from datetime import datetime


# ============ Date Validations ============

def validate_dates(booking_doc):
    """
    التحقق من صحة التواريخ
    
    Args:
        booking_doc: مستند الحجز
    
    Raises:
        frappe.ValidationError: إذا كان التاريخ غير صحيح
    """
    today = getdate(nowdate())
    
    # Service: تاريخ واحد
    if booking_doc.booking_type == 'Service' and booking_doc.get('booking_date'):
        if getdate(booking_doc.booking_date) < today:
            frappe.throw(_("لا يمكن إنشاء حجز في تاريخ سابق"))
    
    # Package: تواريخ متعددة
    if booking_doc.booking_type == 'Package':
        _validate_package_dates(booking_doc, today)


def _validate_package_dates(booking_doc, today):
    """التحقق من تواريخ الباقة"""
    future_exists = False
    past_rows = []
    
    for row in (booking_doc.get('package_booking_dates') or []):
        if row.get('booking_date'):
            row_date = getdate(row.booking_date)
            if row_date >= today:
                future_exists = True
            else:
                past_rows.append(str(row.booking_date))
    
    # إذا كل التواريخ في الماضي
    if booking_doc.get('package_booking_dates') and not future_exists:
        frappe.throw(_("لا يمكن إنشاء حجز كل تواريخه في الماضي"))
    
    # تحذير للتواريخ الماضية
    if past_rows and future_exists:
        frappe.msgprint(
            _(f"تحذير: بعض التواريخ في الماضي: {', '.join(past_rows)}"),
            indicator='orange'
        )


def validate_studio_working_day(booking_doc):
    """
    التحقق من أن التاريخ في يوم عمل
    
    Args:
        booking_doc: مستند الحجز
    """
    if not booking_doc.get('booking_date'):
        return
    
    try:
        booking_date = datetime.strptime(str(booking_doc.booking_date), '%Y-%m-%d')
        day_name = booking_date.strftime('%A')
        
        # جلب أيام العمل
        from .booking_utils import get_studio_working_days
        working_days = get_studio_working_days()
        
        if day_name not in working_days:
            day_arabic = _get_arabic_day_name(day_name)
            frappe.throw(_(
                f"لا يمكن الحجز في يوم {day_arabic} - "
                f"هذا اليوم عطلة رسمية حسب إعدادات الاستديو"
            ))
    except Exception as e:
        frappe.log_error(f"خطأ في التحقق من يوم العمل: {str(e)}")


def _get_arabic_day_name(day_name):
    """تحويل اسم اليوم للعربية"""
    days = {
        'Sunday': 'الأحد',
        'Monday': 'الاثنين',
        'Tuesday': 'الثلاثاء',
        'Wednesday': 'الأربعاء',
        'Thursday': 'الخميس',
        'Friday': 'الجمعة',
        'Saturday': 'السبت'
    }
    return days.get(day_name, day_name)


# ============ Availability Validation ============

def validate_availability(booking_doc):
    """
    التحقق من توفر الوقت (لا يوجد حجز متداخل)
    
    Args:
        booking_doc: مستند الحجز
    """
    if not (booking_doc.get('start_time') and 
            booking_doc.get('end_time') and 
            booking_doc.get('booking_date') and 
            booking_doc.get('photographer')):
        return
    
    # البحث عن حجوزات متداخلة
    existing = frappe.get_all(
        "Booking",
        filters=[
            ["booking_date", "=", booking_doc.booking_date],
            ["photographer", "=", booking_doc.photographer],
            ["status", "not in", ["Cancelled"]],
            ["name", "!=", booking_doc.name or "new"],
            ["start_time", "<", booking_doc.end_time],
            ["end_time", ">", booking_doc.start_time]
        ]
    )
    
    if existing:
        frappe.throw(_("هذا الوقت محجوز بالفعل. الرجاء اختيار وقت آخر."))


# ============ Hours Validation ============

def validate_package_hours(booking_doc):
    """
    التحقق من عدم تجاوز ساعات الباقة
    
    Args:
        booking_doc: مستند الحجز
    """
    if booking_doc.booking_type != 'Package':
        return
    
    # حساب الساعات المستخدمة
    from .booking_calculations import compute_package_hours_usage
    compute_package_hours_usage(booking_doc)
    
    # التحقق من التجاوز
    package_total = flt(frappe.db.get_value('Package', booking_doc.package, 'total_hours') or 0)
    used = flt(booking_doc.get('used_hours', 0))
    
    if package_total > 0 and used > package_total:
        excess = used - package_total
        if excess > 0.01:  # هامش خطأ
            frappe.throw(_(
                f"⚠️ تم تجاوز ساعات الباقة!<br><br>"
                f"<b>إجمالي الباقة:</b> {package_total} ساعة<br>"
                f"<b>المستخدم:</b> {used} ساعة<br>"
                f"<b>الزائد:</b> {round(excess, 2)} ساعة"
            ), title="تجاوز ساعات الباقة")


# ============ Deletion Permission ============

def check_deletion_permission(booking_doc):
    """
    منع حذف/إلغاء الحجوزات المدفوعة بالكامل
    
    Args:
        booking_doc: مستند الحجز
    """
    # السماح للـ Administrator
    if frappe.session.user == "Administrator":
        return
    
    # فقط للـ Service
    if booking_doc.booking_type != 'Service':
        return
    
    paid = flt(booking_doc.get('paid_amount', 0))
    total = flt(booking_doc.get('total_amount', 0))
    
    # إذا مدفوع بالكامل
    if paid > 0 and total > 0 and abs(paid - total) < 0.01:
        frappe.throw(_(
            f"⛔ لا يمكن حذف أو إلغاء هذا الحجز!<br><br>"
            f"<b>السبب:</b> تم دفع المبلغ بالكامل<br>"
            f"<b>المبلغ:</b> {paid:,.2f} ريال<br><br>"
            f"يمكن فقط لـ Administrator الحذف"
        ), title="غير مسموح بالحذف")


# ... باقي دوال التحقق (15+ دالة)

# النتيجة: ملف 400 سطر، كل التحققات في مكان واحد
```

---

### 4️⃣ booking_calculations.py (Calculation Logic - 500 سطر)

```python
# booking_calculations.py - جميع الحسابات

import frappe
from frappe.utils import flt, time_diff_in_seconds
from datetime import datetime


# ============ Time Calculations ============

def calculate_time_usage(booking_doc):
    """
    حساب الوقت المستخدم
    
    Args:
        booking_doc: مستند الحجز
    """
    if booking_doc.booking_type == 'Service':
        _calculate_service_time_usage(booking_doc)
    elif booking_doc.booking_type == 'Package':
        _calculate_package_time_usage(booking_doc)


def _calculate_service_time_usage(booking_doc):
    """حساب وقت الخدمة"""
    if not (booking_doc.get('start_time') and booking_doc.get('end_time')):
        return
    
    try:
        seconds = time_diff_in_seconds(booking_doc.end_time, booking_doc.start_time)
        if seconds < 0:
            frappe.throw(_('وقت النهاية يجب أن يكون بعد وقت البداية'))
        
        booking_doc.total_booked_hours = round(seconds / 3600.0, 2)
        
        # تحديث كمية الخدمات
        for row in (booking_doc.get('selected_services_table') or []):
            row.quantity = booking_doc.total_booked_hours
    except Exception as e:
        frappe.log_error(f"خطأ في حساب وقت الخدمة: {str(e)}")


def _calculate_package_time_usage(booking_doc):
    """حساب وقت الباقة"""
    rows = booking_doc.get('package_booking_dates') or []
    if not rows:
        frappe.throw(_('يجب إدخال تواريخ الحجز للباقة'))
    
    used = 0.0
    for row in rows:
        if row.get('start_time') and row.get('end_time'):
            try:
                seconds = time_diff_in_seconds(row.end_time, row.start_time)
                if seconds < 0:
                    frappe.throw(_('وقت النهاية يجب أن يكون بعد وقت البداية'))
                
                row_hours = round(seconds / 3600.0, 2)
                row.hours = row_hours
                used += row_hours
            except Exception:
                pass
    
    booking_doc.used_hours = round(used, 2)


def compute_package_hours_usage(booking_doc):
    """
    حساب استخدام ساعات الباقة مع التحقق
    
    Args:
        booking_doc: مستند الحجز
    """
    if booking_doc.booking_type != 'Package':
        return
    
    # جلب إجمالي ساعات الباقة
    package_total = flt(frappe.db.get_value('Package', booking_doc.package, 'total_hours') or 0)
    
    used = 0.0
    for row in (booking_doc.get('package_booking_dates') or []):
        if row.get('start_time') and row.get('end_time'):
            try:
                # استخدام التاريخ من الصف
                booking_date = row.get('booking_date') or booking_doc.get('booking_date')
                
                if booking_date:
                    start_str = f"{booking_date} {row.start_time}"
                    end_str = f"{booking_date} {row.end_time}"
                    fmt = '%Y-%m-%d %H:%M:%S'
                    
                    start_dt = datetime.strptime(start_str, fmt)
                    end_dt = datetime.strptime(end_str, fmt)
                    
                    # عبور منتصف الليل
                    if end_dt <= start_dt:
                        end_dt = end_dt.replace(day=end_dt.day + 1)
                    
                    row.hours = round((end_dt - start_dt).total_seconds() / 3600.0, 2)
            except Exception as e:
                frappe.log_error(f"خطأ في حساب الساعات للصف: {str(e)}")
                if not row.get('hours'):
                    row.hours = 0
        
        if row.get('hours'):
            used += flt(row.hours)
    
    booking_doc.used_hours = round(used, 2)
    remaining = max(package_total - used, 0.0)
    booking_doc.remaining_hours = round(remaining, 2)


def calculate_booking_datetime(booking_doc):
    """حساب تاريخ ووقت الحجز"""
    if booking_doc.get('booking_date') and booking_doc.get('booking_time'):
        booking_datetime = f"{booking_doc.booking_date} {booking_doc.booking_time}:00"
        booking_doc.booking_datetime = booking_datetime


# ============ Pricing Calculations ============

def recompute_pricing(booking_doc):
    """
    إعادة حساب جميع الأسعار
    
    Args:
        booking_doc: مستند الحجز
    """
    try:
        # تحميل بيانات المصور
        ctx = _load_photographer_context(booking_doc)
        
        # إعادة بناء الصفوف مع الأسعار
        if booking_doc.booking_type == 'Package':
            _build_package_rows(booking_doc, ctx)
            _aggregate_package_totals(booking_doc)
        elif booking_doc.booking_type == 'Service':
            _build_service_rows(booking_doc, ctx)
            _aggregate_service_totals(booking_doc)
        
        # حساب العربون
        from .booking_utils import calculate_deposit_amount, auto_set_payment_status
        calculate_deposit_amount(booking_doc)
        auto_set_payment_status(booking_doc)
        
    except Exception as e:
        frappe.log_error(f"خطأ في إعادة حساب الأسعار: {str(e)}")


def _load_photographer_context(booking_doc):
    """تحميل بيانات المصور للخصومات"""
    ctx = {"discount_pct": 0.0, "allowed_services": set()}
    
    if booking_doc.get('photographer_b2b') and booking_doc.get('photographer'):
        try:
            ctx["discount_pct"] = flt(frappe.db.get_value(
                "Photographer", booking_doc.photographer, "discount_percentage"
            ) or 0)
            
            services = frappe.get_all(
                "Photographer Service",
                filters={"parent": booking_doc.photographer, "is_active": 1},
                fields=["service"]
            )
            ctx["allowed_services"] = {s.service for s in services}
        except Exception:
            pass
    
    return ctx


def _build_package_rows(booking_doc, ctx):
    """بناء صفوف خدمات الباقة مع الخصومات"""
    # ... منطق معقد هنا
    pass


def _build_service_rows(booking_doc, ctx):
    """بناء صفوف الخدمات مع الخصومات"""
    # ... منطق معقد هنا
    pass


def _aggregate_package_totals(booking_doc):
    """تجميع إجماليات الباقة"""
    base_total = 0.0
    final_total = 0.0
    
    for row in (booking_doc.get('package_services_table') or []):
        qty = flt(row.get('quantity', 1))
        bp = flt(row.get('base_price', 0))
        base_total += bp * qty
        final_total += flt(row.get('amount', 0))
    
    booking_doc.base_amount_package = round(base_total, 2)
    booking_doc.total_amount_package = round(final_total, 2)


def _aggregate_service_totals(booking_doc):
    """تجميع إجماليات الخدمات"""
    base_total = 0.0
    final_total = 0.0
    
    for row in (booking_doc.get('selected_services_table') or []):
        base_total += flt(row.get('base_amount', 0))
        final_total += flt(row.get('total_amount', 0))
    
    booking_doc.base_amount = round(base_total, 2)
    booking_doc.total_amount = round(final_total, 2)


def calculate_booking_total(booking_doc):
    """حساب الإجمالي الكلي"""
    if booking_doc.booking_type == 'Service':
        _aggregate_service_totals(booking_doc)
    elif booking_doc.booking_type == 'Package':
        _aggregate_package_totals(booking_doc)


# ... باقي دوال الحساب (20+ دالة)

# النتيجة: ملف 500 سطر، كل الحسابات في مكان واحد
```

---

### 5️⃣ booking_api.py (API Layer - 700 سطر)

```python
# booking_api.py - جميع الـ APIs المكشوفة

import frappe
from frappe import _
from frappe.utils import flt


# ============ Package APIs ============

@frappe.whitelist()
def get_package_services(package_name):
    """
    جلب خدمات الباقة
    
    Args:
        package_name: اسم الباقة
    
    Returns:
        dict: قاموس بخدمات الباقة
    """
    try:
        if not package_name:
            return {"error": "Package name is required"}
        
        services = frappe.get_all(
            "Package Service Item",
            filters={"parent": package_name},
            fields=["service", "service_name", "quantity", "base_price", "package_price"]
        )
        
        return {"services": services}
    except Exception as e:
        frappe.log_error(f"Error fetching package services: {str(e)}")
        return {"error": str(e)}


@frappe.whitelist()
def get_package_services_with_photographer(package_name, photographer=None, photographer_b2b=0):
    """
    جلب خدمات الباقة مع تطبيق خصم المصور
    
    Args:
        package_name: اسم الباقة
        photographer: اسم المصور
        photographer_b2b: تفعيل B2B (0 أو 1)
    
    Returns:
        dict: خدمات الباقة مع الخصومات
    """
    try:
        if not package_name:
            return {"error": "Package name is required"}
        
        # جلب الخدمات الأساسية
        package_doc = frappe.get_doc("Package", package_name)
        services = []
        
        # تطبيق الخصم إذا كان هناك مصور
        if photographer and int(photographer_b2b):
            from .booking_utils import calculate_photographer_discounted_rate
            
            for item in package_doc.get('services', []):
                discounted_rate = calculate_photographer_discounted_rate(
                    item, photographer, package_doc
                )
                
                services.append({
                    "service": item.service,
                    "service_name": item.service_name,
                    "quantity": item.quantity,
                    "base_price": item.base_price,
                    "package_price": item.package_price,
                    "photographer_discount_amount": discounted_rate,
                    "amount": item.quantity * discounted_rate
                })
        else:
            # بدون خصم
            for item in package_doc.get('services', []):
                services.append({
                    "service": item.service,
                    "service_name": item.service_name,
                    "quantity": item.quantity,
                    "base_price": item.base_price,
                    "package_price": item.package_price,
                    "amount": item.quantity * item.package_price
                })
        
        return {
            "services": services,
            "total_hours": package_doc.total_hours
        }
    except Exception as e:
        frappe.log_error(f"Error fetching package services with photographer: {str(e)}")
        return {"error": str(e)}


# ============ Service APIs ============

@frappe.whitelist()
def get_service_details(service):
    """جلب تفاصيل الخدمة"""
    try:
        if not service:
            return {"error": "Service name is required"}
        
        service_doc = frappe.get_doc("Service", service)
        
        return {
            "name": service_doc.name,
            "service_name": service_doc.service_name,
            "price": service_doc.price,
            "duration": service_doc.duration,
            "category": service_doc.category
        }
    except Exception as e:
        return {"error": str(e)}


# ============ Photographer APIs ============

@frappe.whitelist()
def get_available_photographers(booking_date, booking_time, service=None, duration=60):
    """جلب المصورين المتاحين"""
    try:
        # ... منطق معقد
        return {"photographers": []}
    except Exception as e:
        return {"error": str(e)}


@frappe.whitelist()
def get_photographer_details(photographer):
    """جلب تفاصيل المصور"""
    try:
        photographer_doc = frappe.get_doc("Photographer", photographer)
        
        return {
            "name": photographer_doc.name,
            "full_name": photographer_doc.full_name,
            "b2b": photographer_doc.b2b,
            "discount_percentage": photographer_doc.discount_percentage
        }
    except Exception as e:
        return {"error": str(e)}


# ============ Booking Management APIs ============

@frappe.whitelist()
def create_booking_invoice(booking):
    """إنشاء فاتورة من الحجز"""
    try:
        # ... منطق معقد
        return {"invoice": "INV-001"}
    except Exception as e:
        return {"error": str(e)}


@frappe.whitelist()
def update_booking_status(booking, status):
    """تحديث حالة الحجز"""
    try:
        doc = frappe.get_doc("Booking", booking)
        doc.status = status
        doc.save()
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}


# ... باقي الـ APIs (35+ دالة أخرى)

# النتيجة: ملف 700 سطر، كل الـ APIs في مكان واحد
```

---

## 📊 المقارنة النهائية

### الوضع الحالي (❌):
```
booking.py: 2381 سطر
  ├── Class Booking (30 methods)
  ├── 40 دالة API (@frappe.whitelist)
  ├── دوال مساعدة
  └── كل شيء معاً!

booking_utils.py: 262 سطر
  └── 8 دوال فقط

الإجمالي: 2643 سطر في ملفين
```

### الوضع المقترح (✅):
```
booking.py: 600 سطر (Orchestration فقط)
booking_utils.py: 1200 سطر (Business Logic)
booking_validations.py: 400 سطر (Validations)
booking_calculations.py: 500 سطر (Calculations)
booking_api.py: 700 سطر (APIs)

الإجمالي: 3400 سطر في 5 ملفات
    (أطول لكن أوضح وأسهل بكثير!)
```

---

## ✅ الفوائد

### 1. **الوضوح** 📖
- كل ملف له مسؤولية واضحة
- سهل إيجاد أي دالة
- سهل فهم تدفق العمل

### 2. **الصيانة** 🔧
- تعديل جزء بدون التأثير على الباقي
- اختبار كل ملف بشكل مستقل
- إضافة ميزات جديدة سهلة

### 3. **الأداء** ⚡
- تحميل أسرع (lazy import)
- استجابة أسرع
- استهلاك ذاكرة أقل

### 4. **التعاون** 👥
- عدة مطورين بدون تعارض
- git conflicts أقل
- code review أسهل

---

## 🎯 الخلاصة

> **"الهيكل المقترح يجعل الكود أطول بـ 30% لكن أوضح بـ 300%!"**

**التوصية النهائية:** استكمل التقسيم فوراً! 🚀
