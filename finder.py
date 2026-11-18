import requests, re, csv, time, json

TARGET = 300
HEADERS = {"User-Agent": "Mozilla/5.0"}

SKINCARE_WORDS = ["skincare", "skin care", "serum", "moisturizer", "cleanser", "face cream", "face wash", "beauty", "cosmetic", "facial", "skin serum", "hydrating", "glow skin", "acne", "vitamin c serum"]

# كلمات بتدل انه متجر مش مدونة
SHOP_WORDS = ["add to cart", "add-to-cart", "checkout", "cart", "shop now", "buy now", "woocommerce", "shopify", "myshopify", "bigcommerce", "magento", "product"]

def clean_host(url):
    try:
        if "://" in url:
            h = url.split("://")[1].split("/")[0].split(":")[0].lower()
        else:
            # surt: com,example,skincare)/...
            host_part = url.split(")")[0]
            parts = host_part.split(",")
            parts.reverse()
            h = ".".join(parts).strip().lower()
        h = h.replace("www.", "")
        # شيل اي دومين غريب
        if "." not in h or len(h) < 4:
            return None
        # استبعد مواقع مش متاجر
        if any(x in h for x in ["facebook", "instagram", "youtube", "amazon", "wikipedia", "pinterest", "google", "twitter"]):
            return None
        return "https://" + h
    except:
        return None

def get_domains():
    domains = set()
    # هندور بالكلمة في الدومين نفسه، مش شوبيفاي بس
    queries = ["*skincare*", "*skin-care*", "*beauty*", "*serum*", "*cosmetic*", "*facial*", "*glow-skin*", "*skincare*"]
    indexes = ["CC-MAIN-2025-30", "CC-MAIN-2025-21", "CC-MAIN-2025-13"]
    for idx in indexes:
        for q in queries:
            for page in range(0, 5):
                url = f"https://index.commoncrawl.org/{idx}-index?url={q}&output=json&filter=status:200&collapse=host&limit=10000&page={page}"
                try:
                    r = requests.get(url, headers=HEADERS, timeout=60)
                    if not r.text.strip():
                        break
                    for line in r.text.splitlines():
                        try:
                            j = json.loads(line)
                            d = clean_host(j.get("url", ""))
                            if d:
                                domains.add(d)
                        except:
                            pass
                    print(f"{idx} {q} page {page} -> total {len(domains)}")
                    if len(domains) >= 5000:
                        return list(domains)
                    time.sleep(0.5)
                except Exception as e:
                    print(e)
                    break
    return list(domains)

def check_site(domain):
    try:
        r = requests.get(domain, headers=HEADERS, timeout=15)
        text = r.text.lower()
        skin = sum(1 for w in SKINCARE_WORDS if w in text)
        is_shop = any(w in text for w in SHOP_WORDS)
        # لازم يكون سكين كير + متجر
        if skin >= 2 and is_shop:
            return True, r.text
        return False, ""
    except:
        return False, ""

def find_email(text, domain):
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    clean = [e for e in emails if not any(x in e.lower() for x in ['example', 'png', 'jpg', 'sentry', 'cloudflare', 'wix.com', 'wordpress.com'])]
    if clean:
        return clean[0]
    for path in ["/contact-us", "/contact", "/pages/contact-us", "/pages/contact"]:
        try:
            r = requests.get(f"{domain}{path}", headers=HEADERS, timeout=12)
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
            clean = [e for e in emails if not any(x in e.lower() for x in ['example', 'png', 'jpg'])]
            if clean:
                return clean[0]
        except:
            pass
    return ""

domains = get_domains()
print(f"Found {len(domains)} candidates, checking...")

count = 0
checked = 0
with open("emails.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["store", "website", "email", "platform"])
    for d in domains:
        if count >= TARGET:
            break
        checked += 1
        ok, text = check_site(d)
        if not ok:
            print(f"SKIP {d}")
            continue
        email = find_email(text, d)
        # اعرف المنصة
        low = text.lower()
        if "myshopify" in low or "shopify" in low:
            platform = "Shopify"
        elif "woocommerce" in low or "wp-content" in low:
            platform = "WooCommerce"
        elif "magento" in low:
            platform = "Magento"
        elif "bigcommerce" in low:
            platform = "BigCommerce"
        else:
            platform = "Other"
        shop_url = d
        try:
            r = requests.get(d, headers=HEADERS, timeout=10, allow_redirects=True)
            shop_url = r.url.rstrip("/")
        except:
            pass
        w.writerow([d, shop_url, email, platform])
        count += 1
        print(f"[{count}/{TARGET}] {platform} {d} -> {email} | checked {checked}")
        time.sleep(0.5)
    print("DONE")
