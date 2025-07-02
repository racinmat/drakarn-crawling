#!/usr/bin/env python3
"""
Anime Data Analyzer
Analyzes scraped anime data to find patterns, common titles, and interesting insights
"""

import json
import csv
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
import re
from statistics import mean, median
from config import ANALYSIS_CONFIG


class AnimeDataAnalyzer:
    def __init__(self, combined_data_file: str = 'results/all_anime_data_combined.json'):
        self.combined_data_file = combined_data_file
        self.data = {}
        self.analysis_results = {}
        
    def load_data(self) -> bool:
        """Load combined anime data from JSON file"""
        try:
            with open(self.combined_data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"Loaded data from {self.combined_data_file}")
            return True
        except FileNotFoundError:
            print(f"File {self.combined_data_file} not found. Run scrapers first.")
            return False
        except json.JSONDecodeError:
            print(f"Invalid JSON in {self.combined_data_file}")
            return False
    
    def analyze_all(self):
        """Run all analysis functions"""
        if not self.load_data():
            return
        
        print("Starting comprehensive anime data analysis...")
        
        self.basic_statistics()
        self.find_common_anime()
        self.analyze_scores()
        self.category_analysis()
        self.source_comparison()
        self.title_analysis()

        self.export_analysis()
    
    def basic_statistics(self):
        """Generate basic statistics about the data"""
        print("\n" + "="*50)
        print("BASIC STATISTICS")
        print("="*50)
        
        stats = {
            'total_sources': len(self.data),
            'total_categories': 0,
            'total_anime_entries': 0,
            'sources': {}
        }
        
        for source, categories in self.data.items():
            source_stats = {
                'categories': len(categories),
                'total_entries': 0,
                'avg_entries_per_category': 0
            }
            
            for category, anime_list in categories.items():
                source_stats['total_entries'] += len(anime_list)
                stats['total_categories'] += 1
                stats['total_anime_entries'] += len(anime_list)
            
            source_stats['avg_entries_per_category'] = (
                source_stats['total_entries'] / source_stats['categories'] 
                if source_stats['categories'] > 0 else 0
            )
            
            stats['sources'][source] = source_stats
            
            print(f"\n{source.upper()}:")
            print(f"  Categories: {source_stats['categories']}")
            print(f"  Total entries: {source_stats['total_entries']}")
            print(f"  Avg per category: {source_stats['avg_entries_per_category']:.1f}")
        
        print(f"\nOVERALL:")
        print(f"  Sources: {stats['total_sources']}")
        print(f"  Categories: {stats['total_categories']}")
        print(f"  Total entries: {stats['total_anime_entries']}")
        
        self.analysis_results['basic_statistics'] = stats
    
    def find_common_anime(self):
        """Find anime that appear across multiple sources"""
        print("\n" + "="*50)
        print("COMMON ANIME ANALYSIS")
        print("="*50)
        
        # Collect all anime titles
        title_sources = defaultdict(set)
        title_data = defaultdict(list)
        
        for source, categories in self.data.items():
            for category, anime_list in categories.items():
                for anime in anime_list:
                    title = self.normalize_title(anime.get('title', ''))
                    if title:
                        title_sources[title].add(source)
                        title_data[title].append({
                            'source': source,
                            'category': category,
                            'rank': anime.get('rank', 'N/A'),
                            'score': anime.get('score', 'N/A'),
                            'original_title': anime.get('title', '')
                        })
        
        # Find anime in multiple sources
        common_anime = {}
        for title, sources in title_sources.items():
            if len(sources) > 1:
                common_anime[title] = {
                    'sources': list(sources),
                    'source_count': len(sources),
                    'data': title_data[title]
                }
        
        # Sort by number of sources
        sorted_common = sorted(common_anime.items(), 
                             key=lambda x: x[1]['source_count'], 
                             reverse=True)
        
        print(f"Found {len(common_anime)} anime appearing in multiple sources:")
        
        for i, (title, info) in enumerate(sorted_common[:20]):  # Show top 20
            print(f"\n{i+1}. {title}")
            print(f"   Sources: {', '.join(info['sources'])} ({info['source_count']} sources)")
            
            # Show rankings and scores across sources
            for data in info['data']:
                score_text = f"Score: {data['score']}" if data['score'] != 'N/A' else "No score"
                print(f"   - {data['source']}: Rank {data['rank']} in {data['category']} | {score_text}")
        
        self.analysis_results['common_anime'] = {
            'total_common': len(common_anime),
            'top_common': dict(sorted_common[:50])  # Store top 50
        }
    
    def analyze_scores(self):
        """Analyze score distributions and patterns"""
        print("\n" + "="*50)
        print("SCORE ANALYSIS")
        print("="*50)
        
        all_scores = []
        source_scores = defaultdict(list)
        
        for source, categories in self.data.items():
            for category, anime_list in categories.items():
                for anime in anime_list:
                    score_str = anime.get('score', 'N/A')
                    if score_str != 'N/A':
                        try:
                            score = float(score_str)
                            if 0 <= score <= 10:  # Valid score range
                                all_scores.append(score)
                                source_scores[source].append(score)
                        except ValueError:
                            continue
        
        if all_scores:
            score_stats = {
                'total_scored_anime': len(all_scores),
                'average_score': mean(all_scores),
                'median_score': median(all_scores),
                'min_score': min(all_scores),
                'max_score': max(all_scores),
                'source_averages': {}
            }
            
            print(f"Total anime with scores: {score_stats['total_scored_anime']}")
            print(f"Overall average score: {score_stats['average_score']:.2f}")
            print(f"Median score: {score_stats['median_score']:.2f}")
            print(f"Score range: {score_stats['min_score']:.1f} - {score_stats['max_score']:.1f}")
            
            print("\nScore averages by source:")
            for source, scores in source_scores.items():
                if scores:
                    avg_score = mean(scores)
                    score_stats['source_averages'][source] = avg_score
                    print(f"  {source}: {avg_score:.2f} (from {len(scores)} entries)")
            
            self.analysis_results['score_analysis'] = score_stats
        else:
            print("No valid scores found in the data.")
    
    def category_analysis(self):
        """Analyze popularity of different categories"""
        print("\n" + "="*50)
        print("CATEGORY ANALYSIS")
        print("="*50)
        
        category_counts = Counter()
        category_by_source = defaultdict(Counter)
        
        for source, categories in self.data.items():
            for category, anime_list in categories.items():
                count = len(anime_list)
                category_counts[category] += count
                category_by_source[source][category] = count
        
        print("Most populated categories across all sources:")
        for category, count in category_counts.most_common(15):
            print(f"  {category}: {count} entries")
        
        print("\nCategory distribution by source:")
        for source, categories in category_by_source.items():
            print(f"\n{source.upper()}:")
            for category, count in categories.most_common(10):
                print(f"  {category}: {count} entries")
        
        self.analysis_results['category_analysis'] = {
            'overall_categories': dict(category_counts),
            'by_source': dict(category_by_source)
        }
    
    def source_comparison(self):
        """Compare different sources"""
        print("\n" + "="*50)
        print("SOURCE COMPARISON")
        print("="*50)
        
        source_comparison = {}
        
        for source, categories in self.data.items():
            unique_titles = set()
            total_entries = 0
            categories_with_data = 0
            
            for category, anime_list in categories.items():
                if anime_list:  # Category has data
                    categories_with_data += 1
                total_entries += len(anime_list)
                
                for anime in anime_list:
                    title = self.normalize_title(anime.get('title', ''))
                    if title:
                        unique_titles.add(title)
            
            source_comparison[source] = {
                'total_entries': total_entries,
                'unique_titles': len(unique_titles),
                'categories_with_data': categories_with_data,
                'duplicate_ratio': (total_entries - len(unique_titles)) / total_entries if total_entries > 0 else 0
            }
        
        print("Source comparison:")
        for source, stats in source_comparison.items():
            print(f"\n{source.upper()}:")
            print(f"  Total entries: {stats['total_entries']}")
            print(f"  Unique titles: {stats['unique_titles']}")
            print(f"  Categories with data: {stats['categories_with_data']}")
            print(f"  Duplicate ratio: {stats['duplicate_ratio']:.1%}")
        
        self.analysis_results['source_comparison'] = source_comparison
    
    def title_analysis(self):
        """Analyze title patterns and characteristics"""
        print("\n" + "="*50)
        print("TITLE ANALYSIS")
        print("="*50)
        
        all_titles = []
        title_lengths = []
        
        for source, categories in self.data.items():
            for category, anime_list in categories.items():
                for anime in anime_list:
                    title = anime.get('title', '').strip()
                    if title and title != 'N/A':
                        all_titles.append(title)
                        title_lengths.append(len(title))
        
        if title_lengths:
            title_stats = {
                'total_titles': len(all_titles),
                'average_length': mean(title_lengths),
                'median_length': median(title_lengths),
                'min_length': min(title_lengths),
                'max_length': max(title_lengths)
            }
            
            print(f"Title statistics:")
            print(f"  Total titles: {title_stats['total_titles']}")
            print(f"  Average length: {title_stats['average_length']:.1f} characters")
            print(f"  Median length: {title_stats['median_length']:.1f} characters")
            print(f"  Length range: {title_stats['min_length']} - {title_stats['max_length']} characters")
            
            # Find common words in titles
            word_counter = Counter()
            for title in all_titles:
                words = re.findall(r'\b\w+\b', title.lower())
                word_counter.update(words)
            
            print(f"\nMost common words in titles:")
            for word, count in word_counter.most_common(20):
                if len(word) > 2:  # Skip very short words
                    print(f"  {word}: {count} times")
            
            self.analysis_results['title_analysis'] = {
                'statistics': title_stats,
                'common_words': dict(word_counter.most_common(50))
            }
    
    def normalize_title(self, title: str) -> str:
        """Normalize title for comparison (remove special characters, convert to lowercase)"""
        if not title or title == 'N/A':
            return ''
        
        # Remove common prefixes/suffixes and normalize
        title = title.strip().lower()
        title = re.sub(r'\s+', ' ', title)  # Normalize whitespace
        title = re.sub(r'[^\w\s]', '', title)  # Remove special characters
        return title.strip()
    
    def export_analysis(self):
        """Export analysis results to JSON file"""
        output_file = 'anime_analysis_report.json'
        
        self.analysis_results['metadata'] = {
            'analysis_timestamp': __import__('time').strftime('%Y-%m-%d %H:%M:%S'),
            'source_file': self.combined_data_file,
            'analyzer_version': '1.0'
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
        
        print(f"\nAnalysis results exported to {output_file}")
    
    def export_to_csv(self, output_file: str = 'anime_analysis_summary.csv'):
        """Export a summary analysis to CSV"""
        if 'common_anime' not in self.analysis_results:
            print("No analysis data available. Run analyze_all() first.")
            return
        
        # Export common anime to CSV
        common_anime = self.analysis_results['common_anime']['top_common']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Title', 'Sources', 'Source Count', 'Details'])
            
            for title, info in common_anime.items():
                details = '; '.join([
                    f"{data['source']}:Rank{data['rank']}({data['score']})" 
                    for data in info['data']
                ])
                writer.writerow([
                    title,
                    ', '.join(info['sources']),
                    info['source_count'],
                    details
                ])
        
        print(f"Summary exported to {output_file}")


def main():
    analyzer = AnimeDataAnalyzer()
    analyzer.analyze_all()
    
    # Also export to CSV
    analyzer.export_to_csv()


if __name__ == "__main__":
    main() 