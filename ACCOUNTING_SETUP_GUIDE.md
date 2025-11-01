# 📊 دليل إعداد التكامل المحاسبي - Re Studio Booking

## ✅ **ما تم إضافته:**

### 1️⃣ **حقول محاسبية جديدة في Booking Invoice:**
- **Company** (الشركة): ربط بـ Company DocType
- **Cost Center** (مركز التكلفة): لتصنيف الإيرادات
- **Debit To** (حساب المدين): حساب الخزينة/البنك الذي يستقبل الأموال
- **Income Account** (حساب الإيرادات): حساب إيرادات الاستوديو
- **Journal Entry** (القيد المرتبط): رابط للقيد المحاسبي المُنشأ تلقائياً

### 2️⃣ **إنشاء قيود محاسبية تلقائياً:**
عند **Submit** الفاتورة، يتم إنشاء Journal Entry:
```
المدين (Debit):   حساب الخزينة/البنك    [المبلغ المدفوع]
الدائن (Credit):  حساب الإيرادات       [المبلغ المدفوع]
```

### 3️⃣ **أزرار جديدة في Booking Invoice:**
- **إنشاء قيد محاسبي** (يظهر للفواتير المعتمدة بدون قيد)
- **عرض القيد المحاسبي** (للانتقال للقيد المرتبط)

---

## 🔧 **خطوات الإعداد:**

### **الخطوة 1: إنشاء Chart of Accounts (إذا لم يكن موجوداً)**

```bash
# من Terminal
bench --site site1.local install-app erpnext
```

أو يدوياً:

1. اذهب إلى: **Accounting > Chart of Accounts**
2. أنشئ الحسابات التالية تحت **Assets**:
   ```
   - Cash
     - Studio Cash (نقدية الاستوديو)
     - Studio Bank Account (حساب بنك الاستوديو)
   ```

3. أنشئ حساب إيرادات تحت **Income**:
   ```
   - Service Income
     - Photography Services Revenue (إيرادات خدمات التصوير)
   ```

### **الخطوة 2: إنشاء Cost Center**

1. اذهب إلى: **Accounting > Cost Center**
2. أنشئ:
   ```
   Name: Studio Revenue
   Parent Cost Center: Main - [Your Company]
   ```

### **الخطوة 3: إعداد General Settings**

1. اذهب إلى: **Re Studio Booking > General Settings**
2. أضف قسم "إعدادات محاسبية افتراضية":
   - Default Company
   - Default Cost Center
   - Default Debit Account
   - Default Income Account

### **الخطوة 4: تحديث Booking Invoice Defaults**

في DocType Customization:
```python
# في booking_invoice.py - دالة validate()
if not self.company:
    self.company = frappe.defaults.get_user_default('Company')

if not self.cost_center:
    # Get from General Settings or Company
    self.cost_center = frappe.db.get_single_value('General Settings', 'default_cost_center')

if not self.debit_to:
    self.debit_to = frappe.db.get_single_value('General Settings', 'default_cash_account')

if not self.income_account:
    self.income_account = frappe.db.get_single_value('General Settings', 'default_income_account')
```

---

## 📋 **سير العمل (Workflow):**

### **سيناريو كامل:**

```
1. إنشاء حجز (Booking)
   ├─ نوع الحجز: Service/Package
   ├─ المبلغ الإجمالي: 5000 ريال
   └─ العربون: 1500 ريال

2. إنشاء فاتورة من الحجز
   ├─ زر: "إنشاء فاتورة من الحجز"
   ├─ تُملأ الفاتورة تلقائياً:
   │  ├─ Total Amount: 5000
   │  ├─ Paid Amount: 1500 (العربون)
   │  ├─ Outstanding: 3500
   │  └─ Payment Table: صف واحد للعربون
   │
   └─ تُملأ الحقول المحاسبية تلقائياً:
      ├─ Company: [من الإعدادات]
      ├─ Cost Center: Studio Revenue
      ├─ Debit To: Studio Cash
      └─ Income Account: Photography Services Revenue

3. اعتماد الفاتورة (Submit)
   └─ ✅ يتم إنشاء Journal Entry تلقائياً:
      ├─ المدين: Studio Cash - 1500 ريال
      └─ الدائن: Photography Services Revenue - 1500 ريال

4. إضافة دفعة جديدة (500 ريال)
   ├─ يتم تحديث:
   │  ├─ Paid Amount: 2000
   │  ├─ Outstanding: 3000
   │  └─ Status: Partially Paid
   │
   └─ ⚠️ ملاحظة: القيد القديم يبقى كما هو (1500)
      للتحديث: إلغاء الفاتورة وإعادة اعتمادها

5. عرض في General Ledger
   اذهب إلى: Accounting > General Ledger
   ├─ فلتر: Account = Studio Cash
   ├─ فلتر: Cost Center = Studio Revenue
   └─ النتيجة: جميع المعاملات تظهر مع التفاصيل
```

---

## 🎯 **المزايا:**

✅ **تتبع مالي دقيق**: كل دفعة لها قيد محاسبي
✅ **تقارير شاملة**: General Ledger, Profit & Loss, Balance Sheet
✅ **ربط بمراكز التكلفة**: تحليل ربحية كل قسم
✅ **جرد يومي**: مطابقة الخزينة الفعلية مع النظام
✅ **تكامل مع ERPNext**: إذا كنت تستخدم ERPNext Accounting

---

## 📊 **التقارير المتاحة:**

### 1. **General Ledger** (دفتر الأستاذ العام)
```
Accounting > General Ledger
Filters:
- Account: Studio Cash
- Cost Center: Studio Revenue
- From Date: 2025-10-01
- To Date: 2025-10-31
```

### 2. **Profit and Loss Statement** (قائمة الدخل)
```
Accounting > Profit and Loss Statement
Filters:
- Company: Your Company
- Cost Center: Studio Revenue
- Period: October 2025
```

### 3. **Cash Flow Report** (تقرير التدفقات النقدية)
```
Accounting > Cash Flow
Filters:
- From Date: 2025-10-01
- To Date: 2025-10-31
```

---

## ⚠️ **ملاحظات مهمة:**

1. **القيد يُنشأ عند Submit فقط** - Draft لا ينشئ قيود
2. **إلغاء الفاتورة يلغي القيد** - تلقائياً
3. **تعديل الدفعات بعد Submit** - يحتاج إلغاء وإعادة اعتماد
4. **Multiple Payments** - إذا أضفت دفعة جديدة بعد Submit:
   - الخيار 1: إلغاء الفاتورة وإعادة اعتمادها
   - الخيار 2: إنشاء قيد يدوي للدفعة الجديدة

---

## 🔄 **التطوير المستقبلي (اختياري):**

### **1. إنشاء قيد لكل دفعة منفصلة:**
```python
def on_update_after_submit(self):
    """إنشاء قيود للدفعات الجديدة"""
    # Logic to create JE for new payments only
```

### **2. ربط مع POS Shift:**
```python
def add_to_active_shift(self, payment_amount):
    """إضافة الدفعة للوردية المفتوحة"""
    active_shift = frappe.get_value('Cash Shift', 
        {'status': 'Open', 'employee': frappe.session.user}, 
        'name')
    if active_shift:
        # Add transaction to shift
```

### **3. تقرير مخصص للإيرادات اليومية:**
```javascript
// Daily Revenue Report
frappe.query_reports["Daily Studio Revenue"] = {
    filters: [
        {fieldname: "date", label: "Date", fieldtype: "Date"},
        {fieldname: "cost_center", label: "Cost Center", fieldtype: "Link", options: "Cost Center"}
    ]
}
```

---

## 🚀 **الخطوات التالية:**

الآن لديك تكامل محاسبي كامل! يمكنك:
1. ✅ اختبار إنشاء فاتورة ← Submit ← التحقق من Journal Entry
2. ✅ فحص General Ledger للتأكد من ظهور القيود
3. 🔄 إعداد نظام الورديات (Cash Shift) - الخطوة 3 من طلبك
4. 📊 إنشاء تقارير مخصصة حسب احتياجاتك

---

**تم إنشاؤه بواسطة:** GitHub Copilot AI Assistant  
**التاريخ:** 27 أكتوبر 2025  
**الإصدار:** 1.0
