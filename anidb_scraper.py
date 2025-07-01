#!/usr/bin/env python3
"""
AniDB Top Anime Scraper
Scrapes top 20 anime from various categories on AniDB
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import re
from typing import List, Dict, Optional


class AniDBScraper:
    def __init__(self):
        self.base_url = "https://anidb.net"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Updated categories with more likely working URLs
        self.categories = {
            'top_anime': '/anime/',
            'highest_rated': '/anime/',  # Will need to sort by rating
            'most_popular': '/anime/',   # Will need to sort by popularity
            'most_watched': '/anime/',   # Will need to sort differently
            'newest': '/anime/',         # Will sort by newest
        }
    
    def scrape_category(self, category: str, limit: int = 20) -> List[Dict]:
        """Scrape top anime from a specific category"""
        if category not in self.categories:
            print(f"Category '{category}' not found. Available categories: {list(self.categories.keys())}")
            return []
        
        url = self.base_url + self.categories[category]
        print(f"Scraping {category} from {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            anime_list = []
            
            # AniDB uses different structures, try multiple selectors
            anime_rows = self._find_anime_rows(soup)
            
            for i, row in enumerate(anime_rows[:limit]):
                if i >= limit:
                    break
                    
                anime_data = self._extract_anime_data(row, i + 1)
                if anime_data:
                    anime_list.append(anime_data)
                
                # Rate limiting
                time.sleep(0.5)
            
            return anime_list
            
        except requests.RequestException as e:
            print(f"Error scraping {category}: {e}")
            return []
    
    def _find_anime_rows(self, soup):
        """Find anime rows using multiple possible selectors"""
        # Try different possible selectors for AniDB
        selectors = [
            'table.animelist tr',
            'div.anime_list .anime',
            'tr.g_odd, tr.g_even', 
            'table tr[class*="g_"]',
            '.animetable tr',
            'table tr',  # More generic
            '.data tr'   # Another common pattern
        ]
        
        for selector in selectors:
            rows = soup.select(selector)
            if rows and len(rows) > 1:  # Skip header row
                print(f"Found {len(rows)} rows with selector: {selector}")
                return rows[1:] if selector.startswith('table') else rows
        
        # Fallback: look for any table rows
        tables = soup.find_all('table')
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            if len(rows) > 3:  # Likely an anime list
                print(f"Using table {i} with {len(rows)} rows")
                return rows[1:]  # Skip header
        
        # Last resort: look for any links that might be anime
        links = soup.find_all('a', href=True)
        anime_links = [link for link in links if '/anime/' in link.get('href', '')]
        if anime_links:
            print(f"Found {len(anime_links)} anime links as backup")
            return anime_links[:20]  # Limit to reasonable number
        
        print("No anime data found")
        return []
    
    def _extract_anime_data(self, row, rank: int) -> Optional[Dict]:
        """Extract anime data from a row element"""
        try:
            # Handle if row is actually a link (backup method)
            if row.name == 'a':
                title = row.text.strip()
                anime_url = self.base_url + row.get('href', '')
                return {
                    'rank': str(rank),
                    'title': title,
                    'score': "N/A",
                    'url': anime_url,
                    'additional_info': "",
                    'source': 'AniDB'
                }
            
            # For AniDB table structure: No | Image | Title | Award | Type | ...
            cells = row.find_all(['td', 'th'])
            
            if len(cells) < 3:  # Not enough cells for anime data
                return None
            
            # Extract rank from first cell
            rank_text = cells[0].get_text(strip=True)
            if rank_text.isdigit():
                actual_rank = rank_text
            else:
                actual_rank = str(rank)
            
            # Title and URL - check both image cell (index 1) and title cell (index 2)
            title = "N/A"
            anime_url = "N/A"
            
            # First try the image cell for anime link
            image_cell = cells[1] if len(cells) > 1 else None
            if image_cell:
                image_links = image_cell.find_all('a', href=re.compile(r'/anime/\d+'))
                if image_links:
                    anime_url = self.base_url + image_links[0].get('href', '')
            
            # Then try the title cell
            title_cell = cells[2] if len(cells) > 2 else None
            if title_cell:
                title_links = title_cell.find_all('a', href=re.compile(r'/anime/\d+'))
                if title_links:
                    title_link = title_links[0]
                    title = title_link.get('title', '') or title_link.get_text(strip=True)
                    if not anime_url or anime_url == "N/A":
                        anime_url = self.base_url + title_link.get('href', '')
                else:
                    # If no link, try to get text directly
                    title_text = title_cell.get_text(strip=True)
                    if title_text and title_text != '?':
                        title = title_text
            
            # If title is still "?" or empty, try to get it from the anime URL by making a request
            # (This is expensive, so we'll skip it for now)
            
            # Type information (usually in cell 4)
            anime_type = "N/A"
            if len(cells) > 4:
                type_text = cells[4].get_text(strip=True)
                if type_text:
                    anime_type = type_text
            
            # Score - AniDB doesn't show scores on the main list, so leave as N/A
            score = "N/A"
            
            # Additional info
            additional_info = anime_type
            
            # Only return data if we have meaningful information
            if (title != "N/A" and title != '?' and len(title) > 0) or anime_url != "N/A":
                return {
                    'rank': actual_rank,
                    'title': title if title not in ["N/A", '?'] else f"Anime #{actual_rank}",
                    'score': score,
                    'url': anime_url,
                    'additional_info': additional_info,
                    'source': 'AniDB'
                }
            else:
                return None
            
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
            time.sleep(3)
        
        return all_data
    
    def save_to_json(self, data: Dict, filename: str = 'anidb_anime_data.json'):
        """Save data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Data saved to {filename}")
    
    def save_to_csv(self, data: Dict, filename: str = 'anidb_anime_data.csv'):
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
    scraper = AniDBScraper()
    
    # Option 1: Scrape specific category
    # category_data = scraper.scrape_category('highest_rated', 20)
    
    # Option 2: Scrape all categories
    all_data = scraper.scrape_all_categories(20)
    
    # Save data
    scraper.save_to_json(all_data, 'anidb_top_anime.json')
    scraper.save_to_csv(all_data, 'anidb_top_anime.csv')


if __name__ == "__main__":
    main() 