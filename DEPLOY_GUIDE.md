# Deploy CommentLens to the Cloud (Mobile-Friendly)

After deployment, you'll get a URL like `https://commentlens.vercel.app` that works on any phone, tablet, or computer — no laptop required to keep it running. Total time: ~25 minutes. Total cost: **$0** (plus AI usage at ~$0.01/summary).

---

## What you need before starting
- A GitHub account → [github.com/signup](https://github.com/signup) (free)
- Your two API keys (`YOUTUBE_API_KEY` and `ANTHROPIC_API_KEY`)
- About 25 minutes

---

## Part 1 — Push code to GitHub (5 min)

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `commentlens`
3. Set to **Private** (so your code stays yours)
4. Click **Create repository**
5. On the next page, click **uploading an existing file**
6. Open File Explorer → drag the **entire** `Youtube Comments Summarizer` folder contents into the GitHub upload area
7. Scroll down → click **Commit changes**

> The `.gitignore` file makes sure your `.env` (with API keys) is **never** uploaded.

---

## Part 2 — Deploy backend to Render (10 min)

The backend is the brain — it talks to YouTube and Claude.

1. Go to [render.com](https://render.com) → **Sign up with GitHub** (free)
2. Authorize Render to access your repos
3. Click **New +** (top right) → **Blueprint**
4. Pick your `commentlens` repository → click **Connect**
5. Render auto-detects the `render.yaml` file. Click **Apply**.
6. It will ask for **3 environment variables** — fill them in:

   | Variable | Value |
   |----------|-------|
   | `YOUTUBE_API_KEY` | Your YouTube key |
   | `ANTHROPIC_API_KEY` | Your Anthropic key |
   | `FRONTEND_ORIGINS` | Leave blank for now (we fill this after Vercel) |

7. Click **Apply** / **Deploy**
8. Wait ~3–5 minutes. When done, you'll see a URL like:
   ```
   https://commentlens-api.onrender.com
   ```
9. **Copy this URL** — you'll paste it into Vercel next.

> ⚠️ Render's free tier sleeps after 15 min of no use. First request after sleeping takes ~30 seconds to wake up. Subsequent requests are instant.

---

## Part 3 — Deploy frontend to Vercel (5 min)

The frontend is what your friend sees and clicks.

1. Go to [vercel.com](https://vercel.com) → **Sign up with GitHub** (free)
2. On the dashboard click **Add New** → **Project**
3. Find your `commentlens` repo → click **Import**
4. **Important settings:**
   - **Root Directory** → click *Edit* and set it to `frontend`
   - **Framework Preset** → should auto-detect as **Vite**
5. Expand **Environment Variables** and add:

   | Name | Value |
   |------|-------|
   | `VITE_API_URL` | The Render URL from Part 2 (e.g. `https://commentlens-api.onrender.com`) |

6. Click **Deploy**
7. Wait ~1 minute. You'll get a URL like:
   ```
   https://commentlens.vercel.app
   ```

---

## Part 4 — Connect them (2 min)

Tell the backend it's safe to accept requests from your new Vercel URL.

1. Go back to Render → your `commentlens-api` service
2. Click **Environment** in the left sidebar
3. Edit `FRONTEND_ORIGINS` → set value to your Vercel URL (e.g. `https://commentlens.vercel.app`)
4. Click **Save Changes** — Render auto-redeploys

> The CORS config also auto-allows any `*.vercel.app` URL, so preview deployments work too.

---

## Part 5 — Test it on your phone (1 min)

1. Open your Vercel URL on your phone's browser
2. Paste any YouTube link → tap **Summarize**
3. You're done!

### Add to Home Screen (makes it feel like a real app)

**iPhone (Safari):**
- Tap the **Share** button (square with arrow)
- Scroll down → **Add to Home Screen**
- Tap **Add**

**Android (Chrome):**
- Tap the **⋮** menu (top right)
- Tap **Add to Home screen**
- Tap **Add**

The app now lives on your home screen with the CommentLens icon.

---

## Sharing with your friend

Just send them the URL. That's it. No setup on their end.

```
https://commentlens.vercel.app
```

They can also add it to their home screen using the steps above.

---

## Updating the app later

Whenever you change code:

1. Edit files locally
2. Upload changed files to GitHub (or use GitHub Desktop)
3. Vercel and Render **auto-redeploy** within 1–2 minutes

---

## Costs breakdown

| Service | Cost |
|---------|------|
| GitHub | Free |
| Vercel | Free (hobby plan, generous limits) |
| Render | Free (with cold starts) |
| YouTube API | Free (10,000 requests/day quota) |
| Anthropic (Claude) | ~$0.01 per summary |

For ~500 summaries: about **$5 total**.

---

## Troubleshooting

**"First summary takes 30+ seconds"**
→ Render free tier was sleeping. Subsequent requests will be fast. Upgrade to Render's $7/mo plan to remove cold starts.

**"CORS error" in browser console**
→ `FRONTEND_ORIGINS` on Render doesn't match your Vercel URL exactly. Update and redeploy.

**"500 error on summarize"**
→ Check Render logs for the real error. Most likely an invalid API key. Re-enter under **Environment**.

**"Anthropic key has no credits"**
→ Add $5 at [console.anthropic.com/settings/billing](https://console.anthropic.com/settings/billing).
