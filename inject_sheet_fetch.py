#!/usr/bin/env python3
"""
inject_sheet_fetch.py

For every product HTML file in this directory:
  1. Adds id="product-price" to the price <span>
  2. Adds id="product-desc" to the description <p>
  3. Injects a Google Sheets fetch script with the correct per-file SKU
     and a REPLACE_WITH_STORE_SHEET_ID placeholder.

Run once from the smokeshopinboxlandingpages/ directory:
    python3 inject_sheet_fetch.py

Safe to re-run — it detects already-modified files and skips them.
"""

import os
import re

SKIP_FILES = {'template.html', 'inject_sheet_fetch.py'}
DIR = os.path.dirname(os.path.abspath(__file__))

JS_TEMPLATE = """
  <!-- Google Sheet live pricing — replace SHEET_ID per store -->
  <script>
    (function() {{
      var SHEET_ID = 'REPLACE_WITH_STORE_SHEET_ID';
      var SKU = '{sku}';
      fetch('https://docs.google.com/spreadsheets/d/' + SHEET_ID + '/gviz/tq?tqx=out:json&sheet=products')
        .then(function(r) {{ return r.text(); }})
        .then(function(raw) {{
          var data = JSON.parse(raw.slice(47, -2));
          var row = data.table.rows.find(function(r) {{ return r.c[0] && r.c[0].v === SKU; }});
          if (!row) return;
          var price = row.c[1] && row.c[1].v;
          var desc  = row.c[2] && row.c[2].v;
          if (price) {{
            var el = document.getElementById('product-price');
            if (el) el.textContent = '$' + Number(price).toFixed(2);
          }}
          if (desc) {{
            var el = document.getElementById('product-desc');
            if (el) el.textContent = desc;
          }}
        }})
        .catch(function() {{}});  // keep hardcoded fallback on any error
    }})();
  </script>
"""


def extract_sku(html: str) -> str:
    """Pull SKU from the visible SKU span in the page."""
    m = re.search(r'SKU:\s*([A-Z0-9\-]+)', html)
    return m.group(1) if m else ''


def already_modified(html: str) -> bool:
    return 'id="product-price"' in html or 'REPLACE_WITH_STORE_SHEET_ID' in html


def add_id_to_price(html: str) -> str:
    """Add id="product-price" to the price span (text-4xl font-bold)."""
    # Match <span class="text-4xl font-bold"> (no existing id)
    pattern = r'(<span)(\s+class="text-4xl font-bold">)'
    replacement = r'<span id="product-price"\2'
    new_html, count = re.subn(pattern, replacement, html, count=1)
    if count == 0:
        print("  WARNING: price span not found")
    return new_html


def add_id_to_desc(html: str) -> str:
    """Add id="product-desc" to the About this item paragraph."""
    pattern = r'(<p)(\s+class="text-white/70 leading-relaxed text-sm">)'
    replacement = r'<p id="product-desc"\2'
    new_html, count = re.subn(pattern, replacement, html, count=1)
    if count == 0:
        print("  WARNING: description paragraph not found")
    return new_html


def inject_script(html: str, sku: str) -> str:
    """Inject the fetch script just before </body>."""
    script = JS_TEMPLATE.format(sku=sku)
    return html.replace('</body>', script + '</body>', 1)


def process_file(path: str):
    filename = os.path.basename(path)
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    if already_modified(html):
        print(f'  SKIP (already modified): {filename}')
        return

    sku = extract_sku(html)
    if not sku:
        print(f'  SKIP (no SKU found): {filename}')
        return

    html = add_id_to_price(html)
    html = add_id_to_desc(html)
    html = inject_script(html, sku)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'  OK [{sku}]: {filename}')


def main():
    html_files = [
        os.path.join(DIR, f)
        for f in sorted(os.listdir(DIR))
        if f.endswith('.html') and f not in SKIP_FILES
    ]
    print(f'Processing {len(html_files)} HTML files...\n')
    for path in html_files:
        process_file(path)
    print(f'\nDone. {len(html_files)} files processed.')


if __name__ == '__main__':
    main()
