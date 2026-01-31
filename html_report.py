#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML Report Generator for Email Scraper Pro
Generates beautiful HTML reports from scan results.
"""

import json
import os
from datetime import datetime


def generate_html_report(json_file, output_file=None):
    """JSON sonuçlarından HTML rapor oluştur"""
    
    # JSON yükle
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    if output_file is None:
        output_file = json_file.replace('.json', '_report.html')
    
    # Domain'e göre grupla
    emails_by_domain = {}
    for email_data in data.get('emails', []):
        email = email_data.get('email', '')
        domain = email_data.get('domain', email.split('@')[1] if '@' in email else 'unknown')
        
        if domain not in emails_by_domain:
            emails_by_domain[domain] = []
        emails_by_domain[domain].append(email_data)
    
    # HTML oluştur
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Scraper Report - {data.get('target', 'Unknown')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e0e0e0;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            padding: 40px 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            margin-bottom: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            background: linear-gradient(45deg, #00d9ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            color: #888;
            font-size: 1.1em;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(0, 217, 255, 0.2);
        }}
        
        .stat-card .icon {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #00d9ff;
        }}
        
        .stat-card .label {{
            color: #888;
            margin-top: 5px;
        }}
        
        .section {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
        }}
        
        .section h2 {{
            color: #00ff88;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .domain-group {{
            margin-bottom: 25px;
        }}
        
        .domain-header {{
            background: rgba(0, 217, 255, 0.1);
            padding: 12px 20px;
            border-radius: 10px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .domain-name {{
            font-weight: bold;
            color: #00d9ff;
        }}
        
        .domain-count {{
            background: #00d9ff;
            color: #1a1a2e;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        
        .email-list {{
            list-style: none;
            padding-left: 20px;
        }}
        
        .email-item {{
            padding: 10px 15px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 8px;
            margin-bottom: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.2s;
        }}
        
        .email-item:hover {{
            background: rgba(255, 255, 255, 0.05);
        }}
        
        .email-address {{
            font-family: 'Courier New', monospace;
        }}
        
        .email-status {{
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.8em;
        }}
        
        .status-valid {{
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
        }}
        
        .status-invalid {{
            background: rgba(255, 0, 0, 0.2);
            color: #ff4444;
        }}
        
        .status-unknown {{
            background: rgba(255, 200, 0, 0.2);
            color: #ffc800;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: #666;
        }}
        
        .footer a {{
            color: #00d9ff;
            text-decoration: none;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .stats {{
                grid-template-columns: 1fr 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📧 Email Scraper Report</h1>
            <p class="subtitle">Scan Results for {data.get('target', 'Unknown Target')}</p>
            <p class="subtitle" style="margin-top: 10px; font-size: 0.9em;">
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
                Scan Date: {data.get('scan_date', 'Unknown')[:19].replace('T', ' ')}
            </p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="icon">📧</div>
                <div class="value">{data.get('total_emails', len(data.get('emails', [])))}</div>
                <div class="label">Total Emails</div>
            </div>
            <div class="stat-card">
                <div class="icon">🌐</div>
                <div class="value">{len(emails_by_domain)}</div>
                <div class="label">Unique Domains</div>
            </div>
            <div class="stat-card">
                <div class="icon">✅</div>
                <div class="value">{len([e for e in data.get('emails', []) if e.get('valid') == True])}</div>
                <div class="label">Validated</div>
            </div>
            <div class="stat-card">
                <div class="icon">🎯</div>
                <div class="value">{data.get('target', 'N/A').replace('https://', '').replace('http://', '').split('/')[0][:20]}</div>
                <div class="label">Target</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 Harvested Emails by Domain</h2>
'''
    
    # Domain gruplarını ekle
    for domain, emails in sorted(emails_by_domain.items()):
        html += f'''
            <div class="domain-group">
                <div class="domain-header">
                    <span class="domain-name">@{domain}</span>
                    <span class="domain-count">{len(emails)} emails</span>
                </div>
                <ul class="email-list">
'''
        for email_data in emails:
            email = email_data.get('email', '')
            valid = email_data.get('valid')
            
            if valid is True:
                status_class = 'status-valid'
                status_text = '✓ Valid'
            elif valid is False:
                status_class = 'status-invalid'
                status_text = '✗ Invalid'
            else:
                status_class = 'status-unknown'
                status_text = '? Unknown'
            
            source = email_data.get('source', '')
            source_short = source[:50] + '...' if len(source) > 50 else source
            
            html += f'''
                    <li class="email-item">
                        <span class="email-address">{email}</span>
                        <span class="email-status {status_class}">{status_text}</span>
                    </li>
'''
        
        html += '''
                </ul>
            </div>
'''
    
    html += '''
        </div>
        
        <div class="footer">
            <p>Generated by <a href="#">Email Scraper Pro v3.0</a> | Ethical Hacking Bootcamp</p>
            <p style="margin-top: 10px; font-size: 0.8em;">⚠️ This tool is for authorized security testing only</p>
        </div>
    </div>
</body>
</html>
'''
    
    # Dosyaya kaydet
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"[+] HTML report saved to: {output_file}")
    return output_file


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 html_report.py <results.json> [output.html]")
        print("\nExample:")
        print("  python3 html_report.py emails.json")
        print("  python3 html_report.py emails.json report.html")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(json_file):
        print(f"[-] File not found: {json_file}")
        sys.exit(1)
    
    generate_html_report(json_file, output_file)
