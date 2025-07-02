#!/usr/bin/env python3
"""
AniDB Tag-Based Anime Scraper
Scrapes top 20 anime from tag-based categories on AniDB using numeric tag IDs
"""

import re
import time
import urllib.parse
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup

from base_scraper import BaseScraper


class AniDBScraper(BaseScraper):
    def __init__(self):
        super().__init__("anidb")
        self.base_anime_url = "https://anidb.net/anime/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Tag-based categories with numeric AniDB tag IDs
        # Based on AniDB tag list: https://anidb.net/tag
        # Using confirmed IDs from search results
        self.categories = {
            'action_adventure_shounen': {
                'name': 'Action, Adventure, Shounen',
                'tags': {
                    2841: 100,  # Action
                    2850: 100,  # Adventure
                    922: 0   # Shounen
                },
                'description': 'Action, adventure, shounen anime'
            },
            'romance': {
                'name': 'Romance',
                'tags': {
                    2858: 100   # Romance
                },
                'description': 'Romance anime'
            },
            'ecchi': {
                'name': 'Ecchi',
                'tags': {
                    2856: 100   # Ecchi
                },
                'description': 'Ecchi anime'
            },
            'comedy': {
                'name': 'Comedy',
                'tags': {
                    2853: 100   # Comedy
                },
                'description': 'Comedy anime'
            }
        }

    @property
    def base_url(self):
        return "https://anidb.net"

    def _make_request(self, url: str, timeout: int) -> Optional[str]:
        """Make HTTP request using requests session"""
        # Add initial delay to avoid immediate blocking
        time.sleep(2)
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Request failed: {e}")
            return None

    def _build_tag_search_url(self, tags: Dict[int, int]) -> str:
        """Build AniDB search URL with proper tag IDs and ordering"""
        # Base URL with proper ordering: rating descending, then name ascending
        url = f"{self.base_anime_url}?h=1&noalias=1&orderby.name=1.1&orderby.rating=0.2"
        
        # Add tag filters using numeric IDs
        for tag_id, value in tags.items():
            url += f"&tag.{tag_id}={value}"
        
        return url

    def scrape_category(self, category_key: str, limit: int = 20) -> List[Dict]:
        """Scrape anime from a specific tag-based category"""
        if category_key not in self.categories:
            print(f"Warning: Category '{category_key}' not found")
            return []
        
        category = self.categories[category_key]
        print(f"Scraping {category['name']} ({category['description']})...")
        
        # Build search URL with tag filters
        search_url = self._build_tag_search_url(category['tags'])
        print(f"Search URL: {search_url}")
        
        try:
            html_content = self._get_page_content(search_url)
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
            
            # AniDB anime list uses table structure with id 'animelist'
            anime_table = soup.find('table', id='animelist')
            if not anime_table:
                # Try alternative selectors
                anime_table = soup.find('table', class_='animelist')
                if not anime_table:
                    print("No anime table found on page")
                    return []
            
            # Find anime rows in the table body (skip header)
            tbody = anime_table.find('tbody')
            if not tbody:
                print("No table body found")
                return []
            
            anime_rows = tbody.find_all('tr')
            
            for i, row in enumerate(anime_rows[:limit]):
                if i >= limit:
                    break
                
                try:
                    # Extract title and URL from the title cell
                    title_cell = row.find('td', class_='name')
                    if not title_cell:
                        continue
                    
                    title_link = title_cell.find('a')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    anime_url = title_link.get('href', '')
                    if anime_url and not anime_url.startswith('http'):
                        anime_url = self.base_url + anime_url
                    
                    # Extract rating from the rating cell
                    rating_cell = row.find('td', class_='rating')
                    rating = "N/A"
                    if rating_cell:
                        rating_text = rating_cell.get_text(strip=True)
                        # Rating format: "9.73 (3700)" - extract the first number
                        rating_match = re.search(r'(\d+\.\d+)', rating_text)
                        if rating_match:
                            rating = rating_match.group(1)
                    
                    # Extract additional info (type, episodes, etc.)
                    type_cell = row.find('td', class_='type')
                    eps_cell = row.find('td', class_='eps')
                    
                    info_parts = []
                    if type_cell:
                        info_parts.append(f"Type: {type_cell.get_text(strip=True)}")
                    if eps_cell:
                        info_parts.append(f"Episodes: {eps_cell.get_text(strip=True)}")
                    
                    additional_info = " | ".join(info_parts) if info_parts else "N/A"
                    
                    if not title:
                        continue  # Skip if we couldn't extract title
                    
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
            
            # Add delay between categories to be respectful
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