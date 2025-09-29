import os
import csv
import requests
from urllib.parse import urljoin, urlparse
import time
import random
from collections import deque
from http.client import IncompleteRead
import socket

class WebCrawler:
    def __init__(self, domains_file, output_file, html_dir, max_depth=3, max_links_per_page=10, proxy=None):
        self.domains_file = domains_file
        self.output_file = output_file
        self.html_dir = html_dir
        self.max_depth = max_depth
        self.max_links_per_page = max_links_per_page
        self.proxy = proxy
        self.proxies = {'http': self.proxy} if self.proxy else None
        self.visited_urls = set()

        os.makedirs(self.html_dir, exist_ok=True)
        
        self.prepare_csv()
        
        self.session = requests.Session()
        if self.proxies:
            self.session.proxies = self.proxies
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def prepare_csv(self):
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'source_url',
                'source_url_text',
                'source_link_caption',
                'target_url',
                'target_url_text',
                'target_link_caption',
                'domain',
                'depth',
                'status_code',
                'content_type',
                'html_filename'  
            ])
    
    def save_html(self, url, html_content):
        try:
            safe_filename = "".join([c if c.isalnum() else "_" for c in url])
            filename = f"{safe_filename[:200]}.html" 
            filepath = os.path.join(self.html_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return filename
        except Exception as e:
            print(f"Error saving HTML for {url}: {str(e)}")
            return None
    
    def get_page_title(self, response_text):
        try:
            start = response_text.lower().find('<title>') + len('<title>')
            end = response_text.lower().find('</title>')
            if start > 0 and end > 0:
                return response_text[start:end].strip()
            return ''
        except:
            return ''
    
    def get_link_caption(self, soup, url):
        try:
            link_element = soup.find('a', href=lambda x: x and urljoin(url, x) == url)
            if not link_element:
                return ''
            
            img = link_element.find('img')
            if img and img.get('alt'):
                return img['alt'].strip()
            
            text = link_element.get_text(strip=True)
            if text:
                return text
            
            parent = link_element.find_parent(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div'])
            if parent:
                return parent.get_text(strip=True)[:100] 
                
            return ''
        except:
            return ''
    
    def is_valid_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except:
            return False
    
    def fetch_page(self, url):
        retries = 3
        while retries > 0:
            try:
                time.sleep(5)
                
                response = self.session.get(
                    url,
                    timeout=30,
                    stream=True,
                    verify=False
                )
                response.raise_for_status()
                return response
            except (requests.exceptions.RequestException, IncompleteRead, socket.error) as e:
                print(f"Attempt {4-retries}/3 failed for {url}: {str(e)}")
                retries -= 1
                if retries > 0:
                    time.sleep(random.uniform(1, 3))
        return None

    def extract_links(self, url, html_content):
        links = []
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for a_tag in soup.find_all('a', href=True):
                try:
                    absolute_url = urljoin(url, a_tag['href'])
                    if self.is_valid_url(absolute_url):
                        links.append({
                            'url': absolute_url,
                            'text': a_tag.get_text(strip=True) or '',
                            'caption': self.get_link_caption(soup, absolute_url)
                        })
                        
                        if len(links) >= self.max_links_per_page:
                            break
                except Exception as e:
                    continue
        except ImportError:
            print("U dont have BeautifulSoup Chris. Install it -- Cheers Pavel!!")
            return []
        
        return links

    def crawl_url(self, url, depth, writer, base_domain):
        if depth > self.max_depth or url in self.visited_urls:
            return
        
        print(f"\nCrawling {url} at depth {depth}")
        
        response = self.fetch_page(url)
        if not response:
            return
            
        self.visited_urls.add(url)
        html_content = response.text
        
        html_filename = self.save_html(url, html_content)
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        page_text = self.get_page_title(html_content)
        source_caption = self.get_link_caption(soup, url)
        links = self.extract_links(url, html_content)
        
        for link in links:
            try:
                target_url = link['url']
                if urlparse(target_url).netloc == base_domain and target_url not in self.visited_urls:
                    target_response = self.fetch_page(target_url)
                    if target_response:
                        target_html = target_response.text
                        target_html_filename = self.save_html(target_url, target_html)
                        
                        target_soup = BeautifulSoup(target_html, 'html.parser')
                        target_text = self.get_page_title(target_html)
                        target_caption = self.get_link_caption(target_soup, target_url)
                        
                        writer.writerow([
                            url,
                            page_text,
                            source_caption,
                            target_url,
                            target_text,
                            target_caption,
                            base_domain,
                            depth,
                            target_response.status_code,
                            target_response.headers.get('Content-Type', ''),
                            target_html_filename
                        ])
                        self.crawl_url(target_url, depth + 1, writer, base_domain)
            
            except Exception as e:
                print(f"Error processing link {link['url']}: {str(e)}")
                continue
    
    def crawl(self):
        with open(self.domains_file, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
        
        with open(self.output_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            for domain in domains:
                if not domain.startswith(('http://', 'https://')):
                    domain = f'http://{domain}'
                
                print(f"\nStarting new domain: {domain}")
                base_domain = urlparse(domain).netloc
                
                try:
                    self.crawl_url(domain, 1, writer, base_domain)
                except Exception as e:
                    print(f"Error processing domain {domain}: {str(e)}")
                    continue
                
                self.visited_urls.clear()
                
                csvfile.flush()


domains_file = 'domains.txt'
output_file = 'crawl_results_domain_boundary.csv'
html_dir = 'html_pages_domain_boundary'  
proxy = 'http://wayback.protoweb.org:7856'
    
crawler = WebCrawler(
    domains_file=domains_file,
    output_file=output_file,
    html_dir=html_dir,
    max_depth=10,
    max_links_per_page=10,
    proxy=proxy
)
crawler.crawl()

