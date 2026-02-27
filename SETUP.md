# Smoke Shop in a Box — New Store Setup Guide

Each store gets:
- Their own **Google Sheet** (you control the prices)
- Their own **GitHub fork** of this repo
- Their own **Render Static Site** (free tier, live URL)

Update a price in the Sheet → the page reflects it within ~30 seconds. No code, no deploys.

---

## Step 1 — Create the Store's Google Sheet

1. Open the master template sheet (ask LuvBuds for the link)
2. **File → Make a copy** — name it something like `[Store Name] — Product Prices`
3. Click **Share → Anyone with the link → Viewer**
4. Copy the **Sheet ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/SHEET_ID_IS_HERE/edit
   ```

### Sheet structure (do not change column order)

| A — sku | B — price | C — description |
|---------|-----------|-----------------|
| SE-WP-ORACLEORB-BX | 79.99 | The Oracle Orb does what a great pipe should... |
| BT-380VV | 10.00 | The 380 is your reliable, no-nonsense battery... |
| ... | ... | ... |

- Row 1 is the header row — leave it as-is
- SKUs must match exactly (case-sensitive, including spaces/dots for oddly-named products)
- Price is a plain number — no `$` sign
- Description is free text

---

## Step 2 — Fork This Repo

1. Go to the `luvbuds-store-landing` GitHub repo
2. Click **Fork** → create the fork under your account or the org
3. In your fork, do a **global find-and-replace** (all files):
   - Find: `REPLACE_WITH_STORE_SHEET_ID`
   - Replace with: the Sheet ID you copied in Step 1

   **On macOS (terminal):**
   ```bash
   find . -name "*.html" -exec sed -i '' 's/REPLACE_WITH_STORE_SHEET_ID/YOUR_SHEET_ID_HERE/g' {} +
   ```

4. Commit and push the change

---

## Step 3 — Deploy to Render

1. Log in at [render.com](https://render.com)
2. Click **New → Static Site**
3. Connect your GitHub fork
4. Settings:
   - **Root Directory:** leave blank (or `.`)
   - **Build Command:** leave blank
   - **Publish Directory:** `.`
5. Click **Create Static Site**

Render will deploy and give you a free URL like `your-store-name.onrender.com`.

---

## Step 4 — Done

Share the URL with the store owner. They open their Google Sheet, edit the `price` or `description` column, and the next page load picks up the change automatically.

---

## How Pricing Updates Work

```
Store owner edits Google Sheet
  → saves
  → next visitor loads the page
  → JS fetches Sheet (public read, no API key needed)
  → price/description updates on screen
```

Latency: 10–30 seconds (Google's sheet publish cache).

**Fallback:** If the fetch fails for any reason (offline, Sheet permissions changed), the hardcoded price already in the HTML shows instead. The page never breaks.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Price not updating | Check Sheet sharing is "Anyone with link → Viewer" |
| Price shows old value | Hard-refresh (`Cmd+Shift+R`), wait 30s, try again |
| Blank price after load | Sheet ID wrong in HTML files — redo Step 2 |
| Console error `Failed to fetch` | Sheet not shared publicly — fix sharing settings |
