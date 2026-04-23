#!/usr/bin/env python3
"""
Generate QR PNGs + HTML/CSV catalog from products_with_urls.csv for a configurable base domain.
Run: pip install qrcode[pil]  &&  python generate_qr_catalog.py
"""
from __future__ import annotations

import csv
import html as html_mod
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_M
except ImportError:
    print("Install dependencies: pip install 'qrcode[pil]'", file=sys.stderr)
    raise

# Primary public URL for landing pages (HTTPS, no trailing slash on host)
BASE_URL = "https://box.shopluvbuds.com"

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "products_with_urls.csv"
QR_DIR = ROOT / "qr-codes"
OUT_HTML = ROOT / "qr-catalog.html"
OUT_CSV = ROOT / "qr-catalog.csv"


def safe_filename(sku: str) -> str:
    return re.sub(r"[^\w\-+.]", "_", sku)


def landing_path_from_row(page_url: str) -> str:
    """Path only, e.g. /bic-maxi-hazmat.html — keeps CSV as source of truth for slugs."""
    p = urlparse(page_url)
    path = p.path or "/"
    if not path.startswith("/"):
        path = "/" + path
    return path


def public_url(path: str) -> str:
    base = BASE_URL.rstrip("/")
    path = path if path.startswith("/") else "/" + path
    return base + path


def title_from_html(html_path: Path) -> str | None:
    if not html_path.is_file():
        return None
    try:
        text = html_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    m = re.search(r"<title>\s*(.*?)\s*</title>", text, re.IGNORECASE | re.DOTALL)
    if not m:
        return None
    raw = html_mod.unescape(re.sub(r"\s+", " ", m.group(1)).strip())
    # Strip common site suffix from product pages
    for sep in (" | Smoke Shop in a Box", " | Smoke Shop"):
        if sep in raw:
            raw = raw.split(sep)[0].strip()
            break
    return raw or None


def short_name_from_description(desc: str, max_len: int = 72) -> str:
    one = desc.strip().strip('"')
    if len(one) <= max_len:
        return one
    cut = one[: max_len - 1].rsplit(" ", 1)[0]
    return cut + "…"


def main() -> None:
    if not CSV_PATH.is_file():
        print(f"Missing {CSV_PATH}", file=sys.stderr)
        sys.exit(1)

    QR_DIR.mkdir(exist_ok=True)

    rows: list[dict] = []
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sku = (row.get("sku") or "").strip()
            if not sku:
                continue
            page_url = (row.get("page_url") or "").strip()
            desc = (row.get("description") or "").strip()
            path = landing_path_from_row(page_url)
            url = public_url(path)
            slug = path.strip("/").replace(".html", "") or sku.lower()

            html_file = ROOT / Path(path).name
            name = title_from_html(html_file) or short_name_from_description(desc)

            png_name = f"{safe_filename(sku)}.png"
            png_path = QR_DIR / png_name

            qr = qrcode.QRCode(
                version=None,
                error_correction=ERROR_CORRECT_M,
                box_size=8,
                border=2,
            )
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(png_path)

            rows.append(
                {
                    "sku": sku,
                    "product_name": name,
                    "url": url,
                    "qr_png": png_name,
                    "path": path,
                }
            )

    # CSV (relative paths work when opening HTML from same folder)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["sku", "product_name", "url", "qr_png_relative"],
        )
        w.writeheader()
        for r in rows:
            w.writerow(
                {
                    "sku": r["sku"],
                    "product_name": r["product_name"],
                    "url": r["url"],
                    "qr_png_relative": f"qr-codes/{r['qr_png']}",
                }
            )

    # HTML table
    esc = (
        lambda s: s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    trs = []
    for r in rows:
        trs.append(
            "<tr>"
            f'<td class="qr"><img src="qr-codes/{esc(r["qr_png"])}" alt="QR {esc(r["sku"])}" width="120" height="120" loading="lazy" />'
            f'<br/><a class="dl-btn" href="qr-codes/{esc(r["qr_png"])}" download="{esc(r["qr_png"])}">Download</a></td>'
            f'<td class="sku"><code>{esc(r["sku"])}</code></td>'
            f'<td class="name">{esc(r["product_name"])}</td>'
            f'<td class="url"><a href="{esc(r["url"])}" target="_blank" rel="noopener">{esc(r["url"])}</a></td>'
            "</tr>"
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>QR catalog — {esc(BASE_URL)}</title>
  <style>
    :root {{ font-family: system-ui, sans-serif; }}
    body {{ margin: 1rem; background: #fafafa; color: #111; }}
    h1 {{ font-size: 1.25rem; margin-bottom: 0.5rem; }}
    p.meta {{ color: #555; margin-top: 0; font-size: 0.9rem; }}
    table {{ border-collapse: collapse; width: 100%; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,.08); }}
    th, td {{ border: 1px solid #e5e5e5; padding: 0.5rem 0.6rem; vertical-align: top; text-align: left; }}
    th {{ background: #f4f4f5; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; }}
    td.qr {{ width: 140px; }}
    td.sku {{ white-space: nowrap; }}
    td.name {{ max-width: 28rem; }}
    td.url {{ word-break: break-all; font-size: 0.85rem; }}
    code {{ font-size: 0.9rem; }}
    a {{ color: #2563eb; }}

    .dl-btn {{ display: inline-block; margin-top: 6px; padding: 3px 10px; font-size: 0.75rem; background: #2563eb; color: #fff; border-radius: 4px; text-decoration: none; }}
    .dl-btn:hover {{ background: #1d4ed8; }}
    @media print {{
      .dl-btn {{ display: none; }}
      body {{ background: #fff; }}
      a {{ color: #000; text-decoration: none; }}
    }}
  </style>
</head>
<body>
  <h1>Product QR codes</h1>
  <p class="meta">Base URL: <strong>{esc(BASE_URL)}</strong> · Generated from <code>products_with_urls.csv</code> · {len(rows)} products</p>
  <table>
    <thead>
      <tr><th>QR</th><th>SKU</th><th>Product name</th><th>Link</th></tr>
    </thead>
    <tbody>
{chr(10).join(trs)}
    </tbody>
  </table>
</body>
</html>
"""
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote {len(rows)} QR images to {QR_DIR}")
    print(f"Wrote {OUT_HTML}")
    print(f"Wrote {OUT_CSV}")


if __name__ == "__main__":
    main()
