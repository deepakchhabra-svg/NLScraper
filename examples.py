#!/usr/bin/env python3
"""
Example usage scripts for NLScraper

This file demonstrates various ways to use the scraper programmatically
instead of using the command-line interface.
"""
import sys
import os

# Add parent directory to path if running as script
if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from scraper import NoelLeemingScraper
from image_downloader import ImageDownloader
from exporter import DataExporter
from utils import setup_logging


def example_basic_scrape():
    """Example 1: Basic scraping with default settings"""
    print("=" * 60)
    print("Example 1: Basic Scraping")
    print("=" * 60)
    
    # Initialize logger
    logger = setup_logging()
    
    # Create scraper instance
    scraper = NoelLeemingScraper()
    
    # Scrape all products (with resume enabled by default)
    products = scraper.scrape_all(resume=True)
    
    logger.info(f"Scraped {len(products)} products")
    
    # Export to CSV
    exporter = DataExporter()
    output_files = exporter.export(products)
    
    logger.info(f"Data exported to: {output_files}")
    
    return products


def example_scrape_with_images():
    """Example 2: Scraping with image downloads"""
    print("=" * 60)
    print("Example 2: Scraping with Images")
    print("=" * 60)
    
    logger = setup_logging()
    
    # Enable image downloads
    config.DOWNLOAD_IMAGES = True
    
    # Create scraper
    scraper = NoelLeemingScraper()
    
    # Scrape products
    products = scraper.scrape_all(resume=True)
    
    # Download images
    image_downloader = ImageDownloader()
    image_map = image_downloader.download_all_images(products)
    
    logger.info(f"Downloaded images for {len(image_map)} products")
    
    # Export with image paths
    exporter = DataExporter()
    output_files = exporter.export(products, image_map)
    
    logger.info(f"Data exported to: {output_files}")
    
    return products, image_map


def example_limited_scrape():
    """Example 3: Scraping limited products for testing"""
    print("=" * 60)
    print("Example 3: Limited Scraping (Testing)")
    print("=" * 60)
    
    logger = setup_logging()
    
    # Disable image downloads for faster testing
    config.DOWNLOAD_IMAGES = False
    
    # Create scraper
    scraper = NoelLeemingScraper()
    
    # Get categories first
    categories = scraper.scrape_categories()
    
    if not categories:
        logger.error("No categories found")
        return []
    
    # Scrape products from first category only
    first_category = categories[0]
    logger.info(f"Scraping products from: {first_category['name']}")
    
    product_list = scraper.scrape_products_from_category(
        first_category['url'],
        first_category['name']
    )
    
    # Scrape details for first 10 products
    products = []
    for i, product_info in enumerate(product_list[:10]):
        logger.info(f"Scraping product {i+1}/10")
        product = scraper.scrape_product_details(
            product_info['url'],
            product_info['category']
        )
        if product:
            products.append(product)
    
    # Export
    exporter = DataExporter()
    output_files = exporter.export(products)
    
    logger.info(f"Scraped {len(products)} test products")
    logger.info(f"Data exported to: {output_files}")
    
    return products


def example_custom_config():
    """Example 4: Using custom configuration"""
    print("=" * 60)
    print("Example 4: Custom Configuration")
    print("=" * 60)
    
    logger = setup_logging()
    
    # Customize settings
    config.REQUEST_DELAY = 3  # Slower, more respectful
    config.OUTPUT_FORMAT = 'excel'  # Excel instead of CSV
    config.DOWNLOAD_IMAGES = False
    config.TRADEME_COMPATIBLE = True
    config.LOG_LEVEL = 'DEBUG'  # Verbose logging
    
    logger.info("Using custom configuration:")
    logger.info(f"  - Request delay: {config.REQUEST_DELAY}s")
    logger.info(f"  - Output format: {config.OUTPUT_FORMAT}")
    logger.info(f"  - TradeMe format: {config.TRADEME_COMPATIBLE}")
    
    # Create scraper with custom settings
    scraper = NoelLeemingScraper()
    
    # Scrape products
    products = scraper.scrape_all(resume=True)
    
    # Export
    exporter = DataExporter()
    output_files = exporter.export(products)
    
    logger.info(f"Data exported to: {output_files}")
    
    return products


def example_single_category():
    """Example 5: Scraping a specific category"""
    print("=" * 60)
    print("Example 5: Single Category Scraping")
    print("=" * 60)
    
    logger = setup_logging()
    
    # Create scraper
    scraper = NoelLeemingScraper()
    
    # Get all categories
    categories = scraper.scrape_categories()
    
    if not categories:
        logger.error("No categories found")
        return []
    
    # Display categories
    logger.info("Available categories:")
    for i, cat in enumerate(categories):
        logger.info(f"  {i+1}. {cat['name']}")
    
    # Scrape a specific category (e.g., first one)
    selected_category = categories[0]
    logger.info(f"\nScraping category: {selected_category['name']}")
    
    # Get products from category
    product_list = scraper.scrape_products_from_category(
        selected_category['url'],
        selected_category['name']
    )
    
    # Scrape details for each product
    products = []
    for i, product_info in enumerate(product_list):
        logger.info(f"Scraping product {i+1}/{len(product_list)}")
        product = scraper.scrape_product_details(
            product_info['url'],
            product_info['category']
        )
        if product:
            products.append(product)
    
    # Export
    exporter = DataExporter()
    output_files = exporter.export(products)
    
    logger.info(f"Scraped {len(products)} products from {selected_category['name']}")
    logger.info(f"Data exported to: {output_files}")
    
    return products


def example_programmatic_export():
    """Example 6: Working with scraped data programmatically"""
    print("=" * 60)
    print("Example 6: Programmatic Data Manipulation")
    print("=" * 60)
    
    logger = setup_logging()
    
    # Scrape some products (limited for demo)
    config.DOWNLOAD_IMAGES = False
    scraper = NoelLeemingScraper()
    
    # For demo, create sample data instead of actual scraping
    # In real use, you would scrape actual products
    sample_products = [
        {
            'name': 'Sample Product 1',
            'price': '299.99',
            'description': 'A great product',
            'category': 'Electronics',
            'sku': 'SKU001',
            'rating': '4.5',
            'url': 'https://example.com/product1',
            'images': ['https://example.com/image1.jpg'],
            'specifications': {'Color': 'Black', 'Size': 'Large'}
        },
        {
            'name': 'Sample Product 2',
            'price': '499.99',
            'description': 'Another great product',
            'category': 'Electronics',
            'sku': 'SKU002',
            'rating': '4.8',
            'url': 'https://example.com/product2',
            'images': ['https://example.com/image2.jpg'],
            'specifications': {'Color': 'White', 'Size': 'Medium'}
        }
    ]
    
    logger.info(f"Working with {len(sample_products)} products")
    
    # Filter products by price
    expensive_products = [p for p in sample_products if float(p['price']) > 400]
    logger.info(f"Found {len(expensive_products)} expensive products (>$400)")
    
    # Group by category
    categories = {}
    for product in sample_products:
        cat = product['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(product)
    
    logger.info(f"Products grouped into {len(categories)} categories")
    for cat, prods in categories.items():
        logger.info(f"  - {cat}: {len(prods)} products")
    
    # Export filtered data
    exporter = DataExporter()
    output_files = exporter.export(expensive_products)
    
    logger.info(f"Filtered data exported to: {output_files}")
    
    return sample_products


def main():
    """Main function to demonstrate all examples"""
    print("\n" + "=" * 60)
    print("NLScraper Usage Examples")
    print("=" * 60)
    print("\nThis script demonstrates various ways to use NLScraper.")
    print("Uncomment the example you want to run.\n")
    
    # IMPORTANT: Uncomment ONE example at a time to run
    
    # Example 1: Basic scraping
    # products = example_basic_scrape()
    
    # Example 2: Scraping with images
    # products, image_map = example_scrape_with_images()
    
    # Example 3: Limited scraping for testing
    # products = example_limited_scrape()
    
    # Example 4: Custom configuration
    # products = example_custom_config()
    
    # Example 5: Single category scraping
    # products = example_single_category()
    
    # Example 6: Programmatic data manipulation
    products = example_programmatic_export()
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
