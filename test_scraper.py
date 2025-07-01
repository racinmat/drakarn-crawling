#!/usr/bin/env python3
"""
Test script to debug the anime scrapers
"""

from mal_scraper import MALScraper
from anidb_scraper import AniDBScraper
from animeplanet_scraper import AnimePlanetScraper

def test_mal_scraper():
    print("Testing MyAnimeList scraper...")
    scraper = MALScraper()
    
    # Test with just 3 anime from top anime
    try:
        data = scraper.scrape_category('top_anime', 3)
        print(f"Successfully scraped {len(data)} anime:")
        
        for anime in data:
            rank = anime.get('rank', '?')
            title = anime.get('title', 'N/A')
            score = anime.get('score', 'N/A')
            print(f"  {rank}. {title} - Score: {score}")
            
        return len(data) > 0  # Only return True if we got data
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_anidb_scraper():
    print("\nTesting AniDB scraper...")
    scraper = AniDBScraper()
    
    try:
        data = scraper.scrape_category('highest_rated', 3)
        print(f"Successfully scraped {len(data)} anime:")
        
        for anime in data:
            rank = anime.get('rank', '?')
            title = anime.get('title', 'N/A')
            score = anime.get('score', 'N/A')
            print(f"  {rank}. {title} - Score: {score}")
            
        return len(data) > 0  # Only return True if we got data
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_animeplanet_scraper():
    print("\nTesting AnimePlanet scraper...")
    scraper = AnimePlanetScraper()
    
    try:
        data = scraper.scrape_category('highest_rated', 3)
        print(f"Successfully scraped {len(data)} anime:")
        
        for anime in data:
            rank = anime.get('rank', '?')
            title = anime.get('title', 'N/A')
            score = anime.get('score', 'N/A')
            print(f"  {rank}. {title} - Score: {score}")
            
        return len(data) > 0  # Only return True if we got data
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    results = []
    
    # Test all scrapers
    results.append(("MyAnimeList", test_mal_scraper()))
    results.append(("AniDB", test_anidb_scraper()))
    results.append(("AnimePlanet", test_animeplanet_scraper()))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{name}: {status}")
    
    total_passed = sum(1 for _, success in results if success)
    print(f"\nTotal: {total_passed}/{len(results)} scrapers working") 