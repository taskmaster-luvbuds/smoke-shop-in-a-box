#!/usr/bin/env python3
"""Generator v2: NEW Smoke-Shop-in-a-Box landing pages — CONSUMER voice (no wholesale language).
Run: .venv-qr/bin/python /tmp/build_ssib_pages.py   (writes into box repo working tree, local)."""
import os, re, csv, json, shutil, html, urllib.request, urllib.parse, time
import qrcode

BOX = "/Users/alexandermazzei2020/Documents/cursor projects/ontology/feb27/smokeshopinboxlandingpages"
CAT = "/Users/alexandermazzei2020/Documents/cursor projects/meridian/alexander/luvbuds/planogram full v4/smokeshopinboxplanogram/catalog.json"
IMGDIR = "/Users/alexandermazzei2020/Downloads/luvbuds qr code ssib images"
BASE_URL = "https://box.shopluvbuds.com"
catalog = json.load(open(CAT)).get("products", {}) if os.path.exists(CAT) else {}
def slug(s): return s.strip().lower().replace(" ", "-")

# rank, sku, CONSUMER name, product_id, category, CONSUMER description (no wholesale/case/display terms)
ITEMS = [
(5,"HP-CHILL3","3\" Glass Chillum","112","pipe",
 "The 3\" chillum is the one-hitter you actually keep on you — pack it, hit it, pocket it. Clean glass draw, no fuss, in a bold color that's easy to spot at the bottom of any bag. Simple, done right."),
(8,"HP-2.5P40G","2.5\" Glass Hand Pipe","113","pipe",
 "Tiny but mighty — the 2.5\" pipe slips into any pocket and goes anywhere with you. Smooth glass-on-glass draw with zero harshness. Sometimes the smallest piece is the one you reach for every day."),
(9,"BT-350VV","350mAh Variable Voltage Battery","731","battery",
 "Your reliable, no-nonsense 510 battery — slim, pocket-friendly, and it just works with every cart. Variable voltage lets you go light and flavorful or thick and cloudy. USB charger included so you're never stuck."),
(10,"PFC-PROXYCOREKIT","Puffco Proxy Core Kit, Onyx","5675","dab",
 "The Proxy Core is the heart of Puffco's most versatile system — drop it into any Proxy glass and get the same legendary dab in a shape that fits your style. Onyx finish, app-connected, and built to evolve with you."),
(11,"OOZ-1453","Ooze HiLo Conceal 510 Battery","5429","battery",
 "The HiLo Conceal hides a full variable-voltage 510 battery inside a discreet, palm-sized shell — nobody gives it a second look until you need it. 400mAh, preheat mode, and a design built to go unnoticed."),
(13,"BT-V985D","Pulsar 510 DL 5.0 Auto-Draw Battery","5274","battery",
 "Pulsar's 510 DL 5.0 fires the second you inhale — no buttons, just auto-draw simplicity, with variable voltage when you want a bigger pull. Slim, dependable, and ready for any cart."),
(14,"KA-WP-STEELCHILL13","13\" Chill Stainless Steel Bong","3509","waterpipe",
 "The Chill Steel bong is built to survive everything — a vacuum-insulated stainless steel base, an 8.5\" steel neck (13\" total), an aluminum diffuser downstem, and an easy-clean ceramic interior that wipes down with just ISO. Backed by Chill's warranty."),
(15,"ZZUT48","Zig-Zag Ultra Thin 1 1/4\" Rolling Papers","1539","papers",
 "Zig-Zag Ultra Thin papers burn slow and clean, so the flavor comes through, not the paper. The 1 1/4 size is the everyday standard — the name rollers have trusted for generations."),
(18,"PFC-PEAKNEWBLK","The New Puffco Peak, Onyx","4826","dab",
 "The new Peak redefined the dab rig — real-time temperature control, faster heat-up, and a smoother, bigger hit than anything before it. Onyx finish, smart-connected, and unmistakably the centerpiece of any session."),
(24,"BT-V1180D","Pulsar 510 DL 5.0 Battery, Thermo Series","5455","battery",
 "The DL 5.0 Thermo runs a full 1000mAh with auto-draw and variable voltage, wrapped in a thermochromic finish that shifts color with heat. Big battery, bold look, and it works with every 510 cart."),
(26,"SE-BT-380VV-BX-24PK","SirEEL 380mAh Preheat Battery","5581","battery",
 "The 380mAh flashlight-style battery is a pocket classic — preheat-capable, variable voltage, and compatible with every 510 cart. USB charger included, in assorted colors."),
(27,"OOZ-1379","Ooze Smart Battery 650mAh","4532","battery",
 "The Ooze Smart Battery reads your cart and auto-adjusts the voltage, so every hit is dialed in without you thinking about it. 650mAh keeps you going all day, and the smart-sensing tech makes it foolproof. Assorted colors."),
(32,"CLIP-PROMO-HAZMAT","Clipper Large Lighter","5682","lighter",
 "Clipper has been the OG refillable lighter for 50+ years — a round body, a removable flint housing that doubles as a poker for your papers, and a build you keep going for years. Full-size, childproof, and refillable, in assorted designs."),
(34,"HP-3P55G","3.5\" Glass Hand Pipe","114","pipe",
 "The 3.5\" spoon hits the sweet spot between pocket-friendly and comfortable in the hand. Clean draw, glass thick enough to feel confident about, and colors good enough to leave sitting out. Your everyday carry, elevated."),
(36,"PC-6PCK-PINK-MC","Blazy Susan 1 1/4\" Pink Pre-Rolled Cones, 6 Pack","2744","papers",
 "Blazy Susan's signature pink cones come pre-rolled and ready — just fill, twist, and go. The 1 1/4 size is the everyday favorite, six cones to a pack. As fun to look at as they are easy to use."),
(37,"POP-114-VARIETY-UB2.0","Pop Cones Unbleached 1 1/4\" Variety, 25 Pack","5463","papers",
 "Pop Cones come pre-rolled and pre-tipped, so there's zero fuss — just pack and spark. The unbleached 1 1/4 variety pack gives you 25 cones, slow-burning and clean every time."),
(38,"SE-WP-BEAKUV","10\" SirEEL UV Beaker Bong","4820","waterpipe",
 "This 10\" beaker glows under UV and hits like a classic should — a wide base for stability, smooth water filtration, and a flower bowl included so you're ready out of the box. Assorted colors, each one a little different."),
(39,"HP-4P85G","4.5\" Glass Hand Pipe","115","pipe",
 "At 4.5 inches this spoon fits perfectly in your hand and your pocket — the pipe you grab without thinking because it just works. Borosilicate glass, a clean draw, and colors varied enough that every one feels like a find."),
(41,"CCELL-M4BPRO-ASST","CCELL M4B Pro 290mAh Battery","5487","battery",
 "CCELL sets the standard for cart compatibility, and the M4B Pro adds variable voltage in a slim 290mAh body that disappears in your pocket. Reliable connection, clean flavor, assorted colors."),
(42,"PFC-PEAKNEWSAPPHIRE","The New Puffco Peak, Sapphire Edition","5701","dab",
 "The new Peak in a limited-edition Sapphire finish — the same category-defining dab with real-time temperature control and a bigger, smoother hit, dressed in a color you won't see twice."),
(44,"NWTN-WP-DECOGP-ASST","NWTN Deco Gravity Bong","5472","waterpipe",
 "The Deco gives the gravity bong an old-world, art-deco twist — heavy borosilicate glass that looks at home on any bar or shelf. Four easy-to-clean pieces: glass shell, glass core, 14mm slide, and silicone gasket. Smooth, discreet, and built to impress (8.1\" x 3.3\")."),
(45,"RAWCONEDISP20PK114","RAW Classic 1 1/4\" Pre-Rolled Cones, 20 Pack","3076","papers",
 "RAW's classic pre-rolled cones in the everyday 1 1/4 size — natural, slow-burning, and ready to fill. Twenty cones to a pack, so you're set for a while. The trusted name in unrefined papers."),
(47,"GRAV-PBS.0","GRAV 3\" Spherical Pocket Bubbler","3792","waterpipe",
 "The 3\" GRAV Spherical Pocket Bubbler packs real water filtration into a pocket-sized sphere — fit a 10mm bowl, a banger, or even a pre-roll, and it does it all. Designed by Micah Evans in clean borosilicate. Discreet, sturdy, endlessly versatile, and it includes a 10mm cup bowl."),
(50,"PFC-PEAKNEWZEST","The New Puffco Peak, Zest Edition","5702","dab",
 "The new Peak in a limited-edition Zest finish — bright, bold, and unmistakable, with the same real-time temperature control and big, smooth hits that made the Peak legendary."),
(51,"BT-V852D","Pulsar 510 DL 2.0 PRO Vape Bar, Mist Series","4624","battery",
 "The DL 2.0 PRO Vape Bar gives you 1000mAh of auto-draw power with variable voltage in a slim, modern bar shape. The Mist Series finish keeps it understated — ready for any 510 cart."),
(52,"YOCAN-ZIVAPRO-ASST-10PK","Yocan ZIVA PRO 650mAh Battery","5556","battery",
 "The Yocan ZIVA PRO pairs a 650mAh variable-voltage battery with smart-charging convenience, so it's ready when you are. Reliable with every 510 cart and built to last. Assorted colors."),
]
LOCAL_IMG = {"NWTN-WP-DECOGP-ASST":"NWTN-WP-DECOGP-ASST.jpg","GRAV-PBS.0":"GRAV-PBS.0.jpg",
             "KA-WP-STEELCHILL13":'13" Chill Stainless Steel Bong.jpg',"CLIP-PROMO-HAZMAT":"CLIP-PROMO.jpg"}
FEATURES = {
 "battery": [("zap","Variable Voltage","Dial your hit"),("battery-charging","Rechargeable","USB charging"),("box","510 Thread","Fits any cart"),("shield-check","LuvBuds QA","Verified Quality")],
 "dab":     [("thermometer","Temp Control","Real-time heat"),("sparkles","Bigger Hits","Smoother vapor"),("bluetooth","Smart-Connected","App ready"),("shield-check","LuvBuds QA","Verified Quality")],
 "pipe":    [("gem","Premium Glass","Heat resistant"),("hand","Pocket Size","Grab & go"),("palette","Assorted Colors","Each unique"),("shield-check","LuvBuds QA","Verified Quality")],
 "waterpipe":[("droplet","Water Filtration","Smooth hits"),("gem","Built to Last","Heavy glass"),("sparkles","Statement Piece","Turns heads"),("shield-check","LuvBuds QA","Verified Quality")],
 "papers":  [("flame","Slow Burn","Even every time"),("leaf","Clean Draw","Pure flavor"),("check-circle","Ready to Roll","No fuss"),("shield-check","LuvBuds QA","Verified Quality")],
 "lighter": [("flame","Reliable Flame","Every strike"),("refresh-cw","Refillable","Long life"),("palette","Assorted","Styles vary"),("shield-check","LuvBuds QA","Verified Quality")],
}
def first_bc_img(e):
    for u in e.get("images",[]):
        if isinstance(u,str) and "bigcommerce.com" in u: return u
    return None
def to_orig(u): return re.sub(r'/images/stencil/\d+x\d+/','/images/stencil/original/',u)
def cat_image(sku):
    if sku in catalog:
        u=first_bc_img(catalog[sku])
        if u: return u
    core=sku.replace("SE-","").replace("-BX","").replace("-SOLID","").upper()
    for k,v in catalog.items():
        if k.replace("SE-","").replace("-BX","").replace("-SOLID","").upper()==core:
            u=first_bc_img(v)
            if u: return u
    return None
def fetch(u): return urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}),timeout=15).read().decode("utf-8","replace")
def scrape_image(sku,pid):
    try:
        for pg in ("","&page=2","&page=3"):
            h=fetch(f"https://shopluvbuds.com/search.php?search_query={urllib.parse.quote(sku)}{pg}")
            m=re.search(rf'(https://cdn11\.bigcommerce\.com/s-ijm7dw7yvr/[^"\'\s]*products/{pid}/[^"\'\s]+?\.(?:jpg|jpeg|png))',h,re.I)
            if m: return to_orig(m.group(1))
    except Exception: pass
    return None
def render(name,img,alt,desc,feats):
    cards=""; pal=["brand-orange","brand-green","blue-400","purple-400"]; bg=["brand-orange/20","brand-green/20","blue-500/20","purple-500/20"]
    for i,(ic,t,sub) in enumerate(feats):
        cards+=f'''
            <div class="bg-brand-card border border-white/5 rounded-[2rem] p-5 flex flex-col gap-3 justify-center items-start">
                <div class="w-10 h-10 rounded-full bg-{bg[i]} text-{pal[i]} flex items-center justify-center"><i data-lucide="{ic}" class="w-5 h-5"></i></div>
                <div><h4 class="font-semibold text-sm">{html.escape(t)}</h4><p class="text-xs text-white/50 mt-0.5">{html.escape(sub)}</p></div>
            </div>'''
    return f'''<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{html.escape(name)} | Smoke Shop in a Box</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>tailwind.config={{theme:{{extend:{{fontFamily:{{sans:['Outfit','sans-serif']}},colors:{{brand:{{orange:'#F97316',green:'#22C55E',dark:'#0a0a0a',card:'#171717'}}}},animation:{{blob:'blob 7s infinite'}},keyframes:{{blob:{{'0%':{{transform:'translate(0px,0px) scale(1)'}},'33%':{{transform:'translate(30px,-50px) scale(1.1)'}},'66%':{{transform:'translate(-20px,20px) scale(0.9)'}},'100%':{{transform:'translate(0px,0px) scale(1)'}}}}}}}}}}}}</script>
    <style>::-webkit-scrollbar{{display:none}}body{{-ms-overflow-style:none;scrollbar-width:none;-webkit-tap-highlight-color:transparent}}</style>
</head>
<body class="bg-brand-dark text-white font-sans antialiased pb-28">
    <div class="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div class="absolute top-0 left-1/4 w-96 h-96 bg-brand-orange/20 rounded-full mix-blend-screen filter blur-[100px] animate-blob"></div>
        <div class="absolute top-0 right-1/4 w-96 h-96 bg-brand-green/10 rounded-full mix-blend-screen filter blur-[100px] animate-blob"></div>
    </div>
    <nav class="fixed top-0 w-full z-50 bg-brand-dark/80 backdrop-blur-xl border-b border-white/5">
        <div class="max-w-md mx-auto px-4 h-16 flex items-center justify-between">
            <div class="flex items-center gap-2"><i data-lucide="package" class="w-6 h-6 text-brand-orange"></i><span class="font-bold tracking-tight text-lg">Smoke Shop in a Box</span></div>
            <button class="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center text-white/70 hover:text-white hover:bg-white/10 transition"><i data-lucide="share" class="w-5 h-5"></i></button>
        </div>
    </nav>
    <main class="relative z-10 pt-20 px-4 max-w-md mx-auto flex flex-col gap-6">
        <div class="relative w-full aspect-square rounded-[2rem] bg-brand-card border border-white/5 overflow-hidden group">
            <div class="absolute top-4 left-4 z-20 bg-brand-dark/60 backdrop-blur-md px-3 py-1.5 rounded-full border border-white/10 flex items-center gap-1.5"><div class="w-2 h-2 rounded-full bg-brand-green animate-pulse"></div><span class="text-xs font-semibold tracking-wide uppercase">In Stock</span></div>
            <img src="{html.escape(img)}" alt="{html.escape(alt)}" class="absolute inset-0 w-full h-full object-cover opacity-90 transition-transform duration-700 group-hover:scale-105">
            <div class="absolute inset-0 bg-gradient-to-t from-brand-dark/80 via-transparent to-transparent"></div>
        </div>
        <div class="flex flex-col gap-2"><div><p class="text-brand-orange text-sm font-semibold tracking-wide uppercase mb-1">Powered by LuvBuds</p><h1 class="text-3xl font-bold leading-tight">{html.escape(name)}</h1></div></div>
        <div class="relative w-full rounded-[2rem] bg-brand-card border border-white/5 overflow-hidden aspect-[16/9] shadow-2xl">
            <img src="assets/video-placeholder.png" class="absolute inset-0 w-full h-full object-cover opacity-80" alt="Product demo coming soon">
            <div class="absolute bottom-3 right-3 bg-black/50 backdrop-blur-md px-2 py-1 rounded-lg flex items-center gap-1"><i data-lucide="play" class="w-3 h-3 text-white"></i><span class="text-[10px] font-medium uppercase tracking-wider">Coming Soon</span></div>
        </div>
        <div class="bg-brand-card/50 border border-white/5 rounded-[2rem] p-6"><h3 class="text-lg font-semibold mb-3">About this item</h3><p class="text-white/70 leading-relaxed text-sm">{html.escape(desc)}</p></div>
        <div class="grid grid-cols-2 gap-4">{cards}
        </div>
    </main>
    <div class="fixed bottom-0 left-0 w-full z-50 bg-brand-dark/90 backdrop-blur-2xl border-t border-white/10 pt-4 px-4 pb-6">
        <div class="max-w-md mx-auto flex items-center gap-4">
            <button class="w-14 h-14 shrink-0 rounded-2xl bg-brand-card border border-white/10 flex items-center justify-center text-white hover:bg-white/5 transition active:scale-95"><i data-lucide="heart" class="w-6 h-6"></i></button>
            <button class="flex-1 h-14 rounded-2xl bg-brand-orange hover:bg-orange-500 text-white font-bold text-lg flex items-center justify-center gap-2 transition-all active:scale-95 shadow-[0_0_20px_rgba(249,115,22,0.3)]"><span>Grab it Now</span><i data-lucide="arrow-right" class="w-5 h-5"></i></button>
        </div>
    </div>
    <script>lucide.createIcons();</script>
</body>
</html>'''
SHEET_JS="""
  <script>
    (function() {{
      var SHEET_ID='REPLACE_WITH_STORE_SHEET_ID'; var SKU='{sku}';
      fetch('https://docs.google.com/spreadsheets/d/'+SHEET_ID+'/gviz/tq?tqx=out:json&sheet=products')
        .then(function(r){{return r.text();}}).then(function(raw){{
          var data=JSON.parse(raw.slice(47,-2));
          var row=data.table.rows.find(function(r){{return r.c[0]&&r.c[0].v===SKU;}});
          if(!row)return; var desc=row.c[2]&&row.c[2].v;
          if(desc){{var el=document.getElementById('product-desc'); if(el)el.textContent=desc;}}
        }}).catch(function(){{}});
    }})();
  </script>
"""
os.makedirs(os.path.join(BOX,"assets","products"),exist_ok=True)
os.makedirs(os.path.join(BOX,"qr-codes"),exist_ok=True)
rows=[]
for rank,sku,name,pid,cat,desc in ITEMS:
    s=slug(sku)
    if sku in LOCAL_IMG:
        src=os.path.join(IMGDIR,LOCAL_IMG[sku]); ext=os.path.splitext(src)[1].lower(); rel=f"assets/products/{s}{ext}"
        shutil.copyfile(src,os.path.join(BOX,rel)); img,isrc=rel,"local-file"
    else:
        g=cat_image(sku) or scrape_image(sku,pid); img,isrc=(g,"catalog/scrape") if g else ("assets/video-placeholder.png","MISSING")
    page=render(name,img,name,desc,FEATURES[cat])
    page=page.replace('<p class="text-white/70 leading-relaxed text-sm">','<p id="product-desc" class="text-white/70 leading-relaxed text-sm">',1)
    page=page.replace('</body>',SHEET_JS.format(sku=sku)+'</body>',1)
    open(os.path.join(BOX,f"{s}.html"),"w",encoding="utf-8").write(page)
    url=f"{BASE_URL}/{s}.html"
    qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=10,border=4); qr.add_data(url); qr.make(fit=True)
    qr.make_image(fill_color="black",back_color="white").save(os.path.join(BOX,"qr-codes",f"{sku}.png"))
    rows.append({"rank":rank,"sku":sku,"slug":s,"landing_url":url,"product_name":name,"image_source":isrc,"qr_file":f"qr-codes/{sku}.png","page_file":f"{s}.html"})
rows.sort(key=lambda r:r["rank"])
with open(os.path.join(BOX,"new-items-manifest.csv"),"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["rank","sku","slug","landing_url","product_name","image_source","qr_file","page_file"]); w.writeheader(); w.writerows(rows)
# idempotent products.csv: drop our 26 SKUs then re-append fresh desc
our={sku for _,sku,*_ in ITEMS}
kept=[r for r in csv.reader(open(os.path.join(BOX,"products.csv"))) if not (r and r[0] in our)]
with open(os.path.join(BOX,"products.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerows(kept)
    for rank,sku,name,pid,cat,desc in ITEMS: w.writerow([sku,"",desc])

# ---- WHOLESALE-TERM GATE: scan visible copy (name+desc+features) ----
BLOCK=["wholesale","ships as","pop display","retail display","display of","per box","packs/box","packs per box",
       "off the counter","key account","bulk","case pack"," moq","8pk","24pk","10pk","20pk","48 book","50 pk","50pk","12 pack","per case","8-pack","24-pack","10-pack"]
hits=[]
for rank,sku,name,pid,cat,desc in ITEMS:
    blob=(name+" "+desc).lower()
    for t in BLOCK:
        if t in blob: hits.append((sku,t))
print(f"BUILT {len(rows)} pages + QR  | images: local={sum(1 for r in rows if r['image_source']=='local-file')} resolved={sum(1 for r in rows if r['image_source']=='catalog/scrape')} MISSING={[r['sku'] for r in rows if r['image_source']=='MISSING']}")
print(f"WHOLESALE-TERM GATE: {'CLEAN ✓' if not hits else 'HITS: '+str(hits)}")
