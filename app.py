import re
import requests
import streamlit as st
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin

st.set_page_config(page_title="BeautyAI", page_icon="💄", layout="centered")

SITES = [
    "https://www.digikala.com/",
    "https://ellicosmetic.ir/",
    "https://saminbeauty.ir/",
    "https://mohanacosmetic.com/",
    "https://pharmaashop.com/",
    "https://nolisse.ir/",
    "https://beauty-lounge.ir/",
    "https://www.ziba-moon.com/",
]

HEADERS = {"User-Agent": "Mozilla/5.0"}

def clean_number(text):
    if text is None:
        return ""
    persian = "۰۱۲۳۴۵۶۷۸۹"
    arabic = "٠١٢٣٤٥٦٧٨٩"
    for i, d in enumerate(persian):
        text = text.replace(d, str(i))
    for i, d in enumerate(arabic):
        text = text.replace(d, str(i))
    return text

def extract_prices(text):
    text = clean_number(text)
    text = text.replace(",", "").replace("٬", "")
    nums = re.findall(r"\d{5,12}", text)

    prices = []
    for n in nums:
        p = int(n)
        if 50_000 <= p <= 50_000_000:
            prices.append(p)
    return prices

def build_search_urls(site, query):
    q = quote_plus(query)

    if "digikala.com" in site:
        return [f"https://www.digikala.com/search/?q={q}"]

    return [
        urljoin(site, f"?s={q}"),
        urljoin(site, f"search?q={q}"),
    ]

def get_market_prices(product_name):
    results = []

    for site in SITES:
        for url in build_search_urls(site, product_name):
            try:
                r = requests.get(url, headers=HEADERS, timeout=10)
                if r.status_code != 200:
                    continue

                soup = BeautifulSoup(r.text, "html.parser")
                text = soup.get_text(" ", strip=True)

                prices = extract_prices(text)

                if prices:
                    results.append({
                        "site": site,
                        "url": url,
                        "price": min(prices)
                    })

            except Exception:
                continue

    return results

def round_price(price):
    return round(price / 10000) * 10000

def toman(x):
    return f"{x:,.0f} تومان"

st.title("💄 BeautyAI")

product_name = st.text_input("نام محصول")

buy = st.number_input("قیمت خرید (€)", min_value=0.0, value=None, placeholder="مثلاً 8.5")
rate = st.number_input("نرخ یورو (تومان)", min_value=0, value=None, placeholder="مثلاً 105000")
commission = st.number_input("کمیسیون (%)", min_value=0.0, value=None, placeholder="مثلاً 10")
weight = st.number_input("وزن (گرم)", min_value=0.0, value=None, placeholder="مثلاً 180")
shipping = st.number_input("هزینه ارسال هر کیلو (€)", min_value=0.0, value=None, placeholder="مثلاً 3")
profit = st.number_input("سود موردنظر (%)", min_value=0.0, value=None, placeholder="مثلاً 35")

if None not in (buy, rate, commission, weight, shipping, profit):
    final_eur = buy * (1 + commission / 100) + (weight / 1000) * shipping
    final_toman = final_eur * rate
    raw_sell_price = final_toman * (1 + profit / 100)
    sell_price = round_price(raw_sell_price)

    st.divider()
    st.metric("قیمت تمام‌شده (€)", f"{final_eur:,.2f}")
    st.metric("قیمت تمام‌شده (تومان)", toman(final_toman))
    st.metric("قیمت پیشنهادی BeautyAI", toman(sell_price))

st.divider()

if st.button("بررسی کف و سقف قیمت بازار"):
    if not product_name:
        st.warning("اول نام محصول را وارد کن.")
    else:
        with st.spinner("در حال بررسی بازار..."):
            prices = get_market_prices(product_name)

        if not prices:
            st.error("قیمتی پیدا نشد. نام محصول را دقیق‌تر وارد کن.")
        else:
            market_prices = [p["price"] for p in prices]

            min_price = min(market_prices)
            max_price = max(market_prices)
            avg_price = sum(market_prices) / len(market_prices)

            st.subheader("قیمت بازار")
            st.metric("کف قیمت بازار", toman(min_price))
            st.metric("میانگین قیمت بازار", toman(avg_price))
            st.metric("سقف قیمت بازار", toman(max_price))

            with st.expander("جزئیات سایت‌ها"):
                for item in prices:
                    st.write(f"{item['site']} — {toman(item['price'])}")
                    st.write(item["url"])