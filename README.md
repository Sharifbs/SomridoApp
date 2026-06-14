# 📊 Somrido NGO & Premium Accounts Management Suite

SomridoApp is a comprehensive financial and administrative management application designed for NGOs and premium asset management. Built using Python, this ecosystem integrates both a high-end desktop dashboard for administrators and a mobile-friendly accounting portal.

---

## 🚀 Core Features

### 1. 🔐 Premium Login Portal (Desktop)
* **Secure Gatekeeper:** Only accessible via verified admin credentials.
* **Credentials:** Username: `somrido` | Password: `admin321`
* **Interactive Controls:** Toggle password visibility using the built-in show/hide (👁️) feature.
* **Commercial UX:** Embedded mock features for account recovery (Forgot Password) and registration (Sign Up).

### 2. 💼 Financial Ledger & Asset Monitoring (`desktop_app.py`)
* **Multi-Channel Tracking:** Real-time liquidity reporting across Cash, bKash, and Bank repositories.
* **Automated Capitalization:** Dynamic calculation formulas for liquid capital balance computation:
  `Net Liquid Capital = Final Cash + Final bKash + Final Bank`
* **Database Management:** Backed by robust localized SQLite database structures (`somrido_premium.db` and `somrido_ngo.db`).

### 3. ✉️ Subscription Due Monitor & Mail Automation
* **Overdue Matrix:** Automatically scans active member logs to track monthly payment defaults.
* **Smart Thresholding:** Switches notice labels dynamically between `⚠️ PENDING PAYMENT` and `🚨 CRITICAL OVERDUE` based on the 15th-of-the-month margin.
* **Asynchronous SMTP Engine:** Dispatches personalized multi-part MIME text email alerts to overdue members on a separate background thread without locking up the UI.
* **Custom Routing Panel:** Complete secure graphical configuration panel for SMTP routing credentials (`smtp.gmail.com`, custom app tokens, port specifications).

### 4. 📱 Mobile Accounting Module (`main.py`)
* **Framework:** Powered by Kivy & KivyMD for seamless light-weight mobile UI compliance.
* **Instant Calculation:** Computes admission revenue matrices alongside operational expense deductions on-the-fly.

---

## 🛠️ Tech Stack & Architecture

* **Frontend GUI:** CustomTkinter (Desktop Theme Mode: Dark), Kivy & KivyMD (Mobile UI Theme Mode: Light)
* **Backend Engines:** Python 3.13+, SQLite3 Database Driver
* **Networking / Protocols:** Smtplib (TLS/SSL Security Handshakes), Email MIME, Multithreading Arch

---

## 💻 Local Installation & Setup Guide

To run this desktop suite locally on your computer, ensure you have Python installed, then execute the following steps in your terminal:

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/Sharifbs/SomridoApp.git](https://github.com/Sharifbs/SomridoApp.git)
   cd SomridoApp
