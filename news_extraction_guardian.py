import requests
import json
import time
from datetime import date, timedelta
from calendar import monthrange
from os import makedirs, listdir
from os.path import join, exists

API_ENDPOINT = "https://content.guardianapis.com/search"

def safe_request(url, params, max_retries=6):
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, timeout=15)
            data = resp.json()
        except Exception as e:
            print(f"Request error: {e}. Retrying...")
            time.sleep(2 ** attempt)
            continue

        if "response" in data:
            return data

        if "message" in data and "rate limit" in data["message"].lower():
            wait = 2 ** attempt
            print(f"Rate limit hit. Waiting {wait} seconds…")
            time.sleep(wait)
            continue

        print("Unexpected response:", data)
        return None

    print("Failed after max retries.")
    return None

# used for resuming as we cannot extract all articles in one go
def get_latest_downloaded_date(folder):
    files = sorted(f[:-5] for f in listdir(folder) if f.endswith(".json"))
    if not files:
        return None
    last = files[-1]  # YYYY-MM-DD format
    y, m, _ = map(int, last.split("-"))
    return y, m


def fetch_full_article(article_id, api_key):
    url = f"https://content.guardianapis.com/{article_id}"
    params = {
        "api-key": api_key,
        "show-fields": "all"
    }
    return safe_request(url, params)

def download_range(start_date_str, end_date_str, output_folder, api_key):

    makedirs(output_folder, exist_ok=True)

    start_y, start_m, _ = map(int, start_date_str.split("-"))
    end_y, end_m, _ = map(int, end_date_str.split("-"))

    # Resume, we start from the laterst downloaded files for efficiency 
    resume = get_latest_downloaded_date(output_folder)
    if resume:
        start_y, start_m = resume
        print(f"Resuming from {start_y}-{start_m:02d}")

    print(f"\n=== Downloading {start_date_str} → {end_date_str} ===\n")

    for year in range(start_y, end_y + 1):
        for month in range(1, 13):

            if (year == start_y and month < start_m) or (year == end_y and month > end_m):
                continue

            month_last = monthrange(year, month)[1]
            from_d = date(year, month, 1)
            to_d = date(year, month, month_last)

            print(f"Fetching list for {year}-{month:02d}...")

            all_articles = []
            page = 1
            total_pages = 1

            # started looking for articles 
            while page <= total_pages:

                params = {
                    "from-date": from_d.strftime("%Y-%m-%d"),
                    "to-date": to_d.strftime("%Y-%m-%d"),
                    "order-by": "newest",
                    "show-fields": "all",
                    "page-size": 200,
                    "page": page,
                    "api-key": api_key,

                    # Accident filtering using querywords and tags 
                    "q": (
                        "crash OR accident OR collision OR fata OR injured OR killed OR "
                        "pedestrian OR cyclist OR vehicle OR road"
                    ),
                    "tag": (
                        "society/road-accidents-and-safety|"
                        "uk/transport"
                    )
                }

                data = safe_request(API_ENDPOINT, params)
                if data is None:
                    print("Skipping this month due to errors.")
                    break

                resp = data["response"]

                if resp.get("total", 0) == 0:
                    print("   (No matching articles)")
                    break

                total_pages = resp.get("pages", 1)
                all_articles.extend(resp.get("results", []))

                print(f"Page {page}/{total_pages}")
                page += 1
                time.sleep(0.2)

            print(f"Found {len(all_articles)} candidate articles")

            full_articles_by_day = {}

            for art in all_articles:
                article_id = art["id"]  

                full_data = fetch_full_article(article_id, api_key)
                if full_data is None:
                    continue

                content = full_data["response"].get("content", None)
                if not content:
                    continue

                # extracting the publication date
                pubdate = content["webPublicationDate"][:10]
                full_articles_by_day.setdefault(pubdate, []).append(content)

                time.sleep(0.15)  # small throttle

            for pubdate, items in full_articles_by_day.items():
                fname = join(output_folder, pubdate + ".json")
                if exists(fname):
                    continue
                with open(fname, "w") as f:
                    f.write(json.dumps(items, indent=2))

            print(f"Saved {len(full_articles_by_day)} daily files\n")


BASE_DIR = "project"
MY_API_KEY = open(join(BASE_DIR, "creds_guardian_text.txt")).read().strip()

ARTICLES_DIR = join(BASE_DIR, "articles")
articles_1999_2009 = join(ARTICLES_DIR, "1999-2009")
articles_2010_2019 = join(ARTICLES_DIR, "2010-2019")
articles_2020_2025 = join(ARTICLES_DIR, "2020-2025")

# 1999–2009
download_range("1999-01-01", "2009-12-31", articles_1999_2009, MY_API_KEY)

# 2010–2019
download_range("2010-01-01", "2019-12-31", articles_2010_2019, MY_API_KEY)

# 2020–2025
download_range("2020-01-01", "2025-09-30", articles_2020_2025, MY_API_KEY)
print("Finished collecting the data")
