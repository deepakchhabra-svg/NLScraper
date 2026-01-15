# Quick Start Guide for NLScraper

## 5-Minute Setup

### Step 1: Install Python
Make sure Python 3.8+ is installed:
```bash
python --version
```

If not installed, download from [python.org](https://www.python.org/downloads/)

### Step 2: Clone and Setup
```bash
# Clone the repository
git clone https://github.com/deepakchhabra-svg/NLScraper.git
cd NLScraper

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Run the Scraper
```bash
# Basic run - scrapes all products
python main.py

# Test run - scrape only 10 products
python main.py --max-products 10

# Fast test - 5 products, no images
python main.py --max-products 5 --no-images
```

### Step 4: Check Output
```bash
# View exported data
ls -l output/

# View downloaded images
ls -l images/

# Check logs
cat logs/scraper.log
```

## Common First-Time Issues

### Issue: "No module named 'scrapy'"
**Fix**: Make sure you installed dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Scraper is slow
**Fix**: Test with fewer products first:
```bash
python main.py --max-products 10 --no-images
```

### Issue: Getting blocked by website
**Fix**: Increase delay between requests:
```bash
python main.py --delay 5
```

## What Gets Created?

After running, you'll have:
- `output/noel_leeming_products_[timestamp].csv` - Product data
- `output/noel_leeming_products_trademe_[timestamp].csv` - TradeMe format (optional)
- `images/` - Downloaded product images
- `logs/scraper.log` - Detailed logs
- `checkpoints/scraper.checkpoint` - Resume point

## Next Steps

1. **Customize Settings**: Edit `config.py` to adjust scraper behavior
2. **Review Data**: Open CSV files in Excel or any spreadsheet program
3. **Upload to TradeMe**: Use the TradeMe-formatted CSV for manual upload
4. **Read Documentation**: Check README.md for advanced features

## Quick Commands Reference

```bash
# Standard scraping
python main.py

# Scrape without images (faster)
python main.py --no-images

# Export to Excel instead of CSV
python main.py --format excel

# Test with limited products
python main.py --max-products 20

# Resume from previous run
python main.py --resume

# Start fresh (ignore checkpoint)
python main.py --no-resume

# Adjust request delay
python main.py --delay 3

# Verbose logging for debugging
python main.py --log-level DEBUG

# Combination example
python main.py --format excel --no-images --delay 3 --max-products 50
```

## Configuration Tips

### For Faster Scraping
```python
# In config.py
REQUEST_DELAY = 1  # Minimum recommended
DOWNLOAD_IMAGES = False
USE_SELENIUM = False
```

### For More Reliable Scraping
```python
# In config.py
REQUEST_DELAY = 5  # More respectful
MAX_RETRIES = 5
TIMEOUT = 60
ENABLE_CHECKPOINTS = True
```

### For Testing
```python
# In config.py
LOG_LEVEL = 'DEBUG'
CHECKPOINT_INTERVAL = 10  # Save more often
```

## Monitoring Progress

### Watch logs in real-time
```bash
# In a separate terminal
tail -f logs/scraper.log
```

### Check how many products scraped
```bash
grep "Total products" logs/scraper.log
```

### See if any errors occurred
```bash
grep "ERROR" logs/scraper.log
```

## Resuming After Interruption

If the scraper stops (crash, Ctrl+C, power loss):

1. Simply run it again:
```bash
python main.py --resume
```

2. It will automatically continue from the last checkpoint

3. All previously scraped data is preserved

## Need Help?

- **Errors**: Check `logs/scraper.log`
- **Configuration**: See `config.py` and `config.example.py`
- **Detailed Docs**: Read `README.md`
- **Troubleshooting**: Check `TROUBLESHOOTING.md`
- **Issues**: Open an issue on GitHub

## Tips for Success

1. ✅ **Start small**: Test with 5-10 products first
2. ✅ **Monitor logs**: Watch for errors during first run
3. ✅ **Be patient**: Scraping large sites takes time
4. ✅ **Be respectful**: Don't reduce delays too much
5. ✅ **Backup data**: Keep output files safe
6. ✅ **Check output**: Verify CSV looks correct before uploading to TradeMe

## What to Expect

**Small Test** (10 products, no images):
- Time: ~30 seconds
- Output: 1 CSV file
- Data: Basic product info

**Medium Run** (100 products, with images):
- Time: ~10-15 minutes
- Output: 2 CSV files + ~300 images
- Data: Complete product details

**Full Run** (all products):
- Time: Several hours (depends on site size)
- Output: Full product database
- Data: Everything from Noel Leeming

## Safety Features

The scraper includes:
- ✅ Auto-save checkpoints (every 50 products)
- ✅ Error recovery (continues on failures)
- ✅ Request throttling (respects website)
- ✅ Detailed logging (tracks everything)
- ✅ Resume capability (never lose progress)

Happy scraping! 🚀
