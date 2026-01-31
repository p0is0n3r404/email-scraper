#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                     EMAIL SCRAPER PRO v3.0 - INTERACTIVE MODE                 ║
║                         Advanced Email Harvesting Tool                        ║
║                            For Kali Linux / Pentest                           ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Interactive menu-based email scraper for ease of use.
Run: python3 email_scraper_interactive.py
"""

import os
import sys
import time
from datetime import datetime

# Renk desteği
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


def clear_screen():
    """Ekranı temizle"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Banner göster"""
    banner = f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════════════════════════════════════════════════╗
║{Colors.RED}  ███████╗███╗   ███╗ █████╗ ██╗██╗         ███████╗ ██████╗██████╗  █████╗  ██████╗ ███████╗██████╗  {Colors.CYAN}║
║{Colors.RED}  ██╔════╝████╗ ████║██╔══██╗██║██║         ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗ {Colors.CYAN}║
║{Colors.RED}  █████╗  ██╔████╔██║███████║██║██║         ███████╗██║     ██████╔╝███████║██████╔╝█████╗  ██████╔╝ {Colors.CYAN}║
║{Colors.RED}  ██╔══╝  ██║╚██╔╝██║██╔══██║██║██║         ╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗ {Colors.CYAN}║
║{Colors.RED}  ███████╗██║ ╚═╝ ██║██║  ██║██║███████╗    ███████║╚██████╗██║  ██║██║  ██║██║     ███████╗██║  ██║ {Colors.CYAN}║
║{Colors.RED}  ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝ {Colors.CYAN}║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════╣
║{Colors.YELLOW}                          ⚡ Interactive Email Harvesting Tool v3.0 ⚡                             {Colors.CYAN}║
║{Colors.GREEN}                                [ Ethical Hacking Bootcamp ]                                       {Colors.CYAN}║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)


def print_menu():
    """Ana menü göster"""
    menu = f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════════════╗
║{Colors.WHITE}                      📧 MAIN MENU                             {Colors.CYAN}║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  {Colors.GREEN}[1]{Colors.WHITE} 🔍 Quick Scan          {Colors.DIM}- Fast scan with defaults{Colors.RESET}{Colors.CYAN}       ║
║  {Colors.GREEN}[2]{Colors.WHITE} ⚙️  Advanced Scan       {Colors.DIM}- Configure all options{Colors.RESET}{Colors.CYAN}        ║
║  {Colors.GREEN}[3]{Colors.WHITE} 🌐 Subdomain Discovery  {Colors.DIM}- Find subdomains first{Colors.RESET}{Colors.CYAN}       ║
║  {Colors.GREEN}[4]{Colors.WHITE} 🔐 Proxy Scan           {Colors.DIM}- Scan through proxy{Colors.RESET}{Colors.CYAN}          ║
║  {Colors.GREEN}[5]{Colors.WHITE} 📊 View Last Results    {Colors.DIM}- Show previous scan{Colors.RESET}{Colors.CYAN}          ║
║  {Colors.GREEN}[6]{Colors.WHITE} 📖 Help                 {Colors.DIM}- Usage guide{Colors.RESET}{Colors.CYAN}                 ║
║  {Colors.GREEN}[0]{Colors.WHITE} 🚪 Exit                                                 {Colors.CYAN}║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(menu)


def get_input(prompt, default=None, required=True):
    """Kullanıcı girişi al"""
    if default:
        prompt = f"{prompt} [{Colors.DIM}{default}{Colors.RESET}]: "
    else:
        prompt = f"{prompt}: "
    
    value = input(f"{Colors.GREEN}>>> {Colors.RESET}{prompt}").strip()
    
    if not value and default:
        return default
    elif not value and required:
        print(f"{Colors.RED}[!] This field is required!{Colors.RESET}")
        return get_input(prompt.replace(f" [{Colors.DIM}{default}{Colors.RESET}]", "").replace(": ", ""), default, required)
    
    return value


def get_yes_no(prompt, default='n'):
    """Evet/Hayır girişi"""
    choice = input(f"{Colors.GREEN}>>> {Colors.RESET}{prompt} (y/n) [{default}]: ").strip().lower()
    if not choice:
        choice = default
    return choice == 'y'


def build_command(options):
    """Komut satırı oluştur"""
    cmd = "python3 email_scraper.py"
    
    cmd += f" -u {options['url']}"
    cmd += f" -l {options['limit']}"
    cmd += f" -t {options['threads']}"
    cmd += f" --timeout {options['timeout']}"
    
    if options.get('output'):
        cmd += f" -o {options['output']}"
        cmd += f" --format {options['format']}"
    
    if options.get('domain_only'):
        cmd += " -d"
    
    if options.get('delay'):
        cmd += f" --delay {options['delay']}"
    
    if options.get('proxy'):
        cmd += f" --proxy {options['proxy']}"
    
    if options.get('robots'):
        cmd += " --robots"
    
    if options.get('sitemap'):
        cmd += " --sitemap"
    
    if options.get('subdomains'):
        cmd += " --subdomains"
    
    if options.get('validate'):
        cmd += " --validate"
    
    if options.get('verbose'):
        cmd += " -v"
    
    return cmd


def quick_scan():
    """Hızlı tarama modu"""
    clear_screen()
    print_banner()
    
    print(f"\n{Colors.CYAN}{'═' * 65}")
    print(f"{Colors.WHITE}                    🔍 QUICK SCAN MODE")
    print(f"{Colors.CYAN}{'═' * 65}{Colors.RESET}\n")
    
    url = get_input("Enter target URL (e.g., https://example.com)")
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    options = {
        'url': url,
        'limit': 100,
        'threads': 5,
        'timeout': 10,
        'verbose': True
    }
    
    # Kaydetme seçeneği
    if get_yes_no("Save results to file?"):
        filename = get_input("Output filename", f"emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        options['output'] = filename
        options['format'] = 'txt'
    
    cmd = build_command(options)
    
    print(f"\n{Colors.YELLOW}[*] Executing:{Colors.RESET} {cmd}\n")
    print(f"{Colors.CYAN}{'═' * 65}{Colors.RESET}\n")
    
    os.system(cmd)
    
    input(f"\n{Colors.GREEN}[Press Enter to continue...]{Colors.RESET}")


def advanced_scan():
    """Gelişmiş tarama modu"""
    clear_screen()
    print_banner()
    
    print(f"\n{Colors.CYAN}{'═' * 65}")
    print(f"{Colors.WHITE}                   ⚙️  ADVANCED SCAN MODE")
    print(f"{Colors.CYAN}{'═' * 65}{Colors.RESET}\n")
    
    # Temel ayarlar
    print(f"{Colors.YELLOW}[Basic Settings]{Colors.RESET}")
    url = get_input("Target URL")
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    limit = int(get_input("Max URLs to scan", "100"))
    threads = int(get_input("Number of threads", "5"))
    timeout = int(get_input("Request timeout (seconds)", "10"))
    
    # Filtre ayarları
    print(f"\n{Colors.YELLOW}[Filter Settings]{Colors.RESET}")
    domain_only = get_yes_no("Only collect emails from target domain?")
    delay = get_input("Delay between requests (seconds)", "0", required=False)
    
    # Gelişmiş özellikler
    print(f"\n{Colors.YELLOW}[Advanced Features]{Colors.RESET}")
    robots = get_yes_no("Respect robots.txt?")
    sitemap = get_yes_no("Parse sitemap.xml?") if robots else False
    subdomains = get_yes_no("Scan for subdomains?")
    validate = get_yes_no("Validate emails via SMTP?")
    verbose = get_yes_no("Enable verbose output?", 'y')
    
    # Çıktı ayarları
    print(f"\n{Colors.YELLOW}[Output Settings]{Colors.RESET}")
    save_results = get_yes_no("Save results to file?", 'y')
    
    options = {
        'url': url,
        'limit': limit,
        'threads': threads,
        'timeout': timeout,
        'domain_only': domain_only,
        'delay': float(delay) if delay else 0,
        'robots': robots,
        'sitemap': sitemap,
        'subdomains': subdomains,
        'validate': validate,
        'verbose': verbose
    }
    
    if save_results:
        print(f"\n  {Colors.CYAN}[1]{Colors.RESET} TXT (Plain text)")
        print(f"  {Colors.CYAN}[2]{Colors.RESET} JSON (Structured)")
        print(f"  {Colors.CYAN}[3]{Colors.RESET} CSV (Spreadsheet)")
        
        format_choice = get_input("Choose format", "1")
        formats = {'1': 'txt', '2': 'json', '3': 'csv'}
        options['format'] = formats.get(format_choice, 'txt')
        
        default_filename = f"emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{options['format']}"
        options['output'] = get_input("Output filename", default_filename)
    
    cmd = build_command(options)
    
    print(f"\n{Colors.CYAN}{'═' * 65}{Colors.RESET}")
    print(f"\n{Colors.YELLOW}[*] Command:{Colors.RESET}\n{cmd}\n")
    
    if get_yes_no("Execute this scan?", 'y'):
        print(f"\n{Colors.CYAN}{'═' * 65}{Colors.RESET}\n")
        os.system(cmd)
    
    input(f"\n{Colors.GREEN}[Press Enter to continue...]{Colors.RESET}")


def subdomain_scan():
    """Subdomain tarama modu"""
    clear_screen()
    print_banner()
    
    print(f"\n{Colors.CYAN}{'═' * 65}")
    print(f"{Colors.WHITE}                  🌐 SUBDOMAIN DISCOVERY MODE")
    print(f"{Colors.CYAN}{'═' * 65}{Colors.RESET}\n")
    
    url = get_input("Enter target URL")
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    limit = int(get_input("Max URLs per subdomain", "50"))
    
    options = {
        'url': url,
        'limit': limit,
        'threads': 10,
        'timeout': 10,
        'subdomains': True,
        'verbose': True,
        'output': f"subdomain_emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        'format': 'json'
    }
    
    cmd = build_command(options)
    
    print(f"\n{Colors.YELLOW}[*] Executing:{Colors.RESET} {cmd}\n")
    print(f"{Colors.CYAN}{'═' * 65}{Colors.RESET}\n")
    
    os.system(cmd)
    
    input(f"\n{Colors.GREEN}[Press Enter to continue...]{Colors.RESET}")


def proxy_scan():
    """Proxy tarama modu"""
    clear_screen()
    print_banner()
    
    print(f"\n{Colors.CYAN}{'═' * 65}")
    print(f"{Colors.WHITE}                    🔐 PROXY SCAN MODE")
    print(f"{Colors.CYAN}{'═' * 65}{Colors.RESET}\n")
    
    print(f"{Colors.YELLOW}[Proxy Types]{Colors.RESET}")
    print(f"  {Colors.CYAN}[1]{Colors.RESET} HTTP Proxy     (http://host:port)")
    print(f"  {Colors.CYAN}[2]{Colors.RESET} SOCKS5 Proxy   (socks5://host:port)")
    print(f"  {Colors.CYAN}[3]{Colors.RESET} Tor Network    (socks5://127.0.0.1:9050)")
    
    proxy_choice = get_input("Choose proxy type", "1")
    
    if proxy_choice == '3':
        proxy = "socks5://127.0.0.1:9050"
        print(f"{Colors.GREEN}[+] Using Tor network{Colors.RESET}")
    else:
        proxy_host = get_input("Proxy host", "127.0.0.1")
        proxy_port = get_input("Proxy port", "8080")
        prefix = "http://" if proxy_choice == '1' else "socks5://"
        proxy = f"{prefix}{proxy_host}:{proxy_port}"
    
    url = get_input("\nTarget URL")
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    options = {
        'url': url,
        'limit': 100,
        'threads': 3,  # Proxy ile daha az thread
        'timeout': 15,  # Proxy ile daha uzun timeout
        'proxy': proxy,
        'verbose': True,
        'delay': 1  # Proxy ile delay
    }
    
    if get_yes_no("Save results?", 'y'):
        options['output'] = f"proxy_emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        options['format'] = 'txt'
    
    cmd = build_command(options)
    
    print(f"\n{Colors.YELLOW}[*] Executing:{Colors.RESET} {cmd}\n")
    print(f"{Colors.CYAN}{'═' * 65}{Colors.RESET}\n")
    
    os.system(cmd)
    
    input(f"\n{Colors.GREEN}[Press Enter to continue...]{Colors.RESET}")


def view_results():
    """Son sonuçları görüntüle"""
    clear_screen()
    print_banner()
    
    print(f"\n{Colors.CYAN}{'═' * 65}")
    print(f"{Colors.WHITE}                   📊 VIEW LAST RESULTS")
    print(f"{Colors.CYAN}{'═' * 65}{Colors.RESET}\n")
    
    # Sonuç dosyalarını tara
    result_files = []
    for f in os.listdir('.'):
        if f.startswith('emails_') or f.startswith('subdomain_emails_') or f.startswith('proxy_emails_'):
            if f.endswith(('.txt', '.json', '.csv')):
                result_files.append(f)
    
    if not result_files:
        print(f"{Colors.YELLOW}[!] No result files found in current directory.{Colors.RESET}")
        input(f"\n{Colors.GREEN}[Press Enter to continue...]{Colors.RESET}")
        return
    
    # Dosyaları listele
    print(f"{Colors.YELLOW}Available result files:{Colors.RESET}\n")
    for i, f in enumerate(sorted(result_files, reverse=True), 1):
        size = os.path.getsize(f)
        mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%d %H:%M')
        print(f"  {Colors.CYAN}[{i}]{Colors.RESET} {f} ({size} bytes) - {mtime}")
    
    choice = get_input("\nSelect file number to view", "1")
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(result_files):
            filename = sorted(result_files, reverse=True)[idx]
            print(f"\n{Colors.CYAN}{'═' * 65}{Colors.RESET}")
            print(f"{Colors.WHITE}File: {filename}{Colors.RESET}")
            print(f"{Colors.CYAN}{'═' * 65}{Colors.RESET}\n")
            
            with open(filename, 'r') as f:
                content = f.read()
                print(content)
    except (ValueError, IndexError):
        print(f"{Colors.RED}[!] Invalid selection{Colors.RESET}")
    
    input(f"\n{Colors.GREEN}[Press Enter to continue...]{Colors.RESET}")


def show_help():
    """Yardım menüsü"""
    clear_screen()
    print_banner()
    
    help_text = f"""
{Colors.CYAN}{'═' * 65}
{Colors.WHITE}                        📖 HELP GUIDE
{Colors.CYAN}{'═' * 65}{Colors.RESET}

{Colors.YELLOW}QUICK SCAN{Colors.RESET}
  Fast scanning with default settings. Just enter the target URL
  and start collecting emails immediately.

{Colors.YELLOW}ADVANCED SCAN{Colors.RESET}
  Full control over all scanning parameters:
  • Max URLs: Number of pages to crawl
  • Threads: Parallel connections (higher = faster)
  • Timeout: Connection timeout per request
  • Domain filter: Only collect emails from target domain
  • Delay: Wait time between requests (avoid rate limits)

{Colors.YELLOW}SUBDOMAIN DISCOVERY{Colors.RESET}
  Automatically discover subdomains before crawling:
  • Checks 100+ common subdomain names
  • Adds discovered subdomains to scan queue
  • Useful for finding hidden email addresses

{Colors.YELLOW}PROXY SCAN{Colors.RESET}
  Route traffic through a proxy:
  • HTTP proxy: Standard web proxy
  • SOCKS5 proxy: More flexible proxy protocol
  • Tor network: Anonymous scanning via Tor

{Colors.YELLOW}OUTPUT FORMATS{Colors.RESET}
  • TXT: Simple text file with one email per line
  • JSON: Structured data with metadata
  • CSV: Spreadsheet-compatible format

{Colors.CYAN}{'═' * 65}{Colors.RESET}

{Colors.GREEN}CLI Usage Examples:{Colors.RESET}

  python3 email_scraper.py -u https://example.com
  python3 email_scraper.py -u https://example.com -l 500 --subdomains
  python3 email_scraper.py -u https://example.com --proxy socks5://127.0.0.1:9050
  python3 email_scraper.py -u https://example.com --validate -o emails.json --format json

{Colors.CYAN}{'═' * 65}{Colors.RESET}
"""
    print(help_text)
    input(f"\n{Colors.GREEN}[Press Enter to continue...]{Colors.RESET}")


def main():
    """Ana döngü"""
    while True:
        clear_screen()
        print_banner()
        print_menu()
        
        choice = input(f"{Colors.GREEN}>>> {Colors.RESET}Select option: ").strip()
        
        if choice == '1':
            quick_scan()
        elif choice == '2':
            advanced_scan()
        elif choice == '3':
            subdomain_scan()
        elif choice == '4':
            proxy_scan()
        elif choice == '5':
            view_results()
        elif choice == '6':
            show_help()
        elif choice == '0':
            clear_screen()
            print(f"\n{Colors.GREEN}[+] Goodbye! Happy hacking! 🔐{Colors.RESET}\n")
            sys.exit(0)
        else:
            print(f"{Colors.RED}[!] Invalid option. Please try again.{Colors.RESET}")
            time.sleep(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[!] Interrupted by user.{Colors.RESET}")
        sys.exit(0)
