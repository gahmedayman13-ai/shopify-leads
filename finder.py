import requests, re, csv, time, json

NICHE = "skincare"
TARGET = 1000
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_domains():
    domains = set()
    # بنجيب من أرشيف Common Crawl - مش محظور من جيت هب
    indexes = ["CC-MAIN-2025-30", "CC-MAIN-2025-21", "CC-MAIN-2025-13"]
    for idx in indexes:
        url = f"https://index.commoncrawl.org/{idx}-index?url=*.myshopify.com&output=json&limit=20000&filter=status:200"
        try:
            print(f"Trying {idx}...")
            r = requests.get(url, headers=HEADERS, timeout=60)
            for line in r.text.splitlines():
                try:
                    j = json.loads(line)
                    host = j.get("url", "").split("/")[2] if "://" in j.get("url","") else j.get("url","").split("/")[0]
                    if ".myshopify.com" in host:
                        domains.add("https://" + host)
                except:
                    pass
            print(f"{idx} -> total {len(domains)}")
            if len(domains) >= TARGET:
                break
            time.sleep(2)
        except Exception as e:
            print(e)
    return list(domains)[:TARGET]

def find_email(domain):
    for path in ["/", "/pages/contact-us", "/pages/contact", "/contact"]:
        try:
            r = requests.get(f"{domain}{path}", headers=HEADERS, timeout=15)
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
            clean = [e for e in emails if not any(x in e.lower() for x in ['example', 'wix', 'shopify', 'png', 'jpg', 'sentry', 'cloudflare'])]
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
        shop_url = d
        try:
            r = requests.get(d, headers=HEADERS, timeout=10, allow_redirects=True)
            shop_url = r.url.rstrip("/")
        except:
            pass
        w.writerow([d, shop_url, email])
        print(f"{d} -> {email}")
        time.sleep(0.5)
    print("DONE")
