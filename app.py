import re
import requests
import streamlit as st
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="BeautyAI", page_icon="💄", layout="centered")

CURRENCIES = ["یورو", "دلار آمریکا", "دلار کانادا", "پوند", "لیر ترکیه", "درهم امارات"]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def to_number(x):
    if not x:
        return None
    x = str(x)
    x = x.replace(",", "").replace("٬", "").strip()
    return float(x)

def toman(x):
    return f"{x:,.0f} تومان"

def round_price(x, step=10000):
    return round(x / step) * step

def normalize_digits(text):
    fa = "۰۱۲۳۴۵۶۷۸۹"
    ar = "٠١٢٣٤٥٦٧٨٩"
    for i, d in enumerate(fa):
        text = text.replace(d, str(i))
    for i, d in enumerate(ar):
        text = text.replace(d, str(i))
    return text

def extract_prices(text):
    text = normalize_digits(text)
    text = text.replace(",", "").replace("٬", "")
    nums = re.findall(r"\d{5,12}", text)

    prices = []
    for n in nums:
        p = int(n)
        if 50_000 <= p <= 200_000_000:
            prices.append(p)

    return prices

def fetch_prices_from_url(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ", strip=True)
        return extract_prices(text)
    except:
        return []

@st.cache_data(ttl=600)
def get_market_prices(product_name):
    q = quote_plus(product_name)

    urls = {
        "ترب": f"https://torob.com/search/?query={q}",
        "ایمالز": f"https://emalls.ir/Search.aspx?keyword={q}",
    }

    results = []

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(fetch_prices_from_url, url): (name, url)
            for name, url in urls.items()
        }

        for future in futures:
            name, url = futures[future]
            prices = future.result()

            if prices:
                results.append({
                    "source": name,
                    "url": url,
                    "min": min(prices),
                    "max": max(prices),
                    "count": len(prices),
                })

    return results

st.title("💄 BeautyAI")

product = st.text_input("نام محصول")

currency = st.selectbox("نوع ارز", CURRENCIES)

buy = st.text_input("قیمت خرید")
rate = st.text_input(f"نرخ {currency} به تومان")
commission = st.text_input("کمیسیون (%)")
weight = st.text_input("وزن محصول (گرم)")
shipping = st.text_input(f"هزینه ارسال هر کیلو ({currency})")
profit = st.text_input("سود موردنظر (%)")

buy = to_number(buy)
rate = to_number(rate)
commission = to_number(commission)
weight = to_number(weight)
shipping = to_number(shipping)
profit = to_number(profit)

if all(v is not None for v in [buy, rate, commission, weight, shipping, profit]):
    cost_currency = buy * (1 + commission / 100) + (weight / 1000) * shipping
    cost_toman = cost_currency * rate
    suggested = round_price(cost_toman * (1 + profit / 100))

    st.divider()
    st.metric(f"قیمت تمام‌شده ({currency})", f"{cost_currency:,.2f}")
    st.metric("قیمت تمام‌شده (تومان)", toman(cost_toman))
    st.metric("قیمت پیشنهادی BeautyAI", toman(suggested))

st.divider()

if st.button("بررسی کف و سقف بازار"):
    if not product:
        st.warning("نام محصول را وارد کن.")
    else:
        with st.spinner("در حال بررسی ترب و ایمالز..."):
            data = get_market_prices(product)

        if not data:
            st.error("قیمتی پیدا نشد. اسم محصول را دقیق‌تر وارد کن.")
        else:
            all_mins = [x["min"] for x in data]
            all_maxs = [x["max"] for x in data]

            st.subheader("قیمت بازار")
            st.metric("کف قیمت بازار", toman(min(all_mins)))
            st.metric("سقف قیمت بازار", toman(max(all_maxs)))

            with st.expander("جزئیات"):
                for item in data:
                    st.write(f"**{item['source']}**")
                    st.write("کف:", toman(item["min"]))
                    st.write("سقف:", toman(item["max"]))
                    st.write("لینک:", item["url"])