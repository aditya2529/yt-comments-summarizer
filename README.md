# CommentLens — YouTube Comment Summarizer

Paste any YouTube URL and instantly get an AI-powered summary of the comment section: sentiment, key themes, notable quotes, audience profile, and more.

---

## Setup

### 1. Get API Keys

| Key | Where to get it |
|-----|----------------|
| `YOUTUBE_API_KEY` | [Google Cloud Console](https://console.cloud.google.com/) → Enable **YouTube Data API v3** → Create credential → API Key |
| `ANTHROPIC_API_KEY` | [Anthropic Console](https://console.anthropic.com/) → API Keys |

---

### 2. Backend

```bash
cd backend

# Copy and fill in your keys
cp .env.example .env

# Install dependencies (Python 3.11+)
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000
```

---

### 3. Frontend

```bash
cd frontend

# Install dependencies (Node 18+)
npm install

# Start dev server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## How It Works

1. You paste a YouTube URL
2. The backend extracts the video ID and fetches up to 150 top comments via YouTube Data API v3
3. Claude (claude-sonnet-4-6) analyzes the comments and returns structured insights
4. The frontend renders a beautiful summary card

## Features

- **Sentiment score** — 1–10 scale with a visual meter
- **Key themes** — What topics dominate the conversation
- **Notable quotes** — Standout comments worth reading
- **Audience profile** — Who's watching and engaging
- **Top praises & criticisms** — Quick pros/cons view
- **Fun fact** — A surprising or interesting observation
- **Copy summary** — One click to share as plain text

## Tech Stack

- **Frontend**: React 18, Vite, Tailwind CSS, lucide-react
- **Backend**: Python FastAPI, Anthropic SDK, httpx
- **AI**: Claude Sonnet 4.6
- **Data**: YouTube Data API v3
