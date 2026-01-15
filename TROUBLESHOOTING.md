# Troubleshooting Guide for NLScraper

This guide covers common issues and their solutions.

## Table of Contents
- [Installation Issues](#installation-issues)
- [Scraping Issues](#scraping-issues)
- [Image Download Issues](#image-download-issues)
- [Export Issues](#export-issues)
- [Performance Issues](#performance-issues)
- [Network Issues](#network-issues)

## Installation Issues

### Python Version Error
**Problem**: Error about Python version when installing dependencies

**Solution**:
```bash
# Check your Python version
python --version

# NLScraper requires Python 3.8+
# Install Python 3.8 or higher from python.org
```

### Dependency Installation Fails
**Problem**: `pip install -r requirements.txt` fails

**Solution**:
```bash
# Update pip first
pip install --upgrade pip

# Install dependencies one by one if batch fails
pip install scrapy
pip install selenium
pip install beautifulsoup4
# ... etc

# On Windows, you may need Visual C++ Build Tools for some packages
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

### Selenium/ChromeDriver Issues
**Problem**: Selenium fails to start or can't find ChromeDriver

**Solution**:
```bash
# Make sure Chrome is installed
# ChromeDriver should auto-install, but if it fails:

# Option 1: Set USE_SELENIUM = False in config.py (if not needed)

# Option 2: Manually install ChromeDriver
# Download from: https://chromedriver.chromium.org/
# Add to PATH

# Option 3: Use webdriver-manager (already in requirements)
pip install --upgrade webdriver-manager
```

## Scraping Issues

### No Categories Found
**Problem**: Scraper reports "No categories found"

**Solution**:
1. Check if website is accessible:
   ```bash
   curl -I https://www.noelleeming.co.nz
   ```

2. Website structure may have changed. Update selectors in `scraper.py`:
   ```python
   # In scrape_categories() method, try different selectors
   category_selectors = [
       'nav a[href*="/shop/"]',  # Update these
       '.category-link',
       '.nav-category a',
   ]
   ```

3. Enable DEBUG logging to see what's being scraped:
   ```bash
   python main.py --log-level DEBUG
   ```

### No Products Found in Category
**Problem**: Scraper finds categories but no products

**Solution**:
1. Check product selectors in `scraper.py`:
   ```python
   # In scrape_products_from_category() method
   product_selectors = [
       '.product-item a[href*="/p/"]',  # Update these
       'a.product-link[href*="/p/"]',
   ]
   ```

2. Verify pagination works correctly

3. Some categories might be empty - this is normal

### Missing Product Data
**Problem**: Some fields are missing or show "N/A"

**Solution**:
1. This is expected - not all products have all fields

2. Check if selectors need updating:
   ```bash
   # Run with DEBUG to see extraction details
   python main.py --log-level DEBUG --max-products 5
   ```

3. Update selectors in `scrape_product_details()` method

### Rate Limiting / IP Blocking
**Problem**: Getting 403 errors or blocked

**Solution**:
1. Increase delay between requests:
   ```python
   # In config.py
   REQUEST_DELAY = 5  # Increase from 2 to 5 seconds
   ```

2. Use VPN or wait before retrying

3. Check if you've been temporarily blocked:
   ```bash
   # Test website access
   curl https://www.noelleeming.co.nz
   ```

4. Reduce concurrent requests:
   ```python
   CONCURRENT_REQUESTS = 1  # More respectful
   ```

### Captcha Encountered
**Problem**: Website shows captcha

**Solution**:
1. Increase delays to appear more human-like:
   ```python
   REQUEST_DELAY = 5
   ```

2. Enable Selenium (may help with some captchas):
   ```python
   USE_SELENIUM = True
   ```

3. If persistent, you may need to solve captchas manually or use a captcha-solving service (not included)

## Image Download Issues

### Images Not Downloading
**Problem**: No images in `images/` folder

**Solution**:
1. Check if image download is enabled:
   ```python
   # In config.py
   DOWNLOAD_IMAGES = True
   ```

2. Check permissions on `images/` directory:
   ```bash
   ls -la images/
   chmod 755 images/
   ```

3. Check logs for specific image errors:
   ```bash
   grep "image" logs/scraper.log
   ```

### Invalid Images
**Problem**: Downloaded images are corrupted

**Solution**:
1. The scraper verifies images before saving

2. Source images might be corrupted - check URLs manually

3. Adjust timeout settings:
   ```python
   TIMEOUT = 60  # Increase for slow connections
   ```

### Image Storage Space
**Problem**: Running out of disk space

**Solution**:
1. Disable image download for testing:
   ```bash
   python main.py --no-images
   ```

2. Reduce image quality:
   ```python
   IMAGE_QUALITY = 'medium'  # or 'low'
   ```

3. Set max image size:
   ```python
   MAX_IMAGE_SIZE = 1 * 1024 * 1024  # 1MB max
   ```

## Export Issues

### No Output File Created
**Problem**: Scraping completes but no CSV/Excel file

**Solution**:
1. Check if products were actually scraped:
   ```bash
   cat logs/scraper.log | grep "Total products"
   ```

2. Check permissions on `output/` directory:
   ```bash
   ls -la output/
   chmod 755 output/
   ```

3. Check for export errors in logs:
   ```bash
   grep "export" logs/scraper.log
   ```

### Excel Export Fails
**Problem**: Error when exporting to Excel

**Solution**:
1. Install openpyxl:
   ```bash
   pip install openpyxl
   ```

2. Use CSV instead:
   ```bash
   python main.py --format csv
   ```

3. Check if file is locked/open:
   - Close Excel if output file is open
   - Delete any partial/corrupted files

### CSV Encoding Issues
**Problem**: Special characters appear wrong in CSV

**Solution**:
1. CSV is exported with UTF-8-BOM encoding (Excel compatible)

2. When opening in Excel, use "Import Data" feature:
   - Data → From Text/CSV
   - Select UTF-8 encoding

3. Open with text editor first to verify content

## Performance Issues

### Scraper is Too Slow
**Problem**: Scraping takes very long

**Solution**:
1. Reduce delays (but be respectful):
   ```python
   REQUEST_DELAY = 1  # Minimum recommended
   ```

2. Disable image downloads for faster scraping:
   ```bash
   python main.py --no-images
   ```

3. Test with limited products first:
   ```bash
   python main.py --max-products 100
   ```

4. Disable Selenium if not needed:
   ```python
   USE_SELENIUM = False
   ```

### High Memory Usage
**Problem**: Scraper uses too much RAM

**Solution**:
1. Reduce checkpoint interval (saves more often):
   ```python
   CHECKPOINT_INTERVAL = 25  # Save every 25 products
   ```

2. Process in batches using `--max-products`

3. Close unnecessary programs

### Scraper Crashes
**Problem**: Scraper terminates unexpectedly

**Solution**:
1. Check logs for error:
   ```bash
   tail -50 logs/scraper.log
   ```

2. Resume from checkpoint:
   ```bash
   python main.py --resume
   ```

3. Enable more error handling:
   ```python
   CONTINUE_ON_ERROR = True
   ```

## Network Issues

### Connection Timeout
**Problem**: Frequent timeout errors

**Solution**:
1. Increase timeout:
   ```python
   TIMEOUT = 60  # Increase from 30 to 60 seconds
   ```

2. Check internet connection:
   ```bash
   ping www.noelleeming.co.nz
   ```

3. Increase retries:
   ```python
   MAX_RETRIES = 5
   RETRY_DELAY = 10
   ```

### DNS Resolution Fails
**Problem**: Can't resolve website hostname

**Solution**:
1. Check DNS settings

2. Try using Google DNS (8.8.8.8)

3. Verify website is up:
   ```bash
   nslookup www.noelleeming.co.nz
   ```

### SSL Certificate Errors
**Problem**: SSL verification fails

**Solution**:
1. Update certifi:
   ```bash
   pip install --upgrade certifi
   ```

2. Update requests library:
   ```bash
   pip install --upgrade requests
   ```

## Resume Issues

### Can't Resume from Checkpoint
**Problem**: `--resume` doesn't work

**Solution**:
1. Check if checkpoint file exists:
   ```bash
   ls -la checkpoints/
   ```

2. Checkpoint might be corrupted - start fresh:
   ```bash
   python main.py --no-resume
   ```

3. Enable checkpoints in config:
   ```python
   ENABLE_CHECKPOINTS = True
   ```

### Resume Duplicates Products
**Problem**: Some products appear twice after resume

**Solution**:
1. This shouldn't happen - URL deduplication is built-in

2. Check logs for issues

3. If it persists, start fresh and report as a bug

## General Debugging

### Enable Verbose Logging
```bash
python main.py --log-level DEBUG
```

### Check What's Being Scraped
```bash
# Watch logs in real-time
tail -f logs/scraper.log
```

### Test with Limited Products
```bash
# Test scraping just 5 products
python main.py --max-products 5 --log-level DEBUG
```

### Verify Dependencies
```bash
pip list | grep -E "scrapy|selenium|beautifulsoup4|pandas|requests"
```

### Clean Start
```bash
# Remove all cached data and start fresh
rm -rf checkpoints/*.checkpoint
rm -rf output/*
rm -rf images/*
rm -rf logs/*

python main.py --no-resume
```

## Getting Help

If you're still having issues:

1. Check the main README.md for documentation
2. Review logs in `logs/scraper.log`
3. Open an issue on GitHub with:
   - Error message
   - Log output
   - Steps to reproduce
   - Your configuration (remove sensitive data)

## Best Practices

1. **Always start with a small test**:
   ```bash
   python main.py --max-products 10 --no-images
   ```

2. **Monitor logs during scraping**:
   ```bash
   tail -f logs/scraper.log
   ```

3. **Be respectful to the website**:
   - Don't reduce delays too much
   - Don't run multiple scrapers simultaneously
   - Use reasonable checkpoint intervals

4. **Backup your data**:
   - Checkpoints are saved automatically
   - Export data periodically
   - Keep output files backed up

5. **Test configuration changes**:
   - Always test with `--max-products` first
   - Check logs for errors before full run
   - Verify output file is correct
