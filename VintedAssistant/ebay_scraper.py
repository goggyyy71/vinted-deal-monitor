
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import time
from datetime import datetime, timedelta
import statistics
import logging
import random

logger = logging.getLogger(__name__)

class EbayScraper:
    def __init__(self):
        self.base_url = "https://www.ebay.co.uk/sch/i.html"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "DNT": "1"
        }
        self.session = requests.Session()
        # Cache results to avoid too many requests
        self.price_cache = {}
        self.cache_expiry = 3600  # 1 hour
        
    def get_average_sold_price(self, brand: str, title: str) -> float:
        """
        Get average sold price from eBay or generate a reasonable estimate
        This is a fast fallback implementation for performance reasons
        """
        # Create a cache key
        cache_key = f"{brand}:{title}"
        
        # Return from cache if available
        if cache_key in self.price_cache:
            return self.price_cache[cache_key]["price"]
            
        # Generate reasonable estimated value based on brand and keywords
        base_price = 50.0  # Default base price
        
        # Brand-based pricing
        brand_multipliers = {
            "Nike": 1.3,
            "Adidas": 1.2,
            "Jordan": 1.8,
            "Supreme": 2.0,
            "The North Face": 1.5,
            "Stone Island": 1.7,
            "Puma": 1.1,
            "New Balance": 1.2,
            "Carhartt": 1.3,
            "Ralph Lauren": 1.1,
            "Trapstar": 1.6,
            "Corteiz": 1.4
        }
        
        # Apply brand multiplier
        multiplier = brand_multipliers.get(brand, 1.0)
        base_price *= multiplier
        
        # Key item types with their own base prices
        item_keywords = {
            "hoodie": 60,
            "jacket": 80,
            "puffer": 100,
            "nuptse": 120,
            "shoes": 70,
            "trainers": 65,
            "shirt": 40,
            "jersey": 50,
            "tee": 35,
            "joggers": 45,
            "pants": 50,
            "hat": 25,
            "cap": 25,
            "box logo": 150
        }
        
        # Check for specific item types in title
        title_lower = title.lower()
        for keyword, keyword_price in item_keywords.items():
            if keyword in title_lower:
                base_price = keyword_price * multiplier
                break
        
        # Add some randomness to price (±20%)
        price_variance = random.uniform(0.8, 1.2)
        final_price = base_price * price_variance
        
        # Store in cache
        self.price_cache[cache_key] = {
            "price": final_price,
            "timestamp": time.time()
        }
        
        return final_price

    def get_average_sold_price(self, brand: str, item_title: str) -> Optional[float]:
        """
        Get the average sold price for similar items on eBay
        For now, this is a mock implementation to avoid getting blocked
        """
        # Check cache first
        cache_key = f"{brand}:{item_title}"
        if cache_key in self.price_cache:
            cache_time, price = self.price_cache[cache_key]
            if datetime.now().timestamp() - cache_time < self.cache_expiry:
                return price
                
        logger.info(f"Using mock data for eBay prices for {brand}")
        # Mock implementation to avoid getting blocked
        base_prices = {
            "Nike": (60.0, 100.0),
            "Adidas": (50.0, 90.0),
            "Puma": (35.0, 65.0),
            "New Balance": (70.0, 110.0),
            "Jordan": (100.0, 180.0),
            "Reebok": (40.0, 70.0),
            "Supreme": (100.0, 200.0),
            "Palace": (80.0, 160.0),
            "Stussy": (70.0, 120.0),
            "BAPE": (100.0, 200.0),
            "Off-White": (150.0, 300.0),
            "Stone Island": (120.0, 250.0),
            "Carhartt": (50.0, 90.0),
            "The North Face": (80.0, 150.0),
            "Yeezy": (150.0, 250.0),
            "Fear of God": (120.0, 220.0),
            "Ralph Lauren": (40.0, 80.0),
            "Tommy Hilfiger": (35.0, 75.0),
            "Other": (30.0, 60.0)
        }
        
        price_range = base_prices.get(brand, (30.0, 70.0))
        price = random.uniform(price_range[0], price_range[1])
        
        # Special case adjustments based on item title
        title_lower = item_title.lower()
        if "jordan" in title_lower and "retro" in title_lower:
            price *= 1.5
        elif "nike" in title_lower and "dunk" in title_lower:
            price *= 1.3
        elif "yeezy" in title_lower:
            price *= 1.4
        elif "supreme" in title_lower and "box logo" in title_lower:
            price *= 1.8
        elif "vintage" in title_lower:
            price *= 1.2
            
        # Cache the result
        self.price_cache[cache_key] = (datetime.now().timestamp(), price)
        return round(price, 2)
