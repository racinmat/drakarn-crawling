#!/usr/bin/env python3
"""
Test the data analyzer
"""

from data_analyzer import AnimeDataAnalyzer

def main():
    print("Testing Data Analyzer...")
    print("="*50)
    
    analyzer = AnimeDataAnalyzer('test_combined_results.json')
    
    try:
        analyzer.analyze_all()
        print("\n✅ Analysis completed successfully!")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 