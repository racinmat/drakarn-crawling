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

    @property
    def base_url(self):
        return "https://myanimelist.net"

    @property
    def output_file(self):
        return "mal_genre_anime"

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
    
    def _parse_anime_search_list(self, html_content: str, category_name: str, limit: int) -> List[Dict]:
        """Parse anime list from MAL's anime.php search pages"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            anime_list = []
            
            # Find all table rows containing anime data
            # Each anime is in a <tr> with multiple <td> cells
            anime_rows = soup.find_all('tr')
            
            count = 0
            for row in anime_rows:
                if count >= limit:
                    break
                
                try:
                    # Look for the title link in the row
                    title_link = row.find('a', class_='hoverinfo_trigger fw-b fl-l')
                    if not title_link:
                        continue
                    
                    # Extract title and URL
                    title = title_link.text.strip()
                    url = title_link.get('href', '')
                    if url and not url.startswith('http'):
                        url = self.base_url + url
                    
                    # Extract all table cells for this row
                    cells = row.find_all('td')
                    
                    # Initialize data
                    score = "N/A"
                    additional_info = "N/A"
                    rank = str(count + 1)  # Use sequential numbering
                    
                    # The cells typically contain: [image, title+description, type, episodes, score]
                    if len(cells) >= 5:
                        # Type is usually in the 3rd cell (index 2)
                        type_cell = cells[2] if len(cells) > 2 else None
                        episodes_cell = cells[3] if len(cells) > 3 else None
                        score_cell = cells[4] if len(cells) > 4 else None
                        
                        # Extract type and episodes for additional info
                        type_text = type_cell.text.strip() if type_cell else ""
                        episodes_text = episodes_cell.text.strip() if episodes_cell else ""
                        
                        if type_text and episodes_text:
                            additional_info = f"{type_text}, {episodes_text} episodes"
                        elif type_text:
                            additional_info = type_text
                        
                        # Extract score from the last cell
                        if score_cell:
                            score_text = score_cell.text.strip()
                            # Check if it's a valid score (decimal number)
                            if re.match(r'^\d+\.\d+$', score_text):
                                score = score_text
                    
                    # Skip entries with empty titles
                    if not title or title == "N/A":
                        continue
                    
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
                    count += 1
                    
                except Exception as e:
                    print(f"Error parsing anime row: {e}")
                    continue
            
            return anime_list
            
        except Exception as e:
            print(f"Error parsing anime search list for {category_name}: {e}")
            return []

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
        
        # Collect anime from all genres in this category
        all_anime = []
        
        for genre_id in category['genres']:
            genre_anime = self._scrape_single_genre(genre_id, category['name'], limit)
            all_anime.extend(genre_anime)

        # Remove duplicates based on title (keep the one with better score)
        unique_anime = {}
        for anime in all_anime:
            title = anime['title']
            if title not in unique_anime:
                unique_anime[title] = anime
            else:
                # Keep the one with better score
                current_score = self._parse_score(anime['score'])
                existing_score = self._parse_score(unique_anime[title]['score'])
                if current_score > existing_score:
                    unique_anime[title] = anime
        
        # Convert back to list and sort by score (highest first)
        final_anime = list(unique_anime.values())
        final_anime.sort(key=lambda x: self._parse_score(x['score']), reverse=True)
        
        # Update category and re-rank based on combined results
        for i, anime in enumerate(final_anime[:limit]):
            anime['category'] = category['name']
            anime['rank'] = str(i + 1)
        
        print(f"Final results for {category['name']}: {len(final_anime[:limit])} unique anime")
        return final_anime[:limit]
    
    def _scrape_single_genre(self, genre_id: int, category_name: str, limit: int = 20) -> List[Dict]:
        """Scrape anime from a single genre"""
        url = f"{self.base_url}/anime.php?genre[]={genre_id}&o=3"
        print(f"  Scraping genre {genre_id}: {url}")
        
        try:
            html_content = self._get_page_content(url)
            if not html_content:
                print(f"  Failed to get content for genre {genre_id}")
                return []
            
            results = self._parse_anime_search_list(html_content, category_name, limit)
            print(f"  Found {len(results)} anime for genre {genre_id}")
            return results
            
        except Exception as e:
            print(f"  Error scraping genre {genre_id}: {e}")
            return []
    
    def _parse_score(self, score_str: str) -> float:
        """Parse score string to float for sorting"""
        if score_str == "N/A" or not score_str:
            return 0.0
        
        try:
            # Extract numeric value from score string
            match = re.search(r'(\d+\.?\d*)', str(score_str))
            if match:
                return float(match.group(1))
        except:
            pass
        
        return 0.0
    
    def scrape_all_categories(self, limit: int = 20) -> Dict[str, List[Dict]]:
        """Scrape all genre-based categories"""
        results = {}
        for category_key in self.categories.keys():
            results[category_key] = self.scrape_category(category_key, limit)
        return results
    



def main():
    scraper = MALScraper()
    
    try:
        # Option 1: Scrape specific category
        # category_data = scraper.scrape_category('action_adventure_shounen', 20)
        
        # Option 2: Scrape all genre-based categories
        all_data = scraper.scrape_all_categories(20)
        
        # Save data
        scraper.save_to_json(all_data)
        scraper.save_to_csv(all_data)
        
    finally:
        scraper.close()


if __name__ == "__main__":
    main() 