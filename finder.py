import requests, re, csv, time, json

TARGET = 1000
HEADERS = {"User-Agent": "Mozilla/5.0"}

def parse_surt(surt):
    # com,myshopify,xxx)/ -> xxx.myshopify.com
    try:
        host_part = surt.split(")")[0]
        parts = host_part.split(",")
        parts.reverse()
        host = ".".join(parts)
        if ".myshopify.com" in host:
            return "https://" + host
    except:
        pass
    return None

def get_domains():
    domains = set()
    indexes = ["CC-MAIN-2025-30", "CC-MAIN-2025-21", "CC-MAIN-2025-13", "CC-MAIN-2025-08"]
    for idx in indexes:
        for page in range(0, 20):
            url = f"https://index.commoncrawl.org/{idx}-index?url=*.myshopify.com/*&output=json&filter=status:200&collapse=urlkey&limit=10000&page={page}"
            try:
                r = requests.get(url, headers=HEADERS, timeout=60)
                if not r.text.strip():
                    break
                for line in r.text.splitlines():
                    try:
                        j = json.loads(line)
                        surt = j.get("url", "")
                        d = parse_surt(surt)
                        if d:
                            domains.add(d)
                        # لو رجع url عادي مش surt
                        elif ".myshopify.com" in surt:
                            m = re.search(r'([a-z0-9\-]+\.myshopify\.com)', surt)
                            if m:
                                domains.add("https://" + m.group(1))
                    except:
                        pass
                print(f"{idx} page {page} -> total {len(domains)}")
                if len(domains) >= TARGET:
                    return list(domains)[:TARGET]
                time.sleep(1)
            except Exception as e:
                print(e)
                break
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
