import sqlite3
import pandas as pd
from collections import Counter

def analyze_crawler_data():
    conn = sqlite3.connect('web_crawler.db')
    
    def run_query(query, params=()):
        return pd.read_sql_query(query, conn, params=params)

    def print_section(title):
        print(f"\n{'='*50}\n{title}\n{'='*50}")

    print_section("Overall Statistics")
    
    stats_query = """
    SELECT 
        (SELECT COUNT(*) FROM pages) as total_pages,
        (SELECT COUNT(*) FROM links) as total_links,
        (SELECT AVG(depth) FROM links) as avg_crawl_depth,
        (SELECT MAX(depth) FROM links) as max_depth
    """
    stats = run_query(stats_query)
    print(stats)

    print_section("Top 10 Most Common Domains")
    
    domains_query = """
    SELECT domain, COUNT(*) as page_count
    FROM pages
    WHERE domain IS NOT NULL
    GROUP BY domain
    ORDER BY page_count DESC
    LIMIT 10
    """
    print(run_query(domains_query))

    print_section("Content Type Distribution")
    
    content_type_query = """
    SELECT content_type, COUNT(*) as count
    FROM pages
    WHERE content_type IS NOT NULL
    GROUP BY content_type
    ORDER BY count DESC
    """
    print(run_query(content_type_query))

analyze_crawler_data()