import requests, re, csv, time, random
from bs4 import BeautifulSoup

NICHE = "skincare"
TARGET = 1000
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_domains():
    domains = set()
    # بنجيب متاجر السكين كير من بحث Bing
    for page in range(0, 100, 10):
        url = f"https://www.bing.com/search?q=site:myshopify.com+{NICHE}&first={page}&count=50"
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            found = re.findall(r'https?://([a-z0-9\-]+\.myshopify\.com)', r.text)
            for d in found:
                domains.add(d)
            print(f"Page {page} -> total {len(domains)}")
            if len(domains) >= TARGET:
                break
            time.sleep(2)
        except Exception as e:
            print(e)
    return list(domains)[:TARGET]

def find_email(domain):
    for path in ["/", "/pages/contact-us", "/pages/contact", "/contact"]:
        try:
            r = requests.get(f"https://{domain}{path}", headers=HEADERS, timeout=15)
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
            # فلتر ايميلات ملهاش لازمة
            clean = [e for e in emails if not any(x in e.lower() for x in ['example', 'wix', 'shopify', 'png', 'jpg', 'sentry'])]
            if clean:
                return clean[0]
        except:
            pass
    return ""

domains = get_domains()
print(f"Found {len(domains)} stores")

with open("emails.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["store", "website", "email"])
    for d in domains:
        email = find_email(d)
        shop_url = f"https://{d.replace('.myshopify.com','')}.com"
        # حاول تجيب الدومين الحقيقي
        try:
            r = requests.get(f"https://{d}", headers=HEADERS, timeout=10, allow_redirects=True)
            shop_url = r.url.rstrip("/")
        except:
            pass
        w.writerow([d, shop_url, email])
        print(f"{d} -> {email}")
        time.sleep(0.5)
print("DONE")
