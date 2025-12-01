import os
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

# --- CONFIGURATION ---
# Point this to the extracted 'dataset' folder
BASE_DIR = "../data/dataset" 
WEBSITE_DIR = os.path.join(BASE_DIR, "website_crawls", "dataset")
NEWS_DIR = os.path.join(BASE_DIR, "news_articles", "dataset")
OUTPUT_FILE = "../output/master_timeline.csv"

def parse_date_from_folder(folder_name):
    """Attempts to parse date from folder name (e.g., '2017-05-15')"""
    try:
        return datetime.strptime(folder_name, "%Y-%m-%d").date()
    except ValueError:
        return None

def scan_website_snapshots():
    records = []
    
    # 1. Scan HTML for Text Content
    html_root = os.path.join(WEBSITE_DIR, "html")
    if os.path.exists(html_root):
        for date_folder in os.listdir(html_root):
            date_obj = parse_date_from_folder(date_folder)
            if not date_obj: continue # Skip if not a date folder
            
            file_path = os.path.join(html_root, date_folder, "index.html")
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        soup = BeautifulSoup(f, 'html.parser')
                        # Get title and main paragraphs
                        title = soup.title.string if soup.title else "No Title"
                        text = soup.get_text()[:500].replace('\n', ' ').strip() # Preview only
                        
                        records.append({
                            "date": date_obj,
                            "type": "Web Snapshot",
                            "source": date_folder,
                            "content_snippet": text,
                            "asset_path": file_path
                        })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    # 2. Scan Images to link them to Dates
    img_root = os.path.join(WEBSITE_DIR, "images")
    if os.path.exists(img_root):
        for date_folder in os.listdir(img_root):
            date_obj = parse_date_from_folder(date_folder)
            if not date_obj: continue
            
            folder_path = os.path.join(img_root, date_folder)
            for img in os.listdir(folder_path):
                records.append({
                    "date": date_obj,
                    "type": "Image Asset",
                    "source": date_folder,
                    "content_snippet": f"Visual asset: {img}",
                    "asset_path": os.path.join(folder_path, img)
                })

    return records

def scan_news_articles():
    records = []
    html_root = os.path.join(NEWS_DIR, "html")
    
    if os.path.exists(html_root):
        for folder in os.listdir(html_root):
            file_path = os.path.join(html_root, folder, "index.html")
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        soup = BeautifulSoup(f, 'html.parser')
                        # Try to find headline (h1)
                        headline = soup.find('h1').get_text() if soup.find('h1') else folder
                        
                        records.append({
                            "date": datetime(2025, 1, 1).date(), # Placeholder date for news
                            "type": "News Article",
                            "source": folder,
                            "content_snippet": headline.strip(),
                            "asset_path": file_path
                        })
                except Exception as e:
                    pass
    return records

def main():
    print("Scanning Website History...")
    web_data = scan_website_snapshots()
    
    print("Scanning News Articles...")
    news_data = scan_news_articles()
    
    # Combine
    all_data = web_data + news_data
    df = pd.DataFrame(all_data)
    
    # Sort Chronologically
    # (News articles with placeholder dates will go to the end/start)
    df = df.sort_values(by="date")
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSUCCESS: Generated Timeline with {len(df)} data points.")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()