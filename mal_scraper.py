#!/usr/bin/env python3
"""
MyAnimeList Genre-Based Anime Scraper
Scrapes top 20 anime from genre-based categories on MyAnimeList
Categories: Action/Adventure/Shounen, Romance, Ecchi/Erotica, Slice of Life, Comedy
"""

import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Optional
import re
from base_scraper import BaseScraper


class MALScraper(BaseScraper):
    def __init__(self):
        super().__init__("mal")
        self.base_url = "https://myanimelist.net"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Genre-based categories as requested by user
        # Using actual MAL genre IDs and proper search URLs
        self.categories = {
            "action_adventure_shounen": {
                "name": "Action, Adventure, Shounen",
                "genres": [1, 2, 27],  # Action=1, Adventure=2, Shounen=27
                "description": "Action, adventure, shounen anime"
            },
            "romance": {
                "name": "Romance", 
                "genres": [22],  # Romance=22
                "description": "Romance anime"
            },
            "ecchi_erotica": {
                "name": "Ecchi, Erotica",
                "genres": [9],  # Ecchi=9 (skip erotica for now due to uncertain ID)
                "description": "Ecchi anime"
            },
            "slice_of_life": {
                "name": "Slice of Life",
                "genres": [36],  # Slice of Life=36
                "description": "Slice of life anime"
            },
            "comedy": {
                "name": "Comedy",
                "genres": [4],  # Comedy=4
                "description": "Comedy anime"
            }
        }
        
        # Exclude hentai (ID 12)
        self.excluded_genres = [12]  # Hentai
    
    def _make_request(self, url: str, timeout: int) -> Optional[str]:
        """Make HTTP request using requests session"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def _parse_topanime_list(self, html_content: str, category_name: str, limit: int) -> List[Dict]:
        """Parse anime list from MAL's top anime by genre pages"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            anime_list = []
            
            # Top anime pages use ranking-list class
            anime_rows = soup.find_all('tr', class_='ranking-list')
            
            for i, row in enumerate(anime_rows[:limit]):
                if i >= limit:
                    break
                
                try:
                    # Extract rank
                    rank_td = row.find('td', class_='rank ac')
                    rank = rank_td.find('span').text.strip() if rank_td else "N/A"
                    
                    # Extract title and URL
                    title_cell = row.find('td', class_='title al va-t word-break')
                    if not title_cell:
                        continue
                    
                    # Find the title in the h3 section
                    title_h3 = title_cell.find('h3', class_='fl-l fs14 fw-b anime_ranking_h3')
                    if not title_h3:
                        continue
                    
                    title_link = title_h3.find('a', class_='hoverinfo_trigger')
                    if not title_link:
                        title_link = title_h3.find('a')
                    
                    if not title_link:
                        continue
                    
                    title = title_link.text.strip()
                    url = title_link.get('href', '')
                    if url and not url.startswith('http'):
                        url = self.base_url + url
                    
                    # Extract score
                    score_td = row.find('td', class_='score ac fs14')
                    score = "N/A"
                    if score_td:
                        score_span = score_td.find('span', class_='score-label')
                        if score_span:
                            score = score_span.text.strip()
                    
                    # Extract additional info (type, episodes, etc.)
                    info_div = title_cell.find('div', class_='information di-ib mt4')
                    additional_info = info_div.text.strip() if info_div else "N/A"
                    
                    anime_data = {
                        'title': title,
                        'score': score,
                        'rank': rank,
                        'url': url,
                        'additional_info': additional_info,
                        'source': 'MyAnimeList',
                        'category': category_name
                    }
                    
                    anime_list.append(anime_data)
                    
                except Exception as e:
                    print(f"Error parsing anime row: {e}")
                    continue
            
            return anime_list
            
        except Exception as e:
            print(f"Error parsing top anime list for {category_name}: {e}")
            return []
    
    def _extract_anime_from_item(self, item) -> Optional[Dict]:
        """Extract anime data from various HTML item structures"""
        try:
            title = "N/A"
            url = "N/A"
            score = "N/A"
            rank = "N/A"
            additional_info = "N/A"
            
            # Try different extraction methods
            
            # Method 1: Seasonal anime structure
            title_link = item.find('a', class_='link-title')
            if not title_link:
                # Method 2: Ranking list structure
                title_link = item.find('a', class_='hoverinfo_trigger')
            if not title_link:
                # Method 3: Generic anime link
                title_link = item.find('a', href=lambda x: x and '/anime/' in x)
            
            if title_link:
                title = title_link.text.strip()
                url = title_link.get('href', '')
                if url and not url.startswith('http'):
                    url = self.base_url + url
            
            # Extract score
            score_elem = item.find('span', class_='score-label') or item.find('span', class_='score')
            if not score_elem:
                score_elem = item.find('td', class_='score ac fs14')
                if score_elem:
                    score_elem = score_elem.find('span')
            
            if score_elem:
                score = score_elem.text.strip()
            
            # Extract rank
            rank_elem = item.find('span', class_='rank') or item.find('td', class_='rank ac')
            if rank_elem:
                rank_span = rank_elem.find('span') if rank_elem.name == 'td' else rank_elem
                if rank_span:
                    rank = rank_span.text.strip()
            
            # Extract additional info
            info_elem = item.find('div', class_='information') or item.find('div', class_='prodsrc')
            if info_elem:
                additional_info = info_elem.text.strip()
            
            # Only return if we have at least a title
            if title != "N/A":
                return {
                    'title': title,
                    'score': score,
                    'rank': rank,
                    'url': url,
                    'additional_info': additional_info,
                    'source': 'MyAnimeList'
                }
            
            return None
            
        except Exception as e:
            print(f"Error extracting anime data: {e}")
            return None
    
    def scrape_category(self, category_key: str, limit: int = 20) -> List[Dict]:
        """Scrape anime from a specific genre-based category"""
        if category_key not in self.categories:
            print(f"Warning: Category '{category_key}' not found")
            return []
        
        category = self.categories[category_key]
        print(f"Scraping {category['name']} ({category['description']})...")
        
        # Use top anime by genre URL - this is more reliable than search
        # We'll scrape from each genre separately and combine results
        all_results = []
        
        for genre_id in category['genres']:
            # Use the genre-specific top anime URL
            url = f"{self.base_url}/topanime.php?genre%5B%5D={genre_id}"
            
            try:
                html_content = self._get_page_content(url)
                if not html_content:
                    print(f"Failed to get content for genre {genre_id}")
                    continue
                
                results = self._parse_topanime_list(html_content, category['name'], limit)
                all_results.extend(results)
                
                # Add delay between requests
                time.sleep(1)
                
            except Exception as e:
                print(f"Error scraping genre {genre_id}: {e}")
        
        # Remove duplicates based on title and limit results
        seen_titles = set()
        unique_results = []
        for anime in all_results:
            if anime['title'] not in seen_titles:
                seen_titles.add(anime['title'])
                unique_results.append(anime)
                if len(unique_results) >= limit:
                    break
        
        return unique_results[:limit]
    
    def scrape_all_categories(self, limit: int = 20) -> Dict[str, List[Dict]]:
        """Scrape all genre-based categories"""
        results = {}
        for category_key in self.categories.keys():
            results[category_key] = self.scrape_category(category_key, limit)
            time.sleep(1)  # Be respectful to the server
        return results
    



def main():
    scraper = MALScraper()
    
    try:
        # Option 1: Scrape specific category
        # category_data = scraper.scrape_category('action_adventure_shounen', 20)
        
        # Option 2: Scrape all genre-based categories
        all_data = scraper.scrape_all_categories(20)
        
        # Save data
        scraper.save_to_json(all_data, 'mal_genre_anime.json')
        scraper.save_to_csv(all_data, 'mal_genre_anime.csv')
        
    finally:
        scraper.close()


if __name__ == "__main__":
    main() 