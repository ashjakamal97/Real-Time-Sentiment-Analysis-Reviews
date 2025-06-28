# FILE 1: scraper.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime, timedelta
import time
import textwrap
import re

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(), options=options)
wait = WebDriverWait(driver, 10)

#input url
product_urls = {
    "iPhone 15": "https://www.flipkart.com/apple-iphone-15-black-128-gb/product-reviews/itm6ac6485515ae4?pid=MOBGTAGPTB3VS24W",
    "Samsung Galaxy A35": "https://www.flipkart.com/samsung-galaxy-a35-5g-awesome-navy-256-gb/product-reviews/itm2d2e398127998?pid=MOBGYT2HEEYGMZFH",
    "Samsung 7kg Washing Machine": "https://www.flipkart.com/samsung-7-kg-5-star-ecobubble-technology-hygiene-steam-digital-inverter-fully-automatic-front-load-washing-machine-in-built-heater-grey/product-reviews/itm1eb327d8b2ee1?pid=WMNGYGJKCVNKSZWY",
    "Milton Electric Kettle": "https://www.flipkart.com/milton-electro-electric-kettle/product-reviews/itm7071829829f15?pid=EKTG26FTFQSG84CG",
    "Realme C61": "https://www.flipkart.com/realme-c61-safari-green-128-gb/product-reviews/itmd6ddbcefce040?pid=MOBHFRKRAVXUKDGX",
    "MarQ AC 2025": "https://www.flipkart.com/marq-flipkart-2025-1-ton-5-star-split-inverter-5-in-1-convertible-turbo-cool-technology-ac-white/product-reviews/itmfd8dfe14ce4f5?pid=ACNH76Z3Q6TDP42V"
   
}


def fix_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%d %b, %Y").strftime("%Y-%m-%d")
    except:
        return date_str.strip()

MAX_PAGES=10 #input user limit
all_reviews = []  # ✅ This line is essential

def scraper(pages, url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(), options=options)
    wait = WebDriverWait(driver, 10)

    MAX_PAGES = pages
    all_reviews = []

    # Validate Flipkart product review URL
    if not isinstance(url, str) or not re.match(r"^https://www\.flipkart\.com/.+/product-reviews/", url):
        print("❌ Invalid URL. Please provide a valid Flipkart product review URL.")
        driver.quit()
        return pd.DataFrame()
    match = re.search(r"flipkart\.com/([^/]+)/product-reviews", url)
    if match:
        product = match.group(1).replace("-", " ").title()
    else:
        product = "Unknown Product"
    print(f"\n🔍 Scraping: {product}")
    driver.get(url)
    page = 0

    while page < MAX_PAGES:
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "z9E0IG")))
            authors = driver.find_elements(By.CSS_SELECTOR, "._2NsDsF.AwS1CA")
            ratings = driver.find_elements(By.CLASS_NAME, "XQDdHH")
            reviews = driver.find_elements(By.CLASS_NAME, "ZmyHeo")
            dates = driver.find_elements(By.XPATH, "//p[contains(@class, '_2NsDsF') and not(contains(@class, 'AwS1CA'))]")
            
            # Find the element containing total pages info
            try:
                total_pages_elem = driver.find_element(By.CLASS_NAME, "_1G0WLw.mpIySA")
                total_pages_text = total_pages_elem.text  # e.g., "Page 1 of 1,169"
                match = re.search(r'of\s+([\d,]+)', total_pages_text)
                if match:
                    total_review_pages = int(match.group(1).replace(',', ''))
                    print(f"Total review pages: {total_review_pages}")
                else:
                    total_review_pages = None
                    print("Could not parse total review pages.")
            except Exception as e:
                total_review_pages = None
                print(f"Error fetching total review pages: {e}")
            
            if not reviews:
                print(f"❌ No reviews on page {page + 1}")
                break

            for a, r, t, d in zip(authors, ratings, reviews, dates):
                all_reviews.append({
                        "Product": product,
                        "Author": a.text.strip(),
                        "Rating": r.text.strip(),
                        "Review": textwrap.fill(t.text.strip(), width=50),
                        "Date": fix_date(d.text.strip())
                    })

            print(f"✅ Page {page + 1} scraped.")
            page += 1

            try:
                next_button = driver.find_element(By.XPATH, "//span[text()='Next']")
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(5)
            except Exception as e:
                print(f"⏹ No Next button or error: {e}")
                break

        except Exception as e:
            print(f"⚠ Error on {product}, page {page}: {e}")
            break
    print(f"✅ Scraping completed for {product}. Total pages scraped: {page + 1}")
    df = pd.DataFrame(all_reviews)
    df["date_review"] = df["Date"].apply(fix_date)
    df['date_review'] = df['date_review'].apply(fix_date)
    df['Parsed_Date'] = pd.to_datetime(df['date_review'], format='%b, %Y', errors='coerce')
    df = df.set_index('Parsed_Date').sort_index()

    driver.quit()
    return df, total_review_pages

def fix_date(x):
        if pd.isna(x):
            return x
        x = x.strip()

        # Already formatted like "Oct, 2023"
        if re.match(r'^[A-Za-z]+, \d{4}$', x):
            return x

        # Match "X days ago"
        match_days = re.match(r'(\d+)\s+days?\s+ago', x)
        if match_days:
            days_ago = int(match_days.group(1))
            estimated_date = datetime.today() - timedelta(days=days_ago)
            return estimated_date.strftime("%b, %Y")

        # Match "X months ago"
        match_months = re.match(r'(\d+)\s+months?\s+ago', x)
        if match_months:
            months_ago = int(match_months.group(1))
            estimated_date = datetime.today() - timedelta(days=months_ago * 30)
            return estimated_date.strftime("%b, %Y")

        # Match "1 month ago" (non-numeric)
        if "month ago" in x:
            estimated_date = datetime.today() - timedelta(days=30)
            return estimated_date.strftime("%b, %Y")

        # Match "1 day ago" (non-numeric)
        if "day ago" in x:
            estimated_date = datetime.today() - timedelta(days=1)
            return estimated_date.strftime("%b, %Y")

        return "Unknown"


