#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                     WAYBACK MACHINE EMAIL HARVESTER                           ║
║                  Historical Email Collection from Archives                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Uses the Wayback Machine (web.archive.org) to find historical email addresses
from archived versions of websites.

Usage: python3 wayback_emails.py -d example.com
"""

import argparse
import re
import sys
import time
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
except ImportError:
    print("\033[91m[!] Missing requests. Install with: pip3 install requests\033[0m")
    sys.exit(1)


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'


BANNER = f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════════════════════════════╗
║{Colors.BLUE}  ██╗    ██╗ █████╗ ██╗   ██╗██████╗  █████╗  ██████╗██╗  ██╗                  {Colors.CYAN}║
║{Colors.BLUE}  ██║    ██║██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝                  {Colors.CYAN}║
║{Colors.BLUE}  ██║ █╗ ██║███████║ ╚████╔╝ ██████╔╝███████║██║     █████╔╝                   {Colors.CYAN}║
║{Colors.BLUE}  ██║███╗██║██╔══██║  ╚██╔╝  ██╔══██╗██╔══██║██║     ██╔═██╗                   {Colors.CYAN}║
║{Colors.BLUE}  ╚███╔███╔╝██║  ██║   ██║   ██████╔╝██║  ██║╚██████╗██║  ██╗                  {Colors.CYAN}║
║{Colors.BLUE}   ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝   ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝                  {Colors.CYAN}║
╠═══════════════════════════════════════════════════════════════════════════════╣
║{Colors.GREEN}            ⏰ Historical Email Harvesting from Web Archives ⏰               {Colors.CYAN}║
╚═══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""


class WaybackHarvester:
    def __init__(self, domain, limit=50, threads=5, years=None):
        self.domain = domain.replace('http://', '').replace('https://', '').split('/')[0]
        self.limit = limit
        self.threads = threads
        self.years = years  # Belirli yılları filtrele
        self.emails = set()
        self.emails_by_year = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
        })
    
    def log(self, level, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "info": (Colors.GREEN, "[+]"),
            "warning": (Colors.YELLOW, "[!]"),
            "error": (Colors.RED, "[-]"),
            "success": (Colors.MAGENTA, "[✓]"),
            "email": (Colors.CYAN, "[📧]"),
            "archive": (Colors.BLUE, "[📦]"),
        }
        color, prefix = colors.get(level, (Colors.WHITE, "[*]"))
        print(f"{Colors.BLUE}[{timestamp}]{Colors.RESET} {color}{prefix}{Colors.RESET} {message}")
    
    def get_snapshots(self):
        """Wayback Machine'den snapshot listesi al"""
        cdx_url = f"https://web.archive.org/cdx/search/cdx"
        params = {
            'url': f"{self.domain}/*",
            'output': 'json',
            'fl': 'timestamp,original,statuscode,mimetype',
            'filter': 'statuscode:200',
            'filter': 'mimetype:text/html',
            'collapse': 'urlkey',
            'limit': self.limit * 2  # Fazla al, filtrele
        }
        
        try:
            response = self.session.get(cdx_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if len(data) > 1:
                    # İlk satır header
                    snapshots = []
                    for row in data[1:]:
                        timestamp, url, status, mime = row
                        year = timestamp[:4]
                        
                        # Yıl filtresi
                        if self.years and year not in self.years:
                            continue
                        
                        snapshots.append({
                            'timestamp': timestamp,
                            'url': url,
                            'year': year,
                            'archive_url': f"https://web.archive.org/web/{timestamp}/{url}"
                        })
                    
                    return snapshots[:self.limit]
            
            return []
            
        except Exception as e:
            self.log("error", f"CDX API error: {str(e)[:50]}")
            return []
    
    def extract_emails(self, text):
        """Metinden email adreslerini çıkar"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        found = set(re.findall(pattern, text, re.IGNORECASE))
        
        # Filtrele
        valid_emails = set()
        for email in found:
            email = email.lower()
            # Geçersiz uzantıları atla
            if any(email.endswith(ext) for ext in ['.png', '.jpg', '.gif', '.css', '.js']):
                continue
            # Wayback Machine emaillerini atla
            if 'archive.org' in email:
                continue
            valid_emails.add(email)
        
        return valid_emails
    
    def fetch_snapshot(self, snapshot):
        """Tek bir arşiv sayfasını getir"""
        try:
            response = self.session.get(snapshot['archive_url'], timeout=15)
            
            if response.status_code == 200:
                emails = self.extract_emails(response.text)
                return snapshot, emails
            
        except Exception as e:
            pass
        
        return snapshot, set()
    
    def run(self):
        """Ana tarama döngüsü"""
        print(BANNER)
        
        self.log("info", f"Target domain: {Colors.BOLD}{self.domain}{Colors.RESET}")
        self.log("info", f"Max snapshots: {self.limit} | Threads: {self.threads}")
        
        if self.years:
            self.log("info", f"Year filter: {', '.join(self.years)}")
        
        print(f"{Colors.CYAN}{'═' * 80}{Colors.RESET}\n")
        
        # Snapshot'ları al
        self.log("archive", "Fetching Wayback Machine snapshots...")
        snapshots = self.get_snapshots()
        
        if not snapshots:
            self.log("warning", "No snapshots found for this domain")
            return self.emails
        
        self.log("success", f"Found {len(snapshots)} snapshots to analyze")
        print()
        
        # Paralel tarama
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self.fetch_snapshot, s): s for s in snapshots}
            
            processed = 0
            for future in as_completed(futures):
                snapshot, emails = future.result()
                processed += 1
                
                # Yeni emailler
                new_emails = emails - self.emails
                if new_emails:
                    self.emails.update(new_emails)
                    
                    year = snapshot['year']
                    if year not in self.emails_by_year:
                        self.emails_by_year[year] = set()
                    self.emails_by_year[year].update(new_emails)
                    
                    for email in new_emails:
                        self.log("email", f"[{year}] Found: {Colors.BOLD}{email}{Colors.RESET}")
                
                # İlerleme
                if processed % 10 == 0:
                    self.log("archive", f"Progress: {processed}/{len(snapshots)} snapshots analyzed")
        
        # Sonuçlar
        self.show_results(len(snapshots))
        
        return self.emails
    
    def show_results(self, total_snapshots):
        """Sonuçları göster"""
        print(f"\n{Colors.CYAN}{'═' * 80}{Colors.RESET}")
        print(f"{Colors.GREEN}{Colors.BOLD}                          📊 WAYBACK RESULTS{Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 80}{Colors.RESET}\n")
        
        print(f"  {Colors.YELLOW}📦 Snapshots Analyzed:{Colors.RESET}  {total_snapshots}")
        print(f"  {Colors.YELLOW}📧 Emails Found:{Colors.RESET}        {Colors.GREEN}{Colors.BOLD}{len(self.emails)}{Colors.RESET}")
        print(f"  {Colors.YELLOW}📅 Years Covered:{Colors.RESET}       {len(self.emails_by_year)}\n")
        
        if self.emails:
            print(f"{Colors.CYAN}{'─' * 80}{Colors.RESET}")
            print(f"{Colors.MAGENTA}{Colors.BOLD}                      📧 EMAILS BY YEAR{Colors.RESET}")
            print(f"{Colors.CYAN}{'─' * 80}{Colors.RESET}\n")
            
            for year in sorted(self.emails_by_year.keys(), reverse=True):
                emails = self.emails_by_year[year]
                print(f"  {Colors.YELLOW}📅 {year}{Colors.RESET} ({len(emails)} emails)")
                for email in sorted(emails):
                    print(f"    {Colors.GREEN}•{Colors.RESET} {email}")
                print()
            
            # Domain özeti
            print(f"{Colors.CYAN}{'─' * 80}{Colors.RESET}")
            print(f"{Colors.MAGENTA}{Colors.BOLD}                      📧 ALL UNIQUE EMAILS{Colors.RESET}")
            print(f"{Colors.CYAN}{'─' * 80}{Colors.RESET}\n")
            
            by_domain = {}
            for email in sorted(self.emails):
                domain = email.split('@')[1]
                if domain not in by_domain:
                    by_domain[domain] = []
                by_domain[domain].append(email)
            
            for domain, emails in sorted(by_domain.items()):
                print(f"  {Colors.CYAN}@{domain}{Colors.RESET}")
                for email in emails:
                    print(f"    {Colors.GREEN}•{Colors.RESET} {email}")
                print()
        
        print(f"{Colors.CYAN}{'═' * 80}{Colors.RESET}\n")
    
    def save_results(self, filename, format='txt'):
        """Sonuçları kaydet"""
        if format == 'json':
            data = {
                'domain': self.domain,
                'scan_date': datetime.now().isoformat(),
                'total_emails': len(self.emails),
                'emails_by_year': {y: list(e) for y, e in self.emails_by_year.items()},
                'all_emails': sorted(list(self.emails))
            }
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            with open(filename, 'w') as f:
                f.write(f"# Wayback Machine Email Harvest\n")
                f.write(f"# Domain: {self.domain}\n")
                f.write(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Total: {len(self.emails)}\n\n")
                
                for year in sorted(self.emails_by_year.keys(), reverse=True):
                    f.write(f"\n# === {year} ===\n")
                    for email in sorted(self.emails_by_year[year]):
                        f.write(f"{email}\n")
        
        self.log("success", f"Results saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description=f'{Colors.CYAN}Wayback Machine Email Harvester{Colors.RESET}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
{Colors.YELLOW}Examples:{Colors.RESET}
  python3 wayback_emails.py -d example.com
  python3 wayback_emails.py -d example.com -l 100 -t 10
  python3 wayback_emails.py -d example.com --years 2020,2021,2022
  python3 wayback_emails.py -d example.com -o historical_emails.json --format json

{Colors.GREEN}Notes:{Colors.RESET}
  - Wayback Machine has limited API rate, be patient
  - Older snapshots may contain outdated but still useful emails
  - Great for finding emails that were removed from current site
        '''
    )
    
    parser.add_argument('-d', '--domain', required=True,
                        help='Target domain (e.g., example.com)')
    
    parser.add_argument('-l', '--limit', type=int, default=50,
                        help='Maximum snapshots to analyze (default: 50)')
    
    parser.add_argument('-t', '--threads', type=int, default=5,
                        help='Number of concurrent threads (default: 5)')
    
    parser.add_argument('--years',
                        help='Filter by years, comma-separated (e.g., 2020,2021)')
    
    parser.add_argument('-o', '--output',
                        help='Output file to save results')
    
    parser.add_argument('--format', choices=['txt', 'json'], default='txt',
                        help='Output format (default: txt)')
    
    args = parser.parse_args()
    
    years = args.years.split(',') if args.years else None
    
    harvester = WaybackHarvester(
        domain=args.domain,
        limit=args.limit,
        threads=args.threads,
        years=years
    )
    
    harvester.run()
    
    if args.output:
        harvester.save_results(args.output, args.format)


if __name__ == '__main__':
    main()
