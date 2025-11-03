# AMA-IMPACT Default User Credentials

**⚠️ IMPORTANT: Change these passwords in production!**

## 🔐 Test User Accounts

### 👨‍💼 Admin (Full System Access)
- **Email:** `admin@ama-impact.com`
- **Password:** `Admin123!`
- **Access:** All contracts, all users, system settings

### 👔 HR (Multi-Contract Access)
- **Email:** `hr@ama-impact.com`
- **Password:** `HR123!`
- **Access:** ASSESS-2025 contract, generate reports
- **Contract:** ASSESS-2025

### 📊 Program Manager (Contract-Wide)
- **Email:** `pm@ama-impact.com`
- **Password:** `PM123!`
- **Access:** All users in ASSESS-2025 contract
- **Contract:** ASSESS-2025

### 👨‍💻 Tech Lead (Team-Level)
- **Email:** `techlead@ama-impact.com`
- **Password:** `Tech123!`
- **Access:** Own data + direct/indirect reports
- **Contract:** ASSESS-2025
- **Reports To:** Program Manager

### 👤 Staff (Self-Only)
- **Email:** `staff@ama-impact.com`
- **Password:** `Staff123!`
- **Access:** Own visa records only
- **Contract:** ASSESS-2025
- **Reports To:** Tech Lead

---

## 📊 Sample Data Included

### Contracts
- ASSESS-2025 (Active)
- RESESS-2025 (Active)

### Visa Types (12 types)
- H1B - H-1B Specialty Occupation
- L1 - L-1 Intracompany Transfer
- O1 - O-1 Extraordinary Ability
- TN - TN NAFTA Professional
- EB1A - EB-1A Extraordinary Ability
- EB1B - EB-1B Outstanding Researcher
- EB2 - EB-2 Advanced Degree
- EB2NIW - EB-2 National Interest Waiver
- PERM - PERM Labor Certification
- OPT - Optional Practical Training
- EAD - Employment Authorization Document
- GREEN_CARD - Permanent Resident Card

---

## 🧪 Quick Test

1. Start backend: `cd backend && ./start.sh`
2. Open: http://localhost:8000/docs
3. Click **Authorize** button
4. Use **POST /api/v1/auth/login** with admin credentials
5. Copy the `access_token` from response
6. Click **Authorize** again and enter: `Bearer <access_token>`
7. Now test any endpoint!

---

## 🔄 Reset Database

To reset the database and recreate all sample data:

```bash
cd backend
./reset_db.sh
```

**Warning:** This will delete ALL existing data!
