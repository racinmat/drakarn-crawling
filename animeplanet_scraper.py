#!/usr/bin/env python3
"""
AnimePlanet Top Anime Scraper
Scrapes top 20 anime from various categories on AnimePlanet
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import re
from typing import List, Dict, Optional


class AnimePlanetScraper:
    def __init__(self):
        self.base_url = "https://www.anime-planet.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        })
        
        # Available categories on AnimePlanet
        self.categories = {
            'top_anime': '/anime/top-anime',
            'highest_rated': '/anime/top-anime?sort=rating&order=desc',
            'most_watched': '/anime/top-anime?sort=watching&order=desc',
            'most_completed': '/anime/top-anime?sort=completed&order=desc',
            'most_want_to_watch': '/anime/top-anime?sort=want_to_watch&order=desc',
            'newest': '/anime/top-anime?sort=newest&order=desc',
            'most_popular': '/anime/top-anime?sort=popularity&order=desc'
        }
    
    def scrape_category(self, category: str, limit: int = 20) -> List[Dict]:
        """Scrape top anime from a specific category"""
        if category not in self.categories:
            print(f"Category '{category}' not found. Available categories: {list(self.categories.keys())}")
            return []
        
        url = self.base_url + self.categories[category]
        print(f"Scraping {category} from {url}")
        
        # Add initial delay to avoid immediate blocking
        time.sleep(2)
        
        try:
            # Try multiple times with increasing delays
            for attempt in range(3):
                try:
                    response = self.session.get(url, timeout=30)
                    response.raise_for_status()
                    break
                except requests.exceptions.HTTPError as e:
                    if response.status_code == 403:
                        print(f"Attempt {attempt + 1}: Got 403 Forbidden, waiting {5 * (attempt + 1)} seconds...")
                        time.sleep(5 * (attempt + 1))
                        if attempt == 2:  # Last attempt
                            print("All attempts failed. AnimePlanet may be blocking requests.")
                            return []
                    else:
                        raise e
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            anime_list = []
            
            # AnimePlanet typically uses card-based layouts
            anime_cards = self._find_anime_cards(soup)
            
            for i, card in enumerate(anime_cards[:limit]):
                if i >= limit:
                    break
                    
                anime_data = self._extract_anime_data(card, i + 1)
                if anime_data:
                    anime_list.append(anime_data)
                
                # Rate limiting
                time.sleep(1.0)  # Increased delay
            
            return anime_list
            
        except requests.RequestException as e:
            print(f"Error scraping {category}: {e}")
            return []
    
    def _find_anime_cards(self, soup):
        """Find anime cards using multiple possible selectors"""
        # Try different possible selectors for AnimePlanet
        selectors = [
            'div.cardDeck ul li',
            '.entryBar',
            'tr.card',
            '.cardName',
            'li[data-type="anime"]',
            'div.card',
            'table.pure-table tr'
        ]
        
        for selector in selectors:
            cards = soup.select(selector)
            if cards and len(cards) >= 5:  # Reasonable number of results
                return cards
        
        # Fallback: look for list items or table rows
        fallback_selectors = ['li', 'tr']
        for selector in fallback_selectors:
            elements = soup.select(selector)
            # Filter elements that likely contain anime data
            anime_elements = []
            for elem in elements:
                if elem.find('a') and len(elem.text.strip()) > 10:
                    anime_elements.append(elem)
            if len(anime_elements) >= 5:
                return anime_elements[:50]  # Limit to reasonable number
        
        return []
    
    def _extract_anime_data(self, card, rank: int) -> Optional[Dict]:
        """Extract anime data from a card element"""
        try:
            # Title and URL
            title = "N/A"
            anime_url = "N/A"
            
            # Look for main anime link
            links = card.find_all('a')
            anime_link = None
            
            for link in links:
                href = link.get('href', '')
                if '/anime/' in href and link.text.strip():
                    anime_link = link
                    break
            
            if anime_link:
                title = anime_link.text.strip()
                anime_url = self.base_url + anime_link.get('href', '')
            
            # Rating/Score
            score = "N/A"
            
            # Look for rating indicators
            rating_selectors = [
                '.avgRating',
                '.rating',
                '.score',
                '[class*="rating"]',
                '[class*="score"]'
            ]
            
            for selector in rating_selectors:
                rating_elem = card.select_one(selector)
                if rating_elem:
                    rating_text = rating_elem.text.strip()
                    score_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if score_match:
                        score = score_match.group(1)
                        break
            
            # Additional info
            additional_info = ""
            
            # Look for metadata
            info_selectors = [
                '.type',
                '.year',
                '.episodes',
                '.metadata',
                '.tags'
            ]
            
            info_parts = []
            for selector in info_selectors:
                info_elem = card.select_one(selector)
                if info_elem:
                    info_text = info_elem.text.strip()
                    if info_text and info_text != title:
                        info_parts.append(info_text)
            
            additional_info = " | ".join(info_parts[:3])  # Limit to first 3 pieces of info
            
            # If no specific info found, try to extract from general text
            if not additional_info:
                card_text = card.text.strip()
                lines = [line.strip() for line in card_text.split('\n') if line.strip()]
                # Get lines that aren't the title and look informative
                for line in lines[1:4]:  # Skip title, take next few lines
                    if len(line) < 100 and line != title:  # Reasonable length
                        additional_info += line + " | "
                additional_info = additional_info.rstrip(" | ")
            
            return {
                'rank': str(rank),
                'title': title,
                'score': score,
                'url': anime_url,
                'additional_info': additional_info,
                'source': 'AnimePlanet'
            }
            
        except Exception as e:
            print(f"Error extracting anime data: {e}")
            return None
    
    def scrape_all_categories(self, limit: int = 20) -> Dict[str, List[Dict]]:
        """Scrape all available categories"""
        all_data = {}
        
        for category in self.categories.keys():
            print(f"\nScraping category: {category}")
            category_data = self.scrape_category(category, limit)
            all_data[category] = category_data
            
            # Longer delay between categories
            time.sleep(2)
        
        return all_data
    
    def save_to_json(self, data: Dict, filename: str = 'animeplanet_anime_data.json'):
        """Save data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Data saved to {filename}")
    
    def save_to_csv(self, data: Dict, filename: str = 'animeplanet_anime_data.csv'):
        """Save data to CSV file"""
        all_anime = []
        for category, anime_list in data.items():
            for anime in anime_list:
                anime['category'] = category
                all_anime.append(anime)
        
        if all_anime:
            fieldnames = ['category', 'rank', 'title', 'score', 'url', 'additional_info', 'source']
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_anime)
            print(f"Data saved to {filename}")


def main():
    scraper = AnimePlanetScraper()
    
    # Option 1: Scrape specific category
    # category_data = scraper.scrape_category('highest_rated', 20)
    
    # Option 2: Scrape all categories
    all_data = scraper.scrape_all_categories(20)
    
    # Save data
    scraper.save_to_json(all_data, 'animeplanet_top_anime.json')
    scraper.save_to_csv(all_data, 'animeplanet_top_anime.csv')


if __name__ == "__main__":
    main() 