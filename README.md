# Cisco – Customer Intelligence Prototype (Competitor Signal Scanner)

This is a lightweight **Customer Intelligence System (CIS) prototype** that:
- Fetches recent public news about key competitors
- Uses GenAI to **auto-score attention** (0–100)
- Generates **seller-ready insights** with:
  - Summary
  - Why this matters to Cisco
  - Recommended next best actions

---

## 🧱 Features

- Competitor selection (Juniper, Arista, Palo Alto, Fortinet, HPE Aruba)
- Live news fetch via Google News RSS
- Auto-generated:
  - Attention Score (0–100)
  - Signal type (e.g., Expansion, M&A, New product)
  - Insight summary
  - “Why this matters to Cisco”
  - Next best actions
- Split view:
  - 🚨 High-attention signals (above threshold)
  - 📝 Other recent signals (below threshold)

---

## 🛠️ Tech Stack

- **Frontend / UI**: Streamlit
- **News Fetching**: Google News RSS via `feedparser`
- **AI / GenAI**: OpenAI Responses API (`gpt-4.1-mini`)

---

## ⚙️ Setup

1. **Clone the repo**

```bash
git clone https://github.com/<your-org>/cisco-cis-competitor-prototype.git
cd cisco-cis-competitor-prototype
