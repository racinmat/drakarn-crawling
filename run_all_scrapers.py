#!/usr/bin/env python3
"""
Master script to run all anime scrapers
Scrapes top 20 anime from MyAnimeList, AniDB, and AnimePlanet
"""

import json
import time
import os
from mal_scraper import MALScraper
from anidb_scraper import AniDBScraper
from animeplanet_scraper import AnimePlanetScraper


def run_all_scrapers(limit: int = 20):
    """Run all three scrapers and combine results"""
    print("Starting anime scraping from all sources...")
    
    # Ensure results directory exists
    os.makedirs('results', exist_ok=True)
    
    all_results = {}
    
    # MyAnimeList
    print("\n" + "="*50)
    print("SCRAPING MYANIMELIST")
    print("="*50)
    try:
        mal_scraper = MALScraper()
        mal_data = mal_scraper.scrape_all_categories(limit)
        all_results['myanimelist'] = mal_data
        mal_scraper.save_to_json(mal_data, 'mal_top_anime.json')
        mal_scraper.save_to_csv(mal_data, 'mal_top_anime.csv')
        print("MyAnimeList scraping completed successfully!")
    except Exception as e:
        print(f"Error scraping MyAnimeList: {e}")
        all_results['myanimelist'] = {}
    
    # Wait between different sites
    time.sleep(5)
    
    # AniDB
    print("\n" + "="*50)
    print("SCRAPING ANIDB")
    print("="*50)
    try:
        anidb_scraper = AniDBScraper()
        anidb_data = anidb_scraper.scrape_all_categories(limit)
        all_results['anidb'] = anidb_data
        anidb_scraper.save_to_json(anidb_data, 'anidb_top_anime.json')
        anidb_scraper.save_to_csv(anidb_data, 'anidb_top_anime.csv')
        print("AniDB scraping completed successfully!")
    except Exception as e:
        print(f"Error scraping AniDB: {e}")
        all_results['anidb'] = {}
    
    # Wait between different sites
    time.sleep(5)
    
    # AnimePlanet
    print("\n" + "="*50)
    print("SCRAPING ANIMEPLANET")
    print("="*50)
    try:
        animeplanet_scraper = AnimePlanetScraper()
        animeplanet_data = animeplanet_scraper.scrape_all_categories(limit)
        all_results['animeplanet'] = animeplanet_data
        animeplanet_scraper.save_to_json(animeplanet_data, 'animeplanet_top_anime.json')
        animeplanet_scraper.save_to_csv(animeplanet_data, 'animeplanet_top_anime.csv')
        animeplanet_scraper.close()
        print("AnimePlanet scraping completed successfully!")
    except Exception as e:
        print(f"Error scraping AnimePlanet: {e}")
        all_results['animeplanet'] = {}
    
    # Save combined results
    print("\n" + "="*50)
    print("SAVING COMBINED RESULTS")
    print("="*50)
    
    combined_results_path = os.path.join('results', 'all_anime_data_combined.json')
    with open(combined_results_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"Combined results saved to {combined_results_path}")
    
    # Create summary report
    create_summary_report(all_results)
    
    print("All scraping completed! Check the 'results' directory for output files.")
    print("Check the 'html_cache' directory for cached HTML files.")


def create_summary_report(all_results):
    """Create a summary report of all scraped data"""
    summary = {
        'total_sources': len(all_results),
        'scraping_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'sources': {}
    }
    
    for source, data in all_results.items():
        source_summary = {
            'categories_scraped': len(data),
            'total_anime_entries': 0,
            'categories': {}
        }
        
        for category, anime_list in data.items():
            source_summary['categories'][category] = len(anime_list)
            source_summary['total_anime_entries'] += len(anime_list)
        
        summary['sources'][source] = source_summary
    
    summary_path = os.path.join('results', 'scraping_summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Summary report saved to {summary_path}")
    
    # Print summary to console
    print("\nSCRAPING SUMMARY:")
    print("-" * 30)
    for source, info in summary['sources'].items():
        print(f"{source.upper()}:")
        print(f"  Categories: {info['categories_scraped']}")
        print(f"  Total anime: {info['total_anime_entries']}")
        print()


if __name__ == "__main__":
    run_all_scrapers(20) 