#!/usr/bin/env python3
"""
Demo Usage Examples
Shows different ways to use the anime scrapers and analyzer
"""

from mal_scraper import MALScraper
from anidb_scraper import AniDBScraper
from animeplanet_scraper import AnimePlanetScraper
from data_analyzer import AnimeDataAnalyzer
import json


def demo_single_scraper():
    """Demo: Using a single scraper for specific data"""
    print("="*60)
    print("DEMO 1: Single Scraper - MyAnimeList Top Anime")
    print("="*60)
    
    scraper = MALScraper()
    
    # Get top 10 anime from the main ranking
    top_anime = scraper.scrape_category('top_anime', 10)
    
    print(f"Found {len(top_anime)} top anime from MyAnimeList:")
    for anime in top_anime[:5]:  # Show first 5
        print(f"  {anime['rank']}. {anime['title']} (Score: {anime['score']})")
    
    # Save to file
    scraper.save_to_json({'top_anime': top_anime}, 'demo_mal_top10.json')
    print("\nSaved to demo_mal_top10.json")


def demo_specific_categories():
    """Demo: Scraping specific categories from multiple sources"""
    print("\n" + "="*60)
    print("DEMO 2: Specific Categories from All Sources")
    print("="*60)
    
    results = {}
    
    # MyAnimeList - Top Movies
    mal_scraper = MALScraper()
    mal_movies = mal_scraper.scrape_category('top_movie', 5)
    results['mal_movies'] = mal_movies
    print(f"MAL Top Movies: {len(mal_movies)} found")
    
    # AniDB - Highest Rated
    anidb_scraper = AniDBScraper()
    anidb_rated = anidb_scraper.scrape_category('highest_rated', 5)
    results['anidb_rated'] = anidb_rated
    print(f"AniDB Highest Rated: {len(anidb_rated)} found")
    
    # AnimePlanet - Most Watched
    ap_scraper = AnimePlanetScraper()
    ap_watched = ap_scraper.scrape_category('most_watched', 5)
    results['animeplanet_watched'] = ap_watched
    print(f"AnimePlanet Most Watched: {len(ap_watched)} found")
    
    # Save results
    with open('demo_specific_categories.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\nSaved to demo_specific_categories.json")


def demo_custom_analysis():
    """Demo: Custom data analysis"""
    print("\n" + "="*60)
    print("DEMO 3: Custom Data Analysis")
    print("="*60)
    
    # This assumes you have run the full scrapers first
    try:
        analyzer = AnimeDataAnalyzer()
        if analyzer.load_data():
            print("Running analysis on combined data...")
            
            # Just run basic statistics
            analyzer.basic_statistics()
            
            # Find common anime
            analyzer.find_common_anime()
            
            print("\nAnalysis completed!")
        else:
            print("No combined data found. Run 'python run_all_scrapers.py' first.")
    
    except Exception as e:
        print(f"Analysis failed: {e}")
        print("Make sure to run the scrapers first to generate data.")


def demo_comparison():
    """Demo: Compare anime rankings across sources"""
    print("\n" + "="*60)
    print("DEMO 4: Quick Ranking Comparison")
    print("="*60)
    
    # Get top 3 from each source for comparison
    sources = {
        'MyAnimeList': MALScraper(),
        'AniDB': AniDBScraper(),
        'AnimePlanet': AnimePlanetScraper()
    }
    
    print("Top 3 anime from each source:")
    
    for source_name, scraper in sources.items():
        try:
            if source_name == 'MyAnimeList':
                top_anime = scraper.scrape_category('top_anime', 3)
            elif source_name == 'AniDB':
                top_anime = scraper.scrape_category('highest_rated', 3)
            else:  # AnimePlanet
                top_anime = scraper.scrape_category('highest_rated', 3)
            
            print(f"\n{source_name}:")
            for anime in top_anime:
                title = anime.get('title', 'N/A')
                score = anime.get('score', 'N/A')
                print(f"  {anime.get('rank', '?')}. {title} (Score: {score})")
                
        except Exception as e:
            print(f"\n{source_name}: Failed to scrape ({e})")


def demo_find_specific_anime():
    """Demo: Search for a specific anime across sources"""
    print("\n" + "="*60)
    print("DEMO 5: Find Specific Anime Across Sources")
    print("="*60)
    
    # This is a simplified example - in reality you'd need to scrape first
    # then search through the results
    search_terms = ['demon slayer', 'attack on titan', 'your name']
    
    print("This demo would search for specific anime across all sources.")
    print("Search terms:", ', '.join(search_terms))
    print("\nTo implement this, you would:")
    print("1. Run full scraping with run_all_scrapers.py")
    print("2. Load the combined JSON data")
    print("3. Search through titles using fuzzy matching")
    print("4. Compare rankings and scores across sources")


if __name__ == "__main__":
    print("Anime Scraper Demo - Multiple Usage Examples")
    print("Note: These demos make actual web requests, so they may take time.")
    print("Some demos require running full scrapers first.\n")
    
    # Run demos
    demo_single_scraper()
    demo_specific_categories()
    demo_custom_analysis()
    demo_comparison()
    demo_find_specific_anime()
    
    print("\n" + "="*60)
    print("DEMO COMPLETED")
    print("="*60)
    print("Files created:")
    print("- demo_mal_top10.json")
    print("- demo_specific_categories.json")
    print("\nFor full functionality, run:")
    print("- python run_all_scrapers.py  (full scraping)")
    print("- python data_analyzer.py     (data analysis)") 