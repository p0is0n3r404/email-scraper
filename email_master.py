#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                       EMAIL SCRAPER PRO - MASTER TOOL                         ║
║                    All-in-One Email Harvesting Solution                       ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Combines all email harvesting tools into one powerful interface.
Runs multiple techniques and merges results.

Usage: python3 email_master.py -d example.com --all
"""

import argparse
import subprocess
import sys
import os
import json
import time
from datetime import datetime


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
{Colors.CYAN}╔═══════════════════════════════════════════════════════════════════════════════════════════════════╗
║{Colors.MAGENTA}  ███╗   ███╗ █████╗ ███████╗████████╗███████╗██████╗     ████████╗ ██████╗  ██████╗ ██╗          {Colors.CYAN}║
║{Colors.MAGENTA}  ████╗ ████║██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗    ╚══██╔══╝██╔═══██╗██╔═══██╗██║          {Colors.CYAN}║
║{Colors.MAGENTA}  ██╔████╔██║███████║███████╗   ██║   █████╗  ██████╔╝       ██║   ██║   ██║██║   ██║██║          {Colors.CYAN}║
║{Colors.MAGENTA}  ██║╚██╔╝██║██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗       ██║   ██║   ██║██║   ██║██║          {Colors.CYAN}║
║{Colors.MAGENTA}  ██║ ╚═╝ ██║██║  ██║███████║   ██║   ███████╗██║  ██║       ██║   ╚██████╔╝╚██████╔╝███████╗     {Colors.CYAN}║
║{Colors.MAGENTA}  ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝     {Colors.CYAN}║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════╣
║{Colors.YELLOW}                    ⚡ All-in-One Email Harvesting Solution ⚡                                     {Colors.CYAN}║
║{Colors.GREEN}                         Web Crawler • Dorking • Wayback • OSINT                                  {Colors.CYAN}║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""


class MasterTool:
    def __init__(self, args):
        self.domain = args.domain.replace('http://', '').replace('https://', '').split('/')[0]
        self.url = f"https://{self.domain}"
        self.output_dir = args.output_dir or f"results_{self.domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.run_scraper = args.scraper or args.all
        self.run_dorking = args.dorking or args.all
        self.run_wayback = args.wayback or args.all
        self.generate_report = args.report
        self.verbose = args.verbose
        
        self.all_emails = set()
        self.emails_by_source = {}
        self.results = {}
        
        # Çalışma dizinini al
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
    
    def log(self, level, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "info": (Colors.GREEN, "[+]"),
            "warning": (Colors.YELLOW, "[!]"),
            "error": (Colors.RED, "[-]"),
            "success": (Colors.MAGENTA, "[✓]"),
            "tool": (Colors.CYAN, "[🔧]"),
            "email": (Colors.BLUE, "[📧]"),
        }
        color, prefix = colors.get(level, (Colors.WHITE, "[*]"))
        print(f"{Colors.BLUE}[{timestamp}]{Colors.RESET} {color}{prefix}{Colors.RESET} {message}")
    
    def create_output_dir(self):
        """Çıktı dizinini oluştur"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            self.log("info", f"Created output directory: {self.output_dir}")
    
    def run_email_scraper(self):
        """Web crawler'ı çalıştır"""
        self.log("tool", f"{Colors.BOLD}Running Web Crawler...{Colors.RESET}")
        
        output_file = os.path.join(self.output_dir, "scraper_results.json")
        script_path = os.path.join(self.script_dir, "email_scraper.py")
        
        cmd = [
            sys.executable, script_path,
            "-u", self.url,
            "-l", "200",
            "-t", "10",
            "--format", "json",
            "-o", output_file
        ]
        
        if self.verbose:
            cmd.append("-v")
        
        try:
            result = subprocess.run(cmd, capture_output=not self.verbose, text=True, timeout=300)
            
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    data = json.load(f)
                    emails = [e['email'] if isinstance(e, dict) else e for e in data.get('emails', [])]
                    self.emails_by_source['Web Crawler'] = set(emails)
                    self.all_emails.update(emails)
                    self.results['scraper'] = data
                    self.log("success", f"Web Crawler found {len(emails)} emails")
            else:
                self.log("warning", "Web Crawler produced no output file")
                
        except subprocess.TimeoutExpired:
            self.log("error", "Web Crawler timed out")
        except Exception as e:
            self.log("error", f"Web Crawler error: {str(e)[:50]}")
    
    def run_google_dorking(self):
        """Google Dorking'i çalıştır"""
        self.log("tool", f"{Colors.BOLD}Running Google Dorking...{Colors.RESET}")
        
        output_file = os.path.join(self.output_dir, "dorking_results.txt")
        script_path = os.path.join(self.script_dir, "google_dorking.py")
        
        cmd = [
            sys.executable, script_path,
            "-d", self.domain,
            "-e", "duckduckgo,bing",
            "-o", output_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=not self.verbose, text=True, timeout=180)
            
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    emails = set()
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '@' in line:
                            emails.add(line)
                    
                    self.emails_by_source['Google Dorking'] = emails
                    self.all_emails.update(emails)
                    self.log("success", f"Google Dorking found {len(emails)} emails")
            else:
                self.log("warning", "Google Dorking produced no output file")
                
        except subprocess.TimeoutExpired:
            self.log("error", "Google Dorking timed out")
        except Exception as e:
            self.log("error", f"Google Dorking error: {str(e)[:50]}")
    
    def run_wayback_harvester(self):
        """Wayback Machine Harvester'ı çalıştır"""
        self.log("tool", f"{Colors.BOLD}Running Wayback Machine Harvester...{Colors.RESET}")
        
        output_file = os.path.join(self.output_dir, "wayback_results.json")
        script_path = os.path.join(self.script_dir, "wayback_emails.py")
        
        cmd = [
            sys.executable, script_path,
            "-d", self.domain,
            "-l", "50",
            "-t", "5",
            "--format", "json",
            "-o", output_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=not self.verbose, text=True, timeout=300)
            
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    data = json.load(f)
                    emails = set(data.get('all_emails', []))
                    self.emails_by_source['Wayback Machine'] = emails
                    self.all_emails.update(emails)
                    self.results['wayback'] = data
                    self.log("success", f"Wayback Harvester found {len(emails)} emails")
            else:
                self.log("warning", "Wayback Harvester produced no output file")
                
        except subprocess.TimeoutExpired:
            self.log("error", "Wayback Harvester timed out")
        except Exception as e:
            self.log("error", f"Wayback Harvester error: {str(e)[:50]}")
    
    def merge_results(self):
        """Tüm sonuçları birleştir"""
        self.log("info", "Merging results from all sources...")
        
        # JSON çıktısı
        merged_data = {
            'domain': self.domain,
            'scan_date': datetime.now().isoformat(),
            'total_unique_emails': len(self.all_emails),
            'sources': {},
            'all_emails': []
        }
        
        # Her email için kaynak bilgisi
        email_sources = {}
        for source, emails in self.emails_by_source.items():
            merged_data['sources'][source] = len(emails)
            for email in emails:
                if email not in email_sources:
                    email_sources[email] = []
                email_sources[email].append(source)
        
        # Email listesi
        for email in sorted(self.all_emails):
            merged_data['all_emails'].append({
                'email': email,
                'domain': email.split('@')[1] if '@' in email else '',
                'found_in': email_sources.get(email, [])
            })
        
        # Kaydet
        merged_file = os.path.join(self.output_dir, "merged_results.json")
        with open(merged_file, 'w') as f:
            json.dump(merged_data, f, indent=2)
        
        self.log("success", f"Merged results saved to: {merged_file}")
        
        # TXT çıktısı
        txt_file = os.path.join(self.output_dir, "all_emails.txt")
        with open(txt_file, 'w') as f:
            f.write(f"# Email Scraper Pro - Master Tool Results\n")
            f.write(f"# Domain: {self.domain}\n")
            f.write(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total Unique Emails: {len(self.all_emails)}\n")
            f.write(f"# Sources: {', '.join(self.emails_by_source.keys())}\n\n")
            
            for email in sorted(self.all_emails):
                sources = email_sources.get(email, [])
                f.write(f"{email}\t# Found in: {', '.join(sources)}\n")
        
        self.log("success", f"Email list saved to: {txt_file}")
        
        return merged_data
    
    def generate_html_report(self):
        """HTML raporu oluştur"""
        self.log("tool", f"{Colors.BOLD}Generating HTML Report...{Colors.RESET}")
        
        merged_file = os.path.join(self.output_dir, "merged_results.json")
        report_file = os.path.join(self.output_dir, "report.html")
        script_path = os.path.join(self.script_dir, "html_report.py")
        
        if os.path.exists(merged_file):
            cmd = [sys.executable, script_path, merged_file, report_file]
            
            try:
                subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if os.path.exists(report_file):
                    self.log("success", f"HTML report saved to: {report_file}")
                else:
                    self.log("warning", "HTML report generation failed")
                    
            except Exception as e:
                self.log("error", f"Report generation error: {str(e)[:50]}")
        else:
            self.log("warning", "No merged results file to generate report from")
    
    def show_summary(self):
        """Özet göster"""
        print(f"\n{Colors.CYAN}{'═' * 100}{Colors.RESET}")
        print(f"{Colors.GREEN}{Colors.BOLD}                                    📊 MASTER TOOL SUMMARY{Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 100}{Colors.RESET}\n")
        
        print(f"  {Colors.YELLOW}🎯 Target Domain:{Colors.RESET}     {self.domain}")
        print(f"  {Colors.YELLOW}📁 Output Directory:{Colors.RESET}  {self.output_dir}")
        print(f"  {Colors.YELLOW}📧 Total Unique:{Colors.RESET}      {Colors.GREEN}{Colors.BOLD}{len(self.all_emails)}{Colors.RESET}\n")
        
        print(f"{Colors.CYAN}{'─' * 100}{Colors.RESET}")
        print(f"{Colors.WHITE}  Results by Source:{Colors.RESET}\n")
        
        for source, emails in self.emails_by_source.items():
            bar_length = min(len(emails), 50)
            bar = '█' * bar_length
            print(f"  {Colors.CYAN}{source:20}{Colors.RESET} │ {Colors.GREEN}{bar}{Colors.RESET} {len(emails)} emails")
        
        print(f"\n{Colors.CYAN}{'─' * 100}{Colors.RESET}")
        print(f"{Colors.MAGENTA}{Colors.BOLD}                                    📧 ALL UNIQUE EMAILS{Colors.RESET}")
        print(f"{Colors.CYAN}{'─' * 100}{Colors.RESET}\n")
        
        # Domain'e göre grupla
        by_domain = {}
        for email in sorted(self.all_emails):
            domain = email.split('@')[1] if '@' in email else 'unknown'
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append(email)
        
        for domain, emails in sorted(by_domain.items()):
            print(f"  {Colors.CYAN}@{domain}{Colors.RESET} ({len(emails)} emails)")
            for email in emails:
                print(f"    {Colors.GREEN}•{Colors.RESET} {email}")
            print()
        
        print(f"{Colors.CYAN}{'═' * 100}{Colors.RESET}")
        print(f"\n  {Colors.GREEN}[✓]{Colors.RESET} All results saved to: {Colors.BOLD}{self.output_dir}/{Colors.RESET}\n")
    
    def run(self):
        """Ana çalıştırma döngüsü"""
        print(BANNER)
        
        start_time = time.time()
        
        self.log("info", f"Target: {Colors.BOLD}{self.domain}{Colors.RESET}")
        self.log("info", f"Output: {Colors.BOLD}{self.output_dir}{Colors.RESET}")
        
        techniques = []
        if self.run_scraper:
            techniques.append("Web Crawler")
        if self.run_dorking:
            techniques.append("Google Dorking")
        if self.run_wayback:
            techniques.append("Wayback Machine")
        
        self.log("info", f"Techniques: {', '.join(techniques)}")
        print(f"{Colors.CYAN}{'═' * 100}{Colors.RESET}\n")
        
        # Çıktı dizinini oluştur
        self.create_output_dir()
        
        # Araçları çalıştır
        if self.run_scraper:
            self.run_email_scraper()
            print()
        
        if self.run_dorking:
            self.run_google_dorking()
            print()
        
        if self.run_wayback:
            self.run_wayback_harvester()
            print()
        
        # Sonuçları birleştir
        if self.all_emails:
            self.merge_results()
            
            # HTML raporu oluştur
            if self.generate_report:
                self.generate_html_report()
        
        elapsed = time.time() - start_time
        self.log("success", f"Completed in {elapsed:.1f} seconds")
        
        # Özet göster
        self.show_summary()


def main():
    parser = argparse.ArgumentParser(
        description=f'{Colors.CYAN}Email Scraper Pro - Master Tool{Colors.RESET}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
{Colors.YELLOW}Examples:{Colors.RESET}
  {Colors.GREEN}# Run all techniques{Colors.RESET}
  python3 email_master.py -d example.com --all

  {Colors.GREEN}# Run specific techniques{Colors.RESET}
  python3 email_master.py -d example.com --scraper --dorking

  {Colors.GREEN}# Run with HTML report{Colors.RESET}
  python3 email_master.py -d example.com --all --report

  {Colors.GREEN}# Custom output directory{Colors.RESET}
  python3 email_master.py -d example.com --all -o my_results

{Colors.CYAN}This tool combines:{Colors.RESET}
  • Web Crawler (email_scraper.py)
  • Google Dorking (google_dorking.py)
  • Wayback Machine (wayback_emails.py)
  • HTML Report Generator (html_report.py)
        '''
    )
    
    parser.add_argument('-d', '--domain', required=True,
                        help='Target domain (e.g., example.com)')
    
    parser.add_argument('--all', action='store_true',
                        help='Run all harvesting techniques')
    
    parser.add_argument('--scraper', action='store_true',
                        help='Run web crawler')
    
    parser.add_argument('--dorking', action='store_true',
                        help='Run Google dorking')
    
    parser.add_argument('--wayback', action='store_true',
                        help='Run Wayback Machine harvester')
    
    parser.add_argument('--report', action='store_true',
                        help='Generate HTML report')
    
    parser.add_argument('-o', '--output-dir',
                        help='Output directory for results')
    
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show verbose output from tools')
    
    args = parser.parse_args()
    
    # En az bir teknik seçilmeli
    if not (args.all or args.scraper or args.dorking or args.wayback):
        parser.error("Please specify at least one technique: --all, --scraper, --dorking, or --wayback")
    
    tool = MasterTool(args)
    tool.run()


if __name__ == '__main__':
    main()
