#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                          EMAIL SCRAPER PRO v3.0                               ║
║                     Advanced Email Harvesting Tool                            ║
║                         For Kali Linux / Pentest                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Author: Ethical Hacking Bootcamp
Usage: python3 email_scraper.py -u <target_url> [options]

Features:
    - Multi-threaded scanning
    - Proxy support (HTTP/SOCKS)
    - robots.txt parsing
    - Subdomain discovery
    - Email validation (SMTP check)
    - Multiple output formats (TXT, JSON, CSV)
    - User-Agent rotation
    - Rate limiting
"""

import argparse
import re
import sys
import time
import signal
import json
import csv
import socket
import dns.resolver
from collections import deque
from urllib.parse import urlsplit, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from urllib.robotparser import RobotFileParser

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"\033[91m[!] Missing dependency: {e}\033[0m")
    print("\033[93m[*] Install with: pip3 install requests beautifulsoup4 lxml dnspython\033[0m")
    sys.exit(1)

try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════════
# RENK KODLARI (ANSI)
# ══════════════════════════════════════════════════════════════════════════════
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    DIM = '\033[2m'


# ══════════════════════════════════════════════════════════════════════════════
# BANNER
# ══════════════════════════════════════════════════════════════════════════════
BANNER = f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════════════════════════════════════════════════╗
║{Colors.RED}  ███████╗███╗   ███╗ █████╗ ██╗██╗         ███████╗ ██████╗██████╗  █████╗  ██████╗ ███████╗██████╗  {Colors.CYAN}║
║{Colors.RED}  ██╔════╝████╗ ████║██╔══██╗██║██║         ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗ {Colors.CYAN}║
║{Colors.RED}  █████╗  ██╔████╔██║███████║██║██║         ███████╗██║     ██████╔╝███████║██████╔╝█████╗  ██████╔╝ {Colors.CYAN}║
║{Colors.RED}  ██╔══╝  ██║╚██╔╝██║██╔══██║██║██║         ╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗ {Colors.CYAN}║
║{Colors.RED}  ███████╗██║ ╚═╝ ██║██║  ██║██║███████╗    ███████║╚██████╗██║  ██║██║  ██║██║     ███████╗██║  ██║ {Colors.CYAN}║
║{Colors.RED}  ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝ {Colors.CYAN}║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════╣
║{Colors.YELLOW}                          ⚡ Advanced Email Harvesting Tool v3.0 ⚡                                {Colors.CYAN}║
║{Colors.GREEN}                               [ Ethical Hacking Bootcamp ]                                       {Colors.CYAN}║
║{Colors.DIM}                    Proxy • Subdomain • robots.txt • Email Validation                              {Colors.CYAN}║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""


# ══════════════════════════════════════════════════════════════════════════════
# USER-AGENT LİSTESİ
# ══════════════════════════════════════════════════════════════════════════════
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
]


# ══════════════════════════════════════════════════════════════════════════════
# SUBDOMAIN LISTESI
# ══════════════════════════════════════════════════════════════════════════════
COMMON_SUBDOMAINS = [
    'www', 'mail', 'webmail', 'email', 'smtp', 'pop', 'imap',
    'ftp', 'admin', 'administrator', 'blog', 'shop', 'store',
    'api', 'dev', 'staging', 'test', 'demo', 'beta', 'alpha',
    'portal', 'secure', 'login', 'auth', 'sso', 'app', 'apps',
    'mobile', 'm', 'cdn', 'static', 'assets', 'media', 'images',
    'img', 'news', 'support', 'help', 'docs', 'documentation',
    'wiki', 'forum', 'community', 'board', 'status', 'monitor',
    'dashboard', 'panel', 'cpanel', 'plesk', 'whm', 'ns1', 'ns2',
    'dns', 'mx', 'vpn', 'remote', 'gateway', 'proxy', 'cache',
    'backup', 'old', 'new', 'legacy', 'archive', 'files', 'download',
    'upload', 'cloud', 'storage', 'db', 'database', 'mysql', 'sql',
    'postgres', 'mongo', 'redis', 'elastic', 'search', 'solr',
    'git', 'gitlab', 'github', 'bitbucket', 'svn', 'jenkins',
    'ci', 'cd', 'build', 'deploy', 'releases', 'updates',
    'crm', 'erp', 'hr', 'finance', 'billing', 'payment', 'pay',
    'checkout', 'cart', 'order', 'orders', 'invoice', 'invoices',
    'customer', 'customers', 'client', 'clients', 'partner', 'partners',
    'vendor', 'vendors', 'supplier', 'suppliers', 'dealer', 'dealers',
    'career', 'careers', 'jobs', 'hr', 'recruit', 'recruiting',
    'investor', 'investors', 'ir', 'press', 'pr', 'marketing',
    'sales', 'promo', 'campaign', 'ads', 'adserver', 'tracking',
    'analytics', 'stats', 'metrics', 'report', 'reports', 'log', 'logs'
]


# ══════════════════════════════════════════════════════════════════════════════
# EMAIL DOĞRULAYICI
# ══════════════════════════════════════════════════════════════════════════════
class EmailValidator:
    """SMTP üzerinden email doğrulama"""
    
    def __init__(self, timeout=5):
        self.timeout = timeout
        self.mx_cache = {}
    
    def get_mx_record(self, domain):
        """Domain için MX kaydını al"""
        if domain in self.mx_cache:
            return self.mx_cache[domain]
        
        if not DNS_AVAILABLE:
            return None
        
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            mx_host = str(sorted(mx_records, key=lambda x: x.preference)[0].exchange).rstrip('.')
            self.mx_cache[domain] = mx_host
            return mx_host
        except Exception:
            return None
    
    def validate_email(self, email):
        """Email adresini SMTP ile doğrula"""
        try:
            domain = email.split('@')[1]
            mx_host = self.get_mx_record(domain)
            
            if not mx_host:
                return None  # MX kaydı bulunamadı
            
            # SMTP bağlantısı (sadece MX kontrolü)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            try:
                sock.connect((mx_host, 25))
                response = sock.recv(1024).decode()
                sock.close()
                
                if response.startswith('220'):
                    return True
                return False
            except (socket.timeout, socket.error):
                return None
            finally:
                try:
                    sock.close()
                except:
                    pass
                    
        except Exception:
            return None
    
    def validate_batch(self, emails, log_func=None):
        """Toplu email doğrulama"""
        results = {
            'valid': [],
            'invalid': [],
            'unknown': []
        }
        
        for email in emails:
            result = self.validate_email(email)
            
            if result is True:
                results['valid'].append(email)
                if log_func:
                    log_func("success", f"Valid: {email}")
            elif result is False:
                results['invalid'].append(email)
                if log_func:
                    log_func("error", f"Invalid: {email}")
            else:
                results['unknown'].append(email)
                if log_func:
                    log_func("warning", f"Unknown: {email}")
        
        return results


# ══════════════════════════════════════════════════════════════════════════════
# SUBDOMAIN TARAYICI
# ══════════════════════════════════════════════════════════════════════════════
class SubdomainScanner:
    """Subdomain keşif aracı"""
    
    def __init__(self, domain, timeout=3, threads=10):
        self.domain = domain
        self.timeout = timeout
        self.threads = threads
        self.found_subdomains = []
    
    def check_subdomain(self, subdomain):
        """Tek bir subdomain kontrol et"""
        full_domain = f"{subdomain}.{self.domain}"
        
        try:
            socket.setdefaulttimeout(self.timeout)
            socket.gethostbyname(full_domain)
            return full_domain
        except socket.gaierror:
            return None
        except Exception:
            return None
    
    def scan(self, log_func=None, wordlist=None):
        """Subdomain taraması başlat"""
        subdomains_to_check = wordlist if wordlist else COMMON_SUBDOMAINS
        
        if log_func:
            log_func("info", f"Scanning {len(subdomains_to_check)} potential subdomains...")
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self.check_subdomain, sub): sub for sub in subdomains_to_check}
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    self.found_subdomains.append(result)
                    if log_func:
                        log_func("success", f"Found subdomain: {result}")
        
        return self.found_subdomains


# ══════════════════════════════════════════════════════════════════════════════
# ROBOTS.TXT PARSER
# ══════════════════════════════════════════════════════════════════════════════
class RobotsParser:
    """robots.txt analiz edici"""
    
    def __init__(self, base_url, session):
        self.base_url = base_url
        self.session = session
        self.parser = RobotFileParser()
        self.disallowed_paths = []
        self.sitemaps = []
        self.loaded = False
    
    def load(self):
        """robots.txt dosyasını yükle"""
        robots_url = f"{self.base_url}/robots.txt"
        
        try:
            response = self.session.get(robots_url, timeout=10)
            
            if response.status_code == 200:
                self.parser.parse(response.text.splitlines())
                
                # Disallowed path'leri çıkar
                for line in response.text.splitlines():
                    line = line.strip()
                    if line.lower().startswith('disallow:'):
                        path = line.split(':', 1)[1].strip()
                        if path:
                            self.disallowed_paths.append(path)
                    elif line.lower().startswith('sitemap:'):
                        sitemap = line.split(':', 1)[1].strip()
                        if sitemap:
                            self.sitemaps.append(sitemap)
                
                self.loaded = True
                return True
            
            return False
            
        except Exception:
            return False
    
    def can_fetch(self, url):
        """URL'nin taranıp taranamayacağını kontrol et"""
        if not self.loaded:
            return True
        return self.parser.can_fetch('*', url)
    
    def get_sitemap_urls(self):
        """Sitemap'lerden URL çıkar"""
        urls = []
        
        for sitemap_url in self.sitemaps:
            try:
                response = self.session.get(sitemap_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'xml')
                    for loc in soup.find_all('loc'):
                        urls.append(loc.text)
            except Exception:
                continue
        
        return urls


# ══════════════════════════════════════════════════════════════════════════════
# EMAIL SCRAPER SINIFI
# ══════════════════════════════════════════════════════════════════════════════
class EmailScraper:
    def __init__(self, args):
        self.target_url = args.url
        self.max_urls = args.limit
        self.timeout = args.timeout
        self.threads = args.threads
        self.output_file = args.output
        self.output_format = args.format
        self.verbose = args.verbose
        self.domain_only = args.domain_only
        self.delay = args.delay
        self.proxy = args.proxy
        self.respect_robots = args.robots
        self.scan_subdomains = args.subdomains
        self.validate_emails = args.validate
        self.use_sitemap = args.sitemap
        
        self.urls_to_scan = deque([self.target_url])
        self.scanned_urls = set()
        self.emails = set()
        self.emails_by_source = {}  # Email -> kaynak URL eşlemesi
        self.errors = []
        self.start_time = None
        self.running = True
        
        # Domain bilgisi
        parts = urlsplit(self.target_url)
        self.base_domain = parts.netloc.replace('www.', '')
        self.base_url = f"{parts.scheme}://{parts.netloc}"
        
        # Session oluştur
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENTS[0],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Proxy ayarla
        if self.proxy:
            self.setup_proxy()
        
        # Robots.txt parser
        self.robots_parser = RobotsParser(self.base_url, self.session)
        
        # Email validator
        self.email_validator = EmailValidator() if self.validate_emails else None
        
        # Signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def setup_proxy(self):
        """Proxy ayarlarını yapılandır"""
        proxy_url = self.proxy
        
        # SOCKS proxy desteği
        if proxy_url.startswith('socks'):
            try:
                import socks
                import socket
                
                proxy_parts = urlsplit(proxy_url)
                socks_type = socks.SOCKS5 if 'socks5' in proxy_url else socks.SOCKS4
                
                socks.set_default_proxy(
                    socks_type,
                    proxy_parts.hostname,
                    proxy_parts.port or 1080
                )
                socket.socket = socks.socksocket
                self.log("info", f"SOCKS proxy configured: {proxy_url}")
                
            except ImportError:
                self.log("error", "PySocks not installed. Install with: pip3 install PySocks")
                sys.exit(1)
        else:
            # HTTP/HTTPS proxy
            self.session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            self.log("info", f"HTTP proxy configured: {proxy_url}")
    
    def signal_handler(self, sig, frame):
        """Ctrl+C handler"""
        print(f"\n{Colors.YELLOW}[!] Interrupt received, stopping...{Colors.RESET}")
        self.running = False
    
    def log(self, level, message):
        """Renkli log çıktısı"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        levels = {
            "info": (Colors.GREEN, "[+]"),
            "warning": (Colors.YELLOW, "[!]"),
            "error": (Colors.RED, "[-]"),
            "success": (Colors.MAGENTA, "[✓]"),
            "email": (Colors.CYAN, "[📧]"),
            "scan": (Colors.WHITE, "[→]"),
            "subdomain": (Colors.BLUE, "[🌐]"),
            "robot": (Colors.DIM, "[🤖]"),
        }
        
        color, prefix = levels.get(level, (Colors.WHITE, "[*]"))
        print(f"{Colors.BLUE}[{timestamp}]{Colors.RESET} {color}{prefix}{Colors.RESET} {message}")
    
    def extract_emails(self, text):
        """Metinden email adreslerini çıkar"""
        # Gelişmiş email regex
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        found_emails = set(re.findall(email_pattern, text, re.IGNORECASE))
        
        # Geçersiz uzantıları filtrele
        invalid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.svg', '.woff', '.ttf', '.eot']
        invalid_prefixes = ['noreply', 'no-reply', 'donotreply', 'mailer-daemon']
        
        filtered_emails = set()
        
        for email in found_emails:
            email_lower = email.lower()
            
            # Geçersiz uzantıları filtrele
            if any(email_lower.endswith(ext) for ext in invalid_extensions):
                continue
            
            # Geçersiz önekleri filtrele
            local_part = email_lower.split('@')[0]
            if any(local_part.startswith(prefix) for prefix in invalid_prefixes):
                continue
            
            # Domain filtresi
            if self.domain_only:
                email_domain = email_lower.split('@')[1]
                if self.base_domain in email_domain:
                    filtered_emails.add(email_lower)
            else:
                filtered_emails.add(email_lower)
        
        return filtered_emails
    
    def extract_links(self, soup, current_url):
        """Sayfadan linkleri çıkar"""
        links = set()
        
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            
            # Mutlak URL'ye dönüştür
            full_url = urljoin(current_url, href)
            
            # URL'yi temizle (fragment kaldır)
            parts = urlsplit(full_url)
            clean_url = f"{parts.scheme}://{parts.netloc}{parts.path}"
            if parts.query:
                clean_url += f"?{parts.query}"
            
            # Aynı domain'de mi kontrol et
            url_domain = parts.netloc.replace('www.', '')
            if self.base_domain in url_domain:
                # Geçersiz uzantıları atla
                skip_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', 
                                   '.png', '.jpg', '.jpeg', '.gif', '.mp3', '.mp4', '.avi',
                                   '.exe', '.dmg', '.pkg', '.deb', '.rpm']
                if not any(clean_url.lower().endswith(ext) for ext in skip_extensions):
                    # robots.txt kontrolü
                    if self.respect_robots and not self.robots_parser.can_fetch(clean_url):
                        continue
                    links.add(clean_url)
        
        return links
    
    def scan_url(self, url):
        """Tek bir URL'yi tara"""
        if not self.running:
            return None, set(), set()
        
        try:
            # User-Agent rotasyonu
            import random
            self.session.headers['User-Agent'] = random.choice(USER_AGENTS)
            
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            
            # Email çıkar
            emails = self.extract_emails(response.text)
            
            # Link çıkar
            soup = BeautifulSoup(response.text, 'lxml')
            links = self.extract_links(soup, url)
            
            # Kaynak URL'yi sakla
            for email in emails:
                if email not in self.emails_by_source:
                    self.emails_by_source[email] = url
            
            return url, emails, links
            
        except requests.exceptions.Timeout:
            if self.verbose:
                self.log("warning", f"Timeout: {url[:60]}...")
            return url, set(), set()
        except requests.exceptions.TooManyRedirects:
            if self.verbose:
                self.log("warning", f"Too many redirects: {url[:60]}...")
            return url, set(), set()
        except requests.exceptions.RequestException as e:
            if self.verbose:
                self.log("error", f"Error: {url[:40]}... - {str(e)[:30]}")
            return url, set(), set()
        except Exception as e:
            if self.verbose:
                self.log("error", f"Unexpected: {str(e)[:50]}")
            return url, set(), set()
    
    def run(self):
        """Ana tarama döngüsü"""
        print(BANNER)
        
        self.log("info", f"Target: {Colors.BOLD}{self.target_url}{Colors.RESET}")
        self.log("info", f"Max URLs: {self.max_urls} | Threads: {self.threads} | Timeout: {self.timeout}s")
        
        if self.proxy:
            self.log("info", f"Proxy: {Colors.YELLOW}{self.proxy}{Colors.RESET}")
        if self.domain_only:
            self.log("info", f"Domain filter: {Colors.YELLOW}Only {self.base_domain}{Colors.RESET}")
        
        print(f"{Colors.CYAN}{'═' * 100}{Colors.RESET}\n")
        
        self.start_time = time.time()
        
        # robots.txt yükle
        if self.respect_robots:
            self.log("robot", "Loading robots.txt...")
            if self.robots_parser.load():
                self.log("robot", f"robots.txt loaded. {len(self.robots_parser.disallowed_paths)} disallowed paths")
                if self.robots_parser.sitemaps:
                    self.log("robot", f"Found {len(self.robots_parser.sitemaps)} sitemaps")
            else:
                self.log("warning", "robots.txt not found or inaccessible")
        
        # Sitemap'ten URL al
        if self.use_sitemap and self.respect_robots:
            sitemap_urls = self.robots_parser.get_sitemap_urls()
            if sitemap_urls:
                self.log("info", f"Adding {len(sitemap_urls)} URLs from sitemap")
                for url in sitemap_urls[:self.max_urls]:
                    if url not in self.urls_to_scan and url not in self.scanned_urls:
                        self.urls_to_scan.append(url)
        
        # Subdomain taraması
        if self.scan_subdomains:
            print(f"\n{Colors.CYAN}{'─' * 100}{Colors.RESET}")
            self.log("subdomain", f"Starting subdomain scan for {self.base_domain}...")
            
            subdomain_scanner = SubdomainScanner(self.base_domain, threads=self.threads)
            found_subdomains = subdomain_scanner.scan(log_func=self.log)
            
            if found_subdomains:
                self.log("success", f"Found {len(found_subdomains)} subdomains")
                parts = urlsplit(self.target_url)
                for subdomain in found_subdomains:
                    subdomain_url = f"{parts.scheme}://{subdomain}"
                    if subdomain_url not in self.urls_to_scan:
                        self.urls_to_scan.append(subdomain_url)
            
            print(f"{Colors.CYAN}{'─' * 100}{Colors.RESET}\n")
        
        # Ana tarama
        scanned_count = 0
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            while self.urls_to_scan and scanned_count < self.max_urls and self.running:
                # Batch olarak URL al
                batch = []
                while self.urls_to_scan and len(batch) < self.threads:
                    url = self.urls_to_scan.popleft()
                    if url not in self.scanned_urls:
                        batch.append(url)
                        self.scanned_urls.add(url)
                
                if not batch:
                    break
                
                # Paralel tarama
                futures = {executor.submit(self.scan_url, url): url for url in batch}
                
                for future in as_completed(futures):
                    if not self.running:
                        break
                    
                    url, emails, links = future.result()
                    if url is None:
                        continue
                    
                    scanned_count += 1
                    
                    # Yeni emailleri ekle
                    new_emails = emails - self.emails
                    if new_emails:
                        self.emails.update(new_emails)
                        for email in new_emails:
                            self.log("email", f"Found: {Colors.BOLD}{email}{Colors.RESET}")
                    
                    # Yeni linkleri ekle
                    for link in links:
                        if link not in self.scanned_urls and link not in self.urls_to_scan:
                            self.urls_to_scan.append(link)
                    
                    # İlerleme göster
                    if self.verbose or scanned_count % 10 == 0:
                        progress = f"[{scanned_count}/{self.max_urls}]"
                        self.log("scan", f"{progress} {url[:70]}...")
                    
                    # Delay
                    if self.delay > 0:
                        time.sleep(self.delay)
        
        # Email doğrulama
        validation_results = None
        if self.validate_emails and self.emails:
            print(f"\n{Colors.CYAN}{'─' * 100}{Colors.RESET}")
            self.log("info", f"Validating {len(self.emails)} emails via SMTP...")
            validation_results = self.email_validator.validate_batch(self.emails, log_func=self.log)
            print(f"{Colors.CYAN}{'─' * 100}{Colors.RESET}")
        
        # Sonuçları göster
        self.show_results(scanned_count, validation_results)
        
        # Kaydet
        if self.output_file:
            self.save_results(validation_results)
    
    def show_results(self, scanned_count, validation_results=None):
        """Sonuçları göster"""
        elapsed = time.time() - self.start_time
        
        print(f"\n{Colors.CYAN}{'═' * 100}{Colors.RESET}")
        print(f"{Colors.GREEN}{Colors.BOLD}                                      📊 SCAN RESULTS{Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 100}{Colors.RESET}\n")
        
        print(f"  {Colors.YELLOW}⏱  Elapsed Time:{Colors.RESET}     {elapsed:.2f} seconds")
        print(f"  {Colors.YELLOW}🔗 URLs Scanned:{Colors.RESET}     {scanned_count}")
        print(f"  {Colors.YELLOW}📧 Emails Found:{Colors.RESET}     {Colors.GREEN}{Colors.BOLD}{len(self.emails)}{Colors.RESET}")
        print(f"  {Colors.YELLOW}⚡ Scan Speed:{Colors.RESET}       {scanned_count/elapsed:.1f} URLs/sec\n")
        
        if validation_results:
            print(f"  {Colors.GREEN}✓  Valid Emails:{Colors.RESET}     {len(validation_results['valid'])}")
            print(f"  {Colors.RED}✗  Invalid Emails:{Colors.RESET}   {len(validation_results['invalid'])}")
            print(f"  {Colors.YELLOW}?  Unknown:{Colors.RESET}          {len(validation_results['unknown'])}\n")
        
        if self.emails:
            print(f"{Colors.CYAN}{'─' * 100}{Colors.RESET}")
            print(f"{Colors.MAGENTA}{Colors.BOLD}                                    📧 HARVESTED EMAILS{Colors.RESET}")
            print(f"{Colors.CYAN}{'─' * 100}{Colors.RESET}\n")
            
            # Domain'e göre grupla
            emails_by_domain = {}
            for email in sorted(self.emails):
                domain = email.split('@')[1]
                if domain not in emails_by_domain:
                    emails_by_domain[domain] = []
                emails_by_domain[domain].append(email)
            
            for domain, domain_emails in sorted(emails_by_domain.items()):
                print(f"  {Colors.CYAN}@{domain}{Colors.RESET} ({len(domain_emails)} emails)")
                for email in domain_emails:
                    status = ""
                    if validation_results:
                        if email in validation_results['valid']:
                            status = f" {Colors.GREEN}[✓ Valid]{Colors.RESET}"
                        elif email in validation_results['invalid']:
                            status = f" {Colors.RED}[✗ Invalid]{Colors.RESET}"
                        else:
                            status = f" {Colors.YELLOW}[? Unknown]{Colors.RESET}"
                    print(f"    {Colors.GREEN}•{Colors.RESET} {email}{status}")
                print()
        else:
            print(f"  {Colors.YELLOW}[!] No emails found on target.{Colors.RESET}\n")
        
        print(f"{Colors.CYAN}{'═' * 100}{Colors.RESET}\n")
    
    def save_results(self, validation_results=None):
        """Sonuçları dosyaya kaydet"""
        try:
            if self.output_format == 'txt':
                with open(self.output_file, 'w') as f:
                    f.write(f"# Email Scraper Pro v3.0 Results\n")
                    f.write(f"# Target: {self.target_url}\n")
                    f.write(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"# Total Emails: {len(self.emails)}\n\n")
                    
                    for email in sorted(self.emails):
                        source = self.emails_by_source.get(email, "unknown")
                        f.write(f"{email}\t# Source: {source}\n")
            
            elif self.output_format == 'json':
                data = {
                    'target': self.target_url,
                    'scan_date': datetime.now().isoformat(),
                    'total_emails': len(self.emails),
                    'emails': []
                }
                
                for email in sorted(self.emails):
                    email_data = {
                        'email': email,
                        'source': self.emails_by_source.get(email, "unknown"),
                        'domain': email.split('@')[1]
                    }
                    
                    if validation_results:
                        if email in validation_results['valid']:
                            email_data['valid'] = True
                        elif email in validation_results['invalid']:
                            email_data['valid'] = False
                        else:
                            email_data['valid'] = None
                    
                    data['emails'].append(email_data)
                
                with open(self.output_file, 'w') as f:
                    json.dump(data, f, indent=2)
            
            elif self.output_format == 'csv':
                with open(self.output_file, 'w', newline='') as f:
                    fieldnames = ['Email', 'Domain', 'Source', 'Valid']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for email in sorted(self.emails):
                        row = {
                            'Email': email,
                            'Domain': email.split('@')[1],
                            'Source': self.emails_by_source.get(email, "unknown"),
                            'Valid': ''
                        }
                        
                        if validation_results:
                            if email in validation_results['valid']:
                                row['Valid'] = 'Yes'
                            elif email in validation_results['invalid']:
                                row['Valid'] = 'No'
                            else:
                                row['Valid'] = 'Unknown'
                        
                        writer.writerow(row)
            
            self.log("success", f"Results saved to: {Colors.BOLD}{self.output_file}{Colors.RESET}")
            
        except Exception as e:
            self.log("error", f"Failed to save results: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# ARGÜMAN PARSER
# ══════════════════════════════════════════════════════════════════════════════
def parse_arguments():
    parser = argparse.ArgumentParser(
        description=f'{Colors.CYAN}Email Scraper Pro v3.0 - Advanced Email Harvesting Tool{Colors.RESET}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
{Colors.YELLOW}Examples:{Colors.RESET}
  {Colors.GREEN}# Basic scan{Colors.RESET}
  python3 email_scraper.py -u https://example.com

  {Colors.GREEN}# Advanced scan with subdomain discovery{Colors.RESET}
  python3 email_scraper.py -u https://example.com -l 500 -t 10 --subdomains

  {Colors.GREEN}# Scan with proxy and save to JSON{Colors.RESET}
  python3 email_scraper.py -u https://example.com --proxy http://127.0.0.1:8080 --format json -o result.json

  {Colors.GREEN}# Respect robots.txt and validate emails{Colors.RESET}
  python3 email_scraper.py -u https://example.com --robots --validate -v

  {Colors.GREEN}# Use SOCKS5 proxy (Tor){Colors.RESET}
  python3 email_scraper.py -u https://example.com --proxy socks5://127.0.0.1:9050

{Colors.CYAN}For Kali Linux / Penetration Testing{Colors.RESET}
        '''
    )
    
    # Temel argümanlar
    parser.add_argument('-u', '--url', required=True,
                        help='Target URL to scan (e.g., https://example.com)')
    
    parser.add_argument('-l', '--limit', type=int, default=100,
                        help='Maximum number of URLs to scan (default: 100)')
    
    parser.add_argument('-t', '--threads', type=int, default=5,
                        help='Number of concurrent threads (default: 5)')
    
    parser.add_argument('--timeout', type=int, default=10,
                        help='Request timeout in seconds (default: 10)')
    
    # Çıktı argümanları
    parser.add_argument('-o', '--output',
                        help='Output file path (e.g., emails.txt)')
    
    parser.add_argument('--format', choices=['txt', 'json', 'csv'], default='txt',
                        help='Output format: txt, json, csv (default: txt)')
    
    # Filtre argümanları
    parser.add_argument('-d', '--domain-only', action='store_true',
                        help='Only collect emails from target domain')
    
    parser.add_argument('--delay', type=float, default=0,
                        help='Delay between requests in seconds (default: 0)')
    
    # Gelişmiş özellikler
    parser.add_argument('--proxy',
                        help='Proxy URL (http://host:port or socks5://host:port)')
    
    parser.add_argument('--robots', action='store_true',
                        help='Respect robots.txt rules')
    
    parser.add_argument('--sitemap', action='store_true',
                        help='Parse sitemap.xml for additional URLs')
    
    parser.add_argument('--subdomains', action='store_true',
                        help='Scan for subdomains before crawling')
    
    parser.add_argument('--validate', action='store_true',
                        help='Validate emails via SMTP (requires dnspython)')
    
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose output')
    
    return parser.parse_args()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    args = parse_arguments()
    
    # URL kontrolü
    if not args.url.startswith(('http://', 'https://')):
        args.url = 'https://' + args.url
    
    # Bağımlılık kontrolü
    if args.validate and not DNS_AVAILABLE:
        print(f"{Colors.YELLOW}[!] dnspython not installed. Email validation disabled.{Colors.RESET}")
        print(f"{Colors.YELLOW}[*] Install with: pip3 install dnspython{Colors.RESET}")
        args.validate = False
    
    scraper = EmailScraper(args)
    scraper.run()


if __name__ == '__main__':
    main()
