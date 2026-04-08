"""Verify Prices — community thumbs-up/thumbs-down for reported prices."""

import streamlit as st

st.set_page_config(
    page_title="Verify Prices — Cheapest Near Me",
    page_icon="✅",
    layout="centered",
    initial_sidebar_state="expanded",
)

from utils import render_sidebar, init_session

init_session()
render_sidebar()

# ── Mock prices to verify ─────────────────────────────────────────────────────
PENDING = [
    {"id": "v01", "product": "Whole Milk 2L",            "shop": "Lidl, Brixton",          "price": 1.09, "upvotes": 12, "downvotes": 0, "verified": True,  "when": "Today, 09:15"},
    {"id": "v02", "product": "White Bread 800g",          "shop": "Aldi, Stockwell",         "price": 0.75, "upvotes": 8,  "downvotes": 1, "verified": True,  "when": "Today, 08:42"},
    {"id": "v03", "product": "Paracetamol 500mg (16)",    "shop": "Tesco Express, Vauxhall", "price": 0.65, "upvotes": 5,  "downvotes": 0, "verified": False, "when": "Today, 07:30"},
    {"id": "v04", "product": "Chicken Breast 500g",       "shop": "Co-op Food, Kennington",  "price": 4.00, "upvotes": 2,  "downvotes": 3, "verified": False, "when": "Yesterday, 18:10"},
    {"id": "v05", "product": "Orange Juice 1L",           "shop": "Sainsbury's, Waterloo",   "price": 1.35, "upvotes": 3,  "downvotes": 1, "verified": False, "when": "Yesterday, 15:00"},
    {"id": "v06", "product": "Laundry Tablets (20)",      "shop": "Aldi, Stockwell",         "price": 3.89, "upvotes": 6,  "downvotes": 0, "verified": True,  "when": "Yesterday, 12:20"},
    {"id": "v07", "product": "LED Bulb E27 (806lm)",      "shop": "Screwfix, Vauxhall",      "price": 2.49, "upvotes": 1,  "downvotes": 0, "verified": False, "when": "2 days ago"},
    {"id": "v08", "product": "Baked Beans 400g",          "shop": "Iceland Foods, Brixton",  "price": 0.39, "upvotes": 9,  "downvotes": 0, "verified": True,  "when": "2 days ago"},
]


def cast_vote(price_id: str, vote: int):
    """Record vote in session state and attempt Supabase persist."""
    st.session_state.votes[price_id] = vote
    try:
        from database.supabase_client import get_client
        client = get_client()
        client.table("user_reports").insert({
            "price_id": price_id,
            "reporter": st.session_state.session_id,
            "vote":     vote,
        }).execute()
    except Exception:
        pass


# ── Page header ───────────────────────────────────────────────────────────────
st.title("✅ Verify Prices")
st.write(
    "Help your neighbours by checking whether these prices are still correct. "
    "A quick thumbs up or down only takes a second."
)
st.divider()

# ── Filters ───────────────────────────────────────────────────────────────────
f_col, s_col = st.columns(2)
with f_col:
    show = st.selectbox("Show", ["All", "Not yet verified", "Already verified"], key="vp_show")
with s_col:
    sort = st.selectbox("Sort by", ["Newest first", "Most helpful", "Most disputed"], key="vp_sort")

items = list(PENDING)
if show == "Not yet verified":
    items = [x for x in items if not x["verified"]]
elif show == "Already verified":
    items = [x for x in items if x["verified"]]

if sort == "Most helpful":
    items = sorted(items, key=lambda x: x["upvotes"], reverse=True)
elif sort == "Most disputed":
    items = sorted(items, key=lambda x: x["downvotes"], reverse=True)
# "Newest first" keeps original order

st.write(f"**{len(items)} price(s) to check:**")
st.write("")

# ── Price cards ───────────────────────────────────────────────────────────────
for item in items:
    pid = item["id"]
    my_vote = st.session_state.votes.get(pid, 0)

    # Apply session vote to display counts
    up   = item["upvotes"]   + (1 if my_vote ==  1 else 0)
    down = item["downvotes"] + (1 if my_vote == -1 else 0)
    total_votes = up + down
    confidence  = round(up / total_votes * 100) if total_votes else 0

    verified_tag = (
        ' &nbsp;<span style="background:#34a853;color:white;border-radius:20px;'
        'padding:1px 9px;font-size:0.75rem;font-weight:600">Verified</span>'
        if item["verified"] else ""
    )

    border = "2px solid #34a853" if item["verified"] else "1.5px solid #e8eaed"
    bg     = "#f6ffed" if item["verified"] else "#fff"

    with st.container():
        st.markdown(
            f"""
            <div style="border:{border};border-radius:14px;padding:1rem 1.2rem;
                        background:{bg};margin-bottom:0.5rem">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div>
                        <span style="font-size:1.05rem;font-weight:700">{item['product']}</span>
                        {verified_tag}<br>
                        <span style="color:#555;font-size:0.9rem">
                            {item['shop']} &nbsp;·&nbsp; {item['when']}
                        </span>
                    </div>
                    <div style="text-align:right">
                        <span style="font-size:1.5rem;font-weight:800;color:#4285f4">
                            £{item['price']:.2f}
                        </span><br>
                        <span style="font-size:0.8rem;color:#888">
                            {confidence}% say this is correct
                        </span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if my_vote != 0:
            if my_vote == 1:
                st.success("You said this price looks right. Thank you!", icon="👍")
            else:
                st.warning("You said this price may be out of date. Thank you!", icon="👎")
        else:
            v1, v2, v3 = st.columns([2, 2, 5])
            with v1:
                if st.button(
                    f"👍 Looks right ({up})",
                    key=f"up_{pid}",
                    use_container_width=True,
                ):
                    cast_vote(pid, 1)
                    st.rerun()
            with v2:
                if st.button(
                    f"👎 Out of date ({down})",
                    key=f"dn_{pid}",
                    use_container_width=True,
                ):
                    cast_vote(pid, -1)
                    st.rerun()

        st.write("")

# ── Stats footer ──────────────────────────────────────────────────────────────
st.divider()
n_verified   = sum(1 for x in PENDING if x["verified"])
n_unverified = len(PENDING) - n_verified
my_votes     = len(st.session_state.votes)

c1, c2, c3 = st.columns(3)
c1.metric("Verified prices",  n_verified)
c2.metric("Awaiting review",  n_unverified)
c3.metric("Your votes today", my_votes)

st.caption(
    "Prices with 5 or more 'looks right' votes and fewer than 2 disputes "
    "are automatically marked as Verified."
)