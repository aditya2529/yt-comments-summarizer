import os
import re
import json
import httpx
import streamlit as st
from groq import Groq
from pathlib import Path
from dotenv import load_dotenv, set_key

# ── Load saved keys from .env ─────────────────────────────────────────────────
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(ENV_PATH)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="YouTube Comments Summarizer",
    page_icon="🎬",
    layout="centered",
)

st.title("🎬 YouTube Comments Summarizer")
st.caption("Paste a YouTube URL and get AI-powered insights from the comments — free!")

# ── Sidebar: API keys ─────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔑 API Keys")
    st.markdown(
        "**YouTube Data API v3** — [get one free](https://console.cloud.google.com)\n\n"
        "**Groq API** — [get one free](https://console.groq.com/keys) (sign up with personal Gmail)"
    )
    yt_key = st.text_input("YouTube API Key", type="password",
                           value=os.getenv("YOUTUBE_API_KEY", ""))
    groq_key = st.text_input("Groq API Key", type="password",
                              value=os.getenv("GROQ_API_KEY", ""))

    if st.button("💾 Save keys", use_container_width=True):
        ENV_PATH.touch(exist_ok=True)
        set_key(str(ENV_PATH), "YOUTUBE_API_KEY", yt_key)
        set_key(str(ENV_PATH), "GROQ_API_KEY", groq_key)
        st.success("Keys saved! They'll load automatically next time.")

    st.divider()
    max_comments = st.slider("Max comments to fetch", 200, 3000, 1000, step=100)
    st.caption(f"Up to {min(1500, max_comments)} sent to AI for analysis.")

# ── Helpers ───────────────────────────────────────────────────────────────────
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
    """Pick the most representative comments:
    - Top 60% by like count (most engaged)
    - Random 40% from the rest (diversity)
    """
    import random
    if len(comments) <= target:
        return comments

    def get_likes(c):
        try:
            return int(re.search(r"\[(\d+) likes\]", c).group(1))
        except:
            return 0

    sorted_by_likes = sorted(comments, key=get_likes, reverse=True)
    top_count = int(target * 0.6)
    rest_count = target - top_count
    top = sorted_by_likes[:top_count]
    rest = random.sample(sorted_by_likes[top_count:], min(rest_count, len(sorted_by_likes) - top_count))
    return top + rest


def analyse_with_groq(comments: list[str], title: str, channel: str, api_key: str) -> dict:
    client = Groq(api_key=api_key)
    # Llama 3.3 70B on Groq has a 128k token context window. Cap at 1500
    # comments (~60-80k tokens) to leave room for prompt + response and
    # avoid context-overflow errors. If user fetched fewer, use them all.
    target = min(1500, len(comments))
    sampled = smart_sample(comments, target=target)
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
        model="llama-3.3-70b-versatile",  # free model on Groq
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    raw = response.choices[0].message.content.strip()
    # Strip markdown fences if present
    raw = re.sub(r"^```json\s*|^```\s*|```$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(raw)


# ── Main UI ───────────────────────────────────────────────────────────────────
url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")

if st.button("✨ Summarise Comments", type="primary", use_container_width=True):
    if not yt_key or not groq_key:
        st.warning("⚠️ Please enter both API keys in the sidebar.")
        st.stop()
    if not url:
        st.warning("⚠️ Please enter a YouTube URL.")
        st.stop()

    video_id = extract_video_id(url)

    with st.spinner("Fetching video info..."):
        meta = fetch_metadata(video_id, yt_key)

    # Video card
    col1, col2 = st.columns([1, 2])
    with col1:
        if meta["thumbnail"]:
            st.image(meta["thumbnail"], use_container_width=True)
    with col2:
        st.subheader(meta["title"])
        st.caption(f"**{meta['channel']}**")
        m1, m2, m3 = st.columns(3)
        m1.metric("👁 Views", f"{int(meta['views']):,}" if meta["views"] != "N/A" else "N/A")
        m2.metric("👍 Likes", f"{int(meta['likes']):,}" if meta["likes"] != "N/A" else "N/A")
        m3.metric("💬 Comments", f"{int(meta['comments']):,}" if meta["comments"] != "N/A" else "N/A")

    with st.spinner(f"Fetching up to {max_comments} comments..."):
        comments = fetch_comments(video_id, yt_key, max_comments)

    if not comments:
        st.error("No comments found — comments may be disabled.")
        st.stop()

    sample_size = min(1500, len(comments))
    st.info(f"Fetched **{len(comments)}** comments — analysing a smart sample of **{sample_size}** with Groq (Llama 3.3 70B)...")

    with st.spinner("Generating insights..."):
        result = analyse_with_groq(comments, meta["title"], meta["channel"], groq_key)

    st.success("Done!")
    st.divider()

    # ── Results ───────────────────────────────────────────────────────────────
    sentiment_emoji = {"positive": "😊", "negative": "😠", "mixed": "😐", "neutral": "😶"}.get(
        result.get("overall_sentiment", "neutral"), "😶"
    )
    score = result.get("sentiment_score", 5)

    st.subheader("📊 Overview")
    c1, c2 = st.columns([1, 3])
    c1.metric(f"{sentiment_emoji} Sentiment", result.get("overall_sentiment", "").title())
    c2.progress(score / 10, text=f"Sentiment score: {score}/10")
    st.info(f"**💡 {result.get('one_line_summary', '')}**")

    st.subheader("🎯 Key Themes")
    for t in result.get("key_themes", []):
        freq_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(t.get("frequency", "low"), "⚪")
        with st.expander(f"{freq_color} {t.get('theme', '')}"):
            st.write(t.get("description", ""))

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("👏 Top Praises")
        for p in result.get("top_praises", []):
            st.markdown(f"- {p}")
    with col_b:
        st.subheader("⚠️ Top Criticisms")
        crits = result.get("top_criticisms", [])
        if crits:
            for c in crits:
                st.markdown(f"- {c}")
        else:
            st.write("None found!")

    st.subheader("💬 Notable Quotes")
    for q in result.get("notable_quotes", []):
        st.markdown(f"> *\"{q.get('quote', '')}\"*")
        st.caption(f"Why notable: {q.get('reason', '')}")

    st.subheader("👥 Audience Profile")
    st.write(result.get("audience_profile", ""))

    st.subheader("🎉 Fun Fact")
    st.success(result.get("fun_fact", ""))
