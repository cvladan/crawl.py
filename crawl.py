import os
import sys
import psutil
import asyncio
import requests
import argparse
import re
from xml.etree import ElementTree
from urllib.parse import urlparse
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

__location__ = os.path.dirname(os.path.abspath(__file__))
__output__ = os.path.join(__location__, "crawls")

# Append parent directory to system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def crawl_parallel(urls: List[str], max_concurrent: int = 3):
    print("\n=== Parallel Crawling with Browser Reuse + Memory Check ===")

    # We'll keep track of peak memory usage across all tasks
    peak_memory = 0
    process = psutil.Process(os.getpid())

    def log_memory(prefix: str = ""):
        nonlocal peak_memory
        current_mem = process.memory_info().rss  # in bytes
        if current_mem > peak_memory:
            peak_memory = current_mem
        print(f"{prefix} Current Memory: {current_mem // (1024 * 1024)} MB, Peak: {peak_memory // (1024 * 1024)} MB")

    # Minimal browser config
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,   # corrected from 'verbos=False'
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )
    crawl_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(threshold=0.48, threshold_type="fixed", min_word_threshold=0)
        ),
    )

    # Create the crawler instance
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    accumulated_content = []

    try:
        # We'll chunk the URLs in batches of 'max_concurrent' 
        success_count = 0
        fail_count = 0
        for i in range(0, len(urls), max_concurrent):
            batch = urls[i : i + max_concurrent]
            tasks = []

            for j, url in enumerate(batch):
                # Unique session_id per concurrent sub-task
                session_id = f"parallel_session_{i + j}"
                task = crawler.arun(url=url, config=crawl_config, session_id=session_id)
                tasks.append(task)

            # Check memory usage prior to launching tasks
            log_memory(prefix=f"Before batch {i//max_concurrent + 1}: ")

            # Gather results
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check memory usage after tasks complete
            log_memory(prefix=f"After batch {i//max_concurrent + 1}: ")

            # Evaluate results
            for url, result in zip(batch, results):
                if isinstance(result, Exception):
                    print(f"Error crawling {url}: {result}")
                    fail_count += 1
                elif result.success:
                    success_count += 1
                    # Save markdown
                    domain = urlparse(url).netloc.replace('www.', '')
                    # Extract slug from URL path
                    slug = re.sub(r'[^a-zA-Z0-9]+', '-', urlparse(url).path.strip('/'))
                    output_dir = os.path.join(__output__, domain)
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # Write individual file
                    individual_filename = f"{slug}.md" if slug else "index.md"
                    with open(os.path.join(output_dir, individual_filename), 'w') as file:
                        file.write(result.markdown_v2.fit_markdown)

                    # Accumulate content for combined file
                    accumulated_content.append({
                        "url": url,
                        "content": result.markdown_v2.fit_markdown
                    })
                else:
                    fail_count += 1

        print(f"\nSummary:")
        print(f"  - Successfully crawled: {success_count}")
        print(f"  - Failed: {fail_count}")

    finally:
        print("\nClosing crawler...")
        await crawler.close()
        # Final memory log
        log_memory(prefix="Final: ")
        print(f"\nPeak memory usage (MB): {peak_memory // (1024 * 1024)}")

        # Write accumulated content to combined file
        for domain, files in accumulated_content_by_domain.items():
            combined_output_dir = os.path.join(__output__, domain)
            os.makedirs(combined_output_dir, exist_ok=True)
            combined_output_path = os.path.join(combined_output_dir, "_combined.md")
            
            with open(combined_output_path, 'w') as file:
                for entry in files:
                    file.write(f"<url>{entry['url']}</url>\n")
                    file.write(f"<content>\n{entry['content']}\n</content>\n\n")
            
            print(f"Combined output for {domain} written to: {combined_output_path}")

def generate_accumulated_content(urls, results):
    accumulated_content = []
    for url, result in zip(urls, results):
        if result.success:
            accumulated_content.append(f"<url>{url}</url>\n<content>\n{result.markdown_v2.fit_markdown}\n</content>\n")
    return accumulated_content

def get_pydantic_ai_docs_urls(sitemap_url: str):
    """
    Fetches all URLs from the provided sitemap URL.
    
    Args:
        sitemap_url (str): URL of the sitemap to parse
    
    Returns:
        List[str]: List of URLs
    """            
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        # Parse the XML
        root = ElementTree.fromstring(response.content)
        
        # Extract all URLs from the sitemap
        # The namespace is usually defined in the root element
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
        
        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []        

async def main():
    parser = argparse.ArgumentParser(description="Web crawler for sitemap URLs")
    parser.add_argument(
        '-s', '--sitemap',
        type=str,
        default="https://www.cnc24.com/sitemap.xml",
        help="URL of the sitemap to crawl (default: https://www.cnc24.com/sitemap.xml)"
    )
    args = parser.parse_args()
    
    urls = get_pydantic_ai_docs_urls(args.sitemap)
    if urls:
        print(f"Found {len(urls)} URLs to crawl")
        await crawl_parallel(urls, max_concurrent=10)
    else:
        print("No URLs found to crawl")    

if __name__ == "__main__":
    asyncio.run(main())
