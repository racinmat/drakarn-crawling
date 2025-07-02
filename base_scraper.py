#!/usr/bin/env python3
"""
Base Scraper Class
Contains shared HTTP request and caching logic for all anime scrapers
"""

import csv
import json
import os
import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseScraper(ABC):
    """Base class for all anime scrapers with shared functionality"""
    
    def __init__(self, site_name: str):
        self.site_name = site_name
        self.session = None  # To be set by child classes
        
        # Create directories if they don't exist
        os.makedirs('html_cache', exist_ok=True)
        os.makedirs('results', exist_ok=True)

    @property
    @abstractmethod
    def base_url(self):
        pass

    def _get_cache_filename(self, url: str) -> str:
        """Generate a cache filename based on URL"""
        # Extract the path and query from URL
        url_part = url.replace(self.base_url, '').lstrip('/')
        # Replace all non-alphanumeric characters with underscores
        clean_name = re.sub(r'[^a-zA-Z0-9]', '_', url_part)
        # Remove multiple consecutive underscores and trailing underscores
        clean_name = re.sub(r'_+', '_', clean_name).strip('_')
        # If empty, use 'main'
        clean_name = clean_name or 'main'
        
        filename = f"{self.site_name.lower()}_{clean_name}.html"
        return os.path.join('html_cache', filename)
    
    def _get_page_content(self, url: str, timeout: int = 10) -> Optional[str]:
        """Get HTML content from URL with caching"""
        cache_file = self._get_cache_filename(url)
        
        # Try to load from cache first
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    print(f"Loading from cache: {cache_file}")
                    return f.read()
            except Exception as e:
                print(f"Error reading cache file {cache_file}: {e}")
        
        # Download if not in cache
        try:
            print(f"Downloading: {url}")
            response = self._make_request(url, timeout)
            
            if response is None:
                return None
            
            # Save to cache
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(response)
                print(f"HTML cached to {cache_file}")
            except Exception as e:
                print(f"Error saving to cache: {e}")
            
            return response
            
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return None
    
    @abstractmethod
    def _make_request(self, url: str, timeout: int) -> Optional[str]:
        """Make HTTP request - to be implemented by child classes"""
        pass
    
    def save_to_json(self, data: Dict, filename: str):
        """Save data to JSON file in results directory"""
        filepath = os.path.join('results', filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Data saved to {filepath}")
    
    def save_to_csv(self, data: Dict, filename: str, fieldnames: List[str] = None):
        """Save data to CSV file in results directory"""
        # Flatten all anime data from all categories
        all_anime = []
        for category, anime_list in data.items():
            for anime in anime_list:
                all_anime.append(anime)
        
        if not all_anime:
            print("No data to save")
            return
        
        # Use provided fieldnames or auto-detect
        if fieldnames is None:
            fieldnames_set = set()
            for anime in all_anime:
                fieldnames_set.update(anime.keys())
            fieldnames = sorted(list(fieldnames_set))
        
        filepath = os.path.join('results', filename)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_anime)
        print(f"Data saved to {filepath}")
    
    @abstractmethod
    def scrape_category(self, category_key: str, limit: int = 20) -> List[Dict]:
        """Scrape anime from a specific category - to be implemented by child classes"""
        pass
    
    @abstractmethod
    def scrape_all_categories(self, limit: int = 20) -> Dict[str, List[Dict]]:
        """Scrape all categories - to be implemented by child classes"""
        pass
    
    def close(self):
        """Close the session if needed - can be overridden by child classes"""
        if hasattr(self.session, 'close'):
            self.session.close() 