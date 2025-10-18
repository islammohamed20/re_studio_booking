# نظام Cost Center - نظام إدارة الخزن والورديات

## نظرة عامة

تم إنشاء نظام Cost Center كامل داخل تطبيق Re Studio Booking لإدارة الخزن المالية، الورديات، المعاملات المالية، التحويلات بين الخزن، وتسليم الورديات.

## 📦 DocTypes المنشأة

### 1. **Cost Center** (الخزنة الافتراضية)

**الحقول:**
- `cost_center_name` (Data) - اسم الخزنة (unique, autoname)
- `cost_center_type` (Select) - نوع الخزنة: Cash, Wallet, Bank, CardTerminal
- `user_account` (Link: User) - حساب المستخدم المسؤول
- `company` (Link: Company) - الشركة
- `currency` (Link: Currency) - العملة
- `default_account` (Link: Account) - الحساب المحاسبي الافتراضي
- `is_active` (Check) - نشط
- `current_balance` (Currency, Read Only) - الرصيد الحالي
- `last_shift` (Link: Shift, Read Only) - آخر وردية
- `total_in` (Currency, Read Only) - إجمالي الإيداعات
- `total_out` (Currency, Read Only) - إجمالي السحوبات

**الوظائف:**
- `validate()` - التحقق من صحة البيانات وحساب الأرصدة
- `validate_default_account()` - التأكد من أن الحساب المحاسبي ليس حساب مجموعة
- `calculate_balances()` - حساب الأرصدة من جميع الورديات المغلقة
- `get_open_shift()` - الحصول على الوردية المفتوحة الحالية
- `can_open_shift()` - التحقق من إمكانية فتح وردية جديدة

**الأزرار:**
- **فتح وردية** - يفتح dialog لفتح وردية جديدة
- **عرض الورديات** - عرض قائمة الورديات الخاصة بهذه الخزنة
- **عرض المعاملات** - عرض تقرير Cost Center Ledger

---

### 2. **Shift Transaction** (معاملة الوردية - Child Table)

**الحقول:**
- `trx_type` (Select) - نوع المعاملة:
  - Payment (دفعة)
  - Refund (مرتجع)
  - Expense (مصروف)
  - OpeningBalance (رصيد افتتاحي)
  - Deposit (إيداع)
  - Withdrawal (سحب)
- `payment_method` (Select) - طريقة الدفع: Cash, Wallet, Bank, Card
- `amount` (Currency) - المبلغ
- `reference_doctype` (Data) - نوع المرجع
- `reference_name` (Data) - رقم المرجع
- `party` (Link: Customer) - العميل
- `description` (Small Text) - الوصف
- `created_by` (Link: User, Read Only) - أنشئ بواسطة
- `created_on` (Datetime, Read Only) - تاريخ الإنشاء

---

### 3. **Shift** (الوردية)

**الحقول:**
- `naming_series` - SHIFT-.YYYY.-.#####
- `cost_center` (Link: Cost Center) - الخزنة
- `opened_by` (Link: User) - فتح بواسطة
- `opened_on` (Datetime) - تاريخ الفتح
- `status` (Select) - الحالة: Open, Closed, Handed Over, Cancelled
- `closed_by` (Link: User) - أغلق بواسطة
- `closed_on` (Datetime) - تاريخ الإغلاق
- `expected_opening_balance` (Currency) - الرصيد الافتتاحي المتوقع
- `actual_closing_balance` (Currency) - الرصيد الختامي الفعلي
- `theoretical_closing_balance` (Currency, Read Only) - الرصيد الختامي النظري
- `difference` (Currency, Read Only) - الفرق
- `shift_transactions` (Table: Shift Transaction) - جدول المعاملات
- الإجماليات:
  - `total_payments` - إجمالي المدفوعات
  - `total_refunds` - إجمالي المرتجعات
  - `total_expenses` - إجمالي المصروفات
  - `total_deposits` - إجمالي الإيداعات
  - `total_withdrawals` - إجمالي السحوبات
  - `net_total` - الصافي

**الوظائف:**
- `validate()` - التحقق من صحة البيانات وحساب الأرصدة
- `validate_single_open_shift()` - منع فتح أكثر من وردية لنفس الخزنة
- `calculate_totals()` - حساب إجماليات المعاملات
- `calculate_theoretical_closing()` - حساب الرصيد النظري
- `calculate_difference()` - حساب الفرق بين الفعلي والنظري
- `validate_closing()` - التحقق من صحة الإغلاق
- `update_cost_center_balance()` - تحديث رصيد الخزنة عند الإغلاق
- `can_add_transaction()` - التحقق من إمكانية إضافة معاملة
- `add_transaction()` - إضافة معاملة جديدة

**الأزرار:**
- **إضافة معاملة** (status=Open) - يفتح dialog لإضافة معاملة
- **طلب تسليم** (status=Open) - طلب تسليم الوردية لمستخدم آخر
- **إغلاق الوردية** (status=Open) - إغلاق الوردية وحساب الفرق
- **عرض التسليمات** (status=Handed Over) - عرض تسليمات هذه الوردية

---

### 4. **Cost Center Transfer** (تحويل بين الخزن)

**الحقول:**
- `naming_series` - CCT-.YYYY.-.#####
- `from_cost_center` (Link: Cost Center) - من الخزنة
- `to_cost_center` (Link: Cost Center) - إلى الخزنة
- `amount` (Currency) - المبلغ
- `transfer_date` (Datetime) - تاريخ التحويل
- `status` (Select) - الحالة: Draft, Completed, Cancelled
- `reference` (Data) - المرجع
- `description` (Text) - الوصف
- `journal_entry` (Link: Journal Entry, Read Only) - القيد المحاسبي

**الوظائف:**
- `validate()` - التحقق من صحة التحويل
- `validate_different_cost_centers()` - التأكد من اختلاف الخزنتين
- `validate_sufficient_balance()` - التحقق من كفاية الرصيد
- `on_submit()` - تنفيذ التحويل وإنشاء القيد
- `create_journal_entry()` - إنشاء قيد محاسبي للتحويل

---

### 5. **Shift Handover** (تسليم الوردية)

**الحقول:**
- `naming_series` - SHO-.YYYY.-.#####
- `shift` (Link: Shift) - الوردية
- `from_user` (Link: User) - المسلم
- `to_user` (Link: User) - المستلم
- `handed_amount` (Currency) - المبلغ المسلم
- `handover_on` (Datetime) - تاريخ التسليم
- `accepted` (Check) - تم القبول
- `accepted_on` (Datetime) - تاريخ القبول
- `notes` (Text) - ملاحظات

**الوظائف:**
- `validate()` - التحقق من صحة التسليم
- `on_update()` - تحديث حالة الوردية عند القبول
- `update_shift_status()` - تغيير حالة الوردية إلى "Handed Over"

---

## 🔌 API Methods

جميع الدوال في الملف: `re_studio_booking/re_studio_booking/api/cost_centers.py`

### 1. `open_shift(cost_center_name, expected_opening_balance=None)`

**الوصف:** فتح وردية جديدة لخزنة معينة

**المعاملات:**
- `cost_center_name` (str) - اسم الخزنة
- `expected_opening_balance` (float, optional) - الرصيد الافتتاحي المتوقع

**الإرجاع:** `shift_name` (str) - اسم الوردية المنشأة

**التحققات:**
- صلاحية إنشاء وردية
- نشاط الخزنة
- عدم وجود وردية مفتوحة بالفعل
- صلاحية المستخدم للخزنة

**مثال:**
```python
shift_name = frappe.call('re_studio_booking.re_studio_booking.api.cost_centers.open_shift',
    cost_center_name='Main Cash',
    expected_opening_balance=5000
)
```

---

### 2. `add_shift_transaction(...)`

**الوصف:** إضافة معاملة إلى وردية مفتوحة

**المعاملات:**
- `shift_name` (str) - اسم الوردية
- `trx_type` (str) - نوع المعاملة
- `payment_method` (str) - طريقة الدفع
- `amount` (float) - المبلغ
- `reference_doctype` (str, optional) - نوع المرجع
- `reference_name` (str, optional) - رقم المرجع
- `party` (str, optional) - العميل
- `description` (str, optional) - الوصف

**الإرجاع:** `row` (dict) - المعاملة المنشأة

**التحققات:**
- صلاحية تعديل الوردية
- حالة الوردية = Open

---

### 3. `close_shift(shift_name, actual_closing_balance, create_journal=True)`

**الوصف:** إغلاق وردية وحساب الفرق

**المعاملات:**
- `shift_name` (str) - اسم الوردية
- `actual_closing_balance` (float) - الرصيد الفعلي المعدود
- `create_journal` (bool, default=True) - إنشاء قيد محاسبي

**الإرجاع:**
```python
{
    "shift_name": "SHIFT-2025-00001",
    "difference": 100.0,
    "theoretical_closing": 5500.0,
    "actual_closing": 5600.0,
    "journal_entry": "JV-2025-00001"  # إن وجد
}
```

**التحققات:**
- صلاحية إغلاق الوردية
- حالة الوردية = Open
- إدخال الرصيد الفعلي

**القيد المحاسبي:**
- إذا كان `difference > 0` (Actual > Theoretical): Cash Over
  - Debit: Cost Center Account
  - Credit: Cash Difference Account
- إذا كان `difference < 0` (Actual < Theoretical): Cash Short
  - Debit: Cash Difference Account
  - Credit: Cost Center Account

---

### 4. `create_cost_center_transfer(from_cost_center, to_cost_center, amount, reference=None)`

**الوصف:** إنشاء تحويل بين خزنتين

**المعاملات:**
- `from_cost_center` (str) - الخزنة المصدر
- `to_cost_center` (str) - الخزنة الهدف
- `amount` (float) - المبلغ
- `reference` (str, optional) - مرجع

**الإرجاع:** `transfer_name` (str)

**التحققات:**
- صلاحية إنشاء تحويل
- اختلاف الخزنتين
- كفاية الرصيد في الخزنة المصدر

**القيد المحاسبي:**
- عند Submit:
  - Debit: To Cost Center Account
  - Credit: From Cost Center Account

---

### 5. `request_handover(shift_name, to_user, handed_amount, notes=None)`

**الوصف:** طلب تسليم وردية

**المعاملات:**
- `shift_name` (str) - اسم الوردية
- `to_user` (str) - المستلم
- `handed_amount` (float) - المبلغ المسلم
- `notes` (str, optional) - ملاحظات

**الإرجاع:** `handover_doc` (dict)

**التحققات:**
- صلاحية طلب تسليم
- حالة الوردية = Open
- المسلم هو من فتح الوردية

---

### 6. `accept_handover(handover_name)`

**الوصف:** قبول تسليم وردية

**المعاملات:**
- `handover_name` (str) - اسم التسليم

**الإرجاع:**
```python
{
    "success": True,
    "message": "تم قبول التسليم بنجاح"
}
```

**التحققات:**
- المستخدم الحالي هو المستلم
- لم يتم القبول مسبقاً

**التأثير:**
- تحديث حالة الوردية إلى "Handed Over"

---

### 7. `get_cost_center_balance(cost_center_name)`

**الوصف:** الحصول على رصيد خزنة

**الإرجاع:**
```python
{
    "cost_center": "Main Cash",
    "current_balance": 5600.0,
    "total_in": 50000.0,
    "total_out": 44400.0,
    "last_shift": "SHIFT-2025-00001"
}
```

---

### 8. `reconcile_incomplete_shifts()`

**الوصف:** تسوية الورديات المتوقفة/القديمة

**الوظيفة:**
- يبحث عن الورديات المفتوحة لأكثر من 24 ساعة
- يغير حالتها إلى "Cancelled"

**الإرجاع:**
```python
{
    "reconciled_shifts": ["SHIFT-2025-00001", "SHIFT-2025-00002"],
    "count": 2
}
```

**الاستخدام:** يجب تشغيله دورياً أو بعد أي عطل في الخادم

---

## 🔒 الصلاحيات (Permissions)

### الأدوار (Roles):

1. **Cost Center Admin**
   - إنشاء وتعديل وحذف Cost Centers
   - عرض جميع الورديات والتحويلات

2. **Cashier**
   - فتح ورديات جديدة للخزن المخصصة له
   - إضافة معاملات للورديات المفتوحة
   - طلب تسليم الورديات

3. **Shift Manager**
   - إغلاق الورديات
   - قبول التسليمات
   - إنشاء تحويلات بين الخزن
   - عرض جميع الورديات

4. **Accountant**
   - عرض جميع المعاملات والقيود
   - إنشاء القيود المحاسبية
   - عرض التقارير المالية

---

## 📊 سير العمل (Workflow)

### فتح وردية:
1. الموظف يذهب إلى Cost Center
2. يضغط على "فتح وردية"
3. يدخل الرصيد الافتتاحي المتوقع
4. يتم إنشاء Shift بحالة "Open"
5. يتم إضافة معاملة OpeningBalance

### إضافة معاملات:
1. الموظف يفتح الوردية المفتوحة
2. يضغط على "إضافة معاملة"
3. يختار نوع المعاملة وطريقة الدفع ويدخل المبلغ
4. يتم إضافة السطر في shift_transactions
5. يتم تحديث الإجماليات تلقائياً

### إغلاق وردية:
1. الموظف يضغط على "إغلاق الوردية"
2. يعد النقد الفعلي ويدخله
3. يتم حساب الفرق تلقائياً
4. إذا كان هناك فرق، يتم إنشاء قيد محاسبي
5. يتم تحديث رصيد Cost Center

### تسليم وردية:
1. المسلم يضغط على "طلب تسليم"
2. يختار المستلم ويدخل المبلغ المسلم
3. يتم إنشاء Shift Handover
4. المستلم يفتح التسليم ويضغط "قبول"
5. يتم تحديث حالة الوردية إلى "Handed Over"

### تحويل بين خزن:
1. Shift Manager ينشئ Cost Center Transfer
2. يختار الخزنة المصدر والهدف ويدخل المبلغ
3. عند Submit، يتم إنشاء قيد محاسبي
4. يتم خصم من المصدر وإضافة للهدف

---

## 🎯 ملاحظات مهمة

### Validation Rules:
- ✅ لا يمكن فتح أكثر من وردية لنفس الخزنة
- ✅ لا يمكن إضافة معاملات لوردية مغلقة
- ✅ يجب إدخال الرصيد الفعلي قبل الإغلاق
- ✅ لا يمكن التحويل من وإلى نفس الخزنة
- ✅ يجب التحقق من كفاية الرصيد قبل التحويل
- ✅ فقط من فتح الوردية يمكنه طلب التسليم
- ✅ فقط المستلم يمكنه قبول التسليم

### Audit Trail:
- جميع DocTypes تتبع التغييرات (`track_changes = 1`)
- يتم تسجيل `created_by` و `created_on` لكل معاملة
- يتم تسجيل `opened_by`, `closed_by` للورديات
- يتم ربط القيود المحاسبية بالمعاملات

### Edge Cases:
- **Server Crash:** استخدم `reconcile_incomplete_shifts()` لتسوية الورديات القديمة
- **Concurrent Access:** يتم منع فتح ورديتين لنفس الخزنة
- **Balance Mismatch:** يتم إنشاء قيد محاسبي تلقائي للفرق
- **Missing Accounts:** يتم عرض رسالة تنبيه بدلاً من خطأ

---

## 📈 التقارير المطلوبة (TODO)

### 1. Shift Summary Report
- قائمة بجميع الورديات
- الإجماليات لكل طريقة دفع
- من فتح ومن أغلق
- التواريخ والفروقات

### 2. Cost Center Ledger Report
- جميع المعاملات لخزنة معينة
- Running Balance
- التصفية حسب التاريخ ونوع المعاملة

### 3. POS-like Interface (Desk Page)
- واجهة سريعة لإضافة المدفوعات
- أزرار سريعة للمبالغ الشائعة
- عرض الرصيد الحالي
- ملخص الوردية الحالية

---

## ✅ ما تم إنجازه

1. ✅ إنشاء جميع DocTypes المطلوبة (5 DocTypes)
2. ✅ إنشاء جميع API Methods المطلوبة (8 functions)
3. ✅ إضافة Validation Logic كاملة
4. ✅ إضافة UI Buttons والعمليات
5. ✅ إعداد Permissions للأدوار الأربعة
6. ✅ إنشاء القيود المحاسبية التلقائية
7. ✅ معالجة Edge Cases (Server Crash, Concurrent Access)
8. ✅ Audit Trail كامل

## 🔄 ما يحتاج تطوير إضافي

1. ⏳ إنشاء Script Reports (Shift Summary & Cost Center Ledger)
2. ⏳ إنشاء Desk Page لواجهة POS
3. ⏳ إضافة Web Form للعملاء
4. ⏳ إضافة Notifications عند طلب التسليم
5. ⏳ إنشاء Dashboard للمتابعة اليومية

---

## 🚀 كيفية الاستخدام

### 1. إنشاء خزنة جديدة:
```
http://192.168.1.27:8090/app/cost-center/new
```

### 2. فتح وردية:
```
افتح Cost Center → اضغط "فتح وردية"
```

### 3. إضافة معاملة:
```
افتح Shift المفتوحة → اضغط "إضافة معاملة"
```

### 4. إغلاق وردية:
```
افتح Shift المفتوحة → اضغط "إغلاق الوردية"
```

### 5. عرض التقارير:
```
http://192.168.1.27:8090/app/query-report/Cost%20Center%20Ledger
```

---

**تاريخ الإنشاء:** 18 أكتوبر 2025
**الحالة:** ✅ جاهز للاستخدام
**الإصدار:** 1.0.0
