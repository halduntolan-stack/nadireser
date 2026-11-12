import json,html,re,os
import urllib.request,sys,glob
def fetch():
    r=urllib.request.Request("https://yonetim.nadireser.com.tr/api/works.json",headers={"User-Agent":"nadireser-pages-bot"})
    return json.load(urllib.request.urlopen(r,timeout=30))
W=fetch()
if not isinstance(W,list) or not W: sys.exit("works.json bos")
_ix=open('index.html',encoding='utf-8').read()
_m=re.search(r'var HIDDEN\s*=\s*\[([^\]]*)\]',_ix)
HIDDEN=set(re.findall(r'"([^"]+)"',_m.group(1))) if _m else set()
BASE="https://nadireser.com.tr"
def imgurl(w):
    i=w['img']
    return i if i.startswith('http') else f"{BASE}/lot-{w['id']}.jpg"
works=[dict(w,img=imgurl(w),more=[m for m in (w.get('more') or []) if str(m).startswith('http')]) for w in W if str(w['id']) not in HIDDEN]
e=lambda s:html.escape(str(s or ''),quote=True)
import datetime
DEAL_EXCLUDE={'28','421','30','31'}
def deal(w): return str(w['id']) not in DEAL_EXCLUDE and not w.get('sold') and datetime.datetime.utcnow()<datetime.datetime(2026,11,14,20,59,59)
def price(n): return "$"+format(int(n),",")
def meta(w): return " · ".join(x for x in [w.get('year'),w.get('medium'),w.get('size')] if x)
def fixsize(s): return (s or '').replace('x',' × ').replace('  ',' ') if re.match(r'^\s*\d+x\d',s or '') else (s or '')
css=open('page.css',encoding='utf-8').read()
def page(w):
    t=w['title'];a=w['artist'];sold=w['sold']
    url=f"{BASE}/eser-{w['id']}"
    ttl=f"{a} - {t} | Nadir Eser"
    sz=fixsize(w['size'])
    desc=f"{a}, \"{t}\"" + (f" ({w['year']})" if w.get('year') else "") + f". {w.get('medium','')}, {sz}. " + ("Satıldı." if sold else f"Sabit fiyat {price(w['price'])}, Nadir Eser'de hemen satın alınabilir.")
    ld={"@context":"https://schema.org","@type":"Product","name":f"{a} - {t}","image":[w['img']]+w['more'],"description":desc,"brand":{"@type":"Brand","name":a},"category":"Sanat eseri",
        "offers":{"@type":"Offer","url":url,"priceCurrency":"USD","price":int(w['price']),"availability":"https://schema.org/OutOfStock" if sold else "https://schema.org/InStock","seller":{"@type":"Organization","name":"Nadir Eser"}}}
    others=[x for x in works if x['artist']==a and x['id']!=w['id']]
    more=[x for x in works if x['artist']!=a and not x['sold']][:6]
    def card(x): return f'<a class="mc" href="/eser-{x["id"]}"><img src="{e(x["img"])}" alt="{e(x["artist"])} - {e(x["title"])}" loading="lazy"><b>{e(x["artist"])}</b><span>{e(x["title"])}</span></a>'
    rel=""
    if others: rel+=f'<h2>{e(a)} — diğer eserler</h2><div class="mg">{"".join(card(x) for x in others)}</div>'
    rel+=f'<h2>Koleksiyondan seçmeler</h2><div class="mg">{"".join(card(x) for x in more)}</div>'
    dl=''.join(f'<dt>{k}</dt><dd>{e(v)}</dd>' for k,v in [("Sanatçı",a),("Eser adı",t),("Yıl",w.get('year')),("Teknik",w.get('medium')),("Ölçü",sz)] if v)
    waq=f"Merhaba, {a} - {t} (lot {w['id']}) eseri hakkında bilgi almak istiyorum."
    buy=('<button class="btn" disabled>Satıldı</button>' if sold else
         f'<a class="btn" href="mailto:info@nadireser.com.tr?subject={e("Satın alma talebi: "+a+" - "+t)}">E-posta ile satın alın</a><a class="btn wa" href="#" data-wa="{e(waq)}">WhatsApp ile yazın</a>')
    return f'''<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(ttl)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="product"><meta property="og:site_name" content="Nadir Eser"><meta property="og:title" content="{e(ttl)}"><meta property="og:description" content="{e(desc)}"><meta property="og:image" content="{e(w['img'])}"><meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='10' fill='%231d4a3c'/%3E%3Crect x='11' y='11' width='42' height='42' fill='none' stroke='%23f3e6c8' stroke-width='4'/%3E%3Cpolygon points='32,19 45,32 32,45 19,32' fill='%23d9a940'/%3E%3C/svg%3E">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,400;6..96,500;6..96,600&family=Jost:wght@400;500;600&display=swap">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>
<style>{css}</style></head><body>
<header><div class="wrap"><a class="logo" href="/">Nadir <i>Eser</i></a><a class="back" href="/#koleksiyon">← Tüm eserler</a></div></header>
<main class="wrap">
<nav class="bc"><a href="/">Nadir Eser</a> › <a href="/#koleksiyon">Koleksiyon</a> › {e(a)}</nav>
<article class="work"><div class="im{' sold' if sold else ''}{' multi' if w['more'] else ''}"><img src="{e(w['img'])}" alt="{e(a)}, {e(t)}">{"".join(f'<img src="{e(m)}" alt="{e(a)}, {e(t)}" loading="lazy">' for m in w['more'])}</div>
<div class="tx"><div class="ar">{e(a)}</div><h1>{e(t)}</h1><dl>{dl}</dl>
<div class="pr">{'Satıldı' if sold else (f'<s>{price(w["price"])}</s> {price(round(int(w["price"])*0.9))}' if deal(w) else price(w['price']))}</div>{('<div class="dl">%10 indirim · 12-14 Kasım&apos;a özel</div>' if deal(w) and not sold else '')}
<p class="hw">{'Bu eser satılmıştır. Benzer eserler için bize yazabilirsiniz.' if sold else 'Sabit fiyatlı, hemen satın alınabilir. Satın almak için e-posta ya da WhatsApp ile yazın; ödeme ve teslimat detaylarını birlikte netleştirelim.'}</p>
<div class="cr">{buy}</div></div></article>
{rel}
</main>
<footer><div class="wrap">© Nadir Eser · <a href="mailto:info@nadireser.com.tr">info@nadireser.com.tr</a></div></footer>
<script>document.addEventListener("click",function(e){{var a=e.target.closest&&e.target.closest("[data-wa]");if(!a)return;e.preventDefault();window.open("https://wa.me/905323662713?text="+encodeURIComponent(a.getAttribute("data-wa")),"_blank","noopener")}});</script>
<script src="https://yonetim.nadireser.com.tr/t.js" defer></script>
</body></html>'''
keep=set()
for w in works:
    fn=f"eser-{w['id']}.html"; keep.add(fn)
    open(fn,"w",encoding="utf-8").write(page(w))
for f in glob.glob('eser-*.html'):
    if f not in keep: os.remove(f)
import datetime
today=datetime.date.today().isoformat()
sm='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n<url><loc>'+BASE+'/</loc><lastmod>'+today+'</lastmod></url>\n'+''.join(f'<url><loc>{BASE}/eser-{w["id"]}</loc><lastmod>{today}</lastmod></url>\n' for w in works)+'</urlset>\n'
open('sitemap.xml','w',encoding='utf-8').write(sm)
open('robots.txt','w').write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
by={}
for w in works: by.setdefault(w['artist'],[]).append(w)
li=''.join(f'<li><a href="/eser-{w["id"]}">{html.escape(w["artist"])} — {html.escape(w["title"])}</a></li>' for a in sorted(by) for w in by[a])
blk='<!--ESERLER-->'+f'<nav class="note" aria-label="Eser sayfaları" style="border-top:1px solid var(--hair);padding:28px 0"><div class="wrap"><h2 style="font:500 1.3rem var(--display);margin:0 0 12px">Tüm eser sayfaları</h2><ul style="columns:2 260px;margin:0;padding-left:18px;font-size:.9rem;line-height:1.9">{li}</ul></div></nav>'+'<!--/ESERLER-->'
if '<!--ESERLER-->' in _ix:
    new=re.sub(r'<!--ESERLER-->.*?<!--/ESERLER-->',lambda m:blk,_ix,flags=re.S)
    if new!=_ix: open('index.html','w',encoding='utf-8').write(new)
print(len(works))
