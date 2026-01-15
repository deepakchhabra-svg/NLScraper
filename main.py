#!/usr/bin/env python3
"""
Main entry point for NLScraper
High-performance web scraper for Noel Leeming website
"""
import sys
import argparse
import logging
from typing import Optional

import config
from scraper import NoelLeemingScraper
from image_downloader import ImageDownloader
from exporter import DataExporter
from utils import setup_logging


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='NLScraper - High-performance web scraper for Noel Leeming',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic scraping with default settings
  python main.py
  
  # Scrape without downloading images
  python main.py --no-images
  
  # Resume from previous checkpoint
  python main.py --resume
  
  # Export to Excel format
  python main.py --format excel
  
  # Scrape without TradeMe format
  python main.py --no-trademe
        """
    )
    
    parser.add_argument(
        '--no-images',
        action='store_true',
        help='Skip downloading product images'
    )
    
    parser.add_argument(
        '--resume',
        action='store_true',
        default=True,
        help='Resume from previous checkpoint (default: True)'
    )
    
    parser.add_argument(
        '--no-resume',
        action='store_true',
        help='Start fresh scraping without resuming'
    )
    
    parser.add_argument(
        '--format',
        choices=['csv', 'excel'],
        default=config.OUTPUT_FORMAT,
        help=f'Output format (default: {config.OUTPUT_FORMAT})'
    )
    
    parser.add_argument(
        '--no-trademe',
        action='store_true',
        help='Disable TradeMe compatible format'
    )
    
    parser.add_argument(
        '--delay',
        type=int,
        default=config.REQUEST_DELAY,
        help=f'Delay between requests in seconds (default: {config.REQUEST_DELAY})'
    )
    
    parser.add_argument(
        '--max-products',
        type=int,
        help='Maximum number of products to scrape (for testing)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default=config.LOG_LEVEL,
        help=f'Logging level (default: {config.LOG_LEVEL})'
    )
    
    return parser.parse_args()


def main():
    """Main function"""
    args = parse_arguments()
    
    # Apply command line arguments to config
    if args.no_images:
        config.DOWNLOAD_IMAGES = False
    
    if args.no_resume:
        resume = False
    else:
        resume = args.resume
    
    config.OUTPUT_FORMAT = args.format
    
    if args.no_trademe:
        config.TRADEME_COMPATIBLE = False
    
    config.REQUEST_DELAY = args.delay
    config.LOG_LEVEL = args.log_level
    
    # Setup logging
    logger = setup_logging()
    
    logger.info("=" * 80)
    logger.info("NLScraper - High-Performance Noel Leeming Web Scraper")
    logger.info("=" * 80)
    logger.info(f"Configuration:")
    logger.info(f"  - Output format: {config.OUTPUT_FORMAT}")
    logger.info(f"  - Download images: {config.DOWNLOAD_IMAGES}")
    logger.info(f"  - TradeMe format: {config.TRADEME_COMPATIBLE}")
    logger.info(f"  - Request delay: {config.REQUEST_DELAY}s")
    logger.info(f"  - Resume mode: {resume}")
    logger.info(f"  - Log level: {config.LOG_LEVEL}")
    logger.info("=" * 80)
    
    try:
        # Initialize scraper
        logger.info("Initializing scraper...")
        scraper = NoelLeemingScraper()
        
        # Scrape all products
        logger.info("Starting scraping process...")
        products = scraper.scrape_all(resume=resume)
        
        if not products:
            logger.error("No products scraped. Exiting.")
            return 1
        
        logger.info(f"Successfully scraped {len(products)} products")
        
        # Limit products if specified (for testing)
        if args.max_products and len(products) > args.max_products:
            logger.info(f"Limiting to {args.max_products} products for testing")
            products = products[:args.max_products]
        
        # Download images
        image_map = {}
        if config.DOWNLOAD_IMAGES:
            logger.info("Downloading product images...")
            image_downloader = ImageDownloader()
            image_map = image_downloader.download_all_images(products)
            logger.info(f"Downloaded images for {len(image_map)} products")
        else:
            logger.info("Image downloading disabled")
        
        # Export data
        logger.info("Exporting data...")
        exporter = DataExporter()
        output_files = exporter.export(products, image_map)
        
        # Summary
        logger.info("=" * 80)
        logger.info("SCRAPING COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        logger.info(f"Total products scraped: {len(products)}")
        logger.info(f"Total images downloaded: {len(image_map)}")
        logger.info(f"Output files created:")
        for output_file in output_files:
            logger.info(f"  - {output_file}")
        logger.info("=" * 80)
        logger.info("You can now manually upload the data to TradeMe using the generated files.")
        logger.info("=" * 80)
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\nScraping interrupted by user")
        logger.info("Progress has been saved. You can resume by running the script again.")
        return 130
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
