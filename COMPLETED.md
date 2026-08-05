# Smoke Shop in a Box — Completed Work

## Deployment
- [x] **Render static site created** — `smoke-shop-in-a-box-59wb.onrender.com`
- [x] Auto-deploy on push to `main` branch (GitHub: `taskmaster-luvbuds/smoke-shop-in-a-box`)
- [x] Root URL rewrite rule added (`/` → `/index.html`)
- [x] Cache-Control set to `no-cache` for live updates

## Product Catalog (index.html)
- [x] 5 box configurations: Standard, Deluxe+PCL, Electronic Station, SirEEL Glass Station, SirEEL Simple Pipes
- [x] 63 product one-pager HTML pages linked from catalog
- [x] Dark theme with brand colors (orange/green/dark)
- [x] Mobile-responsive layout
- [x] Hero image + section jump links

## Product Demo Videos (22 of 63 products)
- [x] Videos uploaded to CloudFront CDN
- [x] Embedded as `<video autoplay loop muted playsinline>` — plays automatically
- [x] `preload="auto"` for faster load
- [x] JavaScript fallback for Safari/iOS autoplay: retries `.play()` on first user interaction (touch/scroll/click)
- [x] Mute/unmute toggle button (bottom-right, 56px round) — icon swaps `volume-x` ↔ `volume-2`

### Products with live video:
| SKU | Product |
|-----|---------|
| BIC-MAXI-HAZMAT | BIC Maxi Lighter 50pk Display |
| BT-380VV | LuvBuds 380mAh Battery, Asst |
| BT-PENJAMINCARKEY-ASST | Penjamin Car Key Battery, Asst |
| BT-V846D2 | Pulsar SYNDR Dry Herb Battery 5pk |
| GND-ZNC50 | LuvBuds 50mm Zinc Grinder, Asst |
| LOOK-SH-PRO-PLUS-BK | Lookah Seahorse Pro Plus, Black |
| LOOK-SNAIL2.0-BK | Lookah Snail 2.0, Black |
| OOZ-1187 | Ooze Slim Twist Pen 2.0, Asst |
| SE-BT-EV-THERMO-10PK | SirEEL Hover EV 10pk, Thermo |
| SE-BT-IRONLUNG5P-SOLID | SirEEL Iron Lung 5pc, Solid |
| SE-HP-4P85G-BX | SirEEL 4.5" Bulk Pipes 25pc |
| SE-HP-CHILL3-BX | SirEEL 3" Chillums 36pc, Asst |
| SE-WP-LEAFNECKBASE | SirEEL 9.75" Technicolor Beaker |
| SE-WP-TUBE10 | SirEEL 10" Iridized Illusion Bong |
| SE-WP-TWISTBKR8 | SirEEL 8" Twisted Neck Beaker |
| WP-DONUTMACSTAR7 | LuvBuds 7" Slime Donut Bong, Asst |
| WP-SPOREORBRIG | LuvBuds 7" Spore Perc Dab Rig |
| WP-WIGWAGDONUT6 | LuvBuds 6" Wig Wag D'OH-nut Bong |
| ZZ114-48 | Zig-Zag Orange Papers 48pk Display |
| ZZ114C24 | Zig-Zag Ultra Thin Cones 24ct 6pk |
| ZZUB11424 | Zig-Zag Unbleached Cones 24ct 6pk |
| ZZHMP48 | Zig-Zag Organic Hemp Papers 48pk |

## Lead Capture (All 63 Product Pages)
- [x] "Get the Deal" sticky CTA button at bottom of every page
- [x] Centered modal with name/email/phone inputs (mobile keyboard compatible)
- [x] `pointer-events` fix applied — inputs are tappable on mobile
- [x] "You're in!" success animation with auto-close after 2.5s
- [x] Form submits to Google Apps Script via hidden iframe POST
- [x] Apps Script endpoint: `https://script.google.com/macros/s/AKfycbz...5ay/exec`
- [x] Target Google Sheet: "Smoke Shop Leads 2026" (`1MgTFDelEff_1FbCNOmF74nWrKKQKmi55hzstDxVDtgQ`)
- [x] Email notification on each lead to `tasks@luvbuds.co`
- [x] Data captured: timestamp, name, email, phone, product name, SKU, page URL

## Other Features
- [x] Share button on every product page (native share API or clipboard copy)
- [x] Product images from BigCommerce CDN
- [x] Google Sheets pricing fetch (per-store Sheet ID injection point)
- [x] 3 experimental BIC Maxi variants (brutalist, brutalist-dark, GRAB and GO)
- [x] `inject_sheet_fetch.py` — bulk script to inject pricing fetch into HTML files
- [x] `SETUP.md` — store onboarding guide

## Git History (Key Commits)
```
435099b fix: switch to hidden form submission for reliable Apps Script delivery
897d171 fix: remove pointer-events-none from modal sheet so inputs are tappable
f18db53 fix: convert signup modal to centered card for mobile keyboard compat
164828e feat: wire signup forms to Google Sheets + email notifications
d46a26a fix: enlarge mute/unmute button for easier mobile tapping
4daa10b fix: force video autoplay on Safari/iOS with JS fallback
5dee165 fix: add rewrite rule so root URL serves index.html
5887851 feat: add mute/unmute toggle button to product demo videos
c8fd8c1 feat: replace video placeholders with product demo videos for 22 SKUs
```


## Aug 5 2026 Video Batch (CDN + page wire)

Wired new CloudFront videos into placeholder pages and generated missing pages. **Did not replace** any existing live video `src`.

### Newly wired onto existing pages (26)
BT-GROOVE-BOLT-24PK, BT-GROOVE-CARAPLUS, CB-GLOB-TRAVEL, CLE-RANDYBLK12, FL SB5-HAZMAT, GROOVE-GND-RIPSTER, HP-OGCHILL, LOOK-BEAR-ASST-5PK, LOOK-BEARTDYE-ASST-5PK, LOOK-CAT-BL, LOOK-GTA-ASST-5PK, LOOK-UNICORNMINI-BK, SE-BT-DOPPLEGANGER, SE-BT-GASTANKDISP, SE-BT-IRONLUNG5P-THERMO, SE-HP-2.5P40G-BX, SE-HP-SPOON45-BX, SE-QBNG-ETCHBCKT-14M-BX, SE-WP-FUMRECYC5-BX, SE-WP-MARBLEDRIG6-BX, VP-TRPPEN2-BLACK, YOCAN-EVOLVE-PLUS-XL, YOCAN-FLATPLUS, YOCAN-KODOPRO, YOCAN-POCKET, ZZUB11436

### New pages generated + video wired (7)
- `SE-BT-EV-ELECTRO-10PK` → `se-bt-ev-electro-10pk.html` (SirEEL Hover EV 10pk, Electro)
- `SE-WP-RASTALEAF` → `se-wp-rastaleaf.html` (SirEEL 9.75" Rasta Leaf Beaker)
- `SE-DUG-STATICTRIP` → `se-dug-statictrip.html` (SirEEL Static Trip Dugout)
- `WP-SG8` → `wp-sg8.html` (8" Soft Glass Water Pipe)
- `ZZUB48` → `zzub48.html` (Zig-Zag Unbleached Papers 48pk)
- `SE-WP-CLEARHANG6` → `se-wp-clearhang6.html` (SirEEL 6" Clear Hanger Rig)
- `ZZ114` → `zz114.html` (Zig-Zag Orange Papers 1 1/4)

### Skipped (already had live video — left alone)
SE-HP-CHILL3-BX, LOOK-SH-PRO-PLUS-BK, SE-WP-LEAFNECKBASE, SE-BT-IRONLUNG5P-SOLID, WP-SG6, ZZHMP48, ZZ114C24, PFC-PEAKNEWCANYON, ZZUB11424

### Notes
- `ZZUB114.mp4` → **ZZ114** (Zig-Zag Orange 1 1/4)
- `ZZUB114-48.mp4` → **ZZUB48**
- Total on-site after this batch: see `video-factory/has-video.json`
