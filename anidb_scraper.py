#!/usr/bin/env python3
"""
AniDB Tag-Based Anime Scraper
Scrapes top 20 anime from tag-based categories on AniDB using search functionality
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict, Optional
import urllib.parse
from base_scraper import BaseScraper


class AniDBScraper(BaseScraper):
    def __init__(self):
        super().__init__("anidb")
        self.base_url = "https://anidb.net"
        self.search_url = "https://anidb.net/search/anime"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Tag-based categories as requested (4 categories)
        self.categories = {
            'action_adventure_shounen': {
                'name': 'Action, Adventure, Shounen',
                'tags': ['action', 'adventure', 'shounen'],
                'description': 'Action, adventure, shounen anime'
            },
            'romance': {
                'name': 'Romance',
                'tags': ['romance'],
                'description': 'Romance anime'
            },
            'ecchi': {
                'name': 'Ecchi',
                'tags': ['ecchi'],
                'description': 'Ecchi anime'
            },
            'comedy': {
                'name': 'Comedy',
                'tags': ['comedy'],
                'description': 'Comedy anime'
            }
        }
    
    def _make_request(self, url: str, timeout: int) -> Optional[str]:
        """Make HTTP request using requests session"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Request failed: {e}")
            return None

    def scrape_category(self, category_key: str, limit: int = 20) -> List[Dict]:
        """Scrape anime from a specific tag-based category"""
        if category_key not in self.categories:
            print(f"Warning: Category '{category_key}' not found")
            return []
        
        category = self.categories[category_key]
        print(f"Scraping {category['name']} ({category['description']})...")
        
        # Use anime listing page with tag filters instead of search
        # AniDB anime list: https://anidb.net/anime/?tag.include=comedy&orderby.name=rating.rating&orderby.order=desc
        
        # Join tags with comma for AniDB's format
        tag_params = ",".join(category['tags'])
        
        # Build URL for tag-filtered anime list, sorted by rating descending
        url = f"{self.base_url}/anime/?tag.include={urllib.parse.quote(tag_params)}&orderby.name=rating.rating&orderby.order=desc"
        
        try:
            html_content = self._get_page_content(url)
            if not html_content:
                print(f"Failed to get content for {category['name']}")
                return []
            
            # Parse the anime list
            anime_list = self._parse_anime_list(html_content, category['name'], limit)
            print(f"Found {len(anime_list)} anime for {category['name']}")
            return anime_list
            
        except Exception as e:
            print(f"Error scraping {category['name']}: {e}")
            return []
    
    def _parse_anime_list(self, html_content: str, category_name: str, limit: int) -> List[Dict]:
        """Parse anime list from AniDB's anime listing page"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            anime_list = []
            
            # AniDB anime list uses table structure
            # Find the main anime table
            anime_table = soup.find('table', class_='animelist')
            if not anime_table:
                print("No anime table found on page")
                return []
            
            # Find anime rows in the table
            anime_rows = anime_table.find_all('tr')[1:]  # Skip header row
            
            for i, row in enumerate(anime_rows[:limit]):
                if i >= limit:
                    break
                
                try:
                    cells = row.find_all('td')
                    if len(cells) < 3:  # Need at least title, rating, etc.
                        continue
                    
                    # Extract anime data from table cells
                    # Usually: Title | Type | Episodes | Year | Rating | ... 
                    title_cell = cells[0] if cells else None
                    rating_cell = None
                    
                    # Find rating cell (usually contains numbers and decimal)
                    for cell in cells:
                        cell_text = cell.get_text(strip=True)
                        if re.match(r'\d+\.\d+', cell_text):
                            rating_cell = cell
                            break
                    
                    if not title_cell:
                        continue
                    
                    # Extract title and URL
                    title_link = title_cell.find('a')
                    if title_link:
                        title = title_link.get_text(strip=True)
                        anime_url = title_link.get('href', '')
                        if anime_url and not anime_url.startswith('http'):
                            anime_url = self.base_url + anime_url
                    else:
                        title = title_cell.get_text(strip=True)
                        anime_url = "N/A"
                    
                    # Extract rating
                    rating = "N/A"
                    if rating_cell:
                        rating_text = rating_cell.get_text(strip=True)
                        rating_match = re.search(r'(\d+\.\d+)', rating_text)
                        if rating_match:
                            rating = rating_match.group(1)
                    
                    # Extract additional info from other cells
                    additional_info = " | ".join([cell.get_text(strip=True) for cell in cells[1:3]]) if len(cells) > 1 else "N/A"
                    
                    anime_data = {
                        'rank': str(i + 1),
                        'title': title,
                        'score': rating,
                        'url': anime_url,
                        'additional_info': additional_info,
                        'source': 'AniDB',
                        'category': category_name
                    }
                    
                    anime_list.append(anime_data)
                    
                except Exception as e:
                    print(f"Error parsing anime row {i}: {e}")
                    continue
            
            return anime_list
            
        except Exception as e:
            print(f"Error parsing anime list: {e}")
            return []
    
    def scrape_all_categories(self, limit: int = 20) -> Dict[str, List[Dict]]:
        """Scrape all available tag-based categories"""
        all_data = {}
        
        for category_key in self.categories.keys():
            print(f"\nScraping category: {category_key}")
            category_data = self.scrape_category(category_key, limit)
            all_data[category_key] = category_data
            
            # Longer delay between categories
            time.sleep(3)
        
        return all_data
    



def main():
    scraper = AniDBScraper()
    
    try:
        # Option 1: Scrape specific category
        # category_data = scraper.scrape_category('action_adventure_shounen', 20)
        
        # Option 2: Scrape all categories
        all_data = scraper.scrape_all_categories(20)
        
        # Save data
        scraper.save_to_json(all_data, 'anidb_tag_anime.json')
        scraper.save_to_csv(all_data, 'anidb_tag_anime.csv')
        
    finally:
        scraper.close()


if __name__ == "__main__":
    main() 