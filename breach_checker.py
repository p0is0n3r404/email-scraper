#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         BREACH CHECKER                                        ║
║                  Check Emails Against Public Breach Databases                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Checks email addresses against public breach databases.
Uses haveibeenpwned.com API (requires API key for full access).

Usage: python3 breach_checker.py -e email@example.com
"""

import argparse
import hashlib
import sys
import time
import json
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
║{Colors.RED}  ██████╗ ██████╗ ███████╗ █████╗  ██████╗██╗  ██╗                             {Colors.CYAN}║
║{Colors.RED}  ██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝██║  ██║                             {Colors.CYAN}║
║{Colors.RED}  ██████╔╝██████╔╝█████╗  ███████║██║     ███████║                             {Colors.CYAN}║
║{Colors.RED}  ██╔══██╗██╔══██╗██╔══╝  ██╔══██║██║     ██╔══██║                             {Colors.CYAN}║
║{Colors.RED}  ██████╔╝██║  ██║███████╗██║  ██║╚██████╗██║  ██║                             {Colors.CYAN}║
║{Colors.RED}  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝                             {Colors.CYAN}║
║{Colors.YELLOW}   ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗                      {Colors.CYAN}║
║{Colors.YELLOW}  ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗                     {Colors.CYAN}║
║{Colors.YELLOW}  ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝                     {Colors.CYAN}║
║{Colors.YELLOW}  ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗                     {Colors.CYAN}║
║{Colors.YELLOW}  ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║                     {Colors.CYAN}║
║{Colors.YELLOW}   ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝                     {Colors.CYAN}║
╠═══════════════════════════════════════════════════════════════════════════════╣
║{Colors.GREEN}              ⚡ Check Emails Against Breach Databases ⚡                     {Colors.CYAN}║
╚═══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""


class BreachChecker:
    """Email breach kontrolü"""
    
    # HIBP API
    HIBP_API = "https://haveibeenpwned.com/api/v3"
    
    # Ücretsiz alternatifler
    DEHASHED_API = "https://api.dehashed.com"
    
    def __init__(self, hibp_api_key=None):
        self.hibp_api_key = hibp_api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EmailScraperPro-BreachChecker/1.0'
        })
        
        if hibp_api_key:
            self.session.headers['hibp-api-key'] = hibp_api_key
    
    def log(self, level, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "info": (Colors.GREEN, "[+]"),
            "warning": (Colors.YELLOW, "[!]"),
            "error": (Colors.RED, "[-]"),
            "success": (Colors.MAGENTA, "[✓]"),
            "breach": (Colors.RED, "[💀]"),
            "safe": (Colors.GREEN, "[✓]"),
        }
        color, prefix = colors.get(level, (Colors.WHITE, "[*]"))
        print(f"{Colors.BLUE}[{timestamp}]{Colors.RESET} {color}{prefix}{Colors.RESET} {message}")
    
    def check_hibp(self, email):
        """HaveIBeenPwned API kontrolü"""
        if not self.hibp_api_key:
            self.log("warning", "HIBP API key required for breach details")
            return None
        
        url = f"{self.HIBP_API}/breachedaccount/{email}"
        params = {'truncateResponse': 'false'}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return []  # Breach yok
            elif response.status_code == 401:
                self.log("error", "Invalid HIBP API key")
                return None
            elif response.status_code == 429:
                self.log("warning", "Rate limited, waiting...")
                time.sleep(2)
                return self.check_hibp(email)
            else:
                return None
                
        except Exception as e:
            self.log("error", f"HIBP error: {str(e)[:50]}")
            return None
    
    def check_password_pwned(self, password):
        """Şifrenin breach'lerde olup olmadığını kontrol et (k-anonymity)"""
        sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]
        
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                hashes = response.text.splitlines()
                
                for line in hashes:
                    hash_suffix, count = line.split(':')
                    if hash_suffix == suffix:
                        return int(count)
                
                return 0  # Breach'te yok
            
            return None
            
        except Exception as e:
            self.log("error", f"Password check error: {str(e)[:50]}")
            return None
    
    def check_email_format(self, email):
        """Email formatını kontrol et"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def generate_report(self, email, breaches):
        """Breach raporu oluştur"""
        report = {
            'email': email,
            'checked_at': datetime.now().isoformat(),
            'breach_count': len(breaches) if breaches else 0,
            'breaches': []
        }
        
        if breaches:
            for breach in breaches:
                report['breaches'].append({
                    'name': breach.get('Name', 'Unknown'),
                    'domain': breach.get('Domain', ''),
                    'breach_date': breach.get('BreachDate', ''),
                    'added_date': breach.get('AddedDate', ''),
                    'pwn_count': breach.get('PwnCount', 0),
                    'data_classes': breach.get('DataClasses', []),
                    'is_verified': breach.get('IsVerified', False),
                    'is_sensitive': breach.get('IsSensitive', False)
                })
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description=f'{Colors.CYAN}Breach Checker - Check Emails Against Breach Databases{Colors.RESET}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
{Colors.YELLOW}Examples:{Colors.RESET}
  {Colors.GREEN}# Check single email (requires HIBP API key){Colors.RESET}
  python3 breach_checker.py -e email@example.com --api-key YOUR_KEY

  {Colors.GREEN}# Check multiple emails from file{Colors.RESET}
  python3 breach_checker.py -f emails.txt --api-key YOUR_KEY

  {Colors.GREEN}# Check if password has been pwned (no API key needed){Colors.RESET}
  python3 breach_checker.py --password "mypassword123"

{Colors.RED}Note:{Colors.RESET} HIBP API key required for email breach checks.
      Get your API key at: https://haveibeenpwned.com/API/Key
      Password check is FREE and uses k-anonymity (safe).
        '''
    )
    
    parser.add_argument('-e', '--email',
                        help='Email address to check')
    
    parser.add_argument('-f', '--file',
                        help='File containing email addresses (one per line)')
    
    parser.add_argument('--password',
                        help='Check if password has been pwned (anonymous)')
    
    parser.add_argument('--api-key',
                        help='HaveIBeenPwned API key')
    
    parser.add_argument('-o', '--output',
                        help='Output file for results (JSON)')
    
    parser.add_argument('--delay', type=float, default=1.5,
                        help='Delay between requests (default: 1.5s)')
    
    args = parser.parse_args()
    
    print(BANNER)
    
    checker = BreachChecker(hibp_api_key=args.api_key)
    results = []
    
    # Şifre kontrolü
    if args.password:
        checker.log("info", f"Checking password... (using k-anonymity, safe)")
        count = checker.check_password_pwned(args.password)
        
        if count is None:
            checker.log("error", "Could not check password")
        elif count > 0:
            checker.log("breach", f"Password found in {Colors.BOLD}{count:,}{Colors.RESET} breaches!")
            print(f"\n  {Colors.RED}⚠️  This password has been exposed in data breaches!{Colors.RESET}")
            print(f"  {Colors.YELLOW}It has appeared {count:,} times in breach databases.{Colors.RESET}")
            print(f"  {Colors.GREEN}Recommendation: Change this password immediately!{Colors.RESET}\n")
        else:
            checker.log("safe", "Password NOT found in any known breaches")
            print(f"\n  {Colors.GREEN}✓ This password has not been found in known breaches.{Colors.RESET}")
            print(f"  {Colors.YELLOW}Note: This doesn't guarantee it's secure!{Colors.RESET}\n")
        
        sys.exit(0)
    
    # Email kontrolleri
    emails_to_check = []
    
    if args.email:
        emails_to_check.append(args.email)
    
    if args.file:
        try:
            with open(args.file, 'r') as f:
                for line in f:
                    email = line.strip()
                    if email and '@' in email and not email.startswith('#'):
                        emails_to_check.append(email)
        except FileNotFoundError:
            checker.log("error", f"File not found: {args.file}")
            sys.exit(1)
    
    if not emails_to_check:
        parser.print_help()
        print(f"\n{Colors.YELLOW}[!] Please provide an email (-e) or file (-f) to check{Colors.RESET}")
        sys.exit(1)
    
    if not args.api_key:
        checker.log("warning", "No HIBP API key provided. Breach check requires API key.")
        checker.log("info", "Get your key at: https://haveibeenpwned.com/API/Key")
        checker.log("info", "You can still check passwords with --password flag")
        sys.exit(1)
    
    checker.log("info", f"Checking {len(emails_to_check)} email(s)...")
    print(f"{Colors.CYAN}{'═' * 80}{Colors.RESET}\n")
    
    breached_count = 0
    safe_count = 0
    
    for i, email in enumerate(emails_to_check, 1):
        if not checker.check_email_format(email):
            checker.log("warning", f"Invalid email format: {email}")
            continue
        
        checker.log("info", f"[{i}/{len(emails_to_check)}] Checking: {email}")
        
        breaches = checker.check_hibp(email)
        
        if breaches is None:
            checker.log("error", f"Could not check: {email}")
        elif breaches:
            breached_count += 1
            checker.log("breach", f"{Colors.BOLD}{email}{Colors.RESET} - Found in {Colors.RED}{len(breaches)}{Colors.RESET} breach(es)!")
            
            # Breach detayları
            for breach in breaches[:5]:  # İlk 5 breach
                name = breach.get('Name', 'Unknown')
                date = breach.get('BreachDate', 'Unknown')
                data = ', '.join(breach.get('DataClasses', [])[:3])
                print(f"    {Colors.DIM}• {name} ({date}): {data}{Colors.RESET}")
            
            if len(breaches) > 5:
                print(f"    {Colors.DIM}... and {len(breaches) - 5} more breaches{Colors.RESET}")
            
            # Rapor için kaydet
            results.append(checker.generate_report(email, breaches))
        else:
            safe_count += 1
            checker.log("safe", f"{Colors.BOLD}{email}{Colors.RESET} - Not found in any breaches")
            results.append(checker.generate_report(email, []))
        
        # Rate limit
        if i < len(emails_to_check):
            time.sleep(args.delay)
    
    # Özet
    print(f"\n{Colors.CYAN}{'═' * 80}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}                              📊 SUMMARY{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 80}{Colors.RESET}\n")
    
    print(f"  {Colors.YELLOW}📧 Emails Checked:{Colors.RESET}  {len(emails_to_check)}")
    print(f"  {Colors.RED}💀 Breached:{Colors.RESET}        {breached_count}")
    print(f"  {Colors.GREEN}✓  Safe:{Colors.RESET}           {safe_count}")
    
    if breached_count > 0:
        print(f"\n  {Colors.RED}⚠️  {breached_count} email(s) found in breach databases!{Colors.RESET}")
        print(f"  {Colors.YELLOW}Recommendation: Change passwords for breached accounts.{Colors.RESET}")
    
    print(f"\n{Colors.CYAN}{'═' * 80}{Colors.RESET}\n")
    
    # Kaydet
    if args.output and results:
        with open(args.output, 'w') as f:
            json.dump({
                'checked_at': datetime.now().isoformat(),
                'total_checked': len(emails_to_check),
                'breached': breached_count,
                'safe': safe_count,
                'results': results
            }, f, indent=2)
        
        checker.log("success", f"Results saved to: {args.output}")


if __name__ == '__main__':
    main()
