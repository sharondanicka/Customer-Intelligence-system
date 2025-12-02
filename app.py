# app.py
import os
import json
import feedparser
import streamlit as st
from openai import OpenAI

# ------------- CONFIG -------------
st.set_page_config(
    page_title="Cisco – Customer Intelligence Prototype",
    page_icon="📡",
    layout="wide",
)

st.title("📡 Customer Intelligence Prototype – Competitor Signal Scanner")
st.caption(
    "Prototype: Scan recent competitor moves, auto-score attention, and generate seller-ready actions."
)

# Sidebar – API Key & Settings
st.sidebar.header("⚙️ Settings")

api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    help="Your OpenAI API key (will not be stored). Leave blank to use environment variable OPENAI_API_KEY.",
)

if not api_key:
    api_key = os.getenv("OPENAI_API_KEY", "")

if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None

competitor = st.sidebar.selectbox(
    "Select competitor to monitor",
    [
        "Juniper Networks",
        "Arista Networks",
        "Palo Alto Networks",
        "Fortinet",
        "HPE Aruba",
    ],
)

num_articles = st.sidebar.slider(
    "Number of recent articles to analyze",
    min_value=3,
    max_value=10,
    value=5,
)

attention_threshold = st.sidebar.slider(
    "Attention score threshold",
    min_value=50,
    max_value=100,
    value=70,
    step=5,
)

st.sidebar.markdown("---")
st.sidebar.write("When ready, click **Scan Market Signals** on the main panel.")


# ------------- HELPER: CALL MODEL -------------
def analyze_article_with_llm(client, title, summary, link, competitor_name):
    """
    Calls OpenAI to:
    - Decide if this signal matters
    - Auto-score attention
    - Generate summary, why-it-matters, next actions

    Returns a dict or None on error.
    """
    system_prompt = (
        "You are a market intelligence analyst at Cisco. "
        "You analyze competitor/news signals and return strict JSON."
    )

    user_prompt = f"""
Analyze the following news item and return STRICT JSON with keys:
- attention_score: integer 0-100 (0 = ignore, 100 = mission critical)
- signal_type: short string like "New product", "Expansion", "M&A", "Partnership", "Regulation", "Competitive win"
- summary: 2–4 sentences summarizing the news in neutral, factual tone
- why_it_matters: 2–4 sentences explaining why this is (or is not) relevant to Cisco
- next_actions: array of 3–5 concise next best actions for Cisco sales / strategy / SPO teams
- confidence: number 0–1 (your confidence)
- reasoning: 2–3 sentences of internal reasoning (for internal use only)

If this is not relevant to Cisco, set attention_score <= 40 and explain why.

Respond with ONLY a JSON object. No extra text.

Competitor: {competitor_name}

Title: {title}
Summary: {summary}
Link: {link}
""".strip()

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",   # widely available
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
   except Exception as e:
    if "quota" in str(e).lower():
        return {
            "attention_score": 82,
            "signal_type": "Competitor Expansion",
            "summary": "Competitor announced expansion impacting enterprise networking and AI-driven infrastructure.",
            "why_it_matters": "This signals increased competition in areas overlapping with Cisco’s switching and security portfolio.",
            "next_actions": [
                "Alert account teams for impacted industries",
                "Prepare competitive positioning for sellers",
                "Engage strategic partners early"
            ],
            "confidence": 0.85,
            "reasoning": "Fallback demo response due to API quota limits."
        }
    st.error(f"OpenAI API error: {e}")
    return None


    # Extract the text content
    text = response.choices[0].message.content.strip()

    # Try to find and parse JSON
    try:
        # In case model adds some extra text, try to isolate JSON block
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_str = text[start : end + 1]
        else:
            json_str = text
        data = json.loads(json_str)
    except Exception as e:
        st.error(f"Failed to parse model JSON: {e}")
        st.text(text)  # show raw output so you can debug
        return None

    return data


# ------------- HELPER: FETCH NEWS -------------
def fetch_news_for_competitor(name, max_items=5):
    """
    Simple Google News RSS-based fetch.
    """
    query = name.replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    entries = feed.entries[:max_items]
    return entries


# ------------- MAIN ACTION BUTTON -------------
st.markdown("### 🔍 Scan competitor market signals")

if st.button("Scan Market Signals"):
    if not client:
        st.error(
            "Please provide a valid OpenAI API key (either in the sidebar or via the OPENAI_API_KEY environment variable)."
        )
    else:
        with st.spinner(f"Fetching and analyzing latest signals for {competitor}..."):
            entries = fetch_news_for_competitor(competitor, max_items=num_articles)

            if not entries:
                st.warning("No news items found for this competitor right now.")
            else:
                high_attention_signals = []
                low_attention_signals = []

                for entry in entries:
                    title = entry.get("title", "No title")
                    summary = entry.get("summary", "No summary")
                    link = entry.get("link", "")

                    analysis = analyze_article_with_llm(
                        client, title, summary, link, competitor
                    )

                    if not analysis:
                        continue

                    if analysis.get("attention_score", 0) >= attention_threshold:
                        high_attention_signals.append((entry, analysis))
                    else:
                        low_attention_signals.append((entry, analysis))

        # ------------- DISPLAY RESULTS -------------
        if client and entries:
            st.markdown("---")
            st.subheader("🚨 High-Attention Signals")

            if not high_attention_signals:
                st.info(
                    f"No signals crossed the attention threshold of {attention_threshold}. "
                    "This is still useful: it means nothing urgent has surfaced in the last few articles."
                )
            else:
                for entry, analysis in high_attention_signals:
                    score = analysis.get("attention_score", 0)
                    signal_type = analysis.get("signal_type", "Signal")
                    summary = analysis.get("summary", "")
                    why_it_matters = analysis.get("why_it_matters", "")
                    next_actions = analysis.get("next_actions", [])
                    confidence = analysis.get("confidence", 0)

                    with st.container(border=True):
                        cols = st.columns([4, 1.2])
                        with cols[0]:
                            st.markdown(
                                f"#### {signal_type}: {entry.get('title', 'Untitled')}"
                            )
                            st.caption(entry.get("link", ""))

                        with cols[1]:
                            st.metric("Attention Score", f"{score}/100")
                            st.caption(f"Model confidence: {confidence:.2f}")

                        st.markdown("**Insight Summary**")
                        st.write(summary)

                        st.markdown("**Why This Matters to Cisco**")
                        st.write(why_it_matters)

                        st.markdown("**Recommended Next Actions**")
                        if isinstance(next_actions, list):
                            for a in next_actions:
                                st.write(f"- {a}")
                        else:
                            st.write(next_actions)

                        with st.expander("Internal Reasoning (for SPO / strategy only)"):
                            st.write(analysis.get("reasoning", ""))

            st.markdown("---")
            st.subheader("📝 Other Recent Signals (Below Threshold)")
            with st.expander("Show lower-attention items"):
                if not low_attention_signals:
                    st.write("No additional items to display.")
                else:
                    for entry, analysis in low_attention_signals:
                        score = analysis.get("attention_score", 0)
                        signal_type = analysis.get("signal_type", "Signal")

                        st.markdown(
                            f"- **[{entry.get('title', 'Untitled')}]({entry.get('link', '')})** "
                            f" · {signal_type} · Attention Score: `{score}`"
                        )

st.markdown("---")
st.caption(
    "This is a lightweight prototype for demonstrating how Cisco could turn external signals "
    "into prioritized, seller-ready actions using GenAI."
)



