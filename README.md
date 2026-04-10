# 🛡️ SSL Shield — Website SSL Certificate Validator

A full-stack SSL certificate analysis and vulnerability scanning tool with a modern dark UI.

![SSL Shield](https://img.shields.io/badge/SSL-Shield-22c55e?style=for-the-badge&logo=shield&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0+-black?style=for-the-badge&logo=flask)

---

## 📸 Screenshots

| Home Page | Scan Page | Results Page |
|-----------|-----------|--------------|
| Enter any domain | Live scan animation | Full certificate details |

---

## ✨ Features

- 🔍 **Real-time SSL Analysis** — Fetches live certificate data from any domain
- 🏆 **Security Grading** — Grades certificates from A+ to F based on multiple factors
- 📊 **Security Score** — 0–100 score with detailed breakdown
- 🛡️ **Vulnerability Scanning** — Checks TLS protocols, expiry, domain match, issuer trust
- 📋 **Certificate Details** — Health, Grade, Expiry, Issuer, Issue Date, Type, SANs
- 🔐 **Protocol Check** — Detects insecure TLS 1.0 / 1.1 usage
- 💡 **Interactive Modals** — Click any card to see detailed scan steps and findings
- 🌙 **Dark Terminal UI** — Clean dark theme with green accents

---

## 🗂️ Project Structure

```
SSL-Shield/
├── app.py           # Flask backend — SSL analysis logic
├── ssl.html         # Home page — domain input
├── process.html     # Scan & results page
├── ssl.css          # All styles
└── ssl.js           # Frontend JS (redirect logic)
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/mbchiranth/SSL-Website-Certificate-Validator.git
cd SSL-Website-Certificate-Validator
```

**2. Install dependencies**
```bash
pip install flask flask-cors
```

**3. Start the Flask backend**
```bash
python app.py
```
You should see:
```
* Running on http://127.0.0.1:5000
```

**4. Serve the frontend**

Open a second terminal in the same folder:
```bash
python -m http.server 3000
```

**5. Open in browser**
```
http://localhost:3000/ssl.html
```

> ⚠️ Always open via `http://localhost:3000` — NOT by double-clicking the file. Direct file access blocks backend calls.

---

## 🔬 How It Works

```
User enters domain
       ↓
ssl.html → redirects to process.html
       ↓
Scan animation plays (5 steps)
       ↓
process.html → POST /analyze → app.py
       ↓
Flask fetches real SSL certificate
       ↓
Calculates grade, score, vulnerabilities
       ↓
Results displayed in cards
       ↓
Click any card → detailed modal with findings
```

---

## 📊 Security Scoring

| Factor | Impact |
|--------|--------|
| Certificate expiry > 180 days | ✅ No penalty |
| Certificate expiry < 180 days | -15 points |
| Certificate expiry < 30 days | -30 points |
| Domain mismatch | 0 (Critical fail) |
| Untrusted issuer | -20 points |
| Insecure protocols (TLS 1.0/1.1) | -20 points |
| DV certificate | -5 points |
| EV certificate | +5 points |

### Grade Scale
| Score | Grade |
|-------|-------|
| 90–100 | A+ |
| 80–89 | A |
| 65–79 | B |
| 50–64 | C |
| Below 50 | F |

---

## 🌐 Trusted Certificate Authorities

The following CAs are recognized as trusted:
- DigiCert
- GlobalSign
- Let's Encrypt
- Sectigo
- GoDaddy
- Amazon
- Google Trust Services
- Cloudflare

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask, Flask-CORS |
| SSL Analysis | Python `ssl`, `socket` modules |
| Frontend | HTML5, CSS3, JavaScript |
| Fonts | Inter, JetBrains Mono |
| Styling | Custom CSS with CSS variables |

---

## 📡 API Reference

### `POST /analyze`

Analyzes the SSL certificate for a given domain.

**Request Body:**
```json
{
  "domain": "google.com"
}
```

**Response:**
```json
{
  "domain": "google.com",
  "certificate_health": "Active",
  "certificate_grade": "A",
  "expiry_date": "2026-04-23",
  "issuer": "Google Trust Services",
  "issued_on": "2026-01-23",
  "cert_type": "OV",
  "valid_sans": ["*.google.com", "google.com"],
  "security_score": 85,
  "days_remaining": 180,
  "trusted_issuer": true,
  "domain_match": true,
  "vulnerabilities": [...],
  "score_breakdown": [...]
}
```

---

## ⚙️ Certificate Types

| Type | Description |
|------|-------------|
| **DV** | Domain Validated — verifies domain ownership only |
| **OV** | Organization Validated — verifies domain + organization |
| **EV** | Extended Validated — highest trust, full org verification |

---

## 🤝 Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👨‍💻 Author

**mbchiranth** — [GitHub](https://github.com/mbchiranth)

---

> Built with 🛡️ to make SSL security analysis accessible to everyone.
