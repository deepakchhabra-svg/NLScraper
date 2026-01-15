"""
Robots.txt checker for ethical scraping
"""
import logging
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import requests

import config


class RobotsChecker:
    """Check and respect robots.txt rules"""
    
    def __init__(self):
        """Initialize the robots checker"""
        self.logger = logging.getLogger('NLScraper.RobotsChecker')
        self.rp = RobotFileParser()
        self.user_agent = config.USER_AGENTS[0] if config.USER_AGENTS else '*'
        self.loaded = False
    
    def load_robots_txt(self, base_url: str) -> bool:
        """
        Load robots.txt from the website
        
        Args:
            base_url: Base URL of the website
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            parsed_url = urlparse(base_url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            self.logger.info(f"Loading robots.txt from {robots_url}")
            
            # Try to fetch robots.txt
            response = requests.get(robots_url, timeout=10)
            
            if response.status_code == 200:
                self.rp.parse(response.text.splitlines())
                self.loaded = True
                self.logger.info("robots.txt loaded successfully")
                
                # Log crawl delay if present
                crawl_delay = self.rp.crawl_delay(self.user_agent)
                if crawl_delay:
                    self.logger.info(f"Crawl delay from robots.txt: {crawl_delay} seconds")
                    if crawl_delay > config.REQUEST_DELAY:
                        self.logger.warning(
                            f"Consider increasing REQUEST_DELAY to {crawl_delay} "
                            f"to respect robots.txt crawl delay"
                        )
                
                return True
            elif response.status_code == 404:
                self.logger.info("No robots.txt found (404) - proceeding with default settings")
                self.loaded = True
                return True
            else:
                self.logger.warning(f"Could not load robots.txt (HTTP {response.status_code})")
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading robots.txt: {e}")
            return False
    
    def can_fetch(self, url: str) -> bool:
        """
        Check if URL can be fetched according to robots.txt
        
        Args:
            url: URL to check
            
        Returns:
            True if allowed, False if disallowed
        """
        if not config.RESPECT_ROBOTS_TXT:
            return True
        
        if not self.loaded:
            # Try to load robots.txt if not already loaded
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            self.load_robots_txt(base_url)
        
        try:
            allowed = self.rp.can_fetch(self.user_agent, url)
            
            if not allowed:
                self.logger.warning(f"URL disallowed by robots.txt: {url}")
            
            return allowed
        except Exception as e:
            self.logger.error(f"Error checking robots.txt for {url}: {e}")
            # Default to allowing if there's an error
            return True
    
    def get_crawl_delay(self) -> float:
        """
        Get the crawl delay from robots.txt
        
        Returns:
            Crawl delay in seconds, or None if not specified
        """
        if not self.loaded:
            return None
        
        try:
            return self.rp.crawl_delay(self.user_agent)
        except Exception:
            return None
    
    def should_respect_delay(self) -> float:
        """
        Get the delay that should be respected
        
        Returns:
            Delay in seconds (max of config delay and robots.txt delay)
        """
        crawl_delay = self.get_crawl_delay()
        
        if crawl_delay and crawl_delay > config.REQUEST_DELAY:
            self.logger.info(
                f"Using crawl delay from robots.txt: {crawl_delay}s "
                f"(config: {config.REQUEST_DELAY}s)"
            )
            return crawl_delay
        
        return config.REQUEST_DELAY
