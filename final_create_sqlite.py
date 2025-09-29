import sqlite3
import csv
from pathlib import Path

def create_database():
    conn = sqlite3.connect('web_crawler.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL UNIQUE,
        domain TEXT,
        title TEXT,
        content_type TEXT,
        status_code INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_page_id INTEGER,
        target_page_id INTEGER,
        link_text TEXT,
        link_caption TEXT,
        depth INTEGER,
        FOREIGN KEY (source_page_id) REFERENCES pages (id),
        FOREIGN KEY (target_page_id) REFERENCES pages (id)
    )
    ''')

    def insert_page(url, domain, content_type, status_code):
        cursor.execute('''
        INSERT OR IGNORE INTO pages (url, domain, content_type, status_code)
        VALUES (?, ?, ?, ?)
        ''', (url, domain, content_type, status_code))
        return cursor.lastrowid or cursor.execute(
            'SELECT id FROM pages WHERE url = ?', (url,)).fetchone()[0]

    def process_csv(file_path):
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                source_id = insert_page(
                    row['source_url'],
                    row['domain'],
                    row['content_type'],
                    int(row['status_code']) if row['status_code'] else None
                )

                target_id = insert_page(
                    row['target_url'],
                    row['domain'],
                    row['content_type'],
                    int(row['status_code']) if row['status_code'] else None
                )

                cursor.execute('''
                INSERT INTO links (source_page_id, target_page_id, link_text, link_caption, depth)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    source_id,
                    target_id,
                    row['source_url_text'],
                    row['source_link_caption'],
                    int(row['depth'])
                ))

        conn.commit()

    csv_file = 'crawl_results_with_domain_boundary.csv'  
    if Path(csv_file).exists():
        process_csv(csv_file)
        print(f"Database created successfully with data from {csv_file}")
    else:
        print(f"Warning: {csv_file} not found. Database schema created without data.")

    conn.close()


create_database()