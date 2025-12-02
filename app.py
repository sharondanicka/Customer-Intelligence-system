import streamlit as st
import feedparser
import json
from openai import OpenAI

# ----------------- PAGE SETUP -----------------
st.set_page_config(
    page_title="Cisco | Customer Intelligence Prototype",
    layout="wide"
)

st.title("📡 Customer Intelligence – Competitor Signal Scanner")
st.caption("Prototype: Convert market signals into prioritized Cisco actions")

# ----------------- SIDEBAR -----------------
st.sidebar.header("Monitoring Settings")

competitor = st.sidebar.selectbox(
    "Select competitor",
    [
        "Juniper Networks",
        "Arista Networks",
        "Palo Alto Networks",
        "Fortinet",
        "HPE Aruba"
    ]
)

article_limit = st.sidebar.slider("Number of articles", 3, 7, 5)
ATTENTION_THRESHOLD = 70

api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    help="Required for live AI analysis"
)

if not api_key:
    st.warning("Please enter a valid OpenAI API key to continue.")
    st.stop()

client = OpenAI(api_key=api_key)

# ----------------- NEWS FETCH -----------------
def fetch_news(company, limit):
    url = f"https://news.google.com/rss/search?q={company.replace(' ','+')}"
    feed = feedparser.parse(url)

    articles = []
    for entry in feed.entries[:limit]:
        articles.append({
            "title": entry.get("title", ""),
            "summary": entry.get("summary", ""),
            "link": entry.get("link", "")
        })
    return articles

# ----------------- AI ANALYSIS -----------------
def analyze_article_with_llm(client, article, competitor_name):
    system_prompt = (
        "You are a market intelligence analyst at Cisco. "
        "Analyze competitor and market signals and return strict JSON only."
    )

    user_prompt = f"""
Analyze the following competitor news and return STRICT JSON with keys:
- attention_score (0–100)
- signal_type
- summary
- why_it_matters
- next_actions (array of 3 strings)
- confidence (0–1)
- reasoning

Competitor: {competitor_name}
Title: {article['title']}
Summary: {article['summary']}
Link: {article['link']}
""".strip()

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )

        text = response.choices[0].message.content.strip()

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            text = text[start:end + 1]

        return json.loads(text)

    except Exception as e:
        # ✅ DEMO FALLBACK (quota-safe)
        if "quota" in str(e).lower() or "429" in str(e):
            return {
                "attention_score": 82,
                "signal_type": "Competitor Expansion",
                "summary": "Competitor announced a strategic expansion impacting enterprise networking and AI-led infrastructure.",
                "why_it_matters": "This directly overlaps with Cisco’s core switching, security, and data center portfolio.",
                "next_actions": [
                    "Alert account teams covering impacted customers",
                    "Refresh competitive positioning and battlecards",
                    "Proactively engage priority enterprise accounts"
                ],
                "confidence": 0.85,
                "reasoning": "Fallback response used due to temporary AI quota limits."
            }

        st.error(f"OpenAI API error: {e}")
        return None

# ----------------- MAIN ACTION -----------------
if st.button("🔍 Scan Market Signals"):
    articles = fetch_news(competitor, article_limit)

    if not articles:
        st.warning("No recent news found.")
        st.stop()

    st.subheader("🚨 High-Attention Signals")

    for article in articles:
        analysis = analyze_article_with_llm(client, article, competitor)

        if not analysis:
            continue

        if analysis["attention_score"] >= ATTENTION_THRESHOLD:
            with st.contai
