import argparse
import base64
import csv
import html
import json
import mimetypes
import re
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

CARD_W,CARD_H=252,180
RED=HexColor('#df1f26'); INK=HexColor('#192131'); MUTE=HexColor('#657083')
FONT='Helvetica';BOLD='Helvetica-Bold'


def local_photo(row):
    return SOURCE_IMG / (row['ItemNumber'] + '.jpg')


def paragraph(c, text, x, y_top, w, max_h, max_pt, min_pt=5.3, bold=False, leading=None):
    for size in [max_pt-j*0.2 for j in range(int((max_pt-min_pt)/.2)+1)]:
        st=ParagraphStyle('f',fontName=BOLD if bold else FONT,fontSize=size,leading=leading or size*1.21,textColor=INK,spaceAfter=0,allowWidows=0,allowOrphans=0)
        p=Paragraph(xml_escape(text).replace('\n','<br/>'), st)
        _,h=p.wrap(w,max_h)
        if h<=max_h+0.1:
            p.drawOn(c,x,y_top-h)
            return h
    return 0

def paint_card(c,row,x=0,y=0):
    c.saveState(); c.translate(x,y)
    c.setFillColor(HexColor('#ffffff'));c.rect(0,0,CARD_W,CARD_H,stroke=0,fill=1)
    c.setFillColor(RED);c.rect(0,CARD_H-23,CARD_W,23,stroke=0,fill=1)
    c.setFont(BOLD,9.7);c.setFillColor(HexColor('#ffffff'));c.drawString(9,CARD_H-15,'LuvBuds')
    c.setFont(BOLD,6.5);c.drawRightString(CARD_W-8,CARD_H-14,row['Brand'][:22].upper())
    photo=local_photo(row)
    if photo:
        im=ImageReader(str(photo));iw,ih=im.getSize(); box=(10,45,105,102)
        cw,ch=box[2],box[3];scale=min(cw/iw,ch/ih)
        iw,ih=iw*scale,ih*scale
        c.drawImage(im,box[0]+(cw-iw)/2,box[1]+(ch-ih)/2,width=iw,height=ih,mask='auto')
    else:
        c.setFillColor(HexColor('#f0f2f4'));c.roundRect(9,45,107,102,5,stroke=0,fill=1)
        c.setStrokeColor(HexColor('#d4d8de'));c.setLineWidth(.4);c.roundRect(9,45,107,102,5,stroke=1,fill=0)
        c.setFillColor(MUTE);c.setFont(BOLD,7.6);c.drawCentredString(62,95,'PHOTO PENDING')
        c.setFont(FONT,6.3);c.drawCentredString(62,84,'Approved image required')
        c.setFont(FONT,6.2);c.drawCentredString(62,75,'Item '+row['ItemNumber'])
    c.setFillColor(RED);c.rect(123,142,3,6,stroke=0,fill=1)
    c.setFont(BOLD,6.8);c.setFillColor(INK);c.drawString(131,142,row['Category'].upper()[:22])
    paragraph(c,row['Card Title'],123,134,118,32,9.8,min_pt=7.3,bold=True)
    paragraph(c,row['Short Description'],123,97,118,20,7.0,min_pt=6.2)
    c.setFillColor(HexColor('#d7dce1'));c.rect(123,69,120,.4,stroke=0,fill=1)
    c.setFillColor(MUTE);c.setFont(BOLD,6);c.drawString(9,36,'SKU')
    sku=row['Proposed SKU'] or 'PENDING VERIFICATION'
    fs=7.3
    while pdfmetrics.stringWidth(sku, BOLD, fs)>172 and fs>5.3:fs-=.2
    c.setFillColor(INK);c.setFont(BOLD,fs);c.drawString(9,24,sku)
    qrurl=row['QR URL']
    if qrurl:
        p=QR_DIR/(row['ItemNumber']+'.png')
        if not p.exists():qr_png(qrurl,p)
        c.drawImage(ImageReader(str(p)),184,9,59,59)
    else:
        c.setFillColor(HexColor('#f0f1f2'));c.roundRect(184,9,59,59,2,stroke=0,fill=1)
        c.setFillColor(MUTE);c.setFont(BOLD,6);c.drawCentredString(219.5,34,'QR CODE')
        c.drawCentredString(219.5,24,'PENDING')
    c.setFillColor(MUTE);c.setFont(FONT,5.2);c.drawString(139,11,'ITEM '+row['ItemNumber'])
    c.restoreState()

def make_pdf(items):
    for bleed,suffix in [(0,'Trim'),(9,'Bleed')]:
        c=canvas.Canvas(str(HERE/f'LuvBuds_64_Cards_Individual_{suffix}.pdf'),pagesize=(CARD_W+2*bleed,CARD_H+2*bleed),pageCompression=1,initialFontName=FONT)
        c.setTitle(f'LuvBuds 64 Product Cards | {suffix} | 3.5 x 2.5 inch trim')
        c.setAuthor('LuvBuds')
        for row in items:
            c.setTrimBox((bleed,bleed,CARD_W+bleed,CARD_H+bleed))
            c.setBleedBox((0,0,CARD_W+2*bleed,CARD_H+2*bleed))
            c.setFillColor(HexColor('#ffffff'));c.rect(0,0,CARD_W+2*bleed,CARD_H+2*bleed,stroke=0,fill=1)
            c.setFillColor(RED);c.rect(0,CARD_H+bleed-23,CARD_W+2*bleed,23+bleed,stroke=0,fill=1)
            paint_card(c,row,bleed,bleed);c.showPage()
        c.save()
    c=canvas.Canvas(str(HERE/'LuvBuds_64_Cards_8up_Letter.pdf'),pagesize=(612,792),pageCompression=1,initialFontName=FONT)
    c.setTitle('LuvBuds 64 Product Cards | 8-up Letter | Actual-size cutting sheets')
    c.setAuthor('LuvBuds')
    for start in range(0,len(items),8):
        c.setFillColor(MUTE);c.setFont(BOLD,8);c.drawString(54,773,'LuvBuds / Product cards')
        c.setFont(FONT,7);c.drawRightString(558,773,f'Cards {start+1:02d}-{min(start+8,len(items)):02d} | 100% print scale')
        for i,row in enumerate(items[start:start+8]):
            x=54+(i%2)*252;y=759-(i//2+1)*180
            paint_card(c,row,x,y)
        c.setStrokeColor(HexColor('#9da5ae'));c.setLineWidth(.3)
        for x in (54,306,558):
            for y in (35,763):c.line(x,y-3,x,y+3)
        for y in (39,219,399,579,759):
            c.line(47,y,51,y);c.line(561,y,565,y)
        c.setFillColor(MUTE);c.setFont(FONT,6);c.drawString(54,17,'Print at ACTUAL SIZE / 100%. Office cutting sheets. Print shop: use the individual Bleed PDF.')
        c.showPage()
    c.save()


def make_html(items):
    parts=[]
    for r in items:
        name=html.escape(r['Card Title']);brand=html.escape(r['Brand']);desc=html.escape(r['Short Description']);sku=html.escape(r['Proposed SKU'] or 'PENDING VERIFICATION');num=html.escape(r['ItemNumber']); cat=html.escape(r['Category'])
        p=local_photo(r)
        if p:
            photo=f'<img class="product-photo" src="assets/photos/{num}{p.suffix}" alt="Product photograph">'
        else:
            photo=f'<div class="no-photo"><strong>PHOTO PENDING</strong><small>Save approved image as<br>assets/photos/{num}.jpg</small></div>'
        if r['QR URL']:
            q=f'<a href="{html.escape(r["QR URL"], quote=True)}" target="_blank" rel="noopener"><img class="qr" src="assets/qr/{num}.png" alt="QR code"></a>'
        else:
            q='<div class="no-qr">QR<br>PENDING</div>'
        flag=''
        parts.append(f'''<div class="card-item" data-search="{html.escape((r['Brand']+' '+r['Source Description']+' '+sku+' '+num).lower(),quote=True)}" data-category="{cat}">
          <article class="card"><div class="card-head"><b>LuvBuds</b><span>{brand}</span></div>
          <div class="visual">{photo}</div><div class="details"><div class="cat">{cat.upper()}</div><div class="product-name">{name}</div>
          <div class="blurb">{desc}</div><div class="sku-label">SKU</div><div class="sku">{sku}</div></div>
          <div class="qr-wrap">{q}</div><div class="item-number">ITEM {num}</div></article>
          <div class="metadata"><strong>#{r['Rank']:0>2} · Item {num}</strong> &nbsp; {html.escape(r['Match Status'])}{html.escape(flag)}</div>
        </div>''')
    p=HERE/'LuvBuds_64_Cards_Interactive_Production.html'
    htmlbody='\n'.join(parts)
    p.write_text('''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LuvBuds 64 Production Cards</title>
<style>
:root{--red:#df1f26;--ink:#182131;--muted:#677182}*{box-sizing:border-box}body{margin:0;background:#f5f6f8;color:var(--ink);font-family:Inter,Arial,Helvetica,sans-serif}
header{background:#141a23;color:white;padding:24px max(28px,calc((100vw - 1340px)/2));display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap}
header h1{font-size:24px;margin:0}header p{font-size:12px;color:#bfc7d4;margin:7px 0 0}header .pill{font-size:12px;background:#293344;padding:7px 12px;border-radius:6px}
.tools{position:sticky;top:0;z-index:5;display:flex;align-items:center;flex-wrap:wrap;gap:10px;padding:15px max(28px,calc((100vw - 1340px)/2));background:white;border-bottom:1px solid #e2e5eb}
.tools input,.tools select{border:1px solid #d5dbe4;border-radius:6px;padding:10px 11px;font:inherit;font-size:13px;min-width:180px;outline:none}
.tools button{border:none;border-radius:6px;background:var(--red);color:white;font-size:13px;font-weight:700;padding:11px 18px;cursor:pointer}.tools small{color:var(--muted)}
main{padding:28px;max-width:1400px;margin:auto}.info{margin:0 0 20px;font-size:13px;color:#5b6678}.gallery{display:grid;grid-template-columns:repeat(auto-fill,minmax(355px,1fr));gap:18px;align-items:start}
.card-item{display:flex;flex-direction:column;align-items:center;gap:8px;background:white;border:1px solid #e6e9ef;border-radius:12px;padding:13px 10px 11px;box-shadow:0 3px 16px #1c293a0a;overflow:hidden}
.card{width:3.5in;height:2.5in;background:#fff;border:1px solid #e5e8ec;position:relative;overflow:hidden;flex-shrink:0;color:var(--ink);font-family:Arial,Helvetica,sans-serif;box-shadow:0 2px 4px #18213112}
.card-head{position:absolute;left:0;top:0;right:0;height:.32in;background:var(--red);color:white;display:flex;align-items:center;justify-content:space-between;padding:0 9px;font-size:9px}.card-head span{font-weight:700;font-size:8px}
.visual{position:absolute;left:10pt;top:33pt;width:105pt;height:102pt;border-radius:5px;background:#f1f3f6;display:flex;align-items:center;justify-content:center;overflow:hidden}
.product-photo{max-width:100%;max-height:100%;object-fit:contain}.no-photo{text-align:center;color:#657083;font-size:10px}.no-photo small{display:block;font-size:7px;line-height:1.6;margin-top:9px}
.details{position:absolute;left:123pt;top:33pt;width:118pt}.cat{font-size:6px;letter-spacing:.3px;border-left:3px solid var(--red);padding-left:5px;font-weight:bold;margin-bottom:7px}.product-name{font-size:10px;font-weight:750;line-height:1.15;max-height:38px;overflow:hidden}.blurb{font-size:7px;line-height:1.3;margin-top:6px;max-height:25px;overflow:hidden}
.sku-label{position:absolute;left:-114pt;top:108pt;font-size:6px;font-weight:700;color:#677182}.sku{position:absolute;left:-114pt;top:119pt;font-size:7px;font-weight:bold;white-space:nowrap;max-width:175px;overflow:hidden;text-overflow:ellipsis}.qr-wrap{position:absolute;right:9pt;bottom:9pt;width:59pt;height:59pt}.qr{width:59pt;height:59pt}.no-qr{height:57px;background:#f2f3f5;color:#697384;border-radius:4px;display:flex;align-items:center;justify-content:center;text-align:center;font-size:7px;font-weight:bold}
.item-number{position:absolute;left:139pt;bottom:12pt;color:#697384;font-size:6px}.proof{position:absolute;left:9px;bottom:13px;color:var(--red);font-size:6px;font-weight:700}.metadata{font-size:11px;color:#697384;text-align:center}
@page{size:letter;margin:.5in .75in}
@media print{body{background:white}header,.tools,.info,.metadata{display:none!important}main{max-width:none;margin:0;padding:0}.gallery{display:grid;grid-template-columns:3.5in 3.5in;gap:0;justify-content:center}.card-item{width:3.5in;height:2.5in;padding:0;box-shadow:none;border:0;border-radius:0;break-inside:avoid;page-break-inside:avoid}.card{box-shadow:none} }
</style></head><body><header><div><h1>LuvBuds / Florida Display / 64 Production Cards</h1><p>3.5 × 2.5 in cards · 64 highlighted ItemNumbers · no prices</p></div><div class="pill">PRODUCTION · OCT 2026</div></header>
<div class="tools"><input id="search" type="search" placeholder="Search brand, item # or SKU"><select id="category"><option value="">All categories</option><option>Electronics</option><option>Glass</option><option>Papers & Cones</option><option>Other Accessories</option></select><button type="button" onclick="window.print()">Print cards at 100%</button><small id="count">64 cards</small></div>
<main><p class="info">64 product photographs and 64 QR codes. For professional printing, use the individual PDF with 0.125-inch bleed. The Letter sheet PDF is for actual-size office printing.</p>
<div id="cards" class="gallery">''' + htmlbody+'''</div></main><script>
const cards=[...document.querySelectorAll('.card-item')];function filter(){const q=document.getElementById('search').value.toLowerCase(),cat=document.getElementById('category').value;let shown=0;cards.forEach(c=>{const show=(!q||c.dataset.search.includes(q))&&(!cat||c.dataset.category===cat);c.style.display=show?'':'none';if(show)shown++});document.getElementById('count').textContent=shown+' / '+cards.length+' cards'}document.getElementById('search').addEventListener('input',filter);document.getElementById('category').addEventListener('change',filter);
</script></body></html>''',encoding='utf-8')

def main():
    global HERE,SOURCE_IMG,QR_DIR,FONT,BOLD
    parser=argparse.ArgumentParser()
    parser.add_argument('--cards-json',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--font-dir',type=Path)
    args=parser.parse_args();HERE=args.output_dir;SOURCE_IMG=HERE/'assets/photos';QR_DIR=HERE/'assets/qr'
    QR_DIR.mkdir(parents=True,exist_ok=True)
    if args.font_dir:
        pdfmetrics.registerFont(TTFont('LB',str(args.font_dir/'Arial.ttf')))
        pdfmetrics.registerFont(TTFont('LB-Bold',str(args.font_dir/'Arial Bold.ttf')))
        FONT,BOLD='LB','LB-Bold'
    rows=json.loads(args.cards_json.read_text())
    assert len(rows)==64 and len({r['ItemNumber'] for r in rows})==64
    for r in rows:
        assert r['Proposed SKU'] and r['QR URL'].startswith('https://box.shopluvbuds.com/') and local_photo(r).is_file()
        qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=8,border=4)
        qr.add_data(r['QR URL']);qr.make(fit=True);qr.make_image(fill_color='black',back_color='white').save(QR_DIR/(r['ItemNumber']+'.png'))
    make_pdf(rows);make_html(rows)
    page=HERE/'LuvBuds_64_Cards_Interactive_Production.html'
    def embed(match):
        asset=HERE/match.group(2)
        return match.group(1)+'data:'+mimetypes.guess_type(asset.name)[0]+';base64,'+base64.b64encode(asset.read_bytes()).decode()+match.group(3)
    text=re.sub(r'(<img\b[^>]*\bsrc=")(assets/(?:photos|qr)/[^\"]+)(")',embed,page.read_text())
    (HERE/'LuvBuds_64_Cards_Interactive_Standalone.html').write_text(text)
    with (HERE/'image_audit.csv').open('w',newline='') as stream:
        keys=['ItemNumber','Proposed SKU','Photo File','Photo Status','Image Source URL','Image Dimensions','Image Quality Flag']
        writer=csv.DictWriter(stream,fieldnames=keys);writer.writeheader();writer.writerows({k:r[k] for k in keys} for r in rows)
    print('64 production cards; 64 photographs; 64 QR codes; trim, bleed and Letter PDFs')

if __name__=='__main__':
    main()
