# Deploy CommentLens (Apple Skin) to Streamlit Cloud

After this you'll get a URL like `https://commentlens.streamlit.app` that works on **any phone, any computer, anywhere**. Free.

**Total time:** ~15 minutes

---

## What you need

- A **GitHub** account → [github.com/signup](https://github.com/signup) *(free, takes 2 min)*
- A **Streamlit Cloud** account *(sign in with GitHub — free)*
- A **YouTube API key** → [console.cloud.google.com](https://console.cloud.google.com)
- A **Groq API key** → [console.groq.com/keys](https://console.groq.com/keys) *(free with personal Gmail)*

---

## Part 1 — Get the code on GitHub (5 min)

### Easiest way: drag-and-drop upload

1. Go to **[github.com/new](https://github.com/new)**
2. Repository name: `commentlens` *(or whatever you like)*
3. Set to **Public** *(required for free Streamlit Cloud)*
4. ✅ Check **Add a README file**
5. Click **Create repository**
6. On the new repo page, click **Add file** → **Upload files**
7. Open File Explorer, go to `D:\Projects\Youtube Comments Summarizer\`
8. **Drag these files/folders** into the GitHub upload box:
   ```
   ✅ apple_app.py
   ✅ streamlit_app.py
   ✅ requirements.txt
   ✅ .gitignore
   ✅ README.md
   ✅ HOW_TO_USE.txt   (optional)
   ✅ STREAMLIT_DEPLOY.md
   ```
9. **DO NOT upload:**
   - ❌ `.env` *(has your secret keys — `.gitignore` blocks it anyway)*
   - ❌ `backend/` folder *(not needed for Streamlit)*
   - ❌ `frontend/` folder *(not needed for Streamlit)*
   - ❌ `node_modules/` *(if it exists)*

10. Scroll down → click **Commit changes**

---

## Part 2 — Deploy to Streamlit Cloud (5 min)

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Click **Sign in with GitHub** → authorize
3. Click **Create app** *(or "New app")*
4. Choose **Deploy a public app from GitHub**
5. Fill in the form:

   | Field | Value |
   |-------|-------|
   | Repository | `your-username/commentlens` |
   | Branch | `main` |
   | **Main file path** | **`apple_app.py`** ⬅ This is the magic line! |
   | App URL *(optional)* | `commentlens` *(picks the subdomain)* |

6. Click **Advanced settings** before deploying

---

## Part 3 — Add your API keys as Secrets (3 min)

Inside **Advanced settings** (still on the deploy screen):

1. Find the **Secrets** box
2. Paste this, replacing with your actual keys:

   ```toml
   YOUTUBE_API_KEY = "AIzaSy_your_youtube_key_here"
   GROQ_API_KEY = "gsk_your_groq_key_here"
   ```

3. Click **Save**
4. Click **Deploy!**

> **Why secrets?** This keeps your API keys safe — they're stored on Streamlit's servers, NOT in your public GitHub code. Anyone who looks at your code won't see them.

---

## Part 4 — Wait & test (2 min)

- Streamlit will take ~2 minutes to build and start your app
- When it's done you'll see your live URL: `https://commentlens.streamlit.app`
- Open it on your phone → test with a YouTube link → done!

---

## Sharing with your friend

Just send them the URL:
```
https://commentlens.streamlit.app
```

They open it on their phone or laptop. No setup. No installation. It just works.

### Add to Home Screen (so it feels like a real app)

**iPhone (Safari):**
- Tap the **Share** button (square with up-arrow)
- Scroll down → **Add to Home Screen** → **Add**

**Android (Chrome):**
- Tap the **⋮** menu top-right
- Tap **Add to Home screen** → **Add**

---

## Updating the app later

Whenever you want to change something:

1. Edit your file locally
2. Go to GitHub → open the file → click the ✏️ pencil icon → paste new content → **Commit**
3. Streamlit Cloud **auto-redeploys** within ~1 minute

---

## Switching back to the old (non-Apple) UI

If something breaks with `apple_app.py` and you want to go back:

1. On Streamlit Cloud dashboard, click your app
2. Click **⋮ menu** → **Settings**
3. Change **Main file path** from `apple_app.py` → `streamlit_app.py`
4. Click **Save** → it auto-redeploys

You can flip between the two in seconds.

---

## Costs

| Service | Cost |
|---------|------|
| GitHub | Free |
| Streamlit Cloud | Free |
| YouTube API | Free *(10,000 requests/day quota)* |
| Groq API | Free *(generous free tier — Llama 3.3 70B)* |

**Total: $0/month.**

---

## Troubleshooting

**"App is loading forever / build failed"**
→ Check **Manage app** → **Logs** on Streamlit Cloud. 95% of the time it's a missing package — make sure `requirements.txt` is in the repo root.

**"YouTube API error: quota exceeded"**
→ You hit the daily 10,000 quota. Resets at midnight Pacific time, OR create a new project in Google Cloud and use a fresh key.

**"Groq API error"**
→ Re-check your key in Streamlit Cloud → **Settings** → **Secrets**. Don't include extra spaces or quotes inside the value.

**"The styling looks broken"**
→ Hard refresh your browser (Ctrl+Shift+R / Cmd+Shift+R) to clear cached CSS.

**"I want to change the URL"**
→ Streamlit Cloud → your app → **Settings** → **Custom subdomain**.

---

## File reference

| File | Purpose |
|------|---------|
| `apple_app.py` | The Apple-style UI *(what Streamlit Cloud runs)* |
| `streamlit_app.py` | Original UI + all the engine logic *(imported by apple_app.py)* |
| `requirements.txt` | Tells Streamlit Cloud which packages to install |
| `.gitignore` | Stops `.env` from being uploaded *(critical for security)* |
| `STREAMLIT_DEPLOY.md` | This guide |
