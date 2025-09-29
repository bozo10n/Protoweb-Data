# Mining and Mapping the Protoweb

## Introduction

The early 2000s is a foundational era of the internet, widely remembered by static web pages and nascent hyperlink structures. Understanding the structure and behaviour of this era of the internet is vital for tracing the evolution of modern web tech. This project aims to mine and map the Protoweb which is a Open-Source project that contains a catalog of restored sites from the early 2000s by creating a dataset encompassing approximately 3001 pages across 40 domains. Our methodology includes using a custom-built web crawler, metadata such as page title, HTML content, and hyper link structures are extracted and stored in 3 formats which are CSV for raw data, SQLite for relational analysis, and Neo4j for graph based visualization. The relational database model facilitates structured queries and analysis of page interconnections, while the graph database offers useful insight into connectivity patterns, and early concepts such as network traversal. By modeling the Protoweb as a network of nodes and edges, the project reveals vital information regarding the early internet.

## System Architecture

The web crawler implementation utilizes Python libraries such as Beautiful soup to systematically traverse and store web content through a depth-first traversal approach from specified domains. The system architecture consists of multiple interconnected components that work together to crawl and store websites efficiently and safely.

The crawler is built on a class-based system with 3 main components. First the Initialization Component handles setup tasks, managing crawler parameters such as (max_depth), maintaining HTTP connections, organizing output directories, and validating URLs. Second, the Data Collection Pipeline manages URL processing, network requests, HTML content extraction, and link discovery. Third, the Storage system handles data management through CSV writing, HTML content storage, and safe file naming for HTML.

## Database Preparation

### CSV File Structure and Purpose

The web crawling process generates a CSV file that serves as the raw data repository, it captures the details regarding the URL connections. The CSV file contains twelve distinct columns that document the relationships and characteristics of discovered web links. The key columns include the source and target URLs, link captions, domain information, crawl metadata, and response details. The CSV’s primary response extends beyond just data collection, it functions as an intermediary before the data is imported into more complicated database systems such as SQLite and Graph DB.

### SQLite Database: Relational Data Management

Transitioning from the CSV file, the SQLite database offers a more structured and relational approach for data management and analysis. The proposed schema comprises two primary tables, pages and links.

a. Pages: The pages table is the foundational element of the database. Each page is uniquely identified by an auto-incremented integer ID and its URL, domain, link caption, page title, and content type.
b. Links: The companion links table represents the interconnection between each page, establishing a record of hyperlink relationships. By implementing a foreign key constraints to the pages table, the database maintains references while representing link metadata. Each link entry contains source and target page identifiers, link text and caption, and crawl depth.

### Graph Database: Network Structure and Analysis

The Neo4j implementation transforms the web crawling data into an interconnected network representation. Unlike traditional tabular databases, this graph model captures the relational nature of web pages through a node and edge based structure.

a. URL nodes: Each URL would be a node. Core attributes include, Full URL, Domain, Page title, Content type.
b. Edges or Links: Directed or :LINK_TO relationship between each URL node. Core attributes include, Link text, Link Caption, Crawl Depth.

## Challenges and Solutions

These are some challenges I encountered during my implementation, some are solved and unsolved.
a. Incomplete HTTP response: Handling Partial Data Retrieval: The crawler consistently encountered IncompleteRead exceptions, where HTTP responses were frequently interrupted or truncated. This issue significantly impacted my data collection process. Initially, the problem prevented data retrieval altogether but I was able to solve this issue by:
- Enabling streaming in HTTP requests for chunked data processing.
- Adding robust error handling and retry mechanisms.
- Used .session() to maintain connection persistence.
- Introduced timeout and retry logic to manage unstable network state.
b. Web Scraping Framework Selection: From Selenium to BeautifulSoup: Initial attempts using Selenium for web scraping was problematic. The framework’s complexity created significant implementation problems, particularly in handling early web content and maintaining parsing capabilities.
c. Proxy and Rate Limiting Complications: The crawler consistently encountered consistent rate limits or unstable Proxy states.
d. Accidental Overwrite: During the development and testing of the web crawler, critical data management issues occurred which resulted in unintentional data loss. The crawler had successfully collected approximately 6000 samples with corresponding HTML content across 70 domains. However, during script iteration and testing, I ran the script without modifying the output file name which resulted in complete data overwrite.
e. Domain Boundary Oversight and Scope Drift: Another significant oversight occurred during the web crawl. Initially, the crawler included domain boundary logic to ensure it crawled with a list of predefined domains listed in a domains.txt file. However, due to other issues, the task of removing this logic was forgotten and the mistake went unnoticed. This problem was only discovered after a night of scraping and dataset preparation. When the dataset was re-scraped without boundaries to compensate, it still failed to reach the desired sample size due to limited time constraints.
f. Time Constraints: Despite working on this project for weeks I wasn’t able to finish the analysis I wanted to do with the SQLite database nor was I able to reach the Sample Size I desired. The dataset could also be greatly enriched and improved with some minor bug fixes and some more time to build a dataset without domain boundaries.

## Results and Data Analysis

There are a total of two datasets, First a dataset with domain boundaries with a sample of 3900 pages spanning 40-50 different domains, the second dataset with a sample of approximately 500 pages spanning 25 domains. I was unable to build the second dataset in time due to an error during the crawling process (refer to challenges and solutions). The crawling process collected a variety of metadata, including page titles, content types, hyperlink relationships, and additional crawl-related metadata. The raw data was captured in CSV format, which provided a simple tabular representation of the relationships between different pages. Then I transformed and transferred this data into both a relational SQLite database and a graph-based Neo4j database for further analysis.

### Top 10 Most Common Domains

| Domain | Page Count |
|---|---|
| cd.textfiles.com | 698 |
| simpsonsarchive.com | 583 |
| nethack.org | 298 |
| www.cornica.org | 280 |
| theoldnet.com | 233 |
| system7today.com | 180 |
| falconfly.3dfx.pl | 107 |
| nofi.mariteaux.somnolescent.net | 88 |
| retrosite.org | 76 |
| www.warpstream.net | 62 |

### Content Type Distribution

| Content Type | Count |
|---|---|
| text/html | 932 |
| text/html; charset=utf-8 | 449 |
| text/html; charset=UTF-8 | 385 |
| [empty] (unclassified content) | 286 |
| text/html; charset=iso-8859-1 | 233 |
| application/zip | 167 |
| application/x-msdownload | 126 |

## Future Directions

The project opens up numerous possibilities for further research:
a. Extended Domain and Temporal Scope: Expanding the list of domains and content from other periods would provide a better view of the web’s evolution. This would involve tackling the issues related to incomplete responses and scaling the crawler for a broader coverage.
b. Dynamic Content Crawling: Enhancing the crawler to handle dynamic content with frameworks like selenium could enrich the dataset with more interactive elements of early websites that static crawlers like mine may miss.
c. Integration with Machine Learning: Applying machine learning techniques to predict patterns in early web connectivity or reconstruct missing data could provide new insights that might go unnoticed with traditional analysis.
d. Publication: Publishing the dataset as an open-source resource for researchers and hobbyists could cause a more comprehensive exploration of the early web. However, before doing so, I would like to improve and enrich both the crawler and the dataset.

## Project Structure

```
.
├── 1175516_final_create_neo4j_graph.py
├── 1175516_final_create_sqlite.py
├── 1175516_final_domain_no_domain_boundary.py
├── 1175516_final_domain_with_domain_boundary.py
├── 1175516_final_sqlanalysis.py
├── domains.txt
├── extra_unfinished_data/
├── final_data/
└── Mining and Mapping the Protoweb.docx
```

## Scripts

### `1175516_final_domain_with_domain_boundary.py`

*   **Purpose:** Crawls websites starting from a list of domains in `domains.txt`, staying within the same domain.
*   **Input:** `domains.txt`
*   **Output:**
    *   `crawl_results_domain_boundary.csv`: A CSV file containing the crawled data.
    *   `html_pages_domain_boundary/`: A directory containing the saved HTML files.
*   **Proxy:** `http://wayback.protoweb.org:7856`

### `1175516_final_domain_no_domain_boundary.py`

*   **Purpose:** Crawls websites starting from a list of domains in `domains.txt`, without enforcing a domain boundary.
*   **Input:** `domains.txt`
*   **Output:**
    *   `crawl_results_http_only.csv`: A CSV file containing the crawled data.
    *   `html_pages__http_only/`: A directory containing the saved HTML files.
*   **Proxy:** `http://wayback2.protoweb.org:7851`

### `1175516_final_create_sqlite.py`

*   **Purpose:** Creates a SQLite database (`web_crawler.db`) and populates it with data from `crawl_results_with_domain_boundary.csv`.
*   **Input:** `crawl_results_with_domain_boundary.csv`
*   **Output:** `web_crawler.db`

### `1175516_final_create_neo4j_graph.py`

*   **Purpose:** Loads data from a CSV file into a Neo4j graph database.
*   **Input:** `crawl_results_http_only.csv` (can be configured for `crawl_results_with_domain_boundary.csv`).
*   **Output:** A graph in the configured Neo4j database.
*   **Note:** The script contains a warning about differences in the CSV format between the two crawl variations.

### `1175516_final_sqlanalysis.py`

*   **Purpose:** Performs basic analysis on the `web_crawler.db` database.
*   **Input:** `web_crawler.db`
*   **Output:** Prints analysis results to the console.

## How to Run

1.  **Install Dependencies:**
    ```bash
    pip install requests beautifulsoup4 pandas neo4j
    ```
2.  **Configure `domains.txt`:** Add the seed domains to this file, one per line.
3.  **Run the Crawler:** Choose one of the crawler scripts to run:
    *   For domain-bounded crawling: `python 1175516_final_domain_with_domain_boundary.py`
    *   For unbounded crawling: `python 1175516_final_domain_no_domain_boundary.py`
4.  **Create the SQLite Database:** `python 1175516_final_create_sqlite.py`
5.  **Load the Neo4j Graph:**
    *   Make sure your Neo4j database is running.
    *   Update the `NEO4J_URI`, `NEO4J_USER`, and `NEO4J_PASSWORD` constants in `1175516_final_create_neo4j_graph.py`.
    *   Run the script: `python 1175516_final_create_neo4j_graph.py`
6.  **Analyze the Data:** `python 1175516_final_sqlanalysis.py`

## Data

*   **`crawl_results_domain_boundary.csv` / `crawl_results_http_only.csv`:** These CSV files contain the raw crawl data.
*   **`web_crawler.db`:** A SQLite database containing the structured crawl data.
*   **`html_pages_domain_boundary/` / `html_pages__http_only/`:** These directories contain the HTML source of the crawled pages.
*   **`final_data/`:** This directory contains the final data generated by the project.
*   **`extra_unfinished_data/`:** This directory contains extra data that was not used in the final project.
