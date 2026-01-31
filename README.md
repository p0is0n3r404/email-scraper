# 📧 Email Scraper Pro v3.0

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Platform-Kali%20Linux-red?style=for-the-badge&logo=linux" alt="Platform">
</p>

<p align="center">
  <b>Advanced Email Harvesting Toolkit for Penetration Testing & OSINT</b>
</p>

---

## 🚀 Features

| Tool                             | Description                                                              |
| -------------------------------- | ------------------------------------------------------------------------ |
| **email_master.py**              | 🔧 All-in-one master tool - runs all techniques together                 |
| **email_scraper.py**             | Multi-threaded web crawler with proxy, subdomain, and validation support |
| **email_scraper_interactive.py** | Menu-based interactive interface                                         |
| **google_dorking.py**            | Passive email collection via search engines                              |
| **wayback_emails.py**            | Historical email harvesting from Wayback Machine                         |
| **hunter_api.py**                | Hunter.io API integration for professional email finding                 |
| **email_permutator.py**          | Generate possible emails from names                                      |
| **breach_checker.py**            | Check emails against breach databases (HIBP)                             |
| **html_report.py**               | Generate beautiful HTML reports from JSON results                        |

---

## 📦 Installation

```bash
# Clone or download the toolkit
cd email-scraper-pro

# Install dependencies
pip3 install -r requirements.txt

# Make scripts executable (Linux/macOS)
chmod +x *.py
```

### Dependencies

- `requests` - HTTP library
- `beautifulsoup4` - HTML parsing
- `lxml` - Fast XML/HTML parser
- `dnspython` - DNS resolution for email validation
- `PySocks` - SOCKS proxy support (for Tor)

---

## 📖 Usage

### 1. Main Email Scraper (CLI)

```bash
# Basic scan
python3 email_scraper.py -u https://example.com

# Advanced scan with all features
python3 email_scraper.py -u https://example.com \
    -l 500 \
    -t 10 \
    --subdomains \
    --robots \
    --validate \
    -o results.json \
    --format json \
    -v

# Scan through Tor
python3 email_scraper.py -u https://example.com \
    --proxy socks5://127.0.0.1:9050 \
    --delay 2
```

#### CLI Options

| Option              | Description                  | Default      |
| ------------------- | ---------------------------- | ------------ |
| `-u, --url`         | Target URL to scan           | **Required** |
| `-l, --limit`       | Max URLs to crawl            | 100          |
| `-t, --threads`     | Concurrent threads           | 5            |
| `--timeout`         | Request timeout (sec)        | 10           |
| `-o, --output`      | Output file path             | -            |
| `--format`          | Output format (txt/json/csv) | txt          |
| `-d, --domain-only` | Only target domain emails    | -            |
| `--delay`           | Delay between requests       | 0            |
| `--proxy`           | Proxy URL                    | -            |
| `--robots`          | Respect robots.txt           | -            |
| `--sitemap`         | Parse sitemap.xml            | -            |
| `--subdomains`      | Scan for subdomains          | -            |
| `--validate`        | SMTP email validation        | -            |
| `-v, --verbose`     | Verbose output               | -            |

---

### 2. Interactive Mode

```bash
python3 email_scraper_interactive.py
```

Features:

- 🔍 Quick Scan - Fast scan with defaults
- ⚙️ Advanced Scan - Full configuration
- 🌐 Subdomain Discovery - Find subdomains first
- 🔐 Proxy Scan - Route through proxy
- 📊 View Results - Browse previous scans
- 📖 Help - Usage guide

---

### 3. Google Dorking (Passive)

```bash
# Using DuckDuckGo (recommended)
python3 google_dorking.py -d example.com

# Multiple search engines
python3 google_dorking.py -d example.com -e bing,duckduckgo,ask

# Save results
python3 google_dorking.py -d example.com -o dorking_results.txt
```

This is a **passive reconnaissance** technique - no direct connection to target.

---

### 4. Wayback Machine Harvester

```bash
# Basic historical scan
python3 wayback_emails.py -d example.com

# Filter by years
python3 wayback_emails.py -d example.com --years 2020,2021,2022

# More snapshots with parallel threads
python3 wayback_emails.py -d example.com -l 100 -t 10

# Save as JSON
python3 wayback_emails.py -d example.com -o historical.json --format json
```

Great for finding:

- Removed email addresses
- Old contact information
- Historical data

---

### 5. HTML Report Generator

```bash
# Generate HTML report from JSON results
python3 html_report.py results.json

# Custom output filename
python3 html_report.py results.json custom_report.html
```

Creates beautiful, interactive HTML reports with:

- Statistics dashboard
- Emails grouped by domain
- Validation status
- Modern glassmorphism design

---

## 🔧 Advanced Features

### Subdomain Discovery

Automatically discovers 100+ common subdomains before crawling:

```bash
python3 email_scraper.py -u https://example.com --subdomains
```

### Email Validation (SMTP)

Validates collected emails via MX record lookup:

```bash
python3 email_scraper.py -u https://example.com --validate
```

### Proxy Support

Route traffic through HTTP or SOCKS5 proxy:

```bash
# HTTP proxy
python3 email_scraper.py -u https://example.com --proxy http://127.0.0.1:8080

# SOCKS5 proxy
python3 email_scraper.py -u https://example.com --proxy socks5://127.0.0.1:1080

# Tor network
python3 email_scraper.py -u https://example.com --proxy socks5://127.0.0.1:9050
```

### robots.txt Compliance

Respect website's crawling rules:

```bash
python3 email_scraper.py -u https://example.com --robots --sitemap
```

---

## 📊 Output Formats

### TXT (Plain Text)

```
# Email Scraper Results
# Target: https://example.com
# Total: 15

admin@example.com    # Source: https://example.com/contact
info@example.com     # Source: https://example.com/about
```

### JSON (Structured)

```json
{
  "target": "https://example.com",
  "scan_date": "2024-01-15T10:30:00",
  "total_emails": 15,
  "emails": [
    {
      "email": "admin@example.com",
      "domain": "example.com",
      "source": "https://example.com/contact",
      "valid": true
    }
  ]
}
```

### CSV (Spreadsheet)

```csv
Email,Domain,Source,Valid
admin@example.com,example.com,https://example.com/contact,Yes
info@example.com,example.com,https://example.com/about,Unknown
```

---

## ⚠️ Legal Disclaimer

This toolkit is intended for **authorized security testing and educational purposes only**.

- ✅ Always obtain proper authorization before scanning
- ✅ Respect website terms of service
- ✅ Use responsibly and ethically
- ❌ Do not use for spamming or malicious purposes
- ❌ Do not violate privacy laws (GDPR, etc.)

**The authors are not responsible for misuse of this tool.**

---

## 📚 Part of Ethical Hacking Bootcamp

This toolkit is developed as part of the **Complete Ethical Hacking Bootcamp** course materials.

**Module:** Reconnaissance & Information Gathering - Part 02

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest features
- Submit pull requests

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

<p align="center">
  <b>Happy Hacking! 🔐</b>
</p>
