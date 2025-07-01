#!/usr/bin/env python3
"""
MyAnimeList Top Anime Scraper
Scrapes top 20 anime from various categories on MyAnimeList
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import os
from typing import List, Dict, Optional


class MALScraper:
    def __init__(self):
        self.base_url = "https://myanimelist.net"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Available categories on MAL
        self.categories = {
            'top_anime': '/topanime.php',
            'most_popular': '/topanime.php?type=bypopularity',
            'top_airing': '/topanime.php?type=airing',
            'top_upcoming': '/topanime.php?type=upcoming',
            'top_tv': '/topanime.php?type=tv',
            'top_movie': '/topanime.php?type=movie',
            'top_ova': '/topanime.php?type=ova',
            'top_special': '/topanime.php?type=special',
            'most_favorited': '/topanime.php?type=favorite'
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
            ranking_items = soup.find_all('tr', class_='ranking-list')
            
            for i, item in enumerate(ranking_items[:limit]):
                if i >= limit:
                    break
                    
                anime_data = self._extract_anime_data(item)
                if anime_data:
                    anime_list.append(anime_data)
                
                # Rate limiting
                time.sleep(0.5)
            
            return anime_list
            
        except requests.RequestException as e:
            print(f"Error scraping {category}: {e}")
            return []
    
    def _extract_anime_data(self, item) -> Optional[Dict]:
        """Extract anime data from a ranking item"""
        try:
            # Rank
            rank_elem = item.find('td', class_='rank ac')
            rank = rank_elem.find('span').text.strip() if rank_elem else "N/A"
            
            # Title and URL
            title_elem = item.find('div', class_='detail')
            if not title_elem:
                return None
                
            title_link = title_elem.find('a', class_='hoverinfo_trigger')
            title = title_link.text.strip() if title_link else "N/A"
            anime_url = title_link.get('href') if title_link else "N/A"
            
            # Score
            score_elem = item.find('td', class_='score ac fs14')
            score_span = score_elem.find('span') if score_elem else None
            score = score_span.text.strip() if score_span else "N/A"
            
            # Additional info (type, episodes, dates)
            info_elem = title_elem.find('div', class_='information di-ib mt4')
            info_text = info_elem.text.strip() if info_elem else "N/A"
            
            return {
                'rank': rank,
                'title': title,
                'score': score,
                'url': anime_url,
                'additional_info': info_text,
                'source': 'MyAnimeList'
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
    
    def save_to_json(self, data: Dict, filename: str = 'mal_anime_data.json'):
        """Save data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Data saved to {filename}")
    
    def save_to_csv(self, data: Dict, filename: str = 'mal_anime_data.csv'):
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
    scraper = MALScraper()
    
    # Option 1: Scrape specific category
    # category_data = scraper.scrape_category('top_anime', 20)
    
    # Option 2: Scrape all categories
    all_data = scraper.scrape_all_categories(20)
    
    # Save data
    scraper.save_to_json(all_data, 'mal_top_anime.json')
    scraper.save_to_csv(all_data, 'mal_top_anime.csv')


if __name__ == "__main__":
    main() 