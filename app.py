import re
import requests
import streamlit as st
from bs4 import BeautifulSoup

st.set_page_config(page_title="BeautyAI Pricing", layout="centered")

@st.cache_data(ttl=300)
def get_euro_rate():
    url = "https://www.bonbast.com/"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8",
    }

    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()

    text = BeautifulSoup(r.text, "html.parser").get_text(" ", strip=True)
    text = text.replace(",", "")

    match = re.search(r"EUR\s*Euro\s*(\d{4,8})", text)

    if not match:
        raise ValueError("Euro rate not found")

    return int(match.group(1))


st.title("BeautyAI")
st.subheader("محاسبه‌گر قیمت تمام‌شده و قیمت پیشنهادی فروش")

try:
    eur_rate = get_euro_rate()
    st.success(f"نرخ یورو زنده از Bonbast: {eur_rate:,.0f} تومان")
except Exception:
    st.warning("نرخ یورو خودکار دریافت نشد. لطفاً دستی وارد کن.")
    eur_rate = st.number_input("نرخ یورو به تومان", min_value=0, value=105000, step=1000)

product_name = st.text_input("نام محصول", "KIKO 3D Hydra Lip Gloss")

buy_price_eur = st.number_input("قیمت خرید به یورو", min_value=0.0, value=8.5, step=0.1)
commission_percent = st.number_input("کمیسیون خریدار (%)", min_value=0.0, value=10.0, step=0.5)
weight_gram = st.number_input("وزن محصول به گرم", min_value=0.0, value=180.0, step=10.0)
shipping_per_kg_eur = st.number_input("هزینه ارسال به ازای هر کیلوگرم - یورو", min_value=0.0, value=3.0, step=0.5)
profit_percent = st.number_input("سود موردنظر فروشگاه (%)", min_value=0.0, value=35.0, step=1.0)

weight_kg = weight_gram / 1000

commission_cost_eur = buy_price_eur * commission_percent / 100
buy_with_commission_eur = buy_price_eur + commission_cost_eur
shipping_cost_eur = weight_kg * shipping_per_kg_eur

final_cost_eur = buy_with_commission_eur + shipping_cost_eur
final_cost_toman = final_cost_eur * eur_rate

profit_toman = final_cost_toman * profit_percent / 100
suggested_price = final_cost_toman + profit_toman

st.divider()

st.subheader("نتیجه")
st.write(f"محصول: **{product_name}**")

st.metric("نرخ یورو", f"{eur_rate:,.0f} تومان")
st.metric("قیمت خرید با کمیسیون", f"{buy_with_commission_eur:,.2f} €")
st.metric("هزینه ارسال", f"{shipping_cost_eur:,.2f} €")
st.metric("قیمت تمام‌شده تهران - یورو", f"{final_cost_eur:,.2f} €")
st.metric("قیمت تمام‌شده تهران - تومان", f"{final_cost_toman:,.0f} تومان")
st.metric("سود فروشگاه", f"{profit_toman:,.0f} تومان")
st.metric("قیمت پیشنهادی ما", f"{suggested_price:,.0f} تومان")