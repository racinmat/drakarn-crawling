#!/usr/bin/env python3
"""
Configuration file for anime scrapers
Centralizes all settings and makes them easily customizable
"""

# Scraping Configuration
SCRAPING_CONFIG = {
    # Number of anime to scrape per category (can be overridden per scraper)
    'DEFAULT_LIMIT': 20,
    
    # Rate limiting settings (in seconds)
    'DELAY_BETWEEN_REQUESTS': 0.5,
    'DELAY_BETWEEN_CATEGORIES': 2,
    'DELAY_BETWEEN_SITES': 5,
    
    # Request settings
    'REQUEST_TIMEOUT': 30,
    'MAX_RETRIES': 3,
    
    # User agent for requests
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Output Configuration
OUTPUT_CONFIG = {
    'SAVE_JSON': True,
    'SAVE_CSV': True,
    'JSON_INDENT': 2,
    'CSV_ENCODING': 'utf-8',
    
    # Output filenames
    'MAL_JSON': 'mal_top_anime.json',
    'MAL_CSV': 'mal_top_anime.csv',
    'ANIDB_JSON': 'anidb_top_anime.json',
    'ANIDB_CSV': 'anidb_top_anime.csv',
    'ANIMEPLANET_JSON': 'animeplanet_top_anime.json',
    'ANIMEPLANET_CSV': 'animeplanet_top_anime.csv',
    'COMBINED_JSON': 'all_anime_data_combined.json',
    'SUMMARY_JSON': 'scraping_summary.json'
}

# Site-specific configurations
SITE_CONFIGS = {
    'myanimelist': {
        'base_url': 'https://myanimelist.net',
        'enabled': True,
        'categories': {
            'top_anime': '/topanime.php',
            'most_popular': '/topanime.php?type=bypopularity',
            'top_airing': '/topanime.php?type=airing',
            'top_upcoming': '/topanime.php?type=upcoming',
            'top_tv': '/topanime.php?type=tv',
            'top_movie': '/topanime.php?type=movie',
            'top_ova': '/topanime.php?type=ova',
            'top_special': '/topanime.php?type=special',
            'most_favorited': '/topanime.php?type=favorite'
        },
        # Override specific settings for this site
        'custom_delay': 1.0,  # Slower for MyAnimeList
    },
    
    'anidb': {
        'base_url': 'https://anidb.net',
        'enabled': True,
        'categories': {
            'top_anime': '/anime/top',
            'highest_rated': '/anime/top/rating',
            'most_popular': '/anime/top/popular',
            'most_watched': '/anime/top/watched',
            'most_votes': '/anime/top/votes',
            'newest': '/anime/top/newest',
            'random': '/anime/top/random'
        },
        'custom_delay': 2.0,  # AniDB can be strict with rate limiting
    },
    
    'animeplanet': {
        'base_url': 'https://www.anime-planet.com',
        'enabled': True,
        'categories': {
            'top_anime': '/anime/top-anime',
            'highest_rated': '/anime/top-anime?sort=rating&order=desc',
            'most_watched': '/anime/top-anime?sort=watching&order=desc',
            'most_completed': '/anime/top-anime?sort=completed&order=desc',
            'most_want_to_watch': '/anime/top-anime?sort=want_to_watch&order=desc',
            'newest': '/anime/top-anime?sort=newest&order=desc',
            'most_popular': '/anime/top-anime?sort=popularity&order=desc'
        },
        'custom_delay': 1.5,
    }
}

# Categories to skip (if you want to exclude certain categories)
SKIP_CATEGORIES = [
    # 'random',  # Uncomment to skip random categories
    # 'top_upcoming',  # Uncomment to skip upcoming anime
]

# Data validation settings
VALIDATION_CONFIG = {
    'MIN_TITLE_LENGTH': 1,
    'MAX_TITLE_LENGTH': 200,
    'VALID_SCORE_RANGE': (0.0, 10.0),
    'REQUIRED_FIELDS': ['rank', 'title', 'source'],
    'ALLOW_MISSING_SCORES': True,
    'ALLOW_MISSING_URLS': True
}

# Logging configuration
LOGGING_CONFIG = {
    'ENABLE_LOGGING': True,
    'LOG_LEVEL': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'LOG_TO_FILE': False,
    'LOG_FILENAME': 'scraping.log',
    'VERBOSE_OUTPUT': True
}

# Advanced features
ADVANCED_CONFIG = {
    'ENABLE_CACHING': False,  # Cache responses to avoid re-scraping
    'CACHE_DURATION_HOURS': 24,
    'ENABLE_PROXY': False,
    'PROXY_LIST': [],
    'ENABLE_SELENIUM': False,  # Use Selenium for JavaScript-heavy sites
    'HEADLESS_BROWSER': True,
    'BROWSER_TIMEOUT': 30
}

# Data analysis settings
ANALYSIS_CONFIG = {
    'GENERATE_STATISTICS': True,
    'FIND_COMMON_ANIME': True,
    'CALCULATE_SCORE_DIFFERENCES': True,
    'EXPORT_ANALYSIS': True,
    'ANALYSIS_OUTPUT': 'anime_analysis_report.json'
} 