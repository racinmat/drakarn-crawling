#!/usr/bin/env python3
"""
Debug script to examine AniDB HTML structure
"""

import requests
from bs4 import BeautifulSoup

def debug_anidb():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    url = "https://anidb.net/anime/"
    print(f"Fetching: {url}")
    
    try:
        response = session.get(url)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for tables
            tables = soup.find_all('table')
            print(f"Found {len(tables)} tables")
            
            for i, table in enumerate(tables):
                rows = table.find_all('tr')
                print(f"Table {i}: {len(rows)} rows")
                
                if len(rows) > 5:  # Promising table
                    print(f"Examining table {i} (first few rows):")
                    for j, row in enumerate(rows[:3]):
                        cells = row.find_all(['td', 'th'])
                        print(f"  Row {j}: {len(cells)} cells")
                        for k, cell in enumerate(cells[:5]):  # First 5 cells
                            text = cell.get_text(strip=True)[:50]  # First 50 chars
                            links = cell.find_all('a')
                            print(f"    Cell {k}: '{text}' (links: {len(links)})")
                            for link in links[:2]:  # First 2 links
                                href = link.get('href', '')
                                link_text = link.get_text(strip=True)[:30]
                                print(f"      Link: '{link_text}' -> {href}")
                    print()
            
            # Look for specific anime-related elements
            anime_links = soup.find_all('a', href=lambda x: x and '/anime/' in x)
            print(f"Found {len(anime_links)} anime links")
            
            if anime_links:
                print("Sample anime links:")
                for i, link in enumerate(anime_links[:5]):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    print(f"  {i+1}. '{text}' -> {href}")
        
        else:
            print(f"Failed to fetch page: {response.status_code}")
            print(response.text[:500])
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_anidb() 