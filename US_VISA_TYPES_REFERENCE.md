# 🇺🇸 U.S. Visa Case Groups and Associated Visa Types

This table maps each **Visa Case Group** to the corresponding **Visa Types / Petitions / Filings** and **Dependent or Derivative** applications.
It's designed for workflow or milestone automation systems.

---

## 🧩 Employment-Based Immigrant Visas (Green Card)

### **EB1** (Priority Workers)
- **Visa Types:**
  - I-140 (Immigrant Petition)
  - I-485 (Adjustment of Status) or DS-260 (Consular Processing)
  - EAD (I-765 - Employment Authorization Document)
  - Advance Parole (I-131 - Travel Document)
- **Dependents:**
  - I-485 (derivative spouse/children)
  - EAD / AP (for dependents)

### **EB2** (Advanced Degree or Exceptional Ability)
- **Visa Types:**
  - PERM (ETA-9089 Labor Certification)
  - I-140 (Immigrant Petition)
  - I-485 / DS-260
  - EAD (I-765)
  - Advance Parole (I-131)
- **Dependents:**
  - I-485 (derivative spouse/children)
  - EAD / AP

### **EB2-NIW** (National Interest Waiver)
- **Visa Types:**
  - I-140 (Self-sponsored, no PERM required)
  - I-485 / DS-260
  - EAD / AP
- **Dependents:**
  - I-485 (derivative)
  - EAD / AP

### **EB3** (Skilled Workers, Professionals, Other Workers)
- **Visa Types:**
  - PERM (ETA-9089 Labor Certification)
  - I-140
  - I-485 / DS-260
  - EAD / AP
- **Dependents:**
  - I-485 (derivative)
  - EAD / AP

### **EB4** (Special Immigrants) / **EB5** (Investors)
- **Visa Types:**
  - I-360 (EB4) / I-526 or I-526E (EB5)
  - I-485 / DS-260
  - EAD / AP
- **Dependents:**
  - I-485 (derivative)
  - EAD / AP

---

## 🧳 Nonimmigrant Work Visas

### **H1B** (Specialty Occupation)
- **Visa Types:**
  - LCA (Labor Condition Application - filed with DOL)
  - I-129 (Petition for Nonimmigrant Worker)
  - I-797 (Approval Notice)
  - Visa Stamping (at U.S. Embassy/Consulate)
  - I-94 (Admission Record)
- **Dependents:**
  - H4 (I-539 - Change/Extension of Status)
  - H4 EAD (I-765)

### **TN** (USMCA/NAFTA Professionals)
- **Visa Types:**
  - TN Application (filed at Port of Entry or via I-129)
  - I-94 (Admission Record)
  - I-94 Update (for conversions/extensions)
- **Dependents:**
  - TD (I-539 - Change/Extension of Status)

### **L1** (Intracompany Transferee)
- **Visa Types:**
  - I-129 (Petition)
  - I-797 (Approval Notice)
  - Visa Stamping
  - I-94
- **Dependents:**
  - L2 (I-539)
  - L2 EAD (I-765)

### **O1** (Extraordinary Ability)
- **Visa Types:**
  - I-129 (Petition)
  - I-797 (Approval Notice)
  - Visa Stamping
  - I-94
- **Dependents:**
  - O3 (I-539)

### **E1 / E2** (Treaty Trader / Investor)
- **Visa Types:**
  - DS-156E (Nonimmigrant Treaty Application)
  - I-129 (if filed in U.S.)
  - I-797 / I-94
- **Dependents:**
  - E2 Dependent (I-539)
  - EAD (I-765)

### **J1** (Exchange Visitor)
- **Visa Types:**
  - DS-2019 (Certificate of Eligibility)
  - I-94 (Admission Record)
  - Optional: I-612 (212(e) waiver)
- **Dependents:**
  - J2 (I-539)
  - J2 EAD (I-765)

### **F1** (Student)
- **Visa Types:**
  - I-20 (Certificate of Eligibility)
  - I-94 (Admission Record)
  - Optional: I-765 (OPT / STEM OPT)
- **Dependents:**
  - F2 (I-539)

### **M1** (Vocational Student)
- **Visa Types:**
  - I-20M-N (Certificate of Eligibility)
  - I-94 (Admission Record)
  - Optional: I-765 (for practical training)
- **Dependents:**
  - M2 (I-539)

---

## 💍 Family & Marriage-Based Immigrant Visas

### **Marriage-Based** (U.S. Citizen or LPR Spouse)
- **Visa Types:**
  - I-130 (Petition for Alien Relative)
  - I-485 (Adjustment of Status) or DS-260 (Consular Processing)
  - I-864 (Affidavit of Support)
  - I-693 (Medical Exam)
  - EAD (I-765)
  - Advance Parole (I-131)
- **Dependents:**
  - Stepchildren (derivative beneficiaries, if applicable)

### **K1** (Fiancé(e) Visa)
- **Visa Types:**
  - I-129F (Petition for Alien Fiancé(e))
  - DS-160 (Nonimmigrant Visa Application)
  - I-485 (after marriage in U.S.)
  - EAD (I-765)
  - AP (I-131)
- **Dependents:**
  - K2 (children of K1)

---

## 🎓 OPT / STEM OPT Extensions

### **OPT** (Optional Practical Training - Post-Completion)
- **Visa Types:**
  - I-765 (EAD application)
  - I-20 (endorsed for OPT)
  - I-983 (Training Plan – STEM OPT only)
- **Dependents:**
  - F2 (I-539)

---

## 🕊️ Other Common Visas

### **B1/B2** (Visitor / Business)
- **Visa Types:**
  - DS-160 (Nonimmigrant Visa Application)
  - I-94 (Admission Record)
- **Dependents:**
  - None (issued individually)

### **R1** (Religious Worker)
- **Visa Types:**
  - I-129 (Petition)
  - I-797 / I-94
- **Dependents:**
  - R2 (I-539)

### **U / T / Asylum** (Humanitarian)
- **Visa Types:**
  - U-1 (U Visa for Crime Victims)
  - T-1 (T Visa for Trafficking Victims)
  - I-589 (Asylum Application)
  - EAD (I-765)
  - Adjustment to Permanent Resident (I-485)
- **Dependents:**
  - U-2 / T-2 / derivative asylum applicants

---

## 📋 Implementation Notes for AMA-IMPACT

### Data Model Structure

**CaseGroup** represents the **immigration pathway**:
- EB2_NIW, EB2_PERM, EB3_PERM, H1B_INITIAL, TN, etc.

**Petition** (formerly VisaApplication) represents **individual forms**:
- I-140, I-485, I-129, PERM, I-765, I-131, etc.

### Relationship Mapping

```
CaseGroup (EB2-NIW)
├── Petition: I-140 (principal beneficiary)
├── Petition: I-485 (principal beneficiary)
├── Petition: I-765 (principal - EAD)
├── Petition: I-131 (principal - Advance Parole)
├── Petition: I-485 (derivative - spouse)
├── Petition: I-765 (derivative - spouse EAD)
└── Petition: I-131 (derivative - spouse AP)
```

### Special Cases

**TN Visas:**
- Can be filed at Port of Entry (POE) or via I-129
- May require I-94 updates for conversions
- No traditional petition filing in many cases

**Combo Documents:**
- EAD/AP combo card (I-765/I-131 combined)
- Can be tracked as single petition or separate petitions

**Visa Stamping:**
- Not a petition but an administrative step
- May be tracked as milestone rather than petition

---

## 🔄 Migration Path for Current Data

### Current Schema Issues
1. `VisaTypeEnum` mixes pathways (H1B) with forms (I-140)
2. `CaseType` includes PERM (which is a step, not pathway)
3. Three redundant fields: `visa_type`, `visa_type_id`, `petition_type`

### Proposed Schema
```python
# CaseGroup
pathway_type = Enum(EB2_NIW, EB2_PERM, EB3_PERM, H1B_INITIAL, etc.)

# Petition
petition_type = Enum(I140, I485, I129, PERM, I765, I131, etc.)
dependent_id = FK (nullable - links to Dependent table)
```

### Seed Data Requirements
Each realistic case should include:
- **EB2-NIW**: I-140 + I-485 + I-765 + I-131 (4 petitions for principal)
- **H1B**: LCA (tracked?) + I-129 + Visa Stamping (milestone?) + I-94 (milestone?)
- **TN**: TN Application (POE or I-129) + I-94
- **Dependents**: Derivative I-485, I-765, I-131 as applicable

---

## 📊 Reporting Implications

All reporting queries currently use `visa_applications` table. After refactor:
- Update to `petitions` table
- Filter by `petition_type` instead of `visa_type`
- Department stats need to aggregate petitions by case group
- User activity reports need to track petition creation/updates

---

## 🔍 Audit Logging Implications

Current audit logs reference:
- `resource_type = "visa_application"`
- `resource_id = visa_application.id`

After refactor:
- Update to `resource_type = "petition"`
- Ensure backward compatibility for historical audit records
- May need data migration script for audit logs

---

## ✅ Configuration Strategy

### Company-Specific Pipeline Overrides

Store in YAML configuration files:
```yaml
# config/companies/assess.yaml
company_slug: assess
case_group_pipelines:
  EB2_NIW:
    stages:
      - milestone_type: CASE_OPENED
        weight: 5
        custom_field: true
      - milestone_type: STRATEGY_MEETING
        weight: 10

petition_pipelines:
  I140:
    stages:
      - milestone_type: DOCUMENTS_REQUESTED
        weight: 20
        company_specific_note: "Requires 3 reference letters"
```

Load and merge with defaults at runtime.

---

This reference document should guide the complete refactor implementation.
