"""
Main scraper module for Noel Leeming website
"""
import time
import json
import os
import logging
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import random

import config
from utils import setup_logging, save_checkpoint, load_checkpoint, sanitize_filename


class NoelLeemingScraper:
    """High-performance web scraper for Noel Leeming website"""
    
    def __init__(self):
        """Initialize the scraper"""
        self.logger = setup_logging()
        self.session = requests.Session()
        self.products = []
        self.categories = []
        self.checkpoint_file = os.path.join(config.CHECKPOINTS_DIR, 'scraper.checkpoint')
        self.driver = None
        
        # Set up session headers
        self.session.headers.update({
            'User-Agent': random.choice(config.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.logger.info("NoelLeemingScraper initialized")
    
    def _setup_selenium(self):
        """Setup Selenium WebDriver if needed"""
        if not config.USE_SELENIUM or self.driver:
            return
        
        try:
            chrome_options = Options()
            if config.HEADLESS_BROWSER:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument(f'user-agent={random.choice(config.USER_AGENTS)}')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("Selenium WebDriver initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Selenium: {e}")
            self.driver = None
    
    def _close_selenium(self):
        """Close Selenium WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Selenium WebDriver closed")
            except Exception as e:
                self.logger.error(f"Error closing Selenium: {e}")
    
    def _make_request(self, url: str, use_selenium: bool = False) -> Optional[str]:
        """
        Make HTTP request with error handling and retries
        
        Args:
            url: URL to fetch
            use_selenium: Whether to use Selenium for JavaScript rendering
            
        Returns:
            HTML content or None if failed
        """
        for attempt in range(config.MAX_RETRIES):
            try:
                if use_selenium and config.USE_SELENIUM:
                    self._setup_selenium()
                    if self.driver:
                        self.driver.get(url)
                        time.sleep(config.REQUEST_DELAY)
                        return self.driver.page_source
                
                # Use requests for static content
                response = self.session.get(
                    url,
                    timeout=config.TIMEOUT,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    time.sleep(config.REQUEST_DELAY)  # Throttling
                    return response.text
                elif response.status_code == 404:
                    self.logger.warning(f"Page not found (404): {url}")
                    return None
                elif response.status_code == 403:
                    self.logger.warning(f"Access forbidden (403): {url}")
                    return None
                else:
                    self.logger.warning(f"HTTP {response.status_code} for {url}")
                    
            except requests.exceptions.Timeout:
                self.logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request error on attempt {attempt + 1} for {url}: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error on attempt {attempt + 1} for {url}: {e}")
            
            if attempt < config.MAX_RETRIES - 1:
                time.sleep(config.RETRY_DELAY)
        
        self.logger.error(f"Failed to fetch {url} after {config.MAX_RETRIES} attempts")
        return None
    
    def scrape_categories(self) -> List[Dict]:
        """
        Scrape all product categories from Noel Leeming
        
        Returns:
            List of category dictionaries with name and URL
        """
        self.logger.info("Scraping categories...")
        categories = []
        
        html = self._make_request(config.CATEGORIES_URL)
        if not html:
            self.logger.error("Failed to fetch categories page")
            return categories
        
        soup = BeautifulSoup(html, 'lxml')
        
        # This is a generic implementation - actual selectors need to be adjusted
        # based on the real Noel Leeming website structure
        category_selectors = [
            'nav a[href*="/shop/"]',
            '.category-link',
            '.nav-category a',
            'a[data-category]'
        ]
        
        for selector in category_selectors:
            category_links = soup.select(selector)
            if category_links:
                for link in category_links:
                    href = link.get('href', '')
                    if href and '/shop/' in href:
                        category_url = urljoin(config.BASE_URL, href)
                        category_name = link.get_text(strip=True)
                        
                        if category_url not in [c['url'] for c in categories]:
                            categories.append({
                                'name': category_name,
                                'url': category_url
                            })
                            self.logger.info(f"Found category: {category_name}")
                break
        
        if not categories:
            # Fallback: Try to find any links that might be categories
            self.logger.warning("No categories found with standard selectors, using fallback")
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                if '/shop/' in href or '/c/' in href:
                    category_url = urljoin(config.BASE_URL, href)
                    category_name = link.get_text(strip=True)
                    if category_name and category_url not in [c['url'] for c in categories]:
                        categories.append({
                            'name': category_name,
                            'url': category_url
                        })
        
        self.categories = categories
        self.logger.info(f"Found {len(categories)} categories")
        return categories
    
    def scrape_products_from_category(self, category_url: str, category_name: str) -> List[Dict]:
        """
        Scrape all products from a category
        
        Args:
            category_url: URL of the category page
            category_name: Name of the category
            
        Returns:
            List of product dictionaries
        """
        self.logger.info(f"Scraping products from category: {category_name}")
        products = []
        page = 1
        max_pages = 100  # Safety limit
        
        while page <= max_pages:
            # Construct paginated URL (adjust based on actual website structure)
            if '?' in category_url:
                paginated_url = f"{category_url}&page={page}"
            else:
                paginated_url = f"{category_url}?page={page}"
            
            html = self._make_request(paginated_url)
            if not html:
                break
            
            soup = BeautifulSoup(html, 'lxml')
            
            # Find product links (adjust selectors based on actual website)
            product_selectors = [
                '.product-item a[href*="/p/"]',
                'a.product-link[href*="/p/"]',
                'div.product a',
                'article.product a'
            ]
            
            product_links = []
            for selector in product_selectors:
                product_links = soup.select(selector)
                if product_links:
                    break
            
            if not product_links:
                self.logger.info(f"No products found on page {page} of {category_name}")
                break
            
            self.logger.info(f"Found {len(product_links)} products on page {page}")
            
            for link in product_links:
                product_url = urljoin(config.BASE_URL, link.get('href', ''))
                if product_url and product_url not in [p.get('url') for p in products]:
                    products.append({'url': product_url, 'category': category_name})
            
            page += 1
            
            # Check if there's a next page
            next_page = soup.find('a', {'rel': 'next'}) or soup.find('a', text='Next')
            if not next_page:
                break
        
        self.logger.info(f"Found {len(products)} total products in {category_name}")
        return products
    
    def scrape_product_details(self, product_url: str, category: str) -> Optional[Dict]:
        """
        Scrape detailed information from a product page
        
        Args:
            product_url: URL of the product page
            category: Category name
            
        Returns:
            Dictionary with product details or None if failed
        """
        html = self._make_request(product_url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'lxml')
        
        try:
            # Extract product name (adjust selectors based on actual website)
            name_selectors = ['h1.product-name', 'h1.product-title', 'h1[itemprop="name"]', 'h1']
            product_name = None
            for selector in name_selectors:
                element = soup.select_one(selector)
                if element:
                    product_name = element.get_text(strip=True)
                    break
            
            # Extract price
            price_selectors = [
                '.price-value',
                '[itemprop="price"]',
                '.product-price',
                'span.price'
            ]
            price = None
            for selector in price_selectors:
                element = soup.select_one(selector)
                if element:
                    price_text = element.get_text(strip=True)
                    # Extract numeric value
                    price = ''.join(filter(lambda x: x.isdigit() or x == '.', price_text))
                    break
            
            # Extract description
            description_selectors = [
                '.product-description',
                '[itemprop="description"]',
                '.description',
                'div.product-details p'
            ]
            description = None
            for selector in description_selectors:
                element = soup.select_one(selector)
                if element:
                    description = element.get_text(strip=True)
                    break
            
            # Extract images
            image_selectors = [
                'img.product-image',
                'img[itemprop="image"]',
                '.product-gallery img',
                'img.main-image'
            ]
            images = []
            for selector in image_selectors:
                img_elements = soup.select(selector)
                if img_elements:
                    for img in img_elements:
                        img_url = img.get('src') or img.get('data-src')
                        if img_url:
                            images.append(urljoin(config.BASE_URL, img_url))
                    break
            
            # Extract specifications/attributes
            specs = {}
            spec_selectors = [
                '.specifications table tr',
                '.product-specs li',
                '.attributes li'
            ]
            for selector in spec_selectors:
                spec_elements = soup.select(selector)
                if spec_elements:
                    for spec in spec_elements:
                        # Try to extract key-value pairs
                        text = spec.get_text(strip=True)
                        if ':' in text:
                            key, value = text.split(':', 1)
                            specs[key.strip()] = value.strip()
                    break
            
            # Extract rating
            rating = None
            rating_selectors = [
                '[itemprop="ratingValue"]',
                '.rating-value',
                '.star-rating'
            ]
            for selector in rating_selectors:
                element = soup.select_one(selector)
                if element:
                    rating = element.get_text(strip=True) or element.get('content')
                    break
            
            # Extract SKU/Product ID
            sku = None
            sku_selectors = [
                '[itemprop="sku"]',
                '.product-sku',
                '.product-code'
            ]
            for selector in sku_selectors:
                element = soup.select_one(selector)
                if element:
                    sku = element.get_text(strip=True) or element.get('content')
                    break
            
            product = {
                'name': product_name or 'N/A',
                'price': price or 'N/A',
                'description': description or 'N/A',
                'images': images,
                'specifications': specs,
                'rating': rating or 'N/A',
                'sku': sku or 'N/A',
                'url': product_url,
                'category': category
            }
            
            return product
            
        except Exception as e:
            self.logger.error(f"Error extracting product details from {product_url}: {e}")
            return None
    
    def scrape_all(self, resume: bool = True) -> List[Dict]:
        """
        Main method to scrape all products from all categories
        
        Args:
            resume: Whether to resume from checkpoint if available
            
        Returns:
            List of all scraped products
        """
        self.logger.info("Starting full scrape of Noel Leeming website")
        
        # Try to resume from checkpoint
        checkpoint = None
        if resume and config.ENABLE_CHECKPOINTS:
            checkpoint = load_checkpoint(self.checkpoint_file)
            if checkpoint:
                self.logger.info(f"Resuming from checkpoint: {checkpoint['completed_products']} products completed")
                self.products = checkpoint.get('products', [])
                self.categories = checkpoint.get('categories', [])
        
        # Scrape categories if not in checkpoint
        if not self.categories:
            self.categories = self.scrape_categories()
            if not self.categories:
                self.logger.error("No categories found. Aborting.")
                return []
        
        # Track completed product URLs for resume functionality
        completed_urls = set(p.get('url') for p in self.products if p.get('url'))
        
        # Scrape products from each category
        for cat_idx, category in enumerate(self.categories):
            if checkpoint and cat_idx < checkpoint.get('current_category_index', 0):
                continue
            
            self.logger.info(f"Processing category {cat_idx + 1}/{len(self.categories)}: {category['name']}")
            
            # Get product URLs from category
            product_list = self.scrape_products_from_category(
                category['url'],
                category['name']
            )
            
            # Scrape details for each product
            for prod_idx, product_info in enumerate(product_list):
                product_url = product_info['url']
                
                # Skip if already completed
                if product_url in completed_urls:
                    continue
                
                self.logger.info(f"Scraping product {len(self.products) + 1}: {product_url}")
                
                product_details = self.scrape_product_details(
                    product_url,
                    product_info['category']
                )
                
                if product_details:
                    self.products.append(product_details)
                    completed_urls.add(product_url)
                    
                    # Save checkpoint periodically
                    if config.ENABLE_CHECKPOINTS and len(self.products) % config.CHECKPOINT_INTERVAL == 0:
                        checkpoint_data = {
                            'products': self.products,
                            'categories': self.categories,
                            'current_category_index': cat_idx,
                            'completed_products': len(self.products)
                        }
                        save_checkpoint(checkpoint_data, self.checkpoint_file)
                        self.logger.info(f"Checkpoint saved: {len(self.products)} products")
        
        # Final checkpoint
        if config.ENABLE_CHECKPOINTS:
            checkpoint_data = {
                'products': self.products,
                'categories': self.categories,
                'current_category_index': len(self.categories),
                'completed_products': len(self.products)
            }
            save_checkpoint(checkpoint_data, self.checkpoint_file)
        
        self._close_selenium()
        self.logger.info(f"Scraping completed! Total products: {len(self.products)}")
        return self.products
    
    def get_products(self) -> List[Dict]:
        """Get the list of scraped products"""
        return self.products
