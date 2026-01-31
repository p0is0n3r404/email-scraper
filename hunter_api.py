#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         HUNTER.IO API CLIENT                                  ║
║                    Professional Email Finder via API                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Uses Hunter.io API to find and verify email addresses.
Requires a Hunter.io API key (free tier available).

Usage: python3 hunter_api.py -d example.com --api-key YOUR_KEY
"""

import argparse
import json
import sys
from datetime import datetime

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
║{Colors.YELLOW}  ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗    ██╗ ██████╗            {Colors.CYAN}║
║{Colors.YELLOW}  ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗   ██║██╔═══██╗           {Colors.CYAN}║
║{Colors.YELLOW}  ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝   ██║██║   ██║           {Colors.CYAN}║
║{Colors.YELLOW}  ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗   ██║██║   ██║           {Colors.CYAN}║
║{Colors.YELLOW}  ██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║██╗██║╚██████╔╝           {Colors.CYAN}║
║{Colors.YELLOW}  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝╚═╝ ╚═════╝           {Colors.CYAN}║
╠═══════════════════════════════════════════════════════════════════════════════╣
║{Colors.GREEN}                  ⚡ Professional Email Finding via API ⚡                     {Colors.CYAN}║
╚═══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""


class HunterClient:
    """Hunter.io API Client"""
    
    BASE_URL = "https://api.hunter.io/v2"
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
    
    def log(self, level, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "info": (Colors.GREEN, "[+]"),
            "warning": (Colors.YELLOW, "[!]"),
            "error": (Colors.RED, "[-]"),
            "success": (Colors.MAGENTA, "[✓]"),
            "email": (Colors.CYAN, "[📧]"),
            "api": (Colors.BLUE, "[🔌]"),
        }
        color, prefix = colors.get(level, (Colors.WHITE, "[*]"))
        print(f"{Colors.BLUE}[{timestamp}]{Colors.RESET} {color}{prefix}{Colors.RESET} {message}")
    
    def check_account(self):
        """Hesap bilgilerini kontrol et"""
        url = f"{self.BASE_URL}/account"
        params = {'api_key': self.api_key}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                return {
                    'email': data.get('email'),
                    'plan': data.get('plan_name'),
                    'requests_used': data.get('requests', {}).get('searches', {}).get('used', 0),
                    'requests_available': data.get('requests', {}).get('searches', {}).get('available', 0)
                }
            elif response.status_code == 401:
                self.log("error", "Invalid API key")
                return None
            else:
                self.log("error", f"API error: {response.status_code}")
                return None
                
        except Exception as e:
            self.log("error", f"Connection error: {str(e)[:50]}")
            return None
    
    def domain_search(self, domain, limit=100):
        """Domain'deki email adreslerini bul"""
        url = f"{self.BASE_URL}/domain-search"
        params = {
            'domain': domain,
            'api_key': self.api_key,
            'limit': limit
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                return {
                    'domain': data.get('domain'),
                    'organization': data.get('organization'),
                    'emails': data.get('emails', []),
                    'pattern': data.get('pattern'),
                    'total': data.get('total', 0)
                }
            elif response.status_code == 401:
                self.log("error", "Invalid API key")
                return None
            elif response.status_code == 429:
                self.log("error", "Rate limit exceeded")
                return None
            else:
                self.log("error", f"API error: {response.status_code}")
                return None
                
        except Exception as e:
            self.log("error", f"Domain search error: {str(e)[:50]}")
            return None
    
    def email_finder(self, domain, first_name, last_name):
        """İsim ve soyisimden email bul"""
        url = f"{self.BASE_URL}/email-finder"
        params = {
            'domain': domain,
            'first_name': first_name,
            'last_name': last_name,
            'api_key': self.api_key
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                return {
                    'email': data.get('email'),
                    'score': data.get('score'),
                    'position': data.get('position'),
                    'sources': data.get('sources', [])
                }
            else:
                return None
                
        except Exception as e:
            self.log("error", f"Email finder error: {str(e)[:50]}")
            return None
    
    def email_verifier(self, email):
        """Email adresini doğrula"""
        url = f"{self.BASE_URL}/email-verifier"
        params = {
            'email': email,
            'api_key': self.api_key
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                return {
                    'email': data.get('email'),
                    'result': data.get('result'),
                    'score': data.get('score'),
                    'smtp_server': data.get('smtp_server'),
                    'smtp_check': data.get('smtp_check'),
                    'accept_all': data.get('accept_all'),
                    'disposable': data.get('disposable'),
                    'webmail': data.get('webmail')
                }
            else:
                return None
                
        except Exception as e:
            self.log("error", f"Email verifier error: {str(e)[:50]}")
            return None


def main():
    parser = argparse.ArgumentParser(
        description=f'{Colors.CYAN}Hunter.io API Client - Professional Email Finding{Colors.RESET}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
{Colors.YELLOW}Examples:{Colors.RESET}
  {Colors.GREEN}# Domain search{Colors.RESET}
  python3 hunter_api.py -d example.com --api-key YOUR_KEY

  {Colors.GREEN}# Find email by name{Colors.RESET}
  python3 hunter_api.py -d example.com --first John --last Doe --api-key YOUR_KEY

  {Colors.GREEN}# Verify email{Colors.RESET}
  python3 hunter_api.py --verify john@example.com --api-key YOUR_KEY

{Colors.CYAN}Get your free API key at:{Colors.RESET} https://hunter.io
        '''
    )
    
    parser.add_argument('-d', '--domain',
                        help='Target domain for email search')
    
    parser.add_argument('--api-key', required=True,
                        help='Hunter.io API key')
    
    parser.add_argument('--first',
                        help='First name for email finder')
    
    parser.add_argument('--last',
                        help='Last name for email finder')
    
    parser.add_argument('--verify',
                        help='Email address to verify')
    
    parser.add_argument('-l', '--limit', type=int, default=100,
                        help='Max results for domain search (default: 100)')
    
    parser.add_argument('-o', '--output',
                        help='Output file to save results (JSON)')
    
    args = parser.parse_args()
    
    print(BANNER)
    
    client = HunterClient(args.api_key)
    
    # Hesap kontrolü
    account = client.check_account()
    if account:
        client.log("api", f"Account: {account['email']} ({account['plan']})")
        client.log("api", f"Requests: {account['requests_used']}/{account['requests_available']} used")
        print()
    else:
        sys.exit(1)
    
    results = {}
    
    # Email doğrulama
    if args.verify:
        client.log("info", f"Verifying email: {args.verify}")
        result = client.email_verifier(args.verify)
        
        if result:
            results['verification'] = result
            print(f"\n  {Colors.YELLOW}Email:{Colors.RESET}      {result['email']}")
            print(f"  {Colors.YELLOW}Result:{Colors.RESET}     {result['result']}")
            print(f"  {Colors.YELLOW}Score:{Colors.RESET}      {result['score']}")
            print(f"  {Colors.YELLOW}SMTP:{Colors.RESET}       {result['smtp_check']}")
            print(f"  {Colors.YELLOW}Disposable:{Colors.RESET} {result['disposable']}")
            print(f"  {Colors.YELLOW}Webmail:{Colors.RESET}    {result['webmail']}")
            print()
    
    # İsimle email bulma
    elif args.first and args.last and args.domain:
        client.log("info", f"Finding email for {args.first} {args.last} @ {args.domain}")
        result = client.email_finder(args.domain, args.first, args.last)
        
        if result and result.get('email'):
            results['email_finder'] = result
            client.log("email", f"Found: {Colors.BOLD}{result['email']}{Colors.RESET}")
            print(f"\n  {Colors.YELLOW}Email:{Colors.RESET}    {result['email']}")
            print(f"  {Colors.YELLOW}Score:{Colors.RESET}    {result['score']}%")
            if result.get('position'):
                print(f"  {Colors.YELLOW}Position:{Colors.RESET} {result['position']}")
            print()
        else:
            client.log("warning", "No email found for this person")
    
    # Domain araması
    elif args.domain:
        client.log("info", f"Searching emails for domain: {args.domain}")
        result = client.domain_search(args.domain, args.limit)
        
        if result:
            results['domain_search'] = result
            
            print(f"\n  {Colors.YELLOW}Domain:{Colors.RESET}       {result['domain']}")
            print(f"  {Colors.YELLOW}Organization:{Colors.RESET} {result.get('organization', 'N/A')}")
            print(f"  {Colors.YELLOW}Pattern:{Colors.RESET}      {result.get('pattern', 'N/A')}")
            print(f"  {Colors.YELLOW}Total Found:{Colors.RESET}  {result['total']}")
            
            if result['emails']:
                print(f"\n{Colors.CYAN}{'─' * 80}{Colors.RESET}")
                print(f"{Colors.MAGENTA}{Colors.BOLD}                         📧 FOUND EMAILS{Colors.RESET}")
                print(f"{Colors.CYAN}{'─' * 80}{Colors.RESET}\n")
                
                for i, email_data in enumerate(result['emails'], 1):
                    email = email_data.get('value', '')
                    confidence = email_data.get('confidence', 0)
                    name = f"{email_data.get('first_name', '')} {email_data.get('last_name', '')}".strip()
                    position = email_data.get('position', '')
                    
                    confidence_color = Colors.GREEN if confidence >= 80 else Colors.YELLOW if confidence >= 50 else Colors.RED
                    
                    print(f"  {Colors.GREEN}[{i:2d}]{Colors.RESET} {email}")
                    print(f"      {Colors.DIM}Confidence: {confidence_color}{confidence}%{Colors.RESET}")
                    if name:
                        print(f"      {Colors.DIM}Name: {name}{Colors.RESET}")
                    if position:
                        print(f"      {Colors.DIM}Position: {position}{Colors.RESET}")
                    print()
                
                client.log("success", f"Found {len(result['emails'])} emails")
        else:
            client.log("warning", "No emails found for this domain")
    else:
        parser.print_help()
        sys.exit(1)
    
    # Sonuçları kaydet
    if args.output and results:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        client.log("success", f"Results saved to: {args.output}")


if __name__ == '__main__':
    main()
