import json
from html import escape, unescape
from datetime import datetime
import re

def _snapshot_html():
    widgets = [
        ("FOREXCOM:SPXUSD", "S&P 500"),
        ("INDEX:STI", "Straits Times Index"),
        ("INDEX:HSI", "Hang Seng Index"),
        ("INDEX:000001", "Shanghai Composite"),
        ("BITSTAMP:BTCUSD", "Bitcoin"),
        ("TVC:GOLD", "Gold"),
    ]

    cards = []
    for symbol, label in widgets:
        cards.append(
            f"""<div class="snapshot-card">
<div class="snapshot-card-title">{label}</div>
<div class="tradingview-widget-container">
<div class="tradingview-widget-container__widget"></div>
<script src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>{{"symbol":"{symbol}","width":"100%","height":180,"locale":"en","dateRange":"1D","colorTheme":"light","isTransparent":false,"autosize":true}}</script>
</div>
</div>"""
        )

    return "".join(cards)


def render_newsletter(articles, generated_at, preview=False):
    cards = []
    for a in articles:
        title = escape(a["title"])
        url = escape(a["url"], quote=True)
        source = escape(a.get("source", "Unknown source"))
        summary = escape(" ".join(unescape(re.sub(r"<[^>]+>", " ", a.get("summary", ""))).split()[:45]))
        cards.append(f"""
        <article>
        <h2>{title}</h2>
        <p>{summary}</p>
        <div class="story-meta"><span class="source">{source}</span> · <a href="{url}">Read more</a></div>
        </article>""")

    mode = "LOCAL PREVIEW — NOT PUBLISHED" if preview else "Daily Brief"
    specs=[("S&P 500","FOREXCOM:SPXUSD"),("STI","INDEX:STI"),("Hang Seng","INDEX:HSI"),("Shanghai","INDEX:000001"),("Bitcoin","BITSTAMP:BTCUSD"),("Gold","TVC:GOLD")]
    market_cards=[]
    for name,symbol in specs:
        cfg={"symbol":symbol,"width":"100%","height":220,"locale":"en","dateRange":"12M","colorTheme":"light","isTransparent":True,"autosize":True}
        market_cards.append(f'<div class="snapshot-card"><div class="snapshot-card-title">{name}</div><div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>'+json.dumps(cfg)+'</script></div></div>')
    html = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Semiconductor Industry Daily Brief</title>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
* {{ box-sizing:border-box; }}
body {{ margin:0; background:#eef1f4; color:#263449; font:15px/1.7 Montserrat,Arial,sans-serif; }}
header, header * {{ text-align:left !important; }}
header {{ background:#10263f; color:#fff; padding:38px 48px; border-bottom:5px solid #c9a34e; text-align:left; }}
.date {{ margin-bottom:10px; color:#d8e0e8; font-size:12px; }}
header h1 {{ margin:0; text-align:left; font-size:36px; font-weight:800; line-height:1.15; }}
.subtitle {{ margin-top:12px; color:#d8e0e8; font-size:12px; line-height:1.5; }}
@media(max-width:600px) {{ header {{ padding:28px 24px; }} }}
main {{ width:calc(100% - 40px); max-width:none; box-sizing:border-box; margin:30px auto; padding:25px 36px; background:white; }}
article {{ padding:20px 0; border-bottom:1px solid #dce3ec; }}
h1 {{ font-size:clamp(25px,4vw,36px); }}
h2 {{ font-size:19px; }}
a {{ color:#174f86; text-decoration:none; }}
a:hover {{ text-decoration:underline; }}
.source {{ color:#788493; font-size:12px; }}
footer {{ background:#10263f; color:#cbd5e1; padding:24px; text-align:center; font-size:12px; }}
@media(max-width:700px) {{ main {{ margin:15px 10px; padding:18px; }} }}
.snapshot {{padding:24px 48px 28px;border-bottom:1px solid #dfe4e9}}
.snapshot-title {{margin-bottom:14px;color:#10263f;font-size:13px;font-weight:800}}
.snapshot-grid {{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px}}
.market-heatmap {{margin-top:32px;padding-left:8px}}
.market-heatmap .snapshot-card-title {{font-size:13px;font-weight:800}}
.heatmap-links {{display:flex;flex-wrap:wrap;gap:8px 22px;align-items:center;margin-top:16px;width:100%;font-family:Montserrat,Arial,sans-serif;font-size:10px}}
.heatmap-links a {{color:#10263f;font-weight:800;text-decoration:none}}
.snapshot-card {{min-width:0}}
.snapshot-card-title {{margin-bottom:6px;color:#10263f;font-size:10px;font-weight:800}}
.snapshot-card .tradingview-widget-container {{width:100%;overflow:hidden}}
.snapshot-card .tradingview-widget-container iframe {{display:block;width:100%!important;max-width:100%}}
.tradingview-widget-container {{width:100%;overflow:hidden}}
.tradingview-widget-container__widget {{width:100%}}
.tradingview-widget-container iframe {{display:block;width:100%!important;max-width:100%}}
.snapshot {{padding:20px 24px 24px}}</style></head><body>
<header style="text-align:left"><p style="text-align:left;margin:0 0 6px"> {escape(datetime.fromisoformat(generated_at).strftime(chr(37)+"A, "+chr(37)+"-d "+chr(37)+"B "+chr(37)+"Y"))}</p>
<h1 style="text-align:left;margin:0 0 6px">Semiconductor Industry Daily Brief</h1><p style="text-align:left;margin:0">Providing concise, curated market intelligence</p></header>
<section class="snapshot">
<div class="snapshot-title">Market Snapshot — Live, as displayed by TradingView</div>
<div class="snapshot-grid">""" + "".join(market_cards) + """</div>
<div class="market-heatmap">
<div class="snapshot-card-title">Market Heatmap</div>
<div class="heatmap-links"><a href="https://www.tradingview.com/markets/indices/">Global Indices</a> · <a href="https://www.tradingview.com/heatmap/stock/#%7B%22dataSource%22%3A%22SPX500%22%2C%22blockColor%22%3A%22change%22%2C%22blockSize%22%3A%22market_cap_basic%22%2C%22grouping%22%3A%22sector%22%7D">S&amp;P 500 Index</a> · <a href="https://finviz.com/map?t=sec_ndx">Nasdaq 100</a> · <a href="https://finviz.com/map?t=geo">World Index</a> · <a href="https://finviz.com/map?t=themes">Market Themes</a> · <a href="https://www.tradingview.com/heatmap/stock/#%7B%22dataSource%22%3A%22SXXP%22%2C%22blockColor%22%3A%22change%22%2C%22blockSize%22%3A%22market_cap_basic%22%2C%22grouping%22%3A%22sector%22%7D">Stoxx 600 (Europe)</a> · <a href="https://finviz.com/map?t=etf">ETF</a> · <a href="https://finviz.com/map?t=crypto">Crypto</a> · <a href="https://www.tradingview.com/heatmap/stock/#%7B%22dataSource%22%3A%22AllSGP%22%2C%22blockColor%22%3A%22change%22%2C%22blockSize%22%3A%22market_cap_basic%22%2C%22grouping%22%3A%22sector%22%7D">Straits Times Index (STI)</a></div>
</div>
</section>

<main><h2>TODAY'S STORIES</h2>
""" + "".join(cards) + """
</main>
<footer>Semiconductor Industry Daily Brief · For information purposes only</footer>
</body></html>"""
    return html