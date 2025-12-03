import streamlit as st
import feedparser
import random

# ---------------- PAGE SETUP ----------------
st.set_page_config(
    page_title="Cisco | Customer Intelligence Prototype",
    layout="wide"
)

st.title("📡 Customer Intelligence – Signal Prioritization Console")
st.caption(
    "Prototype: Identify, prioritize, and act on market signals using a structured Impact × Urgency framework"
)

# ---------------- SIDEBAR ----------------
st.sidebar.header("Monitoring Controls")

competitor = st.sidebar.selectbox(
    "Monitor competitor",
    [
        "Juniper Networks",
        "Arista Networks",
        "Palo Alto Networks",
        "Fortinet",
        "HPE Aruba"
    ]
)

article_limit = st.sidebar.slider(
    "Number of signals to scan",
    3, 6, 4
)

ATTENTION_THRESHOLD = 70

# ---------------- METRIC EXPLANATION (UI) ----------------
with st.expander("ℹ️ How we determine importance (Attention Score)"):
    st.markdown(
        """
### 🔎 Signal Prioritization Methodology

Each market signal is evaluated using an **Impact × Urgency framework** to ensure sellers
focus only on items that require a decision.

**Impact** answers:
- *If this is true, how much does it affect Cisco’s business?*
- Portfolio overlap, competitive displacement risk, customer relevance

**Urgency** answers:
- *How quickly does Cisco need to act?*
- Time sensitivity, deal cycle impact, competitive momentum

### 🎯 Attention Score
The **Attention Score (0–100)** combines Impact and Urgency:
- **80–100** → Immediate seller action required
- **65–79** → Strategic monitoring and planning
- **<65** → Informational or low priority

This ensures intelligence is **actionable**, not just informative.
"""
    )

# ---------------- DEMO ANALYSIS ENGINE ----------------
def generate_demo_analysis():
    impact = random.choice(["High", "Medium", "Low"])
    urgency = random.choice(["High", "Medium", "Low"])

    score_map = {
        ("High", "High"): random.randint(85, 95),
        ("High", "Medium"): random.randint(75, 85),
        ("Medium", "High"): random.randint(70, 80),
        ("Medium", "Medium"): random.randint(60, 70),
    }

    attention_score = score_map.get((impact, urgency), random.randint(45, 60))

    return {
        "impact": impact,
        "urgency": urgency,
        "attention_score": attention_score,
        "what_changed": [
            "Competitor expanded focus from selective wins to enterprise-scale deals",
            "Go-to-market messaging shifted toward platform-led positioning",
        ],
        "why_it_matters": [
            "Direct overlap with Cisco’s installed base in core enterprise accounts",
            "Potential increase in competitive pressure over the next 1–2 quarters",
        ],
        "recommended_actions": [
            "Identify top at-risk accounts within the seller portfolio",
            "Equip sellers with refreshed competitive positioning",
            "Engage partners for proactive customer outreach",
        ],
    }

# ---------------- NEWS FETCH ----------------
def fetch_news(company, limit):
    url = f"https://news.google.com/rss/search?q={company.replace(' ', '+')}"
    feed = feedparser.parse(url)

    titles = []
    for entry in feed.entries[:limit]:
        titles.append(entry.get("title", ""))
    return titles

# ---------------- MAIN ACTION ----------------
st.markdown("### 🚨 Prioritized Market Signals")

if st.button("Scan Market Signals"):
    articles = fetch_news(competitor, article_limit)

    if not articles:
        st.warning("No recent market signals found.")
    else:
        for idx, title in enumerate(articles):
            analysis = generate_demo_analysis()

            if analysis["attention_score"] >= ATTENTION_THRESHOLD:
                with st.container(border=True):
                    header_cols = st.columns([4, 1])

                    with header_cols[0]:
                        st.subheader(title)

                    with header_cols[1]:
                        st.metric(
                            "Attention Score",
                            analysis["attention_score"],
                            help="Represents combined Impact and Urgency on a 0–100 scale"
                        )

                    # ✅ IMPACT × URGENCY BADGE WITH TOOLTIP
                    st.markdown(
                        f"""
**Priority Classification**  
🧭 Impact: **{analysis['impact']}** &nbsp;&nbsp;|&nbsp;&nbsp; ⏱️ Urgency: **{analysis['urgency']}**
""",
                        help=(
                            "Impact estimates potential business effect on Cisco. "
                            "Urgency reflects how quickly sellers should act."
                        ),
                    )

                    st.markdown("### 🔍 What Changed (Beyond the Headline)")
                    for w in analysis["what_changed"]:
                        st.write("•", w)

                    st.markdown("### ❗ Why This Matters to You")
                    for m in analysis["why_it_matters"]:
                        st.write("•", m)

                    st.markdown("### ✅ Recommended Actions (Near-Term)")
                    for a in analysis["recommended_actions"]:
                        st.write("•", a)

                    st.markdown("---")
                    st.markdown("### 👤 Seller Feedback")

                    fb_cols = st.columns(3)
                    with fb_cols[0]:
                        st.button("📌 Create Opportunity", key=f"opp_{idx}")

                    with fb_cols[1]:
                        st.button("⭐ Mark as Interesting", key=f"int_{idx}")

                    with fb_cols[2]:
                        st.button("❌ Not Relevant", key=f"nr_{idx}")

st.caption(
    "Demo prototype – showcases structured prioritization, seller interaction, and explainable metrics"
)
