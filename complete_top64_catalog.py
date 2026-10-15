import argparse
import csv
import html
import json
import re
import shutil
from pathlib import Path

import qrcode

ROOT = Path(__file__).resolve().parent
BASE_URL = 'https://box.shopluvbuds.com'


def read_csv(path):
    with path.open(newline='', encoding='utf-8-sig') as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def make_page(item, image_path):
    e = html.escape
    title = item['title']
    name = title if item['brand'].lower() in title.lower() else item['brand'] + ' ' + title
    details = [('Brand', item['brand']), ('Category', item['category']), ('SKU', item['sku'])]
    facts = ''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in details)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(name)} | Smoke Shop in a Box</title>
  <meta name="description" content="{e(item['description'], quote=True)}">
  <link rel="canonical" href="{BASE_URL}/{e(item['page'])}">
  <link rel="stylesheet" href="assets/top64-product.css">
</head>
<body>
  <header><div class="bar"><span class="brand"><span aria-hidden="true">▧</span> Smoke Shop in a Box</span><button type="button" id="share" aria-label="Share product information">↗</button></div></header>
  <main>
    <figure class="hero"><img src="{e(image_path)}" alt="{e(name, quote=True)}" width="750" height="750"></figure>
    <div class="heading"><p class="eyebrow">LuvBuds · Product information</p><h1>{e(name)}</h1><p class="sku">{e(item['sku'])}</p></div>
    <section class="about" aria-labelledby="about"><h2 id="about">About this item</h2><p>{e(item['description'])}</p></section>
    <section aria-label="Product details"><dl>{facts}</dl></section>
    <p class="note">{e(item['variant_note'])}</p>
  </main>
  <footer>LuvBuds product reference</footer>
  <script>
  document.getElementById('share').addEventListener('click', async () => {{
    const button = document.getElementById('share');
    try {{
      if (navigator.share) await navigator.share({{title:document.title,url:location.href}});
      else {{await navigator.clipboard.writeText(location.href);button.textContent='Copied';}}
    }} catch (error) {{if(error.name!=='AbortError') button.textContent='Copy URL';}}
  }});
  </script>
</body>
</html>
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--images-dir', required=True, type=Path)
    args = parser.parse_args()
    items = json.loads((ROOT / 'top64-sources.json').read_text())['products']
    catalog = read_csv(ROOT / 'qr-catalog.csv')
    products = read_csv(ROOT / 'products.csv')
    urls = read_csv(ROOT / 'products_with_urls.csv')
    known = {row['sku']: row for row in catalog}
    product_skus = {row['sku'] for row in products}
    url_skus = {row['sku'] for row in urls}
    created, registered = [], []
    for item in items:
        if item['verification'] != 'exact_sku_verified' or not item['image_source_url'].startswith('https://cdn11.bigcommerce.com/'):
            raise ValueError('Unverified product: ' + item['sku'])
        sku, page = item['sku'], item['page']
        if Path(page).name != page or not page.endswith('.html'):
            raise ValueError('Invalid page path')
        target = ROOT / page
        image_path = 'assets/products/top64/' + page.removesuffix('.html') + '.jpg'
        if not target.exists():
            source = args.images_dir / (item['item_number'] + '.jpg')
            if not source.is_file():
                raise FileNotFoundError(source)
            (ROOT / image_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, ROOT / image_path)
            target.write_text(make_page(item, image_path))
            created.append(page)
        if sku not in known:
            png = re.sub(r'[^\w\-+.]', '_', sku) + '.png'
            qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=4)
            qr.add_data(BASE_URL + '/' + page)
            qr.make(fit=True)
            qr.make_image(fill_color='black', back_color='white').save(ROOT / 'qr-codes' / png)
            entry = {'sku': sku, 'product_name': item['brand'] + ' ' + item['title'], 'url': BASE_URL + '/' + page, 'qr_png_relative': 'qr-codes/' + png}
            catalog.append(entry)
            known[sku] = entry
            registered.append(entry)
        if sku not in product_skus:
            products.append({'sku': sku, 'price': '', 'description': item['description']})
            product_skus.add(sku)
        if sku not in url_skus:
            urls.append({'sku': sku, 'price': '', 'description': item['description'], 'page_url': BASE_URL + '/' + page})
            url_skus.add(sku)
    for filename, rows in [('qr-catalog.csv', catalog), ('products.csv', products), ('products_with_urls.csv', urls)]:
        write_csv(ROOT / filename, rows)
    e = html.escape
    additions = []
    for row in registered:
        additions.append(f'<tr><td class="qr"><img src="{e(row["qr_png_relative"])}" alt="QR {e(row["sku"])}" width="120" height="120" loading="lazy"><br><a class="dl-btn" href="{e(row["qr_png_relative"])}" download>Download</a></td><td class="sku"><code>{e(row["sku"])}</code></td><td class="name">{e(row["product_name"])}</td><td class="url"><a href="{e(row["url"])}" target="_blank" rel="noopener">{e(row["url"])}</a></td></tr>')
    catalog_html = ROOT / 'qr-catalog.html'
    text = catalog_html.read_text()
    if additions:
        text = text.replace('</tbody>', '\n'.join(additions) + '\n</tbody>')
        text = re.sub(r'· \d+ products', '· ' + str(len(catalog)) + ' products', text)
        catalog_html.write_text(text)
    print(json.dumps({'new_pages': created, 'catalog_additions': [r['sku'] for r in registered], 'catalog_total': len(catalog)}))


if __name__ == '__main__':
    main()
