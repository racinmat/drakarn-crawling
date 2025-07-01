#!/usr/bin/env python3
"""
Final Demo - Complete Anime Scraping System
Shows all working components together
"""

import json
from mal_scraper import MALScraper
from anidb_scraper import AniDBScraper
from data_analyzer import AnimeDataAnalyzer

def demo_complete_system():
    print("🎌 ANIME SCRAPING SYSTEM - FINAL DEMONSTRATION")
    print("="*70)
    print("This demo shows the complete working system:")
    print("✅ MyAnimeList scraper (fully working)")
    print("✅ AniDB scraper (working with some limitations)")
    print("⚠️  AnimePlanet scraper (blocked by site - common issue)")
    print("✅ Data analyzer (full functionality)")
    print("✅ Multiple output formats (JSON, CSV)")
    print()
    
    # Demo 1: Quick scraping from working sources
    print("📊 DEMO 1: Quick Scraping Sample")
    print("-" * 40)
    
    # MyAnimeList sample
    print("🔴 MyAnimeList - Top 3 Anime:")
    mal_scraper = MALScraper()
    mal_sample = mal_scraper.scrape_category('top_anime', 3)
    for anime in mal_sample:
        print(f"  {anime['rank']}. {anime['title']} - Score: {anime['score']}")
    
    print()
    
    # AniDB sample
    print("🔵 AniDB - Top 3 Anime:")
    anidb_scraper = AniDBScraper()
    anidb_sample = anidb_scraper.scrape_category('top_anime', 3)
    for anime in anidb_sample:
        title = anime['title'] if anime['title'] not in ['N/A', '?'] else f"Anime #{anime['rank']}"
        print(f"  {anime['rank']}. {title} - Type: {anime.get('additional_info', 'N/A')}")
    
    print()
    
    # Demo 2: Show existing analysis
    print("📈 DEMO 2: Data Analysis Results")
    print("-" * 40)
    
    try:
        with open('anime_analysis_report.json', 'r', encoding='utf-8') as f:
            analysis = json.load(f)
        
        stats = analysis.get('basic_statistics', {})
        print(f"📊 Basic Statistics:")
        print(f"  Total sources analyzed: {stats.get('total_sources', 0)}")
        print(f"  Total categories: {stats.get('total_categories', 0)}")
        print(f"  Total anime entries: {stats.get('total_anime_entries', 0)}")
        
        score_analysis = analysis.get('score_analysis', {})
        if score_analysis:
            print(f"\n⭐ Score Analysis:")
            print(f"  Average score: {score_analysis.get('average_score', 0):.2f}")
            print(f"  Score range: {score_analysis.get('min_score', 0)} - {score_analysis.get('max_score', 0)}")
        
        title_analysis = analysis.get('title_analysis', {})
        if title_analysis and 'common_words' in title_analysis:
            print(f"\n📝 Most common words in titles:")
            words = title_analysis['common_words']
            for word, count in list(words.items())[:5]:
                print(f"  {word}: {count} times")
    
    except FileNotFoundError:
        print("  ⚠️  No analysis data found. Run test_working_scrapers.py first.")
    
    print()
    
    # Demo 3: Available categories
    print("📁 DEMO 3: Available Categories")
    print("-" * 40)
    
    print("🔴 MyAnimeList categories:")
    for category in mal_scraper.categories.keys():
        print(f"  • {category}")
    
    print("\n🔵 AniDB categories:")
    for category in anidb_scraper.categories.keys():
        print(f"  • {category}")
    
    print()
    
    # Demo 4: Files generated
    print("📄 DEMO 4: Generated Files")
    print("-" * 40)
    
    files_info = [
        ("test_mal_results.json/csv", "MyAnimeList data in JSON and CSV"),
        ("test_anidb_results.json/csv", "AniDB data in JSON and CSV"),
        ("test_combined_results.json", "Combined data from all sources"),
        ("anime_analysis_report.json", "Comprehensive analysis report")
    ]
    
    for filename, description in files_info:
        print(f"  📄 {filename}")
        print(f"     └─ {description}")
    
    print()
    
    # Summary
    print("🎯 SYSTEM CAPABILITIES SUMMARY")
    print("="*70)
    print("✅ Web scraping from multiple anime databases")
    print("✅ Rate limiting and respectful scraping practices")
    print("✅ Robust error handling and retry logic")
    print("✅ Multiple output formats (JSON, CSV)")
    print("✅ Data analysis and cross-source comparison") 
    print("✅ Configurable limits and categories")
    print("✅ Comprehensive documentation and examples")
    print()
    print("⚠️  NOTE: Some sites (like AnimePlanet) actively block scrapers.")
    print("   This is common and expected with anime databases.")
    print()
    print("🚀 NEXT STEPS:")
    print("   • Run 'python test_working_scrapers.py' for full collection")
    print("   • Modify config.py for custom settings")
    print("   • Check README.md for detailed usage instructions")
    print()
    print("🎌 Anime scraping system demonstration complete!")

if __name__ == "__main__":
    demo_complete_system() 