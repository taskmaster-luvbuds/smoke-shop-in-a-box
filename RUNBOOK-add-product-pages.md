# Runbook — Add Product Landing Pages + QR Codes (Smoke Shop in a Box)

**Use when:** new products need `box.shopluvbuds.com` landing pages + printable QR codes — e.g. a refreshed top-50 list, or the symptom *"the QR code is missing for some products."*

> **The #1 thing to understand:** a "missing QR code" is almost never a printing problem. The QR generator only produces a code for a product that **already has a landing page**. Missing QR = **missing page**. This runbook builds the missing pages, then the QR codes.

---

## Architecture (read first)

| Piece | Reality |
|-------|---------|
| Host | Static site in **this repo** (`taskmaster-luvbuds/smoke-shop-in-a-box`) → **Render** auto-deploys on push → **Cloudflare** in front (DNS + cache). |
| One page per SKU | `<lowercase-sku>.html` at repo root. Spaces → hyphens (`FL SB5-HAZMAT` → `fl-sb5-hazmat.html`). Dots stay (`grav-pbs.0.html`). |
| QR code | Encodes `https://box.shopluvbuds.com/<slug>.html`. One PNG per SKU in `qr-codes/<SKU>.png`. |
| Price + description | Pulled **live from a Google Sheet** (cols: `sku`, `price`, `description`) client-side. Hardcoded HTML values are the fallback. `inject_sheet_fetch.py` wires this in. |
| Template | `template.html` — fill name, image, description, features. |
| Data mirror | `products.csv` (sku, price, description) — local mirror of the Sheet. |

---

## Gotchas (every one cost real time — don't relearn them)

1. **Out-of-stock products vanish from store search.** When a SKU is out of stock, it won't show on `shopluvbuds.com` search, so you can't scrape its image. → pull the image manually from the **BigCommerce admin** and drop it in as a local file.
2. **Store search returns the WHOLE catalog grid, not a filtered match.** `search.php?search_query=<SKU>` returns ~90+ products. **Never take "the first result."** Match by the **product ID inside the CDN image URL** (`/products/<ID>/`). The planogram/order list gives you each product's ID.
3. **Two BigCommerce CDN URL shapes** — match either: `/products/<id>/images/<imgid>/file` (product page) and `/images/stencil/<size>/products/<id>/<imgid>/file` (grid). Rewrite `stencil/<size>/` → `stencil/original/` for full-res.
4. **CONSUMER copy, never wholesale.** The page is scanned by the shopper holding one unit at the shelf. **Strip** all case/display language: `8pk`, `24pk`, `POP Display`, `Retail Display`, `Display of 12`, `48 Books`, `Key Account`, `Bulk`, `ships as a display`. Use the clean product name (`Yocan Kodo Pro`, not `Yocan Kodo Pro 20pc Display | Assorted`). A wholesale-term gate in the generator enforces this.
5. **Dab devices ≠ 510 batteries.** Puffco Peak / Proxy are temp-controlled rigs — don't label them "510 Thread / Variable Voltage." Feature labels are product-type specific.
6. **SKU-scheme mismatch.** The planogram uses house SKUs (`HP-3P55G`); the store/catalog uses retail SKUs (`SE-HP-3P55G-BX`) for the *same* product. Policy (confirmed): **every planogram SKU gets its own page at its own slug**, even if a retail-SKU page exists.
7. **Watch for SKU typos** in the source list. `BIC-MAXI-HAZMAC` was a typo for `…HAZMAT` (page already existed). Cross-check against `products.csv` / catalog before building.
8. **Push auth.** The github.com SSH key resolves to a personal account **without write** to `taskmaster-luvbuds`. Push via the **tasks@luvbuds token remote** (the `https://…@github.com/...` remote, *not* `origin`). Reference it by name so the token never hits your command line.
9. **Render deploy lag + Cloudflare cache.** After push, pages can 404 for **several minutes** while Render builds. Verify with a **retry loop + cache-buster** (`?_cb=<ts>`) — Cloudflare may have cached an earlier 404, so the buster reads true origin. Don't call it done on a 2-minute check.

---

## Procedure

```
0. cd smokeshopinboxlandingpages && git pull          # (the tasks@luvbuds remote)
1. Identify missing SKUs → HEAD each box.shopluvbuds.com/<slug>.html ; 404 = needs a page
2. Resolve images:   catalog.json (exact + structural SKU match)
                   → scrape store by PRODUCT ID (not first result)
                   → operator-supplied local file for out-of-stock
3. Build pages:      fill template.html (name, image, CONSUMER description, category features)
4. Wire pricing:     python3 inject_sheet_fetch.py   (generator does this inline)
5. Generate QRs:     .venv-qr/bin/python  → qr-codes/<SKU>.png  (encodes the page URL)
6. Wholesale gate:   scan names+descriptions for blocked terms → must be CLEAN
7. Verify local:     pages well-formed; QRs decode to correct URL; NO existing page overwritten
8. Commit + push:    git -c user.email=amazzei@luvbuds.co commit ... ; push via token remote
9. Verify LIVE:      all return HTTP 200 (retry ~5 min for Render lag, cache-busted)
10. Hand off:        print ONLY new qr-codes/<SKU>.png ; add new SKUs+prices to the Google Sheet
```

### One-shot generator
`build_landing_pages.py` does steps 2–6 + writes `new-items-manifest.csv`. For a new batch, edit the `ITEMS` list (`rank, sku, name, product_id, category, description`) and `LOCAL_IMG` (out-of-stock images), then:
```bash
.venv-qr/bin/python build_landing_pages.py        # builds pages + qr-codes/ + manifest, runs wholesale gate
```
Categories drive the feature grid: `battery` (510), `dab` (Puffco temp-control), `pipe`, `waterpipe`, `papers`, `lighter`.

> Note: the image resolver reads a catalog.json that lives on the MERIDIAN side (planogram export). If unavailable, the generator falls back to store scraping by product ID; supply local images for anything out-of-stock.

### Deploy (step 8 detail)
```bash
# stage ONLY your artifacts — never `git add .`
git add <slug>.html ... qr-codes/<SKU>.png ... assets/products/*.jpg new-items-manifest.csv products.csv
git -c user.name="amazzei-Luvbuds" -c user.email="amazzei@luvbuds.co" commit -m "Add N product landing pages + QR codes"
TR=$(git remote | grep -v '^origin$' | head -1)   # tasks@luvbuds token remote; name not echoed
git push "$TR" main
```

### Verify live (step 9 detail)
```bash
# retry loop, cache-busted — Render lag means don't trust a too-early check
for slug in $(...); do curl -sI "https://box.shopluvbuds.com/$slug.html?_cb=$(date +%s)" | head -1; done
# expect HTTP/2 200 for all before printing QRs
```

---

## Standing maintenance / hygiene
- **Google Sheet:** new SKUs need a row (sku, price, description) or the page shows copy with no price.
- **Token hygiene:** two plaintext tokens live in `.git/config` (this repo `gho_…`, parent ontology repo `ghp_…`). Rotate them and switch to SSH write-access or a credential helper.
- **Print only the new QRs.** Existing pages' QR codes are already printed; reprinting all wastes a run.

## Reference (last run — 2026-06-18)
26 new pages for top-50 SKUs missing pages. Commit `04f95ec`. 22 images ID-matched from store + 4 out-of-stock supplied. All 26 verified HTTP 200. Manifest: `new-items-manifest.csv`.
