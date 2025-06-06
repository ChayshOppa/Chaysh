import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.core.crawler import ManualCrawler
from src.core.database import Database
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def crawl_and_store():
    # Initialize crawler and database
    crawler = ManualCrawler()
    db = Database()

    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)

    try:
        # Crawl all sources
        logging.info("Starting manual crawl...")
        results = await crawler.crawl_all_sources()

        # Store results in database
        total_added = 0
        for source_type, manuals in results.items():
            logging.info(f"Processing {len(manuals)} manuals from {source_type}")
            for manual in manuals:
                if db.add_manual(manual):
                    total_added += 1

        logging.info(f"Crawl completed. Added {total_added} new manuals to database.")

    except Exception as e:
        logging.error(f"Error during crawl: {str(e)}")
    finally:
        await crawler.close_session()

if __name__ == "__main__":
    asyncio.run(crawl_and_store()) 