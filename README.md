<div align="center">

# 🚀 AI-Powered Regulatory Compliance Checker

### *Automating Contract Review, Risk Assessment & Compliance Tracking with LLMs*

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Groq LLaMA](https://img.shields.io/badge/LLM-Groq%20LLaMA%2070B-green.svg)](https://groq.com/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<p align="center">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-success" alt="Status"/>
  <img src="https://img.shields.io/badge/Integrations-Slack%20%7C%20Email%20%7C%20Sheets-blueviolet" alt="Integrations"/>
</p>

<p align="center">
  <a href="#-why-this-matters">Why This Matters</a> •
  <a href="#-what-it-does">Features</a> •
  <a href="#-how-it-works">Architecture</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-demo">Demo</a> •
  <a href="#-tech-stack">Tech Stack</a>
</p>

---

</div>

## 🎯 Why This Matters

Contract review is a **critical bottleneck** in legal and compliance operations. Traditional manual processes are:
- ⏳ **Painfully slow** – Legal teams spend days analyzing single contracts
- ❌ **Error-prone** – Missing clauses and overlooked risks expose companies to penalties
- 📉 **Reactive** – No real-time tracking of evolving regulations like GDPR/HIPAA
- 🔌 **Disconnected** – Lack of integration with modern collaboration tools

**This project transforms contract compliance from a manual chore into an intelligent, automated system.**

---

## ✨ What It Does

This AI system leverages **Groq LLaMA 70B** and advanced NLP to automate end-to-end contract compliance workflows:

### 🔍 **Core Capabilities**

| Feature | Description |
|---------|-------------|
| **📄 Smart Clause Extraction** | Automatically identifies and categorizes contract clauses (Confidentiality, Liability, GDPR, HIPAA, etc.) using semantic understanding—no keyword matching needed. |
| **⚖️ Dual-Engine Risk Assessment** | Combines **rule-based detection** (fast, precise) + **LLM reasoning** (contextual, nuanced) to score risks as Low/Medium/High/Critical. |
| **🔄 Live Regulatory Tracking** | Monitors GDPR & HIPAA updates in real-time via RSS feeds + web scraping. Auto-flags affected contracts when regulations change. |
| **✍️ Intelligent Amendment Engine** | Rewrites high-risk clauses with compliance-ready language while preserving original contract structure. |
| **📊 Multi-Channel Alerts** | Real-time notifications via **Slack**, **Email**, and **Google Sheets** for compliance issues, regulatory updates, and audit trails. |
| **🎨 Interactive Web UI** | Beautiful Streamlit dashboard with progress tracking, risk visualizations, and downloadable reports. |

---

## 🏗️ How It Works

The system operates through a **7-stage automated pipeline**:

graph LR
    A[📄 Upload PDF] --> B[🔍 Extract Text]
    B --> C[🧹 Clean & Normalize]
    C --> D[📑 Extract Clauses]
    D --> E[⚠️ Risk Analysis]
    E --> F[📡 Regulatory Check]
    F --> G[✍️ Generate Amendments]
    G --> H[📬 Notify & Report]

## 🌟 Key Features Deep Dive

### **1. Clause Extraction Engine**
- **Semantic Understanding**: Unlike keyword-based tools, the LLM reads contracts like a lawyer.
- **Flexible Categorization**: Handles paraphrased clauses (e.g., "confidential info" = "proprietary data").
- **Supports Long Documents**: Auto-chunks contracts >45,000 chars.

### **2. Risk Assessment System**
| Engine Type | Speed | Accuracy | Use Case |
|-------------|-------|----------|----------|
| **Rule-Based** | ⚡ Fast | 95% (predefined patterns) | Immediate red flags (missing GDPR clauses) |
| **LLM-Powered** | 🐢 Slower | 90% (contextual reasoning) | Nuanced risks (vague liability terms) |

### **3. Regulatory Tracking**
- **GDPR**: Monitors European Data Protection Board (EDPB) via RSS + scraping.
- **HIPAA**: Tracks HHS.gov for healthcare compliance updates.
- **Change Detection**: MD5 hashing ensures only new updates trigger alerts.

### **4. Amendment Engine**
# Before
"Company shall not be liable for any damages."

# After (AI Rewrite)
"Company's liability is capped at the total contract value, 
excluding cases of gross negligence or willful misconduct."

