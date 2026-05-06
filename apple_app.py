"""
CommentLens — Apple-style Streamlit UI
Self-contained. streamlit_app.py is NOT imported (importing it would
re-execute its top-level UI and create duplicate widgets).
Run locally:        streamlit run apple_app.py
Streamlit Cloud:    set Main file path = apple_app.py
"""
import os
import re
import json
import random
from pathlib import Path

import httpx
import streamlit as st
from groq import Groq
from dotenv import load_dotenv, set_key


# ── Engine (logic mirrored from streamlit_app.py — kept independent) ─────────
def extract_video_id(url: str) -> str:
    match = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([a-zA-Z0-9_-]{11})", url)
    if not match:
        st.error("❌ Invalid YouTube URL.")
        st.stop()
    return match.group(1)


def fetch_metadata(video_id: str, api_key: str) -> dict:
    r = httpx.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params={"part": "snippet,statistics", "id": video_id, "key": api_key},
    )
    data = r.json()
    if not data.get("items"):
        st.error("❌ Video not found or is private.")
        st.stop()
    item = data["items"][0]
    s, stats = item["snippet"], item.get("statistics", {})
    return {
        "title": s["title"],
        "channel": s["channelTitle"],
        "thumbnail": s["thumbnails"].get("high", {}).get("url", ""),
        "views": stats.get("viewCount", "N/A"),
        "likes": stats.get("likeCount", "N/A"),
        "comments": stats.get("commentCount", "N/A"),
    }


def fetch_comments(video_id: str, api_key: str, max_n: int) -> list[str]:
    comments, page_token = [], None
    with httpx.Client() as client:
        while len(comments) < max_n:
            params = {
                "part": "snippet", "videoId": video_id, "key": api_key,
                "maxResults": min(100, max_n - len(comments)),
                "order": "relevance", "textFormat": "plainText",
            }
            if page_token:
                params["pageToken"] = page_token
            data = client.get(
                "https://www.googleapis.com/youtube/v3/commentThreads",
                params=params,
            ).json()
            if "error" in data:
                st.error(f"YouTube API error: {data['error'].get('message')}")
                st.stop()
            for item in data.get("items", []):
                txt = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                lks = item["snippet"]["topLevelComment"]["snippet"].get("likeCount", 0)
                comments.append(f"[{lks} likes] {txt}")
            page_token = data.get("nextPageToken")
            if not page_token:
                break
    return comments


def smart_sample(comments: list[str], target: int = 500) -> list[str]:
    if len(comments) <= target:
        return comments

    def get_likes(c):
        try:
            return int(re.search(r"\[(\d+) likes\]", c).group(1))
        except Exception:
            return 0

    sorted_by_likes = sorted(comments, key=get_likes, reverse=True)
    top_count = int(target * 0.6)
    rest_count = target - top_count
    top = sorted_by_likes[:top_count]
    rest = random.sample(
        sorted_by_likes[top_count:],
        min(rest_count, len(sorted_by_likes) - top_count),
    )
    return top + rest


def analyse_with_groq(comments: list[str], title: str, channel: str, api_key: str) -> dict:
    client = Groq(api_key=api_key)
    sampled = smart_sample(comments, target=500)
    comments_text = "\n".join(f"- {c}" for c in sampled)

    prompt = f"""Analyze the YouTube comments below for the video "{title}" by {channel}.

COMMENTS:
{comments_text}

Return ONLY a valid JSON object (no markdown, no code fences) with exactly these fields:
{{
  "overall_sentiment": "positive" | "negative" | "mixed" | "neutral",
  "sentiment_score": <1-10>,
  "one_line_summary": "<punchy one-liner>",
  "key_themes": [
    {{"theme": "...", "description": "...", "frequency": "high"|"medium"|"low"}}
  ],
  "notable_quotes": [
    {{"quote": "...", "reason": "..."}}
  ],
  "audience_profile": "...",
  "top_praises": ["..."],
  "top_criticisms": ["..."],
  "fun_fact": "..."
}}
Include 3-5 key_themes, 2-3 notable_quotes, 2-4 top_praises, 0-3 top_criticisms."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```json\s*|^```\s*|```$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(raw)

# ── Config ────────────────────────────────────────────────────────────────────
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(ENV_PATH)

st.set_page_config(
    page_title="CommentLens — Read between the comments",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"About": "CommentLens — AI-powered YouTube comment summarizer."},
)

# ── Apple-style CSS injection ────────────────────────────────────────────────
APPLE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Hide Streamlit chrome — precise selectors so the sidebar collapse icon keeps working */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
#MainMenu,
footer { display: none !important; }
.stDeployButton { display: none !important; }

/* Restore Material Symbols font for icons that DO need to render (sidebar collapse, etc.) */
.material-symbols-rounded, [class*="material-symbols"] {
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    font-feature-settings: 'liga';
}

/* App background */
.stApp {
    background: #000;
    background-image:
        radial-gradient(at 20% 0%, rgba(255, 69, 58, 0.18) 0px, transparent 50%),
        radial-gradient(at 80% 30%, rgba(120, 50, 200, 0.10) 0px, transparent 50%),
        radial-gradient(at 0% 60%, rgba(255, 69, 58, 0.08) 0px, transparent 50%);
    color: #f5f5f7;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* Main container width */
.block-container {
    max-width: 980px;
    padding-top: 1rem !important;
    padding-bottom: 4rem !important;
}

/* Headings */
h1, h2, h3, h4 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.025em !important;
    color: #f5f5f7 !important;
}

/* Body text */
p, span, div, label {
    font-family: 'Inter', sans-serif !important;
}

/* Inputs */
.stTextInput input, .stTextArea textarea {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 14px !important;
    color: #f5f5f7 !important;
    font-size: 16px !important;
    padding: 14px 18px !important;
    transition: all 0.2s !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: rgba(255, 255, 255, 0.25) !important;
    box-shadow: none !important;
    background: rgba(255, 255, 255, 0.06) !important;
}
.stTextInput label, .stTextArea label {
    color: rgba(255, 255, 255, 0.7) !important;
    font-weight: 500 !important;
    font-size: 13px !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(180deg, #ff5a52 0%, #ff3b30 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 999px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 12px 28px !important;
    box-shadow: 0 8px 24px rgba(255, 69, 58, 0.3), inset 0 1px 0 rgba(255,255,255,0.2) !important;
    transition: all 0.25s !important;
    white-space: nowrap !important;
    overflow: hidden;
    text-overflow: ellipsis;
}
.stButton > button p {
    white-space: nowrap !important;
    margin: 0 !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 12px 28px rgba(255, 69, 58, 0.4), inset 0 1px 0 rgba(255,255,255,0.2) !important;
}
.stButton > button:active { transform: scale(0.97); }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(10, 10, 10, 0.95) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    backdrop-filter: blur(20px);
    padding-top: 1rem;
}
section[data-testid="stSidebar"] * {
    color: #f5f5f7 !important;
}
section[data-testid="stSidebar"] h3 {
    font-size: 1rem !important;
    font-weight: 600 !important;
    margin: 0 0 0.5rem !important;
    letter-spacing: -0.01em !important;
}
section[data-testid="stSidebar"] a {
    color: #ff7a72 !important;
    text-decoration: none;
}
section[data-testid="stSidebar"] a:hover { text-decoration: underline; }

/* Sliders */
.stSlider [data-baseweb="slider"] {
    background: transparent !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 16px 20px;
    backdrop-filter: blur(20px);
}
[data-testid="stMetricLabel"] {
    color: rgba(255, 255, 255, 0.5) !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}
[data-testid="stMetricValue"] {
    color: #f5f5f7 !important;
    font-weight: 700 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.6rem !important;
}

/* Progress bar */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #ff5a52, #ff3b30) !important;
}
.stProgress > div > div > div {
    background: rgba(255, 255, 255, 0.08) !important;
}

/* Info / success / warning / error boxes */
.stAlert {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(20px);
}

/* Expander */
.streamlit-expanderHeader, [data-testid="stExpander"] summary {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    color: #f5f5f7 !important;
}
[data-testid="stExpander"] {
    border: none !important;
    background: transparent !important;
}

/* Divider */
hr {
    border-color: rgba(255, 255, 255, 0.08) !important;
    margin: 2.5rem 0 !important;
}

/* Captions */
.stCaption, [data-testid="stCaptionContainer"] {
    color: rgba(255, 255, 255, 0.5) !important;
}

/* Custom Apple-style classes (used via st.markdown) */
.apple-hero {
    text-align: center;
    padding: 4rem 1rem 1.5rem;
}
@media (max-width: 640px) {
    .apple-hero { padding: 2.5rem 1rem 1rem; }
}
.apple-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 14px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #ff7a72;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    margin-bottom: 2rem;
    backdrop-filter: blur(20px);
}
.apple-display {
    font-size: clamp(2.75rem, 7.5vw, 5rem);
    font-weight: 700;
    line-height: 1.02;
    letter-spacing: -0.045em;
    color: #f5f5f7;
    margin: 0 0 1.5rem;
}
.apple-gradient-text {
    background: linear-gradient(135deg, #ff453a 0%, #ff8a80 50%, #ff453a 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 4s linear infinite;
}
@keyframes shimmer { to { background-position: 200% center; } }
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}
.fade-up { animation: fadeUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) both; }
.fade-up-1 { animation-delay: 0.05s; }
.fade-up-2 { animation-delay: 0.15s; }
.fade-up-3 { animation-delay: 0.25s; }
.fade-up-4 { animation-delay: 0.35s; }

.apple-subtitle {
    color: rgba(255, 255, 255, 0.6);
    font-size: clamp(1.05rem, 2vw, 1.25rem);
    line-height: 1.5;
    max-width: 100%;
    margin: 0 auto 2rem;
    font-weight: 400;
    text-align: center;
}

/* Feature cards strip */
.apple-features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1rem;
    margin: 4rem auto 0;
    max-width: 920px;
}
.apple-feature {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 22px;
    padding: 1.75rem;
    backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
    transition: border-color 0.25s, transform 0.25s;
}
.apple-feature:hover {
    border-color: rgba(255, 255, 255, 0.14);
    transform: translateY(-2px);
}
.apple-feature-glow {
    position: absolute;
    top: -50px; right: -50px;
    width: 140px; height: 140px;
    border-radius: 50%;
    filter: blur(40px);
    opacity: 0.5;
}
.feature-glow-emerald { background: rgba(48, 209, 88, 0.25); }
.feature-glow-red { background: rgba(255, 69, 58, 0.25); }
.feature-glow-amber { background: rgba(255, 214, 10, 0.25); }
.apple-feature-icon {
    font-size: 1.5rem;
    margin-bottom: 0.75rem;
    display: block;
    position: relative;
}
.apple-feature-title {
    color: #f5f5f7;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin: 0 0 0.4rem;
    position: relative;
}
.apple-feature-desc {
    color: rgba(255, 255, 255, 0.55);
    font-size: 13.5px;
    line-height: 1.55;
    margin: 0;
    position: relative;
}

/* Closing CTA section */
.apple-cta-section {
    text-align: center;
    margin: 5rem auto 2rem;
    padding: 0 1rem;
}
.apple-cta-heading {
    font-size: clamp(1.75rem, 4vw, 2.5rem);
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.1;
    color: #f5f5f7;
    margin: 0 0 1rem;
}
.apple-cta-sub {
    color: rgba(255, 255, 255, 0.55);
    font-size: 1.05rem;
    line-height: 1.55;
    max-width: 520px;
    margin: 0 auto;
}
.apple-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 24px;
    padding: 2rem;
    backdrop-filter: blur(20px);
    margin-bottom: 1.25rem;
}
.apple-section-label {
    color: rgba(255, 255, 255, 0.5);
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 1rem;
}
.apple-quote {
    border-left: 2px solid rgba(255, 69, 58, 0.5);
    padding-left: 1rem;
    margin: 1rem 0;
}
.apple-quote-text {
    color: #f5f5f7;
    font-style: italic;
    line-height: 1.5;
}
.apple-quote-reason {
    color: rgba(255, 255, 255, 0.45);
    font-size: 12px;
    margin-top: 0.5rem;
}
.apple-theme-row {
    display: flex;
    gap: 1rem;
    padding: 0.75rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.apple-theme-row:last-child { border-bottom: none; }
.apple-theme-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-top: 8px;
    flex-shrink: 0;
}
.apple-dot-high { background: #ff453a; }
.apple-dot-medium { background: #ffd60a; }
.apple-dot-low { background: #64d2ff; }
.apple-theme-name {
    color: #f5f5f7;
    font-weight: 600;
    font-size: 15px;
}
.apple-theme-desc {
    color: rgba(255, 255, 255, 0.55);
    font-size: 13px;
    margin-top: 4px;
    line-height: 1.5;
}
.sentiment-badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    text-transform: capitalize;
    border: 1px solid;
}
.sent-positive { color: #30d158; background: rgba(48, 209, 88, 0.12); border-color: rgba(48, 209, 88, 0.24); }
.sent-negative { color: #ff453a; background: rgba(255, 69, 58, 0.12); border-color: rgba(255, 69, 58, 0.24); }
.sent-mixed { color: #ffd60a; background: rgba(255, 214, 10, 0.12); border-color: rgba(255, 214, 10, 0.24); }
.sent-neutral { color: #64d2ff; background: rgba(100, 210, 255, 0.12); border-color: rgba(100, 210, 255, 0.24); }

.apple-praise-item {
    display: flex;
    gap: 8px;
    padding: 6px 0;
    color: rgba(255, 255, 255, 0.85);
    font-size: 14px;
    line-height: 1.5;
}
.apple-praise-plus { color: #30d158; font-weight: 700; }
.apple-praise-minus { color: #ff453a; font-weight: 700; }

.apple-video-card {
    position: relative;
    border-radius: 24px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 1.25rem;
}
.apple-video-thumb {
    width: 100%;
    aspect-ratio: 16/9;
    object-fit: cover;
}
.apple-video-overlay {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    padding: 1.5rem;
    background: linear-gradient(to top, rgba(0,0,0,0.85), transparent);
}
.apple-video-title {
    color: #fff;
    font-size: 1.25rem;
    font-weight: 700;
    line-height: 1.2;
    margin: 0 0 4px;
    letter-spacing: -0.02em;
}
.apple-video-channel {
    color: rgba(255, 255, 255, 0.7);
    font-size: 14px;
}

.apple-footer {
    text-align: center;
    color: rgba(255, 255, 255, 0.3);
    font-size: 12px;
    margin-top: 4rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
}
</style>
"""
st.markdown(APPLE_CSS, unsafe_allow_html=True)

# ── Sidebar: API keys ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔑 API Keys")
    st.caption(
        "**YouTube Data API v3** — [free key](https://console.cloud.google.com)  \n"
        "**Groq API** — [free key](https://console.groq.com/keys)"
    )

    # On Streamlit Cloud, prefer st.secrets if present (safe fallback locally)
    def _secret(name: str) -> str:
        try:
            return st.secrets[name]
        except Exception:
            return os.getenv(name, "")

    default_yt = _secret("YOUTUBE_API_KEY")
    default_groq = _secret("GROQ_API_KEY")

    yt_key = st.text_input("YouTube API Key", type="password", value=default_yt, key="apple_yt_key")
    groq_key = st.text_input("Groq API Key", type="password", value=default_groq, key="apple_groq_key")

    if st.button("💾 Save keys locally", use_container_width=True, key="apple_save_keys"):
        ENV_PATH.touch(exist_ok=True)
        set_key(str(ENV_PATH), "YOUTUBE_API_KEY", yt_key)
        set_key(str(ENV_PATH), "GROQ_API_KEY", groq_key)
        st.success("Saved to .env")

    st.markdown("---")
    max_comments = st.slider("Max comments to fetch", 200, 2000, 500, step=100, key="apple_max")

# ── HERO + INPUT (same centered column = same vertical axis) ─────────────────
hero_l, hero_c, hero_r = st.columns([1, 4, 1], gap="small")
with hero_c:
    st.markdown(
        """
        <div class="apple-hero">
            <div class="apple-pill fade-up fade-up-1">⚡ POWERED BY GROQ · LLAMA 3.3 70B</div>
            <h1 class="apple-display fade-up fade-up-2">Read between<br><span class="apple-gradient-text">the comments.</span></h1>
            <p class="apple-subtitle fade-up fade-up-3">
                Paste any YouTube link. Get sentiment, themes, and standout opinions
                from thousands of comments — in seconds.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Input — wrapped in inner narrower columns but centered on SAME axis as hero
    in_l, in_c, in_r = st.columns([1, 4, 1], gap="small")
    with in_c:
        url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
            key="apple_url",
        )
        btn_l, btn_c, btn_r = st.columns([1, 2, 1], gap="small")
        with btn_c:
            go = st.button(
                "✨  Summarize Comments",
                use_container_width=True,
                type="primary",
                key="apple_go",
            )

# ── FEATURE CARDS (only when idle) ───────────────────────────────────────────
if not go:
    st.markdown(
        """
        <div class="apple-features fade-up fade-up-4">
            <div class="apple-feature">
                <div class="apple-feature-glow feature-glow-emerald"></div>
                <span class="apple-feature-icon">👁</span>
                <h3 class="apple-feature-title">See sentiment</h3>
                <p class="apple-feature-desc">Instantly know if viewers loved or hated the video, with a clear 1–10 score.</p>
            </div>
            <div class="apple-feature">
                <div class="apple-feature-glow feature-glow-red"></div>
                <span class="apple-feature-icon">💬</span>
                <h3 class="apple-feature-title">Spot themes</h3>
                <p class="apple-feature-desc">The conversations everyone is having — surfaced and ranked by frequency.</p>
            </div>
            <div class="apple-feature">
                <div class="apple-feature-glow feature-glow-amber"></div>
                <span class="apple-feature-icon">✨</span>
                <h3 class="apple-feature-title">Find the gold</h3>
                <p class="apple-feature-desc">Standout quotes and surprising observations you'd otherwise miss.</p>
            </div>
        </div>

        <div class="apple-cta-section">
            <h2 class="apple-cta-heading">Built for the curious.</h2>
            <p class="apple-cta-sub">
                Whether you're a creator analysing feedback, a researcher,
                or just want to know what people really think — CommentLens has you covered.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── PROCESS ───────────────────────────────────────────────────────────────────
if go:
    if not yt_key or not groq_key:
        st.warning("⚠️ Please enter both API keys in the sidebar.")
        st.stop()
    if not url:
        st.warning("⚠️ Please paste a YouTube URL.")
        st.stop()

    video_id = extract_video_id(url)

    with st.spinner("Fetching video info..."):
        meta = fetch_metadata(video_id, yt_key)

    # Video hero card
    thumb_html = (
        f'<img class="apple-video-thumb" src="{meta["thumbnail"]}" alt="thumbnail"/>'
        if meta["thumbnail"] else ""
    )
    st.markdown(
        f"""
        <a href="https://youtube.com/watch?v={video_id}" target="_blank" style="text-decoration:none;">
        <div class="apple-video-card">
            {thumb_html}
            <div class="apple-video-overlay">
                <div class="apple-video-title">{meta["title"]}</div>
                <div class="apple-video-channel">{meta["channel"]}</div>
            </div>
        </div>
        </a>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("👁 Views", f"{int(meta['views']):,}" if meta["views"] != "N/A" else "N/A")
    m2.metric("👍 Likes", f"{int(meta['likes']):,}" if meta["likes"] != "N/A" else "N/A")
    m3.metric("💬 Comments", f"{int(meta['comments']):,}" if meta["comments"] != "N/A" else "N/A")

    with st.spinner(f"Fetching up to {max_comments} comments..."):
        comments = fetch_comments(video_id, yt_key, max_comments)

    if not comments:
        st.error("No comments found — comments may be disabled.")
        st.stop()

    sample_size = min(500, len(comments))
    st.caption(f"Fetched {len(comments)} comments — analysing {sample_size} with Llama 3.3 70B...")

    with st.spinner("Generating insights..."):
        try:
            result = analyse_with_groq(comments, meta["title"], meta["channel"], groq_key)
        except Exception as e:
            err = str(e)
            if "rate" in err.lower() or "429" in err or "tokens per minute" in err.lower():
                st.error("⚠️ Groq's free-tier rate limit was hit. Please wait ~1 minute and try again, or use a video with fewer comments.")
            elif "context" in err.lower() or "too long" in err.lower():
                st.error("⚠️ This video has too many comments for the AI to process at once. Try lowering the slider.")
            else:
                st.error(f"⚠️ AI request failed: {err}")
            st.stop()

    # ── HEADLINE ──────────────────────────────────────────────────────────────
    sentiment = result.get("overall_sentiment", "neutral")
    score = result.get("sentiment_score", 5)

    st.markdown(
        f"""
        <div class="apple-card">
            <div class="apple-section-label">Summary</div>
            <p style="color:#f5f5f7; font-size:1.25rem; font-weight:500; line-height:1.4; margin:0 0 1.25rem; letter-spacing:-0.02em;">
                {result.get("one_line_summary", "")}
            </p>
            <span class="sentiment-badge sent-{sentiment}">{sentiment}</span>
            <span style="color:rgba(255,255,255,0.4); font-size:12px; margin-left:12px;">
                Score: {score}/10 · Based on {len(comments)} comments
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(score / 10)

    # ── KEY THEMES ────────────────────────────────────────────────────────────
    themes_html = '<div class="apple-card"><div class="apple-section-label">⭐ Key Themes</div>'
    for t in result.get("key_themes", []):
        freq = t.get("frequency", "low")
        themes_html += f"""
        <div class="apple-theme-row">
            <div class="apple-theme-dot apple-dot-{freq}"></div>
            <div style="flex:1;">
                <div class="apple-theme-name">{t.get("theme", "")}</div>
                <div class="apple-theme-desc">{t.get("description", "")}</div>
            </div>
        </div>"""
    themes_html += "</div>"
    st.markdown(themes_html, unsafe_allow_html=True)

    # ── PRAISES & CRITICISMS ──────────────────────────────────────────────────
    praises = result.get("top_praises", [])
    criticisms = result.get("top_criticisms", [])

    pc_l, pc_r = st.columns(2)
    with pc_l:
        praise_html = '<div class="apple-card"><div class="apple-section-label">👏 Praises</div>'
        for p in praises:
            praise_html += f'<div class="apple-praise-item"><span class="apple-praise-plus">+</span><span>{p}</span></div>'
        praise_html += "</div>"
        st.markdown(praise_html, unsafe_allow_html=True)
    with pc_r:
        if criticisms:
            crit_html = '<div class="apple-card"><div class="apple-section-label">⚠️ Criticisms</div>'
            for c in criticisms:
                crit_html += f'<div class="apple-praise-item"><span class="apple-praise-minus">−</span><span>{c}</span></div>'
            crit_html += "</div>"
            st.markdown(crit_html, unsafe_allow_html=True)

    # ── NOTABLE QUOTES ────────────────────────────────────────────────────────
    quotes_html = '<div class="apple-card"><div class="apple-section-label">💬 Notable Quotes</div>'
    for q in result.get("notable_quotes", []):
        quotes_html += f"""
        <div class="apple-quote">
            <div class="apple-quote-text">"{q.get("quote", "")}"</div>
            <div class="apple-quote-reason">{q.get("reason", "")}</div>
        </div>"""
    quotes_html += "</div>"
    st.markdown(quotes_html, unsafe_allow_html=True)

    # ── AUDIENCE + FUN FACT ───────────────────────────────────────────────────
    a_l, a_r = st.columns(2)
    with a_l:
        st.markdown(
            f"""
            <div class="apple-card">
                <div class="apple-section-label">👥 Audience</div>
                <p style="color:rgba(255,255,255,0.85); font-size:14px; line-height:1.6; margin:0;">
                    {result.get("audience_profile", "")}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with a_r:
        st.markdown(
            f"""
            <div class="apple-card">
                <div class="apple-section-label">💡 Fun Fact</div>
                <p style="color:rgba(255,255,255,0.85); font-size:14px; line-height:1.6; margin:0;">
                    {result.get("fun_fact", "")}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="apple-footer">
        CommentLens · Powered by Groq Llama 3.3 70B · YouTube Data API
    </div>
    """,
    unsafe_allow_html=True,
)
