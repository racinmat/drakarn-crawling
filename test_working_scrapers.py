#!/usr/bin/env python3
"""
Test script for working scrapers (MAL and AniDB)
"""

from mal_scraper import MALScraper
from anidb_scraper import AniDBScraper
import json
import time

def test_mal_multiple_categories():
    print("="*60)
    print("Testing MyAnimeList - Multiple Categories")
    print("="*60)
    
    scraper = MALScraper()
    categories_to_test = ['top_anime', 'most_popular', 'top_movie']
    all_data = {}
    
    for category in categories_to_test:
        print(f"\nTesting {category}...")
        try:
            data = scraper.scrape_category(category, 5)  # Get 5 from each
            all_data[category] = data
            print(f"  ✅ Success: {len(data)} anime")
            
            for anime in data[:2]:  # Show first 2
                print(f"    {anime.get('rank', '?')}. {anime.get('title', 'N/A')} - Score: {anime.get('score', 'N/A')}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            all_data[category] = []
        
        time.sleep(2)  # Be respectful
    
    return all_data

def test_anidb_multiple_categories():
    print("\n" + "="*60)
    print("Testing AniDB - Multiple Categories") 
    print("="*60)
    
    scraper = AniDBScraper()
    categories_to_test = ['highest_rated', 'top_anime']
    all_data = {}
    
    for category in categories_to_test:
        print(f"\nTesting {category}...")
        try:
            data = scraper.scrape_category(category, 5)  # Get 5 from each
            all_data[category] = data
            print(f"  ✅ Success: {len(data)} anime")
            
            for anime in data[:2]:  # Show first 2
                print(f"    {anime.get('rank', '?')}. {anime.get('title', 'N/A')} - Score: {anime.get('score', 'N/A')}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            all_data[category] = []
        
        time.sleep(3)  # Be extra respectful with AniDB
    
    return all_data

def save_results(mal_data, anidb_data):
    print("\n" + "="*60)
    print("Saving Results")
    print("="*60)
    
    # Save individual results
    mal_scraper = MALScraper()
    mal_scraper.save_to_json(mal_data, 'test_mal_results.json')
    mal_scraper.save_to_csv(mal_data, 'test_mal_results.csv')
    
    anidb_scraper = AniDBScraper()
    anidb_scraper.save_to_json(anidb_data, 'test_anidb_results.json')
    anidb_scraper.save_to_csv(anidb_data, 'test_anidb_results.csv')
    
    # Save combined results
    combined_data = {
        'myanimelist': mal_data,
        'anidb': anidb_data
    }
    
    with open('test_combined_results.json', 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)
    
    print("✅ Results saved to:")
    print("  - test_mal_results.json/csv")
    print("  - test_anidb_results.json/csv") 
    print("  - test_combined_results.json")

def print_summary(mal_data, anidb_data):
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    mal_total = sum(len(anime_list) for anime_list in mal_data.values())
    anidb_total = sum(len(anime_list) for anime_list in anidb_data.values())
    
    print(f"MyAnimeList:")
    print(f"  Categories tested: {len(mal_data)}")
    print(f"  Total anime collected: {mal_total}")
    
    print(f"\nAniDB:")
    print(f"  Categories tested: {len(anidb_data)}")
    print(f"  Total anime collected: {anidb_total}")
    
    print(f"\nOverall:")
    print(f"  Total sources: 2")
    print(f"  Total categories: {len(mal_data) + len(anidb_data)}")
    print(f"  Total anime: {mal_total + anidb_total}")

if __name__ == "__main__":
    print("Testing Working Anime Scrapers")
    print("This will test MyAnimeList and AniDB with multiple categories")
    print("Note: AnimePlanet is currently blocked and excluded from this test\n")
    
    # Test both scrapers
    mal_data = test_mal_multiple_categories()
    anidb_data = test_anidb_multiple_categories()
    
    # Save and summarize
    save_results(mal_data, anidb_data)
    print_summary(mal_data, anidb_data)
    
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60) 