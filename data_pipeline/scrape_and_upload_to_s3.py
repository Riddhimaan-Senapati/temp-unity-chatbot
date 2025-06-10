from urllib.parse import urlparse
import time
import os
import boto3
from dotenv import load_dotenv
import io # Used to treat string content like a file object
import datetime

from data_pipeline.scrapping_helper import (
    fetch_html,
    extract_links_from_html,
    extract_text_content,
    filename_from_url,
    MASTER_PAGE_URL,
    HEADERS,
    REQUEST_DELAY_SECONDS,
    MASTER_NETLOC,
    DATASETS_PATH_PREFIX_TO_BLOCK,
    ALLOWED_DATASETS_PAGE,
    BLOCKED_EDU_DOMAINS
)

# Load environment variables (e.g., AWS credentials) from a .env file
load_dotenv()

# --- Configuration  ---

# S3 bucket name
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
# S3 path prefix to upload documents to
S3_FOLDER_PREFIX = os.getenv("S3_FOLDER_PREFIX")

# Master Netloc is derived from the imported MASTER_PAGE_URL
MASTER_NETLOC = urlparse(MASTER_PAGE_URL).netloc


# --- Helper Functions  ---

def url_to_s3_key(url, s3_prefix=""):
    return s3_prefix+filename_from_url(url)

# --- S3 Upload Function ---

def upload_content_to_s3(content, bucket_name, s3_key, metadata=None):
    """
    Uploads string content to an S3 object.
    """
    if not content:
        print(f"  No content to upload for {s3_key}.")
        return False

    if bucket_name == "YOUR_S3_BUCKET_NAME":
         print("\nERROR: S3_BUCKET_NAME is not set. Please replace 'YOUR_S3_BUCKET_NAME' with your actual bucket name.")
         return False

    s3 = boto3.client('s3')
    try:
        # Use io.BytesIO to treat the string content as a file-like object
        # Encode content to bytes (utf-8 is standard for text)
        content_bytes = content.encode('utf-8')
        content_buffer = io.BytesIO(content_bytes)

        print(f"Uploading content to s3://{bucket_name}/{s3_key}")
        # Pass metadata as a parameter
        s3.upload_fileobj(content_buffer, bucket_name, s3_key, ExtraArgs={'Metadata': metadata} if metadata else None)
        print(f"Successfully uploaded {s3_key}")
        return True
    except Exception as e:
        print(f"Error uploading to s3://{bucket_name}/{s3_key}: {e}")
        return False


# --- Main Data Pipeline Logic ---

def scrape_and_upload_link(link_url):
        if REQUEST_DELAY_SECONDS > 0:
            time.sleep(REQUEST_DELAY_SECONDS)

        linked_page_html = fetch_html(link_url)
        if linked_page_html:
            content = extract_text_content(linked_page_html)
            print(f"Extracted ~{len(content)} characters from {link_url}")

            if not content or content.startswith("Error:"):
                 print(f"  Skipping upload for {link_url} due to empty or error content.")
                 return

            # Generate S3 key from the URL
            s3_key = url_to_s3_key(link_url, s3_prefix=S3_FOLDER_PREFIX)

            if s3_key:
                 # Add source URL to the content before uploading
                 content_with_source = f"# Source: {link_url}\n\n" + content

                 # Prepare metadata
                 current_datetime = datetime.datetime.now().isoformat()
                 doc_metadata = {
                     'SourceUrl': link_url,
                     'ScrapedDatetime': current_datetime
                 }

                 # Upload content with metadata
                 upload_content_to_s3(content_with_source, S3_BUCKET_NAME, s3_key, metadata=doc_metadata)
            else:
                 print(f"  Could not generate valid S3 key for URL: {link_url}")

        else:
            print(f"  Could not fetch HTML content for {link_url}. Skipping upload.")


def run_scrape_and_upload_pipeline():
    print(f"Starting scrape and upload pipeline...")
    # Use imported constants in print statements for clarity
    print(f"Scraping master page: {MASTER_PAGE_URL}")
    print(f"Uploading to S3 bucket: {S3_BUCKET_NAME} with prefix: {S3_FOLDER_PREFIX}")
    # Optionally print other scraping constants if desired for debugging/info


    master_html = fetch_html(MASTER_PAGE_URL) # Using imported function
    if not master_html:
        print("Failed to fetch master page. Exiting.")
        return

    print(f"\nExtracting links from {MASTER_PAGE_URL}...")
    # Using imported function. This function uses the constants from scrapping.py
    links_to_scrape = extract_links_from_html(master_html, MASTER_PAGE_URL)


    print(f"Found {len(links_to_scrape)} unique links to scrape after filtering.")
    if not links_to_scrape:
        print("No links found on the master page to scrape (after filtering).")
        return

    print("\n--- Scraping and Uploading Content Directly to S3 ---")

    for i, link_url in enumerate(links_to_scrape):
        print(f"\n({i+1}/{len(links_to_scrape)}) Processing: {link_url}")
        
        scrape_and_upload_link(link_url)

    print("\nData pipeline finished.")


if __name__ == "__main__":
    run_scrape_and_upload_pipeline()