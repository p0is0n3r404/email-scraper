#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                     GOOGLE DORKING EMAIL HARVESTER                            ║
║                     Passive Email Collection via Search                       ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Uses Google search dorks to find emails without direct website crawling.
This is a passive reconnaissance technique.

Usage: python3 google_dorking.py -d example.com
"""

import argparse
import re
import sys
import time
import random
from urllib.parse import quote_plus, urlparse
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("\033[91m[!] Missing dependencies. Install with: pip3 install requests beautifulsoup4\033[0m")
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
║{Colors.YELLOW}   ██████╗  ██████╗  ██████╗ ██████╗ ██╗  ██╗    ██████╗  ██████╗ ██████╗ ██╗  ██╗{Colors.CYAN}  ║
║{Colors.YELLOW}  ██╔════╝ ██╔═══██╗██╔═══██╗██╔══██╗██║ ██╔╝    ██╔══██╗██╔═══██╗██╔══██╗██║ ██╔╝{Colors.CYAN}  ║
║{Colors.YELLOW}  ██║  ███╗██║   ██║██║   ██║██║  ██║█████╔╝     ██║  ██║██║   ██║██████╔╝█████╔╝ {Colors.CYAN}  ║
║{Colors.YELLOW}  ██║   ██║██║   ██║██║   ██║██║  ██║██╔═██╗     ██║  ██║██║   ██║██╔══██╗██╔═██╗ {Colors.CYAN}  ║
║{Colors.YELLOW}  ╚██████╔╝╚██████╔╝╚██████╔╝██████╔╝██║  ██╗    ██████╔╝╚██████╔╝██║  ██║██║  ██╗{Colors.CYAN}  ║
║{Colors.YELLOW}   ╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝{Colors.CYAN}  ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║{Colors.GREEN}              ⚡ Passive Email Harvesting via Search Engines ⚡              {Colors.CYAN}║
╚═══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""


# Google Dork sorguları
GOOGLE_DORKS = [
    'site:{domain} "@{domain}"',
    'site:{domain} "email"',
    'site:{domain} "contact"',
    'site:{domain} filetype:pdf',
    'site:{domain} filetype:doc',
    'site:{domain} filetype:xlsx',
    '"{domain}" email',
    '"{domain}" contact',
    'intext:"@{domain}"',
    '"@{domain}" -www.{domain}',
]

# Bing Dork sorguları
BING_DORKS = [
    'site:{domain} "@{domain}"',
    '"{domain}" email',
    'site:{domain} contact',
]

# DuckDuckGo sorguları
DDG_DORKS = [
    'site:{domain} email',
    '@{domain}',
]


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


class GoogleDorker:
    def __init__(self, domain, delay=5, max_results=100, engines=None):
        self.domain = domain.replace('http://', '').replace('https://', '').split('/')[0]
        self.delay = delay
        self.max_results = max_results
        self.engines = engines or ['duckduckgo']  # Default olarak DDG (daha az engelleme)
        self.emails = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
    
    def log(self, level, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "info": (Colors.GREEN, "[+]"),
            "warning": (Colors.YELLOW, "[!]"),
            "error": (Colors.RED, "[-]"),
            "success": (Colors.MAGENTA, "[✓]"),
            "email": (Colors.CYAN, "[📧]"),
            "search": (Colors.BLUE, "[🔍]"),
        }
        color, prefix = colors.get(level, (Colors.WHITE, "[*]"))
        print(f"{Colors.BLUE}[{timestamp}]{Colors.RESET} {color}{prefix}{Colors.RESET} {message}")
    
    def extract_emails(self, text):
        """Metinden email adreslerini çıkar"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        found = set(re.findall(pattern, text, re.IGNORECASE))
        
        # Filtrele
        valid_emails = set()
        for email in found:
            email = email.lower()
            # Geçersiz uzantıları atla
            if not any(email.endswith(ext) for ext in ['.png', '.jpg', '.gif', '.css', '.js']):
                valid_emails.add(email)
        
        return valid_emails
    
    def search_duckduckgo(self, query):
        """DuckDuckGo araması"""
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                emails = self.extract_emails(response.text)
                return emails
            
        except Exception as e:
            self.log("error", f"DDG error: {str(e)[:50]}")
        
        return set()
    
    def search_bing(self, query):
        """Bing araması"""
        try:
            url = f"https://www.bing.com/search?q={quote_plus(query)}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                emails = self.extract_emails(response.text)
                return emails
            
        except Exception as e:
            self.log("error", f"Bing error: {str(e)[:50]}")
        
        return set()
    
    def search_ask(self, query):
        """Ask.com araması"""
        try:
            url = f"https://www.ask.com/web?q={quote_plus(query)}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                emails = self.extract_emails(response.text)
                return emails
            
        except Exception as e:
            self.log("error", f"Ask error: {str(e)[:50]}")
        
        return set()
    
    def run(self):
        """Ana tarama döngüsü"""
        print(BANNER)
        
        self.log("info", f"Target domain: {Colors.BOLD}{self.domain}{Colors.RESET}")
        self.log("info", f"Search engines: {', '.join(self.engines)}")
        self.log("info", f"Delay between queries: {self.delay}s")
        print(f"{Colors.CYAN}{'═' * 80}{Colors.RESET}\n")
        
        query_count = 0
        
        # DuckDuckGo aramaları
        if 'duckduckgo' in self.engines or 'ddg' in self.engines:
            self.log("search", f"Searching DuckDuckGo...")
            for dork in DDG_DORKS:
                query = dork.format(domain=self.domain)
                self.log("info", f"Query: {query}")
                
                emails = self.search_duckduckgo(query)
                new_emails = emails - self.emails
                
                if new_emails:
                    self.emails.update(new_emails)
                    for email in new_emails:
                        self.log("email", f"Found: {Colors.BOLD}{email}{Colors.RESET}")
                
                query_count += 1
                time.sleep(self.delay)
        
        # Bing aramaları
        if 'bing' in self.engines:
            self.log("search", f"Searching Bing...")
            for dork in BING_DORKS:
                query = dork.format(domain=self.domain)
                self.log("info", f"Query: {query}")
                
                emails = self.search_bing(query)
                new_emails = emails - self.emails
                
                if new_emails:
                    self.emails.update(new_emails)
                    for email in new_emails:
                        self.log("email", f"Found: {Colors.BOLD}{email}{Colors.RESET}")
                
                query_count += 1
                time.sleep(self.delay)
        
        # Ask aramaları
        if 'ask' in self.engines:
            self.log("search", f"Searching Ask.com...")
            for dork in [f"@{self.domain}", f"{self.domain} email"]:
                self.log("info", f"Query: {dork}")
                
                emails = self.search_ask(dork)
                new_emails = emails - self.emails
                
                if new_emails:
                    self.emails.update(new_emails)
                    for email in new_emails:
                        self.log("email", f"Found: {Colors.BOLD}{email}{Colors.RESET}")
                
                query_count += 1
                time.sleep(self.delay)
        
        # Sonuçlar
        self.show_results(query_count)
        
        return self.emails
    
    def show_results(self, query_count):
        """Sonuçları göster"""
        print(f"\n{Colors.CYAN}{'═' * 80}{Colors.RESET}")
        print(f"{Colors.GREEN}{Colors.BOLD}                           📊 DORKING RESULTS{Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 80}{Colors.RESET}\n")
        
        print(f"  {Colors.YELLOW}🔍 Queries Executed:{Colors.RESET}  {query_count}")
        print(f"  {Colors.YELLOW}📧 Emails Found:{Colors.RESET}      {Colors.GREEN}{Colors.BOLD}{len(self.emails)}{Colors.RESET}\n")
        
        if self.emails:
            print(f"{Colors.CYAN}{'─' * 80}{Colors.RESET}")
            print(f"{Colors.MAGENTA}{Colors.BOLD}                         📧 HARVESTED EMAILS{Colors.RESET}")
            print(f"{Colors.CYAN}{'─' * 80}{Colors.RESET}\n")
            
            # Domain'e göre grupla
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
    
    def save_results(self, filename):
        """Sonuçları kaydet"""
        with open(filename, 'w') as f:
            f.write(f"# Google Dorking Results\n")
            f.write(f"# Domain: {self.domain}\n")
            f.write(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total: {len(self.emails)}\n\n")
            for email in sorted(self.emails):
                f.write(f"{email}\n")
        
        self.log("success", f"Results saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description=f'{Colors.CYAN}Google Dorking Email Harvester - Passive Email Collection{Colors.RESET}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
{Colors.YELLOW}Examples:{Colors.RESET}
  python3 google_dorking.py -d example.com
  python3 google_dorking.py -d example.com -e bing,duckduckgo
  python3 google_dorking.py -d example.com --delay 10 -o emails.txt

{Colors.GREEN}Available search engines:{Colors.RESET}
  duckduckgo (ddg) - Recommended, less blocking
  bing              - Microsoft Bing
  ask               - Ask.com

{Colors.RED}Note:{Colors.RESET} Google search is not included to avoid CAPTCHA issues.
      For Google dorking, use manual browser or tools like theHarvester.
        '''
    )
    
    parser.add_argument('-d', '--domain', required=True,
                        help='Target domain (e.g., example.com)')
    
    parser.add_argument('-e', '--engines', default='duckduckgo',
                        help='Search engines to use, comma-separated (default: duckduckgo)')
    
    parser.add_argument('--delay', type=int, default=5,
                        help='Delay between queries in seconds (default: 5)')
    
    parser.add_argument('-o', '--output',
                        help='Output file to save results')
    
    args = parser.parse_args()
    
    engines = [e.strip().lower() for e in args.engines.split(',')]
    
    dorker = GoogleDorker(
        domain=args.domain,
        delay=args.delay,
        engines=engines
    )
    
    dorker.run()
    
    if args.output:
        dorker.save_results(args.output)


if __name__ == '__main__':
    main()
