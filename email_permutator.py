#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         EMAIL PERMUTATOR                                      ║
║                  Generate Email Addresses from Names                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Generates possible email addresses from first/last names and domain.
Useful for targeted phishing simulations or email discovery.

Usage: python3 email_permutator.py -f John -l Doe -d example.com
"""

import argparse
import sys
from datetime import datetime

try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False


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
║{Colors.GREEN}  ██████╗ ███████╗██████╗ ███╗   ███╗██╗   ██╗████████╗ █████╗ ████████╗███████╗{Colors.CYAN}║
║{Colors.GREEN}  ██╔══██╗██╔════╝██╔══██╗████╗ ████║██║   ██║╚══██╔══╝██╔══██╗╚══██╔══╝██╔════╝{Colors.CYAN}║
║{Colors.GREEN}  ██████╔╝█████╗  ██████╔╝██╔████╔██║██║   ██║   ██║   ███████║   ██║   █████╗  {Colors.CYAN}║
║{Colors.GREEN}  ██╔═══╝ ██╔══╝  ██╔══██╗██║╚██╔╝██║██║   ██║   ██║   ██╔══██║   ██║   ██╔══╝  {Colors.CYAN}║
║{Colors.GREEN}  ██║     ███████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝   ██║   ██║  ██║   ██║   ███████╗{Colors.CYAN}║
║{Colors.GREEN}  ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚══════╝{Colors.CYAN}║
╠═══════════════════════════════════════════════════════════════════════════════╣
║{Colors.YELLOW}              ⚡ Generate Email Addresses from Names ⚡                       {Colors.CYAN}║
╚═══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""


class EmailPermutator:
    """Email adres permütasyonları oluşturur"""
    
    def __init__(self, first_name, last_name, domain, middle_name=None):
        self.first = first_name.lower().strip()
        self.last = last_name.lower().strip()
        self.middle = middle_name.lower().strip() if middle_name else None
        self.domain = domain.lower().strip()
        
        # Kısaltmalar
        self.f = self.first[0] if self.first else ''
        self.l = self.last[0] if self.last else ''
        self.m = self.middle[0] if self.middle else ''
    
    def generate(self):
        """Tüm olası email adreslerini oluştur"""
        emails = []
        
        # Temel formatlar
        patterns = [
            # İsim tabanlı
            f"{self.first}",
            f"{self.last}",
            f"{self.first}{self.last}",
            f"{self.first}.{self.last}",
            f"{self.first}_{self.last}",
            f"{self.first}-{self.last}",
            f"{self.last}{self.first}",
            f"{self.last}.{self.first}",
            f"{self.last}_{self.first}",
            f"{self.last}-{self.first}",
            
            # Baş harf kombinasyonları
            f"{self.f}{self.last}",
            f"{self.f}.{self.last}",
            f"{self.f}_{self.last}",
            f"{self.f}-{self.last}",
            f"{self.first}{self.l}",
            f"{self.first}.{self.l}",
            f"{self.first}_{self.l}",
            f"{self.first}-{self.l}",
            f"{self.f}{self.l}",
            f"{self.f}.{self.l}",
            f"{self.l}{self.f}",
            f"{self.l}.{self.f}",
            f"{self.last}{self.f}",
            f"{self.last}.{self.f}",
            f"{self.last}_{self.f}",
            f"{self.last}-{self.f}",
            
            # Sadece isim/soyisim
            f"{self.first}1",
            f"{self.last}1",
            f"{self.first}123",
            f"{self.last}123",
        ]
        
        # Orta isim varsa ekle
        if self.middle:
            patterns.extend([
                f"{self.first}{self.middle}{self.last}",
                f"{self.first}.{self.middle}.{self.last}",
                f"{self.first}_{self.middle}_{self.last}",
                f"{self.f}{self.m}{self.last}",
                f"{self.f}.{self.m}.{self.last}",
                f"{self.first}{self.m}{self.last}",
                f"{self.first}.{self.m}.{self.last}",
            ])
        
        # Domain ekle ve listeye al
        for pattern in patterns:
            if pattern:  # Boş değilse
                email = f"{pattern}@{self.domain}"
                if email not in emails:
                    emails.append(email)
        
        return emails
    
    def get_common_patterns(self):
        """En yaygın email formatlarını döndür"""
        common = [
            (f"{self.first}.{self.last}@{self.domain}", "firstname.lastname"),
            (f"{self.first}{self.last}@{self.domain}", "firstnamelastname"),
            (f"{self.f}{self.last}@{self.domain}", "flastname"),
            (f"{self.first}@{self.domain}", "firstname"),
            (f"{self.last}@{self.domain}", "lastname"),
            (f"{self.first}_{self.last}@{self.domain}", "firstname_lastname"),
            (f"{self.first}-{self.last}@{self.domain}", "firstname-lastname"),
            (f"{self.last}.{self.first}@{self.domain}", "lastname.firstname"),
            (f"{self.f}.{self.last}@{self.domain}", "f.lastname"),
            (f"{self.first}.{self.l}@{self.domain}", "firstname.l"),
        ]
        return common


def verify_mx(domain):
    """Domain için MX kaydı kontrol et"""
    if not DNS_AVAILABLE:
        return None
    
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return [str(r.exchange).rstrip('.') for r in mx_records]
    except Exception:
        return None


def log(level, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    colors = {
        "info": (Colors.GREEN, "[+]"),
        "warning": (Colors.YELLOW, "[!]"),
        "error": (Colors.RED, "[-]"),
        "success": (Colors.MAGENTA, "[✓]"),
        "email": (Colors.CYAN, "[📧]"),
    }
    color, prefix = colors.get(level, (Colors.WHITE, "[*]"))
    print(f"{Colors.BLUE}[{timestamp}]{Colors.RESET} {color}{prefix}{Colors.RESET} {message}")


def main():
    parser = argparse.ArgumentParser(
        description=f'{Colors.CYAN}Email Permutator - Generate Email Addresses from Names{Colors.RESET}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
{Colors.YELLOW}Examples:{Colors.RESET}
  python3 email_permutator.py -f John -l Doe -d example.com
  python3 email_permutator.py -f John -m William -l Doe -d example.com
  python3 email_permutator.py -f John -l Doe -d example.com -o emails.txt
  python3 email_permutator.py -f John -l Doe -d example.com --verify

{Colors.GREEN}Common email patterns:{Colors.RESET}
  firstname.lastname@domain.com
  firstnamelastname@domain.com  
  flastname@domain.com
  firstname@domain.com
        '''
    )
    
    parser.add_argument('-f', '--first', required=True,
                        help='First name')
    
    parser.add_argument('-l', '--last', required=True,
                        help='Last name')
    
    parser.add_argument('-m', '--middle',
                        help='Middle name (optional)')
    
    parser.add_argument('-d', '--domain', required=True,
                        help='Target domain')
    
    parser.add_argument('-o', '--output',
                        help='Output file to save results')
    
    parser.add_argument('--verify', action='store_true',
                        help='Verify domain has MX records')
    
    parser.add_argument('--common', action='store_true',
                        help='Show only common patterns')
    
    args = parser.parse_args()
    
    print(BANNER)
    
    log("info", f"Name: {Colors.BOLD}{args.first} {args.middle or ''} {args.last}{Colors.RESET}")
    log("info", f"Domain: {Colors.BOLD}{args.domain}{Colors.RESET}")
    
    # MX doğrulama
    if args.verify:
        mx_records = verify_mx(args.domain)
        if mx_records:
            log("success", f"MX records found: {', '.join(mx_records[:3])}")
        else:
            log("warning", "No MX records found or DNS unavailable")
    
    print(f"{Colors.CYAN}{'═' * 80}{Colors.RESET}\n")
    
    # Permutator oluştur
    permutator = EmailPermutator(
        first_name=args.first,
        last_name=args.last,
        domain=args.domain,
        middle_name=args.middle
    )
    
    if args.common:
        # Sadece yaygın formatlar
        patterns = permutator.get_common_patterns()
        print(f"{Colors.MAGENTA}{Colors.BOLD}                      📧 COMMON EMAIL PATTERNS{Colors.RESET}")
        print(f"{Colors.CYAN}{'─' * 80}{Colors.RESET}\n")
        
        for email, pattern_name in patterns:
            print(f"  {Colors.GREEN}•{Colors.RESET} {email:40} {Colors.DIM}({pattern_name}){Colors.RESET}")
        
        emails = [e[0] for e in patterns]
    else:
        # Tüm permütasyonlar
        emails = permutator.generate()
        
        print(f"{Colors.MAGENTA}{Colors.BOLD}                      📧 GENERATED EMAILS ({len(emails)}){Colors.RESET}")
        print(f"{Colors.CYAN}{'─' * 80}{Colors.RESET}\n")
        
        for i, email in enumerate(emails, 1):
            print(f"  {Colors.GREEN}[{i:2d}]{Colors.RESET} {email}")
    
    print(f"\n{Colors.CYAN}{'═' * 80}{Colors.RESET}")
    log("success", f"Generated {len(emails)} possible email addresses")
    
    # Kaydet
    if args.output:
        with open(args.output, 'w') as f:
            f.write(f"# Email Permutator Results\n")
            f.write(f"# Name: {args.first} {args.middle or ''} {args.last}\n")
            f.write(f"# Domain: {args.domain}\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for email in emails:
                f.write(f"{email}\n")
        
        log("success", f"Results saved to: {args.output}")


if __name__ == '__main__':
    main()
