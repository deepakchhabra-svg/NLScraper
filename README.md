# NLScraper

A high-performance web scraper for the Noel Leeming website designed to extract comprehensive product information for manual upload to TradeMe.

## Features

- **Comprehensive Data Extraction**: Scrapes product names, descriptions, prices, images, specifications, ratings, and more
- **Image Management**: Automatic download of product images to a designated folder
- **Multiple Export Formats**: Outputs data in CSV or Excel format
- **TradeMe Compatibility**: Optional export format specifically designed for TradeMe upload requirements
- **Resume Capability**: Checkpoint system allows resuming from interruptions
- **Rate Limiting**: Built-in throttling to respect website servers and avoid overwhelming them
- **Error Handling**: Graceful handling of missing data, redirects, timeouts, and other edge cases
- **Configurable**: Extensive configuration options via `config.py`
- **Logging**: Detailed logging for monitoring and troubleshooting
- **Ethical Scraping**: Respects robots.txt, implements delays, and uses responsible scraping practices

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/deepakchhabra-svg/NLScraper.git
cd NLScraper
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the scraper with default settings:
```bash
python main.py
```

This will:
- Scrape all products from all categories on Noel Leeming
- Download product images to the `images/` directory
- Export data to CSV format in the `output/` directory
- Create a TradeMe-compatible version of the data

### Command Line Options

```bash
# Scrape without downloading images
python main.py --no-images

# Export to Excel format instead of CSV
python main.py --format excel

# Start fresh without resuming from checkpoint
python main.py --no-resume

# Disable TradeMe compatible format
python main.py --no-trademe

# Adjust request delay (in seconds)
python main.py --delay 3

# Limit number of products (useful for testing)
python main.py --max-products 100

# Change log level
python main.py --log-level DEBUG
```

### Configuration

Edit `config.py` to customize scraper behavior:

```python
# Request throttling
REQUEST_DELAY = 2  # Delay between requests in seconds

# Output format
OUTPUT_FORMAT = 'csv'  # 'csv' or 'excel'

# Image downloads
DOWNLOAD_IMAGES = True
IMAGE_QUALITY = 'high'

# Resume functionality
ENABLE_CHECKPOINTS = True
CHECKPOINT_INTERVAL = 50  # Save checkpoint every N products

# Selenium (for JavaScript-heavy pages)
USE_SELENIUM = False
HEADLESS_BROWSER = True
```

## Output

### Directory Structure

After running the scraper, the following directories will be created:

```
NLScraper/
├── output/              # Exported CSV/Excel files
├── images/              # Downloaded product images
├── checkpoints/         # Resume checkpoints
└── logs/               # Scraper logs
```

### Output Files

The scraper creates the following output files:

1. **Standard CSV/Excel**: Complete product data with all fields
   - Product Name
   - Price
   - Description
   - Category
   - SKU
   - Rating
   - Product URL
   - Image URLs
   - Local Image Paths
   - Specifications (dynamic columns)

2. **TradeMe CSV** (if enabled): Formatted specifically for TradeMe upload
   - Title
   - Category
   - Description
   - StartPrice
   - BuyNowPrice
   - Photos
   - Condition
   - ShippingInfo
   - SKU

## Resume Functionality

The scraper automatically saves checkpoints every 50 products (configurable). If the scraper is interrupted:

1. Simply run the scraper again with the `--resume` flag (enabled by default)
2. It will automatically resume from the last checkpoint
3. Already scraped products will be skipped
4. New products will be added to the existing data

To start fresh, use the `--no-resume` flag.

## Error Handling

The scraper includes robust error handling for:

- **Network Issues**: Automatic retries with exponential backoff
- **Missing Data**: Graceful fallbacks with 'N/A' values
- **Timeouts**: Configurable timeout settings with retries
- **Rate Limiting**: Automatic throttling and delays
- **Invalid Images**: Verification and skipping of corrupt images
- **HTTP Errors**: Proper handling of 404, 403, and other error codes

All errors are logged to `logs/scraper.log` for troubleshooting.

## Ethical Scraping Practices

This scraper is designed with ethical considerations:

- **Respects robots.txt**: Can be configured to honor website policies
- **Rate Limiting**: Implements delays between requests (default: 2 seconds)
- **User Agent Rotation**: Uses realistic user agents
- **Automatic Throttling**: Adjusts request rate based on server response
- **Resume Capability**: Avoids re-scraping the same data
- **Error Handling**: Doesn't hammer the server on errors

## Performance Optimization

The scraper is optimized for performance:

- **Concurrent Requests**: Configurable concurrency level
- **Session Management**: Reuses HTTP connections
- **Efficient Parsing**: Uses lxml parser for speed
- **Checkpoint System**: Saves progress to avoid data loss
- **Selective Image Download**: Only downloads unique images
- **Lazy Loading**: Processes data in batches

## Troubleshooting

### Common Issues

**Issue**: Scraper can't find any categories
- **Solution**: The website structure may have changed. Check logs for details and update selectors in `scraper.py`

**Issue**: Images not downloading
- **Solution**: Check `DOWNLOAD_IMAGES` setting in `config.py` and ensure write permissions for `images/` directory

**Issue**: Rate limiting or IP blocking
- **Solution**: Increase `REQUEST_DELAY` in `config.py` to 3-5 seconds

**Issue**: Selenium errors
- **Solution**: Make sure Chrome/ChromeDriver is installed. Set `USE_SELENIUM = False` if not needed

**Issue**: Out of memory errors
- **Solution**: Reduce `CHECKPOINT_INTERVAL` to save more frequently, or use `--max-products` flag for testing

### Logs

Check the log file for detailed information:
```bash
cat logs/scraper.log
```

For more verbose output, run with DEBUG level:
```bash
python main.py --log-level DEBUG
```

## Advanced Usage

### Using Selenium for JavaScript-Heavy Pages

If the website requires JavaScript rendering:

1. Set `USE_SELENIUM = True` in `config.py`
2. Install Chrome/Chromium browser
3. Run the scraper (ChromeDriver will be auto-installed)

### Custom Selectors

If website structure changes, update selectors in `scraper.py`:

```python
# Example: Update product name selector
name_selectors = ['h1.product-name', 'h1.product-title', 'h1[itemprop="name"]']
```

### Extending the Scraper

To add new data fields:

1. Update extraction logic in `scraper.py` → `scrape_product_details()`
2. Add new columns in `exporter.py` → `_prepare_data_for_export()`
3. Update TradeMe format if needed in `_prepare_trademe_format()`

## Testing

To test the scraper on a small dataset:

```bash
# Scrape only 10 products for testing
python main.py --max-products 10 --no-images

# Test with debug logging
python main.py --max-products 5 --log-level DEBUG
```

## Project Structure

```
NLScraper/
├── main.py                 # Entry point and CLI
├── scraper.py             # Main scraper logic
├── config.py              # Configuration settings
├── utils.py               # Utility functions
├── image_downloader.py    # Image download handler
├── exporter.py            # Data export to CSV/Excel
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── .gitignore            # Git ignore rules
```

## Dependencies

Main dependencies:
- **scrapy**: Web scraping framework
- **selenium**: Browser automation (optional)
- **beautifulsoup4**: HTML parsing
- **pandas**: Data manipulation and export
- **requests**: HTTP library
- **Pillow**: Image processing
- **openpyxl**: Excel file creation

See `requirements.txt` for complete list.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational and personal use only. Please respect the Noel Leeming website's terms of service and robots.txt file.

## Disclaimer

This scraper is provided as-is for educational purposes. Users are responsible for:
- Complying with Noel Leeming's terms of service
- Respecting robots.txt and rate limits
- Using the data ethically and legally
- Obtaining necessary permissions before scraping

The authors are not responsible for any misuse of this tool.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the troubleshooting section above
- Review the logs in `logs/scraper.log`

## Changelog

### Version 1.0.0 (Initial Release)
- Complete scraper implementation
- Multi-format export (CSV/Excel)
- Image download functionality
- Resume capability with checkpoints
- TradeMe compatibility
- Comprehensive error handling
- Detailed logging and documentation