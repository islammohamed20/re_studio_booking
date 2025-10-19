# 💰 إضافة حقل "سعر الكمية" في خدمات الباقة - Package Service Unit Price

## 🎯 المشكلة

بعض الخدمات داخل الباقة تُحسب **بالكمية** وليس **بالمدة**، مثل:
- **Reels**: 10 ريلز
- **Photo**: 50 صورة
- **Promo**: 3 فيديوهات ترويجية

المشكلة السابقة:
- ❌ لم يكن هناك حقل لتحديد **سعر الوحدة/الكمية**
- ❌ الحساب كان دائماً: `amount = price × quantity` بغض النظر عن نوع الخدمة
- ❌ لم يكن هناك تمييز بين الخدمات الزمنية (مدة) والخدمات الكمية (Reels, Photo)

---

## ✅ الحل المطبق

### 1️⃣ إضافة حقل "نوع الوحدة" (`type_unit`)

تم إضافة حقل **نوع الوحدة** في `Package Service` يجلب تلقائياً من `Service`:

```json
{
  "fetch_from": "service.type_unit",
  "fieldname": "type_unit",
  "fieldtype": "Data",
  "label": "نوع الوحدة",
  "read_only": 1
}
```

**القيم الممكنة:**
- `مدة` (Duration) - خدمات زمنية
- `Reels`, `Photo`, `Promo`, `Photo Session`, `Series`, `Podcast Ep`, `أخرى`

### 2️⃣ إضافة حقل "سعر الكمية" (`unit_price`)

```json
{
  "fieldname": "unit_price",
  "fieldtype": "Currency",
  "in_list_view": 1,
  "label": "سعر الكمية",
  "options": "SAR",
  "description": "السعر لكل وحدة/كمية (للخدمات التي تُحسب بالكمية مثل Reels، Photos)"
}
```

### 3️⃣ منطق الحساب الجديد

```python
def calculate_amount(self):
    # للخدمات الزمنية (type_unit = "مدة")
    if self.type_unit == 'مدة':
        self.amount = self.package_price  # ثابت، لا يتأثر بالكمية
    else:
        # للخدمات الكمية
        price_per_unit = self.unit_price or self.package_price or self.base_price
        self.amount = price_per_unit × self.quantity
```

---

## 📊 مثال عملي

| الخدمة | نوع الوحدة | الكمية | سعر الكمية | المبلغ | الحساب |
|--------|------------|--------|------------|--------|---------|
| Full Location | مدة | 2 | - | 500 | ثابت ✅ |
| Reels | Reels | 10 | 50 | 500 | 50 × 10 ✅ |
| Photo | Photo | 50 | 10 | 500 | 10 × 50 ✅ |

---

## 🧪 الاختبار

1. افتح **Package**
2. أضف خدمة كمية (مثل Reels)
3. أدخل الكمية = 10
4. أدخل سعر الكمية = 50
5. ✅ المبلغ = 500 SAR

---

## 🎉 النتيجة

- ✅ إضافة حقل "نوع الوحدة"
- ✅ إضافة حقل "سعر الكمية"
- ✅ حساب صحيح للخدمات الكمية والزمنية
- ✅ تطبيق التغييرات والاختبار

الميزة جاهزة! 🚀
