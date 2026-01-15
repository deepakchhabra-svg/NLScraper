"""
Image downloader module for product images
"""
import os
import logging
import hashlib
from typing import List, Optional
from urllib.parse import urlparse
import requests
from PIL import Image
from io import BytesIO

import config
from utils import sanitize_filename


class ImageDownloader:
    """Download and manage product images"""
    
    def __init__(self):
        """Initialize the image downloader"""
        self.logger = logging.getLogger('NLScraper.ImageDownloader')
        os.makedirs(config.IMAGES_DIR, exist_ok=True)
        self.downloaded_images = set()
    
    def _get_image_filename(self, url: str, product_name: str, index: int = 0) -> str:
        """
        Generate filename for image
        
        Args:
            url: Image URL
            product_name: Product name
            index: Image index for the product
            
        Returns:
            Sanitized filename
        """
        # Create a hash of the URL to ensure uniqueness
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        # Get file extension from URL
        parsed_url = urlparse(url)
        ext = os.path.splitext(parsed_url.path)[1]
        if not ext or ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            ext = f'.{config.IMAGE_FORMAT}'
        
        # Create filename
        safe_name = sanitize_filename(product_name)[:50]  # Limit name length
        filename = f"{safe_name}_{index}_{url_hash}{ext}"
        
        return filename
    
    def download_image(self, url: str, product_name: str, index: int = 0) -> Optional[str]:
        """
        Download a single image
        
        Args:
            url: Image URL
            product_name: Product name for filename
            index: Image index for the product
            
        Returns:
            Local path to downloaded image or None if failed
        """
        if not url or not config.DOWNLOAD_IMAGES:
            return None
        
        # Check if already downloaded
        if url in self.downloaded_images:
            self.logger.debug(f"Image already downloaded: {url}")
            return None
        
        try:
            # Download image
            response = requests.get(url, timeout=config.TIMEOUT, stream=True)
            
            if response.status_code != 200:
                self.logger.warning(f"Failed to download image (HTTP {response.status_code}): {url}")
                return None
            
            # Check file size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > config.MAX_IMAGE_SIZE:
                self.logger.warning(f"Image too large ({content_length} bytes): {url}")
                return None
            
            # Read image content
            image_data = response.content
            
            # Verify it's a valid image
            try:
                img = Image.open(BytesIO(image_data))
                img.verify()
            except Exception as e:
                self.logger.warning(f"Invalid image file: {url} - {e}")
                return None
            
            # Generate filename and save
            filename = self._get_image_filename(url, product_name, index)
            filepath = os.path.join(config.IMAGES_DIR, filename)
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            self.downloaded_images.add(url)
            self.logger.info(f"Downloaded image: {filename}")
            
            return filepath
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error downloading image {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error downloading image {url}: {e}")
            return None
    
    def download_product_images(self, product: dict) -> List[str]:
        """
        Download all images for a product
        
        Args:
            product: Product dictionary with 'images' list and 'name'
            
        Returns:
            List of local paths to downloaded images
        """
        if not config.DOWNLOAD_IMAGES:
            return []
        
        images = product.get('images', [])
        product_name = product.get('name', 'unknown')
        
        if not images:
            return []
        
        downloaded_paths = []
        
        for idx, image_url in enumerate(images):
            filepath = self.download_image(image_url, product_name, idx)
            if filepath:
                downloaded_paths.append(filepath)
        
        return downloaded_paths
    
    def download_all_images(self, products: List[dict]) -> dict:
        """
        Download images for all products
        
        Args:
            products: List of product dictionaries
            
        Returns:
            Dictionary mapping product URLs to local image paths
        """
        self.logger.info(f"Starting download of images for {len(products)} products")
        
        image_map = {}
        
        for idx, product in enumerate(products):
            product_url = product.get('url', '')
            self.logger.info(f"Downloading images for product {idx + 1}/{len(products)}")
            
            downloaded_paths = self.download_product_images(product)
            
            if downloaded_paths:
                image_map[product_url] = downloaded_paths
        
        self.logger.info(f"Image download complete. Downloaded {len(self.downloaded_images)} unique images")
        
        return image_map
