import os
import re
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
import httpx
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="YouTube Comments Summarizer API")

FRONTEND_ORIGINS = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_origins=[o.strip() for o in FRONTEND_ORIGINS if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


class SummarizeRequest(BaseModel):
    url: str
    max_comments: Optional[int] = 200


def extract_video_id(url: str) -> str:
    patterns = [
        r"(?:v=|youtu\.be/|embed/|shorts/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise HTTPException(status_code=400, detail="Invalid YouTube URL. Please provide a valid YouTube video link.")


async def fetch_video_metadata(video_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "snippet,statistics",
                "id": video_id,
                "key": YOUTUBE_API_KEY,
            },
        )
        data = resp.json()
        if not data.get("items"):
            raise HTTPException(status_code=404, detail="Video not found or is private.")
        item = data["items"][0]
        snippet = item["snippet"]
        stats = item.get("statistics", {})
        return {
            "title": snippet["title"],
            "channel": snippet["channelTitle"],
            "thumbnail": snippet["thumbnails"].get("high", {}).get("url", ""),
            "view_count": stats.get("viewCount", "N/A"),
            "like_count": stats.get("likeCount", "N/A"),
            "comment_count": stats.get("commentCount", "N/A"),
        }


async def fetch_comments(video_id: str, max_comments: int) -> list[str]:
    comments = []
    page_token = None

    async with httpx.AsyncClient() as client:
        while len(comments) < max_comments:
            params = {
                "part": "snippet",
                "videoId": video_id,
                "key": YOUTUBE_API_KEY,
                "maxResults": min(100, max_comments - len(comments)),
                "order": "relevance",
                "textFormat": "plainText",
            }
            if page_token:
                params["pageToken"] = page_token

            resp = await client.get(
                "https://www.googleapis.com/youtube/v3/commentThreads",
                params=params,
            )
            data = resp.json()

            if "error" in data:
                err = data["error"].get("message", "YouTube API error")
                raise HTTPException(status_code=502, detail=f"YouTube API: {err}")

            for item in data.get("items", []):
                text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                likes = item["snippet"]["topLevelComment"]["snippet"].get("likeCount", 0)
                comments.append(f"[{likes} likes] {text}")

            page_token = data.get("nextPageToken")
            if not page_token or not data.get("items"):
                break

    return comments


def summarize_with_claude(comments: list[str], video_title: str, channel: str) -> dict:
    comments_text = "\n".join(f"- {c}" for c in comments[:200])

    system_prompt = """You are an expert at analyzing YouTube comment sections and extracting meaningful insights.
Your summaries are clear, engaging, and genuinely useful. You identify patterns, sentiments, and notable perspectives.
Always respond with valid JSON only — no markdown fences, no extra text."""

    user_prompt = f"""Analyze the YouTube comments below for the video "{video_title}" by {channel}.

COMMENTS:
{comments_text}

Return a JSON object with exactly these fields:
{{
  "overall_sentiment": "positive" | "negative" | "mixed" | "neutral",
  "sentiment_score": <number 1-10, where 1=very negative, 10=very positive>,
  "one_line_summary": "<single punchy sentence capturing the essence of the comment section>",
  "key_themes": [
    {{"theme": "<theme name>", "description": "<1-2 sentence explanation>", "frequency": "high" | "medium" | "low"}}
  ],
  "notable_quotes": [
    {{"quote": "<exact or paraphrased comment>", "reason": "<why it stands out>"}}
  ],
  "audience_profile": "<2-3 sentences describing who is watching and engaging>",
  "top_praises": ["<what viewers loved>"],
  "top_criticisms": ["<what viewers criticized, empty array if none>"],
  "fun_fact": "<an interesting or surprising observation from the comments>"
}}

Include 3-5 key_themes, 2-3 notable_quotes, 2-4 top_praises, and 0-3 top_criticisms."""

    message = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    import json
    raw = message.content[0].text.strip()
    return json.loads(raw)


@app.post("/summarize")
async def summarize(req: SummarizeRequest):
    if not YOUTUBE_API_KEY:
        raise HTTPException(status_code=500, detail="YouTube API key not configured.")
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="Anthropic API key not configured.")

    video_id = extract_video_id(req.url)
    metadata, comments = await __import__("asyncio").gather(
        fetch_video_metadata(video_id),
        fetch_comments(video_id, req.max_comments),
    )

    if not comments:
        raise HTTPException(status_code=404, detail="No comments found. Comments may be disabled for this video.")

    summary = summarize_with_claude(comments, metadata["title"], metadata["channel"])

    return {
        "video_id": video_id,
        "metadata": metadata,
        "comments_analyzed": len(comments),
        "summary": summary,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
