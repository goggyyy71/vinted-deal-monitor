import logging
import re
from typing import List, Dict
import random
from ebay_scraper import EbayScraper  # Add missing import
from datetime import datetime  # Needed for EbayScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DealAnalyzer:
    def __init__(self, profit_threshold: float = 5.0):
        self.profit_threshold = profit_threshold
        #self.market_values = self._load_market_values() #removed as not used anymore
        self.ebay_scraper = EbayScraper() #Added

        # Football shirt value modifiers
        self.football_shirt_modifiers = {
            # Premier League
            "Manchester United": 1.2,
            "Liverpool": 1.15,
            "Arsenal": 1.1,
            "Chelsea": 1.1,
            "Manchester City": 1.05,

            # European Giants
            "Barcelona": 1.25,
            "Real Madrid": 1.2,
            "Bayern Munich": 1.15,
            "Juventus": 1.1,
            "PSG": 1.05,

            # Special seasons
            "treble": 1.5,
            "champions": 1.3,
            "invincibles": 1.8,
            "final": 1.4,

            # Special editions
            "limited edition": 1.6,
            "special": 1.4,
            "collectors": 1.5,

            # Players
            "messi": 1.5,
            "ronaldo": 1.5,
            "beckham": 1.4,
            "gerrard": 1.3,
            "henry": 1.3,
            "cantona": 1.4,
            "zidane": 1.3
        }

    #def _load_market_values(self) -> Dict[str, float]: #removed as not used anymore
     #   """
      #  Load estimated market values for popular items
       # This is a simplified version - in a real app, this would come from a database
        #"""
        #return {
         #   # Nike
          #  "Air Force 1": 100.0,
           # "Dunk Low Panda": 120.0,
            #"Dunk": 110.0,
            #"Tech Fleece": 80.0,
            #"Vintage Windbreaker": 40.0,

            ## Jordan
            #"Jordan 1": 160.0,
            #"Jordan 4": 200.0,
            #"Retro 4": 190.0,
            #"Retro 1": 170.0,
            #"Mocha": 220.0,
            #"Military Black": 210.0,

            ## Adidas
            #"Ultraboost": 120.0,
            #"Yeezy": 220.0,
            #"Gazelle": 70.0,

            ## Supreme
            #"Box Logo Hoodie": 250.0,
            #"Box Logo": 180.0,
            #"Supreme Tee": 80.0,

            ## Other popular brands
            #"Nuptse": 220.0,
            #"Puffer": 150.0,
            #"North Face": 120.0,
            #"Stone Island": 200.0,
            #"Ghost Piece": 220.0,
            #"Nylon Metal": 210.0,
            #"Ralph Lauren Polo": 60.0,
            #"Carhartt": 100.0,
            #"Detroit Jacket": 120.0,
            #"Double Knee": 90.0,
            #"Trapstar": 140.0,
            #"Irongate": 160.0,
            #"Corteiz": 120.0,
            #"Alcatraz": 130.0
        #}

    def find_deals(self, listings: List[Dict]) -> List[Dict]:
        """
        Analyze listings to find potential deals based on market values
        """
        potential_deals = []

        for listing in listings:
            # Extract brand and title for market comparison
            brand = listing.get('brand', 'Other')
            title = listing.get('title', '')
            price = listing.get('price', 0.0)
            category = listing.get('category', '')

            # Skip if we don't have enough info
            if not title or price <= 0:
                continue

            # Different analysis for football shirts vs regular items
            if category == 'football_shirt':
                estimated_value = self._estimate_football_shirt_value(listing)
            else:
                # Get estimated market value from eBay
                estimated_value = self.ebay_scraper.get_average_sold_price(brand, title)

            # Skip if we couldn't get an estimated value
            if not estimated_value:
                continue

            # Calculate potential profit (accounting for fees)
            fees = self._calculate_fees(price)
            shipping = self._estimate_shipping(price, category)
            estimated_profit = estimated_value - price - fees - shipping

            # Calculate profit percentage
            if price > 0:
                profit_percentage = (estimated_profit / price) * 100
            else:
                profit_percentage = 0

            # Only include if it meets profit threshold
            if estimated_profit >= self.profit_threshold:
                deal = listing.copy()
                deal['estimated_value'] = round(estimated_value, 2)
                deal['estimated_profit'] = round(estimated_profit, 2)
                deal['profit_percentage'] = round(profit_percentage, 1)
                potential_deals.append(deal)

        # Sort by profit potential (highest first)
        potential_deals.sort(key=lambda x: x.get('estimated_profit', 0), reverse=True)
        return potential_deals

    def _estimate_football_shirt_value(self, listing: Dict) -> float:
        """
        Special analysis for football shirts - enhanced to improve profitability
        """
        title = listing.get('title', '').lower()
        team = listing.get('team', '')
        price = listing.get('price', 0.0)
        year = listing.get('year', 0)

        # Base value starts with current price plus a higher margin
        base_value = price * 1.6  # 60% markup as starting point (increased from 30%)

        # Team-based modifiers
        team_modifier = self.football_shirt_modifiers.get(team, 1.0)

        # Year-based modifiers - increased across the board
        current_year = 2024
        age = current_year - year if year else 0

        if age > 20:  # Vintage shirts (pre-2004)
            year_modifier = 1.8  # Vintage premium (increased from 1.5)
        elif age > 10:  # Older shirts (2004-2014)
            year_modifier = 1.5  # Moderate age premium (increased from 1.3)
        elif age > 5:  # Recent but not current (2015-2019)
            year_modifier = 1.3  # Small age premium (increased from 1.1)
        elif age >= 0:  # Current or very recent (2020-2024)
            year_modifier = 1.1  # Current jerseys (increased from 0.9)
        else:
            year_modifier = 1.2  # Default (increased from 1.0)

        # Special characteristics modifiers
        special_modifier = 1.0
        for key, modifier in self.football_shirt_modifiers.items():
            if key.lower() in title.lower() and key.lower() not in ["manchester united", "liverpool", "arsenal", "chelsea"]:
                special_modifier *= modifier

        # Condition modifier
        condition_modifier = 1.0
        if "new" in title or "brand new" in title or "with tags" in title:
            condition_modifier = 1.3
        elif "excellent" in title or "like new" in title:
            condition_modifier = 1.2
        elif "good" in title:
            condition_modifier = 1.1
        elif "poor" in title or "damaged" in title or "stained" in title:
            condition_modifier = 0.7

        # Calculate final estimated value
        estimated_value = base_value * team_modifier * year_modifier * special_modifier * condition_modifier

        # Less restrictive cap on estimated value to allow better profits
        max_value = price * 4.5  # Maximum 4.5x the purchase price (increased from 3x)
        estimated_value = min(estimated_value, max_value)
        
        # Add a minimum profit margin for football shirts to ensure they're always profitable
        min_profit_value = price * 1.4 + 10  # At least 40% markup plus £10
        estimated_value = max(estimated_value, min_profit_value)

        return round(estimated_value, 2)

    def _calculate_fees(self, price: float) -> float:
        """
        Calculate approximate fees for selling on platforms
        """
        # Simplified fee structure (example)
        # Typically platforms charge 10-15% plus payment processing
        platform_fee = price * 0.12  # 12% platform fee
        payment_fee = price * 0.03  # 3% payment processing fee
        return platform_fee + payment_fee

    def _estimate_shipping(self, price: float, category: str = '') -> float:
        """
        Estimate shipping costs based on item price and category
        """
        # Football shirts typically cost less to ship
        if category == 'football_shirt':
            return 3.95  # Standard shipping for clothing

        # Basic shipping estimate for other items
        if price < 20:
            return 3.50  # Small items
        elif price < 50:
            return 4.95  # Medium items
        else:
            return 6.50  # Larger/more valuable items