import requests
import streamlit as st

st.set_page_config(page_title="BeautyAI Pricing", layout="centered")

API_URL = "https://bonbast.amirhn.com/latest"


@st.cache_data(ttl=300)
def get_euro_rate():
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()

    data = response.json()

    # معمولاً خروجی شامل کلید EUR یا eur است
    possible_keys = ["EUR", "eur", "euro", "Euro"]

    for key in possible_keys:
        if key in data:
            value = data[key]

            if isinstance(value, dict):
                for sub_key in ["sell", "Sell", "price", "value", "rate"]:
                    if sub_key in value:
                        return int(str(value[sub_key]).replace(",", ""))

            return int(str(value).replace(",", ""))

    raise ValueError("Euro rate not found in API response")


def format_toman(x):
    return f"{x:,.0f} تومان"


def format_euro(x):
    return f"{x:,.2f} €"


st.title("BeautyAI")
st.subheader("محاسبه‌گر قیمت تمام‌شده و قیمت پیشنهادی فروش")

try:
    eur_rate = get_euro_rate()
    st.success(f"نرخ یورو خودکار: {format_toman(eur_rate)}")
except Exception as e:
    st.warning("نرخ یورو خودکار دریافت نشد. نرخ را دستی وارد کن.")
    st.caption(f"خطا: {e}")
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

st.metric("نرخ یورو", format_toman(eur_rate))
st.metric("قیمت خرید با کمیسیون", format_euro(buy_with_commission_eur))
st.metric("هزینه ارسال", format_euro(shipping_cost_eur))
st.metric("قیمت تمام‌شده تهران - یورو", format_euro(final_cost_eur))
st.metric("قیمت تمام‌شده تهران - تومان", format_toman(final_cost_toman))
st.metric("سود فروشگاه", format_toman(profit_toman))
st.metric("قیمت پیشنهادی ما", format_toman(suggested_price))