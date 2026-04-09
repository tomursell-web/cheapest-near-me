"""Cheapest Near Me — Google-style home page with AI-powered search."""

import streamlit as st

st.set_page_config(
    page_title="Cheapest Near Me",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="expanded",
)

from utils import (
    render_sidebar,
    init_session,
    ai_interpret_search,
    db_search_products,
    db_get_price_rows,
    distance_words,
)
from database.mock_data import (
    CATEGORY_ICONS,
    CATEGORIES,
    products_by_category,
)

init_session()

st.markdown("""
<style>
.block-container { padding-top: 3rem !important; max-width: 780px; }
.hero { text-align: center; padding: 3rem 1rem 1.5rem; }
.hero-title {
    font-size: 3rem;
    font-weight: 900;
    letter-spacing: -1px;
    color: #1a1a2e;
    margin: 0;
}
.hero-sub {
    font-size: 1.15rem;
    color: #666;
    margin-top: 0.4rem;
}
.compact-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: #1a1a2e;
    margin: 0;
    white-space: nowrap;
}
.stTextInput > div > div > input {
    font-size: 1.1rem !important;
    border-radius: 28px !important;
    border: 2px solid #dfe1e5 !important;
    padding: 0.75rem 1.4rem !important;
    box-shadow: none !important;
}
.stTextInput > div > div > input:focus {
    border-color: #4285f4 !important;
    box-shadow: 0 1px 8px rgba(66,133,244,.25) !important;
}
div[data-testid="column"] .stButton > button {
    border-radius: 14px;
    border: 2px solid #e8eaed;
    background: #fff;
    font-size: 0.95rem;
    padding: 0.65rem 0.5rem;
    width: 100%;
}
div[data-testid="column"] .stButton > button:hover {
    border-color: #4285f4;
    box-shadow: 0 2px 8px rgba(66,133,244,.18);
}
.result-card {
    border-radius: 14px;
    border: 1.5px solid #e8eaed;
    padding: 1rem 1.2rem 0.8rem;
    margin-bottom: 0.7rem;
    background: #fff;
}
.result-card-best { border-color: #34a853; background: #f6ffed; }
.price-main { font-size: 1.55rem; font-weight: 800; color: #34a853; }
.price-other { font-size: 1.55rem; font-weight: 800; color: #4285f4; }
.best-pill {
    display: inline-block;
    background: #34a853;
    color: white;
    border-radius: 20px;
    padding: 2px 11px;
    font-size: 0.78rem;
    font-weight: 600;
    vertical-align: middle;
    margin-left: 8px;
}
.shop-name { font-size: 1.1rem; font-weight: 700; color: #1a1a2e; }
.shop-detail { color: #666; font-size: 0.9rem; margin-top: 2px; }
.friendly-msg {
    background: #e8f0fe;
    border-radius: 10px;
    padding: 0.6rem 1rem;
    color: #174ea6;
    font-size: 1rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

render_sidebar()

has_query = bool(st.session_state.search_query)

if not has_query:
    st.markdown("""
    <div class="hero">
        <p class="hero-title">🛒 Cheapest Near Me</p>
        <p class="hero-sub">Find the best price near you</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(
        '<p class="compact-title">🛒 Cheapest Near Me</p>',
        unsafe_allow_html=True,
    )

col_input, col_btn = st.columns([5, 1])
with col_input:
    query = st.text_input(
        "Search",
        value=st.session_state.search_query,
        placeholder="What are you looking for?  e.g. milk, Calpol, WD40...",
        label_visibility="collapsed",
        key="main_search_input",
    )
with col_btn:
    search_clicked = st.button("Search", type="primary", use_container_width=True)

if search_clicked or (query != st.session_state.search_query and query):
    st.session_state.search_query = query
    st.session_state.search_result = None
    st.rerun()

if not query and st.session_state.search_query:
    st.session_state.search_query = ""
    st.session_state.search_result = None
    st.rerun()

if not has_query:
    st.write("")
    st.markdown("**Browse by category:**")
    cats_per_row = 4
    for row_start in range(0, len(CATEGORIES), cats_per_row):
        row_cats = CATEGORIES[row_start:row_start + cats_per_row]
        cols = st.columns(4)
        for i, cat in enumerate(row_cats):
            icon = CATEGORY_ICONS.get(cat, "")
            with cols[i]:
                if st.button(f"{icon} {cat.title()}", key=f"cat_{cat}", use_container_width=True):
                    st.session_state.search_query = cat
                    st.session_state.search_result = {
                        "search_terms": [cat],
                        "category": cat,
                        "friendly_message": f"Browsing {cat.lower()} near you...",
                    }
                    st.rerun()

    st.divider()
    st.markdown("### How it works")
    c1, c2, c3 = st.columns(3)
    c1.info("**1. Search** for what you need, or pick a category")
    c2.info("**2. See prices** at shops near you, cheapest first")
    c3.info("**3. Save to basket** to plan your whole shopping trip")
    st.stop()

if st.session_state.search_result is None:
    with st.spinner("Just a moment..."):
        st.session_state.search_result = ai_interpret_search(st.session_state.search_query)

interpretation = st.session_state.search_result

st.markdown(
    f'<div class="friendly-msg">🔍 {interpretation["friendly_message"]}</div>',
    unsafe_allow_html=True,
)

products = db_search_products(
    interpretation["search_terms"],
    interpretation.get("category"),
)

if not products and interpretation.get("category"):
    products = db_search_products(interpretation["search_terms"], None)

if not products and interpretation.get("category"):
    products = products_by_category(interpretation["category"])

if not products:
    st.markdown("### Nothing found nearby")
    st.write(
        "We couldn't find that item in our database. "
        "You can **submit a price** using the page in the sidebar — "
        "it only takes 30 seconds!"
    )
    st.stop()

st.markdown(f"### Found {len(products)} item{'s' if len(products) != 1 else ''}")

for prod in products:
    rows = db_get_price_rows(prod["id"])
    in_basket = any(x["id"] == prod["id"] for x in st.session_state.basket)

    with st.container():
        h_col, b_col = st.columns([5, 2])
        with h_col:
            st.markdown(
                f"**{prod['name']}** &nbsp; "
                f"<span style='color:#888;font-size:0.85rem'>{prod.get('unit','')}</span>",
                unsafe_allow_html=True,
            )
        with b_col:
            if in_basket:
                st.success("In basket")
            else:
                if st.button("+ Basket", key=f"add_{prod['id']}", use_container_width=True):
                    st.session_state.basket.append(prod)
                    st.rerun()

        if not rows:
            st.caption("No prices reported yet — be the first to submit one!")
            st.divider()
            continue

        for i, r in enumerate(rows):
            is_best = i == 0
            card_class = "result-card result-card-best" if is_best else "result-card"
            price_class = "price-main" if is_best else "price-other"
            best_html = '<span class="best-pill">Cheapest</span>' if is_best else ""
            saving = round(r["price"] - rows[0]["price"], 2)
            saving_html = (
                "" if is_best
                else f'<span style="color:#888;font-size:0.9rem"> (+£{saving:.2f} more)</span>'
            )

            st.markdown(f"""
            <div class="{card_class}">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div>
                        <span class="shop-name">{r['shop']}</span>{best_html}<br>
                        <span class="shop-detail">{r['address']} &nbsp;·&nbsp; {distance_words(r['distance'])}</span>
                    </div>
                    <div style="text-align:right">
                        <span class="{price_class}">£{r['price']:.2f}</span>{saving_html}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
