from neo4j import GraphDatabase
import csv


"""
WARNING!!!! WARNING!!! the crawl_results with domain boundary and without domain boundary fields are different!
especially the domain part. for without domain boundary it should be target_domain. why? its self explanatory. 
Just make sure to change the row['target_domain] to domain if ur running it for the with domain boundary dataset. 
"""
NEO4J_URI = "neo4j://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Hello123@"
CSV_FILE = "crawl_results_http_only.csv"

class Neo4jGraphLoader:
    def __init__(self, uri: str, username: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def create_constraints(self):
        with self.driver.session() as session:
            session.run("""
                CREATE CONSTRAINT url_unique IF NOT EXISTS 
                FOR (n:URL) REQUIRE n.full_url IS UNIQUE
            """)

    def load_csv_data(self, file_path: str):
        with self.driver.session() as session:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    session.run("""
                        MERGE (source:URL {full_url: $source_url})
                        ON CREATE SET 
                            source.domain = $domain,
                            source.page_title = $source_url_text,
                            source.content_type = $content_type
                        
                        MERGE (target:URL {full_url: $target_url})
                        ON CREATE SET 
                            target.domain = $domain,
                            target.page_title = $target_url_text,
                            target.content_type = $content_type
                        
                        MERGE (source)-[r:LINK_TO {
                            link_text: $source_url_text,
                            link_caption: $source_link_caption,
                            crawl_depth: toInteger($depth)
                        }]->(target)
                    """, {
                        'source_url': row['source_url'],
                        'source_url_text': row['source_url_text'],
                        'source_link_caption': row['source_link_caption'],
                        'target_url': row['target_url'],
                        'target_url_text': row['target_url_text'],
                        'target_link_caption': row['target_link_caption'],
                        'domain': row['target_domain'],
                        'depth': row['depth'],
                        'content_type': row['content_type'] or 'unknown'
                    })

    def print_stats(self):
        with self.driver.session() as session:
            stats = session.run("""
                MATCH (n:URL)
                WITH count(n) as nodes
                MATCH ()-[r:LINK_TO]->()
                RETURN nodes as total_urls, 
                       count(r) as total_links,
                       count(DISTINCT r.crawl_depth) as unique_depths
            """).single()
            
            print(f"Total URLs: {stats['total_urls']}")
            print(f"Total Links: {stats['total_links']}")
            print(f"Unique Depths: {stats['unique_depths']}")
    
loader = None
try:
    loader = Neo4jGraphLoader(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    loader.create_constraints()
    print("Loading web crawl data...")
    loader.load_csv_data(CSV_FILE)
    loader.print_stats()
except Exception as e:
    print(f"Error: {str(e)}")
finally:
    if loader:
        loader.close()