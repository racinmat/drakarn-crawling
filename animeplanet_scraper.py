#!/usr/bin/env python3
"""
AnimePlanet Tag-Based Anime Scraper
Scrapes top 20 anime from tag-based categories on AnimePlanet using individual tag searches
"""

import time
import urllib.parse
from typing import List, Dict, Optional
import re

import tls_client
from bs4 import BeautifulSoup

from base_scraper import BaseScraper


class AnimePlanetScraper(BaseScraper):
    def __init__(self):
        super().__init__("animeplanet")
        # the very same headers did not work with httpx with http2 nor with requests, interesting.
        self.base_tag_url = "https://www.anime-planet.com/anime/tags"
        self.session = tls_client.Session(
            client_identifier="chrome_120",
            random_tls_extension_order=True
        )
        
        # Set headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }
        
        # Tag-based categories as requested (5 categories)
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
            'slice_of_life': {
                'name': 'Slice of Life',
                'tags': ['slice-of-life'],  # Note: AnimePlanet uses hyphens for multi-word tags
                'description': 'Slice of life anime'
            },
            'comedy': {
                'name': 'Comedy',
                'tags': ['comedy'],
                'description': 'Comedy anime'
            }
        }

    @property
    def base_url(self):
        return "https://www.anime-planet.com"

    def _make_request(self, url: str, timeout: int) -> Optional[str]:
        """Make HTTP request using tls_client with retry logic"""
        # Add initial delay to avoid immediate blocking
        time.sleep(2)
        
        try:
            # Try multiple times with increasing delays
            for attempt in range(3):
                try:
                    response = self.session.get(url, headers=self.headers, timeout_seconds=timeout)
                    
                    if response.status_code == 200:
                        return response.text
                    elif response.status_code == 403:
                        print(f"Attempt {attempt + 1}: Got 403 Forbidden, waiting {5 * (attempt + 1)} seconds...")
                        time.sleep(5 * (attempt + 1))
                        if attempt == 2:  # Last attempt
                            print("All attempts failed. AnimePlanet may be blocking requests.")
                            return None
                    else:
                        print(f"Unexpected status code: {response.status_code}")
                        if attempt == 2:
                            return None
                        time.sleep(5)
                        
                except Exception as e:
                    print(f"Request error on attempt {attempt + 1}: {e}")
                    if attempt == 2:
                        return None
                    time.sleep(5)
            
        except Exception as e:
            print(f"Error downloading HTML: {e}")
            return None
        
        return None

    def _build_tag_url(self, tag: str) -> str:
        """Build AnimePlanet tag URL sorted by average rating"""
        # Format: https://www.anime-planet.com/anime/tags/{tag}?sort=average&order=desc
        tag_encoded = urllib.parse.quote(tag.replace(' ', '-'))
        return f"{self.base_tag_url}/{tag_encoded}?sort=average&order=desc"

    def _scrape_single_tag(self, tag: str, limit: int = 20) -> List[Dict]:
        """Scrape anime from a single tag"""
        tag_url = self._build_tag_url(tag)
        print(f"  Scraping tag '{tag}': {tag_url}")
        
        # Get HTML content (either from cache or download)
        html_content = self._get_page_content(tag_url)
        if not html_content:
            print(f"  Failed to get content for tag '{tag}'")
            return []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            anime_list = []
            
            # AnimePlanet typically uses card-based layouts
            anime_cards = self._find_anime_cards(soup)
            
            for i, card in enumerate(anime_cards[:limit]):
                if i >= limit:
                    break
                    
                anime_data = self._extract_anime_data(card, i + 1, tag)
                if anime_data:
                    anime_list.append(anime_data)
            
            print(f"  Found {len(anime_list)} anime for tag '{tag}'")
            return anime_list
            
        except Exception as e:
            print(f"  Error scraping tag '{tag}': {e}")
            return []

    def scrape_category(self, category_key: str, limit: int = 20) -> List[Dict]:
        """Scrape anime from a specific tag-based category"""
        if category_key not in self.categories:
            print(f"Category '{category_key}' not found. Available categories: {list(self.categories.keys())}")
            return []
        
        category = self.categories[category_key]
        print(f"Scraping {category['name']} ({category['description']})...")
        
        # Collect anime from all tags in this category
        all_anime = []
        
        for tag in category['tags']:
            tag_anime = self._scrape_single_tag(tag, limit)
            all_anime.extend(tag_anime)

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
    
    def _find_anime_cards(self, soup):
        """Find anime cards using the correct AnimePlanet structure"""
        # AnimePlanet uses ul.cardDeck with li.card elements
        anime_cards = soup.select('ul.cardDeck li.card')
        
        if anime_cards:
            print(f"    Found {len(anime_cards)} anime cards")
            return anime_cards
        
        print("    No anime cards found")
        return []
    
    def _extract_anime_data(self, card, rank: int, tag: str) -> Optional[Dict]:
        """Extract anime data from a card element"""
        try:
            # Title and URL from the main link
            title = "N/A"
            anime_url = "N/A"
            
            # Find the main anime link
            main_link = card.select_one('a[href*="/anime/"]')
            if main_link:
                anime_url = self.base_url + main_link.get('href', '')
                
                # Get title from cardName h3
                title_elem = card.select_one('h3.cardName')
                if title_elem:
                    title = title_elem.get_text(strip=True)
            
            # Try to extract score/rating from various sources
            score = self._extract_score(card, main_link)
            
            # Additional info from entryBar
            additional_info = ""
            entry_bar = card.select('.entryBar li')
            if entry_bar:
                info_parts = [li.get_text(strip=True) for li in entry_bar[:3]]
                additional_info = " | ".join(info_parts)
            
            # If no entryBar, try to get info from tooltip
            if not additional_info:
                tooltip_content = main_link.get('title', '') if main_link else ''
                if tooltip_content:
                    # Extract type and year from tooltip
                    type_match = re.search(r'<li class=.*?type.*?>(.*?)</li>', tooltip_content)
                    year_match = re.search(r'<li class=.*?iconYear.*?>(.*?)</li>', tooltip_content)
                    
                    info_parts = []
                    if type_match:
                        info_parts.append(type_match.group(1))
                    if year_match:
                        info_parts.append(year_match.group(1))
                    
                    additional_info = " | ".join(info_parts)
            
            return {
                'rank': str(rank),
                'title': title,
                'score': score,
                'url': anime_url,
                'additional_info': additional_info,
                'source': 'AnimePlanet',
                'tag': tag  # Will be updated to category later
            }
            
        except Exception as e:
            print(f"    Error extracting anime data: {e}")
            return None
    
    def _extract_score(self, card, main_link) -> str:
        """Extract score/rating from card element"""
        # Try various methods to extract rating
        
        # Method 1: Look for rating in card
        rating_elem = card.select_one('.avgRating, .rating, .score')
        if rating_elem:
            return rating_elem.get_text(strip=True)
        
        # Method 2: Check tooltip content for rating (PRIMARY METHOD)
        if main_link:
            tooltip_content = main_link.get('title', '')
            if tooltip_content:
                # Look for ttRating in tooltip content - this is where AnimePlanet stores ratings
                rating_match = re.search(r'<div class=.?ttRating.?>([^<]+)</div>', tooltip_content)
                if rating_match:
                    return rating_match.group(1).strip()
                
                # Fallback: Look for other rating patterns in tooltip
                rating_match = re.search(r'Rating:\s*(\d+\.?\d*)', tooltip_content)
                if rating_match:
                    return rating_match.group(1)
                
                # Look for numeric patterns that might be ratings
                rating_match = re.search(r'(\d+\.?\d*)\s*(?:/|out of|★)', tooltip_content)
                if rating_match:
                    return rating_match.group(1)
        
        # Method 3: Look for data attributes
        rating_data = card.get('data-rating') or card.get('data-score')
        if rating_data:
            return str(rating_data)
        
        # If no rating found, return N/A (will be sorted last)
        return "N/A"
    
    def scrape_all_categories(self, limit: int = 20) -> Dict[str, List[Dict]]:
        """Scrape all available tag-based categories"""
        all_data = {}
        
        for category_key in self.categories.keys():
            print(f"\nScraping category: {category_key}")
            category_data = self.scrape_category(category_key, limit)
            all_data[category_key] = category_data
        
        return all_data
    
    def close(self):
        """Close the TLS session"""
        if hasattr(self.session, 'close'):
            self.session.close()


def main():
    scraper = AnimePlanetScraper()
    
    try:
        # Option 1: Scrape specific category
        # category_data = scraper.scrape_category('action_adventure_shounen', 20)
        
        # Option 2: Scrape all categories
        all_data = scraper.scrape_all_categories(20)
        
        # Save data
        scraper.save_to_json(all_data, 'animeplanet_tag_anime.json')
        scraper.save_to_csv(all_data, 'animeplanet_tag_anime.csv')
        
    finally:
        # Clean up
        scraper.close()


if __name__ == "__main__":
    main() 